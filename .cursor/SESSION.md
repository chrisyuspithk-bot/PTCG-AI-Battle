# Session state — PTCG AI Battle Challenge

## Current focus

**Goal:** Climb ladder μ (leaders ~1310); keep **Search Lucario 668 μ** as Final until beaten.
**Today's submissions (2026-06-21, both COMPLETE):** Alakazam best5 **636.8** (exceeded forecast),
Trevenant **597.7** (weak, as 15% gate predicted). **2/5 slots used → HOLD the other 3.**
**Primary handoff:** [`report/handoffs/deck_rl_continuation_20260621.md`](../report/handoffs/deck_rl_continuation_20260621.md).
**THE pivot this session — field map (`scripts/analyze_winners.py`, 5,584 games):** the meta is a
rock-paper-scissors triangle **Lucario → Bellibolt → Alakazam → Lucario**; Lucario is ~53% of decks;
the **Lucario mirror is ~30% of all games, 50/50 on deck → decided by PILOT.** Field is aggressive
(KO race 72% @ ~13 turns, board-wipe 21% @ ~9 turns, deck-out only 7.5%). Report:
[`report/winner_analysis_20260621.md`](../report/winner_analysis_20260621.md).
**Proven dead end:** robust deck search with a generic brain (L1 3.8–12.5%). Pilot >> deck.
**Next (highest leverage):** improve our Search Lucario **mirror** play (prize-trade sequencing,
KO tempo) — it's the biggest score lever. Then shore up Alakazam's Bellibolt/Iono hole. No uploads w/o user OK.

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main` (ahead, not pushed)
- **Uploads 2026-06-21:** 2/5 used (Alakazam 636.8, Trevenant 597.7) — **3 remain, HOLD** — [`data/SUBMISSION_PLAYBOOK.md`](data/SUBMISSION_PLAYBOOK.md)
- **Live ladder top (ours):** 668 Search Lucario (Final) > 660.5 lucario_ex_search > **636.8 Alakazam** > 633.0 Kyogre > 626 Kyogre-probe1 > 597.7 Trevenant
- **⚠️ Double-submit trap:** a stale autonomous doc (Session 38) says "submit Trevenant Slot 3" — Trevenant is ALREADY done. See PROGRESS Session 39 correction. Do NOT re-submit Alakazam or Trevenant.
- **Field analysis is now the daily routine:** download dump (slugs in `report/deck_rl/episode_dataset_manifest.csv`, refreshed from `kaggle/pokemon-tcg-ai-battle-episodes-index`) → `python scripts/analyze_winners.py --replays report/replays` → dated `report/winner_analysis_<DATE>.md`.
- **Field is hardening:** median agent score 628→1064 over 06-16→06-20 (~+110/day); top plateaus ~1320. Static agent loses rank daily → pilot work is time-sensitive.
- **Robust deck search:** validated method, DEAD END with generic brain (heuristic deck L1 12.5%, search deck L1 3.8% — 78% gauntlet was a same-brain mirror illusion). Subsystem in `rl/robust_*`, `rl/gauntlet.py`; outputs `report/robust_deck_rl/` (+ `_search/`). Don't re-run for ladder gains.
- **Scoring model:** per-game reward is binary ±1; the 600–1300 score is TrueSkill μ; compounds by beating strong (=Lucario) opponents. No hidden per-game points.
- **Code health:** `scripts/analyze_winners.py` reviewed + simplified (dropped an unreliable prize-count metric). `scripts/gate_track_b.py` opponent-tuple fix verified.
- **GPU:** `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe` (cu128)
- **Upload:** user OK required; protect the 668 Final

## Continue prompt

```text
Continue PTCG ladder work. Read first: @.cursor/SESSION.md, @report/handoffs/deck_rl_continuation_20260621.md, @report/winner_analysis_20260621.md, @data/SUBMISSION_PLAYBOOK.md, @PROGRESS.md (top).

Goal: climb μ; protect the 668 Search Lucario Final; upload only with explicit user OK.
Status (2026-06-21): 2/5 slots used — Alakazam best5 636.8, Trevenant 597.7 (both COMPLETE). HOLD remaining 3 slots; neither beats 668. Do NOT re-submit Alakazam/Trevenant (a stale Session 38 doc wrongly says "submit Trevenant Slot 3" — it's done).
Key finding: field is a RPS triangle (Lucario→Bellibolt→Alakazam→Lucario); Lucario = 53% of decks; the Lucario MIRROR is ~30% of games, 50/50 on deck, decided by PILOT. Robust deck search is a proven dead end with a generic brain — pilot >> deck.
Next (highest leverage): improve Search Lucario MIRROR play (prize-trade sequencing, KO tempo; field is aggressive ~12 turns). Baseline with `gate_vs_public.py --only lucario --games 30`. Then fix Alakazam's Bellibolt/Iono hole. Run `scripts/analyze_winners.py` on each new daily dump.

Branch: main (ahead) | Env: Python313 cu128 | Upload only with user OK
```

## Timeline

- **2026-06-21** | Submitted Alakazam best5 (636.8) + Trevenant (597.7); HOLD remaining slots
- **2026-06-21** | Built `analyze_winners.py` field analysis → RPS triangle + Lucario-mirror lever; downloaded episodes-index; code-review + simplify of the analyzer
- **2026-06-21** | Robust deck search proven dead-end (Search-pilot L1 3.8%); pivot to pilot/mirror work
- **2026-06-20T17:05:00Z** | handoff by user | conv `lucario-top-performer-v1`
- **2026-06-20T20:30:00Z** | handoff by user | conv `lucario-hybrid-v2`
- **2026-06-20 EOD** | LucarioSearchScorer impl + partial L1; deck-out insight; strategy doc refresh
- **2026-06-20 EOD** | Alakazam 1M retired; Lucario iter3 assessed; repo cleanup
- **2026-06-20** | SmartBench + meta tactics; ref 53886522 submitted
- **2026-06-20** | Top-performer Kaggle CLI analysis — refs 53802029–53800247
- **2026-06-20T17:35:00Z** | handoff by user | conv `high-mu-submission-plan`
- **2026-06-20T18:00:00Z** | handoff by user | conv `alakazam-upload-iter45-rl`
- **2026-06-20T18:45:00Z** | handoff by user | conv `iter45-staged-handoff`
- **2026-06-20T19:30:00Z** | handoff by user | conv `full-commit-eod-handoff`
