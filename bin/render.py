import argparse
import json
import logging
import shutil
from pathlib import Path

from assistive_gym.learn import render_policy

from riddbot.gym import make_env


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--model_path", type=Path)
    group.add_argument("-c", "--config_path", type=Path)
    return parser.parse_args()


def get_ckpt_path(model_path: Path) -> Path:
    ckpt_path_glob = model_path.glob("*/*/checkpoint_*/checkpoint-*")
    ckpt_path = next(ckpt_path_glob).absolute()
    logger.info(f"Policy will be loaded from {ckpt_path}")
    return ckpt_path


def read_config(config_path: Path) -> dict:
    logger.info(f"Reading config from {config_path}")
    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def main():
    args = parse_args()

    if args.model_path is not None:
        ckpt_path = get_ckpt_path(args.model_path)
        config_path = (args.model_path / "config.json").absolute()
    else:
        ckpt_path = ""
        config_path = args.config_path.absolute()

    config = read_config(config_path)

    env_name, env = make_env(reward_weights=config["reward_weights"])

    filename = render_policy(
        env,
        env_name,
        algo="ppo",
        colab=True,
        seed=config["seed"],
        policy_path=str(ckpt_path),
        extra_configs=dict(env_config=dict(reward_weights=config["reward_weights"])),
    )

    if args.model_path is not None:
        new_filepath = (args.model_path / filename).absolute()
        shutil.move(filename, new_filepath)
        filename = new_filepath

    logger.info(f"Rendered at {filename}")


if __name__ == "__main__":
    main()
