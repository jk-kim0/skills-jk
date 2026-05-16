---
name: github-self-hosted-runner-operations
description: Inspect, document, and operate GitHub Actions self-hosted runners on remote hosts, including native service runners and Docker Compose runner fleets, while avoiding credential disclosure.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github-actions, self-hosted-runner, launchd, docker-compose, devops]
    related_skills: [ssh-host-access-probing, github-actions-hosted-runner-cancelled-job-diagnosis]
---

# GitHub Self-Hosted Runner Operations

## Overview

Use this skill when the user asks where GitHub Actions self-hosted runners are configured, whether they are running, how they are registered, or how to restart/operate them on a machine reachable over SSH.

Goal: separate active runner mechanisms from stale setup files, report exact paths and service/container names, and never print runner tokens or credential file contents.

## When to Use

- User asks to find or audit GitHub runner setup on a server/Mac/workstation.
- User asks how a self-hosted runner is configured or started.
- User asks whether a runner is native, launchd/systemd, Docker Compose, or containerized.
- User asks for runner names, groups, labels, work directories, logs, or restart commands.

If SSH reachability itself is uncertain, first use `ssh-host-access-probing` to confirm login and remote command execution.

## Safety Rules

1. Do not print secrets. Treat these as sensitive:
   - `.credentials`, `.credentials_rsaparams`, `.runner` fields with token/secret/key/password names
   - `.env` values like `RUNNER_TOKEN`, `GITHUB_TOKEN`, PATs, passwords, secrets
   - container environment variables containing token/secret/key/password/credential
2. Prefer metadata: paths, filenames, sizes, hashes, service names, labels, runner names, groups, status.
3. Use redaction filters for config/env output.
4. Avoid restarting or changing runners unless explicitly requested; inspection is read-only by default.

## Native Runner Discovery

Run read-only probes over SSH:

```sh
ssh <user>@<host> '
set -e
printf "[host]\n"; hostname; whoami; pwd
printf "\n[runner processes]\n"
ps aux | grep -Ei "[a]ctions.runner|[r]unsvc|[r]un.sh|[a]ctions-runner|Runner.Listener|Runner.Worker" || true
printf "\n[launchctl user services matching github/actions/runner]\n"
launchctl list 2>/dev/null | grep -Ei "github|actions|runner" || true
printf "\n[LaunchAgents]\n"
for d in "$HOME/Library/LaunchAgents" /Library/LaunchAgents /Library/LaunchDaemons; do
  [ -d "$d" ] && { echo "-- $d"; find "$d" -maxdepth 1 -type f \( -iname "*github*" -o -iname "*actions*" -o -iname "*runner*" \) -print; }
done
printf "\n[top-level likely runner dirs under home]\n"
find "$HOME" -maxdepth 3 -type d \( -iname "actions-runner" -o -iname "*runner*" -o -iname "_work" \) 2>/dev/null | sed -n "1,120p"
'
```

For a candidate runner root:

```sh
ssh <user>@<host> '
RUNNER="$HOME/actions-runner"
PLIST="$HOME/Library/LaunchAgents/actions.runner.<org>.<name>.plist"
ls -la "$RUNNER" | sed -n "1,120p"
/usr/bin/plutil -p "$PLIST" 2>/dev/null || sed -n "1,200p" "$PLIST"
[ -f "$RUNNER/.service" ] && sed -n "1,120p" "$RUNNER/.service" || true
[ -f "$RUNNER/.env" ] && sed -E "s/^([^#=]*(TOKEN|PAT|PASSWORD|SECRET|KEY|CREDENTIAL)[^=]*)=.*/\1=<redacted>/Ig" "$RUNNER/.env" || true
[ -f "$RUNNER/.path" ] && sed -n "1,30p" "$RUNNER/.path" || true
cd "$RUNNER" && ./svc.sh status || true
cd "$RUNNER" && printf "bin -> "; readlink bin; printf "externals -> "; readlink externals; ./bin/Runner.Listener --version 2>/dev/null || true
find "$RUNNER/_work" -maxdepth 2 -mindepth 1 -type d 2>/dev/null | sed -n "1,160p"
ls -lt "$RUNNER/_diag" 2>/dev/null | sed -n "1,30p"
'
```

### Redacted `.runner` parser

GitHub runner JSON files can contain a UTF-8 BOM. Use `utf-8-sig`:

```sh
python3 - <<'PY'
import json, pathlib
p=pathlib.Path('/path/to/actions-runner/.runner')
data=json.loads(p.read_text(encoding='utf-8-sig'))
for k in list(data):
    if any(s in k.lower() for s in ['token','secret','key','password','credential','oauth']):
        data[k] = '<redacted>'
print(json.dumps(data, indent=2, ensure_ascii=False))
PY
```

## Docker Compose Runner Fleet Discovery

Search for compose-managed runner directories:

```sh
ssh <user>@<host> '
find "$HOME" -maxdepth 4 \( -name "docker-compose.yml" -o -name "docker-compose.yaml" -o -name "compose.yml" -o -name "compose.yaml" \) 2>/dev/null | grep -Ei "runner|github|actions" || true
'
```

On macOS, non-interactive SSH shells may not have Docker in PATH. Probe common paths and use an absolute binary:

```sh
ssh <user>@<host> '
for p in /usr/local/bin/docker /opt/homebrew/bin/docker /Applications/Docker.app/Contents/Resources/bin/docker "$HOME/.docker/bin/docker"; do
  [ -x "$p" ] && echo "$p"
done
DOCKER=""
for p in /usr/local/bin/docker /opt/homebrew/bin/docker /Applications/Docker.app/Contents/Resources/bin/docker "$HOME/.docker/bin/docker"; do
  [ -x "$p" ] && { DOCKER="$p"; break; }
done
[ -n "$DOCKER" ] && "$DOCKER" --version
[ -n "$DOCKER" ] && "$DOCKER" ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep -Ei "runner|github|actions|NAMES" || true
'
```

Inspect compose status and config without leaking tokens:

```sh
ssh <user>@<host> '
DOCKER=/usr/local/bin/docker
cd "$HOME/Workspace/github-runner"
$DOCKER compose ps -a
$DOCKER compose config 2>/dev/null | sed -E "s/(RUNNER_TOKEN: ).*/\1<redacted>/; s/(GITHUB_TOKEN: ).*/\1<redacted>/"
'
```

Inspect live container metadata:

```sh
ssh <user>@<host> '
DOCKER=/usr/local/bin/docker
for c in $($DOCKER ps --format "{{.Names}}" | grep -Ei "runner|github|actions"); do
  echo "-- $c"
  $DOCKER inspect "$c" --format "Image={{.Config.Image}} Cmd={{json .Config.Cmd}} Restart={{.HostConfig.RestartPolicy.Name}} Privileged={{.HostConfig.Privileged}}"
  $DOCKER inspect "$c" --format "{{range .Config.Env}}{{println .}}{{end}}" |
    grep -E "^(RUNNER_NAME|RUNNER_LABELS|RUNNER_ORG|RUNNER_GROUPS|GITHUB_URL|RUNNER_WORKDIR|RUNNER_SCOPE|RUNNER_REPLACE_EXISTING)=" |
    sed -E "s/(TOKEN|PAT|PASSWORD|SECRET|KEY|CREDENTIAL)(=[^ ]*)/\1=<redacted>/Ig" | sort
  $DOCKER inspect "$c" --format "Mounts={{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}"
done
'
```

## Planning a New Docker Compose Runner Fleet

When the user is designing or adding runners, do not jump directly to registration or `docker compose up` unless explicitly instructed. Runner setup has short-lived credentials and org-side prerequisites, so first report the exact configuration plan and wait for the user's guide/confirmation when they are actively steering.

Recommended plan shape:

1. Directory and files:
   - Compose project directory, e.g. `$HOME/Workspace/github-runners-for-<org>`.
   - `Dockerfile` copied from a known-good existing fleet when the user wants parity.
   - `docker-compose.yaml` for services.
   - `.env` for org, runner group, labels, and registration token.
   - `.env.example` and `.gitignore` if the directory may be versioned; never commit `.env` with `RUNNER_TOKEN`.
2. GitHub org and runner group:
   - Confirm `RUNNER_ORG` and whether the group already exists or will be created by the user.
   - For host-specific Linux ARM64 fleets, a clear group name is like `mac-studio-llm1-linux-arm64`.
   - If the org is completely separate from existing runners, do not add org-distinguishing labels; runner group separates ownership.
3. Runner names:
   - Use deterministic names with host, OS, arch, and index, e.g. `mac-studio-llm1-linux-arm64-1` through `-6`.
   - Avoid reusing names from another org/fleet unless the user asks.
4. Labels:
   - Keep labels environment/purpose focused, e.g. `arch:arm64`, `os:ubuntu`, `build:build-arm64`, `purpose:ci`, `purpose:build`.
   - Multiple purpose labels are allowed on one runner.
   - GitHub label matching is AND: a job requiring `purpose:build` only matches runners that have that label.
   - A useful split for six runners is: all six get `purpose:ci`; runners 1-3 additionally get `purpose:build`.
5. Operations:
   - Start: `docker compose up -d --build`
   - Stop: `docker compose down`
   - Restart all: `docker compose restart`
   - Restart one: `docker compose restart runner-1`
   - Status: `docker compose ps`
   - Logs: `docker compose logs --tail=100 runner-1`
6. Verification:
   - `docker compose ps` shows all intended services Up.
   - Logs show `Connected to GitHub` and `Listening for Jobs`.
   - GitHub org settings show the runner names online in the expected runner group with expected labels.

Registration token handling:

- Treat `./config.sh --url ... --token ...` snippets as containing secrets. Do not echo the token back to the user or write it into docs.
- A registration token's real validity is proven only by registration; read-only checks can confirm the org URL, target directory, Docker availability, and token-shaped input.
- Because registration tokens expire quickly, once the user approves actual setup, write `.env` and run Compose promptly.

## Reporting Pattern

Separate the report into:

1. Host identity and access user.
2. Active native runner(s): root path, service manager, service name, version, runner name, org/repo, group, work folder, logs, status, restart commands.
3. Active container runner fleet: compose directory, compose files, number of containers, runner names, labels, group, restart policy, mounts, status.
4. Planned new runner fleet, if applicable: directory, files, org, group, runner names, labels, and exact Compose operations — but no secret values.
5. Stale or auxiliary setup files: keep distinct from active processes/containers.
6. Sensitive files found but not printed.
7. Exact commands for safe follow-up status/log checks.

## Common Pitfalls

- Stopping after `ps` and missing Docker Compose runner fleets. Check both native processes and containers.
- Assuming Docker is unavailable because `docker` is not in non-interactive SSH PATH. Try `/usr/local/bin/docker`, `/opt/homebrew/bin/docker`, and Docker.app paths on macOS.
- Printing `.env` or `.credentials` raw. Always redact tokens and credential-like keys.
- Treating compose files as active without checking `docker compose ps` or `docker ps -a`.
- Treating old compose backups as current source of truth. Prefer running containers and current compose file, but mention backups separately if relevant.
- `.runner` may have UTF-8 BOM; parse with `encoding='utf-8-sig'`.

## References

- `references/mac-studio-llm1-runner-audit.md` — concrete Mac Studio LLM1 example with one launchd macOS runner and a 12-container Docker Compose Linux ARM64 runner fleet.
- `references/querypie-org-linux-arm64-compose-plan.md` — concrete plan for a separate QueryPie org Linux ARM64 Docker Compose fleet with 6 runners, host-specific runner group, and split CI/build labels.
- `references/querypie-org-linux-arm64-compose-install.md` — concrete install outcome and verification commands for the QueryPie org six-runner Docker Compose fleet on Mac Studio LLM1.
