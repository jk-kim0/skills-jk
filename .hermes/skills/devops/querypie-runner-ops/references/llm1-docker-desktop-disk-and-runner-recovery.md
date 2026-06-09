# LLM1 Docker Desktop disk expansion and runner recovery notes

Scope: Mac Studio LLM1 (`qp-test@10.11.1.11`) hosting QueryPie org Linux ARM64 Docker Compose self-hosted runners in `/Users/qp-test/Workspace/github-runners-for-querypie-org`.

## Symptoms observed

- GitHub org runners `mac-studio-llm1-linux-arm64-*`: most or all `offline`.
- Host macOS disk may still have plenty of free space.
- Inside runner containers, `df -h / /runner` shows Docker VM filesystem at or near 100%.
- Runner logs may contain:
  - `No space left on device`
  - `Configuration failed. Retrying`
  - `Unhandled exception. System.IO.IOException: No space left on device`
  - after partial recovery, corrupted anonymous runner volumes can show `cp: cannot overwrite non-directory '/runner/bin' with directory '/runnertmp/bin'`
  - if anonymous volumes are recreated while `.env` has an expired org registration token, new registration can fail with `Http response code: NotFound from 'POST https://api.github.com/actions/runner-registration'`

## Safe recovery pattern used

1. Check live state first:
   - GitHub runner status via `gh api /orgs/querypie/actions/runners --paginate` filtered by `^mac-studio-llm1-linux-arm64-`.
   - Host disk with `df -h / /Users`.
   - Docker VM/container disk with `docker exec <runner> sh -lc 'df -h / /runner; df -ih / /runner'`.
   - Compose state/logs from `/Users/qp-test/Workspace/github-runners-for-querypie-org`.
2. Free Docker VM space without deleting runner volumes first:
   - `docker builder prune -af`
   - `docker image prune -af`
3. If runner volumes are already corrupted, recreate only the offline runner services' anonymous `/runner` volumes:
   - Do not disturb any online/busy runner if avoidable.
   - Example for all except runner-10:
     - `services=(runner-1 runner-2 runner-3 runner-4 runner-5 runner-6 runner-7 runner-8 runner-9 runner-11 runner-12)`
     - `docker compose rm -sfv "${services[@]}"`
     - `docker compose up -d --force-recreate "${services[@]}"`
4. If registration fails with 404 after volume recreation, refresh `RUNNER_TOKEN` in `.env`:
   - Locally or from an authenticated environment with org admin permissions: `gh api -X POST /orgs/querypie/actions/runners/registration-token --jq .token`
   - Back up remote `.env` before replacing `RUNNER_TOKEN=`.
   - Do not print token values; report only key presence or token length if needed.
   - Recreate the affected offline services again.
5. Verify:
   - Logs contain `Runner successfully configured`, `Connected to GitHub`, and `Listening for Jobs`.
   - GitHub API shows `online` count equals expected runner count and `offline: 0`.

## Docker Desktop disk expansion pattern used

- Active Docker Desktop disk size setting on this host is in:
  - `~/Library/Group Containers/group.com.docker/settings-store.json` key `DiskSizeMiB`
  - also keep `~/Library/Group Containers/group.com.docker/settings.json` key `diskSizeMiB` aligned when present.
- Disk image path:
  - `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`
- To add about 500 GiB to an 800 GiB allocation, set `DiskSizeMiB` to `1331200` (about 1.3 TiB), backing up settings files first.
- Docker Desktop restart is required. `osascript -e 'quit app "Docker"'` may hang; if Docker API remains unhealthy and Docker processes stay up, terminate Docker Desktop/backend/virtualization processes and re-open Docker.
- After restart, verify with:
  - `ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`
  - `docker run --rm alpine:3.20 sh -lc 'df -h /'`
  - `docker exec <runner> sh -lc 'df -h / /runner'`
  - `docker compose up -d` and GitHub runner API status.

## Cautions

- Docker Desktop restart will temporarily take all runners offline and can interrupt jobs. For user-requested recovery/expansion, give visible progress updates before and after restart.
- Avoid broad `docker volume prune` unless explicitly intended; runner data and other workloads may use volumes.
- Prefer excluding online/busy runners from destructive recreate steps to avoid interrupting active jobs.
- `RUNNER_TOKEN` is short-lived; invalid-token symptoms are not fixed by repeated compose restarts.
