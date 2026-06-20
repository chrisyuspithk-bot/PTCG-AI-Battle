# Lucario RL re-import — blocked (2026-06-20)

**Status:** `[blocked]` until Kaggle notebook shows **iter ≥ 4** with **≥ 2 promoted iters**.

## When unblocked

```bash
python scripts/import_lucario_rl_outputs.py \
  --source report/kaggle_notebook_jobs/lucario \
  --name track_d_lucario_rl_mcts_v2

python scripts/record_local_battle.py \
  --agent-a lucario_mcts --deck-a agent_decks/real_mega_lucario_ex.csv \
  --agent-b heuristic --games 8 --seed 0

python scripts/smoke_test.py
python scripts/smoke_replay.py
python scripts/gate_vs_public.py --agent dist/candidates/track_d_lucario_rl_mcts_v2.tar.gz --games 12
```

Submit only if L1 clears prior best (**μ > 668** on Search Lucario) **and** user confirms upload.

## Prior failure

Ref **53885445** (324.6 μ): empty bench → `no_active` fast losses. Do not re-submit iter-0 checkpoints.
