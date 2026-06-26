# Starmie / Froslass gate — Session 51

**Brain:** `agent/starmie_agent.py` (rule pilot + PrizeTracker + finish search)  
**Deck:** `agent_decks/starmie_froslass_ashleysandlin.csv`

## Mirror smoke (suite `starmie`, n=30)

| Opponent | WR | CI |
|----------|-----|-----|
| `starmie_froslass_ashleysandlin` (mirror) | **56.7%** | [39.2, 72.6] |

## Full native field suite (n=30)

| Opponent | WR |
|----------|-----|
| dragapult_ex_sample | 10.0% |
| real_mega_abomasnow_ex | 3.3% |
| real_iono | 0.0% |
| real_dragapult_ex | 20.0% |
| real_mega_lucario_ex | 13.3% |
| **OVERALL** | **9.3%** |

Filter only — not ladder truth. Pilot is first port; iterate before upload.

## Archaludon vs Starmie (n=30)

See `eval/gate_archaludon.md` — Archaludon **100.0%** vs native Starmie pilot (Metal vs Water skew; author claimed 74.4% vs stronger pilot).

## Infrastructure

- `agent/prize_tracker.py` — wired into `SearchScorer` deck-search picks
- `field/registry.json` — `starmie_froslass_ashleysandlin` native brain
- `scripts/gate_starmie.py`
