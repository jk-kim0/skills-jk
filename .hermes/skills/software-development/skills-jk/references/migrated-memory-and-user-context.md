# Migrated memory and user context for skills-jk

These entries were moved out of global Hermes memory/user profile because they are repository- or platform-specific. Keep them here or split them into narrower workflow skills as they evolve.


## From MEMORY.md


### MEMORY entry 1

In the skills-jk repo, Hermes runtime/setup facts are: portable state lives in tracked `.hermes/config.yaml`, `.hermes/memories/`, `.hermes/skills/`, and repo `skills/`; session-like records remain machine-local; runtime artifacts such as checkpoints, sessions, logs, caches, generated `.hermes/.env`, and other transient state stay untracked; the active runtime in this setup uses `HERMES_HOME=~/workspace/skills-jk/.hermes`, with session files under `.hermes/sessions`; the local Hermes CLI is git-installed under `~/.hermes/hermes-agent` and exposed via `~/.local/bin/hermes`.


### MEMORY entry 2

In the skills-jk repo, PR creation uses the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` via `workflow_dispatch`; it is the preferred PR creation path for this repo.


### MEMORY entry 3

Hermes session files for this setup are stored under ~/workspace/skills-jk/.hermes/sessions, and direct file inspection there can reveal recent Telegram sessions beyond what session_search returns.


### MEMORY entry 4

In the repo-local Hermes setup at ~/workspace/skills-jk/.hermes/config.yaml, mcp_servers.chrome-devtools is configured with npx chrome-devtools-mcp@latest and Hermes reports it enabled via `hermes mcp list`.


### MEMORY entry 5

The user wants the repeated repo-local stale-branch/worktree audit workflow encoded as a reusable skills-jk skill: classify non-open-PR branches by synthetic squash of current local state vs latest origin/main, test disposable rebase onto latest main, preserve meaningful local patches, and delete only clearly stale branches/worktrees.


### MEMORY entry 6

In the repo-local Hermes config at ~/workspace/skills-jk/.hermes/config.yaml, checkpoints.enabled is currently false while stale historical checkpoint repos can still remain on disk under .hermes/checkpoints until manually deleted.


### MEMORY entry 7

In the repo-local Hermes setup under ~/workspace/skills-jk/.hermes/, the user wants the openai-codex credential labeled `gpt4` to be prioritized first in the credential pool (ahead of gpt3/gpt8/gpt11) while keeping `credential_pool_strategies.openai-codex=fill_first`.


### MEMORY entry 8

In skills-jk repeated local-sweep cleanup, if requested scoped files (.hermes/config.yaml, .hermes/memories/MEMORY.md, USER.md) are already identical to latest main but the session creates skill-library residue, split that into a narrow follow-up PR instead of claiming the scoped PR changed.


## From USER.md


### USER entry 1

User does not use /rollback and prefers Hermes checkpoints disabled unless explicitly needed.
