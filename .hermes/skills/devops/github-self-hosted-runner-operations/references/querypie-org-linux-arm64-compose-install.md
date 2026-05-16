# QueryPie Org Linux ARM64 Docker Compose Runner Install Outcome

Concrete session outcome from Mac Studio LLM1 (`qp-test@10.11.1.11`). Keep this as an example/reference for future runner fleet work, not as a universal default.

## Installed Location

- Host: `Mac-Studio-LLM1.local`
- SSH user: `qp-test`
- Directory: `/Users/qp-test/Workspace/github-runners-for-querypie-org`
- Docker CLI expected in non-interactive SSH via `/usr/local/bin/docker` and PATH configured in `~/.zshenv`.

Files created in the directory:

- `README.md` — Korean operational documentation; does not include token values.
- `Dockerfile` — copied from known-good sibling fleet `/Users/qp-test/Workspace/github-runner/Dockerfile`.
- `docker-compose.yaml` — six Compose services.
- `.env` — contains `RUNNER_TOKEN`; never print or commit raw contents.
- `.env.example` — token-free template.
- `.gitignore` — excludes `.env`.

`INSTALL.md` that contained direct tarball install guidance was removed because the chosen install path is Docker Compose runner containers, not direct `config.sh`/`run.sh` installation.

## GitHub Org and Runner Group

GitHub org:

- `querypie`

Runner group created via GitHub API:

- `mac-studio-llm1-linux-arm64`
- visibility: `all`

Useful API checks:

```sh
gh api /orgs/querypie/actions/runner-groups --paginate \
  --jq '.runner_groups[] | [.id,.name,.visibility] | @tsv'

GROUP_ID=$(gh api /orgs/querypie/actions/runner-groups --paginate \
  --jq '.runner_groups[] | select(.name=="mac-studio-llm1-linux-arm64") | .id')
gh api "/orgs/querypie/actions/runner-groups/$GROUP_ID/runners" --paginate \
  --jq '.runners[] | [.name,.os,.status,.busy] | @tsv'
```

## Installed Runner Set

Container names after Compose up:

- `github-runners-for-querypie-org-runner-1-1`
- `github-runners-for-querypie-org-runner-2-1`
- `github-runners-for-querypie-org-runner-3-1`
- `github-runners-for-querypie-org-runner-4-1`
- `github-runners-for-querypie-org-runner-5-1`
- `github-runners-for-querypie-org-runner-6-1`

GitHub runner names:

- `mac-studio-llm1-linux-arm64-1`
- `mac-studio-llm1-linux-arm64-2`
- `mac-studio-llm1-linux-arm64-3`
- `mac-studio-llm1-linux-arm64-4`
- `mac-studio-llm1-linux-arm64-5`
- `mac-studio-llm1-linux-arm64-6`

Labels verified by GitHub API:

- Runners 1-3: `self-hosted`, `Linux`, `ARM64`, `arch:arm64`, `os:ubuntu`, `build:build-arm64`, `purpose:ci`, `purpose:build`
- Runners 4-6: `self-hosted`, `Linux`, `ARM64`, `arch:arm64`, `os:ubuntu`, `build:build-arm64`, `purpose:ci`

All six were verified `online` and not busy immediately after install.

## Compose Operations

Run from the install directory:

```sh
cd /Users/qp-test/Workspace/github-runners-for-querypie-org

docker compose ps
docker compose logs --tail=100 runner-1
docker compose restart runner-1
docker compose restart
docker compose down
docker compose up -d
```

For initial build/start, use:

```sh
docker compose up -d --build
```

If a tool blocks foreground long-running commands, start it in a background tool/session and then poll the process output and `docker compose ps`.

## Verification Pattern Used

1. Confirm Compose services render:

```sh
docker compose config --services
```

2. Start/build with Compose.

3. Confirm containers are up:

```sh
docker compose ps
```

4. Confirm each service logs registration and readiness:

```sh
for svc in runner-1 runner-2 runner-3 runner-4 runner-5 runner-6; do
  echo "-- $svc"
  docker compose logs --tail=160 "$svc" 2>&1 |
    grep -Ei "Connected to GitHub|Runner successfully added|Current runner version|Listening for Jobs|Failed|error" |
    tail -n 20 || true
done
```

Expected readiness lines:

- `Connected to GitHub`
- `Runner successfully added`
- `Listening for Jobs`

5. Confirm labels from live container env without exposing token:

```sh
for c in $(docker ps --format "{{.Names}}" | grep "^github-runners-for-querypie-org-runner-" | sort); do
  echo "-- $c"
  docker inspect "$c" --format "{{range .Config.Env}}{{println .}}{{end}}" |
    grep -E "^(RUNNER_NAME|RUNNER_GROUPS|RUNNER_LABELS|RUNNER_ORG)=" |
    sort
done
```

6. Confirm GitHub-side status and labels:

```sh
gh api /orgs/querypie/actions/runners --paginate \
  --jq '.runners[] | select(.name|startswith("mac-studio-llm1-linux-arm64-")) | [.name,.os,.status,.busy,([.labels[].name]|join(","))] | @tsv' | sort
```

## Pitfalls Captured

- Container-image runner setup does not use GitHub UI's direct tarball install commands (`mkdir actions-runner`, `curl actions-runner-*.tar.gz`, `./config.sh`, `./run.sh`) on the host. Those commands are only useful as a source for org URL/token and OS/arch intent.
- GitHub UI may show `linux-x64` download snippets; for this Mac Studio Docker fleet the actual runner environment is Linux ARM64 (`platform: linux/arm64`, Ubuntu container, ARM64 labels).
- Do not add organization-disambiguation labels such as `org:querypie` when the GitHub organization and runner group already separate ownership.
- User explicitly asked not to auto-proceed while they were guiding configuration. For future runner setup, report the plan first unless the user clearly says to install/start now.
