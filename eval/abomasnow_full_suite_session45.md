# Abomasnow R2 Lever Iteration — Session 45 Report

**Date:** 2026-06-26  
**Decision:** **NEGATIVE** — defer Abomasnow lever tuning; proceed to Alakazam (next R2 opponent)

---

## Ladder context (Phase 0)

| Ref | Agent | μ | Gate |
|-----|-------|--:|------|
| 53989933 | Dragapult v3 | **880.8** | Pin as Final (beats v2) |
| 53995982 | Lucario v5 MCTS | **580.6** | ≥573.8 → FULL SPEED |

See [`eval/kaggle_status_session45.md`](kaggle_status_session45.md).

---

## Variant test (vs `real_mega_abomasnow_ex` only)

**Config:** 10 games per variant, seat-swapped, Wilson 95% CI  
**Harness:** `scripts/test_abomasnow_lever_variant.py --all-variants --games 10`

| Variant | boss_orders | gust | WR | vs baseline | Result |
|---------|------------:|-----:|---:|------------:|--------|
| **baseline** | 1000 | 800 | **50.0%** | — | Reference |
| v1 | 1200 | 1000 | 50.0% | +0.0pp | No improvement |
| v2 | 1200 | 800 | 30.0% | -20.0pp | Regression |
| v3 | 1000 | 1000 | 30.0% | -20.0pp | Regression |

**Winners (>5pp vs baseline):** 0

Raw output: [`eval/abomasnow_lever_variants_session45.txt`](abomasnow_lever_variants_session45.txt)

---

## Full-suite gate (baseline levers — control run)

No winning variant to apply. Ran baseline as regression check.

**Config:** `scripts/gate_abomasnow_full_suite.py --variant baseline --games 10`

| Opponent | Result | Post-R2 baseline | Delta |
|----------|-------:|-----------------:|------:|
| dragapult_ex_sample | 30.0% | 30.0% | +0.0pp |
| real_mega_abomasnow_ex | 30.0% | 50.0% | -20.0pp |
| real_iono | 50.0% | 50.0% | +0.0pp |
| **OVERALL** | **36.7%** | **43.3%** | **-6.6pp** |

Material regressions (>5pp): 1 (abomasnow in this run — high variance at n=10)

Raw output: [`eval/abomasnow_full_suite_session45_raw.txt`](abomasnow_full_suite_session45_raw.txt)

---

## Analysis

1. **No lever variant beat baseline by >5pp.** v1 tied at 50%; v2/v3 regressed sharply in the abomasnow-only gate.
2. **Abomasnow levers may already be near optimum** at boss_orders=1000, gust=800 (post-dragapult-R2 context).
3. **High variance:** 10-game samples show 30–50% swings on the same baseline; CI bands span ~±25pp. A negative finding is honest but not definitive — would need n=20+ to confirm.
4. **Cross-matchup noise:** Session 44j saw abomasnow improve when only dragapult levers changed (+20pp); abomasnow-specific tweaks did not replicate that.

---

## Decision gate

| Criterion | Met? |
|-----------|------|
| >5pp abomasnow improvement | **No** |
| No material regression on full suite | N/A (no variant applied) |
| Package for upload | **No** |

**Next:** Alakazam R2 lever iteration (`alakazam_psychic` in `matchup_levers.py`) per roadmap. User: pin Dragapult v3 @ 880.8 μ on Kaggle web UI.

---

## Files created

- `scripts/test_abomasnow_lever_variant.py`
- `scripts/gate_abomasnow_full_suite.py`
- `eval/abomasnow_lever_variants_session45.txt`
- `eval/abomasnow_full_suite_session45.md` (this file)
- `eval/kaggle_status_session45.md`
- `eval/kaggle_submissions_session45.csv`

**Not modified:** `agent/matchup_levers.py` (no winning variant)
