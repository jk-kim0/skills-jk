# Hermes Agent Installation

This document records the local Hermes Agent installation status used with this repository.

## Install Method

Hermes Agent was installed from the official NousResearch repository with submodules:

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git ~/.hermes/hermes-agent
cd ~/.hermes/hermes-agent
./setup-hermes.sh
```

The setup wizard was not run during installation. It should be run separately when provider authentication and API keys are ready:

```bash
hermes setup
```

## Installed Paths

- Source checkout: `~/.hermes/hermes-agent`
- CLI command: `~/.local/bin/hermes`
- CLI target: `~/.hermes/hermes-agent/venv/bin/hermes`
- Python environment: `~/.hermes/hermes-agent/venv`

## Verified Version

The installed command reported, with the home directory normalized to `~`:

```text
Hermes Agent v0.10.0 (2026.4.16)
Project: ~/.hermes/hermes-agent
Python: 3.11.15
OpenAI SDK: 2.32.0
Up to date
```

The installed checkout was on `main` and described as:

```text
v2026.4.16-590-g5157f542
```

## Repository-Local Runtime

Hermes reads its runtime configuration from `HERMES_HOME/config.yaml`. For this repository, use the repository-local Hermes home:

```bash
HERMES_HOME="$PWD/.hermes" bash -lc 'set -a; source .hermes/.env; set +a; hermes'
```

`HERMES_HOME="$PWD/.hermes" ~/.local/bin/hermes doctor` verified that Hermes recognizes this repository's `.hermes/config.yaml`.

## Doctor Findings

Installation-level checks passed:

- Python `3.11.15` was available through the Hermes virtual environment.
- Required packages were installed.
- `~/.local/bin/hermes` pointed to the expected virtualenv entry point.
- `tinker-atropos` submodule support was installed.
- Built-in memory was active.

Remaining items are operational configuration, not installation failures:

- `hermes setup` has not been run.
- Nous Portal, OpenAI Codex, and Google Gemini auth are not logged in through Hermes.
- Provider API keys such as `OPENROUTER_API_KEY` are not configured.
- AWS Bedrock returned an IAM `AccessDeniedException` for `bedrock:ListFoundationModels`.
- Optional system dependencies such as `agent-browser` are not installed.
- Skills Hub has not been initialized; run `hermes skills list` when needed.

## Secret Policy

Do not write token values, API key values, session cookie values, or private credential values into this document.

Secret values belong in the personal 1Password item `Employee/skills-jk-hermes-local`. This repository may store non-sensitive references such as `.env` key names and `op://Employee/skills-jk-hermes-local/<KEY>` references.

When secrets change, materialize the local `.hermes/.env` file with:

```bash
bin/hermes-sync-env
```

Normal Hermes runs should read the local Git-ignored `.hermes/.env` file and should not call 1Password.
