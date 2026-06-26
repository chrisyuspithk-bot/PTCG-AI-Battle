#!/usr/bin/env python3
"""Full suite gate — core opponents (dragapult, abomasnow, iono).

Thin CLI over eval/harness.

  python scripts/gate_full_suite_20260626.py --games 20
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.gates import gate_matchups, print_harness_summary, write_gate_report  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    print("\n" + "=" * 70)
    print("FULL SUITE GATE — core opponents")
    print("=" * 70)

    result = gate_matchups(suite="core", games_per_opp=args.games)
    if not result.matchups:
        print("No results!")
        return 1

    print()
    print_harness_summary(result)
    if args.report:
        path = write_gate_report(result, stem="gate_full_suite", title="Full suite gate (core)")
        print(f"\nReport: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
