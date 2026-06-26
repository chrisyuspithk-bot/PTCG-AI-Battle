"""Phase-2 gate: SearchScorer vs field opponents (home-grown 660.5 mu bar).

  python scripts/gate_search.py --games 30 --suite full --report
  python scripts/gate_search.py --games 30 --hero-deck agent_decks/real_mega_lucario_ex.csv --report
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
    gate_search_matchups,
    print_harness_summary,
    write_gate_report,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--suite", choices=["core", "full", "alakazam"], default="full")
    ap.add_argument("--opponents", nargs="*", default=None)
    ap.add_argument("--weighted", action="store_true")
    ap.add_argument(
        "--hero-deck",
        default=None,
        help="Hero deck CSV (default: real_mega_lucario_ex.csv)",
    )
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    opponents = args.opponents or opponents_for_suite(args.suite)
    result = gate_search_matchups(
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
        path = write_gate_report(
            result,
            stem="gate_search",
            title="SearchScorer gate",
        )
        print(f"\nReport: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
