# Alakazam best5 — local gate baseline (Session 50 / Phase B1)

**Pilot:** `agent/alakazam_agent.py` (ported from ryotasueyoshi notebook)  
**Package:** `python scripts/package_alakazam.py` → `dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz`  
**Ladder benchmark:** 659.0 μ (ref `53913404`) — **already on ladder; do not re-upload (R12)**

Local WR is **filter only**. Next upload requires **measured improvement** → new catalog row.

---

## Gate A — notebook deck (659 μ ship list)

**Hero:** `alakazam_agent` × `agent_decks/ryotasueyoshi_alakazam_best5.csv`  
**Suite:** full · **n=30** per opponent · seeds from harness defaults

| Opponent | Brain | WR% | 95% CI | Record |
|----------|-------|-----|--------|--------|
| dragapult_ex_sample | dragapult_ex | 36.7 | [21.9, 54.5] | W11/L19/D0/U0 |
| real_mega_abomasnow_ex | mega_abomasnow_ex | 76.7 | [59.1, 88.2] | W23/L7/D0/U0 |
| real_iono | iono | 43.3 | [27.4, 60.8] | W13/L17/D0/U0 |
| real_dragapult_ex | dragapult_ex | 73.3 | [55.6, 85.8] | W22/L8/D0/U0 |
| real_mega_lucario_ex | mega_lucario_ex | 80.0 | [62.7, 90.5] | W24/L6/D0/U0 |

**Overall:** **62.0%** [54.0, 69.4] (n=150 decided)

---

## Gate B — top_mined deck (comparison)

**Hero:** `alakazam_agent` × `agent_decks/top_mined_alakazam.csv`  
**Suite:** full · **n=30** per opponent

| Opponent | Brain | WR% | 95% CI | Record |
|----------|-------|-----|--------|--------|
| dragapult_ex_sample | dragapult_ex | 50.0 | [33.2, 66.8] | W15/L15/D0/U0 |
| real_mega_abomasnow_ex | mega_abomasnow_ex | 73.3 | [55.6, 85.8] | W22/L8/D0/U0 |
| real_iono | iono | 46.7 | [30.2, 63.9] | W14/L16/D0/U0 |
| real_dragapult_ex | dragapult_ex | 43.3 | [27.4, 60.8] | W13/L17/D0/U0 |
| real_mega_lucario_ex | mega_lucario_ex | 83.3 | [66.4, 92.7] | W25/L5/D0/U0 |

**Overall:** **59.3%** [51.3, 66.9] (n=150 decided)

---

## Interpretation

- **Ship deck:** notebook list (`ryotasueyoshi_alakazam_best5.csv`) — matches 659 μ submission; +2.7 pp overall vs top_mined on this gate.
- **Weak matchup:** both decks struggle vs `dragapult_ex_sample` native pilot (37–50%).
- **Strong:** Lucario and Abomasnow matchups (73–83%).
- **Next:** Alakazam **levers** after local uplift — not a ladder re-upload (R12; 53913404 @ 659 μ).

**Commands:**
```powershell
python scripts/gate_alakazam.py --games 30 --suite full --report
python scripts/gate_alakazam.py --games 30 --hero-deck agent_decks/top_mined_alakazam.csv --report
```
