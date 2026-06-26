# Full ladder scoreboard — all COMPLETE submissions (ground truth)

**Source:** Kaggle submissions UI (user paste 2026-06-26) + `report/ladder_history.csv`  
**Sort:** public μ descending. **Bar:** 880.9 μ (Dragapult v3, ref 53989933).

| Rank | μ | Brain | Deck | Tarball / ref | Notes |
|-----:|----:|-------|------|---------------|-------|
| 1 | **880.9** | Official Crispin + bench guard R7 | `dragapult_ex_sample` | dragapult v3 · 53989933 | **Only agent >800 μ** |
| 2 | 833.0 | Official Crispin + wrapper | `dragapult_ex_sample` | dragapult v2 · 53950779 | Superseded |
| 3 | 660.5 | **SearchScorer** (home rules) | `real_mega_lucario_ex` | track_a_lucario_ex_search · 53869254 | **Best home-grown** |
| 4 | 659.0 | **Imported best5 rules** (external) | Alakazam mined | ryotasueyoshi_alakazam_best5 · 53913404 | Best non-Dragapult pilot |
| 5 | 651.3 | RL+MCTS model4 (basic notebook) | `real_mega_lucario_ex` | track_d_lucarioex_rl_mcts_model4 · 53946742 | **Beats v5 field MCTS** |
| 6 | 633.0 | HeuristicScorer | Kyogre | a2_kyogre · 53854707 | Peaked 672.7 early |
| 7 | 626.0 | SearchScorer | Kyogre +2e probe | track_a_probe_1 · 53856711 | |
| 8 | 615.6 | SearchScorer | Trevenant mined | track_a_trevenant · 53916377 | |
| 9 | 600.7 | SearchScorer | gen19 GA deck | track_a_gen19 · 53930652 | GA did not beat hand Kyogre |
| 10 | 585.1 | LearnedScorer (Track B PPO) | RL-deck | track_b_learned · 53868798 | ML < rules |
| 11 | 580.6 | **Field RL+MCTS v5** (25 cycles) | `real_mega_lucario_ex` | lucarioex_v5 · 53995982 | **Below model4 & Search** |
| 12 | 548.6 | SearchScorer | Abomasnow probe | track_a_probe_2 · 53856676 | |
| 13 | 545.6 | SearchScorer | Alakazam leader mined | track_a_alakazam_leader · 53890064 | Our Search << imported best5 |
| 14 | 535.6 | LucarioScorer + smart bench | Lucario sample | track_c_rulecore · 53886522 | |
| 15 | 500.1 | LucarioSearchScorer | Lucario v2 deck | track_a_lucario_search · 53930648 | |
| 16 | 490.4 | LearnedScorer | Alakazam mined | track_b_learned_alakazam · 53856584 | |
| 17 | 468.9 | LearnedScorer | Dragapult spread | track_b_learned_dragapult · 53856590 | Learned on Dragapult deck still fails |
| 18 | 464.7 | Field RL+MCTS v5 cycle13 | `real_mega_lucario_ex` | lucarioex_v5 early · 53978119 | |
| 19 | 460.8 | Field RL+MCTS v2 | `real_mega_lucario_ex` | lucarioex_v2 · 53962060 | |
| 20 | 368.5 | RL+MCTS iter0 (2-cycle GPU) | Lucario | track_d_lucario_rl_mcts · 53885445 | |
| 21 | **185.4** | RL+MCTS model4 (basic) | Alakazam mined | track_d_alakazam · 53946148 | Snorlax-opponent training |

**ERROR (not on ladder):** dragapult v1 (`__file__` bug), a2_kyogre first upload.

---

## Lessons from the full board (not from local gates)

### By brain family — best μ achieved

| Brain family | Best μ | Deck that achieved it |
|--------------|-------:|----------------------|
| Official archetype rules (Crispin Dragapult) | **880.9** | dragapult_ex_sample |
| SearchScorer (our rules+search) | **660.5** | real_mega_lucario_ex |
| Imported external rules | **659.0** | Alakazam best5 |
| Basic RL+MCTS (notebook) | **651.3** | real_mega_lucario_ex |
| HeuristicScorer | **633.0** | Kyogre |
| Field RL+MCTS (25-cycle “champion”) | **580.6** | real_mega_lucario_ex |
| LearnedScorer / Track B | **585.1** | RL-deck |
| RL+MCTS wrong training | **185.4** | Alakazam |

### By deck — best μ achieved (pilot varies!)

| Deck archetype | Best μ | Best brain on that deck |
|----------------|-------:|-------------------------|
| Dragapult ex sample | **880.9** | Official Crispin |
| Mega Lucario ex real | **660.5** | SearchScorer (not field MCTS) |
| Alakazam mined | **659.0** | Imported best5 (not our Search 545.6) |
| Kyogre | **633.0** | HeuristicScorer |
| Trevenant | **615.6** | SearchScorer |
| Abomasnow | **548.6** | SearchScorer |
| GA gen19 | **600.7** | SearchScorer |

### What we should have concluded earlier

1. **Field RL+MCTS v5 (580.6) is a regression** vs basic model4 (651.3) and SearchScorer (660.5) on the **same Lucario deck**.
2. **Only Dragapult official pilot clears 800 μ** — gap to #2 is **~220 μ**, not a few lever points.
3. **SearchScorer on Lucario** is the home-grown iteration path (660.5 μ). LucarioScorer gated **39.3%** @ n=30 — do not upload.
4. **Every LearnedScorer / Track B submission < 600 μ** except one RL-deck at 585.1.
5. **Local gates misordered Kyogre (13% local → 672 μ peak)**, Trevenant (15% L1 → 615.6 μ), and Dragapult v3 (90.6% local → 880.9 μ). Ladder is the only sort key.

### Not tried on ladder (gaps)

- SearchScorer × `dragapult_ex_sample` (only official pilot submitted)
- SearchScorer × Alakazam with imported best5 **code** packaged as ours
- Official Lucario sample pilot × `real_mega_lucario_ex` (only LucarioScorer/smartbench at 535.6)
- Any submission using **mined real_dragapult_ex** deck (only sample list on ladder)
- HeuristicScorer × Lucario / Alakazam (only Kyogre path explored on ladder)
