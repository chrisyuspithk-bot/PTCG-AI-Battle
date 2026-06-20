"""Import a completed Kaggle Lucario RL+MCTS run and package it locally.

This does not submit to Kaggle. It expects downloaded notebook output containing
``model_best.pth`` from ``/kaggle/working/lucario_rl`` and builds a local
candidate archive using ``--scorer lucario_mcts``.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.package_submission import ARCHIVE_DIR, build, dry_run_import  # noqa: E402


def _artifact_dir(source: Path) -> Path:
    if (source / "model_best.pth").exists():
        return source
    nested = source / "lucario_rl"
    if (nested / "model_best.pth").exists():
        return nested
    matches = list(source.rglob("model_best.pth"))
    if matches:
        return matches[0].parent
    raise FileNotFoundError(f"could not find model_best.pth under {source}")


def _copy_artifacts(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in (
        "model_best.pth",
        "model_latest.pth",
        "metrics.csv",
        "run_meta.json",
    ):
        path = src / name
        if path.exists():
            shutil.copy2(path, dest / name)


def _summarize_metrics(metrics: Path) -> str:
    if not metrics.exists():
        return "metrics.csv missing"
    with metrics.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return "metrics.csv has no training rows"
    last = rows[-1]
    best = max(rows, key=lambda r: float(r.get("vs_random") or 0.0))
    promotions = sum(1 for r in rows if str(r.get("promoted", "0")) in {"1", "1.0", "true", "True"})
    return (
        f"rows={len(rows)} last_iter={last.get('iter')} "
        f"last_vs_random={last.get('vs_random')} last_gate={last.get('gate_winrate')} "
        f"best_vs_random={best.get('vs_random')}@iter{best.get('iter')} "
        f"promotions={promotions}"
    )


def _run_gate(archive: Path, games: int, only: str | None, name: str) -> Path:
    out = ROOT / "report" / "public_gate" / f"{name}_field.txt"
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "gate_vs_public.py"),
        "--agent",
        str(archive),
        "--games",
        str(games),
    ]
    if only:
        cmd.extend(["--only", only])
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    print(proc.stdout, end="")
    if proc.returncode != 0:
        raise RuntimeError(f"gate failed with exit code {proc.returncode}; log: {out}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Downloaded Kaggle output folder or lucario_rl folder.")
    parser.add_argument("--name", default="track_d_lucario_rl_mcts", help="Candidate archive basename.")
    parser.add_argument(
        "--dest",
        default="report/kaggle_notebook_jobs/lucario/imported",
        help="Local folder where run artifacts are copied.",
    )
    parser.add_argument("--gate-games", type=int, default=0, help="Optional public gate games per opponent.")
    parser.add_argument("--only", help="Optional gate opponent substring, e.g. crustle.")
    args = parser.parse_args(argv)

    src = _artifact_dir(Path(args.source).resolve())
    dest = (ROOT / args.dest).resolve()
    _copy_artifacts(src, dest)

    model = dest / "model_best.pth"
    meta = dest / "run_meta.json"
    metrics = dest / "metrics.csv"
    if not model.exists():
        raise FileNotFoundError(f"missing imported model: {model}")

    archive = ARCHIVE_DIR / f"{args.name}.tar.gz"
    build(
        deck_path=ROOT / "agent_decks" / "real_mega_lucario_ex.csv",
        archive_path=archive,
        scorer="lucario_mcts",
        model_path=model,
        meta_path=meta if meta.exists() else None,
    )
    dry_run_import(archive)

    print(f"imported: {src}")
    print(f"copied to: {dest}")
    print(f"metrics: {_summarize_metrics(metrics)}")
    print(f"candidate: {archive} ({archive.stat().st_size / 1024:.1f} KiB)")
    print("dry-run import OK; no Kaggle submission attempted")

    if args.gate_games > 0:
        gate_log = _run_gate(archive, args.gate_games, args.only, args.name)
        print(f"gate log: {gate_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
