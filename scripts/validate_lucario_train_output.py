#!/usr/bin/env python3
"""Quick validation of rl_mcts_field train outputs."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
work = ROOT / "rl_mcts_field/lucarioex_v1"


def main() -> int:
    metrics = work / "metrics.csv"
    if not metrics.exists():
        print("FAIL: no metrics.csv")
        return 1

    rows = list(csv.DictReader(metrics.open(encoding="utf-8")))
    evals = [r for r in rows if r["phase"] == "eval"]
    trains = [r for r in rows if r["phase"] == "train"]

    print("=== SETUP CHECK ===")
    meta_path = work / "run_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    expected_opps = 10
    n_opps = len(meta.get("opponents", []))
    print(f"opponents in run_meta: {n_opps} (expect {expected_opps})")
    print(f"train_deck: {meta.get('train_deck')}")
    print(f"config: d={meta['config']['LUC_D_MODEL']} search={meta['config']['LUC_SEARCH_COUNT']}")

    print("\n=== METRICS COVERAGE ===")
    eval_cycles = sorted({int(r["cycle"]) for r in evals})
    train_cycles = sorted({int(r["cycle"]) for r in trains})
    print(f"eval cycles: {eval_cycles}")
    print(f"train cycles completed: {train_cycles}")
    last_eval = max(eval_cycles)
    incomplete = last_eval not in train_cycles
    if incomplete:
        print(f"NOTE: cycle {last_eval} eval done but train row missing (crash mid-cycle)")

    by_opp: dict[str, dict[int, float]] = defaultdict(dict)
    for r in evals:
        by_opp[r["opponent"]][int(r["cycle"])] = float(r["wr_pct"])

    print(f"\n=== MATCHUP TABLE (cycle 0 -> {last_eval}) ===")
    gaps, wins = [], []
    for opp in sorted(by_opp):
        c0 = by_opp[opp].get(0, 0.0)
        cl = by_opp[opp].get(last_eval, 0.0)
        delta = cl - c0
        tag = "GAP" if cl < 30 else ("improved" if delta >= 10 else "")
        line = f"  {opp:32} {c0:5.1f}% -> {cl:5.1f}% ({delta:+.1f})"
        if tag:
            line += f"  [{tag}]"
        print(line)
        if cl < 30:
            gaps.append(opp)
        if cl >= 60:
            wins.append(opp)

    print("\n=== TRAIN ROWS (champion gate) ===")
    for r in trains:
        print(
            f"  cycle {r['cycle']}: mean_eval={r['wr_pct']}% loss={r['loss']} "
            f"promoted={r['promoted']} samples={r['n_samples']}"
        )
    promoted_through = max(int(r["cycle"]) for r in trains if r["promoted"] == "1")
    mean_last = sum(by_opp[o][last_eval] for o in by_opp) / len(by_opp)
    print(f"\nEqual-weight mean WR cycle {last_eval}: {mean_last:.1f}%")
    print(f"model_best last promoted after cycle: {promoted_through}")
    print(f"Strong matchups (>=60% cycle {last_eval}): {len(wins)}")
    print(f"Gap matchups (<30%): {gaps}")

    print("\n=== ARTIFACTS ===")
    for name in ["model_best.pth", "model_latest.pth", "model4.pth", "train.log"]:
        p = work / name
        print(f"  {name}: {'OK' if p.exists() else 'MISSING'} ({p.stat().st_size // 1024} KiB)" if p.exists() else f"  {name}: MISSING")

    if meta.get("cycles") != len(train_cycles):
        print(f"\nWARN: run_meta cycles={meta.get('cycles')} != completed train cycles={len(train_cycles)} (stale meta)")

    print("\n=== ACTIONABLE FOR R1/R2 (rules-first plan) ===")
    print("  Phase 2 lever targets (RL also 0%):", ", ".join(gaps) if gaps else "none")
    print("  Do NOT trust RL alone on gaps — add matchup levers per TASKS R2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
