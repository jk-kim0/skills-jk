---
name: development-environment-ops
description: Use when operating development or staging infrastructure across local Compose, cloud Linux VMs, TLS/nginx, provider OAuth runtime config, and multi-environment deploy/migrate/smoke workflows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, development-environments, cloud-vm, docker-compose, nginx, tls, oauth, deployment, smoke-test]
    related_skills: []
---

# Development Environment Operations

## Overview

Use this umbrella skill for class-level operations that keep development and staging environments runnable: local infrastructure Compose files, Linux VM app deployment, nginx/Let's Encrypt TLS, provider OAuth runtime configuration, and multi-environment deploy/migrate/schema/smoke verification.

This skill replaces several narrow environment-operation skills. Keep the main `SKILL.md` focused on routing, safety, and shared procedure. Put provider-specific command transcripts, incident notes, exact environment maps, and one-off debugging recipes under `references/`.

## When to Use

- The user asks to create or maintain local development infrastructure such as PostgreSQL/Redis via Docker Compose.
- The user asks to provision, document, deploy, or operate an application on a Linux cloud VM.
- The user asks to configure nginx, Certbot, Let's Encrypt, public DNS, or HTTPS on a Linux host.
- The user asks to configure development/staging provider OAuth runtime settings such as Gmail OAuth client IDs/secrets, callback URIs, Vercel env, or VM env files.
- The user asks to verify that one or more dev/stage environments are on latest main, migrated, schema-clean, smoke-tested, reset, or redeployed.

## Shared Safety Rules

1. Separate read-only discovery from live mutation. Report what will change before cloud resources, DNS, secrets, DB reset, deploy, service restart, or TLS issuance.
2. Confirm repository guidance, branch/worktree policy, and git state before editing docs or infra files.
3. Never print secrets: OAuth client secrets, refresh tokens, DB URLs, private keys, cloud tokens, `.env` files, or `/etc/letsencrypt/**/privkey.pem` contents.
4. Treat public internet exposure as a security boundary. Document inbound ports, source ranges, DNS/FQDN, TLS state, and DB bind address.
5. Prefer exact deployment metadata over public HTTP alone. `/login` or `/health` 200 proves availability, not exact revision.
6. Prefer migrate-only before reset unless the user explicitly requests a reset. If reset is authorized, still verify reset, seed, schema, and runtime smoke afterward.

## Routing by Subtask

### Local Compose infrastructure

Use for repo-local `compose.yml` / `infra/local` work. Keep the scope minimal: database/cache/mail/object-store only unless explicitly requested. Verify with `docker compose config`, document start/status/log/stop/reset commands, and call out destructive `down -v` behavior.

Detailed prior workflow: `references/local-development-infra-compose.md`.

### Linux VM application deployment

Use for VM sizing, provider CLI discovery, SSH/bootstrap, app install paths, PostgreSQL via Docker Compose, systemd services, nginx reverse proxy, deployed revision tracking, and operator runbooks. Verify the live deployment mode before assuming the VM path is a git checkout; inspect service `ExecStart`, image/current-release files, and `.deployed-revision`.

Detailed prior workflow: `references/cloud-vm-linux-app-deployment.md`.

### nginx / Certbot / TLS

Use for issuing and validating Let's Encrypt certificates on Linux hosts with nginx. Preflight DNS/public IP, SSH reachability, `nginx -t`, certbot command choice, HTTP->HTTPS redirect, certificate subject/issuer/dates, and renewal timers. Use forced `curl --resolve` when local resolver behavior differs from public DNS.

Detailed prior workflow: `references/linux-host-tls-certbot-nginx.md`.

### Provider OAuth runtime config

Use for development/staging OAuth setup such as Gmail send-only OAuth. Identify exact callback routes and environment URLs, register backend callback URIs only, inject runtime env without printing values, redeploy/restart the affected runtime, then smoke OAuth start/callback/send as appropriate. Treat OAuth start URL evidence, token-exchange evidence, and actual provider send evidence as different proof layers.

Detailed prior workflow: `references/gmail-oauth-dev-environment-setup.md`.

### Multi-environment deploy/migrate/schema/smoke

Use when several dev environments must be checked against latest main. Stabilize the target SHA, dispatch migrations/schema checks, confirm exact deployed versions per platform, run public and DB-backed smoke, and escalate in order from migration failure to schema drift to deploy mismatch to runtime logs.

Detailed prior workflow: `references/multi-environment-dev-deployment-ops.md`.

## Reporting Pattern

Include:

1. Target environments/hosts/FQDNs and whether each action was read-only or mutating.
2. Authoritative target revision, deployment IDs, image tags, service status, or equivalent exact-version evidence.
3. Migration/reset/schema outcome and whether reset was required or explicitly requested.
4. Public smoke and DB-backed/provider smoke evidence, separated by environment.
5. Security posture: public ports, TLS, DB bind address, secret handling, OAuth callback URI parity.
6. Files/docs changed, if any.
7. Follow-up that requires user/cloud-console/provider action.

## Common Pitfalls

- Using a public 200 response as exact-version proof.
- Resetting dev databases before migrate/schema evidence or without explicit reset scope.
- Treating secret existence as runtime injection proof.
- Opening PostgreSQL publicly because Compose defaults publish `5432:5432` on all interfaces.
- Running Certbot before `nginx -t` or before DNS/public IP is understood.
- Reporting OAuth readiness from callback URI configuration alone without OAuth start/callback/provider evidence.
- Mixing local infra, cloud mutation, app code, and documentation into one unreviewable change.

## Verification Checklist

- [ ] Target scope and mutation boundaries are explicit.
- [ ] Secrets were never printed or committed.
- [ ] Exact deployment/runtime evidence was gathered when deployment status was in scope.
- [ ] Local Compose or nginx/TLS syntax checks passed when files/config were changed.
- [ ] Migration/schema/reset/smoke checks were run in the correct escalation order.
- [ ] OAuth/provider flows, if in scope, were verified at the correct layer and reported with redacted evidence.
- [ ] Supporting reference files were consulted for environment-specific command details.
