# Dragapult: official rules vs +R7 bench guard

- Games per opponent per variant: **50**
- Suite: `full`
- Hero deck: `Z:\kaggle\pokemon\agent_decks\dragapult_ex_sample.csv`

## Why bench guard exists

Official sample scores actions by turn order; it can **END or ATTACK** in MAIN
while `bench_count==0` even though a basic PLAY is legal → active KO → `no_active` loss.
SETUP_BENCH ties at score -1 for P1 also pick wrong index. Guard forces best legal basic.

| Opponent | WR% (rules only) | WR% (+guard) | Δpp | no_active (off) | no_active (on) |
|----------|----------------:|-------------:|----:|----------------:|---------------:|
| dragapult_ex_sample | 54.0 | 44.0 | -10.0 | 0 | 0 |
| real_mega_abomasnow_ex | 36.0 | 34.0 | -2.0 | 0 | 0 |
| real_iono | 72.0 | 50.0 | -22.0 | 0 | 0 |
| real_dragapult_ex | 62.0 | 82.0 | +20.0 | 0 | 0 |
| real_mega_lucario_ex | 60.0 | 66.0 | +6.0 | 0 | 0 |

## Overall

- Rules only: **56.8%** (n=250), no_active losses: **0**
- + bench guard: **55.2%** (n=250), no_active losses: **0**
- Δ overall: **-1.6 pp**

**Interpretation:** Ladder truth is μ (53989933 @ 880.9 used guard). Local WR is a filter;
prefer zero `no_active` and stable long-run probes over n=20 snapshots.
