# PROGRESS LOG

Append-only. Newest entry on top. Each nightly run adds one dated block:
what task(s) were worked, what changed, current best win-rate, and the **exact next
step** so the following run can resume instantly.

---

### 2026-06-20 (handoff reconciliation - expanded leader suite + v2 gate/audit)
- **Worked on:** Reconciled stale Lucario v2 handoff against current repo state; filled missing artifacts for mined leader decks, expanded-suite gate, and search audit.
- **Changed:** [`scripts/arena.py`](scripts/arena.py), [`scripts/gate_track_a.py`](scripts/gate_track_a.py),
  [`scripts/record_local_battle.py`](scripts/record_local_battle.py), [`agent/search_policy.py`](agent/search_policy.py),
  [`agent_decks/benchmark/suite.json`](agent_decks/benchmark/suite.json),
  [`report/mined_decks_20260620.md`](report/mined_decks_20260620.md),
  [`report/LUCARIO_V2_GATE.md`](report/LUCARIO_V2_GATE.md),
  [`report/search_audit_20260620.md`](report/search_audit_20260620.md),
  [`report/public_gate/lucario_v2_vs_leader_suite_20260620.txt`](report/public_gate/lucario_v2_vs_leader_suite_20260620.txt).
- **Leader decks mined:** 3 Alakazam variants + 2 Trevenant variants written under `agent_decks/benchmark/`; all pass `validate_deck.py --deck`.
- **Lucario v2 expanded L1 @ 30g:** `lucario_search` **313/450 = 69.6%**, heuristic **281/450 = 62.4%**, SPRT `accept_b`; weakest matchups are Trevenant control **46.7%** and Trevenant Dunsparce **40.0%**.
- **Search audit:** local `lucario_search` vs `search` 5-game audit produced 55/55 eligible opportunities with `search_begin_input`, 55 search results, and 26 Lucario top-2 guard accepts.
- **Verification:** setup script hit Windows `--break-system-packages` incompatibility; fallback `python -m pip install -r requirements.txt` succeeded. `smoke_test.py` **17/17**, `smoke_replay.py` **16/16**, `pytest tests/test_episode_stats.py -q` **5 passed**, touched scripts `py_compile` OK, arena pool smoke OK.
- **No Kaggle upload:** daily quota remains **5/5 used** per current session state; no external irreversible action was attempted.
- **NEXT:** Analyze live Alakazam probe `python scripts/analyze_submission.py --ref 53890064`; import Lucario RL iter4/5 only when downloads are ready; use Trevenant losses as the next `lucario_search` tactical fix.

---

### 2026-06-20 (Alakazam upload #5 + Lucario RL iter 4/5 — user stepping away)
- **Submitted:** **53890064** `track_a_alakazam_leader_search` — COMPLETE **600.0** (validation); ladder μ TBD.
- **Daily quota:** **5/5** used (69254, 68798, 85445, 86522, 90064). Trevenant probe **not** uploaded (400 + quota).
- **Lucario RL (Kaggle):** notebook at **iter 6** self-play; **iter 4** (gate 0.55, promoted) + **iter 5** (gate 0.675, promoted) checkpoints in Downloads — import when idle; **no RL ladder upload** until L1 beats 53869254.
- **NEXT:** `analyze_submission.py --ref 53890064`; import `model_iter4.pth`/`model_iter5.pth`; pin Finals (keep **53869254** until 90064 beats 660.5).

---
- **Worked on:** `analyze_submission.py` per-episode seat; batch leader replays; mine Alakazam/Trevenant; full L1 gate v2.
- **Changed:** [`scripts/episode_stats.py`](scripts/episode_stats.py), [`scripts/analyze_submission.py`](scripts/analyze_submission.py),
  [`scripts/mine_episode_decks.py`](scripts/mine_episode_decks.py), [`tests/test_episode_stats.py`](tests/test_episode_stats.py),
  [`agent_decks/benchmark/suite.json`](agent_decks/benchmark/suite.json),
  [`agent_decks/top_mined_alakazam.csv`](agent_decks/top_mined_alakazam.csv),
  [`agent_decks/top_mined_trevenant.csv`](agent_decks/top_mined_trevenant.csv),
  [`.cursor/SESSION.md`](.cursor/SESSION.md).
- **53869254 (fixed stats):** **54.55%** WR (was 48.48% with global agent_index), avg **13.36** turns, **66.7%** fast_loss, top loss **prize**.
- **Leader replays:** `--fetch-only` top-5 refs → **84 new** + 41 local; mined leader decks validated OK.
- **L1 v2 @ 30g:** suite mean **8.3%** (30/360) — mirror Lucario **10%**, Abomasnow **20%**; **do not submit**.
- **NEXT:** Port Alakazam ~20-turn wall tempo into `LucarioScorer`; audit `search_begin_input` on 53869254 logs; optional public opponents from mined leader decks.

---
- **Worked on:** Kaggle CLI leaderboard + replay mining; Lucario hybrid tuning (search-guard, deck-out throttle).
- **Changed:** [`report/top_performer_reverse_engineering_20260620.md`](report/top_performer_reverse_engineering_20260620.md);
  [`agent/search_policy.py`](agent/search_policy.py), [`agent/lucario_policy.py`](agent/lucario_policy.py);
  [`.cursor/SESSION.md`](.cursor/SESSION.md).
- **Top refs (μ):** 53802029 (1312.7), 53880887 (1304.2), 53876944 (1284.6), 53878567 (1261.3), 53800247 (1252.0).
- **Insight:** Leaders use Alakazam/Trevenant (~20+ turn wins); our 53869254 at 660.5 μ, ~13 turns, 59% fast_loss.
- **NEXT:** Batch leader replays; fix `analyze_submission.py` per-episode agent_index; mined decks → L1 suite; full L1 gate search-guard v2.

---
### 2026-06-20T16:51Z (Robust deck-search ready to run — handoff + continuation prompt)
- **State:** Robust deck-optimisation subsystem is BUILT + UNIT-TESTED on CPU (8/8 pass)
  and untouched by later runs. Goal: maximise win rate vs the WHOLE field (maximin/CVaR),
  not mean-vs-fixed-suite. Standalone; does not touch `report/rl_deck_campaign/`.
- **Files:** `rl/robust_fitness.py`, `rl/meta_solver.py`, `rl/gauntlet.py`,
  `rl/winrate_surrogate.py`, `rl/robust_search.py`, `scripts/robust_deck_search.py`,
  `scripts/extract_gauntlet_from_replays.py`; tests `tests/test_robust_core.py` +
  `tests/test_surrogate.py`. Docs: `report/robust_deck_optimization_design.md`,
  `report/robust_deck_rl/README.md`. Handoff: `ROBUST_DECK_HANDOFF.md`. Continuation
  prompt: `report/CONTINUE_ROBUST_PROMPT.md`. (Detailed build log: run 39 entry below.)
- **Verified:** CLI smoke (10 games, clean 17-opp field) → best_robust=0.113, legal
  60-card `report/robust_deck_rl/best_deck.csv`. RPS Nash→uniform(1/3); surrogate learns
  (corr>0.6). NOT run at scale; surrogate GPU path + real-episode mining need user's box.
- **Episode data:** `report/deck_rl/episode_dataset_manifest.csv` indexes daily ladder
  episode datasets (the real field). Extractor wired to mine them into the gauntlet.
- **Blockers:** none for the subsystem. Real-field gauntlet + GPU surrogate require the
  user's GPU box + Kaggle download (sandbox is CPU-only, no egress).
- **NEXT (single exact action):** on the GPU box run
  `python scripts/robust_deck_search.py --generations 30 --population 16 --games 10 --surrogate`,
  then read `report/robust_deck_rl/metrics.csv` (best_robust climbing? holdout_robust
  keeping up?). Full plan: `report/CONTINUE_ROBUST_PROMPT.md`.

---

### 2026-06-20 (Lucario best-approach refresh — hybrid impl, deck-out, partial L1)
- **Worked on:** Implement `LucarioSearchScorer`; refresh Lucario strategy doc with today's insights.
- **Changed:**
  - [`agent/search_policy.py`](agent/search_policy.py) — `_CgSearchMixin`, **`LucarioSearchScorer`**
    (search on setup/switch/to-active + `LucarioScorer` fallback).
  - [`scripts/package_submission.py`](scripts/package_submission.py) — `--scorer lucario_search`.
  - [`scripts/smoke_replay.py`](scripts/smoke_replay.py) — hybrid instantiate test (**13/13** golden).
  - [`report/lucario_smartbench_report_20260620.md`](report/lucario_smartbench_report_20260620.md) —
    authoritative best-approach doc: portfolio, loss modes, deck-out, hybrid partial L1.
  - [`.cursor/SESSION.md`](.cursor/SESSION.md) — updated focus + continue prompt.
- **Packaged:** `dist/candidates/track_a_lucario_ex_search_v2.tar.gz` (dry-run OK).
- **L1 (partial, interrupted):** v2 vs 7/12 opponents — mirror **23.3%** (SmartBench was **43.3%**);
  cross-archetype ~10%. **Do not submit hybrid.**
- **Insight:** Simulator `deck_out` when `deckCount` ≤ 0; Lucario thins aggressively — Dusk/Pad
  blocked at deck ≤10 but Carmine/Lillie/Lunatone still thin; next lever for wall/long games.
- **Finals:** unchanged — **53869254** Search Lucario **668 μ**.
- **NEXT:** Complete `gate_vs_public.py --games 30` for v2 vs v1; deck-out throttling in
  `LucarioScorer`; try search without `SETUP_BENCH_POKEMON` if mirror stays low.

---
### 2026-06-20 (EOD wrap-up — Alakazam 1M failed, repo cleanup)
- **Worked on:** Record Alakazam 1M GPU verdict; end-of-day handoff + gitignore cleanup.
- **Alakazam 1M:** Train **complete** (1M steps, CUDA); distill/gate **not run**. Verdict: **not
  submission-worthy** — final train WR **30.8%**, Kyogre holdout **0%** @ 1M (peak holdout **21.1%**
  @ 120k). Prior 100k gate **32/110** failed. Handoff:
  [`report/handoffs/alakazam_track_b_1m_status.md`](report/handoffs/alakazam_track_b_1m_status.md).
- **Lucario RL:** iter 3 imported; iter **2** champion only; blocked for ladder until iter 4+ + L1.
- **Finals:** unchanged — **53869254** Search Lucario **668 μ** (both slots).
- **Cleanup:** [`.gitignore`](.gitignore) — ignore `.claude/`, `agent/models/*.npz`, `rl_policy.zip`,
  `report/public_gate/`, GA `population/`, model backups. Updated [`.cursor/SESSION.md`](.cursor/SESSION.md).
- **NEXT:** `LucarioSearchScorer` hybrid → L1 @ 30g vs 53869254; no Alakazam Learned; no Kaggle upload without user OK.

---
- **Worked on:** Import Kaggle Lucario RL checkpoints from Downloads; assess iter 3 vs champion.
- **Moved:** `Downloads/model_iter{0-3}.pth` → [`report/kaggle_notebook_jobs/lucario/kaggle_download_iter3_20260620/`](report/kaggle_notebook_jobs/lucario/kaggle_download_iter3_20260620/).
  Repaired stale `model_best.pth` with **iter 2 champion**; recorded metrics in
  [`iter3_import_assessment_20260620.md`](report/kaggle_notebook_jobs/lucario/iter3_import_assessment_20260620.md).
- **Verdict:** **Iter 3 is NOT an improvement** — `gate=0.175`, `promoted=0`. Champion = **iter 2**
  (`vs_random=1.0`, `gate=0.975`). Notebook was starting iter 4 when captured.
- **Packaged:** `dist/candidates/track_d_lucario_rl_mcts_iter2.tar.gz` (dry-run OK); **no Kaggle upload**.
- **NEXT:** Let notebook finish iter 4+; re-download full `metrics.csv`; L1 gate iter2 champion vs
  Search Lucario baseline before any upload.

---
- **Worked on:** Lucario early-game line setup — search trainers, energy feed, evolve priority.
- **Changed:** [`agent/lucario_policy.py`](agent/lucario_policy.py) — Dusk Ball/Poke Pad/Gong/PPP timing;
  boosted `_energy_score` + ATTACH bonuses for Riolu/Mega; Riolu evolve +2500 when ≥2 energy;
  `_to_hand_score` favors Riolu/ex/energy when line missing. [`scripts/smoke_replay.py`](scripts/smoke_replay.py) — 11 golden checks.
- **Verification:** smoke_replay **11/11**, smoke_test **17/17**; lucario vs heuristic **62.5%** (15/24), avg turns **12.8**.
- **NEXT:** Repackage `track_c_lucario_rulecore_smartbench`, L1 gate, optional Simulation upload with user OK.

---
- **Worked on:** Full **Repo Cleanup & Continuous Improvement** plan (Phases 0–5).
- **Changed:**
  - Phase 0: [`report/submission_log.csv`](report/submission_log.csv), [`scripts/record_local_battle.py`](scripts/record_local_battle.py),
    [`scripts/analyze_submission.py`](scripts/analyze_submission.py), [`scripts/episode_stats.py`](scripts/episode_stats.py),
    [`scripts/smoke_replay.py`](scripts/smoke_replay.py), [`data/KAGGLE_SIMULATION_CLI.md`](data/KAGGLE_SIMULATION_CLI.md) §8–9.
  - Phase 1: [`.gitignore`](.gitignore), handoffs → [`report/handoffs/`](report/handoffs/),
    [`notebooks/README.md`](notebooks/README.md), [`scripts/promote_candidate.py`](scripts/promote_candidate.py).
  - Phase 2: Alakazam package `track_c_alakazam_rulecore` L1 **5.6%** (below 25% — no submit);
    gen19 L2 **PASS** → `dist/candidates/track_b_gen19_fast_basic.tar.gz`;
    Lucario RL re-import **blocked** → [`report/handoffs/lucario_rl_reimport_status.md`](report/handoffs/lucario_rl_reimport_status.md).
  - Phase 3–5: [`data/EVAL_PROTOCOL.md`](data/EVAL_PROTOCOL.md), [`scripts/package_submission.py`](scripts/package_submission.py) `--gate`,
    [`scripts/nightly.py`](scripts/nightly.py) smoke_replay + L1 + analyze steps;
    [`report/FINALS_PIN.md`](report/FINALS_PIN.md) with L4 stats.
  - Bench guard: [`agent/bench_guard.py`](agent/bench_guard.py) routes mandatory PLAY when empty bench; Lucario penalizes non-KO attacks via `remain_hp` plan.
- **Metrics:**
  - L0: smoke_test **17/17**, smoke_replay **3/3**.
  - L4: ref 53869254 — 48.5% WR, avg turns 13.4, fast_loss 58.8% (33 eps);
    ref 53886522 — 50% WR, avg turns 10.5, fast_loss 100% (2 eps only).
  - Alakazam RuleCore L1: **5.6%** (8/144). gen19 L2: **PASS** (155/240 vs Search 188/240, SPRT accept_b).
- **Blockers:** SmartBench ref has too few episodes for Finals decision; loss_reason parser returns `unknown` (replay log format TBD).
- **NEXT:** User pin Finals per [`report/FINALS_PIN.md`](report/FINALS_PIN.md) (53869254 ×2 for now); re-run
  `analyze_submission.py --ref 53886522` after more public games; Alakazam Phase B GPU only if RuleCore L1 ≥ 25%.

---

### 2026-06-20 (run 51 - Lucario official policy + smart bench submit)
- **Worked on:** Finished Lucario bench fix (official sample policy port + smart 1–2 bench depth);
  packaged and submitted Simulation agent; wrote repo cleanup roadmap.
- **Changed:**
  - [`agent/lucario_policy.py`](agent/lucario_policy.py) — competition sample logic + `smart_bench` caps.
  - [`agent/smart_bench.py`](agent/smart_bench.py), [`agent/bench_guard.py`](agent/bench_guard.py),
    [`agent/deck_tech.py`](agent/deck_tech.py) — fixed Lucario card IDs; bench guard in `Agent.act`.
  - [`agent/rule_core.py`](agent/rule_core.py) — Lucario deck delegates to `LucarioScorer`.
  - [`scripts/smoke_test.py`](scripts/smoke_test.py) — smart setup-bench expectation.
  - [`scripts/package_submission.py`](scripts/package_submission.py) — `--scorer lucario` alias.
  - [`report/repo_cleanup_plan_20260620.md`](report/repo_cleanup_plan_20260620.md) — full cleanup + CI roadmap.
- **Verification:** `smoke_test.py` → **17/17**; L1 public gate vs samples **9.0%** (13/144) — low vs
  Search but fixes empty-bench ladder failure mode; not a Learned/RL submit.
- **Submitted:** ref **53886522** — `track_c_lucario_rulecore_smartbench.tar.gz` (PENDING).
  Prior Lucario RL ref 53885445 μ **324.6** (COMPLETE, getting wrecked).
  Best Lucario rules baseline: Search ref **53869254** μ **668.0**.
- **NEXT:** After COMPLETE + ~40 min check μ for 53886522; replay worst episodes; implement
  `scripts/record_local_battle.py`; pin Finals (Kyogre Search + best Lucario) before deadline.

---

- **Worked on:** Saved Kaggle Simulation CLI reference; documented ladder tempo /
  fast-loss scoring; enforced empty-bench policy; queued Alakazam GPU deep train (no submit).
- **Changed:**
  - [`data/KAGGLE_SIMULATION_CLI.md`](data/KAGGLE_SIMULATION_CLI.md) — episodes, replays, logs, scouting.
  - [`data/COMPETITION_SCORING.md`](data/COMPETITION_SCORING.md) — fast-win / fast-loss, bench rule.
  - [`report/kaggle_notebook_jobs/alakazam_deep_track_b.md`](report/kaggle_notebook_jobs/alakazam_deep_track_b.md) — 1M GPU job spec.
  - [`agent/agent.py`](agent/agent.py), [`agent/rule_core.py`](agent/rule_core.py),
    [`agent/evalfn.py`](agent/evalfn.py) — always bench ≥1 when possible; RL/search shaping penalty.
- **Verification:** `python scripts/smoke_test.py` → 17/17 passed.
- **Alakazam:** local 200k CPU finished (~29% peak train WR) — **not submitted** (gate still fails).
- **NEXT:** Run Alakazam deep job on Kaggle GPU; re-import Lucario after more iters; L2 package gen19 fast-basic.

---

### 2026-06-20 (run 49 - Lucario RL+MCTS Kaggle submit)
- **Worked on:** Moved Kaggle Lucario downloads into repo, packaged, submitted one
  Simulation agent. No Alakazam submit (prior gate failed).
- **Changed / moved:**
  - `Downloads/` → [`report/kaggle_notebook_jobs/lucario/kaggle_download_20260620/`](report/kaggle_notebook_jobs/lucario/kaggle_download_20260620/)
    (`model_best.pth`, `metrics.csv`, `model_iter0/1.pth`, `run_meta.json`)
  - Import copy → [`report/kaggle_notebook_jobs/lucario/imported_20260620/`](report/kaggle_notebook_jobs/lucario/imported_20260620/)
  - Archive: [`dist/candidates/track_d_lucario_rl_mcts.tar.gz`](dist/candidates/track_d_lucario_rl_mcts.tar.gz) (~52 MiB)
- **Model choice:** `model_best.pth` = iter-0 champion (`promoted=1`, gate 97.5%);
  iter 1 did not promote (gate 52.5%). Duplicate `model_best (1).pth` identical — ignored.
- **Verification:**
  - `import_lucario_rl_outputs.py --gate-games 4` → dry-run OK; public field 8.3% (4/48) — early checkpoint, vs-random only
  - `kaggle competitions submit` → **SUCCESS**
- **Not submitted:** `track_b_learned_alakazam` — gate **32/110** vs Search 119/240 (failed)
- **NEXT:** Let Kaggle Lucario notebook finish more iters; re-download and re-submit when
  `metrics.csv` shows stable promotions. Optional: L2 package gen19 fast-basic Track B.

---

### 2026-06-20 (run 48 - gen19 lane elites → Track B L1)
- **Worked on:** Promoted gen19 lane elites spread/control (0.753) and fast-basic
  (0.714) to per-deck Track B train → distill → L1 gate. No packaging, no Kaggle
  upload.
- **Changed:**
  - Exported [`agent_decks/deck_rl/gen19_spread_control.csv`](agent_decks/deck_rl/gen19_spread_control.csv)
    from `population/gen019_ind06.csv` and
    [`agent_decks/deck_rl/gen19_fast_basic.csv`](agent_decks/deck_rl/gen19_fast_basic.csv)
    from `population/gen019_ind05.csv` (matched via `deck_ga.json` counts).
  - Artifacts: `agent/models/distilled_gen19-spread-control_v1.npz`,
    `agent/models/distilled_gen19-fast-basic_v1.npz`.
- **Verification:**
  - `validate_deck.py` → both exported decks PASS
  - `train_track_b_deck.py` ×2 (100k timesteps, CPU, `--holdout a2_kyogre`,
    `--gate-games 12`)
- **Results (L1 pool gate, 12 games × 6 opponents = 72 games):**
  - **spread/control:** Learned 60/72 vs Search 66/72 — gate **passed** (SPRT
    `accept_b`); Kyogre holdout eval peaked 60% @60k steps
  - **fast-basic:** Learned 66/72 vs Search 57/72 — gate **passed**; Kyogre
    holdout eval peaked 95% @40k steps
- **Parallel:** User downloaded early Lucario Kaggle outputs (`model_best.pth` =
  iter-0 champion, `metrics.csv` through iter 1 only); import not run yet.
- **NEXT:** L2 gate + `--package` on **fast-basic** first
  (`--gate-games 40 --package`); optionally import Lucario via
  `scripts/import_lucario_rl_outputs.py --source <Downloads>`. No Kaggle upload
  without explicit user OK.

---

### 2026-06-20 (run 47 - Deck RL Phase 2d matchup-collapse penalty)
- **Worked on:** T16 Deck RL Phase 2d — `matchup_collapse_penalty` in deck GA
  fitness. No policy RL and no Kaggle upload.
- **Changed:**
  - [`rl/deck_balance.py`](rl/deck_balance.py): `matchup_collapse_penalty()` —
    penalizes min win rate vs opponents with suite weight ≥ 1.0 below floor 0.30.
  - [`rl/benchmark.py`](rl/benchmark.py): per-opponent `weight`, `min_benchmark_win_rate`,
    `matchup_collapse_penalty` in eval result.
  - [`rl/train_deck_campaign.py`](rl/train_deck_campaign.py): fitness =
    `raw × (1 − 0.15×balance) × (1 − 0.25×collapse)`; logs `collapse` + `min_wr`.
  - [`tests/test_deck_collapse_penalty.py`](tests/test_deck_collapse_penalty.py): 5
    unit tests.
- **Verification:**
  - `python -m py_compile rl/deck_balance.py rl/benchmark.py rl/train_deck_campaign.py`
  - `python -m pytest tests/test_deck_collapse_penalty.py tests/test_deck_lane_selection.py tests/test_deck_genome_mutations.py -q` → 14 passed
  - `python scripts/smoke_test.py` → 17 passed
  - 20-gen GA: `python rl/train_deck_campaign.py --phase deck --generations 20
    --population 8 --games-eval 6 --fresh --seed 99` (~174s CPU)
- **Results (vs run 45, 10 gens games=4, no collapse penalty):**
  - **All 4 lanes present every generation** (gen0–gen19)
  - Gen19 global best: **0.753** (spread/control) — penalized fitness; run 45 gen9
    was 0.825 under old formula
  - Gen19 lane elites: anti-Kyogre **0.561**, fast-basic **0.714**, spread/control
    **0.753**, resilient-generalist **0.200**
  - Prior global checkpoint best **0.864** not beaten; `best_deck.csv` unchanged
  - Collapse penalty active: decks with `min_wr=0.00` get `collapse=1.00` (25% cut)
- **Artifacts:** [`report/deck_rl/lane_elites.json`](report/deck_rl/lane_elites.json)
  updated at gen 19.
- **NEXT:** Promote top lane elites to per-deck Track B (`scripts/train_track_b_deck.py`)
  starting with spread/control (0.753) and fast-basic (0.714); gate at L1 before
  packaging. Consider label-length cap in `DeckGenome` to stop mut_x stacking bloat.

---

### 2026-06-20 (run 46 - Lucario RL+MCTS post-run packaging path)
- **Worked on:** Made the nearly finished Kaggle Lucario self-play run actionable
  after download. No Kaggle upload attempted.
- **Changed:**
  - Added `agent/lucario_mcts_runtime.py`, a mechanical copy of the Lucario
    RL+MCTS notebook runtime for submission inference.
  - Added `agent/lucario_mcts_policy.py`, a safe wrapper that loads
    `model_best.pth`, runs deterministic MCTS with a configurable submit-time
    search count, and falls back to `RuleCoreScorer` if Torch/Search/model load
    fails.
  - Extended `scripts/package_submission.py` with `--scorer lucario_mcts`,
    `--model`, optional `--meta`, and compact fp16 checkpoint packaging to keep
    the archive size away from likely upload limits.
  - Added `scripts/import_lucario_rl_outputs.py` to copy downloaded Kaggle
    artifacts, summarize `metrics.csv`, build `track_d_lucario_rl_mcts`, and
    optionally run `scripts/gate_vs_public.py`.
  - Updated `notebooks/lucario/README.md`, `report/lucario_postrun_checklist.md`,
    and `TASKS.md` with the exact post-run command.
- **Verification:**
  - `python -m py_compile agent\lucario_mcts_policy.py agent\lucario_mcts_runtime.py scripts\package_submission.py scripts\import_lucario_rl_outputs.py`
  - Built a dummy same-shape `model_best.pth` under
    `report/kaggle_notebook_jobs/lucario/smoke/`.
  - `python scripts\import_lucario_rl_outputs.py --source report\kaggle_notebook_jobs\lucario\smoke --name smoke_import_lucario_mcts --dest report\kaggle_notebook_jobs\lucario\smoke_import`
    dry-run packaged successfully.
- **Results:** compact dummy Lucario MCTS archive is **~53,078 KiB** (down from
  ~101,461 KiB before fp16 checkpoint compaction) and dry-run import returns a
  legal 60-card deck. This proves the package path, not model strength.
- **NEXT:** When Kaggle finishes, download outputs, then run:
  `python scripts\import_lucario_rl_outputs.py --source report\kaggle_notebook_jobs\lucario --name track_d_lucario_rl_mcts --gate-games 4`.
  If the public gate clears current baselines, run a larger gate before asking
  for explicit upload approval.

---

### 2026-06-20 (run 45 - RuleCore Crustle wall follow-up, not shippable)
- **Worked on:** Stayed in the RuleCore Lucario Crustle-wall lane only. No Deck
  RL/GA work and no Kaggle upload.
- **Changed:**
  - `agent/deck_tech.py`: added Lucario search-card tech for Dusk Ball,
    Premium Power Pro, Fighting Gong, and Poke Pad.
  - `agent/rule_core.py`: throttles search/draw in Crustle wall games once the
    wall line is started, caps setup-bench picks to distinct high-priority
    Basics, and routes `ATTACH_FROM` energy acceleration toward the focused
    Makuhita/Hariyama line.
  - `scripts/trace_public_matchup.py`: card-choice traces now print selected
    card IDs, which exposed late Hariyama/search timing failures.
  - `report/public_gate/results.md` and `TASKS.md`: checkpointed the measured
    result and decision.
- **Verification:**
  - `python -m py_compile agent\deck_tech.py agent\rule_core.py scripts\trace_public_matchup.py scripts\package_submission.py`
  - `python scripts\package_submission.py --name track_c_rulecore_tech_lucario --scorer rulecore --deck agent_decks\real_mega_lucario_ex.csv`
  - `python scripts\gate_vs_public.py --agent dist\candidates\track_c_rulecore_tech_lucario.tar.gz --games 12 --only crustle`
- **Results:** best kept targeted sample reached **15.0%** Crustle-only (basic
  Crustle 16.7%, anti-wall 12.5% in that sample). Final kept-snapshot retest was
  **9.5%** (basic Crustle 16.7%, anti-wall 0%). This remains below both prior
  RuleCore 23.6% full-public and the submitted Lucario-search 20% public gate.
- **Rejected experiments:** Hero Cape wall-line routing and protecting underbuilt
  Makuhita on forced promotion both regressed targeted gates, so they were
  reverted.
- **Decision:** do **not** submit `track_c_rulecore_tech_lucario`.
- **NEXT:** Implement an explicit Crustle sub-policy for `TO_HAND` and main-phase
  trainer use: search Hariyama over generic energy/cards when a Makuhita exists,
  stop nonessential draw/search once opponent prizes are low, and only then
  rerun `--games 12 --only crustle` before any full public gate.

---

### 2026-06-20 (run 45 - Deck RL Phase 2c role/chain-aware mutations)
- **Worked on:** T16 Deck RL Phase 2c — registry-backed `support_role_swap` and
  `chain_tune` mutation operators. No policy RL and no Kaggle upload.
- **Changed:**
  - [`rl/deck_card_registry.py`](rl/deck_card_registry.py): cached loader for
    `report/deck_rl/registry.json` (support roles, evolution chains).
  - [`rl/deck_genome.py`](rl/deck_genome.py): `support_role_swap` (same trainer
    role from `role_index`), `chain_tune` (paired thicken/thin on evolution lines).
  - [`tests/test_deck_genome_mutations.py`](tests/test_deck_genome_mutations.py): 4
    unit tests (registry, role swap, chain tune, mutate legality).
- **Verification:**
  - `python -m py_compile rl/deck_card_registry.py rl/deck_genome.py`
  - `python -m pytest tests/test_deck_genome_mutations.py tests/test_deck_lane_selection.py -q` → 9 passed
  - `python scripts/smoke_test.py` → 17 passed
  - 10-gen GA: `python rl/train_deck_campaign.py --phase deck --generations 10
    --population 8 --games-eval 4 --fresh --seed 99` (~58s CPU)
- **Results (vs run 44, 5 gens):**
  - **All 4 lanes present every generation** (gen0–gen9)
  - Gen9 global best: **0.825** (`real_mega_abomasnow_ex` lane, fast-basic) — up from 0.798
  - Gen9 lane elites: anti-Kyogre **0.765**, fast-basic **0.825**, spread/control
    **0.783**, resilient-generalist **0.423** (all up except anti-Kyogre −0.033)
  - Prior global checkpoint best **0.864** not beaten; `best_deck.csv` unchanged
- **Artifacts:** [`report/deck_rl/lane_elites.json`](report/deck_rl/lane_elites.json)
  updated at gen 9.
- **NEXT:** Phase 2d — matchup-collapse penalty in fitness; then longer GA
  (`--generations 20`, `--games-eval 6`) before promoting lane elites to per-deck
  Track B.

---

### 2026-06-20 (run 44 - Deck RL Phase 2b per-lane GA selection)
- **Worked on:** T16 Deck RL Phase 2b — per-lane survivor quotas + same-lane
  round-robin breeding in `evolve_decks()`. No policy RL and no Kaggle upload.
- **Changed:**
  - [`rl/train_deck_campaign.py`](rl/train_deck_campaign.py): `_survivor_target`,
    `_select_survivors_by_lane`, `_inject_lane_seed`, `_ensure_lane_coverage`,
    `_breed_next_generation`, `_lane_survivor_counts`; replaced global top-half
    selection with lane-stratified mini-tournaments + extinction recovery.
  - [`tests/test_deck_lane_selection.py`](tests/test_deck_lane_selection.py): 5
    unit tests for selection, breeding, and registry inject (no sim).
- **Verification:**
  - `python -m py_compile rl/train_deck_campaign.py`
  - `python -m pytest tests/test_deck_lane_selection.py -q` → 5 passed
  - `python scripts/smoke_test.py` → 17 passed
  - Smoke GA: `python rl/train_deck_campaign.py --phase deck --generations 5
    --population 8 --games-eval 4 --fresh --seed 99` (~29s CPU)
- **Results (vs run 43 global selection):**
  - **All 4 lanes present every generation** (gen0–gen4 lane elites + survivors=1 each)
  - Gen4 global best: **0.798** (`mut_x_deck_deck`, lane=anti-Kyogre)
  - Gen4 lane elites: anti-Kyogre **0.798**, fast-basic **0.720**, spread/control
    **0.722**, resilient-generalist **0.395**
  - Prior global checkpoint best **0.864** not beaten; `best_deck.csv` unchanged
- **Artifacts:** [`report/deck_rl/lane_elites.json`](report/deck_rl/lane_elites.json)
  has 4 entries at gen 4 (was 2 under run 43).
- **NEXT:** Phase 2c — role/chain-aware mutations and matchup-collapse penalty; then
  longer GA (`--generations 10–20`) before promoting lane elites to per-deck Track B.

---

### 2026-06-20 (run 43 - Deck RL lane GA smoke, 5 generations)
- **Worked on:** Follow-on from run 42 NEXT — cheap multi-gen lane-balanced GA to
  validate wiring under evolution pressure. No policy RL and no Kaggle upload.
- **Ran:** `python rl/train_deck_campaign.py --phase deck --generations 5
  --population 8 --games-eval 4 --fresh --seed 99` (~28s on CPU).
- **Results:**
  - Gen4 global best: **0.814** (`mut_mut_real_mega_abomasnow_ex`, lane=fast-basic)
  - Gen4 lane elites: anti-Kyogre **0.755**, fast-basic **0.814**
  - spread/control and resilient-generalist **extinct by gen 2** under global
    top-half selection (expected; per-lane tournament selection is Phase 2b)
  - Prior global checkpoint best **0.864** not beaten; `best_deck.csv` unchanged
- **Artifacts:** [`report/deck_rl/lane_elites.json`](report/deck_rl/lane_elites.json),
  [`report/deck_rl/lane_elites.md`](report/deck_rl/lane_elites.md) updated at gen 4.
- **NEXT:** Phase 2b — per-lane survivor quotas or mini-tournaments so spread/control
  and resilient-generalist lanes stay in population; then role/chain-aware mutations.

---

### 2026-06-20 (run 42 - Deck RL Phase 2a lane-aware GA wiring)
- **Worked on:** T16 Deck RL Phase 2a — archetype-aware deck-search lane support
  using the Phase 1 registry. No policy RL training and no Kaggle upload attempted.
- **Changed:**
  - Added [`rl/deck_lane_registry.py`](rl/deck_lane_registry.py) to load
    [`report/deck_rl/candidate_registry.csv`](report/deck_rl/candidate_registry.csv),
    normalize lanes (`anti-kyogre-baseline` → `anti-Kyogre`), and group seed paths.
  - Extended [`rl/deck_genome.py`](rl/deck_genome.py) with `lane` field,
    `seed_population_balanced()`, same-lane `mutate`/`crossover` inheritance
    (Starmie/Kyogre hybrids stay in `spread/control` via parent lane, not re-inference).
  - Extended [`rl/deck_ga_checkpoint.py`](rl/deck_ga_checkpoint.py) to serialize `lane`
    (backward compatible with older checkpoints).
  - Wired [`rl/train_deck_campaign.py`](rl/train_deck_campaign.py): `--registry`,
    `--lanes`, lane-stratified seeding, per-lane elite archive to
    [`report/deck_rl/lane_elites.json`](report/deck_rl/lane_elites.json) and
    [`report/deck_rl/lane_elites.md`](report/deck_rl/lane_elites.md).
  - Updated `TASKS.md` T16 with the Phase 2a checkpoint.
- **Verification:**
  - `python -m py_compile rl/deck_lane_registry.py rl/deck_genome.py rl/deck_ga_checkpoint.py rl/train_deck_campaign.py`
  - Inline lane wiring smoke: 17 registry seeds, 4 lanes represented in pop=8,
    Starmie → `spread/control`, mutate/crossover preserve lane
  - `python scripts/smoke_test.py` → 17 passed, 0 failed
  - `python scripts/validate_deck.py --no-engine` → all 16 `agent_decks/*.csv` passed
  - Tiny GA: `python rl/train_deck_campaign.py --phase deck --generations 1 --population 8 --games-eval 2 --fresh --seed 99`
    → lane registry 17 seeds; 4 lane elites written; gen0 best fitness=0.781
    (`a2_big_basic_29_energy`, lane=anti-Kyogre). Global `best_fitness` unchanged
    (0.864 prior checkpoint not beaten).
- **Current best evidence:** unchanged. Live protected pair remains Kyogre
  heuristic 633.0 and TA1 Search 626.0; best local learned candidate remains
  `track_b_learned_rl_deck_kaggle_20260619` with 210/240 = 87.5% gate.
- **Blockers:** none for Phase 2a wiring. Per-lane tournament selection and
  role/chain-aware mutations remain Phase 2b. Any Kaggle upload still requires
  explicit user approval.
- **NEXT:** Run a cheap multi-gen lane-balanced GA (`--generations 5–10`,
  `--games-eval 4–6`) and compare per-lane elites vs global best before promoting
  any candidate to per-deck Track B training.

---

### 2026-06-20 (run 41 - RuleCore Lucario deck-tech layer, gated not shippable)
- **Worked on:** Continued from `report/HANDOFF_20260620.md` and run 40. Built
  the first real deck-aware tech layer over `RuleCoreScorer` to target the
  diagnosed Crustle wall/gust gap. No Kaggle upload attempted.
- **Changed:**
  - Added `agent/deck_tech.py` with declarative Lucario tech facts: Boss's Orders
    gust, Switch/Prime Catcher repositioning, Makuhita/Hariyama non-ex wall line,
    draw cards, Gravity Mountain, and setup priorities.
  - Updated `agent/rule_core.py` to load package-local deck tech, detect gust and
    repositioning, project Makuhita as a potential Hariyama attacker when it can
    evolve this turn, prefer wall-line energy routing, and avoid weak Lucario
    setup openings.
  - Updated `scripts/package_submission.py` with `--scorer rulecore`.
  - Added `scripts/trace_public_matchup.py` for compact candidate-vs-public
    trajectory traces.
  - Built `dist/candidates/track_c_rulecore_tech_lucario.tar.gz`.
  - Updated `report/public_gate/results.md` and `TASKS.md`.
- **Verification:**
  - `python -m py_compile agent\deck_tech.py agent\rule_core.py scripts\trace_public_matchup.py scripts\package_submission.py`
  - `python scripts\package_submission.py --name track_c_rulecore_tech_lucario --scorer rulecore --deck agent_decks\real_mega_lucario_ex.csv`
  - Targeted Crustle gate (`--games 8 --only crustle`): basic Crustle bot moved
    off 0% in one smoke (best 25.0%, full-gate sample 12.5%); anti-wall Crustle
    stayed 0.0%.
  - Full public smoke (`--games 8`): **12.0%** suite mean (6/50 decided), worse
    than prior rulecore 23.6% and submitted Lucario-search 20%.
- **Decision:** do **not** submit `track_c_rulecore_tech_lucario`. The tech layer
  is real infrastructure, but the candidate is below the current gate.
- **NEXT:** Use `scripts/trace_public_matchup.py` to implement a true Crustle
  wall state machine: open/promote the non-ex line, stop over-benching/drawing
  into deck-out, switch Hariyama active once at 3 energy, and only then re-run
  targeted Crustle gates before any full public gate.

---

### 2026-06-20 (run 40 - Deck RL Phase 1 registry and replay hook)
- **Worked on:** Scoped T16 Deck RL Phase 1 implementation from the user-provided
  deck discovery plan. No training run and no Kaggle upload attempted.
- **Environment:** `scripts/setup_env.sh` hit the documented Windows pip
  incompatibility because this pip rejects `--break-system-packages`; used the
  Windows fallback `python -m pip install -r requirements.txt`, which completed.
- **Changed:**
  - Added `scripts/build_card_registry.py`.
  - Generated `report/deck_rl/registry.json` from `data/EN_Card_Data.csv`,
    including card roles, attack cost/damage/effect tags, energy profiles,
    evolution-chain index, simulator-sensitive flags, and local seed-deck
    summaries.
  - Generated `report/deck_rl/candidate_registry.csv` with local seed decks
    mapped to initial lanes: anti-Kyogre, fast-basic, spread/control, and
    resilient-generalist.
  - Generated `report/deck_rl/archetype_seed_notes.md`; fixed lane priority so
    the Starmie spread list is treated as spread/control even though it also
    includes Kyogre.
  - Added `scripts/mine_episode_replays.py`, an offline-only downloaded
    replay/log indexer, and generated `report/deck_rl/replay_index.csv` plus
    `report/deck_rl/mined_archetypes.md`. Current local replay folders contain
    no replay JSON, so the index has 0 rows by design.
  - Updated `TASKS.md` with the completed scoped Phase 1 checkpoint.
- **Verification:**
  - `python -m py_compile scripts/build_card_registry.py scripts/mine_episode_replays.py`
  - `python scripts/build_card_registry.py` -> cards=1267 unique card IDs,
    decks=17 seed decks indexed.
  - `python scripts/mine_episode_replays.py` -> wrote schema-valid 0-row replay
    index because no local replay JSON is present.
  - `python scripts/smoke_test.py` -> 17 passed, 0 failed.
  - `python scripts/validate_deck.py --no-engine` -> all 16 `agent_decks/*.csv`
    passed data-only validation.
- **Current best evidence:** unchanged. Live protected pair remains Kyogre
  heuristic 633.0 and TA1 Search 626.0; best local learned candidate remains
  `track_b_learned_rl_deck_kaggle_20260619` with 210/240 = 87.5% gate.
- **Blockers:** none for Phase 1. Replay mining needs downloaded replay/log JSON
  under `report/replays` and/or `report/agent_logs`. Any Kaggle upload still
  requires explicit user approval.
- **NEXT:** Use the generated registry to implement the first archetype-aware
  search-lane seeds/operators in `rl/deck_genome.py` / `rl/train_deck_campaign.py`
  for anti-Kyogre, fast-basic, spread/control, and resilient-generalist, then run
  a cheap local template/GA pass before any per-deck Track B training.

---

### 2026-06-20 (run 39 - Simulator resources folded into deck RL plan)
- **Worked on:** Incorporated user-provided official simulator-behavior notes,
  card metadata description, and Kaggle episode replay resource guidance into the
  repo plan. No training run and no Kaggle upload attempted.
- **Changed:**
  - Added `data/SIMULATOR_RESOURCE_NOTES.md` with competition-specific simulator
    caveats: simulator legal options are authoritative, some official-rule legal
    attacks may be unselectable, Mega Zygarde ex target order is automatic, and
    simultaneous-KO Prize order/draw behavior must be treated as simulator truth.
  - Updated `report/deck_rl_system_plan_20260620.md` to use simulator quirks in
    feature/legality design and to add replay mining for BC/RL/IL from Kaggle
    episodes/logs.
  - Updated `TASKS.md` with the completed T16 resource-ingestion checkpoint.
- **Current best evidence:** unchanged. Live protected pair remains Kyogre
  heuristic 633.0 and TA1 Search 626.0; best local learned candidate remains
  `track_b_learned_rl_deck_kaggle_20260619` with 210/240 = 87.5% gate.
- **Blockers:** none for docs. Live replay/log mining requires Kaggle credentials
  and available episode exports; any upload still requires explicit user approval.
- **NEXT:** Implement Phase 1 plus replay hooks: add
  `scripts/build_card_registry.py`, generate `report/deck_rl/registry.json`, add
  a `scripts/mine_episode_replays.py` stub for downloaded replay/log JSON, and
  seed `report/deck_rl/archetype_seed_notes.md`.

---

### 2026-06-20 (run 39 - Robust deck-search subsystem: maximin/CVaR + PSRO + GPU surrogate)
- **Worked on:** User goal "win rate vs anything". Built a self-contained robust
  deck-optimisation system (does NOT touch report/rl_deck_campaign/). Reframed the
  objective from mean-vs-fixed-suite to maximin/CVaR over an expanding adversarial field.
- **Design doc:** `report/robust_deck_optimization_design.md` (+ inline architecture
  diagram). Grounded in comp facts: cabt CPU engine, agent(obs_dict) contract, 10-min/game,
  60/<=4 deck rules, ~2090-team Simulation mu ladder, 23 ms/game/core measured.
- **New modules (all CPU-verified):**
  - `rl/robust_fitness.py` - weighted mean + CVaR + maximin objective.
  - `rl/meta_solver.py` - zero-sum regret-matching Nash; adversarial opponent weights (PSRO-lite).
  - `rl/gauntlet.py` - opponent field = benchmark + agent_decks + mined ladder decks + self elites; train/holdout split; CRN pairwise eval via scripts.arena.play_matchup.
  - `rl/winrate_surrogate.py` - P(A beats B) model; PyTorch-CUDA if available else NumPy MLP; prunes O(D^2) matchups.
  - `rl/robust_search.py` + `scripts/robust_deck_search.py` (CLI) - PSRO-lite GA loop with co-evolution, holdout validation, checkpoints to report/robust_deck_rl/.
  - `scripts/extract_gauntlet_from_replays.py` - downloaded episode replays -> report/deck_rl/mined_decks/ (auto-consumed by gauntlet).
- **Episode data:** user supplied `report/deck_rl/episode_dataset_manifest.csv` (daily
  ladder episode datasets, 1.2k-7.8k episodes/day, ~3-21GB each; median avg score
  627->1013 over 4 days = field strengthening fast). Extractor wired to mine these into
  the gauntlet; user downloads datasets locally (sandbox has no Kaggle egress / 4GB disk).
- **Verification:** `tests/test_robust_core.py` (6) + `tests/test_surrogate.py` (2) =
  8/8 pass (RPS Nash -> uniform 1/3, value 0.5; CVaR lower-tail; robust prefers no-collapse
  deck; surrogate learns synthetic matchup corr>0.6). End-to-end CLI smoke OK; 10-game run
  gave best_robust=0.113 (non-zero, worst-case-weighted), legal 60-card best_deck.csv.
- **Could NOT run in sandbox:** torch CUDA (4GB disk / proxy-blocked CPU index) and real
  ladder mining (no egress). Surrogate GPU path + replay mining must run on the user's box.
- **Blockers:** none for the subsystem. Real-field gauntlet needs the user to download a
  daily episode dataset + run the extractor.
- **NEXT (user):** (a) `python scripts/robust_deck_search.py --generations 30 --population 16
  --games 10 --surrogate` on the GPU box; (b) for the real field, download one daily episode
  dataset, run `scripts/extract_gauntlet_from_replays.py --min-score 900`, then re-run search;
  (c) watch holdout_robust vs best_robust in metrics.csv for overfitting.

---

### 2026-06-20 (run 38 - Mega Lucario ex RL+MCTS Kaggle notebook built from official sample)
- **Worked on:** User request — adapt the official "Reinforcement Learning and MCTS
  sample code" (kiyotah) to the Mega Lucario ex deck, improve it, and package for a
  robust Kaggle GPU run (user runs on Kaggle, not locally).
- **Added:** `notebooks/lucario/` — `lucario_rl_mcts.ipynb` (7 cells: GPU-setup,
  config, defs, `main()`, inspect), `lucario_rl_mcts.py` (script form),
  `kernel-metadata.json` (GPU+internet, competition_sources attached), `README.md`.
  Plus top-level `notebooks/lucario_rl_mcts.py` copy.
- **Deck:** `agent_decks/real_mega_lucario_ex.csv` validated — 60 cards, legal
  (battle_start errorPlayer=-1); 4x Mega Lucario ex (678) + Riolu/Solrock/Lunatone/
  Makuhita/Hariyama line, 13 Fighting Energy, Carmine/Lillie's/Boss's/Dusk Ball engine.
- **Improvements over sample:** deck swap; MCTS sims 10→48; model d128/2h/256ff/1+1
  → d256/4h/512ff/2+2; iters 5→40 + wall-clock TIME_BUDGET (8h default) for clean
  save; **champion-gating** checkpoint selection (promote `model_best.pth` only if a
  new net beats the incumbent ≥0.55 H2H — directly fixes the run-34/35 "final-only
  packaging discards a stronger earlier checkpoint" finding); replay buffer (last 3
  iters); Dirichlet root noise + temperature sampling (self-play only); fixed seeds,
  grad-clip, cosine LR, AMP autocast; `metrics.csv` + `run_meta.json` + per-iter
  snapshots. All knobs env-overridable (`LUC_*`).
- **Verification (sandbox, CPU):** `py_compile` OK; notebook JSON valid + defs cell
  compiles; engine smoke test PASSED — deck legal, `search_begin/step/end` work with
  the deck, 3 full random games completed. Torch CUDA build cannot install in the 4GB
  CPU sandbox (CUDA deps too large; pytorch CPU index proxy-blocked), so the NN/training
  path was not executed locally — it is verbatim/minimally-changed from the known-good
  public sample and must be exercised on Kaggle GPU.
- **Assumption (labeled):** Lucario card IDs taken from the existing validated
  `real_mega_lucario_ex.csv`, matching the official Mega Lucario ex rule-based sample.
- **Blockers:** none for the deliverable. Full training requires the user's Kaggle GPU.
- **NEXT (user):** `kaggle kernels push -p notebooks/lucario`; confirm GPU +
  competition data attached; Run All; download `/kaggle/working/lucario_rl/` and check
  `metrics.csv` (`vs_random` trending up, `promoted` flips on gate passes). Do NOT
  submit — training/dev artifact only.

---

### 2026-06-20 (run 37 - Deck RL system plan)
- **Worked on:** T16 planning for a robust deck-discovery RL system. No training
  run and no Kaggle upload attempted.
- **Changed:**
  - Added `report/deck_rl_system_plan_20260620.md`, an execution plan for
    archetype-aware deck RL: card/archetype registry, semantic deck genome,
    legality and stability constraints, benchmark fitness, search loops,
    per-deck policy RL, checkpoint sweep, and ladder-probe discipline.
  - Updated `TASKS.md` with the completed T16 planning checkpoint.
- **Current best evidence:** unchanged from run 36. Live protected pair remains
  Kyogre heuristic 633.0 and TA1 Search 626.0. Best local learned candidate
  remains `track_b_learned_rl_deck_kaggle_20260619` with 210/240 = 87.5% gate.
- **Blockers:** none for planning. Phase 1 implementation and any serious Track B
  retraining still require normal validation and, for GPU runs, user/Kaggle GPU.
- **NEXT:** Implement Phase 1 from `report/deck_rl_system_plan_20260620.md`:
  add `scripts/build_card_registry.py`, generate `report/deck_rl/registry.json`
  and `report/deck_rl/archetype_seed_notes.md`, then use that registry to define
  anti-Kyogre, fast-basic, spread/control, and resilient-generalist search lanes.

---

### 2026-06-20 (run 36 - Submission decision analysis + dual-path recommendation)
- **Worked on:** T15/T16 offline analysis and documentation. No Kaggle submission attempted; no GPU work possible in sandbox.
- **Changed:**
  - Added `report/submission_decision_20260620.md` — comprehensive 4-section analysis (current position, candidate ranking, why 100k beats longer runs, decision tree with pros/cons).
  - Added `report/checkpoint_sweep_execution_guide.md` — step-by-step execution for Option B (checkpoint sweep on Kaggle).
  - Added `RUN_36_HANDOFF.md` — quick-reference summary of what's ready and options available.
  - Verified candidate ranking: **100k (210/240 = 87.5%) > 3M ramp (201/240 = 83.8%) > 1M ramp (193/240 = 80.4%)**.
  - Confirmed key insight: **longer timesteps without checkpoint sweeping do NOT improve gate** due to final-only packaging throwing away stronger intermediate checkpoints at 400k–500k steps.
  - Cross-validated against 1M and 3M training curves; confirmed both used final-only distillation, explaining why they underperformed the 100k gate.
- **Metrics:**
  - Best available candidate: `track_b_learned_rl_deck_kaggle_20260619` (100k timesteps, gate **210/240 = 87.5%**, verified generalization, ready for submission).
  - Current live best: Kyogre heuristic **633.0** (rank ~1219/2090, protected); TA1 SearchScorer **626.0** (protected).
  - Ladder unchanged since run 35 (as of 2026-06-20T02:29Z, 6 complete + 4 completed submissions).
  - Checkpoint sweep cell fully ready: `report/kaggle_notebook_jobs/sweep_track_b_cell.md` (30–60 min Kaggle run, script verified no errors).
- **Files created:** 3 new decision/guide documents + 1 handoff + 1 progress update. All analysis complete.
- **Blockers:** None for offline analysis or documentation. Kaggle GPU run (if Option B chosen) requires user to execute on their platform.
- **NEXT (user decision required):**
  - **Option A (fast, 1 hour total):** Submit `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` now as P1 probe. Expected ladder μ: 520–600 after ~40 min of games. Gate proof: 210/240. Clean ladder data point; keeps Kyogre 633.0 as backup.
  - **Option B (strong, 2–3 days):** Run checkpoint sweep on Kaggle first (using `sweep_track_b_cell.md`). Expected: finds best intermediate checkpoint at 400k–500k, likely gate ≥215/240, estimated ladder μ 550–650. Higher ceiling but delayed.
  - **Also:** Pin current best pair (Kyogre 633.0 ref#53854707 + TA1 626.0 ref#53856711) to Finals in Kaggle UI to prevent auto-disable on next probes.
  - See `RUN_36_HANDOFF.md` for quick reference on both paths.

---

### 2026-06-20 (run 35 - Kaggle API refresh + improvement plan + checkpoint sweep cell)
- **Used Kaggle API/read-only:** refreshed Simulation submissions and competition
  metadata. Confirmed Simulation `teamCount=2090`, `userRank=1219`,
  `maxDailySubmissions=5`, deadline `2026-08-16T23:59:00Z`.
- **Current live scores:** Kyogre heuristic `633.0`; TA1 Search Kyogre+2e
  `626.0`; TA2 Search Abomasnow+4e declined to `548.6`; buggy Learned probes
  remain `490.4` and `468.9`.
- **Updated:** `report/ladder_history.csv` with latest API score transitions.
- **Added:** `report/competition_improvement_plan_20260620.md` with diagnosis and
  prioritized plan.
- **Added:** `report/kaggle_notebook_jobs/sweep_track_b_cell.md`, a Kaggle GPU
  cell that trains 5x100k, distills/gates each checkpoint, and packages the best
  checkpoint instead of blindly packaging the final policy.
- **Key finding:** the 1M ramp run was worse because final-only packaging ignored
  stronger intermediate policies around 400k-500k.
- **NEXT:** Run the sweep cell on Kaggle when ready, download
  `/kaggle/working/track_b_sweep_outputs.zip`, import best package/gate report,
  then decide whether it beats the 100k learned candidate (`210/240` gate).

---

### 2026-06-20 (run 34 - Kaggle 1M ramp Track B imported; PASS but weaker than 100k)
- **Imported downloaded 1M Kaggle ramp artifacts** into
  `report/kaggle_notebook_jobs/rl_deck_ramp_1m_20260620/`: `rl_policy (1).zip`,
  `distilled_rl_deck_ramp_v1.npz`, `distilled_v1 (1).npz`,
  `track_b_learned_rl_deck_ramp.tar.gz`, `track_b_learned_rl_deck_ramp_gate.md`,
  `checkpoint (1).json`, `eval_best-deck (1).json`, and run JSON.
- **Training proof:** checkpoint/run log `status=ok`, `timesteps=1000000`,
  `device=cuda`, `n_envs=4`, `opponents=benchmark`, holdout `a2_kyogre`.
- **Gate PASS confirmed:** Learned **193/240 = 80.4%** vs pool; Search baseline
  **201/240 = 83.8%**; SPRT **accept_b**; dry-run import OK; package built.
- **Promoted local copy for audit:** 
  `dist/candidates/track_b_learned_rl_deck_ramp_1m_20260620.tar.gz`; gate copy at
  `report/track_b_gates/track_b_learned_rl_deck_ramp_1m_20260620_gate.md`.
- **Decision:** keep the earlier 100k Kaggle candidate as the preferred upload
  candidate (`210/240 = 87.5%` gate). The 1M ramp package is valid but weaker.
- **NEXT:** submit the 100k candidate only if the user explicitly approves:
  `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz`. Do not submit
  the 1M ramp package unless we intentionally want a comparison ladder probe.

---

### 2026-06-19 (run 33 - RL deck candidate validation & readiness analysis)
- **Worked on:** T16 (Run SPRT gates) — offline validation, analysis, and reporting (no Kaggle upload).
- **Changed:** `report/ladder_analysis_20260619.md` (new), `report/rl_deck_candidate_readiness_20260619.md` (new).
- **Validated:** `track_b_learned_rl_deck_kaggle_20260619.tar.gz` with 300-game test.
- **Metrics:**
  - **New RL deck (300g vs random):** 272/300 = **90.67%** (ranked 4th locally, below A2/A4/A1 at 96–97%)
  - **Improvement vs buggy learned:** +13.9× (90.67% vs 6.94%)
  - **Gate (Kaggle):** ✅ PASS (Learned 210/240 = 87.5%, SPRT accept_b)
  - **Generalization proof:** Holdout (a2_kyogre, never trained) ~50–60% throughout 100k steps
  - **Ladder history (all 5 day-1 submissions):** A2 Kyogre leads at 633.0; Track B learned (buggy) collapsed to 468–490; Track A SearchScorer stable at 580–626.
- **Key findings:**
  - ✅ New RL deck is **technically sound** (stable inference, archive verified, no crashes).
  - ✅ **Generalization proven** (holdout deck tested; not memorizing).
  - ✅ **Best available learned candidate** (vs prior buggy attempts).
  - ⚠️ **Deck is GA-optimized for benchmark proxy** (not proven on live meta).
  - 📊 **Estimated ladder:** 520–580 μ (below heuristic leader 633, above buggy 468–490).
- **Files changed:** Ladder analysis report, readiness report.
- **Blockers:** none for offline work; Kaggle CLI unavailable in sandbox (no live ladder fetch, uses historical CSV).
- **NEXT:** Await user approval to submit `track_b_learned_rl_deck_kaggle_20260619.tar.gz` when a Kaggle slot opens. Optional parallel: deep-run training (4M additional steps) for higher ceiling. All technical readiness complete; ladder proof awaiting submission.

---

### 2026-06-19 (run 30 - Kaggle T4x2 MCTS/RL notebook tracking)
- **Tracked live Kaggle notebook attempt:** user screenshot shows Draft Session
  **GPU T4 x2**, age 8m, CPU ~397%, RAM 2.8GiB, **GPU0/GPU1 0.0%**. Recorded this
  in `report/training_registry.json` as `running_unverified`; no artifacts counted yet.
- **Downloaded notebook inspected:** `reinforcement-learning-and-mcts-sample-code.ipynb`
  runs a `PARALLEL KYOGRE SELF-PLAY TRAINER`. Each round first runs CPU
  multiprocessing MCTS/self-play (`EVAL_GAMES=40`, `SELFPLAY_GAMES=200`,
  `SEARCH_COUNT=40`), then trains the PyTorch model on `device`.
- **Diagnosis:** 0% GPU is expected while the multiprocessing pool is generating
  games. The run is healthy only if the notebook printed `Train device: cuda`; the
  next useful progress lines are `Round 0 eval win rate`, `collected +...`, and
  `trained round 0`.
- **Files changed:** `report/training_registry.json`,
  `report/kaggle_notebook_jobs/current_status.md`, `PROGRESS.md`.
- **NEXT:** keep the Kaggle cell running until first round output or error. Stop
  only if it printed `Train device: cpu` or never reaches round output.

### 2026-06-19 (run 31 - Kaggle Track B training completed; artifacts on Kaggle)
- **Kaggle one-cell Track B run completed:** clone, deps, CUDA check, engine setup,
  train -> distill -> gate -> package -> collect outputs all reached step 6/6.
- **Checkpoint:** `status=ok`, `timesteps=100000`, `device=cuda`,
  `deck=report/rl_deck_campaign/best_deck.csv`, `deck_slug=best-deck`,
  `opponents=benchmark`, `n_envs=4`, `n_opponents=9`, `holdout=[a2_kyogre]`.
- **Artifacts saved in Kaggle:** `/kaggle/working/out/rl_policy.zip`,
  `distilled_rl_deck_v1.npz`, `distilled_v1.npz`,
  `track_b_learned_rl_deck.tar.gz`, `checkpoint.json`,
  `track_b_learned_rl_deck_gate.md`, `eval_best-deck.json`, and run JSONs.
- **Files changed locally:** `report/training_registry.json`,
  `report/kaggle_notebook_jobs/current_status.md`, `PROGRESS.md`.
- **NEXT:** download `/kaggle/working/out`, import artifacts locally, inspect
  `track_b_learned_rl_deck_gate.md`, then decide whether to ladder-probe. No
  Kaggle upload without explicit user approval.

### 2026-06-19 (run 32 - Kaggle artifacts imported; gate PASS confirmed)
- **Imported downloaded Kaggle artifacts** into
  `report/kaggle_notebook_jobs/rl_deck/`: `rl_policy.zip`,
  `distilled_rl_deck_v1.npz`, `distilled_v1.npz`,
  `track_b_learned_rl_deck.tar.gz`, `checkpoint.json`,
  `track_b_learned_rl_deck_gate.md`, `eval_best-deck.json`, and run JSONs.
- **Gate PASS confirmed:** Learned **210/240 = 87.5%** vs pool; Search baseline
  **223/240 = 92.9%**; SPRT **accept_b**; dry-run import OK; deck selection returns
  60 card IDs. No Kaggle submission attempted.
- **Training proof:** checkpoint `status=ok`, `timesteps=100000`, `device=cuda`,
  `n_envs=4`, `opponents=benchmark`, `n_opponents=9`, holdout `a2_kyogre`.
  Eval @100k: train 13/20 = 65%, Kyogre holdout 12/20 = 60%.
- **Promoted local candidate copy:** 
  `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz`; gate copy at
  `report/track_b_gates/track_b_learned_rl_deck_kaggle_20260619_gate.md`.
- **NEXT (user decision):** upload
  `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` as the next
  Simulation ladder probe when a slot is available. Needs explicit user approval.

### 2026-06-19/20 (run 33 - Kaggle deep Track B completed; zip pending import)
- **Deep Kaggle run completed:** chunked `deep_track_b_cell.md` finished **8/8**
  chunks, **500k timesteps/chunk = 4M requested additional timesteps**, elapsed
  **134.4 min**, `device=cuda`, resumed from prior `rl_policy.zip`.
- **Artifacts on Kaggle:** `/kaggle/working/track_b_deep_outputs.zip` (5,450,193
  bytes), containing `track_b_learned_rl_deck_deep.tar.gz`,
  `track_b_learned_rl_deck_deep_gate.md`, `distilled_rl_deck_deep_v1.npz`,
  `rl_policy.zip`, `eval_best-deck.json`, run JSONs, and checkpoint/progress.
- **Run proof:** `deep_track_b_progress.json` says `chunks_completed=8`,
  `chunks_total=8`, `total_requested_timesteps=4000000`; final checkpoint says
  `status=ok`, `timesteps=500000` (per final chunk), `device=cuda`,
  `opponents=benchmark`, holdout `a2_kyogre`.
- **NEXT:** download or Kaggle-commit `/kaggle/working/track_b_deep_outputs.zip`,
  import locally, inspect `track_b_learned_rl_deck_deep_gate.md`, then decide if
  deep package is better than the 100k gate-passed package. No upload without user OK.

---

### 2026-06-19 (run 29 — Track B GATE PASSED on fixed reward; package built, NOT submitted)
- **Ran full 100k pipeline (fixed reward + Kyogre holdout) → train→distill→gate→package.**
- **Gate PASSED:** Learned **198/240 = 82.5%** vs pool, Search 202/240 = 84.2%,
  SPRT **accept_b**. Reward fix took Learned from run-26's 57/240 (23.8%) to 82.5%.
- **Held-out generalization:** Kyogre (never trained on) ~50–60% across training,
  55% @100k — vs the heuristic's 37%. Train WR plateaued ~70–80%.
- **Package:** `dist/candidates/track_b_learned_rl_deck.tar.gz` (5.4 MiB), dry-run
  import OK (returns 60 card IDs). **No Kaggle upload** (per rules; needs user OK).
- **Promoted:** `distilled_rl_deck_v1.npz` → `distilled_v1.npz`.
- **Real-deck prep (parallel, in progress):** card data confirmed in
  `data/EN_Card_Data.csv` (2102 cards) — Dragapult ex=121, Mega Lucario ex=678,
  Mega Abomasnow ex=723, Iono=supporter. Need full 60-card lists for the 4 real
  decks (best source: episodes dataset or official starter decks).
- **NEXT (user decision):** (1) upload `track_b_learned_rl_deck.tar.gz` as a ladder
  probe when a Simulation slot frees (needs explicit OK), and/or (2) finish the 4
  real decks → re-train/gate vs real meta. Kyogre heuristic (633μ) stays Slot-2
  fallback until RL-deck Learned proves out on ladder μ.

### 2026-06-19 (run 28 — reward dialed in + validated; eval/holdout instrumentation; real assets found)
- **Fixed the reward (2 bugs), verified it works.** `cabt_env.py` shaping was
  (a) asymmetric — only credited our own move, never the opponent's between-turn
  damage — and (b) a terminal Φ term computed on the opponent's perspective
  (`yourIndex==1` at game end) that literally rewarded losing. New shaping is
  per-decision potential delta (our-perspective, telescoping) + ±1 terminal only.
  Same bad policy: mean reward **+9.3 → −2.06** (now correctly penalizes losing).
- **Validated end-to-end (40k smoke):** policy LEARNS — train WR **18%→67%**, and
  held-out **Kyogre 27%→60%** (generalizes, not memorizing). The matchup the
  heuristic loses (37%) the RL policy now wins held-out.
- **Instrumentation added:** `rl/eval_callback.py` (true-terminal-result win-rate
  during training, never reward sign) + Kyogre holdout (excluded from train AND
  gate; consistent generalization probe). `train_rl.py` gets `--holdout/--eval-*`.
- **Fixed teardown crash:** eval callback `close()` → `battle_finish()` on a
  finished battle native-crashed the engine (exit 116, blocked final save). Now
  drops refs instead; clean EXIT_CODE=0, model saves.
- **Real competition assets located (user-supplied):** official RL+MCTS sample
  (`data/kaggle_ref/...ipynb` — AlphaZero MCTS + Transformer using the engine's
  `search_begin/step/end` planning API; outcome-only value, no board shaping —
  confirms our fix direction). Episodes-index dataset: daily real-ladder episodes
  (~20GB/day, top avg score ~1327 vs our 633μ). Real deck field: Iono, Dragapult
  ex, Mega Abomasnow ex, Mega Lucario ex (our suite uses pool_* proxies — overfit
  risk). See [[real-competition-decks]], [[sim-rules-differences]].
- **Files:** `rl/cabt_env.py`, `rl/env_factory.py`, `rl/train_rl.py`,
  `rl/eval_callback.py` (new), `scripts/diag_{teacher,distill}.py` (new),
  `report/track_b_rl_deck_diagnosis.md` (new).
- **NEXT (user decision):** real run config — train the full 100k+ on (a) current
  proxy suite now that reward works, or (b) integrate the 4 real decks first to
  avoid overfitting. Then re-distill + gate. Reward+instrumentation are locked in.

### 2026-06-19 (run 27 — gate-failure root cause: reward misspecification)
- **Worked on:** Debugged why Track B Learned gate failed (23.8% vs 85.4% Search).
- **Diagnosis (real, measured):** the MaskablePPO **teacher itself wins only 18%
  (9/50)** vs benchmark. The student faithfully distilled a losing teacher.
- **Root cause:** reward shaping `0.01*board_value_delta` (`cabt_env.py:172`)
  dominates the ±1 terminal signal. Mean episode reward **+9.3 while losing 82%** —
  agent learned to hoard board value, not win. Reward misspecification.
- **Process note:** first pass mis-read teacher as 83% by classifying wins via
  reward sign; shaping makes loss returns positive. `/code-review` caught the bug;
  reading engine terminal `result` gives the true 18%. Diagnosis flipped from
  "distillation problem" to "training problem."
- **Files changed:** `scripts/diag_teacher.py` (new), `scripts/diag_distill.py`
  (new), `report/track_b_rl_deck_diagnosis.md` (new), this entry.
- **NEXT (user decision):** EITHER (a) rebalance reward (drop shaping to ~0.001 or
  scale terminal to ±10/30), retrain 200k+, re-run `diag_teacher` before distill;
  OR (b) skip Track B for this deck — SearchScorer already pilots `best_deck.csv`
  to **85.4%**; ship it as a Track A (Search) pilot. Recommend (b) for speed, (a)
  only if a Learned agent is specifically wanted.

### 2026-06-19 (run 26 — Phase 2 RL deck training: GATE FAILED)
- **Executed:** Full Track B pipeline on best_deck.csv (RL + distill + SPRT gate @40g).
- **Trained:** MaskablePPO 100k steps, 6 envs, 10 benchmark opponents, CUDA.
- **Distilled:** `distilled_rl_deck_v1.npz` (1592 decisions, 0.04 ms/move).
- **Gate result:** Learned **57/240 = 23.8%** vs pool; Search **205/240 = 85.4%**. 
  SPRT **accept_a** → **GATE FAILED**. Huge drop from heuristic's 87.1%.
- **Analysis:** RL deck architecture (optimized for rule-based pilot) doesn't distill well to 
  neural policy. Options: (a) retry with longer training (200k+ steps), (b) try different deck, 
  (c) fall back to Kyogre Learned (490 μ) or another high-performer.
- **NEXT DECISION:** User call on retry strategy or pivot to backup deck.
  ```
  git clone https://github.com/TomBombadyl/kaggle_pokemon.git
  cd kaggle_pokemon
  pip install -q gymnasium>=0.29 stable-baselines3>=2.3 sb3-contrib>=2.3
  python scripts/train_track_b_deck.py --deck report/rl_deck_campaign/best_deck.csv \
    --slug rl_deck --timesteps 100000 --n-envs 6 --opponents benchmark \
    --gate-games 40 --package --promote
  # Download distilled model + metrics from /kaggle/working/
  ```

---

### 2026-06-19 (run 25 — RL deck validated in-sandbox; Phase 2 training blocked by env)
- **Executed in sandbox (real):** RL deck win-rate gate. `best_deck.csv` legality PASS
  (`validate_deck.py`, engine `battle_start`). Win-rate vs 6 `pool_*` decks, rule-based pilot
  both sides, 40g/opp seats-swapped: **209/240 = 87.1%** (95% CI [82.2, 90.7]), 0 draws/unfinished.
  Confirms GA fitness 0.898 holds at scale. **Gate ≥60% → PASS.** Detail in
  `report/rl_deck_validation.md`.
- **Caveat:** pool is in-distribution (GA trained vs this exact suite). Vs high-performers only 54.2%
  and **loses to Kyogre 11–19 = 36.7%**. Ladder μ is truth.
- **Phase 2 training attempted in sandbox — BLOCKED (environment):**
  (1) No GPU here (`/dev/nvidia*` absent, no `nvidia-smi`) → CUDA impossible.
  (2) Commands hard-capped ~45s with no process persistence between calls (verified) → the 532 MB
  torch wheel can't finish installing in one call, and a multi-minute MaskablePPO 100k run can't be
  kept alive. Validated experimentally; not a config issue.
- **Files changed:** `report/rl_deck_validation.md` (new), this entry.
- **NEXT (must run on user's CUDA machine):**
  `python scripts/train_track_b_deck.py --deck report/rl_deck_campaign/best_deck.csv --slug rl_deck
  --timesteps 100000 --n-envs 6 --opponents benchmark --gate-games 40 --package --promote`
  Then SPRT-gate, and upload only with explicit approval. Also: upload Kyogre Learned tarball when a
  daily slot frees (cmd in `report/submission_pending_kyogre.md`). Keep Kyogre heuristic (633 μ) as
  Slot-2 fallback if RL-deck Learned doesn't beat it on ladder.

### 2026-06-19 (run 24 — deck RL resume crash fixed)
- **Fixed:** `NameError: Counter` on deck GA resume; batched benchmark eval (1 process
  pool per deck, ~0.4s/deck).
- **Verified:** `--resume` reaches gen 4+ with progress lines; policy skips cleanly.
- **NEXT:** `scripts\run_overnight_deck_rl.bat` — finish deck gens 4–19 (~70 min).

### 2026-06-19 (run 23 — Track B Kyogre pipeline + submit blocked)
- **Worked on:** Full Track B per-deck pipeline (train → distill → gate → package); Kaggle upload attempted.
- **Command:** `scripts/train_track_b_deck.py --deck a2_kyogre --timesteps 100k --n-envs 6 --gate-games 40 --package --promote`
- **Train:** MaskablePPO 100k steps, CUDA, vs 10 benchmark opponents; deck Kyogre.
- **Distill:** `distilled_kyogre_v1.npz` (1788 decisions, 0.01 ms/move); promoted → `distilled_v1.npz`.
- **Gate @40g/pool:** Learned **206/240**, Search 212/240, SPRT **accept_b**, **PASS**.
- **Package:** `dist/candidates/track_b_learned_kyogre.tar.gz` (5.4 MiB).
- **Submit:** **BLOCKED** — 5/5 daily Simulation uploads already used; API 400 after upload.
- **Pending:** `report/submission_pending_kyogre.md` — submit command for next quota window.
- **NEXT:** Upload Kyogre Learned tarball (1 slot); pin **Final 1**; `train_track_b_deck.py` Crustle/Dragapult for Final 2.

- **Stopped:** Deck RL campaign crashed gen 5 with `arena.py` job tuple bug (9 vs 11
  fields). Fixed on disk; `best_deck.csv` fitness **0.898** still valid.
- **Progress saved:** deck GA cycle 1 / gen 5 of 20; policy 100k steps on CUDA done.
- **Fixed:** `genome_from_dict` drops negative counts; GA resume re-repairs population.
- **NEXT:** `scripts\run_overnight_deck_rl.bat` (resume) to finish gens 5–19 + cycle 2.

### 2026-06-19 (run 21 — overnight campaign audit + resume fixes)
- **Worked on:** Verified live overnight run; fixed campaign cycle/resume bugs.
- **Live run:** `run_overnight_deck_rl.bat` active — CUDA policy ~1300 fps; deck GA cycle 2
  gen 2+; best fitness **0.823** (`mut_a2_kyogre_33_energy`).
- **Fixed:** Per-cycle policy timesteps (`policy_steps_by_cycle`); separate
  `policy_cycles_done` / `deck_cycles_done`; SB3 `num_timesteps` on resume; `--fresh` flag.
- **Note:** Legacy `cycles_done=1` had skipped deck cycle 0 early — current run still valid
  on cycle 1 deck GA; fixes apply on next resume/restart.
- **NEXT:** Let overnight finish; then validate `best_deck.csv`, gate, package probe.

### 2026-06-19 (run 20 — deck RL campaign setup + overnight launch)
- **Worked on:** Local RL pipeline for deck optimization vs benchmark meta pool.
- **Changed:** `rl/benchmark.py`, `rl/deck_genome.py`, `rl/train_deck_campaign.py`,
  `rl/cabt_env.py`, `agent_decks/benchmark/suite.json`, `scripts/run_overnight_deck_rl.bat`.
- **Approach:** MaskablePPO (GPU) vs 10-deck benchmark + genetic deck search; fitness =
  weighted win rate (meta pool = Worlds-field proxy).
- **Smoke:** GA 2 gen → fitness **0.898** (kyogre×big_basic crossover).
- **Running:** `scripts/run_overnight_deck_rl.bat` (full mode, 2 cycles).
- **NEXT:** `report/rl_deck_campaign/best_deck.csv`; gate + package when fitness plateaus.

### 2026-06-19 (run 20 — submission playbook)
- **Worked on:** Document Kaggle active-submission-limit + daily quota from live probes.
- **Changed:** `data/SUBMISSION_PLAYBOOK.md` (new), `META_NOTES.md`, `PROJECT_RULES.md`,
  `finals_strategy.md`, `submission_candidates_2026-06-19.md`, `CABT_API.md`,
  `scripts/track_ladder.py` docstring.
- **Key rule:** 5 uploads/day; only **latest 2** active for standings; “disabled” ≠ timeout;
  upload probes first, **best artifact last**.
- **NEXT:** Before next upload day, read playbook; re-submit Kyogre heuristic last if still best μ.

### 2026-06-19 (run 19 — 5/5 daily ladder slots live)
- **Worked on:** Handoff after full daily submit quota.
- **Ladder μ (latest sync):** Kyogre heuristic **633.0** (#53854707); Learned alakazam
  **490.4** (#53856584); Learned dragapult **468.9** (#53856590); TA1 Kyogre+Search **600.0**
  (#53856711); TA2 Abomasnow+Search **600.0** (#53856676 — validation baseline, μ settling).
- **Verification:** `python scripts/track_ladder.py` — 6 rows parsed, 4 appended.
- **Blockers:** none; daily quota spent.
- **NEXT:** `track_ladder.py --fetch-logs` for all refs; analyze logs; plan tomorrow probes
  (crustle/starmie Track B or gate_track_a @40g).

### 2026-06-19 (run 18 — Kyogre ladder review + TA2 submit)
- **Worked on:** Sync ladder/logs; decide Track A probe route after live Kyogre.
- **Kyogre #53854707:** μ **672.7 → 645.7 → 633.0** as ladder games accumulated; agent
  logs clean (no stderr, &lt;0.05s/move).
- **Decision:** **Skip TA1** (Kyogre+Search duplicate archetype); **submit TA2** Abomasnow+4e
  SearchScorer (different deck line, 87.5% local pool).
- **Submitted:** #**53856676** `track_a_probe_2.tar.gz` — PENDING.
- **Already today:** dragapult #53856590, alakazam #53856584 @ validation 600.
- **NEXT:** ~40 min → `track_ladder.py --fetch-logs`; compare TA2 μ vs Kyogre; optional
  **crustle** or **starmie** Track B for 5th slot (not TA1).

---

### 2026-06-19 (run 19 — deck RL campaign setup)
- **Worked on:** Overnight deck + policy RL pipeline with benchmark fitness.
- **Changed:** `rl/benchmark.py`, `rl/deck_genome.py`, `rl/train_deck_campaign.py`,
  `rl/cabt_env.py` (league opponents), `agent_decks/benchmark/suite.json`,
  `scripts/run_overnight_deck_rl.bat`.
- **Approach:** MaskablePPO vs meta benchmark (PFSP-style rotation) + genetic deck
  search; fitness = weighted win rate vs pool/worlds-proxy decks.
- **Smoke:** 2 GA generations → best fitness **0.898** hybrid kyogre×big_basic.
- **Running:** `scripts/run_overnight_deck_rl.bat` (full mode, 2 cycles).
- **NEXT:** Check `report/rl_deck_campaign/`; package best deck when fitness plateaus.

### 2026-06-19 (run 17b — Track A two ladder probes)
- **Worked on:** Multi-base deck grid; package two SearchScorer ladder probes.
- **Changed:** `scripts/deck_search.py`, `scripts/prepare_track_a_probes.py`,
  `report/submission_candidates_2026-06-19.md`.
- **Metrics:** Kyogre +2e **91.7%** vs pool; Abomasnow +4e **87.5%** @12g; verify random
  **46/50** and **47/50**.
- **Artifacts:** `dist/candidates/track_a_probe_{1,2}.tar.gz`, `report/track_a/ladder_probes.md`.
- **NEXT:** User OK → submit TA1 then TA2; fetch logs after each.

### 2026-06-19 (run 18 — Track B ladder probes alakazam + dragapult)
- **Worked on:** User-approved Simulation uploads (2 of 5 daily slots).
- **Submitted:** `track_b_learned_alakazam.tar.gz` ref **53856584** (PENDING);
  `track_b_learned_dragapult.tar.gz` ref **53856590** (PENDING).
- **Brain:** LearnedScorer + distilled_v1.npz; decks `pool_alakazam_dudunsparce`,
  `pool_dragapult`.
- **Ladder sync:** A2 Kyogre #53854707 now **645.7** μ (was 672.7 — more W/L played in).
- **NEXT:** ~40 min then `python scripts/track_ladder.py`; `--fetch-logs` when COMPLETE.

### 2026-06-19 (run 17 — Track B deck spread)
- **Worked on:** LearnedScorer benchmark + package 9 diverse deck candidates.
- **Changed:** `scripts/package_track_b_spread.py`, `report/track_b_deck_spread.md`;
  nine `dist/candidates/track_b_learned_*.tar.gz` (LearnedScorer wired).
- **Metrics:** vs pool @12g/opp — kyogre **59/72**, big_basic **58/72**, starmie **56/72**,
  dragapult **48/72**, crustle **45/72**; bellibolt **24/71** (learned weak on simple aggro).
- **Ladder plan:** Kyogre heuristic live (#53854707); probe meta decks (dragapult, crustle,
  alakazam) + high-performers without duplicating Kyogre archetype on ladder.
- **NEXT:** User OK → ladder-probe `track_b_learned_dragapult` then `crustle` / `alakazam`;
  `track_ladder.py --fetch-logs` after each.

### 2026-06-19 (run 16b — Track A search + deck gate)
- **Worked on:** Track A — fix SearchScorer regression, deck search, gate + package.
- **Changed:** `agent/search_policy.py`, `agent/agent.py` (`_best_attack_index` + current),
  `scripts/gate_track_a.py`, `scripts/package_submission.py` (`--scorer search`).
- **Metrics:** deck_search **85.4%** vs pool @8g; Track A gate Search **43/48** vs
  Heuristic **40/48**, SPRT **accept_b**, **PASS**.
- **Artifacts:** `dist/candidates/track_a_search.tar.gz`, `report/deck_search/best_deck.csv`.
- **NEXT:** `gate_track_a.py --games 40`; user OK → ladder probe Track A; fetch logs.

### 2026-06-19 (run 16 — RL distill export + Track B re-gate)
- **Worked on:** MaskablePPO teacher→student distillation; wired LearnedScorer to
  distilled weights; Track B gate at N=40.
- **Changed:** `scripts/distill_policy.py` (teacher rollout, CE student train,
  `rl_policy.zip` path fix), `agent/learned_policy.py` (default `distilled_v1.npz`),
  `scripts/gate_track_b.py` (distilled model path, `eval_scorer` deck_path fix).
- **Metrics:** distill **torch_distill** 1096 teacher decisions, 0.01 ms/move PASS;
  Track B gate **206/240** vs pool (Search **197/240**), SPRT **accept_b**, **PASS**;
  smoke **17/17**; package `dist/candidates/track_b_learned.tar.gz` (2749 KiB).
- **Verification:** `python scripts/distill_policy.py --episodes 100`; smoke 17/17;
  `python scripts/gate_track_b.py --games 40` — pass + package dry-run OK.
- **Blockers:** none; no Kaggle submit.
- **NEXT:** User-approved Track B upload (`track_b_learned.tar.gz`); optional ladder
  probe; retrain BC with full option traces if warm-start desired.

### 2026-06-19 (run 15 — agent log fetch)
- **Worked on:** Kaggle Simulation agent log download after submissions.
- **Changed:** `scripts/fetch_agent_logs.py`, `scripts/track_ladder.py` (`--fetch-logs`),
  `data/META_NOTES.md`.
- **Metrics:** ref 53854707 — 15 episode logs under `report/agent_logs/` (manifest.csv).
- **Verification:** `python scripts/fetch_agent_logs.py --ref 53854707` — 15 files;
  re-run downloaded 0 (dedupe OK). `80702777-1.json` matches user example.
- **Blockers:** none.
- **NEXT:** After future submits, run `python scripts/track_ladder.py --fetch-logs`
  (nightly not wired yet — manual post-submit step).

### 2026-06-19 (run 14b — RL training + ptcg-rl-trainer subagent)
- **Worked on:** User-approved RL pipeline; created `.cursor/agents/ptcg-rl-trainer.md`.
- **Changed:** Installed `torch 2.6.0+cu124`; fixed `rl/cabt_env.py`, `rl/train_rl.py`;
  restored `play_matchup`/`pool_decks` in `scripts/arena.py`.
- **Metrics:** traces 100/4 shards; BC 3104 samples; RL **50k ok**; Track B gate
  **102/120** vs pool (Search 58/120), **PASS**; distill bc_fallback 0.01 ms; smoke 17/17.
- **Artifacts:** `agent/models/rl_policy.pt`, `report/rl_train/checkpoint.json`,
  `dist/candidates/track_b_learned.tar.gz`.
- **Blockers:** RL→numpy distill shape mismatch; no Kaggle submit.
- **NEXT:** Fix RL weight export; `gate_track_b.py --games 40`.

### 2026-06-19 (run 14 — ladder μ interpretation, verified Kaggle sync)
- **Worked on:** Record verified Simulation ladder scoring learnings from first
  successful A2 Kyogre submit (#53854707).
- **Changed:** `report/ladder_history.csv` (+672.7 row), `report/submission_candidates_2026-06-19.md`
  (ladder notes), `.cursor/SESSION.md`, `data/META_NOTES.md`, `report/finals_strategy.md`.
- **Metrics:** A2 ref 53854707 — validation μ **600.0** (self-play gate, not field rank);
  after ~40 min matchmaking **670.3**; API sync **672.7**. Failed submit #53854588
  (__file__ bug). Top ladder ~1350; mid ~1100+.
- **Verification:** `python scripts/track_ladder.py` — 2 rows parsed, 0 appended
  (dedupe by ref+status; score change logged manually). Kaggle CLI publicScore=672.7.
- **Blockers:** none.
- **NEXT:** Continue SPRT gates / ladder probes; do not treat 600 μ as failure on upload.

### 2026-06-19 (run 13 — massive-jump plan, all 16 todos implemented)
- **Worked on:** Full massive-jump plan (Phase 0–5): meta pool, arena/SPRT, OptionScorer
  refactor, Track A search, Track B BC, RL env/league/distill, nightly orchestrator.
- **Changed:** Added/finished `scripts/validate_deck.py`, `arena.py`, `track_ladder.py`,
  `deck_search.py`, `collect_traces.py`, `train_bc.py`, `gate_track_a.py`,
  `gate_track_b.py`, `distill_policy.py`, `nightly.py`, `stats_utils.py`;
  `agent/evalfn.py`, `search_policy.py`, `features.py`, `learned_policy.py`;
  `rl/cabt_env.py`, `rl/league.py`, `rl/train_rl.py`; five `agent_decks/pool_*.csv`
  meta decks; `report/ladder_history.csv`, `report/nightly_checkpoint.json`,
  `report/finals_strategy.md`. Fixed `arena.py` scorer routing + init bug;
  `deck_search.py` imports for new validator API.
- **Metrics:** smoke **17/17**; all 11 `agent_decks/*.csv` PASS validate_deck +
  battle_start; arena pilot **8/10** vs pool (2 games/matchup smoke); deck_search
  best **0.917** vs pool (2 games/opp); current **2/2** vs pool_dragapult (2-game
  matrix). Track A/B SPRT gates **not passed** at smoke counts (expected).
- **Artifacts:** `agent/models/bc_v1.npz`, `distilled_v1.npz`, `rl_policy.pt`;
  `dist/candidates/nightly_probe.tar.gz`; traces in `data/traces/`.
- **Verification:** `python scripts/smoke_test.py` 17/17; `validate_deck.py` ALL PASS;
  `nightly.py --run-all` 16/16 steps; `package_submission.py --name nightly_probe` dry-run OK;
  `python -m rl.cabt_env` OK (after gymnasium install).
- **Blockers:** no Kaggle submit (user rule). SPRT gates need more games before ladder probes.
- **NEXT:** `python scripts/gate_track_a.py --games 40` then user-approved A4/A1 uploads;
  scale `collect_traces.py` + `train_bc.py`; re-run arena with `--games 20`.

### 2026-06-19 (run 13+ - nightly p0_validate)
- **Worked on:** massive-jump plan todo `p0-decks`
- **Changed:** nightly step `p0_validate` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_smoke)
- **Worked on:** massive-jump plan todo `p0-refactor`
- **Changed:** nightly step `p0_smoke` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_arena)
- **Worked on:** massive-jump plan todo `p0-arena`
- **Changed:** nightly step `p0_arena` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_ladder)
- **Worked on:** massive-jump plan todo `p0-ladder`
- **Changed:** nightly step `p0_ladder` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly a_deck_search)
- **Worked on:** massive-jump plan todo `a-deck`
- **Changed:** nightly step `a_deck_search` exit=1
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** Traceback (most recent call last):
  File "Z:\kaggle\pokemon\scripts\deck_search.py", line 17, in <module>
    from scripts.validate_deck import load_card_db, validate_deck_ids  # noqa: E402
    ^^^^^
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_validate)
- **Worked on:** massive-jump plan todo `p0-decks`
- **Changed:** nightly step `p0_validate` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_smoke)
- **Worked on:** massive-jump plan todo `p0-refactor`
- **Changed:** nightly step `p0_smoke` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_arena)
- **Worked on:** massive-jump plan todo `p0-arena`
- **Changed:** nightly step `p0_arena` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly p0_ladder)
- **Worked on:** massive-jump plan todo `p0-ladder`
- **Changed:** nightly step `p0_ladder` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly a_deck_search)
- **Worked on:** massive-jump plan todo `a-deck`
- **Changed:** nightly step `a_deck_search` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly a_gate)
- **Worked on:** massive-jump plan todo `a-gate`
- **Changed:** nightly step `a_gate` exit=1
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** wrote Z:\kaggle\pokemon\report\track_a_gate.md; gate passed=False
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly a_gate)
- **Worked on:** massive-jump plan todo `a-gate`
- **Changed:** nightly step `a_gate` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly b_traces)
- **Worked on:** massive-jump plan todo `b-traces`
- **Changed:** nightly step `b_traces` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly b_bc)
- **Worked on:** massive-jump plan todo `b-bc`
- **Changed:** nightly step `b_bc` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly b_bc_gate)
- **Worked on:** massive-jump plan todo `b-bc-gate`
- **Changed:** nightly step `b_bc_gate` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly rl_env_smoke)
- **Worked on:** massive-jump plan todo `rl-env`
- **Changed:** nightly step `rl_env_smoke` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly rl_train)
- **Worked on:** massive-jump plan todo `rl-train`
- **Changed:** nightly step `rl_train` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly rl_league)
- **Worked on:** massive-jump plan todo `rl-train`
- **Changed:** nightly step `rl_league` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly rl_distill)
- **Worked on:** massive-jump plan todo `rl-distill`
- **Changed:** nightly step `rl_distill` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly package_probe)
- **Worked on:** massive-jump plan todo `finals`
- **Changed:** nightly step `package_probe` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly eval_matrix_pool)
- **Worked on:** massive-jump plan todo `p0-arena`
- **Changed:** nightly step `eval_matrix_pool` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step

### 2026-06-19 (run 13+ - nightly finals_log)
- **Worked on:** massive-jump plan todo `finals`
- **Changed:** nightly step `finals_log` exit=0
- **Metrics:** see report/arena, report/track_*_gate.md
- **Blockers:** none
- **NEXT:** run `python scripts/nightly.py` for next step
## Template (copy for each run)

```
### YYYY-MM-DD (run)
- Worked on: T# ...
- Changed: ...
- Metrics: best win-rate = ?? % over ?? games
- Blockers: none | <describe>
- NEXT: <the single next action>
```

---

### 2026-06-19 (run 13 - massive jump plan Phase 0–5 foundation)
- **Worked on:** Full approved massive-jump plan (16 todos): Phase 0 foundation,
  Track A search/deck/gate, Track B features/traces/BC/gate, RL env/train/distill,
  nightly orchestrator, finals cadence doc.
- **Changed:**
  - `scripts/validate_deck.py` + 5 meta pool decks in `agent_decks/pool_*.csv`
  - `scripts/arena.py` (multiprocess round-robin, Wilson CI, Elo, SPRT helper via
    `scripts/stats_utils.py`); extended `scripts/eval_matrix.py` with `deck:` pool agents
  - `scripts/track_ladder.py` → `report/ladder_history.csv`
  - `agent/agent.py` pluggable `OptionScorer` / `HeuristicScorer`; `build_agent(scorer=...)`
  - Track A: `agent/evalfn.py`, `agent/search_policy.py`, `scripts/deck_search.py`,
    `scripts/gate_track_a.py` → `report/track_a_gate.md`
  - Track B: `agent/features.py`, `scripts/collect_traces.py`, `scripts/train_bc.py`,
    `agent/learned_policy.py`, `agent/models/bc_v1.npz`, `scripts/gate_track_b.py`
  - RL: `rl/cabt_env.py`, `rl/league.py`, `rl/train_ppo.py`, `scripts/distill_policy.py`
  - Automation: `scripts/nightly.py`; `report/finals_strategy.md`; training deps commented
    in `requirements.txt`
- **Metrics:** smoke 17/17; all 5 pool decks PASS validate+battle_start; arena smoke
  11/12 vs 3 pool decks; track_ladder fetched 2 Kaggle submissions (0 new rows — already logged).
- **Blockers:** none for local gates; Kaggle submit still requires explicit user approval.
- **NEXT:** run `scripts/gate_track_a.py` / `gate_track_b.py` with more games for SPRT;
  wire `SearchScorer` into packaged main when gate passes; continue T15 A4/A1 uploads.

### 2026-06-19 (run 12 - T15 first Kaggle Simulation upload)
- **Worked on:** T15 first Kaggle Simulation upload. Diagnosed and fixed packaging
  bug; resubmitted A2 Kyogre.
- **Changed:** `scripts/package_submission.py` — `main.py` no longer uses `__file__`
  (Kaggle exec omits it); deck phase uses sample `read_deck_csv()` pattern; tar
  packaging adds files only (removed duplicate entries); dry-run exec simulates
  Kaggle loader. Rebuilt `dist/candidates/a2_kyogre.tar.gz`. Updated
  `report/submission_candidates_2026-06-19.md` with submission log.
- **Submissions:**
  - #53854588 ERROR — `NameError: __file__ not defined` in packaged `main.py`
  - #53854707 **COMPLETE — score 600.0** (A2 Kyogre, expected μ start)
- **Metrics:** ladder score 600.0; local gate unchanged (963/1000).
- **Blockers:** none for A2 upload.
- **NEXT (T15):** user confirm, submit A4 then A1; rebuild remaining candidates
  with fixed packager before upload.

### 2026-06-19 (run 11 - T15 1000-game validation + audit)
- **Worked on:** T15 pre-submit validation. Rebuilt all five candidate archives,
  ran 1000-game packaged validation for A1/A2/A4, and generated Wilson CI audit.
  No Kaggle submission attempted (no explicit user upload confirmation).
- **Changed:** fetched sim engine via `scripts/fetch_sim_engine.py` (was missing
  locally); rebuilt `dist/candidates/*.tar.gz`; ran
  `scripts/audit_candidates.py` → `report/candidate_package_audit.md`; updated
  `report/submission_candidates_2026-06-19.md` with 1000-game table and revised
  submit order.
- **Metrics (packaged vs default Abomasnow deck, 1000 games, side-swapped):**
  A2 Kyogre **963/1000 = 96.30%** (Wilson 94.94–97.30); A4 big-basic
  **965/1000 = 96.50%** (Wilson 95.17–97.47); A1 current
  **952/1000 = 95.20%** (Wilson 93.69–96.36). All runs: 0 draws, 0 unfinished.
  Head-to-head matrix unchanged: A2 beats A1/A4 at 55/100 and 58/100.
- **Official check:** web search reconfirmed five submissions/day for Simulation
  category; direct Kaggle page fetch timed out — browser recheck still recommended
  immediately before upload.
- **Verification:** `python scripts/smoke_test.py` = 17/17 pass; all five
  candidate packages dry-run imported; audit script wrote clean archive table
  (no missing required files, no forbidden patterns).
- **NEXT (T15):** if user confirms upload, browser-recheck Kaggle rules, submit
  A2 → A4 → A1, record submission IDs/scores. Otherwise start T16 deck grid
  search over `agent_decks/` variants using `verify_archive.py`.

### 2026-06-19 (run 10 - packaged head-to-head validation)
- **Worked on:** strengthened pre-submit validation by testing packaged candidates
  against each other. No Kaggle submission attempted.
- **Changed:** added `scripts/verify_archive_matrix.py`, which imports packaged
  `main.py`/`deck.csv` from multiple candidate tarballs and runs side-swapped
  local cabt matches between the packaged artifacts. It writes CSV/Markdown under
  `report/eval/`. Updated `report/submission_candidates_2026-06-19.md` with the
  top-3 packaged head-to-head matrix.
- **Metrics:** `report/eval/archive_matrix_100_top3_candidates.md` compares A1,
  A2, and A4 over 100 games per ordered pair. A2 is currently the best first-slot
  candidate by combined evidence: packaged default-deck random gate 294/300 =
  98.0%, A2 vs A1 = 55/100, and A2 vs A4 = 58/100. A1 remains the best
  source-matrix/safety-regression candidate; A4 remains the diversity probe.
- **Official check:** in-app browser was unavailable in this session, so the
  current official check remained web-search snippets plus local downloaded API
  artifacts. Do not upload until a browser-visible Kaggle rules check is possible.
- **Verification:** `python -m py_compile scripts\verify_archive_matrix.py`
  passed; the packaged matrix completed with no draws or unfinished games.
- **NEXT (T15):** if the user explicitly confirms upload, perform a browser-visible
  Kaggle final rules/slot check, submit A2 first, then A1/A4 as remaining planned
  probes, recording submission IDs and scores.

### 2026-06-19 (run 9 - packaged artifact validation)
- **Worked on:** validating that the local candidate tarballs themselves behave like
  the source runs, not just that the source agent works. No Kaggle submission
  attempted.
- **Changed:** added `scripts/verify_archive.py`, which extracts a candidate
  `.tar.gz`, imports the packaged top-level `main.py`, uses packaged `deck.csv`,
  and runs side-swapped games against legal random. It supports `--opponent-deck`
  to distinguish mirror checks from cross-deck checks. Updated
  `report/submission_candidates_2026-06-19.md` with package-level evidence and
  current official Kaggle links/snippets.
- **Official constraints rechecked:** current Kaggle search snippets for the
  Simulation rules still show five submissions/day and two final submissions; the
  Simulation overview snippet still says `.tar.gz` with top-level `main.py` and
  `deck.csv`. API contract remains grounded in `data/CABT_API.md` and downloaded
  `data/sim/sample_submission/cg/api.py`.
- **Packaged artifact metrics vs default Abomasnow random deck (300 games each):**
  A0 safety 282/300 = 94.0%; A1 current 288/300 = 96.0%; A2 Kyogre 294/300 =
  98.0%; A3 Starmie 283/300 = 94.3%; A4 big-basic 291/300 = 97.0%. Mirror archive
  checks also passed for A1/A3/A4, with A1 at 287/300, A3 at 291/300, and A4 at
  294/300.
- **Verification:** `python -m py_compile scripts\verify_archive.py` passed; all
  package verification runs finished with no draws or unfinished games.
- **NEXT (T15):** if the user explicitly says to submit, use a browser-visible
  Kaggle final rules check, then submit A2/A1/A4 in that order unless the user
  chooses a different portfolio. Record submission IDs/scores in
  `report/submission_candidates_2026-06-19.md`.

### 2026-06-19 (run 8 - T15 five dry-run candidates)
- **Worked on:** T15 five distinct Simulation submission candidates. No Kaggle
  submission attempted.
- **Changed:** extended `scripts/package_submission.py` with `--deck`,
  `--agent-module`, and `--name`, and isolated per-archive build directories so
  candidate packages do not clobber each other. Added
  `report/submission_candidates_2026-06-19.md` with the five-slot portfolio and
  updated `report/research_and_submission_plan.md` from the stale 88.7% state to
  the current 96.3% local gate. Added/kept deck probes under `agent_decks/`.
- **Candidate archives:** dry-run built and import/deck-selection checked:
  `dist/candidates/a0_safety.tar.gz`,
  `dist/candidates/a1_current_963.tar.gz`,
  `dist/candidates/a2_kyogre.tar.gz`,
  `dist/candidates/a3_starmie.tar.gz`, and
  `dist/candidates/a4_big_basic.tar.gz`.
- **Metrics:** A1 is the recommended first slot if the user confirms submission:
  `matrix_300_current_pref_first` measured 578/600 = 96.3% vs legal random, and
  `matrix_120_current_pref_first_matrix` measured current beating safety 152/240
  across ordered rows. A4 had a promising 120-game gate but did not hold 95% on a
  300-game rerun; A2/A3 are diversity probes, not local-best candidates.
- **Verification:** `python scripts\smoke_test.py` = 17/17 pass;
  `python -m py_compile agent\agent.py agent_snapshots\v2_safety.py
  scripts\eval_matrix.py scripts\smoke_test.py scripts\selfplay.py
  scripts\package_submission.py` passed; all five candidate packages dry-run
  imported and returned 60-card decks. Official rules still require browser-visible
  recheck immediately before any upload.
- **NEXT (T15):** if the user explicitly confirms, open the Kaggle pages in browser
  for final rules/slot check, submit A1 first, and record submission ID/score.
  Otherwise continue reducing `no_active` losses and/or prepare a stronger A4
  anti-ex/basic candidate.

### 2026-06-19 (run 7 - T15 local 95% gate reached)
- **Worked on:** continued T15 toward a validated 95%+ local candidate while
  re-checking official/API constraints. No Kaggle submission attempted.
- **Changed:** kept the A1 current agent path and added two practical improvements:
  MAIN `PLAY` now scores playable cards and prioritizes benching Basic Pokémon
  when the bench is thin, and `IS_FIRST` now chooses to go first because current
  telemetry showed the upgraded pilot performs better from first-player tempo.
  Added role scoring for additional Water candidates (Black Kyurem ex, Veluza,
  Chien-Pao, Staryu/Mega Starmie ex) and smoke coverage for benching Basics before
  draw support. `scripts/eval_matrix.py` now supports `--tag` so candidate evidence
  is no longer overwritten by repeated `matrix_<games>` runs.
- **Deck probes added:** `agent_decks/a2_kyogre_33_energy.csv`,
  `agent_decks/a2_basic_heavy_31_energy.csv`,
  `agent_decks/a2_big_basic_31_energy.csv`,
  `agent_decks/a2_big_basic_29_energy.csv`,
  `agent_decks/a3_starmie_spread_33_energy.csv`, and
  `agent_decks/a4_basic_water_33_energy.csv`. These are test candidates only;
  `agent/deck.csv` remains the current submission deck.
- **Metrics:** best verified local random gate is now
  `report/eval/matrix_300_current_pref_first.*`: current vs random 289/300 and
  reciprocal random vs current 11/300, so current won **578/600 = 96.3%** over
  600 agent-perspective games, sides swapped. Broader tagged matrix
  `report/eval/matrix_120_current_pref_first_matrix.*`: current beat safety
  75/120 and reciprocal safety vs current 43/120, and beat random 235/240 across
  both ordered rows. Remaining losses in the 300-game telemetry are still
  `no_active` (22 losses), not deck-out.
- **Verification:** `python scripts\smoke_test.py` = 17/17 pass;
  `python -m py_compile agent\agent.py agent_snapshots\v2_safety.py
  scripts\eval_matrix.py scripts\smoke_test.py scripts\selfplay.py
  scripts\package_submission.py` passed; `python scripts\package_submission.py`
  built `dist/submission.tar.gz` and dry-run import/deck selection succeeded.
  Official Kaggle Simulation/Strategy rules pages were reopened on 2026-06-19 but
  returned only JavaScript page shells in the fetch; implementation/API grounding
  remains `data/CABT_API.md` plus downloaded `data/sim/sample_submission/cg/api.py`.
- **Blockers / notes:** the local 95% random benchmark is achieved, but the full
  goal is not complete: ladder/submission performance is still unproven and needs
  explicit user confirmation before any Kaggle upload. Pre-submit still requires a
  browser-visible official page check for current limits/rules.
- **NEXT (T15):** create a named submission candidate snapshot/package for the
  current 96.3% agent, then, only with explicit user confirmation, submit one
  Simulation slot and record ladder ID/score; otherwise continue reducing
  `no_active` losses and testing candidate diversity.

### 2026-06-19 (run 6 - T15 A1 initial candidate)
- **Worked on:** T15 first Simulation candidates, specifically A1
  attack/targeting upgrade. No Kaggle submission attempted.
- **Changed:** updated `agent/agent.py` only for the live agent path; preserved
  `agent_snapshots/v2_safety.py` unchanged. The current agent now lazily reads cabt
  attack/card metadata when available, scores attack choices by fixed damage and
  active-KO pressure, promotes developed attackers after KO, scores heal targets by
  damage/value, and targets opponent damaged/low-HP/high-prize Pokémon for damage
  counters/damage effects. Added smoke coverage for active promotion and opponent
  KO targeting.
- **Metrics:** requested matrix
  `python scripts\eval_matrix.py --games 20 --agents current,safety,random --deck
  current=agent\deck.csv` completed. Current/A1 aggregate in telemetry: 60 wins /
  20 losses over 80 agent-perspective rows (75.0%); safety aggregate: 53 wins / 27
  losses (66.2%). Ordered rows: current vs safety 12/20, current vs random 20/20,
  safety vs current 10/20, random vs current 2/20.
- **Verification:** `python scripts\smoke_test.py` = 16/16 pass;
  `python -m py_compile agent\agent.py agent_snapshots\v2_safety.py
  scripts\eval_matrix.py scripts\smoke_test.py scripts\selfplay.py
  scripts\package_submission.py` passed; requested 20-game matrix passed and wrote
  `report/eval/matrix_20.*` plus `report/eval/telemetry_20.*`.
- **Blockers / notes:** A1 is promising but not final; current losses in the
  telemetry are still all `no_active`, so the next candidate work should test more
  robust basic/bench/deck variants before any submission.
- **NEXT (T15):** build A2 reduced-energy Water deck candidate, then compare A0/A1/A2
  on the matrix before deciding whether A1 merits packaging as a Simulation slot.

### 2026-06-19 (run 5 - T14 telemetry)
- **Worked on:** T14 game telemetry for the local evaluation matrix.
- **Changed:** expanded `scripts/eval_matrix.py` with per-game telemetry collection
  and reporting. Normal matrix CSV/Markdown output is unchanged; telemetry is on by
  default and can be skipped with `--no-telemetry`. New outputs:
  `report/eval/telemetry_<games>.csv` (one row per agent perspective per game) and
  `report/eval/telemetry_<games>.md` (aggregate diagnosis by agent, first/second,
  loss reason, decision contexts in losses, and attacker usage).
- **Telemetry fields:** matchup, agent/opponent, actual seat, first/second order,
  result, cabt result reason (`prize`, `deck_out`, `no_active`, `card_effect`),
  turns/steps, prize/deck counts, first attack/evolution turns, evolution count,
  attachment opportunity/attachment/missed-attachment turns, last/top attackers,
  decision context counts, and decision type counts.
- **Metrics:** no new best win-rate claim. Small smoke matrix
  `python scripts\eval_matrix.py --games 4 --agents current,safety,random --deck
  current=agent\deck.csv` completed and wrote `matrix_4.*` plus `telemetry_4.*`.
- **Verification:** `python scripts\smoke_test.py` = 14/14 pass;
  `python -m py_compile agent\agent.py agent_snapshots\v2_safety.py
  scripts\eval_matrix.py scripts\smoke_test.py scripts\selfplay.py
  scripts\package_submission.py` passed; `python scripts\eval_matrix.py --games 2
  --agents current,random --no-telemetry` passed.
- **Blockers:** none for local telemetry. Actual Kaggle submission remains
  intentionally unattempted pending explicit user confirmation and fresh official
  page verification immediately before upload.
- **NEXT (T15):** use the matrix + telemetry reports to build the first five
  Simulation submission candidates: A0 safety baseline, A1 attack/targeting
  upgrade, A2 reduced-energy Water list, A3 Water spread variant, and A4
  anti-ex/single-prize variant.

### 2026-06-19 (run 4 - research roadmap + v2 snapshot + eval matrix)
- **Worked on:** T12 planning checkpoint after the user requested a saved progress
  handoff, deeper academically backed research directions, and preparation for the
  first five Simulation agent submissions.
- **Changed:** added `report/research_and_submission_plan.md` with the current
  baseline, official submission constraints to recheck, untried evaluation/agent/deck
  ideas, research-backed directions (heuristic search, offline imitation/RL,
  PPO/self-play caution, exploitability), and five proposed Simulation submission
  candidates. Updated `report/strategy_report_draft.md` to use the latest 88.7%
  local metric. Expanded `TASKS.md` with Phase 4 tasks T13-T17.
- **T12/T13 DONE:** froze the current v2 safety agent as
  `agent_snapshots/v2_safety.py` and added `scripts/eval_matrix.py`, which compares
  local agents/decks with side swapping and writes CSV/Markdown summaries under
  `report/eval/`. It supports named agents `current`, `safety`, and `random`, plus
  deck overrides such as `--deck current=agent\deck.csv`.
- **Research notes:** current-web snippets from official Kaggle pages indicate the
  Simulation competition allows five submissions per day and up to two final
  submissions, and uses a `submission.tar.gz` upload. Academic sources reviewed:
  RLCard for imperfect-information card-game RL tooling, Metamon/Pokemon offline
  RL for first-person trajectory reconstruction and offline fine-tuning, Hearthstone
  MCTS for heuristic-enhanced search under hidden information, and LOCM/ByteRL work
  for CCG RL/exploitability lessons. These support building telemetry and a local
  match matrix before heavy RL.
- **Metrics:** best win-rate remains **88.7% over 300 games** heuristic-vs-random
  (sides swapped). New harness smoke results: `python scripts\eval_matrix.py
  --games 20` and `python scripts\eval_matrix.py --games 6 --agents
  current,safety,random --deck current=agent\deck.csv` both completed and wrote
  reports in `report/eval/`.
- **Verification:** `python scripts\smoke_test.py` = 14/14 pass;
  `python -m py_compile agent\agent.py agent_snapshots\v2_safety.py
  scripts\eval_matrix.py scripts\smoke_test.py scripts\selfplay.py` passed.
- **Blockers:** no local blocker. Actual Kaggle submission remains intentionally
  unattempted pending explicit user confirmation and one more official Kaggle-page
  verification immediately before upload.
- **NEXT (T14):** add telemetry to `scripts/eval_matrix.py`/the self-play path so
  each matchup explains wins and losses by first/second, turns, prize/deck-out
  reason, active attacker, evolution timing, missed attachments, and decision
  context counts.

### 2026-06-19 (run 3 - T9/T10/T11 complete, package dry-run OK)
- **Worked on:** T9, T10, and T11. Kaggle pages were allowed by the user, but this
  pass did not need browser traversal because the local downloaded official
  `sample_submission/` and cabt engine artifacts were sufficient for the work.
- **T9 DONE:** kept a card-context scoring improvement in `agent/agent.py`:
  optional `TO_HAND` and `ATTACH_TO` selections now take useful visible cards/energy
  instead of declining when `minCount=0`; visible cards are ranked by current Water
  Mega Abomasnow deck roles; required discard/deck-bottom choices prefer lower-value
  cards first. Added smoke coverage in `scripts/smoke_test.py`.
- **Metrics:** current best win-rate = **88.7% over 300 games** heuristic-vs-random
  (sides swapped). Same run random-vs-random = 47.3%. Earlier same-code run measured
  86.3% over 300, both above the previous 78.0% best.
- **T10 DONE:** drafted `report/strategy_report_draft.md` covering verified agent
  interface, deck concept, rule logic, stability tests, local metrics, limitations,
  and next improvements.
- **T11 DONE:** added `scripts/package_submission.py`; built
  `dist/submission.tar.gz` locally; dry-run import returned 60 deck IDs; an unpacked
  archive completed one full cabt game locally. No Kaggle submission was attempted.
- **Verification:** `python scripts\smoke_test.py` = 14/14 pass;
  `python -m py_compile agent\agent.py scripts\smoke_test.py scripts\selfplay.py`
  passed; `python scripts\package_submission.py` passed; archive full-game smoke
  passed (`result=0`, 23 steps in the final run).
- **Blockers:** none for local work. Actual Kaggle submission remains intentionally
  unattempted pending explicit user confirmation and official Kaggle-page validation.
- **NEXT (T12):** before any real submit, use the browser/Kaggle pages to reconfirm
  current Strategy/Simulation submission requirements and limits, then polish
  `report/strategy_report_draft.md` and decide with the user whether to submit
  `dist/submission.tar.gz` or revise further.

### 2026-06-19 (run 2 - T7/T8 strategy v1 complete)
- **Worked on:** saved durable project operating rules, T7, and T8.
- **Changed:** added `PROJECT_RULES.md` with the project operating contract (manual
  run model; no scheduling assumptions); linked it from `README.md`.
- **T7 DONE:** rewrote `agent/agent.py` from attack-first v0 into setup-aware v1:
  MAIN priority is now evolve/play/attach/ability/attack; optional setup bench
  selections fill legal slots instead of declining; draw-count prompts choose the
  largest available number; common yes/no prompts prefer going second, mulligan
  redraws, and useful effect activation; attack and attach choices now use stable
  scoring helpers instead of first-option fallback.
- **T8 DONE:** mirrored `data/sim/sample_submission/deck.csv` to `agent/deck.csv`
  so deck-selection mode returns the intended 60-card list. Recorded the current
  Water Mega Abomasnow concept in `report/deck_concept_v1.md`.
- **Verification:** `python scripts\smoke_test.py` = 12/12 pass;
  `python -m py_compile agent\agent.py scripts\smoke_test.py scripts\selfplay.py`
  passed; `agent/deck.csv` loads 60 IDs.
- **Metrics:** current best win-rate = **78.0% over 200 games** heuristic-vs-random
  (sides swapped). Sanity matchup in same run: random-vs-random = 45.0% over 200.
  Previous best was 7.5% over 160, so v1 is a major local-harness improvement.
- **T9 attempt not kept:** tried a lazy `cg.api.all_attack()` damage/KO scorer for
  attacks. It measured **75.7% over 300 games**, below the 78.0% best, so the
  change was reverted. A post-revert 200-game check measured 77.0%, consistent
  with the kept v1 range.
- **Blockers / notes:** `bash scripts/setup_env.sh` was attempted first, but Windows
  pip rejected `--break-system-packages`; fallback `python -m pip install -r
  requirements.txt` succeeded on Python 3.13.12. No Kaggle submission attempted.
- **NEXT (T9):** add card-data-aware CARD/DISCARD/TO_HAND scoring (keep evolution
  pieces and draw/search supporters, discard excess Energy first), then rerun
  `python scripts\selfplay.py 300` and keep the change only if it beats 78.0%.

### 2026-06-19 (run 1d — ENGINE running, T4 + T5 done, first win-rates)
- **cabt engine fetched.** User joined the **Simulation** comp; added
  `scripts/fetch_sim_engine.{py,bat}` → downloaded its `sample_submission/` into
  `data/sim/`: starter `main.py`, a sample `deck.csv` (60 ids), and the engine
  `cg/` (`libcg.so` Linux + `cg.dll` Windows, `api/game/sim/utils.py`).
- **Engine RUNS IN THE SANDBOX (Python 3.10).** `cg/sim.py` is a ctypes wrapper that
  auto-loads `libcg.so` on Linux / `cg.dll` on Windows. So the **Python ≥3.11
  blocker is moot** for direct play — only `kaggle_environments` needs 3.11, which we
  bypass by calling `cg.game.battle_start/battle_select` directly.
- **T4 DONE.** `scripts/selfplay.py` plays full games to completion (game ends when
  `current.result != -1`; 0/1 = winner, 2 = draw). One game ≈ 50 decisions / ~14 turns.
- **T5 DONE — first measured win-rates (160 games/matchup, sides swapped, ~4s):**
  - random vs random = **48.1%** → harness is fair (sanity check passes).
  - **heuristic v0 vs random = 7.5%** → our naive "attack-first + first-option
    fallback" policy is **much worse than random**. Key insight: greedy attacking
    without board setup, and picking the first option for targeting/discards, plays
    badly. This is the concrete signal to drive T7.
- **Real interface confirmed from starter `main.py`:** `agent(obs_dict)` →
  `to_observation_class`; `obs.select is None` ⇒ return 60-card deck; else return
  indices in `[minCount,maxCount]`. Matches `agent/agent.py`.
- **Engine kept out of git** (`data/*` gitignored except `*.md`); reproducible via the
  fetch script. Card-supertype/energy enums confirmed in `cg/api.py`.
- **NEXT (T7):** Beat the random baseline. Replace the rigid MAIN priority with
  setup-aware logic: in the early game attach energy + develop bench/evolve before
  attacking; only attack when it KOs or trades up; for CARD/DISCARD/target contexts
  score options instead of taking the first. Re-run `python3 scripts/selfplay.py 200`
  and keep the change only if heuristic-vs-random clears ~50%+.

### 2026-06-19 (run 1c — data unblocked, T3 done)
- **Kaggle access fixed.** User signed in to Kaggle in the browser → competition
  data unlocked (rules gate cleared). Token auth path confirmed: the new `KGAT_`
  token works via `kagglehub` (the legacy `kaggle` CLI 1.6/1.7 does NOT read it).
- **Data downloaded** (sandbox can't reach kaggle.com, so fetched on the user's
  machine): added `scripts/fetch_card_data.py` + `fetch_card_data.bat` — reads the
  token from `.kaggle/access_token`, pulls the Strategy dataset via kagglehub, and
  copies the CSVs into `data/`. Now present: `data/EN_Card_Data.csv` (359 kB),
  `data/JP_Card_Data.csv`. (Big PDFs left in kagglehub cache to keep the repo lean.)
- **T3 DONE.** `scripts/summarize_cards.py` → `data/CARDS_SUMMARY.md`.
  **2,022 cards, 17 cols.** Supertype: 958 Basic / 618 Stage 1 / 229 Stage 2
  Pokémon; 82 Item, 61 Supporter, 28 Tool, 26 Stadium, 12 Special / 8 Basic Energy.
  HP min 30 / median 110 / max 380. Retreat 1:859 2:554 3:265 4:70. 324 cards have
  a Rule box (ex etc.). Note: real schema is **17 columns** (the Data-tab prose
  listing 34 fields was descriptive, not literal); "Category" holds mechanics
  (Ancient/Future/Tera/Trainer's Pokémon), supertype is in the Stage/Type column.
- **Still blocked for T4/T5:** the **cabt engine** is NOT in the Strategy dataset —
  it ships via the **Simulation** comp (`pokemon-tcg-ai-battle`) + starter
  notebooks. And the ladder harness `kaggle-environments==1.30.1` needs Python
  ≥3.11 (sandbox is 3.10; user's machine has 3.11/3.13 + Anaconda).
- **NEXT:** Get the engine: Join the **Simulation** competition, then fetch its
  code/engine (`cg/` lib) the same way (extend `fetch_card_data.py` or download a
  starter notebook's engine) into `data/cabt/`. Then wire `agent/agent.py` to
  `kaggle_environments.make("cabt", ...)` on Python 3.11 → **T4** (run one full
  game) and **T5** (random-baseline win-rate).

### 2026-06-19 (run 1b — read competition docs closely via browser)
- **Data tab (official):** the **Strategy** dataset is **card data + PDFs only**
  (4 files, 320.74 MB): `EN_Card_Data.csv`, `JP_Card_Data.csv`,
  `Card_ID List_EN.pdf`, `Card_ID List_JP.pdf`. CSV = **34 columns**
  (Card ID, Card Name, Expansion, Collection No., Stage/Type, Rule, Category,
  Previous stage, HP, Type, Weakness, Resistance, Retreat, Move Name, Cost,
  Damage, Effect Explanation, ...). This is the T3 card DB.
- **The cabt simulator/engine is NOT in the Strategy dataset.** It ships via the
  **Simulation** competition (`pokemon-tcg-ai-battle`) + starter notebooks (e.g.
  "Pokémon TCG EDA & Deck Engine", "EDA Starter Kit"). Needed for T4/T5.
- **ACCESS GATE (root cause):** the Data tab says *"To see this data you need to
  agree to the competition rules… Sign In."* The browser is **NOT signed in** to
  Kaggle and the competition is **not yet joined** ("Join Hackathon"). Kaggle API
  tokens also return 403 until the account has **joined/accepted rules**. So the
  download needs: (1) sign in, (2) Join (accept rules) — both **user-only** actions.
- **Prep done this run:** `scripts/summarize_cards.py` written + syntax-checked —
  parses `EN_Card_Data.csv` (schema-tolerant) → `data/CARDS_SUMMARY.md`. Runs the
  instant the CSV lands. `uv`/apt py3.11 routes tried; GitHub-release + kaggle.com
  egress both 403 from sandbox, so download must happen on the user's machine.
- **NEXT:** User signs in to Kaggle + clicks **Join Hackathon** on BOTH the
  Strategy and Simulation comps; then either (a) I drive the browser to download
  the 4 data files, or (b) user runs `kaggle competitions download -c
  pokemon-tcg-ai-battle-challenge-strategy -p data/` on Windows. Then run
  `python scripts/summarize_cards.py` → completes **T3**.

### 2026-06-19 (run 1)
- **Worked on:** T1 (done), T2 (partial/blocked), T6 (done). T3-T5 blocked offline.
- **T1 — interfaces CONFIRMED from official cabt Engine 0.1.0 docs**
  (matsuoinstitute.github.io/cabt + /api.html). Full schema written to
  `data/CABT_API.md`. Key facts:
  - Agent contract: `def agent(obs_dict) -> list[int]` returning **indices** into
    `obs_dict["select"]["option"]`, count in `[minCount, maxCount]`.
  - Deck phase: `select`/`current` are `None` → return **60 card IDs** (not indices).
  - obs keys: `logs`, `current` (State|None), `select` (SelectData|None).
  - 11 SelectTypes, 17 OptionTypes, 49 SelectContexts, 12 AreaTypes — all tabulated.
  - Engine API: `battle_start/select/finish`, `all_card_data()` (~2,000 cards),
    `all_attack()`, lookahead `search_begin/step/end`.
  - Harness: `make("cabt", configuration={"decks":[d,d]})`; ladder uses
    `kaggle-environments==1.30.1`.
  - Rewrote `agent/agent.py` to this real interface: legal/deterministic baseline
    with MAIN priority (attack>evolve>attach>ability>play>retreat>end) + a
    never-crash `_legal_fallback`. Added `scripts/smoke_test.py` → **10/10 pass**.
- **T2 — env partially configured.**
  - Deps install OK (numpy 2.2.6, pandas 2.3.3, kaggle 1.7.4.5, kagglehub 1.0.2).
  - **Kaggle token RECEIVED** (new `KGAT_` format) and stored at
    `.kaggle/access_token` (gitignored). `setup_env.sh` updated to use it.
  - **[BLOCKED] data download:** sandbox proxy returns **403 Forbidden** for
    `api.kaggle.com` AND `www.kag
