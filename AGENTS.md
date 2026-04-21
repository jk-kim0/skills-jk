# AGENTS.md

## Purpose

This repository is used by both humans and AI agents, but this file is the working guide for AI agents such as Codex and Claude Code.
It explains how to do repository work safely and consistently.

## Common guide for humans and AI agents

These rules apply to everyone working in this repository.

- Keep changes small and focused.
- Prefer the source of truth: code and structured content first, then docs.
- If a rule affects both humans and agents, keep the wording aligned across files and avoid duplicating long policy text.
- When documentation and implementation diverge, update the source of truth first.

## Before you work

1. Read `README.md` for repository context.
2. Read the relevant skill if the task matches an existing Skill.
3. Confirm the active branch and worktree before editing.
4. Prefer a new worktree for isolated branch work.

## Skill discovery

At the start of every user turn in this repository:

1. Discover available skills from these sources (in order):
   - Session-provided skill list, if present
   - `skills/` directory in this repository (`skills/<name>/SKILL.md`)
   - `$CODEX_HOME/skills/.system/` for built-in system skills
2. Build a short in-memory registry for this turn with:
   - `name`
   - `description`
   - `path to SKILL.md`
3. Match the user task against that registry.
4. Load only the minimum `SKILL.md` and linked files needed.

## Trigger rules

- If the user names a skill explicitly, use that skill.
- If the task clearly matches a skill description, use that skill even without an explicit name.
- If multiple skills match, use the minimum set and state the execution order briefly.
- Do not carry skill activation across turns unless re-triggered.

## Work rules

- Use a worktree for branch-isolated work.
- Make the smallest change that satisfies the request.
- Keep docs and implementation aligned.
- Verify the result before finishing.
- If a PR already exists for the branch, commit and push the change.
- If no PR exists, follow the repository workflow for committing, pushing, and creating one.

## Output contract

Before substantial work, state one short line:

- which skill(s) are being used
- why they were selected
- in what order, if multiple
