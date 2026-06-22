# Matchup playbook — field decks vs Lucario (Phase 1–2)

**Purpose:** Counter-research for the 10 real-field opponents + how to tune **global rules**
(`lucario_policy.py`, `deck_tech.py`) vs **matchup levers** (`agent/matchup_levers.py`, `rule_core.py`).

**Authority order:** simulator legal mask > this doc > real-world TCG articles. Always verify lever
changes with `gate_vs_public.py` or per-opponent arena runs.

**Sources:** Pokemon.com official Lucario article; wmh/ptcg-abc meta; deck CSVs in `agent_decks/`;
train eval `rl_mcts_field/lucarioex_v1/metrics.csv`; public sample agents in competition.

---

## Global rules already in our Lucario pilot (Phase 1 baseline)

| Mechanism | Where | Role |
|-----------|-------|------|
| Solrock/Lunatone draw engine | `lucario_policy.py` | Single-prize pressure; bridge when Mega is damaged |
| Hariyama wall-breaker | `lucario_policy.py`, `LUCARIO_TECH` | Non-ex damage vs walls / ex trades |
| Mega Brave finisher | `lucario_policy.py` | 2-prize KOs; skip when target is single-prize bulk |
| Boss's Orders | plan.target + play score | Gust bench targets into active |
| Premium Power Pro / Fighting Gong | supporter scoring | Damage stack for Fighting line |
| Smart bench cap | `smart_bench.py` | Avoid empty bench / over-bench snipe |
| Prize-trade plan | `_build_plan` lines ~388–401 | Solrock vs ≤1 prize; Hariyama vs ex; Mega Brave vs ex |

These are **global** — they should be stable before per-matchup deltas.

---

## Per-opponent counter research

### 1. `real_mega_lucario_ex` / `top_mined_mega_lucario_ex` — **Lucario mirror** (~53% field)

**Their plan:** Same as ours — Aura Jab accel, Mega Brave OHKOs, Solrock/Lunatone, Hariyama gust.

**How they beat us:** Race to Mega Brave on our ex (3 prizes); gust our Riolu before evolve; mirror
prize math punishes reckless Mega Brave (opponent takes 3 prizes if we die).

**Real-world / meta:** Open Solrock vs single-prize decks, Mega vs ex races (Pokemon.com). Psychic
types counter Lucario in TCG Pocket meta — less relevant in mirror.

**Global rules that help:** Prize plan already prefers Mega Brave vs 2-prize targets; Switch after
Mega Brave.

**Levers to add (Phase 2):**
- Gust **Riolu** on bench before evolve (`gust_setup_pokemon`)
- Boss priority when their Mega is 1-hit from death
- Slightly favor **Riolu** active T1 in mirror (contested prize race)

**Train eval:** 50%→75% (cycle 4) — improving; pilot tuning still matters.

---

### 2. `top_mined_alakazam` / public Alakazam — **Psychic single-prize aggro**

**Their plan:** Dudunsparce draw → huge hand → Alakazam **Powerful Hand** (damage scales with hand size);
single-prize line; Enhanced Hammer energy removal.

**How they beat us:** Psychic weakness on Fighting — they OHKO Mega Lucario ex (2–3 prizes). We give
up 3 prizes on Mega death (game-ending).

**Real-world:** Official Lucario article — **Rocky Energy** blocks damage-counter effects (Alakazam line);
pressure with Judge; finish with Solrock/Hariyama single-prize attacks.

**Global rules:** `line_bonus` already skips Mega Brave into bulky single-prize; Solrock line favored.

**Levers:**
- **Open Solrock** vs Alakazam board visible (Abra line)
- **Boss Abra/Kadabra** before evolve
- Deprioritize Mega Brave unless guaranteed KO on ex
- Consider deck tech: Rocky Energy if legal in our list (not in current `real_mega_lucario_ex.csv`)

**Train eval:** 75%→65% — do not over-trust RL; lever Boss + single-prize race.

---

### 3. `real_dragapult_ex` / `top_mined_dragapult_ex` — **Dragapult tempo**

**Their plan:** Dreepy/Drakloak evolution, Dragapult ex **Phantom Dive** spread, Munkidori/Budew tech,
Crushing Hammer + Unfair Stamp disruption.

**How they beat us:** Spread damage weakens our bench; snipe Riolu; tempo before Mega online.

**Real-world:** Ultima/Deltia — Lucario checks some ex decks; retreat with Air Balloon after Mega Brave.

**Levers:**
- Gust **Dreepy/Drakloak** early
- Solrock chip on single-prize basics
- Switch after Mega Brave (already global)
- Higher Boss when spread has damaged bench targets

**Train eval:** 90%→80% — strong; minor Boss tuning.

---

### 4. `real_iono` / `top_mined_iono` — **Iono Bellibolt lightning**

**Their plan:** Iono's Bellibolt ex line, Lillie's Determination, Voltorb/Tadbulb bench, Kilowattrel.

**How they beat us:** Disruption + Bolt Chain energy; wmh notes **simple linear lightning** decks often
outexecute complex pilots. Hand disruption delays our Mega setup.

**Real-world / wmh:** Iono-style Bellibolt was a top **simple** rule deck (Elo ~836) — execute cleanly.

**Levers:**
- **Lillie early** to recover from disruption
- Boss on low-HP basics before evolution
- Don't over-commit second bench (gust exposure) — already in `smart_bench`

**Train eval:** 70%→90% (cycle 4) — one of our best; levers lower priority.

---

### 5. `real_mega_abomasnow_ex` / `top_mined_mega_abomasnow_ex` — **GAP (0% RL eval)**

**Their plan:** 25–32 Water energy, **Hammer-lanche** (discard 6, 100 damage per Water discarded),
Snover evolution, Larry's Skill / Dawn / Lillie (mined has Kyogre + Mega Signal).

**How they beat us:** One-shot OHKOs when energy flip is high; we race Mega Brave into a deck that
doesn't trade prizes fairly; random high damage outpaces our setup.

**Real-world:** Flipside/PokemonCard — Boss to pick weak targets; deck thinning helps Hammer-lanche;
Kyogre recycles energy from discard in mined lists.

**Why our pilot fails:**
- We commit **Mega Lucario ex** into OHKO range before Snover is gone
- Insufficient **Solrock/Hariyama** race in first 2–3 turns
- Boss not prioritized on **Snover** (id 722)

**Levers (highest priority):**
- `prefer_solrock_open` +3
- `gust_setup_pokemon` +800 on Snover
- `skip_mega_brave_vs_bulk_single_prize` — don't Mega Brave into Snover
- `premium_power_pro` negative early — race, don't stack
- Target Snover with Boss before Hammer-lanche online

**Simulator note:** Verify Hammer-lanche damage in `cg` — mask-driven, not card text.

---

### 6. `top_mined_trevenant` — **GAP (20% RL eval)**

**Their plan:** Hop's Phantump → Trevenant, **Horrifying Revenge** (big damage if Hop mon died last turn),
Hop's Snorlax damage modifier, Dudunsparce draw, Boss + Choice Band.

**How they beat us:** Revenge punishes our KOs; Boss pulls our setup; we knock out Phantump and enable
220+ damage next turn.

**Real-world:** CardsRealm — avoid careless KOs that enable revenge; Boss their support; attack bench
setup before Trevenant online; control their special energy if possible.

**Levers:**
- `avoid_ko_trevenant_setup` — penalize KO on Phantump/Snorlax when Trevenant in hand/board
- Boss **Phantump** before evolve
- Solrock chip without enabling revenge KO lines
- Higher Boss priority (they run 2–3 Boss)

---

### 7. Crustle (public gate opponent, not in 10-deck train set)

**Their plan:** Dwebble/Crustle — **immune to Pokemon-ex** damage.

**Already implemented:** `rule_core.py` `crustle_wall` → Hariyama/Makuhita line, wall scoring.

**Levers:** Extend to `lucario_policy.py` when not delegating to LucarioScorer only.

---

## Implementation map (code)

| Layer | File | Action |
|-------|------|--------|
| Signatures + delta table | `agent/matchup_levers.py` | **Created** — tune numbers per gate |
| Apply deltas | `agent/lucario_policy.py` | Import `levers_for_lucario`; add to `_score_option` / `_build_plan` |
| Generic decks | `agent/rule_core.py` | Extend `archetype` dict; merge with `matchup_levers` |
| Deck card IDs | `agent/deck_tech.py` | Global gust/search tables (unchanged) |
| Validation | `scripts/gate_vs_public.py`, `scripts/arena.py` | Per-opponent before/after WR |
| Phase 3 mixture | `report/OPPONENT_DECK_DISTRIBUTION.md` | Weights **after** levers pass |

---

## Gate order (R11)

1. **Baseline** — Lucario global rules, equal-weight 10-deck gate → record CSV row.
2. **Abomasnow lever** — implement + re-gate `real_mega_abomasnow_ex` + `top_mined_mega_abomasnow_ex` only.
3. **Trevenant lever** — same pattern.
4. **Mirror / Alakazam** — Boss targeting refinements.
5. **Phase 3** — weight training/gates by field share from opponent tracker.

---

## References

- [Pokemon.com — Building Mega Lucario ex](https://www.pokemon.com/us/strategy/pokemon-tcg-deck-list-and-strategy-building-a-mega-lucario-ex-deck) — Solrock open, Hariyama, Rocky Energy vs Alakazam
- [wmh/ptcg-abc](https://github.com/wmh/ptcg-abc) — Crustle meta, Iono simplicity, local≠ladder
- `data/META_NOTES.md` — competition agent patterns
- `data/SIMULATOR_RESOURCE_NOTES.md` — mask authority, setup benching
- Official samples: repo root Lucario/Dragapult/Iono notebooks
