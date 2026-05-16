---
name: codex
description: Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR reviews, and batch issue fixing. Requires the codex CLI and a git repository.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI API key configured
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## Config troubleshooting

Codex CLI config is commonly at `~/.codex/config.toml`. For Codex CLI 0.130.0 model/service-tier details and a known-good gpt-5.5 config, see `references/codex-cli-0.130-model-and-service-tier.md`.

For Codex CLI 0.130.0 skill discovery paths and how to expose external local skill trees such as `~/workspace/skills-jk/skills` and Hermes `.hermes/skills`, see `references/codex-cli-0.130-skill-discovery.md`. Key point: Codex discovers `$HOME/.agents/skills` and follows symlinked directories there; do not invent unsupported `skills.paths` config keys.

For making Codex reference Hermes Agent durable memory, see `references/codex-cli-0.130-hermes-memory-mirror.md`. Key point: Codex memory reads from `$CODEX_HOME/memories`, rejects symlinks, and should use a generated mirror of Hermes `USER.md`/`MEMORY.md` with `features.memories=true`, `memories.use_memories=true`, and `memories.generate_memories=false`.

If Codex fails with:

```
Error loading config.toml: unknown variant `standard`, expected `fast` or `flex`
in `service_tier`
```

then the installed Codex CLI no longer accepts `service_tier = "standard"`. Do not blindly change this to `fast`: if the user's intent is normal/non-fast mode, remove the `service_tier` line entirely so Codex uses its default service tier.

Do not use `service_tier = "flex"` as the automatic replacement unless verified against the user's account/API path; some setups parse it locally but fail at runtime with `Unsupported service_tier: flex`.

Verify config parsing with a lightweight command such as `codex --help`. If possible, also run a minimal Codex command that reaches the API before declaring the fix complete.

## Model selection

For repo-heavy coding workflows, prefer `gpt-5.5` with `model_reasoning_effort = "high"` as the default when it is available and verified with a minimal `codex exec` call. Keep `gpt-5.4` as a balanced fallback for routine coding or when stability/predictability matters more than frontier model quality. Keep `gpt-5.4-mini` for explicitly fast/simple tasks.

Recommended profile shape:

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"

[profiles.fast]
model = "gpt-5.4-mini"
model_reasoning_effort = "low"

[profiles.balanced]
model = "gpt-5.4"
model_reasoning_effort = "medium"

[profiles.deep]
model = "gpt-5.5"
model_reasoning_effort = "high"

[profiles.deep_xhigh]
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
```

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees (follow repo-root-worktree-path-policy)
terminal(command="git worktree add .worktrees/issue-78 -b fix/issue-78 origin/main", workdir="~/project")
terminal(command="git worktree add .worktrees/issue-99 -b fix/issue-99 origin/main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="~/project/.worktrees/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="~/project/.worktrees/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd ~/project/.worktrees/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove .worktrees/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building** — auto-approves changes within the sandbox
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work
