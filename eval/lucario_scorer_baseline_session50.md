# LucarioScorer — local gate baseline (Session 50)

**Pilot:** `LucarioScorer` × `agent_decks/real_mega_lucario_ex.csv`  
**Suite:** full · **n=30** per opponent  
**Command:** `python scripts/gate_lucario_rules.py --games 30 --suite full --report`

Local WR is **filter only**. Ladder bar on this deck: **SearchScorer @ 660.5 μ** (ref 53869254).

## Result — **do not upload** (39.3% << 55% minimum, far below Search)

| Opponent | Brain | WR% | 95% CI | Record |
|----------|-------|-----|--------|--------|
| dragapult_ex_sample | dragapult_ex | 26.7 | [14.2, 44.4] | W8/L22/D0/U0 |
| real_mega_abomasnow_ex | mega_abomasnow_ex | 23.3 | [11.8, 40.9] | W7/L23/D0/U0 |
| real_iono | iono | 46.7 | [30.2, 63.9] | W14/L16/D0/U0 |
| real_dragapult_ex | dragapult_ex | 33.3 | [19.2, 51.2] | W10/L20/D0/U0 |
| real_mega_lucario_ex | mega_lucario_ex | 66.7 | [48.8, 80.8] | W20/L10/D0/U0 |

**Overall:** **39.3%** [31.9, 47.3] (n=150 decided)

## Interpretation

- LucarioScorer **underperforms SearchScorer** on this deck locally — uploading would waste a slot (R12).
- Weak vs Dragapult/Abomasnow natives (~23–27%) — same cliff as other non-Dragapult pilots.
- **Next:** iterate SearchScorer (660.5 μ bar) or Alakazam levers (62% local bar → 659 μ), not raw LucarioScorer upload.

```powershell
python scripts/check_upload_eligible.py --brain LucarioScorer `
  --deck agent_decks/real_mega_lucario_ex.csv `
  --change "..." --local-gate 39.3
# → BLOCKED (< 55% minimum)
```
