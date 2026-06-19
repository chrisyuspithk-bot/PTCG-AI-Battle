# Finals strategy (massive-jump plan)

**Full test workflow:** [`data/EVAL_PROTOCOL.md`](../data/EVAL_PROTOCOL.md)  
**Upload rules:** [`data/SUBMISSION_PLAYBOOK.md`](../data/SUBMISSION_PLAYBOOK.md)

## Portfolio recommendation — **Track B priority (2026-06-19+)**

Use **both Final Submission slots** for LearnedScorer agents after per-deck train+distill+gate.

| Slot | Agent | Deck | Rationale |
|------|-------|------|-----------|
| **Final 1** | LearnedScorer | Kyogre (`a2_kyogre_33_energy.csv`) | Best ladder signal (633 μ heuristic); retrain policy on this deck first |
| **Final 2** | LearnedScorer | Second meta archetype (Crustle or Dragapult) | Diversify matchup coverage; requires separate `train_track_b_deck.py` run |

Track A (Search) and heuristic Kyogre remain **local baselines** and ladder probes — not Finals unless Track B gates fail.

```bash
# First production Track B run (no Kaggle submit in script)
python scripts/train_track_b_deck.py \
  --deck agent_decks/a2_kyogre_33_energy.csv \
  --slug kyogre --timesteps 100000 --gate-games 40 --package --promote
```

## Ladder probes (do not auto-submit)

**Read [`data/SUBMISSION_PLAYBOOK.md`](../data/SUBMISSION_PLAYBOOK.md) before every upload.**

- Record all submission IDs in `report/ladder_history.csv`
- Use `scripts/track_ladder.py` after each upload; `--fetch-logs` when COMPLETE
- **5 uploads/day** (hard cap) | **Latest 2 active** for standings (older show “disabled”)
- **Probe order:** experiments first → **best μ last** so it stays in the active pair
- **μ interpretation:** ~600 on COMPLETE = validation baseline; real W/L after ~40 min
- **2026-06-19 lesson:** Kyogre 633.0 was best μ but disabled after 3 later probes

## Local gates (SPRT)

- Track A: `scripts/gate_track_a.py` — SearchScorer vs pool (currently **not passed** at smoke game count)
- Track B: `scripts/gate_track_b.py` — LearnedScorer vs pool
- Distill: `scripts/distill_policy.py` — latency + numpy-only packaging

## Nightly cadence

```bash
python scripts/nightly.py --run-all
```

Checkpoint: `report/nightly_checkpoint.json` (all 16 steps complete as of run 13).
