# Search audit (2026-06-20)

## Scope

- Agent under test: `lucario_search`
- Command:
  `SEARCH_AUDIT_LOG=report/search_audit_events_20260620.jsonl python scripts/record_local_battle.py --agent-a lucario_search --agent-b search --deck-a agent_decks/real_mega_lucario_ex.csv --deck-b agent_decks/real_mega_lucario_ex.csv --games 5 --name lucario_search_audit_20260620`
- Local result: 4/1/0, 80.0% WR, 17 avg turns, 0.0% fast losses.

## Verdict

Search fires in local simulator games. This audit does not prove live ladder firing for ref 53869254, but it rules out the local implementation being permanently blocked by missing `search_begin_input`.

## Counters

| Metric | Count |
|---|---:|
| `try_search` calls | 602 |
| Eligible search contexts | 55 |
| Eligible with `search_begin_input` | 55 |
| Eligible missing `search_begin_input` | 0 |
| Search results returned | 55 |
| Lucario top-2 guard accepted | 26 |
| Lucario top-2 guard rejected | 0 |

Eligible contexts:

| Context | Count |
|---|---:|
| 1 | 10 |
| 3 | 31 |
| 4 | 14 |

## Interpretation

- `search_begin_input` is present for the local high-leverage contexts tested.
- `SearchBegin`/`SearchStep` return picks locally.
- The Lucario top-2 guard is conservative by design, but in this batch every guarded pick that reached the guard was accepted.
- Live 53869254 ladder logs still show very low decision durations, so ladder search may still be rare because eligible contexts are rare in public games, not because the local search path is dead.

## Artifacts

- Raw audit log: `report/search_audit_events_20260620.jsonl`
- Local replay summary: `report/local_replays/lucario_search_audit_20260620_seed0.json`
