# Lucario RL re-import — blocked (2026-06-20)

**Status:** `[blocked]` for Kaggle upload until **iter ≥ 4 complete** on notebook **and** L1 clears Search Lucario baseline.

**2026-06-20 update:** Downloads iter 0–3 imported to
[`kaggle_download_iter3_20260620/`](../kaggle_notebook_jobs/lucario/kaggle_download_iter3_20260620/).
See [`iter3_import_assessment_20260620.md`](../kaggle_notebook_jobs/lucario/iter3_import_assessment_20260620.md).

- **Champion:** iter **2** (`gate=0.975`, `vs_random=1.0`) → use `model_iter2.pth` / repaired `model_best.pth`
- **Iter 3:** **not promoted** (`gate=0.175`) — do **not** submit
- Promotions: 2 (iter 0, 2) ✓ | Notebook iter 4 was in progress when captured
- **Iter 4–5 (2026-06-20):** staged in
  [`kaggle_download_iter45_20260620/`](../kaggle_notebook_jobs/lucario/kaggle_download_iter45_20260620/)
  — `model_best.pth` = **iter 5** (gate 0.675, promoted)

## When unblocked

```bash
python scripts/import_lucario_rl_outputs.py \
  --source report/kaggle_notebook_jobs/lucario/kaggle_download_iter45_20260620 \
  --name track_d_lucario_rl_mcts_iter5

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
