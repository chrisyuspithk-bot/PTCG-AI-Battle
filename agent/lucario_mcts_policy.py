"""Submission wrapper for the Mega Lucario RL+MCTS checkpoint.

The heavyweight model/search code lives in ``agent.lucario_mcts_runtime`` and is
kept mechanically aligned with ``notebooks/lucario/lucario_rl_mcts.py``. This
wrapper is the safe competition surface: load ``model_best.pth`` when available,
run deterministic MCTS, and fall back to RuleCore if Torch/Search/model loading
fails for any reason.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path

from agent.agent import HeuristicScorer, load_deck
from agent.bench_guard import bench_critical
from agent.lucario_policy import LucarioScorer, is_lucario_deck


DEFAULT_SEARCH_COUNT = 12


class LucarioMCTSScorer(HeuristicScorer):
    """Torch/MCTS scorer with a legal deterministic fallback."""

    def __init__(
        self,
        deck_path: str | None = None,
        model_path: str | None = None,
        meta_path: str | None = None,
        rng=None,
    ) -> None:
        super().__init__(rng=rng)
        deck_ids = load_deck(deck_path) if deck_path else []
        if is_lucario_deck(deck_ids):
            self._fallback = LucarioScorer(rng=rng, deck_path=deck_path)
        else:
            from agent.rule_core import RuleCoreScorer

            self._fallback = RuleCoreScorer(rng=rng, deck_path=deck_path)
        self._rng = rng if rng is not None else random.Random(0)
        self._ready = False
        self._rt = None
        self._torch = None
        self._model = None
        self._deck = load_deck(deck_path) if deck_path else []

        if not self._deck:
            self._deck = list(getattr(_safe_runtime(), "LUCARIO_DECK", []))
        self._load_model(model_path, meta_path)

    def _load_model(self, model_path: str | None, meta_path: str | None) -> None:
        try:
            import torch
            from agent import lucario_mcts_runtime as rt

            search_count = int(os.environ.get("LUC_SUBMIT_SEARCH_COUNT", DEFAULT_SEARCH_COUNT))
            rt.SEARCH_COUNT = max(1, search_count)

            cfg = _read_model_config(meta_path)
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = rt.MyModel(
                cfg.get("LUC_D_MODEL", cfg.get("D_MODEL", rt.D_MODEL)),
                cfg.get("LUC_HEADS", cfg.get("NUM_HEADS", rt.NUM_HEADS)),
                cfg.get("LUC_D_FF", cfg.get("D_FF", rt.D_FF)),
                cfg.get("LUC_ENC_LAYERS", cfg.get("ENC_LAYERS", rt.ENC_LAYERS)),
                cfg.get("LUC_DEC_LAYERS", cfg.get("DEC_LAYERS", rt.DEC_LAYERS)),
            ).to(device)
            if model_path:
                state = torch.load(_resolve_existing(model_path), map_location=device)
                model.load_state_dict(state)
            model.eval()

            self._torch = torch
            self._rt = rt
            self._model = model
            self._ready = True
        except Exception:
            self._ready = False

    def choose(self, obs_dict, select, current, options):
        if bench_critical(obs_dict, select, current, options):
            return self._fallback.choose(obs_dict, select, current, options)
        if not self._ready or self._rt is None or self._torch is None or self._model is None:
            return self._fallback.choose(obs_dict, select, current, options)
        try:
            with self._torch.inference_mode():
                selected, _ = self._rt.mcts_agent(
                    obs_dict,
                    self._deck,
                    self._model,
                    add_noise=False,
                    temperature=0.0,
                )
            return selected
        except Exception:
            return self._fallback.choose(obs_dict, select, current, options)


def build_lucario_mcts_scorer(
    deck_path: str | None = None,
    model_path: str | None = None,
    meta_path: str | None = None,
    rng=None,
) -> LucarioMCTSScorer:
    return LucarioMCTSScorer(
        deck_path=deck_path,
        model_path=model_path,
        meta_path=meta_path,
        rng=rng,
    )


def _safe_runtime():
    try:
        from agent import lucario_mcts_runtime as rt

        return rt
    except Exception:
        return None


def _read_model_config(meta_path: str | None) -> dict:
    if not meta_path:
        return {}
    path = Path(meta_path)
    if not path.exists():
        return {}
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    cfg = meta.get("config", {})
    return cfg if isinstance(cfg, dict) else {}


def _resolve_existing(path: str) -> str:
    if os.path.exists(path):
        return path
    local = Path(__file__).resolve().parent / "models" / Path(path).name
    if local.exists():
        return str(local)
    return path
