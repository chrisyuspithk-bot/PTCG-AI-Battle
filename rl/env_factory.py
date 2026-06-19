"""Shared CabtEnv construction for Track B RL training and distillation."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

ROOT = Path(__file__).resolve().parents[1]

OpponentMode = Literal["benchmark", "pool"]


def resolve_deck_path(deck_path: str | Path | None) -> Path:
    path = Path(deck_path or ROOT / "agent" / "deck.csv")
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"deck not found: {path}")
    return path


def _load_deck_ids(path: Path) -> list[int]:
    return [int(x) for x in path.read_text().splitlines() if x.strip()]


def load_opponent_decks(mode: OpponentMode = "benchmark") -> list[list[int]]:
    """Return opponent deck lists for training rollouts."""
    if mode == "benchmark":
        from rl.benchmark import load_suite

        return [d.load() for d in load_suite()]
    if mode == "pool":
        from scripts.arena import pool_decks

        decks = list(pool_decks().values())
        if not decks:
            raise FileNotFoundError("no pool_*.csv opponents found under agent_decks/")
        return decks
    raise ValueError(f"unknown opponent mode: {mode}")


def make_masked_cabt_env(
    deck_path: str | Path,
    *,
    opponents: OpponentMode = "benchmark",
    seed: int = 0,
):
    """Return ActionMasker-wrapped CabtEnv for MaskablePPO."""
    import numpy as np
    from sb3_contrib.common.wrappers import ActionMasker

    from rl.cabt_env import CabtEnv

    deck = resolve_deck_path(deck_path)
    opp_decks = load_opponent_decks(opponents)

    def mask_fn(env):
        info = getattr(env.unwrapped, "_last_info", {})
        mask = info.get("action_mask") if isinstance(info, dict) else None
        if mask is None:
            return None
        return np.asarray(mask, dtype=bool)

    class MaskedCabtEnv(CabtEnv):
        def reset(self, *, seed=None, options=None):
            obs, info = super().reset(seed=seed, options=options)
            self._last_info = info
            return obs, info

        def step(self, action):
            obs, reward, terminated, truncated, info = super().step(action)
            self._last_info = info
            return obs, reward, terminated, truncated, info

    env = MaskedCabtEnv(
        deck_path=deck,
        opponent_decks=opp_decks,
        seed=seed,
    )
    return ActionMasker(env, mask_fn)


def make_env_thunk(
    deck_path: str | Path,
    *,
    opponents: OpponentMode = "benchmark",
    seed: int = 0,
) -> Callable[[], object]:
    """SubprocVecEnv factory: each worker gets a distinct seed offset."""

    def _thunk():
        return make_masked_cabt_env(deck_path, opponents=opponents, seed=seed)

    return _thunk


def deck_slug(deck_path: str | Path) -> str:
    """Stable short name from deck path (e.g. a2_kyogre_33_energy)."""
    path = resolve_deck_path(deck_path)
    name = path.stem
    for prefix in ("pool_", "a2_", "a3_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name.replace("_", "-")[:32].strip("-") or "deck"
