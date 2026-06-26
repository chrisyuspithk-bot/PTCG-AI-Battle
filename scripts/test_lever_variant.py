#!/usr/bin/env python3
"""Generic lever variant gate via eval/harness (no monkey-patch).

Usage:
  python scripts/test_lever_variant.py --archetype alakazam_psychic --variant v1 --games 20
  python scripts/test_lever_variant.py --archetype alakazam_psychic --all-variants --games 20
  python scripts/test_lever_variant.py --archetype abomasnow_water --all-variants --games 20
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.matchup_levers import LUCARIO_LEVERS, LeverDeltas  # noqa: E402
from eval.field_registry import load_registry, opponents_for_suite  # noqa: E402
from eval.gates import gate_matchups, print_harness_summary  # noqa: E402
from eval.harness import clear_caches  # noqa: E402

# Per-archetype variant definitions (delta fields only).
ARCHETYPE_VARIANTS: dict[str, dict[str, dict[str, float]]] = {
    "alakazam_psychic": {
        "baseline": {"boss_orders": 600.0, "gust_setup_pokemon": 500.0},
        "v1": {"boss_orders": 800.0, "gust_setup_pokemon": 700.0},
        "v2": {"boss_orders": 800.0, "gust_setup_pokemon": 500.0},
        "v3": {"boss_orders": 600.0, "gust_setup_pokemon": 700.0},
    },
    "abomasnow_water": {
        "baseline": {"boss_orders": 1000.0, "gust_setup_pokemon": 800.0},
        "v1": {"boss_orders": 1200.0, "gust_setup_pokemon": 1000.0},
        "v2": {"boss_orders": 1200.0, "gust_setup_pokemon": 800.0},
        "v3": {"boss_orders": 1000.0, "gust_setup_pokemon": 1000.0},
    },
    "dragapult_psychic": {
        "baseline": {"boss_orders": 900.0, "gust_setup_pokemon": 600.0},
        "v1": {"boss_orders": 1100.0, "gust_setup_pokemon": 800.0},
    },
}

ARCHETYPE_OPPONENT_SUITE: dict[str, str] = {
    "alakazam_psychic": "alakazam",
    "abomasnow_water": "core",  # single-opp filter below
    "dragapult_psychic": "core",
}

SINGLE_OPPONENT: dict[str, str] = {
    "abomasnow_water": "real_mega_abomasnow_ex",
    "dragapult_psychic": "dragapult_ex_sample",
}


def build_override(archetype: str, variant_key: str) -> dict[str, LeverDeltas]:
    variants = ARCHETYPE_VARIANTS.get(archetype)
    if not variants or variant_key not in variants:
        raise ValueError(f"unknown variant {variant_key} for {archetype}")
    base = LUCARIO_LEVERS.get(archetype)
    if base is None:
        raise ValueError(f"unknown archetype: {archetype}")
    fields = variants[variant_key]
    modified = replace(base, **fields)
    return {archetype: modified}


def opponents_for_archetype(archetype: str) -> list[str]:
    if archetype in SINGLE_OPPONENT:
        return [SINGLE_OPPONENT[archetype]]
    suite = ARCHETYPE_OPPONENT_SUITE.get(archetype, "alakazam")
    return opponents_for_suite(suite)


def run_variant(
    archetype: str,
    variant_key: str,
    games: int,
) -> dict:
    clear_caches()
    overrides = build_override(archetype, variant_key)
    opponents = opponents_for_archetype(archetype)
    result = gate_matchups(
        games_per_opp=games,
        opponents=opponents,
        lever_overrides=overrides,
    )
    if not result.matchups:
        return {"error": "no matchups", "variant": variant_key}

    m = result.matchups[0] if len(result.matchups) == 1 else None
    if m is None:
        wr = result.overall_wr_pct
        lo, hi = result.overall_ci_low_pct, result.overall_ci_high_pct
        opp_label = ",".join(opponents)
    else:
        wr = m.wr_pct
        lo, hi = m.ci_low_pct, m.ci_high_pct
        opp_label = m.opponent

    print(f"\n{'=' * 70}")
    print(f"VARIANT: {variant_key} — archetype {archetype}")
    print(f"  opponent(s): {opp_label}")
    print(f"  overrides: {overrides[archetype]}")
    print(f"{'=' * 70}")
    print_harness_summary(result)

    return {
        "variant": variant_key,
        "archetype": archetype,
        "wr_pct": wr,
        "ci_low_pct": lo,
        "ci_high_pct": hi,
        "wins": m.wins if m else result.overall_wins,
        "losses": m.losses if m else (result.overall_games - result.overall_wins),
        "opponent": opp_label,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archetype", required=True, choices=sorted(ARCHETYPE_VARIANTS.keys()))
    ap.add_argument("--variant", default="v1")
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--all-variants", action="store_true")
    args = ap.parse_args()

    variants = ARCHETYPE_VARIANTS[args.archetype]
    keys = list(variants.keys()) if args.all_variants else [args.variant]
    if args.all_variants and "baseline" not in keys:
        keys = ["baseline"] + [k for k in keys if k != "baseline"]

    results = []
    baseline_wr = None
    baseline_lo = None

    for key in keys:
        r = run_variant(args.archetype, key, args.games)
        results.append(r)
        if key == "baseline" and "wr_pct" in r:
            baseline_wr = r["wr_pct"]
            baseline_lo = r["ci_low_pct"]

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    winners = []
    for r in results:
        if "error" in r:
            continue
        v = r["variant"]
        wr = r["wr_pct"]
        if baseline_wr is not None and v != "baseline":
            imp = wr - baseline_wr
            ci_ok = r["ci_low_pct"] > (baseline_lo or 0)
            met = imp > 5.0 and ci_ok
            if met:
                winners.append(r)
            flag = "OK" if met else "--"
            print(f"  {flag} {v:10s}: {wr:5.1f}% ({imp:+5.1f}pp vs baseline, CI low {r['ci_low_pct']:.1f}%)")
        else:
            print(f"     {v:10s}: {wr:5.1f}%")

    if winners:
        best = max(winners, key=lambda x: x["wr_pct"])
        print(f"\nBest: {best['variant']} @ {best['wr_pct']:.1f}%")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
