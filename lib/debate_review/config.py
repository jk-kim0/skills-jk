import os
import yaml

_DEFAULT_CONFIG_PATH = os.path.expanduser(
    "~/workspace/skills-jk/config/cc-codex-debate-review.yml"
)


def load_config(path=None) -> dict:
    config_path = path or _DEFAULT_CONFIG_PATH
    with open(config_path) as f:
        return yaml.safe_load(f)
