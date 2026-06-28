# Archaludon: agent scoring vs + packaged bench guard

- Games per opponent per variant: **50**
- Suite: `full`
- Hero deck: `Z:\kaggle\pokemon\agent_decks\archaludon_ex_cinderace.csv`
- Both variants include in-agent `_empty_bench_basic_score` (R7b)

| Opponent | WR% (guard off) | WR% (+guard) | Δpp | no_active (off) | no_active (on) |
|----------|----------------:|-------------:|----:|----------------:|---------------:|
| dragapult_ex_sample | 52.0 | 64.0 | +12.0 | 1 | 3 |
| real_mega_abomasnow_ex | 70.0 | 72.0 | +2.0 | 0 | 0 |
| real_iono | 52.0 | 38.0 | -14.0 | 0 | 2 |
| real_dragapult_ex | 78.0 | 82.0 | +4.0 | 3 | 1 |
| real_mega_lucario_ex | 86.0 | 72.0 | -14.0 | 1 | 2 |

## Overall

- Guard off (agent only): **67.6%** (n=250), no_active: **5**
- + packaged guard: **65.6%** (n=250), no_active: **8**
- Δ: **-2.0 pp** vs paired A/B

**Ladder truth:** ref 54083197 @ 1224.2 μ. Probe only with material delta + upload gate.
