# Dragapult agent gate — Session 48 baseline

**Date:** 2026-06-26  
**Harness:** `eval/harness.py` + native opponents + `field/weights.json`  
**Hero:** `dragapult_agent` × `dragapult_ex_sample.csv`  
**Games:** 20 per opponent (seat-swapped)

## Per-matchup

| Opponent | Brain | WR% | 95% CI | Record |
|----------|-------|-----|--------|--------|
| dragapult_ex_sample | dragapult_ex | 50.0 | [29.9, 70.1] | W10/L10 |
| real_mega_abomasnow_ex | mega_abomasnow_ex | 45.0 | [25.8, 65.8] | W9/L11 |
| real_iono | iono | 60.0 | [38.7, 78.1] | W12/L8 |
| real_dragapult_ex | dragapult_ex | 75.0 | [53.1, 88.8] | W15/L5 |
| real_mega_lucario_ex | mega_lucario_ex | **80.0** | [58.4, 91.9] | W16/L4 |

## Overall

- **62.0%** [52.2, 70.9] (n=100 decided)
- **Weighted E[win]: 70.5%** (field mixture from `field/weights.json`)

## Lucario R2 lever sweep (Dragapult Phase 2b)

| Variant | vs Lucario | Weighted E[win] | vs baseline |
|---------|----------:|----------------:|------------:|
| baseline | 75.0% | 75.0% | — |
| v1 (+boss hand+play) | 65.0% | 65.0% | **-10pp** |
| v2 (+boss hand) | 65.0% | 65.0% | **-10pp** |
| v3 (+boss play only) | 80.0% | 80.0% | +5pp lucario-only; **full suite tie** (70.4% weighted) |

**Decision:** `dragapult_levers.py` stays at **zero bonuses** — official sample already strong vs Lucario; boss lever tweaks regress or don't move weighted gate.

## Implication for ladder

Local weighted **70.5%** vs Lucario-heavy field supports pushing μ from 880 → 1000+ via **pilot stability + upload probes**, not Dragapult boss levers this session.

Raw log: `eval/dragapult_baseline_session48_run.txt`
