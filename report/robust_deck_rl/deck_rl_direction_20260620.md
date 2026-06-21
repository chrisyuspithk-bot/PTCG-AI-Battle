# Deck RL direction (2026-06-20)

## Position

Deck formation and policy are coupled. For top-level ladder play, pick the deck from
a robustness screen first, then train/distill the strategy for that deck. Do not
keep optimizing Lucario policy if the deck itself has collapse matchups against
the mined field.

## What changed this run

- Confirmed Python313 GPU path: `torch 2.11.0+cu128`, CUDA available.
- Added `scripts/robust_deck_search.py --out-dir` so robust campaigns do not overwrite
  prior evidence.
- Patched `scripts/arena.py` so `workers=1` runs in-process. This avoids Windows
  `PermissionError: [WinError 5] Access is denied` from multiprocessing spawn during
  long robust runs.
- Added `scripts/evaluate_robust_deck_pool.py` to rank known deck candidates against
  the same benchmark + mined gauntlet used by robust search.

## Robust gauntlet

Current gauntlet: 79 deduplicated opponents:

- benchmark suite including leader Alakazam/Trevenant variants
- repo deck candidates under `agent_decks/`
- mined ladder decks under `report/deck_rl/mined_decks/`

This is a better offline proxy for "the whole field" than a fixed public pool.

## Robust search result

Command:

```bash
C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe scripts/robust_deck_search.py --generations 4 --population 6 --games 3 --workers 1 --scorer search --surrogate --out-dir report/robust_deck_rl/search_scorer_stable_20260620
```

Result:

- CUDA surrogate backend: `torch-cuda`
- Best robust score: `0.143`
- Best mean: `0.561`
- Maximin: `0.000`
- Outcome: not enough. The mutation search still finds decks with hard zero-win
  matchups in the expanded mined gauntlet.

Interpretation: do not run longer blindly. Use the known deck pool to choose a
stronger starting deck family, then train policy for that deck.

## Known deck pool screen

Top-5 higher-game triage:

Command:

```bash
python scripts/evaluate_robust_deck_pool.py --games 6 --workers 1 --scorer search --decks report/robust_deck_rl/best_deck.csv,agent_decks/deck_rl/gen19_fast_basic.csv,agent_decks/a2_kyogre_33_energy.csv,agent_decks/top_mined_trevenant.csv,agent_decks/deck_rl/gen19_spread_control.csv --output report/robust_deck_rl/pool_eval_search_top5_20260620
```

| Rank | Deck | Robust | Mean | CVaR | Maximin | Worst |
|---:|---|---:|---:|---:|---:|---|
| 1 | `top_mined_trevenant` | 0.556 | 0.689 | 0.423 | 0.000 | `a2_big_basic` |
| 2 | `gen19_fast_basic` | 0.544 | 0.709 | 0.379 | 0.167 | `033_lucario__w1.00` |
| 3 | `robust_deck_rl/best_deck` | 0.529 | 0.670 | 0.388 | 0.000 | `a2_basic_heavy_31_energy` |
| 4 | `a2_kyogre_33_energy` | 0.521 | 0.676 | 0.366 | 0.000 | `a2_kyogre` |
| 5 | `gen19_spread_control` | 0.488 | 0.632 | 0.343 | 0.000 | `a2_kyogre` |

Full outputs:

- `report/robust_deck_rl/pool_eval_search_top5_20260620/README.md`
- `report/robust_deck_rl/pool_eval_search_top5_20260620/summary.csv`
- `report/robust_deck_rl/pool_eval_search_top5_20260620/details.csv`

## Decision

Prioritize these deck families for the next RL / policy pairing:

1. `top_mined_trevenant.csv` - best robust score in the top-5 screen; matches live leader archetype.
2. `gen19_fast_basic.csv` - best mean and only top-5 deck with nonzero maximin in this low-game pass.
3. Existing `report/robust_deck_rl/best_deck.csv` - still competitive but has a zero-collapse matchup.

Lucario remains useful as a protected live baseline, but its deck is not the best
offline starting point for robust deck RL.

## Exact next experiment

Completed higher-confidence two-deck screen:

```bash
python scripts/evaluate_robust_deck_pool.py --games 12 --workers 1 --scorer search --decks agent_decks/top_mined_trevenant.csv,agent_decks/deck_rl/gen19_fast_basic.csv --output report/robust_deck_rl/pool_eval_search_top2_g12_20260620
```

Result:

| Rank | Deck | Robust | Mean | CVaR | Maximin | Worst |
|---:|---|---:|---:|---:|---:|---|
| 1 | `gen19_fast_basic` | 0.610 | 0.728 | 0.492 | 0.333 | `a2_kyogre` |
| 2 | `top_mined_trevenant` | 0.574 | 0.694 | 0.453 | 0.250 | `a2_kyogre` |

## Updated next action

Promote `agent_decks/deck_rl/gen19_fast_basic.csv` as the next deck-RL / Track B
target because it won the top-2 robust screen and already has prior Track B success.
Keep `top_mined_trevenant.csv` as the next leader-archetype follow-up.

Do not submit either without L1/L2 gates and explicit user approval.
