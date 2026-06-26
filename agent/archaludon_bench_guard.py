"""Empty-bench guard for Archaludon ex / Cinderace pilot (R7).

Wraps agent/empty_bench_guard.py with Metal-line deck priorities.
"""

from __future__ import annotations

try:
    from empty_bench_guard import apply_bench_guard as _apply
except ImportError:
    from agent.empty_bench_guard import apply_bench_guard as _apply

# Duraludon line first, then Relicanth (only basics in this list).
_BENCH_PRIORITY = (169, 57)


def apply_bench_guard(obs_dict: dict, selection: list[int]) -> list[int]:
    return _apply(obs_dict, selection, _BENCH_PRIORITY)
