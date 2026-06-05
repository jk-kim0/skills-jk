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

This skill is a compact trigger/index for QueryPie Vercel operational context, durable command-safety rules, and Vercel/outbound-agent references.

## When to Use

- The current task is in or about `vercel-querypie-ops`.
- The user asks about prior conventions, repo-specific constraints, route/content policy, migration status, or operational quirks for this area.
- You are about to edit code, documentation, GitHub wiki pages, CI, deployment, or infrastructure connected to this area.

## Required Context

For simple Vercel CLI/environment inspection tasks, prefer pure Vercel CLI and basic shell output over Python scripts unless parsing or bulk processing genuinely requires Python.

For Vercel CLI local-link problems or command-safety questions, read `references/vercel-cli-local-link-and-command-safety.md`. It captures the durable pattern: a bare `vercel` command deploys, non-deploy operations must use explicit subcommands, and `vercel link` side effects should be kept local via `.git/info/exclude` unless the repo intentionally tracks them.

For `querypie/outbound-agent` outbound-dev redeploy/reset/smoke work, also read `references/outbound-dev-db-reset-and-smoke.md` before running workflows or diagnosing smoke failures.

For `querypie/outbound-agent` Gmail OAuth / Gmail actual-send readiness setup across `dev-vercel`, `dev-seoul`, or `dev-tokyo`, also read `references/outbound-gmail-oauth-env-setup.md`. It captures the safe secret-handling pattern, Vercel preview-env API workaround, VM `/etc/outbound-agent/front.env` update sequence, and issue-evidence comment shape.

For sensitive Vercel environment variable replacement, rotation, or OAuth client secret updates, read `references/vercel-sensitive-env-replacement.md`. It covers the remove/add pattern for `sensitive` env vars, post-change deployment requirements, secret-exposure rotation, and key/target/type verification without printing values.

For `corp-web-app` GitHub Actions staging/production/preview deploy workflows that fail even though Vercel later shows the deployment as `Ready`, read `references/corp-web-app-deploy-polling-transient-failures.md`. It captures the pattern where `scripts/deploy/index.js` status polling hits transient `TypeError: fetch failed`, how to prove the app deploy is healthy with `vercel inspect` and route probes, and how to add bounded retry without masking real cancelled/terminal deployment failures.

## Common Pitfalls

1. Do not copy repo-specific facts back into global memory unless they are broadly reusable across repositories.
2. Do not treat stored operational notes as a substitute for live Vercel/GitHub/repo verification when deployments, env vars, logs, branches, or runtime state may have changed.
3. Keep new findings in this skill or a more specific existing skill/reference for the repo/workflow.
4. For user-facing Vercel/outbound-dev operations, do not treat tool-call output or a final summary as progress reporting. The user expects visible normal-chat updates between operational steps: state what will be checked and why, run one step, then report the result before the next tool call.

## Verification Checklist

- [ ] Skill loaded because the task matches `vercel-querypie-ops`.
- [ ] Required Vercel/outbound reference files reviewed when the task matches their trigger.
- [ ] Live repo/source checked before acting on potentially stale implementation details.
