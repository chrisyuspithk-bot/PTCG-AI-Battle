# Kaggle Notebook Training Status

Last updated: 2026-06-19T20:47:43Z

## Current Run

- Notebook: `C:\Users\tobin\Downloads\reinforcement-learning-and-mcts-sample-code.ipynb`
- Kaggle session: Draft Session, GPU T4 x2
- Observed panel at 8 minutes: CPU about 397%, RAM 2.8 GiB, GPU0/GPU1 0.0%
- Output artifacts expected from the sample notebook: `out/model_best.pth`,
  `out/model_final.pth`

## What The GPU Panel Means

This sample notebook is CPU-heavy before it trains.

The training cell does this each round:

1. Saves the current model to `weights_cur.pth` on CPU.
2. Starts a multiprocessing pool with `WORKERS = os.cpu_count()`.
3. Runs `EVAL_GAMES = 40` and `SELFPLAY_GAMES = 200` through MCTS/search workers.
4. Only after the pool returns does it move batches to `device` and run optimizer
   steps on the main model.

So high CPU and 0% GPU is normal while the pool is generating games. The first
proof that the notebook is configured correctly is:

```text
Train device: cuda
```

The next useful progress lines are:

```text
Round 0 eval win rate ...
  collected +...
  trained round 0
```

## Stop Conditions

Stop/restart the run if:

- It prints `Train device: cpu`.
- It errors before `Round 0 eval win rate`.
- It runs much longer than expected without any round output and CPU remains high.

Do not count artifacts until `out/model_best.pth` or `out/model_final.pth` exists
and the notebook printed at least one round metric.

## Track B Restart Cells

If the goal is the repo Track B submission policy instead of the downloaded MCTS
sample notebook, stop the current run and use:

`report/kaggle_notebook_jobs/restart_track_b_cell.md`

## 2026-06-19 Track B Run Started

User reran the one-cell Track B notebook flow in Kaggle.

Confirmed output:

- Repo clone OK: `e64783f Add Kaggle notebook + engine bootstrap for GPU training`
- Dependency install completed; RAPIDS/dask dependency warnings are unrelated to
  this SB3/cabt run.
- CUDA OK: `torch 2.10.0+cu128`, `cuda True`, `device_count 2`, `gpu0 Tesla T4`
- CABT engine OK: copied from `/kaggle/input/competitions/pokemon-tcg-ai-battle`
  and verified `battle_start`.
- Current phase: running
  `scripts/train_track_b_deck.py --deck report/rl_deck_campaign/best_deck.csv --slug rl_deck --timesteps 100000 --n-envs 4 --opponents benchmark --holdout a2_kyogre --gate-games 40 --package --promote`

Run completed and collected outputs to `/kaggle/working/out`.

Confirmed checkpoint:

```json
{
  "status": "ok",
  "timesteps": 100000,
  "device": "cuda",
  "deck_slug": "best-deck",
  "opponents": "benchmark",
  "n_envs": 4,
  "n_opponents": 9,
  "holdout": ["a2_kyogre"]
}
```

Kaggle output files:

- `rl_policy.zip`
- `distilled_rl_deck_v1.npz`
- `distilled_v1.npz`
- `track_b_learned_rl_deck.tar.gz`
- `checkpoint.json`
- `track_b_learned_rl_deck_gate.md`
- `eval_best-deck.json`
- `rl_deck_20260619_210540.json`

Next: download `/kaggle/working/out`, import artifacts locally, read the gate
report, then decide whether to ladder-probe the tarball. No upload without
explicit user approval.

## Deep Run Option

For a several-hour follow-up run, use
`report/kaggle_notebook_jobs/deep_track_b_cell.md`. It resumes the current Kaggle
`rl_policy.zip` when present and defaults to 4M additional timesteps.

## Deep Run Completed

User pasted Kaggle output showing the chunked deep run completed:

- chunks completed: 8/8
- timesteps per chunk: 500,000
- total requested timesteps: 4,000,000
- elapsed: 134.4 minutes
- device: cuda
- final package: `track_b_learned_rl_deck_deep.tar.gz`
- final gate report: `track_b_learned_rl_deck_deep_gate.md`
- final zip: `/kaggle/working/track_b_deep_outputs.zip`
- zip size: 5,450,193 bytes

The checkpoint JSON records the final chunk request (`timesteps=500000`), not the
cumulative total. Use `deep_track_b_progress.json` for the cumulative 8/8 chunk
proof.

Next: download or commit `/kaggle/working/track_b_deep_outputs.zip`, then import
locally and inspect `track_b_learned_rl_deck_deep_gate.md`.

## Deep Artifact Recovery Attempt

User provided a copied Kaggle output page showing the deep run completed and the
zip existed during that session:

- `/kaggle/working/track_b_deep_outputs.zip`
- size `5,450,193`
- 8/8 chunks complete
- elapsed `134.4` minutes

However, a later live-session check returned `exists: False` for that zip, and
the Kaggle API command `kaggle kernels output tobin1dr/reinforcement-learning-and-mcts-sample-code`
still downloads only `reinforcement-learning-and-mcts-sample-code.log`. Therefore
the output artifacts are not currently API-visible or present in the live draft
runtime. The copied output page is proof the run completed, but it is not the
artifact bundle.

## 1M Ramp Run Imported

User downloaded the 1M ramp output bundle and individual files from Kaggle.

- Imported to: `report/kaggle_notebook_jobs/rl_deck_ramp_1m_20260620/`
- Local candidate copy:
  `dist/candidates/track_b_learned_rl_deck_ramp_1m_20260620.tar.gz`
- Local gate copy:
  `report/track_b_gates/track_b_learned_rl_deck_ramp_1m_20260620_gate.md`
- Training: `status=ok`, `timesteps=1000000`, `device=cuda`, `n_envs=4`,
  `opponents=benchmark`, holdout `a2_kyogre`
- Gate: Learned `193/240 = 80.4%`, Search `201/240 = 83.8%`,
  SPRT `accept_b`, dry-run import OK

Decision: this 1M ramp package is valid but weaker than the earlier 100k Kaggle
candidate (`210/240 = 87.5%`). Keep
`dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` as the preferred
upload candidate unless intentionally probing the 1M variant.

## Checkpoint Sweep Implemented

Implemented the next learned-policy training path:

- Authoritative script: `scripts/sweep_track_b_checkpoints.py`
- Kaggle wrapper: `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
- Historical fallback marked: `report/kaggle_notebook_jobs/ramp_track_b_cells.md`

The sweep script trains in 100k chunks, copies every `rl_policy.zip` checkpoint,
distills each checkpoint, gates each distilled model, re-distills the best two
passing checkpoints with more teacher episodes, and packages the best passing
model as `track_b_learned_sweep_best.tar.gz`.

Default next run:

- quick: `CHUNKS=5` (`500k` total, target ~30-40 minutes)
- strong: `CHUNKS=7` (`700k` total, target ~50-60 minutes)
- output zip: `/kaggle/working/track_b_sweep_outputs.zip`

The selection rule prefers passing gates, then higher learned-vs-search margin,
then more learned wins, then fewer timesteps to avoid overtraining.
