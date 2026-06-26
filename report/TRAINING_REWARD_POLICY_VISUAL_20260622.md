# Lucario training — reward & policy visual

**Recorded:** 2026-06-22 (companion to FIELD_TRAIN_SPEC_20260622_1730.md)  
- **Interactive canvas:** `canvases/lucario-training-reward-policy.canvas.tsx` (open in Cursor sidebar)  
**Ground truth:** code paths below — not planned features

---

## High-level: one training cycle

```mermaid
flowchart LR
  A[model cycle.pth] --> B[Eval 9×20g champion]
  B --> C[Collect 40 mirror + 220 field]
  C --> D[Replay buffer 2 cycles]
  D --> E[SGD Huber loss]
  E --> F[Gate mirror MCTS 20g]
  F --> G{WR ≥ 55%?}
  G -->|yes| H[model_best.pth]
  G -->|no| I[keep champion]
```

**Files:** `scripts/train_lucario_field_mcts.py` main loop (~line 631)

---

## The only reward signal

There is **no step reward**. Episode ends → terminal scalar → back-propagated onto MCTS samples from **our turns only**.

### Terminal mapping (`label_samples`, `lucario_mcts_runtime.py`)

| Simulator `result` | Our label |
|--------------------|-----------|
| `your_index` (we win) | **+1.0** |
| opponent index (we lose) | **-1.0** |
| `2` (draw) | **0.0** |
| Clock forfeit (`PlayerClock` > 599s) | Loser gets loss label |

```python
# lucario_mcts_runtime.py — label_samples
if terminal_result == 2:
    value = 0.0
elif terminal_result == your_index:
    value = 1.0
else:
    value = -1.0
for sample in reversed(samples):
    sample.value = (value + sample.value) * 0.5
    value = value * VALUE_LAMBDA + sample.value * (1.0 - VALUE_LAMBDA)  # λ=0.9
```

### What is NOT rewarded

- Per-turn margin, prize count, damage dealt
- Kaggle ladder μ
- Beating a specific archetype (only W/L/draw)
- Opponent mistakes

---

## Sample collection (who moves how)

```mermaid
flowchart TB
  subgraph our_turn [Our turn — training sample created]
    MCTS[mcts_agent 12 sims]
    CLK[PlayerClock charge]
    MCTS --> CLK
    CLK --> SAMP[LearnSample to mine]
  end
  subgraph opp_turn [Opponent turn — no sample]
    PILOT[Official kiyotah pilot act]
    CLK2[PlayerClock charge]
    PILOT --> CLK2
  end
  SAMP --> END[label_samples at game end]
  CLK2 --> END
```

**Collection:** `collect_vs_opponent` in `train_lucario_field_mcts.py`  
- `temp = 1.0` if `ply < TEMP_PLIES` (8), else `0.0`  
- `add_noise=True` passed but **not used** inside `mcts_agent`

---

## MCTS decision policy (our move)

```mermaid
flowchart TD
  A[obs + your_deck + opp_deck] --> B[search_begin hidden belief]
  B --> C[12 PUCT rollouts]
  C --> D{lever_blend > 0?}
  D -->|yes| E[Max visits child]
  E --> F[_pick_root_child + LucarioScorer]
  D -->|no, temp>0, ply<8| G[Temperature sample visits]
  D -->|no| E
  F --> H[Play selected indices]
  G --> H
```

### Policy targets (within one search, before game ends)

```python
# mcts_agent — after search
sample.value = root.total / root.visit
policy[i] = clip(child_value - base, -1, 1)
# unexpanded child: min_value - base - 0.03
```

### MCTS terminal in search tree (`create_node`)

| End state | Backprop value |
|-----------|----------------|
| We win | +1 |
| We lose | -1 |
| Draw | 0 |

---

## Soft masking / deck scope (lever gating)

**Not** NN action masking yet — gates **how hard** LucarioScorer levers push MCTS at root.

```mermaid
flowchart LR
  A[opp CSV name + ids] --> C[archetype_confidence 0..1]
  B[visible opponent board] --> C
  C --> D{conf ≥ 0.45?}
  D -->|no| E[effective_blend = 0 pure MCTS]
  D -->|yes| F[effective_blend = base × scale]
  F --> G[LucarioScorer.choose]
  G --> H[+ effective_blend × 1000 visits to matching child]
```

**Files:** `agent/deck_scope.py`, `_pick_root_child` in `lucario_mcts_runtime.py`  
**Lever deltas:** `agent/matchup_levers.py` → consumed in `lucario_policy.py` `_score_option`

---

## Gradient update (train_on_samples)

```mermaid
flowchart LR
  POOL[Replay: last 2 cycles] --> BATCH[Shuffle batch 128]
  BATCH --> ENC[Encoder → Huber vs sample.value δ=0.2]
  BATCH --> DEC[Decoder → masked Huber vs policy δ=0.1]
  ENC --> SUM[loss_enc + loss_dec]
  DEC --> SUM
  SUM --> ADAM[AdamW + grad clip 1.0]
```

**MyModel today:** encoder (value) + decoder (policy). **No opponent head.**

---

## Promotion gate (not field reward)

```python
gate_wr = eval_vs_model(candidate, champion, deck, GATE_GAMES)  # 20 games
promoted = gate_wr >= GATE_WINRATE  # 0.55
```

Both sides = MCTS on **same Lucario deck** (mirror). Field eval WR does not gate.

---

## Default numbers (from code)

| Constant | Value |
|----------|-------|
| VALUE_LAMBDA | 0.9 |
| SEARCH_COUNT | 12 |
| TEMP_PLIES | 8 |
| PLAYER_CLOCK_LIMIT_SEC | 599 |
| SCOPE_CONFIDENCE_FLOOR | 0.45 |
| GATE_WINRATE | 0.55 |
| REPLAY_ITERS | 2 |
| games/cycle collect | 260 (40+220) |
| lever_blend (fresh run) | 0.40 |

---

## Future (documented, not in code)

- **Opponent head** on universal card encoder → archetype embedding → scoped policy adapter
- Dirichlet noise at MCTS root (`add_noise` stub)
