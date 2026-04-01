import os
import yaml

_DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config.yml")
)

_USER_OVERRIDE_PATH = os.path.expanduser(
    "~/.claude/debate-review-config.yml"
)


def load_config(path=None) -> dict:
    config_path = path or _DEFAULT_CONFIG_PATH
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        if path:
            raise  # explicit --config path should exist
        config = {}

    # Apply user-level overrides from ~/.claude/debate-review-config.yml
    try:
        with open(_USER_OVERRIDE_PATH) as f:
            overrides = yaml.safe_load(f) or {}
        config.update(overrides)
    except FileNotFoundError:
        pass

    return config
