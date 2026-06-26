# Ladder best so far — 2026-06-22

> **Not the finish line.** 850.5 μ is our **best result to date** — the **bar every next agent must
> beat**. Field top ~1350; mid-pack ~1100+. We **expect and need** to exceed this.

## Current best (interim)

| Field | Value |
|-------|-------|
| Archive | `dragapult_ex_sample.tar.gz` |
| Kaggle ref | **53950779** |
| Public μ | **850.5** (best so far) |
| Status | COMPLETE |
| Agent | Official Crispin Dragapult ex sample + never-crash wrapper (`agent/dragapult_agent.py`) |
| Deck | `agent_decks/dragapult_ex_sample.csv` (60-card organizer list) |

## Why it matters (not why we stop)

- **Highest μ we have shipped so far** — replaces prior ceiling SearchScorer×Lucario (668).
- Beats **Lucario RL+MCTS model4 (643.9)** on ladder despite strong local eval.
- **Rules-only** — validates official pilots + stability wrapper; still far below field top (~1350).
- **Every probe, lever tune, and train run is gated vs beating 850.5** before it counts as progress.

## Path to 850.5

1. v1 submit (ref 53950246) → **ERROR** (`__file__` missing under Kaggle `exec()`).
2. v2 fix in `main.py` + resubmit (ref 53950779) → validation COMPLETE @ ~600 μ, then ladder games.
3. μ climbed to **850.5** (~6h after upload per Kaggle UI).

## Local gate (pre-submit, filter only)

`scripts/gate_dragapult.py` — 78–88% vs Heuristic/Search pilots on asymmetric real-field decks.
Directionally useful; ladder is authoritative (Ruling R1). **Does not mean we are done.**

## Comparison snapshot (same day)

| Submission | μ |
|------------|--:|
| **dragapult_ex_sample v2** (best so far) | **850.5** |
| track_d_lucarioex_rl_mcts model4 | 643.9 |
| track_a_lucario_ex_search | 660.5 |
| SearchScorer Lucario (prior best rules) | 668 |

## Actions

- [ ] **Pin 53950779 as a Final Submission** on Kaggle (hold the slot while we improve).
- [ ] **Beat 850.5** — Lucario phase-2 levers + field retrain; Dragapult phase-2 levers; any upload must target **> 850.5 μ**.
- [ ] Lucario `lucarioex_v2` — ladder probe; success = μ **above 850.5**, not merely above 668.

Source: `report/ladder_history.csv`, Kaggle submissions UI 2026-06-22.
