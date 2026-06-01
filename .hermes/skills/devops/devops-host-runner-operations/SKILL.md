---
name: devops-host-runner-operations
description: Use when probing SSH access to remote hosts or operating GitHub Actions self-hosted runners on those hosts, with layered reachability diagnosis, safe remote inspection, and secret-redacted runner reporting.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, ssh, remote-hosts, github-actions, self-hosted-runner, docker-compose]
    related_skills: [systematic-debugging, github-actions-hosted-runner-cancelled-job-diagnosis]
---

# DevOps Host and Runner Operations

## Overview

Use this umbrella for remote-host operational work that begins with proving access and often continues into GitHub Actions self-hosted runner inspection or maintenance. Treat SSH reachability, authentication, remote command execution, service/container state, and GitHub runner health as separate layers.

This skill consolidates two recurring classes that are usually part of the same maintenance workflow:

- **Host access probing** — answer whether a named machine, SSH alias, workstation, Mac, server, or IP is reachable from the current Hermes runtime.
- **Self-hosted runner operations** — inspect, document, restart, or plan GitHub Actions self-hosted runners, including native launchd/systemd services and Docker Compose runner fleets.

## When to Use

- User asks whether a machine/SSH alias is reachable, or asks which SSH key/account works.
- User asks to verify access before remote work.
- User asks where GitHub Actions self-hosted runners are configured, whether they are running, or how to restart/operate them.
- User asks for runner names, groups, labels, work directories, logs, cleanup workflows, or resource usage on runner hosts.
- A runner task starts with uncertain network/VPN/DNS/SSH state.
- User asks to verify read-only operational state on a VM-hosted app where the first step is still proving the correct SSH target, service/container state, or local-only database reachability. For a concrete PostgreSQL schema/seed verification pattern, see `references/tencent-vm-postgres-schema-seed-verification.md`.

Do not use this for application deployment or deep service debugging after host access and runner context are no longer central. When the task moves from SSH reachability into nginx/Let's Encrypt certificate issuance or HTTPS smoke verification, switch to `linux-host-tls-certbot-nginx`.

## Safety Rules

1. Default to read-only inspection. Do not restart services, prune Docker, mutate GitHub runner labels, or register runners unless the user explicitly asks.
2. Never print secrets. Redact `.credentials`, `.credentials_rsaparams`, `.runner` secret-like fields, `.env` tokens, PATs, passwords, keys, and container environment variables containing credential-like names.
3. Use short timeouts and `BatchMode=yes` for SSH probes so the agent does not hang on interactive password prompts.
4. Separate facts from inferences: an SSH alias is not access; `nc` success is not authentication; `docker ps` running is not runner health.

## Phase 1: Layered SSH / Host Access Probe

Run a compact, non-destructive probe when the target host name is clear:

```sh
pwd
hostname
ssh -G <host> 2>/dev/null | sed -n '1,40p'
ssh -o BatchMode=yes -o ConnectTimeout=5 <host> 'hostname; uname -a'
```

Interpret results by layer:

- `ssh -G <host>` succeeds: OpenSSH can expand config for the alias; it does not prove DNS or login.
- `Could not resolve hostname`: name resolution failed in this runtime.
- `Connection timed out` / `No route to host`: network path or firewall problem.
- `Permission denied` with `BatchMode=yes`: host resolved and SSH answered, but non-interactive auth failed.
- Remote `hostname; uname -a` output: remote command execution is confirmed.

If resolution fails but local/VPN access is expected, inspect static mappings and SSH config before asking the user for an IP:

```sh
grep -nE '<host>|<host-alias>|mac.?studio|studio|llm|<expected-subnet>' /etc/hosts 2>/dev/null || true
grep -RniE '<host>|<host-alias>|mac.?studio|studio|llm|HostName[[:space:]]+[0-9]' ~/.ssh/config ~/.ssh/config.d 2>/dev/null || true
dscacheutil -q host -a name <candidate-hostname> 2>/dev/null || true
```

For Tencent Cloud CVMs, do not stop at an SSH timeout when Security Group ingress is intentionally narrow. Check Tencent Automation Tools (TAT) agent state if `tccli` credentials are available:

```sh
tccli tat DescribeAutomationAgentStatus --region <region> --Filters '[{"Name":"instance-id","Values":["<instance-id>"]}]'
```

If TAT is `Online` and the requested operation is an explicit host-level maintenance action, `tccli tat RunCommand` can be the correct operational path even when direct SSH from the agent runtime is blocked. Query `DescribeInvocationTasks --HideOutput False` afterward and report the command exit code plus redacted output evidence.

For an IP address, separate routing, port reachability, and auth:

```sh
route -n get <ip> 2>/dev/null | sed -n '1,40p' || true
nc -vz -G 3 <ip> 22
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectionAttempts=1 -o ConnectTimeout=3 <user>@<ip> 'hostname; uname -a'
```

When the user asks which SSH key works, enumerate plausible private keys without printing key material and test them with `BatchMode=yes`, `IdentitiesOnly=yes`, `PreferredAuthentications=publickey`, and short timeouts. The deliverable is the verified account, host/IP, key path, and copy-pasteable SSH command.

## Phase 2: Native Runner Discovery

Once host access is confirmed, search for native GitHub runner mechanisms:

```sh
ssh <user>@<host> '
set -e
printf "[host]\n"; hostname; whoami; pwd
printf "\n[runner processes]\n"
ps aux | grep -Ei "[a]ctions.runner|[r]unsvc|[r]un.sh|[a]ctions-runner|Runner.Listener|Runner.Worker" || true
printf "\n[launchctl/system services matching github/actions/runner]\n"
launchctl list 2>/dev/null | grep -Ei "github|actions|runner" || true
systemctl --user list-units 2>/dev/null | grep -Ei "github|actions|runner" || true
systemctl list-units 2>/dev/null | grep -Ei "github|actions|runner" || true
printf "\n[likely runner dirs]\n"
find "$HOME" -maxdepth 3 -type d \( -iname "actions-runner" -o -iname "*runner*" -o -iname "_work" \) 2>/dev/null | sed -n "1,120p"
'
```

For each candidate runner root, report path, service manager, service name, runner version, runner name/org/repo/group, work folder, diagnostic logs, and restart command. Parse `.runner` with `utf-8-sig` and redact credential-like fields.

## Phase 3: Docker Compose Runner Fleet Discovery

Do not stop after native process checks. Look for compose-managed runner fleets and Docker availability outside the non-interactive SSH PATH:

```sh
ssh <user>@<host> '
find "$HOME" -maxdepth 4 \( -name "docker-compose.yml" -o -name "docker-compose.yaml" -o -name "compose.yml" -o -name "compose.yaml" \) 2>/dev/null | grep -Ei "runner|github|actions" || true
for p in /usr/local/bin/docker /opt/homebrew/bin/docker /Applications/Docker.app/Contents/Resources/bin/docker "$HOME/.docker/bin/docker"; do
  [ -x "$p" ] && echo "$p"
done
'
```

Inspect compose status and live containers with secret redaction. Include restart policy, runner labels, runner groups, workdir mounts, restart counts, and log signals such as `Connected to GitHub`, `Listening for Jobs`, `Cannot configure`, and `Configuration failed`.

## Phase 4: VM-Local App Database State Checks

When the user asks whether a VM-hosted app's PostgreSQL schema or seed data is present, keep the same layered access discipline and stay read-only unless asked to migrate/seed. Do not infer DB state from `/login` returning 200 or a rendered form with default credentials. Verify the database directly: container health, public table count/list, `_prisma_migrations`, row counts for login/user and core domain tables, and the deployed revision versus current repo migrations. If the FQDN resolves to a private IP or resets SSH, inspect repo workflows/infra docs for the canonical public SSH host and user before giving up. See `references/tencent-vm-postgres-schema-seed-verification.md` for a concrete Tencent VM/Postgres pattern.

## Phase 5: Runner Maintenance and Cleanup Workflows

For runner cache/disk cleanup workflows, target exact runners with stable custom labels shaped `runner:<runner-name>`. GitHub Actions cannot target a runner by runner name unless the name is also a label. For destructive cleanup, either rely on exact `runs-on: [self-hosted, runner:<name>]` or pass the expected runner name and refuse if `RUNNER_NAME` mismatches.

When labels are missing, keep mutation in a separate manual/preflight workflow using an org token with `Self-hosted runners: Read and write`; repository `GITHUB_TOKEN` cannot mutate org runner labels. Scheduled cleanup workflows should dispatch label-sync, wait for its run to complete, and gate cleanup on success.

For shared runner pools, distinguish runner-local cleanup from host-wide cleanup. Runner-local `_work/_temp` cleanup is safe while the runner is occupied by its own job; Docker daemon pruning is host-wide and can affect sibling runners sharing the daemon. Keep workspace checkout cleanup disabled by default unless explicitly requested.

## Reporting Pattern

Report in layers:

1. Current local context and SSH alias/config status.
2. Reachability/auth result with exact failure class or remote command output.
3. Active native runner(s): root path, service manager/name, version, labels/group, status/logs.
4. Active container runner fleet: compose directory/files, container count, runner names, labels, group, restart policy, mounts, health signals.
5. Planned or requested maintenance: exact operations and rollback/verification steps, with no secret values.
6. Stale or auxiliary setup files distinct from active mechanisms.
7. Follow-up commands for safe status/log checks.

## References

Session-specific details, host examples, and workflow snippets migrated from the absorbed skills live under `references/` and `scripts/` with `github-self-hosted-runner-operations-*` or `ssh-host-access-probing-*` prefixes.

## Common Pitfalls

- Treating an SSH alias as confirmed access. Always run a non-interactive remote command.
- Mislabeling DNS failure as credential failure.
- Hanging on interactive SSH auth; use `BatchMode=yes` and short timeouts.
- Assuming the current Hermes runtime is on the user's LAN/VPN.
- Stopping after `ps` and missing Docker Compose runner fleets.
- Treating `State=running` as healthy without checking restart counts and logs.
- Printing `.env`, `.credentials`, `.runner` secret-like fields, or registration tokens.
- Treating compose files as active without checking `docker compose ps` or `docker ps -a`.
- Assuming every Linux runner uses `ubuntu` or `/home/ubuntu/actions-runner`; verify account/path per host.
- Assuming `prisma migrate deploy` means seed data was populated. For reviewer/dev apps, verify seed rows directly and ensure automation runs the seed command when that is the expected contract.
- Resetting a deployed Prisma database to fix migration-history drift. If the actual schema already matches, prefer `prisma migrate resolve --applied` after schema verification and report any retained failed/rolled-back row.
- Debugging workflow SSH failures only from the operator workstation. Persistent self-hosted runners may need separate cloud security-group ingress for their own egress IP and fresh SSH config per run.
- For CodeQL toolcache cleanup, check whether other repositories sharing the same labels still run CodeQL before deleting.

## Verification Checklist

- [ ] Host access classified by layer: alias/config, DNS, network, auth, or remote command execution.
- [ ] SSH probes used short non-interactive timeouts.
- [ ] Native and Docker runner mechanisms both checked when runner operations are in scope.
- [ ] Secrets and token-like values redacted.
- [ ] Destructive operations avoided unless explicitly requested.
- [ ] Runner labels/groups/workdirs/log evidence reported with active vs stale sources separated.
