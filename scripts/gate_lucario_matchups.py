"""Phase-2 gate: LucarioScorer vs extended field opponents.

Thin CLI over eval/harness. Decks without an official sample are skipped unless
listed in field/registry.json with opponent_brain=random.

  python scripts/gate_lucario_matchups.py --games 30
  python scripts/gate_lucario_matchups.py --games 20 --suite full
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.field_registry import load_registry, opponents_for_suite  # noqa: E402
from eval.gates import gate_matchups, print_harness_summary  # noqa: E402

# Extended list for matchups script (mined variants + registry full suite).
EXTENDED_OPPONENTS = [
    "dragapult_ex_sample",
    "real_mega_abomasnow_ex",
    "real_iono",
    "real_dragapult_ex",
    "real_mega_lucario_ex",
    "top_mined_mega_abomasnow_ex",
    "top_mined_iono",
    "top_mined_dragapult_ex",
    "top_mined_mega_lucario_ex",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=30)
    ap.add_argument("--suite", choices=["core", "full", "alakazam"], default=None)
    ap.add_argument("--opponents", nargs="*", default=None)
    ap.add_argument(
        "--allow-random",
        action="store_true",
        help="Include registry opponents that use random pilot (e.g. alakazam suite)",
    )
    args = ap.parse_args()

    if args.opponents:
        opponents = args.opponents
    elif args.suite:
        opponents = opponents_for_suite(args.suite)
    else:
        opponents = EXTENDED_OPPONENTS

    if args.allow_random:
        reg = load_registry()
        for stem, meta in reg["opponents"].items():
            if meta.get("opponent_brain") == "random" and stem not in opponents:
                opponents = list(opponents) + [stem]

    result = gate_matchups(games_per_opp=args.games, opponents=opponents)

    if not result.matchups:
        print("\nNo opponents gated.")
        return 1

    print_harness_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
