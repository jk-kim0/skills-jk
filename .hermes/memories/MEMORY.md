User stores personal Hermes runtime secrets in 1Password item 'skills-jk-hermes-local' in the Private vault.
§
In the repo-local Hermes setup, `hermes gateway install/start/restart/status` are the supported service controls, and only one gateway instance should run per `HERMES_HOME`; additional `hermes gateway run` attempts with the same home compete or are refused.
§
In the skills-jk repository, the local `skills/` directory currently has 35 top-level discovered skills, plus one nested duplicate path under `skills/cc-codex-debate-review/skills/cc-codex-debate-review`. The repo's AGENTS rules require per-turn skill discovery from `skills/` and system skills.
§
In corp-web-japan, the user prefers local-only worktree configuration on their PC rather than shared repo changes; do not add scripts for this. Use repo-local git aliases instead, with worktrees under corp-web-japan/.worktrees.
§
In the skills-jk repo, portable Hermes state should live in tracked `.hermes/config.yaml`, tracked markdown memories under `.hermes/memories/`, tracked skills under both `.hermes/skills/` and the repo `skills/` tree; runtime artifacts like `.hermes/checkpoints/`, `.hermes/sessions/`, logs, `state.db*`, caches, and generated `.hermes/.env` should stay untracked/ignored.
§
For portable Hermes setups in skills-jk, session-like records should remain local to each machine/instance and should not be migrated between PCs; only durable memories and config should be synced.
§
In the skills-jk repo, PR creation uses the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` via `workflow_dispatch`; it is the preferred PR creation path for this repo.