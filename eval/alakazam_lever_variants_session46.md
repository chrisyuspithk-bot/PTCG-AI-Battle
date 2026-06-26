# Alakazam R2 lever sweep — Session 46

**Date:** 2026-06-26  
**Script:** `scripts/test_lever_variant.py --archetype alakazam_psychic --all-variants --games 20`  
**Opponent:** `top_mined_alakazam` (random pilot — no official Kaggle sample)

## Results

| Variant | boss_orders | gust | WR% | vs baseline |
|---------|------------:|-----:|----:|------------:|
| baseline | 600 | 500 | 100.0 | — |
| v1 | 800 | 700 | 100.0 | +0.0pp |
| v2 | 800 | 500 | 100.0 | +0.0pp |
| v3 | 600 | 700 | 100.0 | +0.0pp |

## Verdict: **INCONCLUSIVE — no lever change**

- All variants 20–0 vs random pilot (ceiling effect).
- No winner >5pp; `matchup_levers.py` **unchanged**.
- **Next:** import Alakazam best5 rule pilot (`notebooks/ryotasueyoshi_rule_based_alakazam_best5/`) or gate vs public agent before further Alakazam lever sweeps.

Raw log: `eval/alakazam_lever_variants_session46.txt`
