"""MaskablePPO RL training for Track B (training-only).

Trains on a fixed player deck vs benchmark or pool opponents.
Output: agent/models/rl_policy.zip (+ report/rl_train/checkpoint.json metadata).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHECKPOINT = ROOT / "report" / "rl_train" / "checkpoint.json"
MODEL_OUT = ROOT / "agent" / "models" / "rl_policy"


def train_maskable_ppo(
    timesteps: int,
    n_envs: int,
    resume: bool,
    deck_path: Path,
    opponents: str,
    seed: int,
) -> dict:
    try:
        from sb3_contrib import MaskablePPO
        from stable_baselines3.common.callbacks import CheckpointCallback
    except ImportError as exc:
        return {"status": "skipped", "reason": f"missing sb3-contrib: {exc}"}

    from rl.env_factory import deck_slug, load_opponent_decks, make_env_thunk, resolve_deck_path
    from rl.gpu_config import POLICY_CKPT_DIR, apply_torch_safety, detect_hardware, training_defaults

    import torch

    apply_torch_safety()
    defaults = training_defaults(detect_hardware())
    device = defaults["device"]
    n_envs = n_envs or defaults["n_envs"]
    deck = resolve_deck_path(deck_path)
    slug = deck_slug(deck)

    model_path = MODEL_OUT
    POLICY_CKPT_DIR.mkdir(parents=True, exist_ok=True)
    can_resume = resume and model_path.with_suffix(".zip").exists()

    meta_path = CHECKPOINT
    if can_resume and meta_path.exists():
        try:
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            if prev.get("deck") and Path(prev["deck"]).resolve() != deck.resolve():
                return {
                    "status": "error",
                    "reason": f"resume deck mismatch: checkpoint={prev.get('deck')} requested={deck}",
                }
            if prev.get("opponents") and prev["opponents"] != opponents:
                return {
                    "status": "error",
                    "reason": f"resume opponents mismatch: checkpoint={prev.get('opponents')} requested={opponents}",
                }
        except (json.JSONDecodeError, OSError):
            pass

    try:
        if n_envs > 1:
            from stable_baselines3.common.vec_env import SubprocVecEnv

            env = SubprocVecEnv([
                make_env_thunk(deck, opponents=opponents, seed=seed + i * 1000 + 7)
                for i in range(n_envs)
            ])
        else:
            env = make_env_thunk(deck, opponents=opponents, seed=seed)()

        if can_resume:
            model = MaskablePPO.load(str(model_path), env=env, device=device)
        else:
            model = MaskablePPO(
                "MlpPolicy", env, verbose=0, n_steps=defaults["n_steps"],
                batch_size=defaults["batch_size"], device=device,
            )
        ckpt = CheckpointCallback(
            save_freq=max(1, defaults["checkpoint_freq"] // max(1, n_envs)),
            save_path=str(POLICY_CKPT_DIR),
            name_prefix="rl_policy",
        )
        model.learn(total_timesteps=timesteps, reset_num_timesteps=not can_resume, callback=ckpt)
        CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(model_path))
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return {
            "status": "ok",
            "timesteps": timesteps,
            "model": str(model_path.with_suffix(".zip")),
            "device": device,
            "deck": str(deck),
            "deck_slug": slug,
            "opponents": opponents,
            "n_envs": n_envs,
            "n_opponents": len(load_opponent_decks(opponents)),
        }
    except Exception as exc:
        return {"status": "error", "reason": f"{type(exc).__name__}: {exc}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timesteps", type=int, default=2048)
    parser.add_argument("--n-envs", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--deck", default=str(ROOT / "agent" / "deck.csv"), help="Fixed player deck for this policy")
    parser.add_argument(
        "--opponents",
        choices=("benchmark", "pool"),
        default="benchmark",
        help="Opponent deck set (benchmark=suite.json, pool=6 meta pool_*.csv)",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    result = train_maskable_ppo(
        args.timesteps,
        args.n_envs,
        args.resume,
        Path(args.deck),
        args.opponents,
        args.seed,
    )
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in ("ok", "skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
