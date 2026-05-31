---
name: cloud-vm-linux-app-deployment
description: Provision and operate a Linux cloud VM for an internet-facing application, including provider CLI discovery, VM sizing, firewall/DNS, SSH/bootstrap, app deployment, PostgreSQL via Docker Compose, systemd, nginx, and Let's Encrypt TLS.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, cloud-vm, linux, ssh, nginx, certbot, docker-compose, postgresql, systemd, tencent-cloud]
    related_skills: [devops-host-runner-operations, linux-host-tls-certbot-nginx, local-development-infra-compose]
---

# Cloud VM Linux App Deployment

## Overview

Use this class-level skill when the user asks to run an application on a Linux VM in a cloud provider, especially when the work includes discovering provider CLI access, selecting a VM shape, creating or documenting VM/network resources, deploying app code, running a local PostgreSQL service, exposing HTTPS to the public internet, and writing infra runbooks.

This skill is for application host deployment, not GitHub self-hosted runner operations. Use `devops-host-runner-operations` only for SSH reachability and runner-specific maintenance, and use `linux-host-tls-certbot-nginx` for deeper certificate/nginx troubleshooting.

## When to Use

- User asks how to access a cloud provider through a CLI such as `tccli`, `aws`, `gcloud`, or `az` and turn that into a VM deployment plan.
- User asks to create, document, or operate a Linux VM for a web app.
- User specifies VM size, disk size, public FQDN, public internet access, nginx, TLS/Let's Encrypt, systemd, or PostgreSQL on the host.
- User asks for repo-local infra documentation such as `infra/<env>/README.md` or `plan.md`.
- User asks to deploy a Next.js/Node app or similar app to a VM with a local database.

## Safety and Scope Rules

1. Start by confirming the current repository rules and git state if editing repo docs. In repos that require worktrees, make changes only in the repo-local worktree.
2. Separate planning/doc changes from live cloud mutations unless the user explicitly asks to create resources now.
3. Treat public internet exposure as an explicit security boundary: document inbound ports, source ranges, and why each port is open.
4. Never expose PostgreSQL to `0.0.0.0` unless the user explicitly asks. Bind database ports to localhost or avoid publishing them at all.
5. Do not print cloud credentials, SSH private keys, database passwords, `.env` secrets, or provider tokens.
6. For destructive operations such as terminating a VM, deleting disks, changing DNS, or overwriting a production service, confirm scope unless the user has explicitly requested that exact action.

## Phase 1: Provider CLI and Account Discovery

For Tencent Cloud, use `tccli` discovery before inventing console-only steps:

```sh
tccli --version
tccli configure list 2>/dev/null || true
tccli cvm DescribeRegions --region ap-guangzhou
```

Then inspect available regions/zones, images, instance types, VPCs/subnets, security groups, key pairs, and public-IP options. Prefer read-only `Describe*` commands first. Record:

- active credential/config source, without secrets;
- target region/zone and rationale;
- VM shape and disk sizing;
- SSH key pair or login method;
- public IP / EIP allocation approach;
- security group ingress for TCP 22, 80, 443;
- DNS record required for the requested FQDN.

For Tencent-specific session details and command patterns, see `references/tencent-cloud-linux-vm-deployment.md`.

## Phase 2: VM Design

A minimal internet-facing dev VM plan should specify:

- VM name and environment tag, e.g. `app-dev-tokyo`.
- Region/zone.
- OS image, preferably Ubuntu LTS unless the repo requires another distro.
- CPU/memory/disk shape, with user-requested values preserved as current assumptions rather than permanent limits.
- System packages: git, curl, nginx, certbot/nginx plugin, Docker Engine, Docker Compose plugin, Node runtime or a version manager when needed.
- App install path, e.g. `/opt/<app>/repo`.
- Config path, e.g. `/etc/<app>/<service>.env`.
- Service user and file ownership model.
- Database persistence path/volume and backup expectations.
- Run/stop/restart commands.

## Phase 3: Bootstrap and Deployment Pattern

For existing VMs, first verify the live deployment mode before choosing a rollout path. Do not assume `/opt/<app>/repo` is a git checkout just because the path is named `repo`; it may be an extracted source archive with `.deployed-revision`, backup directories, or container-deployment artifacts. Check `git rev-parse --is-inside-work-tree`, `.deployed-revision`, `systemctl show <service> -p ExecStart -p MainPID`, and the live process before deciding between git pull, source archive replacement, or container image deployment.

Recommended host layout for source/release-archive based deployments:

```text
/opt/<app>/repo/                 # deployed app source or release archive
/opt/<app>/repo/.deployed-revision
/etc/<app>/<service>.env         # host-managed app env, secret-redacted in docs
/etc/systemd/system/<service>.service
/etc/nginx/sites-available/<fqdn>.conf
/etc/nginx/sites-enabled/<fqdn>.conf
```

For private-registry container deployments, prefer immutable image tags and make the VM an image consumer instead of a build host. Record current/previous image tags on the VM, keep app containers behind nginx on localhost, keep DB outside the app image, and handle DB migrations before container replacement. See `references/container-image-vm-deployment.md` for the concise pattern.

Prefer an idempotent deployment sequence:

1. Install or update host packages.
2. Install Docker and verify `docker compose version`.
3. Place app source under `/opt/<app>/repo` from a known commit/release. If the existing path is not a git checkout, do not run git commands inside it; deploy a new archive/release directory, write `.deployed-revision`, then atomically switch the app path or service image according to the host's current deployment model.
4. Write `.deployed-revision` with the exact commit or release ID.
5. Install dependencies in the app directory with the runtime version expected by the project.
6. Run database migrations against the intended database.
7. Seed only when the environment is explicitly dev/demo.
8. Build the app.
9. Restart the systemd service.
10. Verify via localhost, nginx, and external HTTPS.

For Node/Prisma apps, do not assume `NODE_ENV=production npm ci` is enough. Prisma config and build steps can require dev dependencies. If the project needs dev tooling during build/migration, use a documented install mode such as `npm ci --include=dev`, then run the service itself with production runtime env.

## Phase 4: PostgreSQL via Docker Compose

For VM-local PostgreSQL:

- Keep PostgreSQL bound to localhost.
- Use a Docker volume for persistence.
- Store connection strings in `/etc/<app>/<service>.env` or another host-managed secret file.
- Apply migrations from the application directory.
- Document start/stop/status/log commands.
- When intentionally wiping a dev database, use `docker compose ... down -v --remove-orphans` only after confirming the compose files and volume name; then recreate PostgreSQL and verify `pg_isready` before migrations/seeds.
- If the env file is root-owned `0600`, do not source it as the service user. Run migration/seed/build through a root wrapper that exports the needed env, then restore app-tree ownership to the service user.
- For Prisma fresh installs, run client generation before seed/build when the seed imports the generated client. If a later migration fails with duplicate columns/indexes on an empty DB, inspect the baseline migration; when the baseline already includes that schema, resolve the duplicate migration as applied and report any retained rolled-back migration row rather than resetting repeatedly.

If the repository's default `compose.yml` publishes `5432:5432`, add a VM-local override file rather than editing shared local-dev compose behavior:

```yaml
services:
  postgres:
    ports: !override
      - "127.0.0.1:5432:5432"
```

Run with both files:

```sh
docker compose -f compose.yml -f /opt/<app>/compose.localhost.yml up -d postgres
docker compose -f compose.yml -f /opt/<app>/compose.localhost.yml ps
```

## Phase 5: systemd, nginx, and TLS

The app should listen on localhost, with nginx as the public reverse proxy:

```text
public internet -> TCP 80/443 -> nginx -> http://127.0.0.1:<app-port>
```

Use certbot with the nginx plugin when possible:

```sh
sudo nginx -t
sudo certbot --nginx -d <fqdn>
systemctl list-timers | grep -E 'certbot|snap.certbot|renew'
```

Verification should include:

```sh
systemctl status <service> --no-pager
curl -fsS http://127.0.0.1:<app-port>/<health-or-login-path>
curl -I http://<fqdn>/<path>
curl -I https://<fqdn>/<path>
```

When DNS is not yet pointed at the VM, use `curl --resolve <fqdn>:443:<public-ip> https://<fqdn>/...` for a targeted smoke test.

## Documentation Deliverables

For repo-local infra docs, keep the plan executable and operator-focused:

- `README.md`: how provider access works, current assumptions, resource inventory, security model, DNS/FQDN, and operational cautions.
- `plan.md`: build, deploy, run, stop, database, migration/seed, TLS, verification, rollback, and teardown commands.
- Keep environment values and passwords represented as placeholders.
- State which steps are already done versus planned only.
- Include public exposure requirements explicitly: inbound 80/443 from internet, SSH restricted if possible, DB localhost-only.

## Reporting Pattern

Summaries should include:

1. Provider CLI access status and the command used to verify it.
2. VM/resource assumptions: region, shape, disk, OS, FQDN.
3. Files created/changed.
4. Deployment/runbook commands documented.
5. Security posture: public ports, TLS, DB bind address, secret handling.
6. Verification performed or explicitly skipped.
7. Any follow-up that requires user/cloud-console action, such as DNS delegation or billing approval.

## Common Pitfalls

- Documenting only console steps when provider CLI access is already available.
- Opening PostgreSQL publicly because Compose defaults publish `5432:5432` on all interfaces.
- Running `npm ci` in production mode and then failing Prisma/build steps that need dev dependencies.
- Treating DNS propagation as proof of nginx/TLS correctness; test each layer separately.
- Forgetting to record the deployed commit/revision on the VM.
- Assuming an existing `/opt/<app>/repo` is a git checkout; verify the live deployment mode before running `git fetch`.
- Using a multi-environment deploy workflow when the user requested one named VM only. If a workflow fans out to multiple VMs (for example Tokyo then Seoul), either use a single-environment workflow or perform the documented direct SSH artifact upload + deploy script path for the requested host.
- Mistaking stale container-deployment files or systemd warnings for the active runtime; inspect the loaded `ExecStart`, active process/container, and recorded current image.
- Treating a transient startup `curl: connection refused` line inside a retrying smoke loop as deployment failure when the deploy command exits successfully. Always verify final state separately: `current-image`, `systemctl`, app container, local `/login`, and public HTTPS `/login`.
- Sourcing a root-only env file as an unprivileged service user during migrations/seeds.
- Repeatedly resetting a dev DB after a Prisma duplicate DDL failure without inspecting whether the baseline migration already contains the later schema.
- Mixing live cloud mutation, repo docs, and app implementation in one unreviewable change.
- Assuming `/opt/<app>/repo` is a live git checkout. Some VM deployments switch to git archives or release/image layouts while retaining the same path. Before running `git fetch`/`git reset` on a VM, verify `test -d .git`, inspect `.deployed-revision`, `systemctl show <service> -p ExecStart`, and any image/current-release files. If the service unit on disk differs from the loaded unit, run `systemctl daemon-reload` before interpreting status.
- Leaving host package PostgreSQL running after moving to Docker Compose PostgreSQL, causing port conflicts or ambiguous data source.

## Verification Checklist

- [ ] Provider CLI access verified with a read-only command.
- [ ] VM shape, disk, OS, region, and FQDN documented.
- [ ] Security group/firewall exposes only intended public ports.
- [ ] App runs under systemd and listens on localhost.
- [ ] nginx proxies from public 80/443 to localhost app port.
- [ ] Let's Encrypt certificate issuance and renewal timer documented or verified.
- [ ] PostgreSQL is Docker-managed or host-managed, not ambiguous, and not public.
- [ ] Database migration/seed commands are documented with environment scope.
- [ ] External HTTPS smoke test documented or executed.
- [ ] Stop/disable/teardown path documented.

## References

- `references/tencent-cloud-linux-vm-deployment.md` — Tencent Cloud / `tccli` patterns and VM deployment notes from a successful session.
