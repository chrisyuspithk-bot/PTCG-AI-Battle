# Pilot × deck matrix — Session 49

**Date:** 2026-06-26  
**Why:** RULINGS pilot-before-deck; prior "Lucario deck is out" conflated brain and deck.  
**Harness:** `gate_dragapult.py` × native opponents, **30 games/opp**, weighted E[win]

## dragapult_agent × dragapult_ex_sample.csv (ladder config)

| Opponent | WR% | 95% CI |
|----------|----:|--------|
| dragapult_ex_sample | 43.3 | [27.4, 60.8] |
| real_mega_abomasnow_ex | 46.7 | [30.2, 63.9] |
| real_iono | 60.0 | [42.3, 75.4] |
| real_dragapult_ex | 76.7 | [59.1, 88.2] |
| real_mega_lucario_ex | 83.3 | [66.4, 92.7] |

- **Overall:** 62.0% [54.0, 69.4]
- **Weighted E[win]:** 67.0%

## dragapult_agent × real_mega_lucario_ex.csv (deck swap only)

| Opponent | WR% | 95% CI |
|----------|----:|--------|
| dragapult_ex_sample | **0.0** | [0.0, 11.4] |
| real_mega_abomasnow_ex | 13.3 | [5.3, 29.7] |
| real_iono | 13.3 | [5.3, 29.7] |
| real_dragapult_ex | 13.3 | [5.3, 29.7] |
| real_mega_lucario_ex | 10.0 | [3.5, 25.6] |

- **Overall:** **10.0%** [6.2, 15.8]
- **Weighted E[win]:** **8.2%**

## Verdict

**The Dragapult pilot is deck-specific.** Same brain on Lucario list → catastrophic collapse (10% vs 62%).  
We have **not** measured whether a *good* pilot on Lucario deck can beat 880.8 μ.  
We **have** measured that **swapping deck without pilot work is suicide**.

Compare: LucarioScorer × real_mega_lucario_ex = **44.0%** @ n=20 (S46) — far above dragapult_agent on that deck.

**KC implication:** Chase μ with **matched pilot×deck pairs** only. Next candidates: improve LucarioScorer / import Alakazam best5 / SearchScorer — each gated on ladder, not deck folklore.
