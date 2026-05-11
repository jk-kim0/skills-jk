---
name: hermes-checkpoint-storage-investigation
description: Investigate Hermes checkpoint disk usage, explain what checkpoints are for, determine whether they are safe to delete, and identify why they grow large in practice.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, checkpoints, rollback, disk-usage, troubleshooting, runtime]
    related_skills: [hermes-agent, hermes-session-forensics]
---

# Hermes checkpoint storage investigation

Use this when the user asks things like:
- "What are Hermes checkpoints for?"
- "Can I delete `.hermes/checkpoints`?"
- "Why are Hermes checkpoints so large?"
- "Why is checkpoint disk usage growing so fast?"

## What this skill is for

Hermes checkpoints are easy to misunderstand because users often already rely on normal git commits, branches, and worktrees. This skill helps distinguish:
- user-facing git history
- Hermes internal rollback safety snapshots

It also captures an important implementation detail discovered in the live codebase:
- `checkpoints.max_snapshots` does **not** currently perform real on-disk pruning of old checkpoint history
- it mainly limits checkpoint listing/log visibility

That detail materially changes how you should explain disk growth.

## Investigation workflow

### 1. Confirm the active Hermes home and config

Always inspect the live environment first.

Check:
- current `pwd`
- current time
- `HERMES_HOME`
- candidate Hermes homes such as:
  - `$HERMES_HOME`
  - `~/workspace/skills-jk/.hermes`
  - `~/.hermes`

Then inspect config for:
- `checkpoints.enabled`
- `checkpoints.max_snapshots`

Example:
```bash
pwd
date '+%Y-%m-%d %H:%M:%S %Z'
echo "$HERMES_HOME"
```

Read the active `config.yaml` and confirm whether checkpoints are enabled.

### 2. Load the relevant Hermes skills/docs first

Load at least:
- `hermes-agent`
- `hermes-session-forensics`

Then inspect the built-in docs page:
- `website/docs/user-guide/checkpoints-and-rollback.md`

What to extract:
- checkpoints exist for destructive operations and file-mutating tools
- Hermes uses a **shadow git repo** under `<HERMES_HOME>/checkpoints/`
- `/rollback` depends on checkpoint history
- checkpoints are separate from the user’s real project `.git`

### 3. Inspect the implementation, not just the docs

Read `tools/checkpoint_manager.py`.

Important lines to confirm and cite:
- `CheckpointManager` is used before file-mutating tool calls
- at most one checkpoint per directory per turn
- shadow repo path per working directory
- checkpoint listing uses git log from the shadow repo
- `_prune()` behavior

Critical finding to verify in code:
- `_prune()` currently does **not actually prune old snapshots from disk**
- comments explicitly say pruning is not performed; only log/listing is limited

This is the main explanation for persistent disk growth when users assume `max_snapshots` is a hard storage cap.

### 4. Measure real checkpoint disk usage

Inspect the checkpoint directory directly.

Recommended checks:
- total size of `<HERMES_HOME>/checkpoints`
- top largest checkpoint repos
- directory count
- whether each checkpoint repo contains normal git internals like `objects/`, `refs/`, `HEAD`
- sample `git count-objects -vH` on a few checkpoint repos

Useful signals:
- many checkpoint repos around similar sizes often means one shadow repo per worktree/project directory
- high loose-object counts with `in-pack: 0` often means poor compaction and more disk overhead

### 5. Map checkpoint repos back to working directories

Check `HERMES_WORKDIR` inside each checkpoint repo.

This is essential because users often have many git worktrees. Disk growth usually comes from:
- one shadow checkpoint repo per worktree
- each repo capturing a large initial snapshot of that worktree

Surface the actual mapped paths in your reasoning, for example:
- repo root
- worktrees under `.worktrees/...`
- temporary directories like `/private/tmp`

### 6. Be careful with disk-size discrepancies

If `du -sh` reports unexpectedly huge sizes, verify with a second method.

Recommended fallback:
- recursively sum file sizes in Python

Reason:
- checkpoint directories may be changing during inspection
- concurrent Hermes activity can cause `du` errors like `No such file or directory`
- APFS/block allocation and transient file churn can distort a single `du` reading

When this happens, report the discrepancy honestly:
- say `du` showed X
- say direct file-size summation showed Y
- mention concurrent mutation if observed

## How to explain checkpoints to the user

Use this conceptual distinction:

### User git commits
- intentional history
- collaboration / PR / review / remote push
- meaningful logical units

### Hermes checkpoints
- automatic pre-mutation safety snapshots
- used by Hermes rollback features
- stored in a separate shadow git repo
- not part of the user’s real git history

Good concise explanation:
- checkpoints are not a replacement for git commits
- they are Hermes’ private recovery layer so it can undo its own changes without rewriting the user’s actual repo history

## Directly answer the three common user questions

### 1. What are checkpoints for?
Answer:
- automatic snapshots before file-modifying or destructive operations
- support `/rollback`, `/rollback diff`, and file restore behavior
- allow Hermes to revert agent-made changes without touching the user’s real `.git`

### 2. Can I delete them?
Answer:
- yes, generally safe to delete
- but doing so removes past `/rollback` restore history
- current and future Hermes operation still works; Hermes can create new checkpoints later
- advise extra caution if a live session may still rely on recent checkpoints

### 3. Why are they so large?
Answer should usually include all of:
- one shadow git repo per working directory/worktree
- large initial snapshots can already be substantial
- checkpoint repos may store many loose objects
- `max_snapshots` currently does not truly prune disk history
- lots of worktrees cause near-linear growth in checkpoint storage

## Recommended wording about deletion safety

Use wording like:
- "Deleting checkpoints is safe for Hermes operation, but you will lose rollback history."
- "It does not damage your actual project git repo because checkpoints live in a separate shadow repo."

Avoid saying:
- "It is completely risk-free"

because users may still want recent `/rollback` history.

## Optional recommendations

Depending on the user’s workflow, suggest one of these:

## Practical cleanup order for repo-local `.hermes/`

When the user explicitly asks you to free disk space under a repo-local Hermes home such as `~/workspace/skills-jk/.hermes`, use this order:

1. Measure the whole tree first:
```bash
du -xhd 2 ~/workspace/skills-jk/.hermes 2>/dev/null | sort -h | tail -n 120
 df -h /
```

2. Check the active config before deleting anything:
- inspect `config.yaml`
- especially confirm `checkpoints.enabled`

3. If `checkpoints.enabled: false` and the checkpoint tree is still large, treat existing `checkpoints/` as stale historical rollback data rather than active runtime state.

4. Quantify checkpoint recency before removal:
- count checkpoint repos
- total size
- last-24h activity
- sample `HERMES_WORKDIR` mappings

If there are no recent checkpoints and the user asked to reclaim space, it is reasonable to remove the entire historical checkpoint tree.

5. Safe deletion candidates inside repo-local `.hermes/` are usually:
- `checkpoints/` — removes rollback history only
- `cache/` — regenerable
- `logs/` — regenerable

6. Usually preserve unless the user explicitly wants deeper cleanup:
- `sessions/` — conversation/session records
- `memories/` — durable memory store
- `skills/` — installed skills
- `config.yaml` and other small runtime configuration/state

7. After deletion, recreate empty `cache/` and `logs/` directories if they existed before, then re-measure:
```bash
rm -rf <paths>
 mkdir -p ~/workspace/skills-jk/.hermes/cache ~/workspace/skills-jk/.hermes/logs
 du -xhd 1 ~/workspace/skills-jk/.hermes 2>/dev/null | sort -h
 df -h /
```

8. Report clearly:
- what was deleted
- what was preserved
- before/after size of `.hermes`
- final free disk space

### Session-specific reusable finding
If the live config has checkpoints disabled, historical checkpoint repos can remain on disk indefinitely until manually removed. In practice this means a repo-local `.hermes/checkpoints/` directory can consume many GiB even though Hermes is no longer creating new checkpoints.

### If the user already uses disciplined git/worktree workflows
Suggest that checkpoints may have low value relative to disk cost, especially if they rarely use `/rollback`.

### If they want to keep the feature
Suggest:
- periodic cleanup of stale or orphaned checkpoint repos
- especially worktrees that no longer exist

### If they want minimal storage growth
Suggest disabling checkpoints in config:
```yaml
checkpoints:
  enabled: false
```

## Pitfalls

- Do not assume checkpoint storage is under `~/.hermes`; confirm the active `HERMES_HOME`
- Do not trust docs alone; verify `_prune()` in the live code
- Do not confuse the user’s repo `.git` with Hermes shadow checkpoint repos
- Do not present `max_snapshots` as a true storage bound unless the implementation changes
- Do not rely on a single `du` reading if checkpoint repos are actively changing

## Evidence checklist

Before giving the final answer, try to have evidence for all of these:
- active `HERMES_HOME`
- `checkpoints.enabled` and `max_snapshots` in config
- docs confirming shadow repos and `/rollback`
- code confirming pre-mutation checkpointing
- code confirming lack of true pruning
- measured checkpoint size and count
- at least one mapping from checkpoint repo to original workdir via `HERMES_WORKDIR`

## Good final answer shape

1. Short conclusion
2. What checkpoints are for
3. Whether they are safe to delete
4. Why they are large in this environment
5. Whether Hermes actually depends on them for any feature
6. Optional next steps: disable, clean up, or inspect stale entries
