# Robust deck pool evaluation

Scorer: `search`
Games per matchup: 12
Opponents: 79

| Rank | Deck | Robust | Mean | CVaR | Maximin | Worst |
|---:|---|---:|---:|---:|---:|---|
| 1 | `gen19_fast_basic` | 0.610 | 0.728 | 0.492 | 0.333 | `('a2_kyogre', 0.333)` |
| 2 | `top_mined_trevenant` | 0.574 | 0.694 | 0.453 | 0.250 | `('a2_kyogre', 0.25)` |

Low game counts are for triage only; re-run top decks at higher games before promotion.
CSV: `report\robust_deck_rl\pool_eval_search_top2_g12_20260620\summary.csv` and `report\robust_deck_rl\pool_eval_search_top2_g12_20260620\details.csv`
