# Overnight Handoff — 2026-06-20 (~00:30 EDT)

## ✅ SUBMITTED tonight (your "best Lucario ex option")
- **`track_a_lucario_ex_search.tar.gz`** → status PENDING
- Mega Lucario ex (real mined meta list) + **SearchScorer** (our best rules)
- Picked search over heuristic on a head-to-head: **search 29/30 (96.7%)** vs heuristic 27/30 (90%) vs benchmark; 0 unfinished, ~55 steps/game (safe on Kaggle time budget)
- **Slots today: 2 of 5 used, 3 left.**

## Deck quality — confirmed "close to the leaders"
`agent_decks/real_mega_lucario_ex.csv` is the **same shell that beat our Kyogre** on the ladder:
4× Mega Lucario ex, 3× Riolu, 2/2 Makuhita/Hariyama, 3× Solrock, 2× Lunatone, 4× Premium Power Pro, 4× Fighting Gong, 4× Carmine, 4× Lillie's Determination, 4× Dusk Ball, 4× Poké Pad, 2× Boss's Orders, 2× Switch, 2× Gravity Mountain, 1× Hero's Cape, 13× Fighting Energy. Mined from real replays — legit meta list.

## 🎮 Deck for YOU to train (as requested)
Path: **`agent_decks/real_mega_lucario_ex.csv`**

Local GPU train command (Track B learned):
```bash
python scripts/train_track_b_deck.py \
  --deck agent_decks/real_mega_lucario_ex.csv --slug lucario_ex \
  --timesteps 100000 --n-envs 4 --opponents benchmark \
  --holdout a2_kyogre --gate-games 40 --package
```
(Lucario's line is shallower than Alakazam's, so RL should learn it better. Consider 200k+ steps.)

## ⚠️ Alakazam RL — did NOT learn (FAILED, shelved)
Flat curve, never came online: train WR 6.7→6.7→15.4→7.1% across 20k–80k. The Abra→Kadabra→Alakazam two-stage line is too complex for 100k-step RL.
**Gate result (final): FAILED** — Learned **32/110 (29%)** vs Search baseline 119/240 (~50%), SPRT `accept_a` (reject learned). No candidate packaged. `distilled_v1.npz` was NOT touched (used `--package`, not `--promote`).
**Recommend:** shelve unless we give it a much longer run; Lucario is the better bet.

## Other ladder notes
- **`track_b_learned_rl_deck`** (slot 1 today): settled to ~500 but only ~4 games in — noise, not a verdict. Let it accumulate games before judging.
- **RL review TODO (you flagged it):** the real issue to fix is the "competitive-then-can't-close" late-game pattern — reward shaping rewards development but under-weights closing prizes / lethal KOs. That's the next training-side fix, affects every learned agent we make.

## Backups
Submitted models + pre-sweep state saved in `report/_model_backup_20260620/`.
