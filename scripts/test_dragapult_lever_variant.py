#!/usr/bin/env python3
"""Dragapult Phase 2b lever variants via harness (no monkey-patch).

  python scripts/test_dragapult_lever_variant.py --archetype lucario_mirror --all-variants --games 20
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.dragapult_levers import DRAGAPULT_LEVERS, DragapultLeverDeltas  # noqa: E402
from eval.field_registry import opponents_for_suite  # noqa: E402
from eval.gates import compute_weighted_summary, gate_dragapult_matchups, print_harness_summary, print_weighted_summary  # noqa: E402
from eval.harness import clear_caches  # noqa: E402

VARIANTS: dict[str, dict[str, dict[str, float]]] = {
    "lucario_mirror": {
        "baseline": {"boss_orders_hand": 0.0, "boss_orders_play": 0.0},
        "v1": {"boss_orders_hand": 20_000.0, "boss_orders_play": 10_000.0},
        "v2": {"boss_orders_hand": 20_000.0, "boss_orders_play": 0.0},
        "v3": {"boss_orders_hand": 0.0, "boss_orders_play": 15_000.0},
    },
}

ARCHETYPE_SUITE: dict[str, str] = {
    "lucario_mirror": "lucario",
}


def build_override(archetype: str, variant_key: str) -> dict[str, DragapultLeverDeltas]:
    variants = VARIANTS.get(archetype)
    if not variants or variant_key not in variants:
        raise ValueError(f"unknown variant {variant_key} for {archetype}")
    base = DRAGAPULT_LEVERS.get(archetype, DragapultLeverDeltas())
    fields = variants[variant_key]
    modified = replace(base, **fields)
    return {archetype: modified}


def run_variant(archetype: str, variant_key: str, games: int) -> dict:
    clear_caches()
    overrides = build_override(archetype, variant_key)
    suite = ARCHETYPE_SUITE.get(archetype, "lucario")
    opponents = opponents_for_suite(suite)
    result = gate_dragapult_matchups(
        games_per_opp=games,
        opponents=opponents,
        lever_overrides=overrides,
    )
    wsum = compute_weighted_summary(result)
    print(f"\n{'=' * 70}")
    print(f"VARIANT {variant_key} — dragapult {archetype}")
    print(f"  overrides: {overrides[archetype]}")
    print(f"{'=' * 70}")
    print_harness_summary(result, weighted=True)

    m = result.matchups[0] if result.matchups else None
    wr = m.wr_pct if m else result.overall_wr_pct
    return {
        "variant": variant_key,
        "wr_pct": wr,
        "weighted_e_win": wsum.expected_win_pct,
        "ci_low": m.ci_low_pct if m else result.overall_ci_low_pct,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archetype", default="lucario_mirror", choices=sorted(VARIANTS.keys()))
    ap.add_argument("--variant", default="v1")
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--all-variants", action="store_true")
    args = ap.parse_args()

    keys = list(VARIANTS[args.archetype].keys()) if args.all_variants else [args.variant]
    if args.all_variants and "baseline" in keys:
        keys = ["baseline"] + [k for k in keys if k != "baseline"]

    results = []
    baseline_wr = None
    baseline_w = None
    for key in keys:
        r = run_variant(args.archetype, key, args.games)
        results.append(r)
        if key == "baseline":
            baseline_wr = r["wr_pct"]
            baseline_w = r["weighted_e_win"]

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
    for r in results:
        v = r["variant"]
        if baseline_wr is not None and v != "baseline":
            imp = r["wr_pct"] - baseline_wr
            wimp = r["weighted_e_win"] - (baseline_w or 0)
            flag = "OK" if imp > 5.0 and r["ci_low"] > 0 else "--"
            print(f"  {flag} {v:10s}: {r['wr_pct']:5.1f}% ({imp:+5.1f}pp)  weighted {r['weighted_e_win']:.1f}% ({wimp:+.1f}pp)")
        else:
            print(f"     {v:10s}: {r['wr_pct']:5.1f}%  weighted {r['weighted_e_win']:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
