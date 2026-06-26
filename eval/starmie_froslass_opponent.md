# Starmie / Froslass — Gold Medal field opponent

**Status:** Deck + **native rule pilot** (`agent/starmie_agent.py`). Harness suite `starmie`; gate report `eval/gate_starmie_session51.md`.

## Source deck

[Limitless — ashleysandlin, Redacted Heroes 2nd Chance #6](https://play.limitlesstcg.com/tournament/69e4f71948d465883f718047/player/ashleysandlin/decklist)

Gold-medal author (1300+ μ) built on this list. Our CSV maps sim card IDs from `data/sim/EN_Card_Data.csv`.

| File | Notes |
|------|-------|
| `agent_decks/starmie_froslass_ashleysandlin.csv` | Canonical name |
| `agent_decks/a3_starmie_spread_33_energy.csv` | Alias (benchmark `suite.json` legacy path) |

**60 cards:** 4 Snorunt, 3 Mega Froslass ex, 4 Staryu, 3 Mega Starmie ex; Lillie/Salvatore/Wally/Hilda/Boss/Poffin suite; 9 Water + Legacy/Ignition/Mist.

## Why this archetype matters

- Top ladder band includes **Starmie / Froslass** rule pilots (author cites **1300+ μ**).
- **Archaludon** community pilot claims **74.4%** vs this archetype (matchup-skewed — Metal weak to Water); see `eval/archaludon_ex_cinderace_candidate.md`.
- Our **Lucario** and **SearchScorer** gates do not yet include Starmie — add once we have a real opponent brain or accept random as a weak smoke filter only.

## Lessons from gold-medal write-up (apply to SearchScorer / finish search)

1. **Normal turns = rules; winning turns = verified search** — matchup modules + lethal `Finish` mode.
2. **Prize tracking for search** — Hilda/Salvatore deck searches must not assume cards still in deck when they are prized (**NOMATCH** failures).
3. **Conservative inference** — wrong prize guess worse than unknown; exact match on prize count only.
4. **In-flight effects** — subtract `obs.select.effect` while Hilda (etc.) resolves (not yet in hand/discard).

Implemented in repo: `agent/prize_tracker.py` (reusable; not yet wired into `search_policy.py`).

## Harness (smoke — random opponent)

```powershell
python -c "
from eval.harness import load_deck, gate_vs_opponent, make_lucario_brain, clear_caches
from eval.field_registry import ROOT
clear_caches()
deck = load_deck(ROOT / 'agent_decks/real_mega_lucario_ex.csv')
brain = make_lucario_brain(deck)
r = gate_vs_opponent(brain, deck, 'starmie_froslass_ashleysandlin', games=2)
print(r)
"
```

**Not** a R2 gate opponent until we port a rule pilot (or import public notebook). Do not add to `core`/`full` weighted gates with random brain.

## Next steps

1. Port gold-medal Starmie rule agent (modes: generic / matchup / finish + forward search).
2. Wire `PrizeTracker` into search layer before enabling finish mode on our Lucario/SearchScorer stack.
3. Gate Archaludon vs **native** Starmie pilot @ n≥30.
4. Optional ladder probe only after local gate + `check_upload_eligible` (R12).
