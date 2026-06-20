# Top performer reverse-engineering (2026-06-20)

Authoritative output from Kaggle CLI + replay mining. See also
[`data/KAGGLE_SIMULATION_CLI.md`](../data/KAGGLE_SIMULATION_CLI.md).

---

## Manifest clarification (`Downloads/manifest.csv`)

Not a per-agent leaderboard index — indexes **daily bulk episode datasets**:

| date | episodes | top_avg_score | median_avg_score |
|------|----------|---------------|------------------|
| 2026-06-16 | 1,277 | 1024.6 | 627.8 |
| 2026-06-17 | 7,819 | 1259.8 | 761.0 |
| 2026-06-18 | 6,532 | **1327.1** | 926.6 |
| 2026-06-19 | 5,426 | 1324.9 | **1013.7** |

`top_avg_score` ≈ leaderboard top μ (~1313). Per-agent refs require
`kaggle competitions leaderboard` + `team-submissions`. Daily datasets (~20 GB/day)
not downloaded locally.

---

## Top 5 performers (Kaggle CLI, 2026-06-20)

| Rank | Team | Ref | μ | Episodes | Deck signal (replay mining) |
|------|------|-----|---|----------|----------------------------|
| 1 | TrustHub hiroingk | **53802029** | **1312.7** | 76 | Alakazam + Dudunsparce, Rare Candy, Poffin, Poké Pad, Dawn/Hilda |
| 2 | The Debauchery Tea Party | **53880887** | **1304.2** | 42 | Hop's Phantump/Trevenant + Hop's Bag, TR Transceiver, Pokégear 3.0 |
| 3 | foo_foo | **53876944** | **1284.6** | 45 | Trevenant/Phantump + Dunsparce, Pokégear, Poké Pad |
| 4 | THIRD PTCG Club | **53878567** | **1261.3** | 46 | Alakazam engine (same family as #1) |
| 5 | カドラバ Kadoraba | **53800247** | **1252.0** | 83 | Alakazam line (Abra/Kadabra, Hilda/Dawn, Poffin/Pad) |

**Sample replay stats (11 fetched games, leaders only):**

| Team | W/L | Avg win turns | Avg loss turns | Fast losses (<15t) |
|------|-----|---------------|----------------|---------------------|
| TrustHub | 3W/2L (5 ep sample) | **21** | 13 | 2/2 losses |
| TrustHub **53802029** (75 ep, seat-fixed) | 39W/36L | — | **13.1** avg all games | **72%** fast_loss |
| Debauchery Tea Party | 2W/3L | **20** | 21 | 0 |
| foo_foo | 2W/1L | **23** | 22 | 0 |
| THIRD PTCG Club | 2W/2L | 13 | 23 | 0 |

Replays saved under `report/replays/` (`top_*.json`, `ref*.json`).

---

## Our agent vs leaders

| Ref | Scorer | μ (Kaggle) | Local stats |
|-----|--------|------------|-------------|
| **53869254** | SearchScorer + Lucario | **660.5** | 48.5% WR, avg **13.4** turns, **58.8%** fast_loss |
| 53886522 | LucarioScorer + SmartBench | 560.5 | 2 ep only |

**Gap:** Leaders win at ~20–23 turns on stable control decks; our Lucario averages
~13 turns with high fast_loss. Top field is **Alakazam/Trevenant**, not Lucario-heavy.

**Search audit (53869254 logs):** decision durations mean ~0.8 ms — `search_*` layer
rarely active (missing `search_begin_input` or fast fallback).

**Data-quality bugs (fixed 2026-06-20):**

- `analyze_submission.py` now resolves **per-episode** `agent_index` via manifest + team name (seat alternates).
- `result_reason` parser uses top-level `rewards` + prize-before-`no_active` terminal state.

**Still open:**

- `result_reason` edge cases on very short games (minor).
- Opponent agent logs unavailable (403).

---

## Top 5 tactics to port (Lucario hybrid)

1. **Expand L1 suite** — add replay-mined Alakazam and Trevenant decks to
   `agent_decks/benchmark/suite.json`; optimize for ~20+ turn matchups, not mirror-only.
2. **Deck-out throttle** — Carmine/Lillie/Lunatone at low `deckCount` (implemented in
   `LucarioScorer`); port RuleCore wall-mode draw penalties for long games.
3. **Search scope + guard** — no `SETUP_BENCH` search (bench_guard already routes it);
   search-guard: only accept cg pick if in Lucario top-2 (`SEARCH_GUARD_TOP_K`).
4. **Verify search fires on ladder** — audit `search_begin_input` on switch/to-active;
   if search inactive, 660 μ is mostly generic Heuristic MAIN.
5. **Reduce fast_loss** — bench_guard + max-2 bench; avoid 2–7 turn collapses (59% of losses).

---

## Data sources

| Source | Status |
|--------|--------|
| `kaggle competitions leaderboard` | ✅ |
| `kaggle competitions team-submissions` | ✅ |
| `kaggle competitions episodes` | ✅ |
| `kaggle competitions replay` | ✅ (11 leader replays) |
| `kaggle competitions logs` (opponents) | ❌ 403 |
| Daily episode datasets (~20 GB) | ❌ not downloaded |
| `Downloads/manifest.csv` | ✅ daily index only |

---

## Blockers

1. Opponent agent logs unavailable (403).
2. Daily bulk datasets not local — need `kaggle datasets download` for BC-scale mining.
3. `result_reason` parser broken.
4. `analyze_submission.py` agent_index bug.
5. Small leader replay sample — batch 20–30 episodes per top ref.

---

## Next commands

```bash
kaggle competitions replay <episode_id> -p report/replays
python scripts/analyze_submission.py --ref 53869254  # fix per-ep agent_index first
# Optional: kaggle datasets download pokemon-tcg-ai-battle-episodes-2026-06-19 -p data/kaggle_ref/episodes
```
