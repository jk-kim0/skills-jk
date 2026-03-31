import os
import yaml

_DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config.yml")
)


def load_config(path=None) -> dict:
    config_path = path or _DEFAULT_CONFIG_PATH
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        if path:
            raise  # explicit --config path should exist
        return {}
