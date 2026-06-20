"""Time-budgeted search-augmented OptionScorer with heuristic fallback.

Track A design: keep the full heuristic policy as the default brain and only
layer shallow search on high-leverage card picks (promotion / switch). The prior
evalfn rerank on MAIN skipped EVOLVE/ATTACH and regressed badly vs heuristic.
"""

from __future__ import annotations

import json
import time

from agent.agent import (
    CTX_SETUP_ACTIVE_POKEMON,
    CTX_SETUP_BENCH_POKEMON,
    CTX_SWITCH,
    CTX_TO_ACTIVE,
    HeuristicScorer,
    SEL_CARD,
)

SEARCH_BUDGET_MS = 200
HIGH_LEVERAGE_CONTEXTS = {
    CTX_TO_ACTIVE,
    CTX_SWITCH,
    CTX_SETUP_ACTIVE_POKEMON,
    CTX_SETUP_BENCH_POKEMON,
}


class SearchScorer(HeuristicScorer):
    """Heuristic baseline + optional cg search_* on promotion/switch picks."""

    def __init__(self, rng=None, budget_ms: float = SEARCH_BUDGET_MS) -> None:
        super().__init__(rng=rng)
        self._fallback = HeuristicScorer(rng=rng)
        self._budget_ms = budget_ms
        self._lib = None
        self._battle_ptr = None

    def choose(self, obs_dict, select, current, options):
        if not options:
            return []
        try:
            context = select.get("context")
            if (
                select.get("type") == SEL_CARD
                and context in HIGH_LEVERAGE_CONTEXTS
                and int(select.get("minCount", 1) or 0) <= 1
            ):
                deadline = time.monotonic() + self._budget_ms / 1000.0
                picked = self._ctypes_search(obs_dict, options, deadline)
                if picked is not None:
                    return picked
        except Exception:
            pass
        return self._fallback.choose(obs_dict, select, current, options)

    def _ensure_engine(self) -> bool:
        if self._lib is not None:
            return True
        try:
            from cg.sim import Battle, lib  # type: ignore

            self._lib = lib
            self._battle_ptr = Battle.battle_ptr
            return self._battle_ptr is not None
        except Exception:
            return False

    def _ctypes_search(self, obs_dict, options, deadline) -> list[int] | None:
        """Best-effort wrapper around cg search_*; returns None on failure."""
        if not self._ensure_engine() or time.monotonic() >= deadline:
            return None
        try:
            lib = self._lib
            ptr = self._battle_ptr
            if lib is None or ptr is None:
                return None
            begin_input = obs_dict.get("search_begin_input", "")
            if not begin_input:
                return None
            n_opts = len(options)
            if n_opts <= 0:
                return None
            ctypes = __import__("ctypes")
            idx_arr = (ctypes.c_int * n_opts)(*range(n_opts))
            out_idx = (ctypes.c_int * 1)(0)
            out_score = (ctypes.c_int * 1)(0)
            out_depth = (ctypes.c_int * 1)(0)
            out_nodes = (ctypes.c_int * 1)(0)
            out_time = (ctypes.c_int * 1)(0)
            remaining_ms = max(1, int((deadline - time.monotonic()) * 1000))
            search_ptr = lib.SearchBegin(
                ptr,
                begin_input.encode("ascii"),
                remaining_ms,
                idx_arr,
                out_idx,
                out_score,
                out_depth,
                out_nodes,
                out_time,
                n_opts,
            )
            if not search_ptr:
                return None
            handle = int(search_ptr, 16) if isinstance(search_ptr, str) else 0
            try:
                step = lib.SearchStep(ptr, handle, out_idx, 1)
                if step:
                    data = json.loads(step.decode()) if isinstance(step, bytes) else {}
                    pick = data.get("index", out_idx[0])
                    if isinstance(pick, int) and 0 <= pick < n_opts:
                        return [pick]
                if 0 <= out_idx[0] < n_opts:
                    return [out_idx[0]]
            finally:
                lib.SearchEnd(ptr)
                if handle:
                    lib.SearchRelease(ptr, handle)
        except Exception:
            return None
        return None
