# Session state — PTCG AI Battle Challenge

## Current focus

Track B is the **primary submission path**. Kyogre per-deck pipeline completed: 100k CUDA train vs 10 benchmark opponents → distill → gate **206/240** (SPRT pass) → package `dist/candidates/track_b_learned_kyogre.tar.gz`. Kaggle upload **blocked** (5/5 daily Simulation quota used 2026-06-19). **Next:** submit tarball when quota resets; pin **Final 1**; run second `train_track_b_deck.py` for Crustle or Dragapult (Final 2).

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main` (ahead 2 of origin, unpushed)
- **Pending upload:** `dist/candidates/track_b_learned_kyogre.tar.gz` — see `report/submission_pending_kyogre.md`
- **Models (local):** `distilled_kyogre_v1.npz`, promoted `distilled_v1.npz`, `rl_policy.zip` — not committed
- **Track B tooling:** `scripts/train_track_b_deck.py`, `rl/env_factory.py`, `rl/train_rl.py --deck --opponents`
- **Testing doc:** `data/EVAL_PROTOCOL.md` | **Upload rules:** `data/SUBMISSION_PLAYBOOK.md`
- **Best ladder μ:** Kyogre heuristic **633.0** (#53854707); old Learned probes 490/469 (wrong-deck train)
- **Today's Finals (Search):** TA1 Kyogre+2e **580.8**, TA2 Abomasnow **486.4**
- **Gate report:** `report/track_b_gates/track_b_learned_kyogre_gate.md`
- **Run log:** `report/track_b_runs/kyogre_20260619_180332.json`
- **Deck RL:** overnight campaign in progress — `report/rl_deck_campaign/` (separate from Track B)
- **Decision:** Track B = Finals target; heuristic/Search = baselines only
- **Blocker:** 5/day Simulation submit cap until next UTC day
- **Env:** Python 3.13, torch 2.6.0+cu124, RTX 4070 Ti SUPER

## Continue prompt

```text
Continue PTCG Track B Kyogre upload + Final 2 deck. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @PROGRESS.md, @report/submission_pending_kyogre.md, @data/SUBMISSION_PLAYBOOK.md

Goal: Upload Learned Kyogre package to Simulation ladder and pin Final 1; start second per-deck Track B train.
Status: Package ready; submit blocked 5/5 today; gate 206/240 SPRT pass.
Next: kaggle competitions submit -f dist/candidates/track_b_learned_kyogre.tar.gz; track_ladder.py --fetch-logs; pin Final on Kaggle UI.

Branch: main (ahead 2) | Env: Python 3.13, torch+cu124 | Submit OK when quota resets.
```

## Timeline

- **2026-06-19T18:15:00Z** | handoff by user | conv `586c52cd`
- **2026-06-19T17:35:00Z** | handoff by user | 5/5 ladder slots live
- **2026-06-19T17:33:00Z** | run 18 | TA1+TA2 submitted; ladder sync dragapult 468.9, alakazam 490.4
- **2026-06-19T17:24:00Z** | run 18 | Track B alakazam + dragapult submitted
- **2026-06-19** | run 16–17 | RL distill export; Track B deck spread; Track A probe tooling
- **2026-06-19T16:08:00Z** | A2 Kyogre #53854707 first successful upload
