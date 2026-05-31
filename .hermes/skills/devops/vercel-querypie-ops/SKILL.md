---
name: vercel-querypie-ops
description: Use when operating QueryPie Vercel projects, runtime logs, firewall/WAF rules, or Vercel CLI inspections; contains migrated repo-specific memory and user preferences.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-context, migrated-memory]
    related_skills: []
---
# Vercel Querypie Ops

## Overview

This skill is a compact trigger/index for repo-specific context migrated out of `.hermes/memories/MEMORY.md` and `.hermes/memories/USER.md` so global memory stays focused on durable user preferences rather than repository implementation details.

Load this skill before substantial work in the named repository or platform area. The detailed migrated notes are kept in `references/migrated-memory-and-user-context.md`.

## When to Use

- The current task is in or about `vercel-querypie-ops`.
- The user asks about prior conventions, repo-specific constraints, route/content policy, migration status, or operational quirks for this area.
- You are about to edit code, documentation, GitHub wiki pages, CI, deployment, or infrastructure connected to this area.

## Required Context

Read `references/migrated-memory-and-user-context.md` after loading this skill. Treat entries from `USER.md` as user preferences/constraints and entries from `MEMORY.md` as repo facts or workflow lessons. If a note is stale when checked against the live repo, update this skill or its reference rather than writing the stale fact back into global memory.

For Vercel CLI local-link problems or command-safety questions, read `references/vercel-cli-local-link-and-command-safety.md`. It captures the durable pattern: a bare `vercel` command deploys, non-deploy operations must use explicit subcommands, and `vercel link` side effects should be kept local via `.git/info/exclude` unless the repo intentionally tracks them.

For `querypie/outbound-agent` outbound-dev redeploy/reset/smoke work, also read `references/outbound-dev-db-reset-and-smoke.md` before running workflows or diagnosing smoke failures.

For `querypie/outbound-agent` Gmail OAuth / Gmail actual-send readiness setup across `dev-vercel`, `dev-seoul`, or `dev-tokyo`, also read `references/outbound-gmail-oauth-env-setup.md`. It captures the safe secret-handling pattern, Vercel preview-env API workaround, VM `/etc/outbound-agent/front.env` update sequence, and issue-evidence comment shape.

## Common Pitfalls

1. Do not copy repo-specific facts back into global memory unless they are broadly reusable across repositories.
2. Do not treat migrated notes as a substitute for live repo verification when code, CI, routes, or deployment state may have changed.
3. Keep new findings in this skill or a more specific existing skill for the repo/workflow.

## Verification Checklist

- [ ] Skill loaded because the task matches `vercel-querypie-ops`.
- [ ] Migrated context reference reviewed when repo-specific history matters.
- [ ] Live repo/source checked before acting on potentially stale implementation details.
