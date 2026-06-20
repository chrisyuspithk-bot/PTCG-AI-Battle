# Session state — PTCG AI Battle Challenge

## Current focus

**Goal:** Climb ladder μ toward leaders (1252+); keep **53869254** (660.5 μ) as Final until beaten.
**53890064** Alakazam probe settled at **512.1 μ** (below Lucario — do not pin). **5/5 uploads
used 2026-06-20**; Trevenant packaged locally for tomorrow. **Lucario RL iter4/5** checkpoints
staged at `kaggle_download_iter45_20260620/` (`model_best.pth` = iter5). **Lucario v2** passes
expanded leader-suite gate **69.6%** locally but no slot today. **Next:** `import_lucario_rl_outputs`
on iter5 + L1 gate; `analyze_submission.py --ref 53890064`; pin Finals (**53869254**).

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main` (ahead 3, dirty post-`f14455b`)
- **Limits:** **5/5 uploads used 2026-06-20** — [`data/SUBMISSION_PLAYBOOK.md`](data/SUBMISSION_PLAYBOOK.md)
- **Best ladder μ:** **53869254** Search Lucario **660.5** — Final 1 — [`report/FINALS_PIN.md`](report/FINALS_PIN.md)
- **53890064** Alakazam + SearchScorer — **512.1 μ** (COMPLETE; below 69254)
- **Not uploaded:** `track_a_trevenant_leader_search.tar.gz` (quota full)
- **Lucario v2 gate:** 313/450 = **69.6%** expanded suite — [`report/LUCARIO_V2_GATE.md`](report/LUCARIO_V2_GATE.md); weak vs Trevenant (~40–47%)
- **RL checkpoints:** [`report/kaggle_notebook_jobs/lucario/kaggle_download_iter45_20260620/`](report/kaggle_notebook_jobs/lucario/kaggle_download_iter45_20260620/) — iter4/5 + `model_best.pth` (iter5)
- **RL upload blocked:** L1 must beat Search Lucario before Kaggle — [`report/handoffs/lucario_rl_reimport_status.md`](report/handoffs/lucario_rl_reimport_status.md)
- **Leader intel:** [`report/top_performer_reverse_engineering_20260620.md`](report/top_performer_reverse_engineering_20260620.md)
- **Analyze tooling:** per-episode seat fix — [`scripts/analyze_submission.py`](scripts/analyze_submission.py)
- **GPU:** `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe` (cu128)
- **Upload policy:** explicit user OK required; no slots until next day

## Continue prompt

```text
Continue ladder + Lucario RL packaging. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @data/SUBMISSION_PLAYBOOK.md, @report/LUCARIO_V2_GATE.md, @scripts/import_lucario_rl_outputs.py

Goal: Package iter5 RL locally and gate; track 53890064 episodes; keep 53869254 as Final until beaten.
Status: Alakazam 53890064 @512.1 μ; iter4/5 in kaggle_download_iter45_20260620; v2 lucario_search 69.6% local; 5/5 uploads used.
Next: python scripts/import_lucario_rl_outputs.py --source report/kaggle_notebook_jobs/lucario/kaggle_download_iter45_20260620 --name track_d_lucario_rl_mcts_iter5 --gate-games 12

Branch: main (ahead 3, dirty) | Env: Python313 cu128 | No upload without user OK
```

## Timeline

- **2026-06-20T17:05:00Z** | handoff by user | conv `lucario-top-performer-v1`
- **2026-06-20T20:30:00Z** | handoff by user | conv `lucario-hybrid-v2`
- **2026-06-20 EOD** | LucarioSearchScorer impl + partial L1; deck-out insight; strategy doc refresh
- **2026-06-20 EOD** | Alakazam 1M retired; Lucario iter3 assessed; repo cleanup
- **2026-06-20** | SmartBench + meta tactics; ref 53886522 submitted
- **2026-06-20** | Top-performer Kaggle CLI analysis — refs 53802029–53800247
- **2026-06-20T17:35:00Z** | handoff by user | conv `high-mu-submission-plan`
- **2026-06-20T18:00:00Z** | handoff by user | conv `alakazam-upload-iter45-rl`
- **2026-06-20T18:45:00Z** | handoff by user | conv `iter45-staged-handoff`
