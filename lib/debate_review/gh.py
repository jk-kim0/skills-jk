import json
import os
import subprocess


def gh(*args) -> str:
    env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GH_TOKEN")}
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"gh {' '.join(args)} failed (exit {result.returncode}):\n{result.stderr}"
        )
    return result.stdout


def gh_json(*args) -> dict | list:
    output = gh(*args)
    return json.loads(output)
