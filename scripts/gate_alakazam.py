"""Local gate for Alakazam best5 agent vs native field opponents (harness).

  python scripts/gate_alakazam.py --games 30 --suite full --weighted --report
  python scripts/gate_alakazam.py --games 30 --hero-deck agent_decks/top_mined_alakazam.csv --report
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.field_registry import opponents_for_suite  # noqa: E402
from eval.gates import (  # noqa: E402
    gate_alakazam_matchups,
    print_harness_summary,
    write_gate_report,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--suite", choices=["core", "full", "lucario", "alakazam"], default="full")
    ap.add_argument("--opponents", nargs="*", default=None)
    ap.add_argument("--weighted", action="store_true")
    ap.add_argument(
        "--hero-deck",
        default=None,
        help="Hero deck CSV (default: ryotasueyoshi_alakazam_best5.csv)",
    )
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    opponents = args.opponents or opponents_for_suite(args.suite)
    result = gate_alakazam_matchups(
        suite=args.suite,
        games_per_opp=args.games,
        opponents=opponents,
        hero_deck=args.hero_deck,
    )
    if not result.matchups:
        print("No opponents gated.")
        return 1

    print_harness_summary(result, weighted=args.weighted)
    if args.report:
        path = write_gate_report(result, stem="gate_alakazam", title="Alakazam best5 agent gate")
        print(f"\nReport: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
