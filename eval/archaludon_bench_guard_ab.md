# Archaludon: agent scoring vs + packaged bench guard

- Games per opponent per variant: **30**
- Suite: `full`
- Hero deck: `/workspace/project/PTCG-AI-Battle/agent_decks/archaludon_ex_cinderace.csv`
- Both variants include in-agent `_empty_bench_basic_score` (R7b)

| Opponent | WR% (guard off) | WR% (+guard) | Δpp | no_active (off) | no_active (on) |
|----------|----------------:|-------------:|----:|----------------:|---------------:|
| dragapult_ex_sample | 53.3 | 70.0 | +16.7 | 0 | 1 |
| real_mega_abomasnow_ex | 73.3 | 63.3 | -10.0 | 0 | 0 |
| real_iono | 40.0 | 50.0 | +10.0 | 0 | 0 |
| real_dragapult_ex | 73.3 | 86.7 | +13.3 | 0 | 0 |
| real_mega_lucario_ex | 80.0 | 60.0 | -20.0 | 0 | 1 |

## Overall

- Guard off (agent only): **64.0%** (n=150), no_active: **0**
- + packaged guard: **66.0%** (n=150), no_active: **2**
- Δ: **+2.0 pp** vs paired A/B

## v32 controlled A/B (same-seed, n=300 each)

Re-run as a strict controlled pair (identical seed stream per opponent, 60 games/opp):

| Variant | WR% (n=300) | no_active |
|--------:|------------:|----------:|
| HEAD baseline (v31) | **70.0%** | 4 |
| v32 fixed (guard + bench-empty priorities) | **74.0%** | 4 |

- Δ: **+4.0 pp** for v32 vs v31 baseline on the same seed stream.
- Local no_active ≈ 4 on both because field opponents rarely donk; the v32 value is
  preventing the *ladder* donk pattern (empty bench + benchable Basic refused) seen in
  v30/v31 replays (v31: 18 no_active after prize-vs-no_active reason fix).

**Ladder truth:** ref 54083197 @ 1224.2 μ (leader); v31 ref 55083287 @ 792.5 μ.
v32 is a material-delta donk fix (guard wired into `agent()`, bench-empty search
priorities); upload gate passed (exit 0).
