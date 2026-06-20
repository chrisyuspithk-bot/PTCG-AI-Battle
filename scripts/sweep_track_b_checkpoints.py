"""Train, checkpoint, distill, gate, and package the best Track B policy.

This is the durable version of the Kaggle checkpoint-sweep workflow. It avoids
packaging only the final PPO state, because intermediate checkpoints can gate
better than the final checkpoint.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _default_out_dir(slug: str) -> Path:
    kaggle_working = Path("/kaggle/working")
    if kaggle_working.exists():
        return kaggle_working / "out_sweep"
    return ROOT / "report" / "rl_sweep" / slug / "out"


def _default_archive_base(slug: str) -> Path:
    kaggle_working = Path("/kaggle/working")
    if kaggle_working.exists():
        return kaggle_working / "track_b_sweep_outputs"
    return ROOT / "report" / "rl_sweep" / slug / "track_b_sweep_outputs"


def run_live(cmd: list[str], *, cwd: Path = ROOT, check: bool = True) -> int:
    print("\n$", " ".join(map(str, cmd)), flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    start = last = time.time()
    assert proc.stdout is not None
    while True:
        line = proc.stdout.readline()
        if line:
            print(line, end="", flush=True)
            last = time.time()
        elif proc.poll() is not None:
            break
        elif time.time() - last > 60:
            print(f"[heartbeat] still running after {(time.time() - start) / 60:.1f} min", flush=True)
            last = time.time()
        else:
            time.sleep(1)
    rc = proc.wait()
    if check and rc != 0:
        raise RuntimeError(f"command failed ({rc}): {' '.join(map(str, cmd))}")
    return rc


def run_capture(cmd: list[str], *, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    print("\n$", " ".join(map(str, cmd)), flush=True)
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, flush=True)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, flush=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(map(str, cmd))}")
    return proc


def parse_gate(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    learned = re.search(r"Learned wins vs pool: (\d+)/(\d+)", text)
    search = re.search(r"Search baseline: (\d+)/(\d+)", text)
    passed = "Gate passed: **True**" in text
    learned_wins = int(learned.group(1)) if learned else -1
    learned_total = int(learned.group(2)) if learned else -1
    search_wins = int(search.group(1)) if search else -1
    search_total = int(search.group(2)) if search else -1
    return {
        "gate_report": str(path),
        "learned_wins": learned_wins,
        "learned_total": learned_total,
        "search_wins": search_wins,
        "search_total": search_total,
        "margin_vs_search": learned_wins - search_wins,
        "passed": passed,
    }


def record_rank_key(record: dict) -> tuple[int, int, int, int]:
    """Higher is better; lower timesteps wins the last tie-break."""
    return (
        1 if record.get("passed") else 0,
        int(record.get("margin_vs_search", -9999)),
        int(record.get("learned_wins", -1)),
        -int(record.get("total_steps", 10**12)),
    )


def collect_outputs(out_dir: Path, archive_base: Path, sweep_dir: Path, best: dict | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    patterns = [
        "agent/models/rl_policy.zip",
        "agent/models/distilled_*.npz",
        "agent/models/distilled_v1.npz",
        "dist/candidates/track_b_learned_*.tar.gz",
        "report/rl_train/checkpoint.json",
        "report/track_b_runs/*.json",
        "report/track_b_gates/*gate.md",
        "report/rl_train/eval_*.json",
    ]
    for pattern in patterns:
        for src_name in glob.glob(str(ROOT / pattern)):
            src = Path(src_name)
            if src.is_file():
                shutil.copy2(src, out_dir / src.name)
    if sweep_dir.exists():
        for src in sweep_dir.rglob("*"):
            if src.is_file():
                rel = src.relative_to(sweep_dir)
                dst = out_dir / "sweep" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    if best is not None:
        (out_dir / "best_gate.json").write_text(json.dumps(best, indent=2), encoding="utf-8")
    zip_path = shutil.make_archive(str(archive_base), "zip", str(out_dir))
    print("download", zip_path, flush=True)
    return Path(zip_path)


def maybe_persist_kaggle_dataset(
    out_dir: Path,
    dataset_slug: str,
    dataset_title: str,
    tag: str,
) -> None:
    """Best-effort Kaggle Dataset versioning; never fail the sweep for this."""
    if not Path("/kaggle/working").exists():
        return
    try:
        from kaggle_secrets import UserSecretsClient  # type: ignore
    except Exception:
        print("[persist] kaggle_secrets unavailable; skipping Dataset persistence", flush=True)
        return
    try:
        user = UserSecretsClient()
        username = user.get_secret("KAGGLE_USERNAME")
        key = user.get_secret("KAGGLE_KEY")
        if not username or not key:
            print("[persist] Kaggle secrets missing; skipping Dataset persistence", flush=True)
            return
        kaggle_dir = Path("/root/.kaggle")
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        cred = kaggle_dir / "kaggle.json"
        cred.write_text(json.dumps({"username": username, "key": key}), encoding="utf-8")
        os.chmod(cred, 0o600)
        metadata = out_dir / "dataset-metadata.json"
        metadata.write_text(
            json.dumps({
                "title": dataset_title,
                "id": f"{username}/{dataset_slug}",
                "licenses": [{"name": "CC0-1.0"}],
            }, indent=2),
            encoding="utf-8",
        )
        run_capture([sys.executable, "-m", "pip", "install", "-q", "kaggle"], check=False)
        run_capture(["kaggle", "datasets", "create", "-p", str(out_dir), "--dir-mode", "zip", "-q"], check=False)
        run_capture([
            "kaggle", "datasets", "version",
            "-p", str(out_dir),
            "-m", tag,
            "--dir-mode", "zip",
            "-q",
        ], check=False)
        print(f"[persist] Dataset version attempted for {tag}", flush=True)
    except Exception as exc:
        print(f"[persist] skipped after error: {type(exc).__name__}: {exc}", flush=True)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def train_chunk(args: argparse.Namespace, chunk: int) -> None:
    cmd = [
        sys.executable, str(ROOT / "scripts" / "train_track_b_deck.py"),
        "--deck", args.deck,
        "--slug", args.slug,
        "--timesteps", str(args.timesteps_per_chunk),
        "--n-envs", str(args.n_envs),
        "--opponents", args.opponents,
        "--holdout", args.holdout,
        "--skip-distill",
        "--skip-gate",
        "--resume",
    ]
    if chunk == 1 and args.fresh:
        cmd.remove("--resume")
    run_live(cmd)


def distill_checkpoint(
    args: argparse.Namespace,
    policy_path: Path,
    distilled: Path,
    *,
    episodes: int,
    epochs: int,
) -> None:
    run_live([
        sys.executable, str(ROOT / "scripts" / "distill_policy.py"),
        "--src", str(policy_path),
        "--out", str(distilled),
        "--deck", args.deck,
        "--opponents", args.opponents,
        "--episodes", str(episodes),
        "--epochs", str(epochs),
    ])


def gate_model(args: argparse.Namespace, distilled: Path, gate_name: str, games: int) -> dict:
    run_live([
        sys.executable, str(ROOT / "scripts" / "gate_track_b.py"),
        "--games", str(games),
        "--deck", args.deck,
        "--model", str(distilled),
        "--name", gate_name,
        "--no-package",
    ], check=False)
    gate_path = ROOT / "report" / "track_b_gates" / f"{gate_name}_gate.md"
    if not gate_path.exists():
        raise RuntimeError(f"missing gate report: {gate_path}")
    return parse_gate(gate_path)


def package_best(args: argparse.Namespace, best_model: Path) -> Path:
    package_name = "track_b_learned_sweep_best"
    run_capture([
        sys.executable, str(ROOT / "scripts" / "package_submission.py"),
        "--name", package_name,
        "--scorer", "learned",
        "--deck", args.deck,
        "--model", str(best_model),
    ])
    promoted = ROOT / "agent" / "models" / "distilled_v1.npz"
    promoted.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_model, promoted)
    return ROOT / "dist" / "candidates" / f"{package_name}.tar.gz"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", default="report/rl_deck_campaign/best_deck.csv")
    parser.add_argument("--slug", default="rl_deck_sweep")
    parser.add_argument("--chunks", type=int, default=5)
    parser.add_argument("--timesteps-per-chunk", type=int, default=100_000)
    parser.add_argument("--n-envs", type=int, default=4)
    parser.add_argument("--opponents", choices=("benchmark", "pool"), default="benchmark")
    parser.add_argument("--holdout", default="a2_kyogre")
    parser.add_argument("--gate-games", type=int, default=40)
    parser.add_argument("--finalist-gate-games", type=int, default=80)
    parser.add_argument("--distill-episodes", type=int, default=300)
    parser.add_argument("--distill-epochs", type=int, default=30)
    parser.add_argument("--finalists", type=int, default=2)
    parser.add_argument("--finalist-distill-episodes", type=int, default=800)
    parser.add_argument("--finalist-distill-epochs", type=int, default=50)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--archive-base", default=None)
    parser.add_argument("--dataset-slug", default="ptcg-track-b-sweep-checkpoints")
    parser.add_argument("--dataset-title", default="PTCG Track B Sweep Checkpoints")
    parser.add_argument("--no-dataset-persist", action="store_true")
    parser.add_argument("--fresh", action="store_true", help="Do not resume on chunk 1.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    started = time.time()
    sweep_dir = ROOT / "report" / "rl_sweep" / args.slug
    checkpoints_dir = sweep_dir / "checkpoints"
    out_dir = Path(args.out_dir) if args.out_dir else _default_out_dir(args.slug)
    archive_base = Path(args.archive_base) if args.archive_base else _default_archive_base(args.slug)
    records_path = sweep_dir / "sweep_records.json"
    summary_path = sweep_dir / "summary.json"

    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    best: dict | None = None
    zip_path: Path | None = None

    for chunk in range(1, args.chunks + 1):
        total_steps = chunk * args.timesteps_per_chunk
        step_label = f"{total_steps // 1000}k"
        ckpt_slug = f"{args.slug}_{step_label}"
        print(f"\n=== chunk {chunk}/{args.chunks}: total target {total_steps} ===", flush=True)

        train_chunk(args, chunk)

        source_policy = ROOT / "agent" / "models" / "rl_policy.zip"
        if not source_policy.exists():
            raise RuntimeError(f"missing trained policy: {source_policy}")
        policy_copy = checkpoints_dir / f"rl_policy_{step_label}.zip"
        shutil.copy2(source_policy, policy_copy)

        distilled = ROOT / "agent" / "models" / f"distilled_{ckpt_slug}_v1.npz"
        distill_checkpoint(
            args,
            policy_copy,
            distilled,
            episodes=args.distill_episodes,
            epochs=args.distill_epochs,
        )

        gate_name = f"track_b_learned_{ckpt_slug}"
        rec = gate_model(args, distilled, gate_name, args.gate_games)
        rec.update({
            "phase": "sweep",
            "chunk": chunk,
            "total_steps": total_steps,
            "policy": str(policy_copy),
            "distilled": str(distilled),
            "gate_name": gate_name,
            "distill_episodes": args.distill_episodes,
            "distill_epochs": args.distill_epochs,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        records.append(rec)
        if best is None or record_rank_key(rec) > record_rank_key(best):
            best = rec
            print("[best] updated", json.dumps(best, indent=2), flush=True)

        write_json(records_path, records)
        write_json(summary_path, {"best": best, "records": records})
        zip_path = collect_outputs(out_dir, archive_base, sweep_dir, best)
        if not args.no_dataset_persist:
            maybe_persist_kaggle_dataset(out_dir, args.dataset_slug, args.dataset_title, f"chunk {chunk}/{args.chunks}")

    passed = [r for r in records if r.get("passed")]
    if not passed:
        zip_path = collect_outputs(out_dir, archive_base, sweep_dir, best)
        print("No passing checkpoint; no final package built.", flush=True)
        print("download", zip_path, flush=True)
        return 2

    finalists = sorted(passed, key=record_rank_key, reverse=True)[:max(1, args.finalists)]
    finalist_records: list[dict] = []
    print(f"\n=== finalist pass: {len(finalists)} checkpoint(s) ===", flush=True)
    for idx, base in enumerate(finalists, start=1):
        total_steps = int(base["total_steps"])
        step_label = f"{total_steps // 1000}k"
        finalist_slug = f"{args.slug}_{step_label}_finalist"
        policy = Path(base["policy"])
        distilled = ROOT / "agent" / "models" / f"distilled_{finalist_slug}_v1.npz"
        distill_checkpoint(
            args,
            policy,
            distilled,
            episodes=args.finalist_distill_episodes,
            epochs=args.finalist_distill_epochs,
        )
        gate_name = f"track_b_learned_{finalist_slug}"
        rec = gate_model(args, distilled, gate_name, args.finalist_gate_games)
        rec.update({
            "phase": "finalist",
            "finalist_rank": idx,
            "total_steps": total_steps,
            "policy": str(policy),
            "distilled": str(distilled),
            "gate_name": gate_name,
            "distill_episodes": args.finalist_distill_episodes,
            "distill_epochs": args.finalist_distill_epochs,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        finalist_records.append(rec)

    passing_finalists = [r for r in finalist_records if r.get("passed")]
    best_finalist = max(passed + passing_finalists, key=record_rank_key)

    package = package_best(args, Path(best_finalist["distilled"]))
    best_finalist["best_package"] = str(package)
    all_records = records + finalist_records
    write_json(records_path, all_records)
    write_json(summary_path, {
        "best_sweep": best,
        "best_finalist_or_fallback": best_finalist,
        "records": all_records,
        "elapsed_minutes": round((time.time() - started) / 60, 1),
    })
    zip_path = collect_outputs(out_dir, archive_base, sweep_dir, best_finalist)
    if not args.no_dataset_persist:
        maybe_persist_kaggle_dataset(out_dir, args.dataset_slug, args.dataset_title, "final package")

    print("\nDONE", flush=True)
    print("elapsed_minutes", round((time.time() - started) / 60, 1), flush=True)
    print("best", json.dumps(best_finalist, indent=2), flush=True)
    print("download", zip_path, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
