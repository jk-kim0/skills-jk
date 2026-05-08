---
name: background-task-patterns
description: Choose the correct Hermes execution mode for work that should not block the conversation, especially CI watching and long-running shell commands.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [background, async, delegate_task, terminal, process, ci, workflow]
---

# Background task patterns

Use this when the user wants work to continue while the assistant remains available for new instructions.

## Core finding

`delegate_task` is not a true background job.

Even though it runs a subagent in an isolated context, the parent turn is still occupied waiting for the result. This can make the assistant appear blocked. Do not use `delegate_task` when the user explicitly wants the assistant to stay responsive during ongoing work.

## Choose the right mechanism

### 1. Use `terminal(background=true)` for long shell work

Best for:
- CI watching
- builds
- tests
- deployments
- log tailing
- any command-line process that can run unattended

Recommended pattern:
- start with `terminal(background=true, notify_on_complete=true)`
- if needed, inspect with `process(list|poll|wait|log)`
- continue helping the user in the meantime

Example uses:
- `gh pr checks --watch`
- `npm run build`
- `pytest`
- deployment scripts

Important practical note:
- use an absolute `workdir`, not `~/...`
- a background process start can fail if `workdir` uses a tilde form that is not expanded by the launcher

Safe pattern:
```json
{
  "command": "env -u GITHUB_TOKEN gh pr checks 127 --watch --interval 10",
  "background": true,
  "notify_on_complete": true,
  "workdir": "/Users/jk/workspace/corp-web-japan"
}
```

### 2. Use `cronjob` for deferred autonomous agent work

Best for:
- run later
- scheduled monitoring
- a self-contained task that does not need interaction

Tradeoff:
- runs in a fresh session
- cannot ask follow-up questions
- current chat context is not automatically preserved unless written into the prompt

Important delivery rule:
- if the user expects the cron result to come back to the current chat, prefer omitting `deliver` so auto-delivery can target the origin thread
- if the created job comes back with `deliver: local` or any non-origin destination, immediately update it to `deliver: origin`
- after `cronjob(create)`, inspect the returned job object instead of assuming the delivery target is correct

Important schedule rule:
- use supported schedule formats only: durations like `1m`, `30m`, `2h`; recurring forms like `every 2h`; cron expressions; or ISO timestamps
- natural-language strings like `in 1 minute` are not accepted

### 3. Use `delegate_task` only for isolated reasoning/implementation, not responsiveness

Best for:
- independent code analysis
- implementation in an isolated context
- research or synthesis that would flood the parent context

Not suitable for:
- user expectation of immediate responsiveness while the work continues
- anything you would naturally describe as a true background job
- "do a full agent task in the background and let me keep chatting" expectations

Important limitation:
- there is currently no true non-blocking general-purpose agent delegation mode equivalent to a detached worker that can keep editing files, opening PRs, and reasoning autonomously while the current chat remains fully interactive
- if the work is fundamentally an agent task rather than a shell command, `delegate_task` will still occupy the parent turn until it returns
- if the user explicitly wants background-style responsiveness, say so clearly and choose between:
  - `terminal(background=true)` for shell-driven work
  - `cronjob` for a deferred autonomous run in a fresh session
  - staying in the current chat and doing the work stepwise

## Practical rule of thumb

If the user means:
- "keep doing this while I can still talk to you" -> use `terminal(background=true)` if the task is shell-driven
- "run this later / separately" -> use `cronjob`
- "have another agent reason about this" -> use `delegate_task`

## PR / CI workflow pattern

For PR follow-up work:
1. make the change
2. push the PR branch
3. start CI watching in the background with `terminal(background=true)`
4. return control to the user immediately
5. react when the background completion notification arrives

This avoids blocking the conversation on `gh pr checks --watch`.

### Important: stale watcher alerts after later pushes

If you start multiple background CI watchers across several pushes, older watcher sessions can keep reporting failures for superseded runs.

Typical case:
- push A starts watcher A
- CI for push A fails
- you fix the issue and push B
- watcher A later emits a `fail` notification even though the latest PR head for push B is already green

Safe handling:
1. after any watcher fail alert, verify the latest PR head SHA
2. list the newest workflow runs for the branch
3. check whether the alerting run belongs to the current head or to an older push
4. only report the PR as currently failing if the failing run matches the latest head/run set

Practical rule:
- treat background watcher alerts as provisional until reconciled against the latest branch head and latest run list
- after each fix push, prefer starting a fresh watcher rather than relying on earlier watch sessions

## Pitfalls

- assuming `delegate_task` behaves like a detached async worker
- starting background commands with `workdir` set to `~/...` instead of an absolute path
- using `cronjob` for work that depends on immediate user feedback
- treating any delayed `gh pr checks --watch` fail alert as the current truth without checking whether it came from an older run
