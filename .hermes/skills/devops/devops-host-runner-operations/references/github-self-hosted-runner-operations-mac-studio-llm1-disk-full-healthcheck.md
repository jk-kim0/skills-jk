# Mac Studio LLM1 runner disk-full healthcheck pattern

Use this when checking whether `Mac-Studio-LLM1.local` / `10.11.1.11` GitHub self-hosted runners are currently failing due to disk pressure. Keep the run read-only unless the user explicitly asks for cleanup or restart.

## Access

Known working SSH pattern from prior audits:

```sh
ssh -i /Users/jk/.ssh/jk_macbook -o BatchMode=yes -o IdentitiesOnly=yes qp-test@10.11.1.11 '<command>'
```

If this fails, classify the layer first: port reachability, auth, or remote execution. Do not assume runner failure from SSH auth failure.

## Minimum evidence for “not disk full”

Collect all three layers:

1. macOS host filesystem and inode usage:

```sh
df -h / /System/Volumes/Data /Users 2>/dev/null || df -h
df -i / /System/Volumes/Data /Users 2>/dev/null || true
```

2. Docker Desktop VM/container filesystem usage, not just host disk:

```sh
DOCKER=/usr/local/bin/docker
$DOCKER info --format 'DockerRootDir={{.DockerRootDir}} Driver={{.Driver}} NCPU={{.NCPU}} Mem={{.MemTotal}}' 2>/dev/null || true
for c in $($DOCKER ps --format '{{.Names}}' | grep -Ei 'runner|github|actions'); do
  echo "-- $c"
  $DOCKER exec "$c" sh -lc 'df -h / /runner /home/runner 2>/dev/null || df -h' 2>/dev/null | sed -n '1,8p' || echo 'exec failed'
done
```

3. Runner logs for disk-pressure strings:

```sh
grep -RniE 'no space left|disk full|ENOSPC|No usable temporary directory|not enough space' \
  "$HOME/actions-runner/_diag" \
  "$HOME/Library/Logs/actions.runner.chequer-io.Dev-MacStudio" 2>/dev/null | tail -80 || true
for c in $($DOCKER ps -a --format '{{.Names}}' | grep -Ei 'runner|github|actions'); do
  echo "-- $c"
  $DOCKER logs --since 72h "$c" 2>&1 | grep -Ei 'no space left|disk full|ENOSPC|not enough space|No usable temporary directory|cannot create temp' | tail -20 || true
done
```

## Runner health cross-check

Use both local process/container state and GitHub API state:

```sh
cd /Users/qp-test/actions-runner && ./svc.sh status || true
cd /Users/qp-test/Workspace/github-runner && /usr/local/bin/docker compose ps -a || true
cd /Users/qp-test/Workspace/github-runners-for-querypie-org && /usr/local/bin/docker compose ps -a || true

for org in chequer-io querypie; do
  echo "## org=$org"
  gh api "/orgs/$org/actions/runners?per_page=100" \
    --jq '.runners[] | select(.name|test("^(Dev-MacStudio|SVR-MS-ARM-RUNNER-|mac-studio-llm1-linux-arm64-)")) | [.name,.status,(.busy|tostring),(.runner_group_name // ""),(.labels|map(.name)|join(","))] | @tsv'
done
```

Do not treat `busy=true` as a problem by itself. It often means the runner is actively taking jobs.

## Preventive cleanup signal

Even when disk is not currently full, Docker BuildKit state can accumulate heavily. Report it separately as a preventive cleanup opportunity, not as an active outage:

```sh
/usr/local/bin/docker system df
/usr/local/bin/docker system df -v | awk '/^Local Volumes space usage:/ {p=1; print; next} /^Build cache usage:/ {p=0} p {print}' | sed -n '1,120p'
/usr/local/bin/docker volume ls -qf dangling=true | wc -l
```

Prior observed shape: host disk had TiB-scale free space, Docker container filesystems still had ~200GB free, runner logs had no ENOSPC evidence, but Docker local volumes had ~200GB reclaimable and many dangling `buildx_buildkit_builder-*_state` volumes. In that case report “no active disk-full condition” plus “preventive Docker buildx/volume cleanup recommended if growth continues.”
