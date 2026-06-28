# Ladder best so far

**Updated:** 2026-06-28 · **Posture:** record every probe; keep iterating small changes toward higher μ.

## Current best (replace when a probe beats this on ladder)

| Ref | Brain × deck | **μ** | Peak μ | Notes |
|-----|--------------|------:|-------:|-------|
| **54083197** | archaludon_rules+R7 × archaludon_ex_cinderace | **1196.1** | 1224.2 | **Leader** — R12: do not re-upload this ref; keep probing new rows |

## Global rank (all submissions, μ desc)

| Rank | Ref | Brain × deck | **μ** |
|-----:|-----|--------------|------:|
| 1 | **54083197** | Archaludon R7 | **1196.1** |
| 2 | 53989933 | Dragapult v3 | 880.9 |
| 3 | 53950779 | Dragapult v2 | 833.0 |
| 4 | 53869254 | SearchScorer × Lucario | 660.5 |
| 5 | 53913404 | imported Alakazam | 659.0 |

## Archaludon track — full record (same deck, sorted by μ)

| Rank | Ref | Lever | Local gate | **μ** | Δ vs leader | Learnings (brief) |
|-----:|-----|-------|------------|------:|------------:|-------------------|
| 1 | **54083197** | R7 bench guard | 72.7% | **1196.1** | — | 50 ep · 70% WR · prize 10 · no_active 4 |
| 2 | 54088877 | R8a+R8b | 75.3% | 983.8 | −212 | Local gate ↑; ladder no_active 17.9% |
| 3 | 54109878 | R7+R8a | 62.7% | 967.3 | −229 | Promote-only on R7 baseline |
| 4 | 54109826 | R7+R10 | 62.0% | 854.0 | −342 | Global prize-attack boost |
| 5 | 54089078 | R8+R9 | 68.0% | 841.0 | −355 | TO_HAND floor on R8 combo |
| 6 | 54138853 | R7+R11 | 58.7% | 535.6 | −660 | Attach cap when lethal behind |
| 7 | **54139502** | R7+R12 | 70.7% | **PENDING** | — | Dead-active tempo (82062971) |

**Target:** beat **1196.1 μ** on ≥2 ladder readings → new leader. Until then, **54083197** stays Final pin (R12).

**Process:** one small lever change → local gate (filter) → ladder probe → log row here + `eval/ladder_log.csv`.

**Sources:** [`eval/ladder_log.csv`](../eval/ladder_log.csv) · [`eval/AGENT_CATALOG_FULL.md`](../eval/AGENT_CATALOG_FULL.md) · [`report/ladder_history.csv`](ladder_history.csv)

**After each upload:** `python scripts/track_ladder.py` → update `eval/ladder_log.csv`.
