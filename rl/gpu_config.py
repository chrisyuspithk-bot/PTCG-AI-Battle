"""GPU-safe defaults and checkpoint paths for local RL training.

Tuned for NVIDIA GeForce RTX 4070 Ti SUPER (16 GB VRAM, CUDA). Policy networks
are small MLPs; the cabt simulator runs on CPU in worker processes — GPU accelerates
forward/backward only, which is the right split for this project.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_DIR = ROOT / "report" / "rl_deck_campaign"
POLICY_CKPT_DIR = CAMPAIGN_DIR / "policy_checkpoints"
POLICY_LATEST = ROOT / "agent" / "models" / "rl_policy_campaign.zip"
CAMPAIGN_JSON = CAMPAIGN_DIR / "checkpoint.json"
DECK_GA_JSON = CAMPAIGN_DIR / "deck_ga.json"


def detect_hardware() -> dict:
    info: dict = {
        "device": "cpu",
        "gpu_name": None,
        "vram_gb": None,
        "cuda_available": False,
    }
    try:
        import torch

        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            props = torch.cuda.get_device_properties(0)
            info["device"] = "cuda"
            info["gpu_name"] = props.name
            info["vram_gb"] = round(props.total_memory / (1024**3), 1)
    except ImportError:
        pass
    return info


def training_defaults(hardware: dict | None = None) -> dict:
    """Conservative-but-fast settings for 4070 Ti SUPER class GPUs."""
    hw = hardware or detect_hardware()
    vram = hw.get("vram_gb") or 0.0
    cuda = hw.get("cuda_available", False)

    if cuda and vram >= 12:
        return {
            "device": "cuda",
            "n_envs": 6,
            "n_steps": 512,
            "batch_size": 256,
            "n_epochs": 4,
            "learning_rate": 3e-4,
            "checkpoint_freq": 10_000,
            "deck_workers": 4,
            "notes": "GPU policy + CPU sim workers; ~6 parallel envs for 12–16GB",
        }
    if cuda:
        return {
            "device": "cuda",
            "n_envs": 4,
            "n_steps": 256,
            "batch_size": 128,
            "n_epochs": 4,
            "learning_rate": 3e-4,
            "checkpoint_freq": 10_000,
            "deck_workers": 4,
            "notes": "Reduced batch for smaller VRAM",
        }
    return {
        "device": "cpu",
        "n_envs": 2,
        "n_steps": 256,
        "batch_size": 64,
        "n_epochs": 4,
        "learning_rate": 3e-4,
        "checkpoint_freq": 5_000,
        "deck_workers": 2,
        "notes": "CPU fallback",
    }


def apply_torch_safety() -> None:
    """Avoid thread oversubscription when multiprocessing envs."""
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    try:
        import torch

        torch.set_num_threads(1)
        if torch.cuda.is_available():
            # Leave headroom — do not pin memory pools aggressively.
            torch.cuda.empty_cache()
    except ImportError:
        pass


def load_campaign_state() -> dict:
    if CAMPAIGN_JSON.exists():
        return json.loads(CAMPAIGN_JSON.read_text(encoding="utf-8"))
    return {}


def save_campaign_state(state: dict) -> None:
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
    CAMPAIGN_JSON.write_text(json.dumps(state, indent=2), encoding="utf-8")


def policy_timesteps_done(state: dict) -> int:
    return int(state.get("policy_timesteps_done", 0))


def policy_steps_for_cycle(state: dict, cycle: int) -> int:
    by_cycle = state.get("policy_steps_by_cycle") or {}
    return int(by_cycle.get(str(cycle), 0))


def set_policy_steps_for_cycle(state: dict, cycle: int, steps: int) -> None:
    by_cycle = state.setdefault("policy_steps_by_cycle", {})
    by_cycle[str(cycle)] = int(steps)


def deck_generation_done(state: dict) -> int:
    return int(state.get("deck_generation_done", 0))


def migrate_campaign_state(state: dict, *, timesteps_per_cycle: int, total_cycles: int) -> dict:
    """Upgrade legacy checkpoint.json fields without breaking in-flight runs."""
    if "policy_steps_by_cycle" not in state:
        per = max(1, timesteps_per_cycle)
        done = policy_timesteps_done(state)
        by_cycle: dict[str, int] = {}
        full_cycles = min(total_cycles, done // per)
        for i in range(full_cycles):
            by_cycle[str(i)] = per
        remainder = done - full_cycles * per
        if remainder and full_cycles < total_cycles:
            by_cycle[str(full_cycles)] = remainder
        state["policy_steps_by_cycle"] = by_cycle

    if "policy_cycles_done" not in state:
        legacy = int(state.get("cycles_done", 0))
        per = max(1, timesteps_per_cycle)
        inferred = min(total_cycles, policy_timesteps_done(state) // per)
        state["policy_cycles_done"] = max(legacy, inferred)

    if "deck_cycles_done" not in state:
        # cycles_done mixed policy+deck progress; deck phase tracks its own counter.
        state["deck_cycles_done"] = 0

    return state
