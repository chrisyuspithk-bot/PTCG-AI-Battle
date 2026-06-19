# Session state — PTCG AI Battle Challenge

## Current focus

**Track B on ladder.** Submitted today: alakazam **#53856584**, dragapult **#53856590** (PENDING).
Kyogre heuristic **#53854707** μ **645.7** (was 672.7). Nine packages in `dist/candidates/`.
Report: `report/track_b_deck_spread.md`. **Next:** `track_ladder.py` after ~40 min; `--fetch-logs` when COMPLETE.

## Track B packages (LearnedScorer + deck)

| Slug | Archetype | Local vs pool | Archive |
|------|-----------|---------------|---------|
| dragapult | Spread (field meta) | 66.7% | `track_b_learned_dragapult.tar.gz` |
| crustle | Non-ex anti-ex | 62.5% | `track_b_learned_crustle.tar.gz` |
| alakazam | Single-prize Dudunsparce | 50.0% | `track_b_learned_alakazam.tar.gz` |
| starmie | Spread pressure | 77.8% | `track_b_learned_starmie.tar.gz` |
| big_basic | Black Kyurem ex | 80.6% | `track_b_learned_big_basic.tar.gz` |
| bellibolt | Lightning aggro (wmh #1 rule-based) | 33.8% | `track_b_learned_bellibolt.tar.gz` |
| kyogre | Big basic Water | 81.9% | `track_b_learned_kyogre.tar.gz` (dup archetype vs live) |

Build all: `python scripts/package_track_b_spread.py --games 12`

## Track A ladder probes (SearchScorer + deck grid)

Two packages ready (`scripts/prepare_track_a_probes.py`). Manifest: `report/track_a/ladder_probes.md`.

| Slot | Archive | Deck | Pool @12g | Random @50g |
|------|---------|------|----------:|------------:|
| **TA1** | `track_a_probe_1.tar.gz` | Kyogre +2 energy | **91.7%** | 46/50 |
| **TA2** | `track_a_probe_2.tar.gz` | Abomasnow +4 energy | **87.5%** | 47/50 |

Both use **SearchScorer** (heuristic + optional promotion search). Submit TA1 first, then TA2;
`track_ladder.py --fetch-logs` after each (~40 min for ladder μ).

## Continue prompt

```text
Continue PTCG ladder probes. Read: @.cursor/SESSION.md, @report/track_a/ladder_probes.md

Goal: Compare Track A SearchScorer probes on ladder (TA1 Kyogre, TA2 Abomasnow deck).
Status: track_a_probe_1/2.tar.gz verified; Track B spread also ready (see track_b_deck_spread.md).
Next: user OK → submit track_a_probe_1; track_ladder.py --fetch-logs; then probe_2.

No Kaggle submit without explicit user OK.
```
