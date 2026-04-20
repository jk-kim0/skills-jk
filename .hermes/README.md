# Hermes Agent Configuration

This directory stores repository-local Hermes agent configuration and long-lived memory.

## Layout

- `config.yaml`: Hermes storage and Git policy for this repository. Run with
  `HERMES_HOME="$PWD/.hermes"` when this repository-local configuration should
  be the active Hermes home.
- `memories/`: Long-lived memory that is intentionally tracked by Git.
- `sessions/`: Runtime session state, transcripts, locks, and cache files. This path is ignored by Git.

## Secret Store

Hermes uses 1Password as the secret store. The primary method is a personal 1Password item:

- Vault: `Employee`
- Item: `skills-jk-hermes-local`
- Item type: Secure Note
- Field names: use the same names as `.env` keys.

Store actual secret values only in that 1Password item. Keep secret references in the local `.env.1password` file, then materialize a local `.env` only when secrets change:

```bash
bin/hermes-sync-env
```

This is the only step that should require 1Password authorization. Normal Hermes runs read the local Git-ignored `.env` file and should not call 1Password:

```bash
HERMES_HOME="$PWD/.hermes" bash -lc 'set -a; source .env; set +a; hermes'
```

Example `.env.1password` content:

```dotenv
OPENAI_API_KEY=op://Employee/skills-jk-hermes-local/OPENAI_API_KEY
GITHUB_TOKEN=op://Employee/skills-jk-hermes-local/GITHUB_TOKEN
HERMES_AGENT_TOKEN=op://Employee/skills-jk-hermes-local/HERMES_AGENT_TOKEN
```

Local `.env` and `.env.1password` files are ignored by Git. `.env` contains plaintext secret values after sync and must stay local. Keep `.env.1password.example` tracked when a non-sensitive template is useful.

1Password Environments are deferred until they become available and useful for this workflow.

## Memory Safety

- `.hermes/memories/` is a Git-tracked long-term memory store.
- Do not store secret values in memories: token values, API key values, session cookie values, private credential values, customer data, or personal sensitive data.
- Store non-sensitive references that help locate those values, such as environment variable names, `.env` key names, config key names, 1Password vault names, 1Password item titles, 1Password secret references, and rotation/check instructions.
- Temporary execution state, raw transcripts, lock files, and cache files must go under `.hermes/sessions/`.
- `.hermes/sessions/` is ignored by Git.
- Before committing memory changes, review them with:

```bash
git diff -- .hermes/memories
```

## Memory Commit Routine

Commit memory updates as a deliberate maintenance step:

```bash
git status --short .hermes/memories
git diff -- .hermes/memories
git add .hermes/memories
git commit -m "chore(hermes): update memories"
```
