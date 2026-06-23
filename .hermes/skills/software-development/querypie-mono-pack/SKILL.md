---
name: querypie-mono-pack
description: Use when working in chequer-io/querypie-mono and needing repo-specific backend, local server, Jira debug, RDP, or AI Native SDLC guidance. Thin active entrypoint that points to the inactive querypie-mono skill pack index instead of injecting every detailed skill into the default skills index.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-skill-pack, querypie-mono, backend, rdp, jira-debug, sdlc, prompt-size]
    related_skills: [backend-style-guide, server-runner, jira-debug, rdp-doc]
---

# querypie-mono Pack

## Overview

This is a thin active entrypoint for the `querypie-mono` repo-specific skill pack. The detailed skills live outside active `.hermes/skills/` at:

`.hermes/skill-packs/querypie-mono/`

Keeping the detailed skills outside `.hermes/skills/` prevents their full name/description index from being injected into every default Hermes request.

## When To Use

- The repository, issue, PR, workflow, local server task, Jira ticket, or support case belongs to `chequer-io/querypie-mono`.
- The user asks for QueryPie monorepo backend coding/review, migrations, local server execution, Jira debugging, RDP architecture/support, or the `.agents` AI Native SDLC workflow.
- The user explicitly mentions `querypie-mono`, `apps/api`, `bambi`, `RDP`, `Server Agent`, `jira-debug`, or `sdlc-*` in a QueryPie monorepo context.

## Required First Step

Read the pack index before selecting detailed skills:

`.hermes/skill-packs/querypie-mono/INDEX.md`

Then read only the specific `SKILL.md` files referenced by the index that match the current task.

If the pack index is absent in the current checkout, fall back to the repo-local guidance files instead of proceeding from memory:

1. Read `AGENTS.md` in the repo/subdirectory context.
2. Read `.agents/skills/**/SKILL.md` files that match the task, if present.
3. For SDLC tasks, read `.agents/sdlc/core/README.md` and the core references named by the selected stage skill.

Record in the progress note that the pack index was unavailable and which fallback guidance was used.

## Common Pitfalls

1. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
2. Do not assume every pack file should become an active Hermes skill. Keep this active entrypoint thin.
3. For SDLC skills, do not omit `.agents/sdlc/core`; stage scripts and references depend on it.
4. For Jira/Slack helper skills, do not echo raw tokens, credentials, customer attachments, or private ticket contents into chat, docs, PR bodies, logs, screenshots, or commits.
5. For RDP support guidance, distinguish architecture explanation from customer-facing response drafting; collect only the diagnostics needed for the support question.

## Verification Checklist

- [ ] `.hermes/skill-packs/querypie-mono/INDEX.md` was read, or repo-local fallback guidance was read when the pack index was absent.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.
- [ ] SDLC core support files are present when using `sdlc-*` skills.
- [ ] Secrets and customer-sensitive artifacts stayed out of chat, docs, PR bodies, logs, screenshots, and commits.
