# LucarioScorer rules baseline — Session 46

**Date:** 2026-06-26  
**Harness:** `eval/harness.py` + `field/registry.json` (F2)  
**Hero:** `LucarioScorer` × `real_mega_lucario_ex.csv`  
**Games:** 20 per opponent (seat-swapped)  
**Metadata:** seeds implicit (engine default); opponents = full registry suite

## Per-matchup

| Opponent | Brain | WR% | 95% CI | Record |
|----------|-------|-----|--------|--------|
| dragapult_ex_sample | dragapult_ex | 30.0 | [14.5, 51.9] | W6/L14/D0/U0 |
| real_mega_abomasnow_ex | mega_abomasnow_ex | 25.0 | [11.2, 46.9] | W5/L15/D0/U0 |
| real_iono | iono | 75.0 | [53.1, 88.8] | W15/L5/D0/U0 |
| real_dragapult_ex | dragapult_ex | 40.0 | [21.9, 61.3] | W8/L12/D0/U0 |
| real_mega_lucario_ex | mega_lucario_ex | 50.0 | [29.9, 70.1] | W10/L10/D0/U0 |

## Overall

- **44.0%** [34.7, 53.8] (n=100 decided, 5 decks)

## Notes

- Replaces stale Session 44i 30% @ n=10 with harness n=20 + Wilson CI.
- Dragapult gap persists (~30%); iono strong (~75%); mirror even (~50%).
- Raw console log: `eval/lucario_rules_baseline_session46_run.txt`
