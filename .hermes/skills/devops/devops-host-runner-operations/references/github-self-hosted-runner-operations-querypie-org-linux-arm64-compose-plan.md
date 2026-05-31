# QueryPie Org Linux ARM64 Docker Compose Runner Plan

Session-specific example from Mac Studio LLM1 (`qp-test@10.11.1.11`). Keep this as a concrete reference, not a universal default.

## Context

- Target host: `Mac-Studio-LLM1.local`
- SSH user: `qp-test`
- Target directory: `/Users/qp-test/Workspace/github-runners-for-querypie-org`
- Existing sibling fleet: `/Users/qp-test/Workspace/github-runner`
- Existing Docker CLI path issue: non-interactive SSH did not include `/usr/local/bin`; fixed via `~/.zshenv` dynamic prepend:

```zsh
# Hermes non-interactive SSH PATH: make Homebrew/Docker CLI shims available to non-login zsh.
case ":$PATH:" in
  *:/usr/local/bin:*) ;;
  *) export PATH="/usr/local/bin:$PATH" ;;
esac
```

## User Constraints

- Do not auto-proceed when the user is guiding runner setup; report planned configuration first.
- Use Docker Compose for start/stop/restart operations.
- Configure only 6 runners initially, not 12.
- GitHub organization is `querypie`, completely separate from existing `chequer-io` runners.
- No macOS native runner is planned.
- Runner Group should represent the Linux ARM64 host/fleet, not the org.

## Proposed GitHub Runner Configuration

Runner group:

- `mac-studio-llm1-linux-arm64`

Runner names:

- `mac-studio-llm1-linux-arm64-1`
- `mac-studio-llm1-linux-arm64-2`
- `mac-studio-llm1-linux-arm64-3`
- `mac-studio-llm1-linux-arm64-4`
- `mac-studio-llm1-linux-arm64-5`
- `mac-studio-llm1-linux-arm64-6`

Labels:

- All six:
  - `arch:arm64`
  - `os:ubuntu`
  - `build:build-arm64`
  - `purpose:ci`
- Runners 1-3 additionally:
  - `purpose:build`

Rationale:

- Jobs requiring `purpose:ci` can use all 6 runners.
- Jobs requiring `purpose:build` can use only runners 1-3.
- Because the organization is separate, no `org:querypie` label is needed.

## `.env` Shape

Do not print or store real registration tokens in notes.

```env
GITHUB_URL=https://github.com/
RUNNER_ORG=querypie
RUNNER_GROUPS=mac-studio-llm1-linux-arm64

RUNNER_LABELS_CI=arch:arm64,os:ubuntu,build:build-arm64,purpose:ci
RUNNER_LABELS_BUILD=${RUNNER_LABELS_CI},purpose:build

# GitHub org runner registration token
# https://github.com/organizations/querypie/settings/actions/runners/new?arch=arm64&os=linux
RUNNER_TOKEN=<redacted>
```

## Compose Service Shape

```yaml
version: "3"

x-runner-common: &runner-common
  platform: linux/arm64
  build:
    context: .
  env_file:
    - .env
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  privileged: true
  restart: unless-stopped
  group_add:
    - "0"

services:
  runner-1:
    environment:
      - RUNNER_NAME=mac-studio-llm1-linux-arm64-1
      - RUNNER_LABELS=${RUNNER_LABELS_BUILD}
    <<: *runner-common

  runner-2:
    environment:
      - RUNNER_NAME=mac-studio-llm1-linux-arm64-2
      - RUNNER_LABELS=${RUNNER_LABELS_BUILD}
    <<: *runner-common

  runner-3:
    environment:
      - RUNNER_NAME=mac-studio-llm1-linux-arm64-3
      - RUNNER_LABELS=${RUNNER_LABELS_BUILD}
    <<: *runner-common

  runner-4:
    environment:
      - RUNNER_NAME=mac-studio-llm1-linux-arm64-4
      - RUNNER_LABELS=${RUNNER_LABELS_CI}
    <<: *runner-common

  runner-5:
    environment:
      - RUNNER_NAME=mac-studio-llm1-linux-arm64-5
      - RUNNER_LABELS=${RUNNER_LABELS_CI}
    <<: *runner-common

  runner-6:
    environment:
      - RUNNER_NAME=mac-studio-llm1-linux-arm64-6
      - RUNNER_LABELS=${RUNNER_LABELS_CI}
    <<: *runner-common
```

## Operations

Run from `/Users/qp-test/Workspace/github-runners-for-querypie-org`:

```sh
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 runner-1
docker compose restart runner-1
docker compose restart
docker compose down
```

Verification:

- `docker compose ps` shows all six services Up.
- Logs show `Connected to GitHub` and `Listening for Jobs`.
- GitHub org settings show six online runners in `mac-studio-llm1-linux-arm64`.

## Token Handling

The user may provide a command like:

```sh
./config.sh --url https://github.com/querypie --token <redacted>
```

Treat the token as secret. Confirm only:

- org URL exists (`querypie`)
- target directory exists
- Docker is available
- actual token validity will be proven only at registration time
