# Session state — PTCG AI Battle Challenge

## Current focus

**Lucario SmartBench + meta tactics complete; report written.** `LucarioScorer` on
`real_mega_lucario_ex.csv` with bench guard, search/energy line setup, and
competitive meta (Solrock/Lunatone, Jab/Brave, Hariyama gust). L1 @ 30 games:
**10% overall**, **43.3% vs Lucario sample** — mirror strong, cross-archetype weak
without search. **Do not replace Finals Search (668 μ, ref 53869254).** **Next:**
implement `LucarioSearchScorer` hybrid (Search lookahead + Lucario MAIN), L1 @ 30g,
compare to 53869254.

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main` (dirty, uncommitted Lucario + tooling)
- **Report:** `report/lucario_smartbench_report_20260620.md` — full write-up of this pass
- **Candidate:** `dist/candidates/track_c_lucario_rulecore_smartbench.tar.gz` (`--scorer lucario --gate` OK)
- **Policy:** `agent/lucario_policy.py`, `agent/bench_guard.py`, `agent/smart_bench.py`, `scripts/smoke_replay.py` (12/12)
- **Best ladder:** ref **53869254** SearchScorer Lucario **668 μ** — keep Finals until hybrid beats L1+L4
- **SmartBench ladder:** ref **53886522** **600 μ** — too few L4 episodes; re-analyze after more games
- **Retired:** ref **53885445** RL iter-0 **324 μ** (empty bench); RL re-import blocked until iter≥4
- **L1 gate cmd:** `python scripts/gate_vs_public.py --agent dist/candidates/track_c_lucario_rulecore_smartbench.tar.gz --games 30`
- **Episode stats:** `python scripts/analyze_submission.py --ref <ref>` — win_rate, avg_turns, fast_loss_pct
- **Submission log:** `report/submission_log.csv` | **Finals guide:** `report/FINALS_PIN.md`
- **Blocker:** no Kaggle upload without explicit user OK
- **Env:** Windows; **GPU RL:** `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe` (cu128). Miniconda `(base)` OK for packaging/gates; avoid miniconda for Track B GPU train (CPU torch).

## Continue prompt

```text
Continue Lucario hybrid agent. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @report/lucario_smartbench_report_20260620.md, @agent/lucario_policy.py, @agent/search_policy.py

Goal: LucarioSearchScorer — Search on setup/switch/to-active + LucarioScorer MAIN/meta; beat 668 μ baseline on L1 @ 30 games.
Status: SmartBench tarball built; L1 10% overall, 43.3% vs Lucario sample; report done; Finals still 53869254.
Next: Implement LucarioSearchScorer, package track_a_lucario_ex_search_v2, run gate_vs_public --games 30; no Kaggle submit without user OK.

Branch: main (dirty) | Env: Python 3.13 for GPU RL; (base) OK for gates
```

## Timeline

- **2026-06-20T18:45:00Z** | handoff by user | conv `9d3d5932`
- **2026-06-20T17:30:00Z** | handoff by user | conv `deck-rl-phase2d`
- **2026-06-20T16:00:00Z** | run 47 | Phase 2d collapse penalty + 20-gen GA
- **2026-06-20T15:00:00Z** | handoff by user | conv `deck-rl-phase2c`
- **2026-06-20T14:30:00Z** | run 45 | Phase 2c role/chain mutations + 10-gen GA
- **2026-06-20T14:00:00Z** | handoff by user | conv `deck-rl-phase2b`
- **2026-06-20T13:30:00Z** | run 44 | Phase 2b per-lane GA selection implemented and verified
- **2026-06-20T13:25:00Z** | handoff by user | conv `deck-rl-phase2a`
- **2026-06-19T18:15:00Z** | handoff by user | conv `586c52cd`
- **2026-06-19T17:35:00Z** | handoff by user | 5/5 ladder slots live
- **2026-06-19T17:33:00Z** | run 18 | TA1+TA2 submitted; ladder sync dragapult 468.9, alakazam 490.4
- **2026-06-19T17:24:00Z** | run 18 | Track B alakazam + dragapult submitted
- **2026-06-19** | run 16–17 | RL distill export; Track B deck spread; Track A probe tooling
- **2026-06-19T16:08:00Z** | A2 Kyogre #53854707 first successful upload
