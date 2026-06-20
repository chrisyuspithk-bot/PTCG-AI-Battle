# Session state — PTCG AI Battle Challenge

## Current focus

**Goal:** Chase leader μ (1252+) via ladder probes + Lucario RL; keep **53869254** (660.5 μ) as Final
until beaten. **53890064** Alakazam leader probe is **COMPLETE @ 600.0** (validation baseline —
re-check μ after ~40+ min ladder games). **Daily quota 5/5 used** (Trevenant packaged locally,
not uploaded). Kaggle Lucario RL notebook running **iter 6**; user has **`model_iter4.pth`** +
**`model_iter5.pth`** (both promoted per notebook) — import when idle, **do not submit RL until
L1 beats Search Lucario**. **Next:** `analyze_submission.py --ref 53890064`; import iter4/5 when
training pauses; pin Finals manually.

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main` (ahead 2, dirty → commit pending)
- **Limits:** **5/5 uploads used 2026-06-20** — [`data/SUBMISSION_PLAYBOOK.md`](data/SUBMISSION_PLAYBOOK.md)
- **Best ladder μ:** **53869254** Search Lucario **660.5** — keep Final 1 — [`report/FINALS_PIN.md`](report/FINALS_PIN.md)
- **New upload:** **53890064** Alakazam + SearchScorer + `top_mined_alakazam.csv` — COMPLETE **600.0**
- **Not uploaded:** `track_a_trevenant_leader_search.tar.gz` (400 on retry; quota full)
- **Do not submit:** v2 hybrid (8.3% L1); Alakazam @600 ≠ beat Lucario yet
- **Lucario RL (Kaggle GPU):** iter **6** self-play; promoted iters **0,2,4,5** — import iter4/5 next
- **Prior RL:** iter2 champion only validated locally — [`report/kaggle_notebook_jobs/lucario/iter3_import_assessment_20260620.md`](report/kaggle_notebook_jobs/lucario/iter3_import_assessment_20260620.md)
- **Leader mining:** [`report/top_performer_reverse_engineering_20260620.md`](report/top_performer_reverse_engineering_20260620.md)
- **Analyze fix:** per-episode `agent_index` — [`scripts/analyze_submission.py`](scripts/analyze_submission.py)
- **GPU box:** `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe` (cu128)
- **User away:** notebook may keep training; import checkpoints when downloads land

## Continue prompt

```text
Continue ladder + Lucario RL import. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @data/SUBMISSION_PLAYBOOK.md, @report/kaggle_notebook_jobs/lucario/iter3_import_assessment_20260620.md, @scripts/import_lucario_rl_outputs.py

Goal: Track 53890064 ladder μ; import model_iter4/5 when training pauses; no RL upload until L1 beats 53869254.
Status: Alakazam ref 53890064 COMPLETE @600; 5/5 daily slots used; Kaggle RL at iter 6; iter4+5 promoted.
Next: python scripts/analyze_submission.py --ref 53890064 — then import iter4/5 from Downloads when ready.

Branch: main (ahead 2) | Env: Python313 cu128 | No upload until user OK + quota
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
