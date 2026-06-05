---
name: local-development-infra-compose
description: Add or maintain minimal Docker Compose based local development infrastructure, especially database-only setups with repo-local documentation and verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [docker, compose, local-development, postgres, infrastructure, documentation]
    related_skills: [git-worktree-safety-pack, github-pr-workflow]
---

# Local Development Infra Compose

Use this skill when adding or maintaining repository-local Docker Compose files for local development infrastructure such as PostgreSQL, Redis, mail sandbox, object storage, or queues.

## Core principles

1. Keep the change scoped to the user's requested local infrastructure.
2. Do not add application services, migrations, seeds, backups, queues, caches, or extra dependencies unless the user explicitly asks for them.
3. Put operational notes near the infra files, commonly under `infra/local/README.md`, and keep them practical: prerequisites, version choice, connection details, start/stop commands, and data reset behavior.
4. Prefer reproducible image tags over floating `latest` when the user asks for a stable/LTS-like local setup.
5. Before choosing database names, users, passwords, container names, volume names, or other code-level identifiers, inspect repo guidance (`AGENTS.md`, repo-local skills, existing docs) for the preferred project prefix. Do not infer a snake_case prefix from the repository name when the repo may prefer a shorter code prefix.
6. Verify the Compose syntax with `docker compose config` before committing.
7. For repo work, follow the repository's branch/worktree policy and PR workflow skills.

## PostgreSQL-only local setup pattern

When the user asks for a local PostgreSQL setup that only needs start/stop support:

- Use a single `postgres` service.
- Keep `compose.yml` at the repository root unless the repo already has a different convention.
- Use a named volume for `/var/lib/postgresql/data` so `docker compose down` stops the service without deleting local data.
- Publish port `5432:5432` only when local app/tooling needs host access.
- Include `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` with clearly local-only values.
- Add a simple `pg_isready` healthcheck.
- Document `docker compose up -d postgres`, `docker compose ps postgres`, `docker compose logs -f postgres`, `docker compose down`, and `docker compose down -v`.

## PostgreSQL version wording

PostgreSQL does not provide Docker tags named `lts`. If the user asks for the latest LTS PostgreSQL version, treat the durable requirement as “latest stable supported PostgreSQL major” unless they name a specific major.

Recommended handling:

1. Check the current official Docker Hub/PostgreSQL tags or official PostgreSQL release information when possible.
2. Avoid `postgres:latest` for committed project configuration.
3. Use the explicit current major tag such as `postgres:18` rather than a patch tag when the team wants to stay on that supported major while receiving image updates.
4. In the README, state that PostgreSQL has no separate `LTS` image tag and explain the chosen stable major tag.

## README shape

A compact `infra/local/README.md` should include:

- Purpose and scope
- What is intentionally not included yet
- Prerequisites
- PostgreSQL/image version and rationale
- Connection table
- Start, status/log, stop, and reset commands
- Local-only secret warning
- Rule that production/deployment settings are out of scope

## Reference examples

- `references/minimal-postgres-compose.md` — minimal PostgreSQL-only `compose.yml` and README documentation points from a local dev infra setup.

## Verification checklist

- [ ] `docker compose config` succeeds.
- [ ] `git diff --check` succeeds before commit.
- [ ] The README commands match the actual service name in `compose.yml`.
- [ ] Database/user/password/URL examples use the repo-approved project prefix.
- [ ] A targeted grep confirms deprecated local infra prefixes are absent from compose/docs, except in guidance that explicitly says not to use them.
- [ ] The setup does not pre-create unrelated infra services or ignore rules.
- [ ] If using a project worktree, root checkout remains untouched except for read-only inspection.

## Common pitfalls

1. Do not translate “latest LTS PostgreSQL” into `postgres:latest`; it is less reproducible and does not encode the intended support major.
2. Do not bundle Redis, mailhog, app containers, seed scripts, or migration commands into a PostgreSQL-only request.
3. Do not add broad `.gitignore` rules for runtime/cache artifacts that have not been created or requested.
4. Do not claim production readiness for a local Compose file.
5. Do not omit the destructive nature of `docker compose down -v`; call out that it deletes the named volume/data.
6. Do not assume database/user identifiers should mirror the repository name exactly. If a repo or user says to use a shorter code prefix (for example `outbound` instead of `outbound_agent`), update compose values, README connection examples, healthchecks, and repo guidance together so future infra additions stay consistent.
