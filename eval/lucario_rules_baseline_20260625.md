# Lucario Rules Baseline Gate (2026-06-25)

**Date:** 2026-06-25 10:16 UTC  
**Scope:** LucarioScorer (rules only) with integrated matchup levers  
**Config:** 10 games/opponent, seat-swapped, Wilson 95% CI  

## Results

| Opponent | WR% | Games | CI Low | CI High | Status |
|----------|-----|-------|--------|---------|--------|
| dragapult_ex_sample | 20.0% | 10 | 5.7% | 51.0% | **GAP** |
| real_mega_abomasnow_ex | 30.0% | 10 | 10.8% | 60.3% | — |
| real_iono | 40.0% | 10 | 16.8% | 68.7% | — |
| **OVERALL** | **30.0%** | **30** | **16.7%** | **47.9%** | — |

## Interpretation

### What this means

1. **Dragapult (20%):** Severe weakness. Levers are active but insufficient. Need specialized strategy or new lever weights.
2. **Abomasnow (30%):** Below acceptable (target 50+%). Bulk water Pokémon still winning.
3. **Iono (40%):** Challenging but closest to acceptable. Electric-type disruption model is problematic.

### Why levers aren't working

**Hypothesis (unvalidated):**
- Lever magnitudes are hypothetical starting values (see `matchup_levers.py` comments: "Values are starting hypotheses — each row must pass L1 re-gate before trust")
- Dragapult specifically: gust_setup_pokemon=600 (Dreepy/Drakloak) may not translate to board detection (e.g., if opponent hasn't yet played Dreepy)
- Boss_orders=700 is active but may be competing with other high-value plays

### Next steps (blocked pending decision)

**Two paths:**
1. **Iterate levers locally:** Tweak boss_orders, gust_setup_pokemon magnitudes; re-gate each change
2. **Check Lucario v5 ladder validation:** If μ < 500, rules baseline may have a deeper issue (train/serve skew); don't iterate levers until validated

**Recommendation:** Await Lucario v5 ladder μ check from user (ref 53995982 on Kaggle). If μ >= 600, proceed with lever iteration. If μ < 500, investigate why RL/MCTS underperforms rules on ladder.

## Files Generated

- `scripts/gate_lucario_rules.py` — Rules-only gate (no torch dependency)
- `eval/lucario_rules_baseline_20260625.md` — This report

## Next Session

- User input: Lucario v5 (ref 53995982) final μ from ladder
- Decision gate: Validate rules baseline vs Dragapult best (850.5 μ)
- Task: R2 lever iteration (if validation passes) OR debug train/serve skew (if validation fails)
