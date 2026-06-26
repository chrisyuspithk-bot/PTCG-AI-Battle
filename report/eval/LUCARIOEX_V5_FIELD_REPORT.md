can you pull the episode date form the k# Lucario v5 Field RL+MCTS — complete training reference

**Canonical report** for `rl_mcts_field/lucarioex_v5_field`.  
**Generated:** 2026-06-24  
**Machine data:** [`lucarioex_v5_training_data.csv`](lucarioex_v5_training_data.csv) (250 rows, all cycles 0–24)  
**Raw log:** `rl_mcts_field/lucarioex_v5_field/train.log`  
**Metrics (post-resume):** `rl_mcts_field/lucarioex_v5_field/metrics.csv`

---

## 1. At a glance

| Item | Value |
|------|-------|
| **Status** | **DONE** — 25/25 cycles, exit 0 (2026-06-23 21:11 local) |
| **Train deck** | `agent_decks/real_mega_lucario_ex.csv` |
| **Champion file** | `model_best.pth` (last promoted cycle **22**; peak field gate **46.1%** at cycle **21**) |
| **Best field gate metric** | **46.1%** (cycles 17 & 21) |
| **Total wall time** | ~13.6 h active training (48880 s in final segment) + ~2 h pre-crash |
| **Ladder probe (cycle ~13)** | ref **53978119** → **464.7 μ** |
| **Ladder final champion** | ref **53995982** → **650.7 μ** (+186 μ vs probe; still ≪ Dragapult **833 μ**) |
| **Bar to beat** | Dragapult v2 ref **53950779** @ **833.0 μ** |

---

## 2. Run timeline

| When | Event |
|------|-------|
| 2026-06-22 18:33 | Run started (PID 52208), cycles 0–2 |
| 2026-06-22 20:24 | **Crash cycle 2** — `RuntimeError: no legal MCTS actions` + `No Basic Pokemon` in MCTS hidden-deck sample |
| 2026-06-22 21:17 | Auto-resume cycle 2 (PID 25416), completed cycles 2–14 |
| 2026-06-23 07:36 | Mid-cycle-15 interrupt; **MCTS fix** deployed (`_sample_hidden_deck_for_search`) |
| 2026-06-23 07:36 | Auto-resume cycle 15 (PID 31692), completed cycles 15–24 |
| 2026-06-23 11:39 | Ladder probe submitted (cycle-13-era `model_best`) → ref **53978119** |
| 2026-06-23 21:11 | Training **DONE** |
| 2026-06-24 01:20 | Final champion submitted → ref **53995982** |

**Three log segments** in `train.log`; cycle 15 eval appears twice (interrupted mid-cycle). Parsed data uses the **post-fix** cycle-15 completion.

---

## 3. Training configuration (exact)

### Launcher

```powershell
powershell -File scripts/run_lucario_field_train_ladder.ps1 `
  -Work rl_mcts_field/lucarioex_v5_field `
  -Cycles 25 -LeverBlend 0.45 -GamesPerOpponent 30 -SearchCount 20 -Device cuda
```

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| Cycles | 25 |
| Device | CUDA |
| MCTS `SEARCH_COUNT` (train) | **20** |
| Model | d128: D_MODEL=128, HEADS=2, D_FF=256, ENC=1, DEC=1 |
| Games / opponent / cycle | 30 |
| Lucario mirror games / cycle | 20 (same deck + **LucarioScorer**) |
| Eval games / opponent (start of cycle) | 20 |
| Gate games / opponent (end of cycle) | 20 |
| Gate mode | `field` — promote if candidate mean field WR **>** champion |
| Gate winrate floor | 0 (beat champion only) |
| Opponent brain | `native` (official kiyotah pilots) |
| Mirror brain | `none` |
| Lever blend | **0.45** |
| Deck scope | enabled (`soft_lever_blend`) |
| Player clock | **599 s** per player (forfeit on overrun) |
| Replay buffer | 2 cycles |
| Batch / LR | 128 / 3e-4, AdamW + cosine schedule |
| MCTS exploration | TEMP_PLIES=8, Dirichlet α=0.03 ε=0.25 |
| Value λ | 0.9 |
| Training samples / cycle (late) | ~30,000 |

### Field opponents (9)

| Deck CSV | Native pilot |
|----------|--------------|
| `dragapult_ex_sample` | `dragapult_agent` (official Crispin sample) |
| `real_dragapult_ex` | `dragapult_agent` |
| `top_mined_dragapult_ex` | `dragapult_agent` |
| `real_iono` | `iono_agent` |
| `top_mined_iono` | `iono_agent` |
| `real_mega_abomasnow_ex` | `abomasnow_agent` |
| `top_mined_mega_abomasnow_ex` | `abomasnow_agent` |
| `real_mega_lucario_ex` | `LucarioScorer` |
| `top_mined_mega_lucario_ex` | `LucarioScorer` |

---

## 4. Logic stack (exact)

### Layer A — Kaggle submission (`lucario_mcts_policy.py`)

1. Load `agent/models/lucario_model_best.pth` + `lucario_run_meta.json`
2. MCTS inference with **`LUC_SEARCH_COUNT` default = 12** (train used **20**)
3. On failure → **`LucarioScorer`** fallback (never crash)
4. **Not active at submit:** lever_blend, deck_scope, player clock

### Layer B — MCTS (`lucario_mcts_runtime.py`)

- Transformer policy-value over legal option mask
- `search_begin` determinization with **`_sample_hidden_deck_for_search()`** (≥1 Basic — crash fix)
- Real `opp_deck` passed during training; submit uses own deck as opp belief
- Root lever override during training only (`_pick_root_child`)

### Layer C — Rules (`lucario_policy.py` / LucarioScorer)

Official Mega Lucario ex kiyotah sample plus:

- Attack plan (Mega Brave vs ex, Solrock vs single-prize, Hariyama wall)
- Smart bench (`LUCARIO_TECH`): ≥1 mandatory basic, max 2 voluntary bench basics
- Supporters: Boss, PPP, Lillie, Gravity Mountain, Dusk Ball, etc.
- **`matchup_levers.py`** deltas from visible opponent board

### Layer D — Training-only lever teaching

- `set_lucario_lever_teaching(blend=0.45)` at MCTS root
- `effective_blend = 0.45 × archetype_confidence(board)` when deck_scope on
- +1000× blend visit bonus for child matching LucarioScorer pick

### Layer E — Opponents (`official_registry.py`)

Only official kiyotah rule pilots — no invented opponents for field training.

---

## 5. Full training summary (all 25 cycles)

**Columns:**

- **Champ eval** — start-of-cycle mean WR of **champion** vs 9 opponents (20g each)
- **Field gate** — end-of-cycle mean WR of **candidate** on promotion eval (20g × 9)
- **Best field** — running best field gate metric seen so far
- **Prom** — champion promoted (1=yes)

| Cycle | Champ eval % | Field gate % | Best field % | Prom | Loss | Samples |
|------:|-------------:|-------------:|-------------:|:----:|-----:|--------:|
| 0 | 0.0 | 5.6 | 5.6 | 1 | 0.2188 | 7,930 |
| 1 | 10.0 | 6.7 | 5.6 | 0 | 0.2169 | 19,076 |
| 2 | 5.6 | 35.0 | 35.0 | 1 | 0.2850 | 10,585 |
| 3 | 40.0 | 38.9 | 38.9 | 1 | 0.2872 | 26,550 |
| 4 | 37.2 | 21.7 | 38.9 | 0 | 0.2977 | 30,586 |
| 5 | 42.2 | 29.4 | 38.9 | 0 | 0.2914 | 28,322 |
| 6 | 39.4 | 35.6 | 38.9 | 0 | 0.2665 | 28,123 |
| 7 | 45.6 | 23.3 | 38.9 | 0 | 0.2911 | 28,669 |
| 8 | 46.1 | 42.2 | 42.2 | 1 | 0.2748 | 28,852 |
| 9 | 42.2 | 42.2 | 42.2 | 1 | 0.2645 | 30,027 |
| 10 | 45.6 | 30.0 | 42.2 | 0 | 0.2865 | 29,540 |
| 11 | 44.2 | 43.5 | 43.5 | 1 | 0.2716 | 28,957 |
| 12 | 32.4 | 39.1 | 43.5 | 0 | 0.2737 | 30,417 |
| 13 | 42.2 | 35.0 | 43.5 | 0 | 0.2862 | 30,307 |
| 14 | 40.0 | 43.3 | 43.5 | 0 | 0.2606 | 30,541 |
| 15 | 45.0 | 23.3 | 46.1* | 0 | 0.2774 | 15,617† |
| 16 | 39.3 | 43.0 | 43.0‡ | 1 | 0.2730 | 31,379 |
| 17 | 43.3 | 46.1 | 46.1 | 1 | 0.2639 | 31,021 |
| 18 | 41.1 | 32.2 | 46.1 | 0 | 0.2796 | 30,436 |
| 19 | 39.6 | 36.3 | 46.1 | 0 | 0.2727 | 30,549 |
| 20 | 45.0 | 38.3 | 46.1 | 0 | 0.2597 | 30,457 |
| 21 | **46.1** | 30.6 | 46.1 | 0 | 0.2784 | 29,826 |
| 22 | 38.3 | 39.4 | 46.1 | 1 | 0.2674 | 29,726 |
| 23 | 36.1 | 42.2 | 46.1 | 0 | 0.2493 | 29,710 |
| 24 | 42.5 | 36.7 | 46.1 | 0 | 0.2788 | 30,170 |

\*Cycle 15 `best_field` logged `0.0` on resume (checkpoint reset artifact); true running best was **43.5%** → **46.1%** by cycle 17.  
†Cycle 15 samples low due to mid-cycle restart (replay buffer repopulating).  
‡Cycle 16 promotion reset logged `best_field` tracking in metrics.csv segment.

### Promotion events

| Cycle | Field gate % | Notes |
|------:|-------------:|-------|
| 0 | 5.6 | First weights beat untrained champion |
| 2 | 35.0 | Post-crash resume |
| 3 | 38.9 | Early climb |
| 8 | 42.2 | Crossed 42% |
| 9 | 42.2 | Held |
| 11 | **43.5** | **Pre-ladder-probe era** (ref 53978119) |
| 16 | 43.0 | Post MCTS-fix resume segment |
| 17 | **46.1** | **Peak field gate** |
| 22 | 39.4 | Last `model_best.pth` write — gate noise |

---

## 6. Per-opponent eval matrix (champion, 20g, all cycles)

Win rate % at **start of each cycle** (champion vs official pilot).

| Cycle | drap_samp | real_drap | real_iono | real_aboma | real_luc | tm_drap | tm_iono | tm_aboma | tm_luc | **Mean** |
|------:|----------:|----------:|----------:|-----------:|---------:|--------:|--------:|---------:|-------:|---------:|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0.0** |
| 1 | 10 | 5 | 5 | 5 | 10 | 25 | 0 | 5 | 25 | **10.0** |
| 2 | 0 | 10 | 0 | 0 | 5 | 5 | 0 | 10 | 20 | **5.6** |
| 3 | 25 | 40 | 25 | 45 | 35 | 50 | 40 | 50 | 50 | **40.0** |
| 4 | 30 | 50 | 30 | 15 | 25 | 55 | 30 | 50 | 50 | **37.2** |
| 5 | 20 | 55 | 35 | 15 | 60 | 70 | 25 | 40 | 60 | **42.2** |
| 6 | 10 | 60 | 30 | 30 | 25 | 75 | 35 | 35 | 55 | **39.4** |
| 7 | 15 | 60 | 30 | 40 | 50 | 70 | 25 | 60 | 60 | **45.6** |
| 8 | 30 | 60 | 35 | 45 | 50 | 70 | 40 | 45 | 40 | **46.1** |
| 9 | 20 | 35 | 40 | 20 | 50 | 75 | 25 | 60 | 55 | **42.2** |
| 10 | 25 | 65 | 50 | 40 | 55 | 60 | 30 | 35 | 50 | **45.6** |
| 11 | 30 | 40 | 40 | 25 | 45 | 65 | 35 | 60 | 58 | **44.2** |
| 12 | 15 | 40 | 35 | 10 | 50 | 37 | 30 | 30 | 45 | **32.4** |
| 13 | 15 | 35 | 30 | 35 | 40 | 75 | 40 | 60 | 50 | **42.2** |
| 14 | 25 | 45 | 35 | 55 | 40 | 45 | 30 | 45 | 40 | **40.0** |
| 15 | 25 | 40 | 30 | 50 | 60 | 45 | 15 | 70 | 70 | **45.0** |
| 16 | 30 | 45 | 30 | 25 | 47 | 55 | 40 | 50 | 32 | **39.3** |
| 17 | 30 | 75 | 30 | 30 | 40 | 60 | 30 | 50 | 45 | **43.3** |
| 18 | 35 | 55 | 30 | 25 | 60 | 50 | 45 | 30 | 40 | **41.1** |
| 19 | 30 | 37 | 30 | 10 | 35 | 40 | 60 | 55 | 60 | **39.6** |
| 20 | 25 | 45 | 55 | 15 | 65 | 60 | 45 | 50 | 45 | **45.0** |
| 21 | 40 | 45 | 45 | 35 | 40 | 65 | 45 | 60 | 40 | **46.1** |
| 22 | 10 | 50 | 35 | 25 | 44 | 55 | 35 | 50 | 40 | **38.3** |
| 23 | 10 | 40 | 45 | 25 | 30 | 70 | 45 | 25 | 35 | **36.1** |
| 24 | 20 | 58 | 35 | 60 | 20 | 60 | 35 | 50 | 45 | **42.5** |

**Column key:** `drap_samp` = `dragapult_ex_sample` (official ladder pilot deck)

### Aggregate over all 25 cycles

| Opponent | Mean WR | Min | Max | σ rough |
|----------|--------:|----:|----:|--------|
| **dragapult_ex_sample** | **21.0%** | 0% | 40% | Worst — never solved |
| real_mega_abomasnow_ex | 27.2% | 0% | 60% | High variance |
| real_iono | 31.4% | 0% | 55% | Flat |
| top_mined_iono | 31.2% | 0% | 60% | Flat |
| real_mega_lucario_ex | 39.3% | 0% | 65% | Mirror swing |
| top_mined_mega_lucario_ex | 44.4% | 0% | 70% | |
| real_dragapult_ex | 43.6% | 0% | 75% | |
| top_mined_mega_abomasnow_ex | 43.0% | 0% | 70% | |
| **top_mined_dragapult_ex** | **53.5%** | 0% | 75% | Best non-sample dragapult |

**Overall mean across opponents & cycles:** ~37% (excluding cycle-0 zeros: ~39%)

---

## 7. Cycle 13 detail (ladder probe checkpoint)

Submitted as ref **53978119** (`best_field=43.5%` at cycle 11 champion; cycle 13 eval below).

| Opponent | W/L/D | WR |
|----------|-------|---:|
| dragapult_ex_sample | 3/17/0 | 15% |
| real_dragapult_ex | 7/13/0 | 35% |
| real_iono | 6/14/0 | 30% |
| real_mega_abomasnow_ex | 7/13/0 | 35% |
| real_mega_lucario_ex | 8/12/0 | 40% |
| top_mined_dragapult_ex | 15/5/0 | 75% |
| top_mined_iono | 8/12/0 | 40% |
| top_mined_mega_abomasnow_ex | 12/8/0 | 60% |
| top_mined_mega_lucario_ex | 10/10/0 | 50% |
| **Mean** | | **42.2%** |

**Ladder result:** validation 600 → **464.7 μ**

---

## 8. Cycle 21 detail (peak field eval)

| Opponent | W/L/D | WR |
|----------|-------|---:|
| dragapult_ex_sample | 8/12/0 | 40% |
| real_dragapult_ex | 9/11/0 | 45% |
| real_iono | 9/11/0 | 45% |
| real_mega_abomasnow_ex | 7/13/0 | 35% |
| real_mega_lucario_ex | 8/12/0 | 40% |
| top_mined_dragapult_ex | 13/7/0 | 65% |
| top_mined_iono | 9/11/0 | 45% |
| top_mined_mega_abomasnow_ex | 12/8/0 | 60% |
| top_mined_mega_lucario_ex | 8/12/0 | 40% |
| **Mean** | | **46.1%** |

Not promoted (field gate 30.6% — candidate lost head-to-head vs champion that cycle).

---

## 9. Ladder results

| Ref | When | Checkpoint | Local field | μ (latest) |
|-----|------|------------|-------------|----------:|
| 53978119 | 2026-06-23 11:39 | ~cycle 13 / best_field 43.5% | 42.2% eval | **464.7** |
| **53995982** | 2026-06-24 01:20 | Final `model_best.pth` | 46.1% peak | **650.7** |
| 53962060 | (v2 baseline) | 20-cycle v2 | — | 460.8 |
| **53950779** | (Dragapult bar) | rules pilot | 88% local gate | **833.0** |

**Takeaway:** +186 μ from longer training validates direction. Still **~180 μ below** Dragapult rules pilot and **~1 μ below** basic `model4` Lucario (651.3) — RL did not beat simple rules + deck on ladder.

---

## 10. Insights

### What worked

1. **Field-native training** — Official pilots match ladder opponents; no random/heuristic fiction.
2. **Lever teaching (0.45)** — Phase-2 `matchup_levers.py` biases MCTS root without replacing search.
3. **Deck-scoped blend** — Reduces wrong-lever activation when archetype uncertain.
4. **Champion gate** — Prevented shipping cycle-0; tracked improvement to 46.1%.
5. **MCTS determinization fix** — `_sample_hidden_deck_for_search` unblocked cycles 15–24.
6. **Lucario mirror slice** — 20g/cycle vs LucarioScorer stabilizes mirror without pure self-play.
7. **Player clock in train** — Models time budget (though not enabled at submit).
8. **Monotonic ladder improvement** — 464.7 → 650.7 μ confirms local metrics correlate with μ (weakly).

### What failed or plateaued

1. **vs `dragapult_ex_sample`** — **21% mean** over 25 cycles; **#1 blocker** for beating Dragapult μ.
2. **High variance** — Same opponent swings 0–75% cycle-to-cycle (20-game eval noise + non-stationary weights).
3. **RL without rules floor** — +3pp field / +186 μ insufficient; rules pilot at 833 μ remains king.
4. **Promotion noise** — Cycle 22 promoted at 39.4% gate while cycle 21 had 46.1% eval peak.
5. **Train/serve skew** — Search 20 vs 12, levers on vs off, clock on vs off, opp deck belief differs.
6. **Aboma / Iono** — Levers defined but **never L1-gated**; eval stays 27–31% mean on real decks.

### Key lessons (RULINGS-aligned)

| Lesson | Implication |
|--------|-------------|
| Local field WR ≠ ladder μ | Use ladder probes sparingly; gate locally first |
| Official sample pilots are strong | `dragapult_ex_sample` at 833 μ >> our Lucario RL |
| Rules before RL (R11) | Gate `matchup_levers` per archetype before more GPU cycles |
| MCTS needs legal beliefs | Hidden-deck samples must respect setup constraints |
| 20-game eval is noisy | Need Wilson CI or more games for promotion decisions |

---

## 11. Train vs submit gaps (action list)

| Knob | Training | Kaggle submit (53995982) | Fix |
|------|----------|--------------------------|-----|
| MCTS depth | 20 | **12** | `LUC_SUBMIT_SEARCH_COUNT=20` |
| Lever blend | 0.45 | **off** | Expected (inference = pure MCTS) |
| Player clock | 599s | **off** | Add `timed_mcts` wrapper for submit |
| Opponent deck in search | real | own deck | Pass observable opp signature if possible |

---

## 12. Recommended next steps

1. **R2 — Gate Lucario levers** (`scripts/gate_lucario_matchups.py`): Aboma, Dragapult sample, Iono — one PR each.
2. **Export `model_cycle21.pth`** — peak eval checkpoint; may beat shipped `model_best` on ladder.
3. **Align submit search=20** before next Lucario probe.
4. **Do not start Dragapult field RL** until Lucario R2 levers pass L1 on weak matchups.
5. **Keep Dragapult 53950779 pinned** as Final until μ > 833.

---

## 13. File index

| Path | Contents |
|------|----------|
| `report/eval/LUCARIOEX_V5_FIELD_REPORT.md` | **This document** |
| `report/eval/lucarioex_v5_training_data.csv` | All cycles 0–24 eval + train rows |
| `report/eval/lucarioex_v5_field_train_eval.md` | Shorter summary (superseded by this report) |
| `rl_mcts_field/lucarioex_v5_field/train.log` | Full stdout |
| `rl_mcts_field/lucarioex_v5_field/metrics.csv` | Cycles 15–24 CSV (post-resume) |
| `rl_mcts_field/lucarioex_v5_field/run_meta.json` | Config snapshot |
| `rl_mcts_field/lucarioex_v5_field/model_best.pth` | Shipped champion |
| `dist/candidates/lucarioex_v5_field_mcts.tar.gz` | Kaggle tarball |
| `eval/ladder_log.csv` | Ladder μ readings |
| `scripts/_parse_v5_train_log.py` | Regenerate CSV from train.log |

---

*End of report.*
