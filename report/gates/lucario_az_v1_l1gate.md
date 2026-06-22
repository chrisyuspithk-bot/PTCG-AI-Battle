# Lucario AZ v1 — L1 Gate Results (2026-06-22)

## Validation Results

**Status:** ❌ FAIL  
**Suite Mean:** 9.7% (35/360 decided)  
**Individual Matchups:**
- 0.0% vs pokemon-tcg-ai-battle-1084-5-baseline (0-30)
- 3.3% vs ptcg-public-915-lucario-search-baseline (1-29)
- 3.3% vs simple-baseline-matchup-tests (1-29)
- 6.7% vs crustle-aware-mega-lucario-ex-anti-wall (2-28)
- 6.7% vs public-scores-915 (2-28)
- 10.0% vs a-sample-rule-based-agent-dragapult-ex-deck (3-27)
- 10.0% vs a-sample-rule-based-agent-iono-s-deck (3-27)
- 10.0% vs rule-based-not-psychic-alakazam-best-5th (3-27)
- 13.3% vs a-sample-rule-based-agent-mega-abomasnow-ex-deck (4-26)
- 13.3% vs beating-the-day-1-1-crustle-bot (4-26)
- 16.7% vs top-dragapult-ex-tempo-control-agent (5-25)
- 23.3% vs a-sample-rule-based-agent-mega-lucario-ex-deck (7-23)

## Analysis

### Overfitting Diagnosis

**Internal eval (v1 training history.json):**
- Mirror: 56% WR ✅ (trained on `real_mega_lucario_ex`)
- Alakazam: 6% WR (trained on `top_mined_alakazam`)

**External eval (public field L1-gate):**
- Mirror (public-915-lucario-baseline): 3.3% WR ❌
- Suite mean: 9.7% ❌

**Root cause:** Model overfit to the two specific training opponents. Public field uses different deck lists, piloting strategies, and meta-matchups.

### Model Quality Assessment

- **Not submission-ready** (typically need >30% suite mean for ladder viability)
- **Internal validation passed** but external validation collapsed
- **Indicates:** Architecture is sound, but training data/opponent model too narrow

## Next Steps (Fix #3: Realistic MCTS Opponent Prior)

**Required to unlock this approach:**
1. Expand opponent pool in AZ training to include diverse public baseline decks
2. Use realistic opponent policy/evaluation (not simplified `SearchOpponent` or placeholder)
3. Retrain with MCTS against realistic opponent mix
4. Re-gate; target >30% suite mean

**Alternative:** Defer AZ approach; focus on simpler search/BC improvements to Lucario or Alakazam.

**Recommendation:** Document as exploratory failure; pivot to other T16 research tracks.
