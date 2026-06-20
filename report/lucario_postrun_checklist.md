# Mega Lucario ex run — post-run checklist

What to do the moment the Kaggle run finishes.

---

## 1. Grab the outputs

Everything is in `/kaggle/working/lucario_rl/`. Cell 4 already prints `run_meta.json`
+ `metrics.csv`. To pull locally:

```bash
kaggle kernels output tobin/ptcg-lucario-rl-mcts -p report/kaggle_notebook_jobs/lucario/
```

**Files you care about:**

- `model_best.pth` — the champion. **This is the one to keep.**
- `metrics.csv` — the training curve.
- `run_meta.json` — config + `best_vs_random`.

---

## 2. Read `metrics.csv` (10-second health check)

Columns: `iter, vs_random, gate_winrate, promoted, n_samples, loss, elapsed_s`.

| Signal | Healthy | Worry |
|---|---|---|
| `vs_random` | climbs past ~0.70, trends up | flat near 0.50 |
| `promoted` | flips to `1` several times early | never `1` after iter ~3 |
| `gate_winrate` | bounces around/above 0.55 | stuck < 0.50 every iter |
| `loss` | drifts down, then plateaus | NaN or rising |

**Rule of thumb:** the sample hit ~0.76 vs random in 5 iters. With 48 sims + the
bigger net you want **clearly higher**, and ideally still rising at the last iter.

---

## 3. Confirm the champion is real (paste as a new Kaggle cell)

Quick 100-game sanity eval of the saved best weights:

```python
import torch
m = MyModel(D_MODEL, NUM_HEADS, D_FF, ENC_LAYERS, DEC_LAYERS).to(
    "cuda" if torch.cuda.is_available() else "cpu")
m.load_state_dict(torch.load("/kaggle/working/lucario_rl/model_best.pth"))
print("best vs random (100g):", eval_vs_random(m, LUCARIO_DECK, 100))
```

Expect **well above 0.50**. If it matches the last `vs_random` in the CSV, the
checkpoint is good.

---

## 4. Decide next step

**If it looks strong (vs_random climbing, ≥ ~0.80):**
- Import, package, and optionally gate locally:
  ```bash
  python scripts/import_lucario_rl_outputs.py --source report/kaggle_notebook_jobs/lucario --name track_d_lucario_rl_mcts --gate-games 4
  ```
- The package uses the dedicated `lucario_mcts` submission wrapper, stores
  `model_best.pth` compactly, dry-runs import/deck selection, and writes a public
  gate log if `--gate-games` is set. **Do not upload unless it clears the public
  gate.**
- Or chain another session for more iters (see resume note below).

**If it stalled (flat ~0.50, never promotes):**
- Bump `LUC_SEARCH_COUNT` 48 → 64 (stronger search signal).
- Lower `LUC_GATE_WINRATE` 0.55 → 0.52 (promote more readily early).
- More data: `LUC_SELFPLAY_GAMES` 120 → 200.
- Re-run.

**If it ran out of time (`iters_done` < `LUC_ITERS`, hit TIME_BUDGET):**
- It still saved cleanly. Either accept `model_best.pth`, or ask me to add
  **resume** (reload `model_latest.pth` + optimizer) so multiple Kaggle sessions
  chain into one long run.

---

## 5. Red flags → quick fixes

- **`loss` is NaN** → drop `LUC_LR` 3e-4 → 1e-4, re-run.
- **Kernel OOM** → drop `LUC_D_MODEL` 256 → 192, or `LUC_BATCH` 128 → 64.
- **Cell 0 asserts "Enable GPU"** → Settings → Accelerator → GPU, restart.
- **`cg-lib` import error** → attach the competition dataset to the notebook.

---

## When you're back

Send me the `metrics.csv` (or just paste the last few rows) and tell me which path
you want from step 4. Fastest high-value move if it's strong: **run the importer,
then gate the packaged `track_d_lucario_rl_mcts` candidate before upload.**
