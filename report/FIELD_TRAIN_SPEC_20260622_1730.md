# Lucario field RL+MCTS — training specification

**Recorded:** 2026-06-22 **17:30** local (5:30 PM)  
**Status:** Pre-flight for **fresh** run (no checkpoint resume)  
**Code entrypoints:** `scripts/train_lucario_field_mcts.py`, `scripts/run_lucario_field_train_fresh.ps1`

---

## Strategy competition grading context (user notes)

| Section | Weight | Our focus |
|---------|--------|-----------|
| **§1 Model & strategy** | **70%** | Lucario MCTS + `LucarioScorer` rules, matchup levers, deck-scoped soft masking, 9:59 clock discipline |
| **§2 Deck concept & integration** | **20%** | `real_mega_lucario_ex.csv` + tech/levers tuned per archetype |
| Other | 10% | Report / presentation |

Architecture target (not fully built yet): **universal card encoder** → **policy head**, **value head**, **opponent head** (archetype embedding for scoped adapters). Current `MyModel` has encoder + policy decoder only; opponent head is **Phase 3 backlog** (see bottom).

---

## Opponents (default: 9 official decks, 4 kiyotah pilots)

| Kaggle kernel | Pilot module | Deck stems |
|---------------|--------------|------------|
| [Mega Lucario ex](https://www.kaggle.com/code/kiyotah/a-sample-rule-based-agent-mega-lucario-ex-deck) | `LucarioScorer` | `real_mega_lucario_ex`, `top_mined_mega_lucario_ex` |
| [Dragapult ex](https://www.kaggle.com/code/kiyotah/a-sample-rule-based-agent-dragapult-ex-deck) | `dragapult_agent.py` | `dragapult_ex_sample`, `real_dragapult_ex`, `top_mined_dragapult_ex` |
| [Iono](https://www.kaggle.com/code/kiyotah/a-sample-rule-based-agent-iono-s-deck) | `iono_agent.py` | `real_iono`, `top_mined_iono` |
| [Mega Abomasnow ex](https://www.kaggle.com/code/kiyotah/a-sample-rule-based-agent-mega-abomasnow-ex-deck) | `abomasnow_agent.py` | `real_mega_abomasnow_ex`, `top_mined_mega_abomasnow_ex` |

**Excluded by default:** `top_mined_alakazam`, `top_mined_trevenant` (no official sample).  
**Brains:** `--opponent-brain native` / `--eval-opponent native`.

Pre-flight: `python scripts/verify_official_opponents.py`

---

## One cycle (order of operations)

1. Save `model{cycle}.pth`
2. **Eval** — champion MCTS vs each opponent, 20 games each (metrics only)
3. **Mirror collect** — 40 games vs native `LucarioScorer` on train deck
4. **Field collect** — 20 games/opponent (40 vs Lucario mirrors via `lucario_game_mult=2`)
5. **Train** — replay buffer last 2 cycles, AdamW + Huber
6. **Gate** — candidate vs champion mirror MCTS, 20 games; promote if WR ≥ 55%
7. Save `model_latest.pth`; `model_best.pth` on promotion

**Collection games/cycle (defaults, 9 opponents):** mirror 40 + field 220 = **260**.

---

## Rewards (only signal)

| Terminal | Value label |
|----------|-------------|
| Win | `+1.0` |
| Loss | `-1.0` |
| Draw | `0.0` |

Backward bootstrap per ply (`VALUE_LAMBDA=0.9`):

```text
sample.value = (terminal + sample.value) * 0.5
terminal     = terminal * 0.9 + sample.value * 0.1
```

Policy targets: relative child values vs root from MCTS (Huber on decoder, masked 64 slots).

**No** ladder μ, **no** step shaping, **no** asymmetric opponent reward.

---

## 9:59 player clock (hard cliff before 10:00 forfeit)

Kaggle: **10 min/player** cumulative think time; overrun → forfeit (often double-loss).  
Training uses **`PlayerClock` limit = 599 s** (`LUC_PLAYER_CLOCK_LIMIT_SEC`):

- Cumulative wall time per player, charged on each `act` / `mcts_agent` call.
- **Over 599 s → that player forfeits → opponent wins** (our samples get loss label if we timed out).
- Wired in field **collect** and **eval** (`collect_vs_opponent`, `eval_matchup`).
- Disable: `--no-player-clock` or `LUC_PLAYER_CLOCK=0`.

This teaches the model to finish decisions before the simulator’s 10:00 cliff.

---

## Matchup levers + deck-scoped soft masking

**Purpose:** Train **our** Lucario MCTS policy with small, archetype-specific nudges from `LucarioScorer` + `matchup_levers.py` — not to replace the NN.

| Mechanism | Where | What |
|-----------|-------|------|
| `--lever-blend` | `set_lucario_lever_teaching` | Global cap (default 0.35; fresh run 0.40) |
| Root MCTS bias | `_pick_root_child` | +`blend * 1000` visits to child matching `LucarioScorer.choose` |
| **Soft mask** | `agent/deck_scope.py` | Scales effective blend by archetype **confidence** (deck CSV + visible board) |
| Opponent moves | Official pilots | Unchanged — always kiyotah rules |

Confidence &lt; 0.45 → **no lever bonus** (pure MCTS/NN). High confidence → full blend.

Disable soft mask: `--no-deck-scope`.

---

## Hyperparameters (defaults)

| Param | Value |
|-------|-------|
| `SEARCH_COUNT` | 12 |
| `TEMP_PLIES` | 8 (temp 1.0 then greedy) |
| `BATCH_SIZE` | 128 |
| `LR` | 3e-4 |
| `REPLAY_ITERS` | 2 cycles |
| `GATE_WINRATE` | 0.55 |
| `D_MODEL` | 128 |
| `mirror_brain` | `native` (LucarioScorer) |

---

## Fresh run checklist

- [ ] `python scripts/verify_official_opponents.py` → exit 0
- [ ] Detached launch (survives closing Cursor):
  `powershell -File scripts/run_lucario_field_train_fresh.ps1`
- [ ] Or resume after interrupt:
  `powershell -File scripts/run_lucario_field_train_detached.ps1 -Work rl_mcts_field/lucarioex_v3_fresh`

## Checkpointing (2026-06-22 update)

| File | Purpose |
|------|---------|
| `checkpoint.json` | `next_cycle`, `status`, resume flags |
| `model_latest.pth` | Weights after last train step |
| `model_best.pth` | Champion after gate promotion |
| `model{cycle}.pth` | Snapshot at start of each cycle |
| `train.pid` | OS process id |
| `train.log` | Appended stdout (detached mode) |

Interrupt/Ctrl+C/signal → emergency save to `model_latest.pth` + `checkpoint.json`.

---

## Phase 3 backlog: opponent head

`MyModel` today: sparse encoder → value + policy decoder. **Not yet:** opponent archetype embedding fed to policy/value (or separate head) for per-deck adapter routing. Until then, soft masking + levers + real `opp_deck` in MCTS search belief approximate deck-scoped play.

---

## Related files

- `agent/official_registry.py` — pilot routing
- `agent/lucario_mcts_runtime.py` — MCTS, clock, training loop helpers
- `agent/matchup_levers.py` — per-archetype `LeverDeltas`
- `agent/lucario_policy.py` — `LucarioScorer` consumes levers
- `agent/deck_scope.py` — confidence + soft lever mask
- `scripts/verify_official_opponents.py` — pre-flight smoke
