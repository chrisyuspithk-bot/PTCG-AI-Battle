"""Phase-2 gate: LucarioScorer (rules only) vs field opponents.

Thin CLI over eval/harness + eval/gates. Local filter only — not ladder truth.

  python scripts/gate_lucario_rules.py --games 20
  python scripts/gate_lucario_rules.py --games 20 --suite core
  python scripts/gate_lucario_rules.py --games 20 --opponents dragapult_ex_sample real_mega_abomasnow_ex
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.field_registry import opponents_for_suite  # noqa: E402
from eval.gates import gate_matchups, print_harness_summary, write_gate_report  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--suite", choices=["core", "full", "alakazam"], default="full")
    ap.add_argument("--opponents", nargs="*", default=None)
    ap.add_argument("--report", action="store_true", help="Write eval/gates_*.md report")
    ap.add_argument("--weighted", action="store_true", help="Print weighted E[win]")
    args = ap.parse_args()

    opponents = args.opponents or opponents_for_suite(args.suite)
    result = gate_matchups(
        suite=args.suite,
        games_per_opp=args.games,
        opponents=opponents,
    )

    if not result.matchups:
        print("No opponents gated.")
        return 1

    print_harness_summary(result, weighted=args.weighted)
    if args.report:
        path = write_gate_report(
            result,
            stem="gate_lucario_rules",
            title="LucarioScorer rules gate",
        )
        print(f"\nReport: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
