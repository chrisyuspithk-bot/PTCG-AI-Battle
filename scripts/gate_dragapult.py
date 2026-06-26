"""Local gate for Dragapult ex agent vs native field opponents (harness).

Uses eval/harness + official opponent brains (R2). Weighted E[win] via field/weights.json.

  python scripts/gate_dragapult.py --games 20 --suite full --weighted --report
  python scripts/gate_dragapult.py --games 30 --suite lucario --weighted
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
    gate_dragapult_matchups,
    print_harness_summary,
    write_gate_report,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--suite", choices=["core", "full", "lucario", "alakazam"], default="full")
    ap.add_argument("--opponents", nargs="*", default=None)
    ap.add_argument("--weighted", action="store_true", help="Print weighted E[win] from field/weights.json")
    ap.add_argument("--hero-deck", default=None, help="Hero deck CSV (default: dragapult_ex_sample.csv)")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    opponents = args.opponents or opponents_for_suite(args.suite)
    result = gate_dragapult_matchups(
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
        path = write_gate_report(result, stem="gate_dragapult", title="Dragapult agent gate")
        print(f"\nReport: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
