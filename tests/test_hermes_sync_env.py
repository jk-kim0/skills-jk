from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path


def _write_fake_op(bin_dir: Path) -> None:
    script = """#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

args = sys.argv[1:]
if args[:2] != ['run', '--env-file']:
    print(f'unsupported args: {args}', file=sys.stderr)
    sys.exit(2)

env_file = Path(args[2])
if args[3] != '--':
    print(f'expected -- separator: {args}', file=sys.stderr)
    sys.exit(2)
cmd = args[4:]

env = os.environ.copy()
for line in env_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    key, value = line.split('=', 1)
    if value == 'op://Employee/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN':
        env[key] = '8600962995:AAHOoz80fcJZhOrevtNEK1Bo06RCXlSXGL0'
    else:
        env[key] = value

result = subprocess.run(cmd, env=env)
sys.exit(result.returncode)
"""
    op_path = bin_dir / "op"
    op_path.write_text(script)
    op_path.chmod(op_path.stat().st_mode | stat.S_IEXEC)


def test_sync_defaults_to_repo_local_hermes_env(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / ".hermes").mkdir()
    (repo / ".hermes" / "config.yaml").write_text("agent:\n  name: hermes\n")
    (repo / "bin").mkdir()
    (repo / ".env.1password").write_text(
        "TELEGRAM_BOT_TOKEN=op://Employee/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN\n"
    )

    source_script = Path(__file__).resolve().parents[1] / "bin" / "hermes-sync-env"
    target_script = repo / "bin" / "hermes-sync-env"
    shutil.copy2(source_script, target_script)
    target_script.chmod(target_script.stat().st_mode | stat.S_IEXEC)

    fake_bin = repo / "fake-bin"
    fake_bin.mkdir()
    _write_fake_op(fake_bin)

    env = os.environ.copy()
    env.pop("HERMES_HOME", None)
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    subprocess.run([str(target_script)], cwd=repo, env=env, check=True)

    hermes_env = repo / ".hermes" / ".env"
    assert hermes_env.exists(), "sync should write the repo-local Hermes env file by default"
    assert (
        "TELEGRAM_BOT_TOKEN=8600962995:AAHOoz80fcJZhOrevtNEK1Bo06RCXlSXGL0"
        in hermes_env.read_text()
    )

    root_env = repo / ".env"
    assert not root_env.exists(), "repo root .env should not be the default target in repo-local mode"
