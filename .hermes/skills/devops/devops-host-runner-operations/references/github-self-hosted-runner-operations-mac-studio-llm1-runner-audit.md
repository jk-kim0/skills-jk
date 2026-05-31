# Mac Studio LLM1 GitHub runner audit example

This reference captures a concrete remote audit pattern for `qp-test@10.11.1.11` / `Mac-Studio-LLM1.local`. It intentionally omits and redacts credential/token contents.

## Host

- SSH target: `qp-test@10.11.1.11`
- hostname: `Mac-Studio-LLM1.local`
- OS: macOS 26.2 arm64

## Native macOS runner

Active runner root:

```text
/Users/qp-test/actions-runner
```

Observed active processes:

```text
/Users/qp-test/actions-runner/runsvc.sh
/Users/qp-test/actions-runner/bin/Runner.Listener run --startuptype service
```

LaunchAgent:

```text
/Users/qp-test/Library/LaunchAgents/actions.runner.chequer-io.Dev-MacStudio.plist
```

Key plist fields:

```text
Label: actions.runner.chequer-io.Dev-MacStudio
ProgramArguments: /Users/qp-test/actions-runner/runsvc.sh
WorkingDirectory: /Users/qp-test/actions-runner
RunAtLoad: true
UserName: qp-test
StandardOutPath: /Users/qp-test/Library/Logs/actions.runner.chequer-io.Dev-MacStudio/stdout.log
StandardErrorPath: /Users/qp-test/Library/Logs/actions.runner.chequer-io.Dev-MacStudio/stderr.log
EnvironmentVariables: ACTIONS_RUNNER_SVC=1
```

Runner metadata from `.runner` / `.runner_migrated`:

```text
agentId: 15614
agentName: Dev-MacStudio
poolId: 9
poolName: inhouse-baremetal
gitHubUrl: https://github.com/chequer-io
workFolder: _work
useV2Flow: true
serverUrlV2: https://broker.actions.githubusercontent.com/
```

Runner version and symlinks:

```text
bin -> /Users/qp-test/actions-runner/bin.2.334.0
externals -> /Users/qp-test/actions-runner/externals.2.334.0
Runner.Listener --version: 2.334.0
```

Native runner work/log locations:

```text
/Users/qp-test/actions-runner/_work
/Users/qp-test/actions-runner/_diag
/Users/qp-test/Library/Logs/actions.runner.chequer-io.Dev-MacStudio/
```

Native `_work` had repo work directories including:

```text
querypie-mono
querypie-engine-backend
duplo-go-sdk
duplo
```

Management commands:

```sh
cd /Users/qp-test/actions-runner && ./svc.sh status
cd /Users/qp-test/actions-runner && ./svc.sh stop
cd /Users/qp-test/actions-runner && ./svc.sh start
```

## Docker Compose Linux ARM64 runner fleet

Active compose root:

```text
/Users/qp-test/Workspace/github-runner
```

Files:

```text
/Users/qp-test/Workspace/github-runner/docker-compose.yaml
/Users/qp-test/Workspace/github-runner/Dockerfile
/Users/qp-test/Workspace/github-runner/.env
/Users/qp-test/Workspace/github-runner/.env.bak
/Users/qp-test/Workspace/github-runner/docker-compose.yaml.0204
```

Important pitfall: non-interactive SSH shell did not have `docker` in PATH, but Docker was available at:

```text
/usr/local/bin/docker
/Applications/Docker.app/Contents/Resources/bin/docker
```

Use:

```sh
cd /Users/qp-test/Workspace/github-runner && /usr/local/bin/docker compose ps
```

Active containers observed:

```text
github-runner-runner-1-1
github-runner-runner-2-1
github-runner-runner-3-1
github-runner-runner-4-1
github-runner-runner-5-1
github-runner-runner-6-1
github-runner-runner-7-1
github-runner-runner-8-1
github-runner-runner-9-1
github-runner-runner-10-1
github-runner-runner-11-1
github-runner-runner-12-1
```

Status:

```text
all containers Up 4 days
restart policy: unless-stopped
Privileged: true
Docker socket mounted: /var/run/docker.sock:/var/run/docker.sock
```

Registration target and group from env/inspect:

```text
GITHUB_URL=https://github.com/
RUNNER_ORG=chequer-io
RUNNER_GROUPS=inhouse-baremetal
```

Runner names:

```text
SVR-MS-ARM-RUNNER-1 through SVR-MS-ARM-RUNNER-12
```

Label groups:

```text
RUNNER_LABELS_BASE=arch:arm64,os:ubuntu,build:build-arm64,purpose:build
RUNNER_LABELS_ACP=${RUNNER_LABELS_BASE},purpose:acp-arm64
```

Current distribution:

```text
runner-1: base labels
runner-2..runner-6: base + purpose:acp-arm64
runner-7..runner-12: base labels
```

Dockerfile base:

```text
FROM --platform=linux/arm64 summerwind/actions-runner:v2.328.0-ubuntu-22.04
```

Dockerfile notable tools/cache:

```text
docker-buildx
git, git-lfs
gh CLI
yq
RUNNER_TOOL_CACHE=/home/runner/cache
WORKDIR /runner
```

Compose management commands:

```sh
cd /Users/qp-test/Workspace/github-runner && /usr/local/bin/docker compose ps
cd /Users/qp-test/Workspace/github-runner && /usr/local/bin/docker compose restart runner-2
cd /Users/qp-test/Workspace/github-runner && /usr/local/bin/docker compose down
cd /Users/qp-test/Workspace/github-runner && /usr/local/bin/docker compose up -d
/usr/local/bin/docker logs github-runner-runner-2-1
```

## Secret-handling notes

The following files exist and contain or may contain secrets. Do not print raw contents:

```text
/Users/qp-test/actions-runner/.credentials
/Users/qp-test/actions-runner/.credentials_rsaparams
/Users/qp-test/Workspace/github-runner/.env
/Users/qp-test/Workspace/github-runner/.env.bak
```

The Docker `.env` includes `RUNNER_TOKEN`; redact it in all reports.
