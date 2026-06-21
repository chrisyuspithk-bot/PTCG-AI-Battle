# Robust deck-search — handoff (2026-06-20)

Self-contained robust deck-optimisation subsystem. Goal: a 60-card deck with high
win rate vs the **whole field** (maximin/CVaR), not the mean vs a fixed suite.
Does **not** touch `report/rl_deck_campaign/` (the existing GA campaign).

Full rationale: `report/robust_deck_optimization_design.md`.
Usage details: `report/robust_deck_rl/README.md`.

## State: RUN AT SCALE on real field (2026-06-20). Method validated; blocked by Lucario.

**Latest run (30 gens, real field of 60 mined winning decks + benchmark = 79 opponents):**
- Surrogate confirmed **torch-cuda**. **No overfitting** — holdout_robust (~0.48) ≥
  best_robust (~0.42) on nearly every gen.
- BUT best_robust never climbs (peak **0.454** gen2 → **0.418** gen29); **maximin floor
  stuck 0.1–0.3** — worst-case was a **Lucario deck in 15/30 gens**. Lucario = 16/60 mined.
- **Verdict:** architecture works; the wall is **Lucario** (deck space + heuristic pilot
  can't beat the Lucario-heavy field). `best_deck.csv` (gen-2 peak) **not promotable**
  (maximin 0.2). Clean-field baseline backed up → `metrics_cleanfield.csv` / `best_deck_cleanfield.csv`.
- **Mining gotcha:** episode `rewards` are win/loss **±1**, not ELO — use `--min-score 1`.
- **Integration decision:** keep **standalone**; fix Lucario matchup before any `--robust`
  phase in `rl/train_deck_campaign.py`.
- **Pyramid (no upload):** L0 PASS; packaged `dist/candidates/track_e_robust_deck_search.tar.gz`;
  **L1 vs public field = 12.5%** (FAILS <25% bar; iono/crustle 0%, lucario ~15%). L2 not run.
  Offline holdout ~48% vs L1 12.5% → gauntlet uses the *same heuristic pilot both sides*; the
  real field has strong **pilots**. **The pilot is the bottleneck, not the deck.**
- **Next:** put the **Search brain inside the gauntlet** (replace heuristic pilot in
  `rl/gauntlet.py winrate_vs`, default `scorer="heuristic"`) so deck fitness reflects real play,
  AND/OR add anti-Lucario/anti-Iono tech to the deck space; re-run, then re-gate. Success =
  L1 suite mean > 25%.

---

## (original build state) BUILT + UNIT-TESTED (CPU).

| File | Role | Status |
|---|---|---|
| `rl/robust_fitness.py` | maximin / CVaR objective | tested |
| `rl/meta_solver.py` | zero-sum Nash (regret matching) → adversarial opponent weights | tested (RPS→1/3) |
| `rl/gauntlet.py` | opponent field: benchmark + agent_decks + mined + self elites; train/holdout | works (17 clean opps) |
| `rl/winrate_surrogate.py` | P(A beats B); torch-CUDA or NumPy fallback; prunes matchups | tested (NumPy) |
| `rl/robust_search.py` + `scripts/robust_deck_search.py` | PSRO-lite GA loop + CLI | smoke OK |
| `scripts/extract_gauntlet_from_replays.py` | episode replays → `report/deck_rl/mined_decks/` | works |
| `tests/test_robust_core.py`, `tests/test_surrogate.py` | 8 tests | 8/8 pass |

Verified CLI smoke (10 games, clean field) → `best_robust=0.113`, legal 60-card
`report/robust_deck_rl/best_deck.csv`.

## NOT done in sandbox (needs the user's box)
- **Surrogate GPU path** — sandbox has no torch CUDA (4 GB disk, proxy-blocked index).
- **Real-field mining** — no Kaggle egress / disk for the 3–21 GB episode datasets.
  Daily dataset slugs are in `report/deck_rl/episode_dataset_manifest.csv`.

## Exact next actions (in order)
1. **Run the search on the GPU box** (clean field first):
   ```bash
   python scripts/robust_deck_search.py --generations 30 --population 16 --games 10 --surrogate
   ```
   Watch `report/robust_deck_rl/metrics.csv`: `best_robust` should climb;
   **`holdout_robust` is the honest "vs anything" number.** If `best_robust` rises
   while `holdout_robust` stalls → overfitting the field (mine more decks).
2. **Feed the real field**:
   ```bash
   kaggle datasets download kaggle/pokemon-tcg-ai-battle-episodes-2026-06-19 -p report/replays --unzip
   python scripts/extract_gauntlet_from_replays.py --replays report/replays --min-score 900 --max-decks 60
   python scripts/robust_deck_search.py --generations 30 --population 16 --games 10 --surrogate
   ```
   (gauntlet auto-includes `report/deck_rl/mined_decks/`.)
3. **Decide integration**: keep standalone, or wire as a `--robust` phase into
   `rl/train_deck_campaign.py` (objective swap only; reuse gauntlet + meta_solver).
4. **Promote a deck**: when `holdout_maximin` is strong, pair `best_deck.csv` with a
   brain (Search/heuristic) and run the normal pyramid (L0 legality → L2 gate →
   package). Do NOT auto-submit.

## Knobs
`--alpha` (0=worst-case,1=mean), `--cvar-q`, `--games` (~2,500 to resolve a 2% edge),
`--surrogate[-margin]`, `--no-meta-solver`, `--no-mined`. Deterministic via `--seed`.

## Tests
```bash
python -m pytest tests/test_robust_core.py tests/test_surrogate.py -q
```
