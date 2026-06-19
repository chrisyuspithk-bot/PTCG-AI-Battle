# Track A gate report

Generated: 2026-06-19T17:14:08.990379+00:00

Deck: `Z:\kaggle\pokemon\report\deck_search\best_deck.csv`

## SPRT (SearchScorer vs pool)
- Search wins: 43/48 (89.6%)
- Heuristic wins: 40/48 (83.3%)
- SPRT decision: **accept_b** (log_ratio=4.028)
- Gate passed: **True**

## Packaging
- Package: `Z:\kaggle\pokemon\dist\candidates\track_a_search.tar.gz`

## Suggested submit command (DO NOT run automatically)
```
kaggle competitions submit -c pokemon-tcg-ai-battle -f Z:\kaggle\pokemon\dist\candidates\track_a_search.tar.gz -m "Track A SearchScorer probe (user approval required)"
```

## Notes
built Z:\kaggle\pokemon\dist\candidates\track_a_search.tar.gz (2749.4 KiB)
dry-run import OK; deck-selection returns 60 card IDs
No Kaggle submission was attempted.

Wire SearchScorer in submission by replacing default agent factory:
```python
from agent.search_policy import SearchScorer
from agent.agent import build_agent
_AGENT = build_agent(scorer=SearchScorer())
```
