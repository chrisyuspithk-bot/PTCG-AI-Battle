"""Evolutionary deck representation with legality + composition balance repair.

Mutations stay within archetype bands (energy / Pokémon / trainer counts) derived
from our pilot and meta pool decks — see rl/deck_profiles.json.
"""

from __future__ import annotations

import copy
import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from rl.deck_balance import (
    card_role,
    composition_of,
    infer_profile,
    rebalance_counts,
    summarize_deck,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_pool():
    import sys

    sys.path.insert(0, str(ROOT))
    from scripts.validate_deck import load_card_pool

    return load_card_pool()


def _validate(ids: list[int], pool) -> tuple[bool, list[str]]:
    import sys

    sys.path.insert(0, str(ROOT))
    from scripts.validate_deck import validate_deck

    errors, _ = validate_deck(ids, pool)
    return not errors, errors


def _ace_spec_ids(pool) -> set[int]:
    return {cid for cid, info in pool.items() if info.is_ace_spec}


def _energy_ids(pool) -> set[int]:
    return {cid for cid, info in pool.items() if info.is_basic_energy}


def _enforce_ace_spec(counts: Counter, pool, rng: random.Random) -> None:
    """At most one ACE SPEC card in the whole deck."""
    ace_pool = _ace_spec_ids(pool)
    present = [cid for cid in counts if cid in ace_pool and counts[cid] > 0]
    if len(present) <= 1 and all(counts[cid] <= 1 for cid in present):
        return
    keep = rng.choice(present) if present else None
    for cid in present:
        if cid == keep:
            counts[cid] = 1
        else:
            del counts[cid]


def _by_role(counts: Counter, pool, role: str) -> list[int]:
    return [cid for cid, n in counts.items() if n > 0 and cid in pool and card_role(pool, cid) == role]


@dataclass
class DeckGenome:
    """Deck as multiset of card IDs (60 total when valid)."""

    counts: Counter
    label: str = ""
    fitness: float = -1.0
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_deck(cls, deck: list[int], label: str = "") -> "DeckGenome":
        return cls(counts=Counter(deck), label=label)

    @classmethod
    def seed_population(
        cls,
        seed_paths: list[Path],
        size: int,
        rng: random.Random,
    ) -> list["DeckGenome"]:
        pop: list[DeckGenome] = []
        for path in seed_paths:
            deck = [int(x) for x in path.read_text().splitlines() if x.strip()]
            pop.append(cls.from_deck(deck, label=path.stem))
        while len(pop) < size:
            base = rng.choice(pop[: max(1, len(seed_paths))])
            child = base.mutate(rng)
            pop.append(child)
        return pop[:size]

    def to_list(self, rng: random.Random | None = None) -> list[int]:
        rng = rng or random.Random(0)
        cards: list[int] = []
        for cid, n in self.counts.items():
            cards.extend([cid] * n)
        rng.shuffle(cards)
        return cards[:60]

    def mutate(self, rng: random.Random, pool=None) -> "DeckGenome":
        pool = pool or _load_pool()
        profile = infer_profile(self.counts, pool)
        energy_ids = _energy_ids(pool)
        counts = copy.deepcopy(self.counts)
        comp = composition_of(counts, pool)

        # Balance-aware ops only: tune energy within band, swap same-role cards,
        # or trade energy <-> trainer when bands allow.
        ops = ["energy_tune", "trainer_swap", "pokemon_swap", "energy_trainer_trade"]
        op = rng.choice(ops)

        eid = next(iter(energy_ids)) if energy_ids else None

        if op == "energy_tune" and eid is not None:
            delta = rng.choice([-2, -1, 1, 2])
            new_e = comp.energy + delta
            if profile.energy[0] <= new_e <= profile.energy[1]:
                if delta > 0:
                    donors = _by_role(counts, pool, "trainer") + [
                        c for c in _by_role(counts, pool, "pokemon") if counts[c] > 1
                    ]
                    if donors:
                        for _ in range(delta):
                            d = rng.choice([c for c in donors if counts[c] > 0])
                            counts[d] -= 1
                            counts[eid] = counts.get(eid, 0) + 1
                else:
                    receivers = [c for c in _by_role(counts, pool, "trainer") if counts.get(c, 0) < 4]
                    if receivers:
                        for _ in range(-delta):
                            if counts.get(eid, 0) <= 0:
                                break
                            counts[eid] -= 1
                            r = rng.choice(receivers)
                            counts[r] = counts.get(r, 0) + 1

        elif op == "trainer_swap":
            trainers = _by_role(counts, pool, "trainer")
            if len(trainers) >= 2:
                a, b = rng.sample(trainers, 2)
                if counts[a] > 0 and counts.get(b, 0) < 4:
                    counts[a] -= 1
                    counts[b] = counts.get(b, 0) + 1

        elif op == "pokemon_swap":
            mons = _by_role(counts, pool, "pokemon")
            if len(mons) >= 2:
                a, b = rng.sample(mons, 2)
                if counts[a] > 0 and counts.get(b, 0) < 4:
                    counts[a] -= 1
                    counts[b] = counts.get(b, 0) + 1

        elif op == "energy_trainer_trade" and eid is not None:
            comp = composition_of(counts, pool)
            trainers = [c for c in _by_role(counts, pool, "trainer") if counts.get(c, 0) < 4]
            if comp.energy > profile.energy[0] and trainers:
                counts[eid] -= 1
                t = rng.choice(trainers)
                counts[t] = counts.get(t, 0) + 1
            elif comp.energy < profile.energy[1]:
                donors = [c for c in _by_role(counts, pool, "trainer") if counts[c] > 1]
                if donors:
                    d = rng.choice(donors)
                    counts[d] -= 1
                    counts[eid] = counts.get(eid, 0) + 1

        g = DeckGenome(counts=counts, label=f"mut_{self.label}")
        return g.repair(rng, pool, fallback=copy.deepcopy(self.counts))

    def repair(
        self,
        rng: random.Random,
        pool=None,
        *,
        fallback: Counter | None = None,
    ) -> "DeckGenome":
        pool = pool or _load_pool()
        profile = infer_profile(self.counts, pool)
        counts = copy.deepcopy(self.counts)

        for cid in list(counts.keys()):
            if cid not in pool:
                del counts[cid]
            elif counts[cid] <= 0:
                del counts[cid]
            elif not pool[cid].is_basic_energy and counts[cid] > 4:
                counts[cid] = 4

        _enforce_ace_spec(counts, pool, rng)
        counts = rebalance_counts(counts, pool, profile, rng)
        _enforce_ace_spec(counts, pool, rng)

        total = sum(counts.values())
        eid = next(iter(_energy_ids(pool)), None)
        if eid is not None and total != 60:
            counts[eid] = counts.get(eid, 0) + (60 - total)

        g = DeckGenome(counts=counts, label=self.label)
        ok, _ = _validate(g.to_list(rng), pool)
        if ok:
            return g

        if fallback is not None:
            return DeckGenome(counts=Counter(fallback), label=self.label)
        return DeckGenome(counts=Counter(self.counts), label=self.label)

    @staticmethod
    def crossover(a: "DeckGenome", b: "DeckGenome", rng: random.Random) -> "DeckGenome":
        pool = _load_pool()
        # Crossover only within matching archetype to avoid illegal composition mashups.
        prof_a = infer_profile(a.counts, pool)
        prof_b = infer_profile(b.counts, pool)
        if prof_a.name != prof_b.name:
            parent = a if rng.random() < 0.5 else b
            return parent.mutate(rng, pool)

        keys = set(a.counts.keys()) | set(b.counts.keys())
        counts: Counter = Counter()
        for k in keys:
            counts[k] = a.counts[k] if rng.random() < 0.5 else b.counts[k]
        child = DeckGenome(counts=counts, label=f"x_{a.label}_{b.label}")
        parent = a if rng.random() < 0.5 else b
        return child.repair(rng, pool, fallback=copy.deepcopy(parent.counts))

    def composition_summary(self, pool=None) -> str:
        return summarize_deck(self.counts, pool or _load_pool())
