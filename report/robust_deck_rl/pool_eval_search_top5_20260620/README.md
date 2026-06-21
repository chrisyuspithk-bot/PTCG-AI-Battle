# Robust deck pool evaluation

Scorer: `search`
Games per matchup: 6
Opponents: 79

| Rank | Deck | Robust | Mean | CVaR | Maximin | Worst |
|---:|---|---:|---:|---:|---:|---|
| 1 | `top_mined_trevenant` | 0.556 | 0.689 | 0.423 | 0.000 | `('a2_big_basic', 0.0)` |
| 2 | `gen19_fast_basic` | 0.544 | 0.709 | 0.379 | 0.167 | `('033_lucario__w1.00', 0.167)` |
| 3 | `robust_deck_rl/best_deck` | 0.529 | 0.670 | 0.388 | 0.000 | `('a2_basic_heavy_31_energy', 0.0)` |
| 4 | `a2_kyogre_33_energy` | 0.521 | 0.676 | 0.366 | 0.000 | `('a2_kyogre', 0.0)` |
| 5 | `gen19_spread_control` | 0.488 | 0.632 | 0.343 | 0.000 | `('a2_kyogre', 0.0)` |

Low game counts are for triage only; re-run top decks at higher games before promotion.
CSV: `report\robust_deck_rl\pool_eval_search_top5_20260620\summary.csv` and `report\robust_deck_rl\pool_eval_search_top5_20260620\details.csv`
