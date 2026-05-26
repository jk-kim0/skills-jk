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

### Runner-by-runner wiki reporting

When the user asks to document resource usage across several self-hosted runners in a GitHub wiki, prefer a runner-by-runner workflow instead of drafting one monolithic page:

1. Clone or reuse the wiki repo in the expected workspace location.
2. Investigate one runner.
3. Create or update that runner's separate wiki detail page.
4. Update the main status page as an index with the runner link and short reclaimable-resource summary.
5. Commit and push that runner's wiki update before moving to the next runner.
6. If a runner cannot be accessed, still create its page with GitHub metadata, QueryPie/SSH probe evidence, and a clear "not collected; do not estimate" statement.

7. When revisiting a runner after access or evidence changes, remove stale failed-probe notes and update the page/index to reflect the verified account and current resource findings; do not leave obsolete workaround guesses in the wiki.

For the querypie-mono runner audit page shape, QueryPie IP/account mapping, `/actions-runner` disk-usage interpretation, browser inventory fallback, timeout-bounded remote probes, and local raw-output hygiene, see `references/querypie-mono-runner-resource-audit.md`. For a reusable read-only remote disk probe, use `scripts/actions-runner-disk-probe.sh`.

For llm1 Mac Studio disk-full checks, see `references/mac-studio-llm1-disk-full-healthcheck.md`. Important pattern: verify host disk and inode availability, Docker Desktop/container filesystem availability, disk-pressure strings in native and container runner logs, and GitHub API online/busy status before concluding. Treat large Docker BuildKit/dangling volume reclaimable space as a preventive cleanup signal, not as proof of an active disk-full outage.

For front-of-page querypie-mono self-hosted runner inventory/status tables, see `references/querypie-mono-runner-inventory-status-table.md`. Important pattern: put a compact Runner / Hostname / IP Address / OS table before investigation prose, use physical host hostname rather than container hostname, and mark rows not live-verified instead of guessing.

For scheduled cleanup workflows that must ensure `runner:<runner-name>` labels exist before cleanup runs, see `references/scheduled-runner-cleanup-label-bootstrap.md`. Key pattern: keep label mutation in a separate manual workflow using a runner-writable org token such as `ORG_RUNNER_WRITABLE_TOKEN`, then have the scheduled cleanup workflow dispatch that workflow first with `actions: write`, wait for it with `gh run watch --exit-status`, and gate cleanup on success while leaving manual cleanup dispatch unchanged.

For CodeQL cache investigations on shared self-hosted runner pools, see `references/codeql-toolcache-on-shared-self-hosted-runners.md`. Important pattern: a target repository's CodeQL workflow may be disabled while other repositories sharing the same runner labels still schedule CodeQL and refresh `_work/_tool/CodeQL`.

For runner-targeted maintenance/cleanup workflows, see `references/runner-targeted-cleanup-workflows.md`. Important pattern: GitHub Actions cannot target a runner by runner name unless that runner name is also present as a custom label such as `runner:SVR-L2-RUNNER-1`; for destructive cleanup jobs, pass the expected runner name into the script and refuse cleanup if `RUNNER_NAME` does not match. The reference also includes a compact `ensure-runner-name-labels.yaml` workflow pattern using an org runner-write token and the actionlint-safe jq quoting form.

For a minimal workflow that provisions missing `runner:<runner-name>` labels using an organization runner-write token such as `ORG_RUNNER_WRITABLE_TOKEN`, see `references/runner-name-label-sync-workflow.md`. Important pattern: repository `GITHUB_TOKEN` cannot mutate org self-hosted runner labels; use a fine-grained PAT/App token with `Self-hosted runners: Read and write`, keep workflow `permissions: {}`, add labels with `POST /labels`, and bind `.runners[] as $runner` in `gh api --jq` so label-array context does not break `"runner:" + $runner.name`.

For repository-managed querypie-mono self-hosted runner cache cleanup workflows, see `references/querypie-mono-runner-cache-cleanup-workflow.md`. Key pattern: querypie-mono uses `develop` as the default branch; keep the workflow as a thin wrapper in `.github/workflows`, place the cleanup bash script in the same directory, default manual runs to dry-run, and assume every target runner has a stable custom label shaped `runner:<runner-name>`. Manual runs should accept `runner_names` as a JSON array, so operators can target one runner (`["SVR-L2-RUNNER-1"]`) or many runners. Prefer a `resolve-runners` job that makes event behavior explicit: `workflow_dispatch` outputs the operator-provided `runner_names`, while `schedule` outputs the full known Linux runner-name list. Keep the scheduled runner inventory legible by listing one runner per heredoc line and converting it with `jq -Rcn '[inputs | select(length > 0)]'`; do not store the whole schedule inventory as one long JSON string, and do not use `jq -Rcns` because `-s` slurps all lines into one newline-containing string. The cleanup job should consume `needs.resolve-runners.outputs.runner_names` as its matrix with `runs-on: ["self-hosted", "runner:${{ matrix.runner_name }}"]` and `fail-fast: false`. Do not rely on `workflow_dispatch` input defaults for schedule behavior, because scheduled events have no `github.event.inputs`. Once exact `runner:<name>` labels are used, remove redundant in-script `RUNNER_NAME` mismatch guards and `TARGET_RUNNER_NAME` plumbing; GitHub's label matcher is the targeting mechanism. Schedule weekly cleanup for Saturday 02:00 KST (`0 17 * * 5` UTC). Use aligned, verb-first workflow naming when the workflow is an operation: e.g. file `.github/workflows/clean-up-self-hosted-runner-cache.yaml`, `name: "Clean Up Self-hosted Runner Cache"`, and `run-name: "🧹 Clean Up Self-hosted Runner Cache"`; put the broom emoji in `run-name` rather than `name` when the user wants it to sort lower in run lists. Do not expose Docker cleanup as a workflow input: the script should auto-skip Docker prune on containerized/shared-daemon runners (`SVR-L3-DOCKERIZED-*`, `SVR-L3-MINI-*`, `SVR-MS-ARM-*`, cgroup/container markers, unknown names) and allow it only on known native VM runners (`SVR-L2-RUNNER-1..6`, `SVR-L3-RUNNER-1..2`). Do not expose retention/pruning knobs as `workflow_dispatch` options; keep them as script defaults/env constants instead: `_work/_temp` retention 8 days / 192 hours, Docker prune retention 72 hours / 3 days when auto-allowed, non-CodeQL toolcache versions 5 recent versions for `go`, `node`, Java, Python, and `uv`, CodeQL 1 recent version, and optional workspace cleanup off by default because it deletes repository checkout directories rather than disposable cache. For CI parity, run the repo lint check that includes actionlint (for example `MISE_TRUSTED_CONFIG_PATHS="$PWD" mise r check -o quiet -f`) after workflow edits, and grep all related workflow files plus PR text for stale retention wording such as `24h` / `24시간`, stale label-pool wording, stale mismatch-guard wording, or stale workflow filenames/titles before reporting completion.

## Common Pitfalls

- For runner-root disk investigations, do not assume large `/actions-runner` usage is logs. Measure `_work`, `_work/_tool`, repo `.git` directories, `_work/_temp`, `_diag`, and versioned `bin.*`/`externals.*` separately; logs may be cleanup candidates but are often not the dominant cause.
- For Docker Desktop-backed macOS runner fleets, host `df` alone is insufficient. Also `docker exec` into runner containers and check `df -h / /runner /home/runner`, because the Docker VM/container filesystem can be much tighter than the macOS host filesystem. Cross-check recent container logs for `ENOSPC`/`no space left` before calling a disk-full condition active.
- Do not overstate Docker reclaimable volume/cache usage as an outage. `docker system df` may show hundreds of GB reclaimable from BuildKit/dangling volumes while all runners are online and container filesystems still have ample free space; report this as preventive cleanup capacity unless logs or `df` show active pressure.
- When adding or expanding manual runner-maintenance workflows, remember GitHub Actions enforces a hard maximum of 10 `workflow_dispatch` inputs. If actionlint reports `maximum number of inputs for "workflow_dispatch" event is 10`, preserve the important operator controls and demote less-used retention knobs to script defaults or env fallbacks. Re-run the repo's actual lint command (for querypie-mono, `MISE_TRUSTED_CONFIG_PATHS="$PWD" mise r check -o quiet -f`) before pushing the fix.
- Do not assume every Linux runner uses `ubuntu` or `/home/ubuntu/actions-runner`. Read the existing runner page or host metadata first; some QueryPie L3 runners use `deploy` with `/home/deploy/actions-runner`.
- When `_work/_temp` contains large cache archives during manual investigation, distinguish current-job artifacts from stale orphans. For a cleanup workflow that is itself running on the target self-hosted runner instance, the runner instance is already exclusively occupied by that job; no separate same-runner busy check is needed for runner-local paths. Keep the default retention conservative when the user asks, e.g. querypie-mono uses 8 days / 192 hours.
- Do not confuse runner-instance exclusivity with host exclusivity: one host can run multiple runner instances/containers. Runner-local cleanup is safe under the active job, but Docker daemon pruning is host-wide and can affect sibling runner instances sharing that daemon. Also do not overclaim the reverse: in Docker fleets where each runner container has a separate `/runner` volume, cleaning one container's `/runner/_work` does not directly delete sibling runner workspaces; leave optional workspace cleanup disabled by default because repository checkouts are broader and less disposable than cache/temp directories, not because sibling workspaces are necessarily shared.
- For `_work/_tool/CodeQL`, do not decide from the current repository alone. First check whether other repositories sharing the same self-hosted labels still run scheduled CodeQL; a disabled CodeQL workflow in one repo does not make runner-local CodeQL toolcache obsolete.
- When CodeQL is still used somewhere in the shared runner pool, prefer version pruning (keep latest 1-2 versions) over full `_work/_tool/CodeQL` deletion; full deletion is correct but can slow and redownload future CodeQL jobs.
- When scheduled cleanup workflows need a preflight label-sync workflow, keep the workflow chain explicit: scheduled cleanup dispatches the label-sync workflow, waits for its run to finish, and gates cleanup on success. Do not treat `gh workflow run` success as proof that the dispatched workflow succeeded.
- `actionlint` runs ShellCheck on embedded workflow scripts. If a jq filter uses jq variables such as `$runner`, single quotes can trigger SC2016. Prefer a double-quoted jq filter with escaped jq variables (`\$runner`) in workflow shell blocks.
- Stopping after `ps` and missing Docker Compose runner fleets. Check both native processes and containers.
- Treating `State=running` as healthy without checking `RestartCount` and logs. A runner can be repeatedly restarting/reconfiguring while briefly showing running; inspect `docker inspect ... RestartCount` and grep logs for `Connected to GitHub`, `Listening for Jobs`, `Cannot configure`, and `Configuration failed`.
- For a single corrupt Docker runner service, do not disrupt the full fleet. Prefer updating the registration token, then `docker compose rm -sfv <service>`, `docker compose create <service>`, and `docker compose start <service>` for only the affected service; verify it reaches `Listening for Jobs`.
- Assuming Docker is unavailable because `docker` is not in non-interactive SSH PATH. Try `/usr/local/bin/docker`, `/opt/homebrew/bin/docker`, and Docker.app paths on macOS.
- Printing `.env` or `.credentials` raw. Always redact tokens and credential-like keys.
- Treating compose files as active without checking `docker compose ps` or `docker ps -a`.
- Treating old compose backups as current source of truth. Prefer running containers and current compose file, but mention backups separately if relevant.
- `.runner` may have UTF-8 BOM; parse with `encoding='utf-8-sig'`.

## References

- `references/mac-studio-llm1-runner-audit.md` — concrete Mac Studio LLM1 example with one launchd macOS runner and a 12-container Docker Compose Linux ARM64 runner fleet.
- `references/mac-studio-llm1-querypie-org-runner-recovery.md` — concrete recovery pattern for a single QueryPie org Docker runner stuck in a restart/configuration loop because its anonymous `/runner` volume is corrupt; update token, remove only that service with `docker compose rm -sfv`, recreate/start, and verify `Listening for Jobs`.
- `references/querypie-org-linux-arm64-compose-plan.md` — concrete plan for a separate QueryPie org Linux ARM64 Docker Compose fleet with 6 runners, host-specific runner group, and split CI/build labels.
- `references/querypie-org-linux-arm64-compose-install.md` — concrete install outcome and verification commands for the QueryPie org six-runner Docker Compose fleet on Mac Studio LLM1.
- `references/querypie-mono-runner-resource-audit.md` — querypie-mono wiki audit pattern: one runner per page, main status index, QueryPie inventory mapping, bounded remote resource probes, and access-blocked runner documentation.
- `references/querypie-mono-runner-inventory-status-table.md` — querypie-mono wiki front-of-page inventory/status table pattern covering runner name, physical host hostname, IP address, OS, execution form, and verification caveats.
