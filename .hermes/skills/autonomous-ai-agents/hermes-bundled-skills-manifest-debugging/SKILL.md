---
name: hermes-bundled-skills-manifest-debugging
description: Trace how Hermes generates and updates the bundled skills manifest, and use it to explain unexpected skill hash diffs.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes bundled skills manifest debugging

Use this when the user asks things like:
- where `.bundled_manifest` comes from
- why a bundled skill hash changed
- whether a manifest diff is the cause or just evidence
- which Hermes code updates bundled skills automatically

## What `.bundled_manifest` is

Hermes stores bundled skill sync state in:
- `$HERMES_HOME/skills/.bundled_manifest`

Each line is:
- `skill_name:origin_hash`

The hash is not for one file only. It represents the bundled skill directory content.

## Real generator location

The actual generator/updater lives in the Hermes application source tree, not in the user repo that merely hosts `HERMES_HOME`.

Primary file:
- `tools/skills_sync.py`

Important implementation facts to verify there:
1. `MANIFEST_FILE = SKILLS_DIR / ".bundled_manifest"`
2. `_dir_hash(directory)` hashes every file in the skill directory
3. `sync_skills()` computes `bundled_hash = _dir_hash(skill_src)` per bundled skill
4. `_write_manifest()` writes sorted `name:hash` lines atomically

## Practical interpretation

When debugging a manifest diff:
- treat the manifest as a derived artifact, not the root cause by default
- if `llama-cpp:<hash>` changed, inspect the whole `llama-cpp/` skill directory
- include `SKILL.md`, `references/`, `templates/`, and any added/removed files
- if many skill keys or hashes change together, suspect a broader bundled snapshot mismatch or rollback rather than a one-file edit

## Primary code-reading workflow

1. Find generator code:
- search for `bundled_manifest`
- open `tools/skills_sync.py`

2. Confirm hash semantics:
- inspect `_dir_hash()`
- confirm it includes relative paths and file bytes for all files under the skill directory

3. Confirm write format:
- inspect `_write_manifest()`
- verify sorted `name:hash` output and atomic temp-file replace

4. Confirm call sites:
- search for `sync_skills(`
- check installer, CLI startup, update flow, profile seeding, and container entrypoint

## Common call sites

Typical places that invoke the sync:
- CLI launch
- install/setup/update flows
- profile seeding logic
- docker entrypoint

When explaining behavior to the user, distinguish:
- code that generates the manifest
- flows that call that code automatically

## Useful investigation outputs

Report these explicitly:
- manifest file path in the current setup
- generator file path
- whether the hash is per-file or per-directory
- which call sites can regenerate it automatically
- whether the observed diff looks isolated or part of a larger bundled snapshot change

## Reusable conclusion pattern

A good final explanation often looks like:
- the manifest change is a consequence of bundled skill content changing
- the underlying cause is the skill directory diff
- the automatic sync code that records it is `tools/skills_sync.py`
- the change may have been triggered during CLI launch, install/update, profile seed, or another sync path
