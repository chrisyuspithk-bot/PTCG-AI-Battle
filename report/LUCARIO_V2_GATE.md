# Lucario v2 gate (2026-06-20)

## Expanded leader-suite L1

Command:

```bash
python scripts/gate_track_a.py --games 30 --agents lucario_search --deck agent_decks/benchmark/suite.json --output report/public_gate/lucario_v2_vs_leader_suite_20260620.txt
```

Result:

- `lucario_search`: 313/450 = 69.6%
- Heuristic baseline: 281/450 = 62.4%
- SPRT decision: `accept_b`
- Gate passed: `True`
- Package built by gate: `dist/candidates/track_a_lucario_search.tar.gz`

Weak matchups remain the Trevenant variants:

- `leader_trevenant_control`: 14/30 = 46.7%
- `leader_trevenant_dunsparce`: 12/30 = 40.0%

## Submission decision

Do not upload automatically. This gate is now strong enough for user-approved probe consideration, but ladder proof is still absent and the project contract requires explicit user OK before any Kaggle submission.

See the full per-opponent report at `report/public_gate/lucario_v2_vs_leader_suite_20260620.txt`.
