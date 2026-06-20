"""Promote a packaged candidate after L1 gate; append to submission_log.csv.

Usage:
  python scripts/promote_candidate.py --name track_c_lucario_rulecore_smartbench --scorer lucario --deck agent_decks/real_mega_lucario_ex.csv --gate-games 12
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "dist" / "candidates"
SUBMISSION_LOG = ROOT / "report" / "submission_log.csv"
LOG_FIELDS = [
    "ref", "date", "scorer", "deck", "mu_initial", "mu_24h",
    "episodes_total", "wins", "losses", "draws", "win_rate",
    "avg_turns", "median_turns", "fast_loss_pct", "top_loss_reason",
    "gate_l1_pct", "notes",
]
PYTHON = sys.executable


def run_l1(archive: Path, games: int) -> tuple[float, str]:
    proc = subprocess.run(
        [PYTHON, "scripts/gate_vs_public.py", "--agent", str(archive), "--games", str(games)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    pct = 0.0
    for line in out.splitlines():
        if "SUITE MEAN:" in line:
            try:
                pct = float(line.split("SUITE MEAN:")[1].split("%")[0].strip())
            except ValueError:
                pass
    return pct, out[-2000:]


def append_log_row(row: dict[str, str]) -> None:
    exists = SUBMISSION_LOG.exists()
    with SUBMISSION_LOG.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_FIELDS, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Candidate tarball basename (without .tar.gz)")
    parser.add_argument("--scorer", required=True)
    parser.add_argument("--deck", required=True)
    parser.add_argument("--gate-games", type=int, default=12)
    parser.add_argument("--min-gate-pct", type=float, default=20.0)
    parser.add_argument("--notes", default="")
    parser.add_argument("--ref", default="", help="Kaggle ref after submit (optional)")
    args = parser.parse_args(argv)

    archive = CANDIDATES / f"{args.name}.tar.gz"
    if not archive.exists():
        print(f"ERROR: missing {archive}", file=sys.stderr)
        return 1

    pct, snippet = run_l1(archive, args.gate_games)
    print(f"L1 public gate: {pct:.1f}% ({args.gate_games} games/opponent)")
    if pct < args.min_gate_pct:
        print(f"FAIL: below min {args.min_gate_pct}%", file=sys.stderr)
        print(snippet[-800:])
        return 1

    append_log_row({
        "ref": args.ref or "pending",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "scorer": args.scorer,
        "deck": args.deck,
        "mu_initial": "",
        "mu_24h": "",
        "gate_l1_pct": str(round(pct, 1)),
        "notes": args.notes or f"promoted after L1 gate {pct:.1f}%",
    })
    print(f"PASS — appended to {SUBMISSION_LOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
