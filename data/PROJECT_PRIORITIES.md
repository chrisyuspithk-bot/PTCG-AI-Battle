# Project priorities (always-on)

Canonical checklist for every agent run. Read with [`AGENTS.md`](../AGENTS.md), [`PROGRESS.md`](../PROGRESS.md), [`TASKS.md`](../TASKS.md).

---

## Two parallel workstreams

| Track | What | Where | Submit as |
|-------|------|-------|-----------|
| **Lucario RL+MCTS** | Transformer + MCTS on fixed Lucario list | Kaggle GPU notebook → download `model_best.pth` | `lucario_mcts` via `scripts/import_lucario_rl_outputs.py` |
| **Deck RL → Track B** | GA deck lists + per-deck MaskablePPO → distill | Local GPU (`train_track_b_deck.py`) | `learned` + `distilled_<slug>_v1.npz` |

Do **not** mix brains across decks (LearnedScorer is deck-specific). Do **not** confuse Lucario RL with Track B Learned on Alakazam.

---

## Environment (Windows)

| Use | Python | Why |
|-----|--------|-----|
| **Track B RL, Lucario import** | `Python313` (`torch 2.11+cu128`) | RTX 4070 Ti SUPER |
| **Smoke tests, GA, packaging** | Either | CPU OK |
| **Avoid for RL** | miniconda3 default | `torch+cpu` only |

---

## Simulator = ground truth

Official Pokémon TCG rules **≠** competition simulator. Organizer stance: **simulator behavior is correct behavior.**

Always read [`SIMULATOR_RESOURCE_NOTES.md`](SIMULATOR_RESOURCE_NOTES.md) before changing attack logic, prize sequencing, or RL features.

Key deltas:
- Unresolvable attack effects → attack **not selectable** (mask-driven legality).
- Mega Zygarde Nullifying Zero → no target-order choice; coins L→R.
- Simultaneous KOs → sequential prize take; all-prize simultaneous = **draw**.

Train and gate only on **legal options from `cg`**, never from card-text inference alone.

---

## Ladder scoring & tempo

Read [`COMPETITION_SCORING.md`](COMPETITION_SCORING.md) — **full μ model**.

Summary:
- **μ = Gaussian skill rating**; starts **~600** after validation self-play (not field WR).
- Each episode updates μ on **win / loss / draw only** (Kaggle: margin/speed **not** in formula).
- **Still avoid fast collapses** — each loss drops μ; deck-out / no bench → many losses quickly.
- **Bench ≥1 Basic** whenever possible (`agent/agent.py`, `rule_core.py`, `evalfn.py`).
- Log **turns + loss reason** from replays/logs; local WR ≠ μ.

---

## Kaggle Simulation CLI (episodes & scouting)

Read [`KAGGLE_SIMULATION_CLI.md`](KAGGLE_SIMULATION_CLI.md).

After every upload:
```bash
kaggle competitions submissions pokemon-tcg-ai-battle -v
kaggle competitions episodes <ref> -v
kaggle competitions replay <episode_id> -p report/replays
kaggle competitions logs <episode_id> <agent_index> -p report/agent_logs
python scripts/track_ladder.py --fetch-logs
```

Use replays/logs to fix fast losses before burning daily upload slots.

---

## Data & imitation learning

**Card metadata:** `data/EN_Card_Data.csv`, `data/JP Card Data.csv`, PDF ID lists — schema in [`SIMULATOR_RESOURCE_NOTES.md`](SIMULATOR_RESOURCE_NOTES.md).

**Daily top episodes (BC/RL/IL):** index at  
https://www.kaggle.com/datasets/kaggle/pokemon-tcg-ai-battle-episodes-index  
Mine for meta decks, trajectories, and benchmark updates (`scripts/mine_episode_decks.py`, `report/deck_rl/`).

---

## Submit discipline

1. User **explicit OK** for Kaggle upload.
2. `scripts/smoke_test.py` (17/17) + gate at appropriate level (L1=12g, L2=40g).
3. [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md) — max **5/day**; pick **2 Final Submissions** manually.
4. Package: `dist/candidates/<name>.tar.gz`.

---

## Current agent candidates (2026-06-20)

| Agent | Status |
|-------|--------|
| Lucario RL+MCTS | Kaggle training ~iter 2; ref 53885445 submitted (early) |
| Alakazam Track B | **1M GPU train in progress** (Python313); submit after L2 gate |
| gen19 fast-basic Track B | L1 passed; L2 package pending |
| Kyogre heuristic / TA1 Search | Protected ladder baselines (633 / 626 μ) |
