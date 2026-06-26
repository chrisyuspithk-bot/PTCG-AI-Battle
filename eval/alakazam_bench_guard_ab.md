# Alakazam best5: rules vs +R7 bench guard

- Games per opponent per variant: **50**
- Suite: `full`
- Hero deck: `Z:\kaggle\pokemon\agent_decks\ryotasueyoshi_alakazam_best5.csv`
- Baseline to beat (no guard, S50): **62.0%** @ n=30

| Opponent | WR% (no guard) | WR% (+guard) | Δpp | no_active (off) | no_active (on) |
|----------|---------------:|-------------:|----:|----------------:|---------------:|
| dragapult_ex_sample | 52.0 | 44.0 | -8.0 | 0 | 0 |
| real_mega_abomasnow_ex | 64.0 | 64.0 | +0.0 | 0 | 0 |
| real_iono | 30.0 | 20.0 | -10.0 | 0 | 0 |
| real_dragapult_ex | 62.0 | 70.0 | +8.0 | 0 | 1 |
| real_mega_lucario_ex | 76.0 | 70.0 | -6.0 | 1 | 0 |

## Overall

- No guard: **56.8%** (n=250), no_active: **1**
- + guard: **53.6%** (n=250), no_active: **1**
- Δ: **-3.2 pp** vs paired A/B
- vs 62% S50 baseline: below (53.6%)

**Upload:** only if guard beats 62% + `check_upload_eligible` passes with material delta vs 53913404.
