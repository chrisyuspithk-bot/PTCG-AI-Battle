"""Fetch Kaggle episodes/replays and compute per-submission win-rate + turn stats.

Pipeline:
  1. fetch_agent_logs.py --ref <ref>  (episode list + optional logs)
  2. kaggle competitions replay <episode_id> for each episode
  3. parse replay JSON → W/L/D, avg_turns, fast_loss_pct, loss reasons
  4. write report/submission_stats/{ref}_stats.csv
  5. update report/submission_log.csv row for ref

Usage:
  python scripts/analyze_submission.py --ref 53886522
  python scripts/analyze_submission.py --ref 53869254 --skip-fetch
  python scripts/analyze_submission.py --fetch-only --refs 53802029,53880887 --limit 25
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from episode_stats import (  # noqa: E402
    EpisodeRow,
    SubmissionStats,
    aggregate_rows,
    load_json,
    parse_replay,
    resolve_agent_index,
)
from fetch_agent_logs import (  # noqa: E402
    MANIFEST_PATH,
    fetch_episodes_csv,
    fetch_logs_for_ref,
    parse_episodes,
)

STATS_DIR = ROOT / "report" / "submission_stats"
SUBMISSION_LOG = ROOT / "report" / "submission_log.csv"
REPLAYS_DIR = ROOT / "report" / "replays"
LOG_FIELDS = [
    "ref", "date", "scorer", "deck", "mu_initial", "mu_24h",
    "episodes_total", "wins", "losses", "draws", "win_rate",
    "avg_turns", "median_turns", "fast_loss_pct", "top_loss_reason",
    "gate_l1_pct", "notes",
]
EPISODE_FIELDS = [
    "episode_id", "agent_index", "outcome", "turn_count",
    "result_reason", "reward", "episode_type", "source_file",
]

# Top ladder refs → display team name (for per-episode seat resolution without logs).
LEADER_REF_TEAMS: dict[str, str] = {
    "53802029": "TrustHub hiroingk",
    "53880887": "The Debauchery Tea Party",
    "53876944": "foo_foo",
    "53878567": "THIRD PTCG Club",
    "53800247": "カドラバ Kadoraba",
}

OUR_TEAM_NAME = "TomBombadyl"


def _replay_path(episode_id: str) -> Path | None:
    """Resolve local replay JSON (Kaggle CLI uses several naming patterns)."""
    candidates = [
        REPLAYS_DIR / f"{episode_id}.json",
        REPLAYS_DIR / f"episode-{episode_id}-replay.json",
        REPLAYS_DIR / f"top_{episode_id}.json",
        REPLAYS_DIR / f"ref{episode_id}.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _canonical_replay_path(episode_id: str) -> Path:
    return REPLAYS_DIR / f"{episode_id}.json"


def _run_kaggle_replay(episode_id: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    existing = _replay_path(episode_id)
    if existing is not None:
        if existing != dest and not dest.exists():
            shutil.copy2(existing, dest)
        return True
    if dest.exists():
        return True
    with tempfile.TemporaryDirectory(prefix="kaggle_replay_") as tmp:
        proc = subprocess.run(
            ["kaggle", "competitions", "replay", episode_id, "-p", tmp, "-q"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if proc.returncode != 0:
            return False
        candidates = list(Path(tmp).glob("*.json"))
        if not candidates:
            return False
        shutil.copy2(candidates[0], dest)
    return True


def _manifest_agent_index_map(ref: str) -> dict[str, int]:
    """Per-episode agent_index from fetch_agent_logs manifest (seat alternates)."""
    if not MANIFEST_PATH.exists():
        return {}
    by_episode: dict[str, list[tuple[str, int]]] = {}
    with MANIFEST_PATH.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("ref") or "").strip() != ref:
                continue
            ep_id = (row.get("episode_id") or "").strip()
            if not ep_id:
                continue
            try:
                idx = int(row.get("agent_index", 0))
            except ValueError:
                continue
            ep_type = (row.get("episode_type") or "").upper()
            by_episode.setdefault(ep_id, []).append((ep_type, idx))
    out: dict[str, int] = {}
    for ep_id, entries in by_episode.items():
        public = [idx for t, idx in entries if "VALIDATION" not in t]
        if len(public) == 1:
            out[ep_id] = public[0]
        elif public:
            out[ep_id] = public[0]
        elif len(entries) == 1:
            out[ep_id] = entries[0][1]
    return out


def _team_name_for_ref(ref: str) -> str | None:
    if ref in LEADER_REF_TEAMS:
        return LEADER_REF_TEAMS[ref]
    return OUR_TEAM_NAME


def _guess_agent_index(ref: str) -> int:
    """Legacy global fallback when per-episode resolution is unavailable."""
    manifest = _manifest_agent_index_map(ref)
    if manifest:
        counts: dict[int, int] = {0: 0, 1: 0}
        for idx in manifest.values():
            counts[idx] = counts.get(idx, 0) + 1
        return 1 if counts.get(1, 0) > counts.get(0, 0) else 0
    return 0


def _load_manifest_episodes(ref: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if (row.get("ref") or "").strip() == ref:
                    rows.append(row)
    if rows:
        return rows
    csv_text = fetch_episodes_csv(ref)
    episodes = parse_episodes(csv_text)
    return [
        {
            "episode_id": ep["episode_id"],
            "episode_type": ep["type"],
            "episode_state": ep["state"],
        }
        for ep in episodes
    ]


def fetch_replays_for_ref(
    ref: str,
    *,
    limit: int | None = None,
    public_only: bool = True,
) -> tuple[int, int]:
    """Download replay JSON for episodes of ref. Returns (fetched, skipped)."""
    csv_text = fetch_episodes_csv(ref)
    episodes = parse_episodes(csv_text)
    fetched = skipped = 0
    for ep in episodes:
        if public_only and "VALIDATION" in ep["type"].upper():
            continue
        if limit is not None and fetched + skipped >= limit:
            break
        ep_id = ep["episode_id"]
        dest = _canonical_replay_path(ep_id)
        if _replay_path(ep_id) is not None:
            if not dest.exists():
                _run_kaggle_replay(ep_id, dest)
            skipped += 1
            continue
        if _run_kaggle_replay(ep_id, dest):
            fetched += 1
        else:
            print(f"  ! replay {ep_id} download failed", file=sys.stderr)
    return fetched, skipped


def analyze_ref(
    ref: str,
    *,
    agent_index: int | None = None,
    skip_fetch: bool = False,
    public_only: bool = True,
) -> SubmissionStats:
    if not skip_fetch:
        fetch_logs_for_ref(ref, output_dir=ROOT / "report" / "agent_logs", agents=[0, 1])

    manifest_index = _manifest_agent_index_map(ref)
    team_name = _team_name_for_ref(ref)
    global_index = agent_index if agent_index is not None else _guess_agent_index(ref)
    manifest_rows = _load_manifest_episodes(ref)
    episode_rows: list[EpisodeRow] = []

    seen: set[str] = set()
    for meta in manifest_rows:
        ep_id = (meta.get("episode_id") or "").strip()
        if not ep_id or ep_id in seen:
            continue
        ep_type = meta.get("episode_type", "")
        if public_only and ep_type and "VALIDATION" in ep_type.upper():
            continue
        seen.add(ep_id)

        replay_path = _canonical_replay_path(ep_id)
        if _replay_path(ep_id) is None:
            _run_kaggle_replay(ep_id, replay_path)
        elif not replay_path.exists():
            _run_kaggle_replay(ep_id, replay_path)
        data = load_json(replay_path) or load_json(_replay_path(ep_id) or replay_path)
        if not isinstance(data, dict):
            continue
        our_index = resolve_agent_index(
            data,
            manifest_index=manifest_index.get(ep_id),
            team_name=team_name if agent_index is None else None,
            default=global_index,
        )
        if agent_index is not None:
            our_index = agent_index
        row = parse_replay(data, our_agent_index=our_index)
        if row is None:
            continue
        row.episode_id = ep_id
        row.episode_type = ep_type
        row.agent_index = our_index
        episode_rows.append(row)

    return aggregate_rows(ref, episode_rows)


def write_stats_csv(stats: SubmissionStats, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=EPISODE_FIELDS)
        writer.writeheader()
        for row in stats.rows:
            writer.writerow({
                "episode_id": row.episode_id,
                "agent_index": row.agent_index,
                "outcome": row.outcome,
                "turn_count": row.turn_count,
                "result_reason": row.result_reason,
                "reward": row.reward,
                "episode_type": row.episode_type,
                "source_file": f"report/replays/{row.episode_id}.json",
            })


def update_submission_log(stats: SubmissionStats) -> None:
    if not SUBMISSION_LOG.exists():
        return
    rows: list[dict[str, str]] = []
    with SUBMISSION_LOG.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or LOG_FIELDS
        for row in reader:
            if (row.get("ref") or "").strip() == stats.ref:
                row["episodes_total"] = str(stats.episodes_total)
                row["wins"] = str(stats.wins)
                row["losses"] = str(stats.losses)
                row["draws"] = str(stats.draws)
                row["win_rate"] = str(stats.win_rate)
                row["avg_turns"] = str(stats.avg_turns)
                row["median_turns"] = str(stats.median_turns)
                row["fast_loss_pct"] = str(stats.fast_loss_pct)
                row["top_loss_reason"] = stats.top_loss_reason
            rows.append(row)
    with SUBMISSION_LOG.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(stats: SubmissionStats) -> None:
    print(f"ref {stats.ref}")
    print(f"  episodes: {stats.episodes_total}  W/L/D: {stats.wins}/{stats.losses}/{stats.draws}")
    print(f"  win_rate: {stats.win_rate}%")
    print(f"  avg_turns: {stats.avg_turns}  median: {stats.median_turns}")
    print(f"  fast_loss_pct (<15 turns): {stats.fast_loss_pct}%")
    print(f"  top_loss_reason: {stats.top_loss_reason or 'n/a'}")
    if stats.loss_reason_counts:
        print(f"  loss reasons: {dict(stats.loss_reason_counts)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", default=None, help="Submission ref ID")
    parser.add_argument(
        "--refs", default=None,
        help="Comma-separated refs for --fetch-only batch replay download",
    )
    parser.add_argument("--fetch-only", action="store_true",
                        help="Only download replays (no stats); use --ref or --refs")
    parser.add_argument("--limit", type=int, default=25,
                        help="Max public episodes per ref when --fetch-only")
    parser.add_argument("--agent-index", type=int, default=None)
    parser.add_argument("--skip-fetch", action="store_true",
                        help="Do not call fetch_agent_logs (use local manifest/replays only)")
    parser.add_argument("--include-validation", action="store_true")
    args = parser.parse_args(argv)

    if args.fetch_only:
        refs = []
        if args.refs:
            refs.extend(x.strip() for x in args.refs.split(",") if x.strip())
        if args.ref:
            refs.append(args.ref.strip())
        if not refs:
            print("ERROR: --fetch-only requires --ref or --refs", file=sys.stderr)
            return 1
        total_new = total_have = 0
        for ref in refs:
            print(f"fetch replays ref {ref} (limit {args.limit})")
            try:
                n_new, n_have = fetch_replays_for_ref(
                    ref, limit=args.limit, public_only=not args.include_validation,
                )
            except RuntimeError as exc:
                print(f"  ERROR: {exc}", file=sys.stderr)
                continue
            total_new += n_new
            total_have += n_have
            print(f"  new={n_new}  already_local={n_have}")
        print(f"batch done: {total_new} new replay(s), {total_have} already present")
        return 0

    if not args.ref:
        print("ERROR: --ref required unless --fetch-only", file=sys.stderr)
        return 1

    try:
        stats = analyze_ref(
            args.ref.strip(),
            agent_index=args.agent_index,
            skip_fetch=args.skip_fetch,
            public_only=not args.include_validation,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    out_path = STATS_DIR / f"{args.ref}_stats.csv"
    write_stats_csv(stats, out_path)
    update_submission_log(stats)
    print_summary(stats)
    print(f"wrote {out_path.relative_to(ROOT)}")
    print(f"updated {SUBMISSION_LOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
