# TASKS — build-order backlog

Work top to bottom. Each step ends with **something measurable**; nothing speculative ships
(Ruling R3). Check `[x]` when done and log it in `STATE.md`. The full rationale for this order is
`ARCHITECTURE.md` § Build order and § Per-deck agent template (phases 1–3). The old 43-session backlog is in `graveyard/pre-reset-20260622`.

---

## Pilot rules — before mixture weighting (standing decision Session 44d)

Work **per deck** (Lucario first, then Dragapult, Alakazam, …). Each sub-step is gated; one change at a time.

- [ ] **R1. Global rules (phase 1).** For each deck: official sample → `agent/<archetype>_policy.py` +
      `deck_tech` entry; L0 smoke + L1 `gate_vs_public.py` / deck-specific gate — record per-opponent WR baseline.
  - [ ] Lucario: `lucario_policy.py` + `LUCARIO_TECH` — baseline gate vs 10 real-field decks.
  - [x] Dragapult: `dragapult_agent.py` — ladder **850.5 μ** (ref **53950779**) — **best so far**; pin Final slot.
  - [x] Dragapult Phase 2: empty-bench guard (`dragapult_bench_guard.py`); gate `scripts/gate_dragapult.py` tracks loss reasons; v3 tarball via `package_dragapult.py`.
  - [x] Dragapult v3 ladder probe: ref **53989933** submitted 2026-06-23 19:44 UTC — await ladder μ vs **850.5** bar (53950779).
  - [ ] **Beat 850.5 μ** — every upload/train gate; field top ~1350 is the real target.
  - [ ] Alakazam: port or re-gate imported best5 pilot on `top_mined_alakazam.csv`.
- [ ] **R2. Matchup levers (phase 2).** Wire `agent/matchup_levers.py` into `lucario_policy.py`;
      research in `data/MATCHUP_PLAYBOOK.md`. One lever per PR; re-gate weak matchups.
  - [x] Wire levers into `lucario_policy.py` (Boss/PPP/Lillie/setup/Solrock/Snover plan).
  - [ ] Lucario vs Abomasnow (0% train eval) — **gate** `scripts/gate_lucario_matchups.py`.
  - [ ] Lucario vs Trevenant — `avoid_ko_trevenant_setup`, Boss Phantump; re-gate.
  - [ ] Mirror / Alakazam — Boss on setup Pokémon (Riolu, Abra).
- [ ] **R3. Field mixture (phase 3).** Only after R1+R2 floor stable:
  - [ ] `scripts/update_from_kaggle.py` → leaderboard snapshot on user machine.
  - [ ] Harden `scripts/update_opponent_tracker.py` → `report/OPPONENT_DECK_DISTRIBUTION.md`.
  - [ ] Weighted gate: `E[win] = Σ share(a)·WR(ours,a)`; optional weighted opponent sampling in field RL.

**Deferred until R1–R2 pass:** weighting Lucario field RL cycles by meta share; upload Slot 2/3 picks from mixture alone. **Dragapult field RL+MCTS** — Lucario v5 **complete** (46.1% field champ); may start after v5 lessons applied.

---

## Foundation (must come first — every pillar depends on it)

- [ ] **F1. `core/` model + prove the foundation.**
  - [ ] `core/cards.py` — typed registry from `data/EN_Card_Data.csv`.
  - [ ] `core/engine.py` — wrapper over local `cg` engine (`data/sim/sample_submission/cg/`).
  - [ ] `core/obs.py` + `tests/test_information_model.py` — **empirically verify** opponent hand =
        count only, deck = count only, prizes face-down (RULINGS Part 4). *Needs Python ≥3.11.*
  - [ ] `core/rules_notes.md` — consolidated verified rules digest.
- [ ] **F2. `eval/` harness + `field/` registry.**
  - [ ] Move `agent_decks/{real_*,top_mined_*}` → `field/decks/`; build `field/registry.json`.
  - [ ] `eval/harness.py` (seeded, side-swapped, Wilson CI) + `eval/gates.py` (L0–L3, real-field only).
  - [ ] **Re-measure the current spine on the real field** — establish the true ~668 floor with metadata.
- [ ] **F3. Migrate + freeze the spine.** Move `agent/` → `agents/`, fix imports + packager, and
      **confirm the smoke test passes** (Python ≥3.11) so we reproduce ~633–668. This is the
      shippable baseline. *(Until F3, the spine stays in `agent/` — Ruling R7.)*

## Episode data → meta (the golden ticket; runs on user's machine)

- [ ] **D1. `episodes/pull.py`** (from `scripts/update_from_kaggle.py`): leaderboard, our
      submissions, new replays. **User runs this — sandbox has no Kaggle egress.**
- [ ] **D2. `episodes/parse.py` + `store/`** — replays → per-game records (one schema).
- [ ] **D3. `meta/build_map.py` + `whatbeatswhat.py`** — archetype × archetype win matrix, field
      shares, expected-WR-vs-mixture ranking. First dated `meta/reports/meta_YYYYMMDD.md`.

## Decision policy (Pillar 3 — the ceiling; each stage gated vs the spine)

- [ ] **P1. Pilot spine** consolidated/clean in `agents/` (the floor). *(= F3.)*
- [ ] **P2. Bounded our-side lookahead** via engine `search_*` under a strong `board_value`.
- [ ] **P3. Determinized opponent search (PIMC)** — sample K opponent hands/decks consistent with
      public info + meta prior; average the lookahead.
- [ ] **P4. ISMCTS** — only if PIMC's known weaknesses cost measurable μ.
- [ ] **P5. Learned belief/opponent prior** from `episodes/store` (the only ML role Ruling R3
      currently endorses, because search gates it).

## Deck discovery (Pillar 4 — after the pilot floor ships)

- [ ] **K1. Objective + scoping** — maximize `E[win vs field mixture]` for a fixed pilot, within a
      type-coherent shell. Best-arm identification (successive halving / SPRT), not blind GA.

## Orchestration (Pillar 5)

- [ ] **O1. Daily loop**: pull → parse → meta → refresh field/prior → re-gate champion + contenders
      → surface the single best next submission. `/schedule` once trusted.

---

## Done log
_(move completed top-level steps here with a date)_
- 2026-06-24: **Lucario v5 final submitted** — ref **53995982**, 25-cycle `model_best.pth` @ 46.1% field; validation 600.0 μ.
- 2026-06-23: **Lucario v5 field RL+MCTS DONE** — 25/25 cycles, `model_best.pth` @ **46.1%** field eval (cycle 21); prior probe 53978119 @ 43.5% → 431.9 μ.
- 2026-06-23: **Dragapult Phase 2 bench guard** — `dragapult_bench_guard.py`, gate loss-reason tracking, `dist/candidates/dragapult_ex_sample.tar.gz` v3; Dragapult field RL deferred until Lucario v5 train completes.
- 2026-06-22 (S44e): **Dragapult 850.5 μ best so far** (ref 53950779) — bar to beat; pin Final slot; target > 850.5.
- 2026-06-22 (S44d): **R11 rules-before-mixture** — phases 1–3 in ARCHITECTURE/TASKS/RULINGS; opponent tracker draft; next: Lucario global gate + Abomasnow lever.
- 2026-06-22 (S44c): **Lucario field RL+MCTS stack** — runtime, trainer, policy wrapper; committed `251da2b`; 5-cycle CPU train → `rl_mcts_field/lucarioex_v1/`.
- 2026-06-22 (S44b): **Dragapult ex baseline** — `agent/dragapult_agent.py`, `agent_decks/dragapult_ex_sample.csv`, `scripts/gate_dragapult.py`; local gate 78–88% vs pilot brains (filter only).
- 2026-06-22 (S44): repo reset — RULINGS/ARCHITECTURE/STATE written, 532→~100 files, spine preserved.
