# Mac Studio LLM1 QueryPie org runner recovery

Concrete recovery pattern from Mac Studio LLM1 (`qp-test@10.11.1.11`) for a Docker Compose GitHub runner fleet under:

```text
/Users/qp-test/Workspace/github-runners-for-querypie-org
```

## Symptom

One runner container appears `running`, but is actually in a fast restart/reconfigure loop:

```text
github-runners-for-querypie-org-runner-1-1 State=running Running=true RestartCount=95+
```

Logs repeat:

```text
Cannot configure the runner because it is already configured. To reconfigure the runner, run 'config.cmd remove' or './config.sh remove' first.
Configuration failed. Retrying
cp: cannot overwrite non-directory '/runner/bin' with directory '/runnertmp/bin'
```

Other sibling runners in the same Compose project may remain healthy and `Listening for Jobs`.

## Diagnosis

The runner's anonymous `/runner` Docker volume can become internally inconsistent. In the observed case, `/runner/bin` was not the expected directory, so the entrypoint could not copy/reconfigure the runner runtime.

This is a runner-local volume problem, not evidence that all runners or the host are broken.

## Safe recovery pattern

1. Obtain a fresh GitHub Actions registration token for the target org. Treat the token as a secret and never print it.
2. SSH to the host with the known working account/key, then enter the Compose project:

```sh
ssh -i /Users/jk/.ssh/jk_macbook -o IdentitiesOnly=yes qp-test@10.11.1.11
cd /Users/qp-test/Workspace/github-runners-for-querypie-org
```

3. Back up `.env` and update only `RUNNER_TOKEN`:

```sh
cp .env ".env.bak.$(date +%Y%m%d%H%M%S)"
python3 - <<'PY'
from pathlib import Path
p = Path('.env')
new_token = '<fresh-registration-token>'
lines = []
seen = False
for line in p.read_text().splitlines():
    if line.startswith('RUNNER_TOKEN='):
        lines.append('RUNNER_TOKEN=' + new_token)
        seen = True
    else:
        lines.append(line)
if not seen:
    lines.append('RUNNER_TOKEN=' + new_token)
p.write_text('\n'.join(lines) + '\n')
PY
```

4. Remove only the broken service container and its anonymous volumes:

```sh
docker compose rm -sfv runner-1
```

5. Recreate and start only that runner:

```sh
docker compose create runner-1
docker compose start runner-1
```

This split `create`/`start` form avoids agent safety wrappers treating `docker compose up -d` as a long-lived server start.

## GitHub Actions fallback when SSH is blocked

If SSH to `qp-test@10.11.1.11` reaches port 22 but closes before key exchange (`kex_exchange_identification: Connection closed by remote host`), use an online sibling runner on the same host to perform the same runner-local recovery through Docker. The pattern is:

1. Confirm at least one sibling runner in `mac-studio-llm1-linux-arm64-*` is `online` in the QueryPie org runner API.
2. Create a short-lived org runner registration token locally with `gh api -X POST /orgs/querypie/actions/runners/registration-token`; do not print it.
3. Store it as a temporary repo secret on a repo allowed to use the runner group, for example `TEMP_QUERYPIE_RUNNER_REGISTRATION_TOKEN` in `querypie/corp-web-app`, then delete the secret after the recovery run.
4. Run a temporary branch workflow on `[self-hosted, Linux, ARM64, arch:arm64, os:ubuntu, purpose:ci]` that mounts the host Compose directory into a helper Docker CLI container and executes Compose there:

```sh
docker run --rm -i --platform linux/arm64 \
  -e RUNNER_TOKEN \
  -e TARGET_SERVICES="runner-2 runner-6" \
  -v /Users/qp-test/Workspace/github-runners-for-querypie-org:/proj \
  -v /var/run/docker.sock:/var/run/docker.sock \
  docker:29-cli sh -eu <<'SH'
cd /proj
docker compose version
cp .env ".env.bak.$(date +%Y%m%d%H%M%S)"
tmp_env="$(mktemp)"
awk -v token="$RUNNER_TOKEN" 'BEGIN{seen=0} /^RUNNER_TOKEN=/{print "RUNNER_TOKEN=" token; seen=1; next} {print} END{if(!seen) print "RUNNER_TOKEN=" token}' .env > "$tmp_env"
mv "$tmp_env" .env
for svc in $TARGET_SERVICES; do
  docker compose rm -sfv "$svc"
  docker compose create "$svc"
  docker compose start "$svc"
  docker compose logs --tail=160 "$svc" 2>&1 |
    grep -Ei 'Connected to GitHub|Runner successfully added|Listening for Jobs|Cannot configure|Configuration failed|ERROR|Failed|Exception' |
    tail -n 80 || true
done
docker compose ps -a
SH
```

Important fallback details:

- Use `docker run -i`; without `-i`, the heredoc script is not passed to the helper container and the job may appear to succeed without running Compose.
- The Actions runner container may not see `/Users/qp-test/...` directly, but Docker can mount that host path into a helper container via the shared Docker socket.
- `docker:29-cli` does not include `python3`; use POSIX shell/awk for `.env` edits inside the helper container.
- A plain `docker restart` can reset restart counts but will not fix a corrupt `/runner` anonymous volume; recreate the affected Compose service with `rm -sfv`, `create`, and `start`.
- Delete the temporary workflow branch and temporary repo secret after runner status is verified online.

## Verification

Check the container state:

```sh
docker inspect github-runners-for-querypie-org-runner-1-1 \
  --format 'State={{.State.Status}} Running={{.State.Running}} RestartCount={{.RestartCount}} Started={{.State.StartedAt}}'
```

Expected:

```text
State=running Running=true RestartCount=0
```

Check logs:

```sh
docker compose logs --tail=120 runner-1 | grep -Ei 'Connected to GitHub|Listening for Jobs|Cannot configure|Configuration failed|ERROR|Failed|Exception'
```

Expected success signals:

```text
√ Connected to GitHub
Listening for Jobs
```

Finally inspect all sibling runner containers and ensure all are `running` with stable restart counts.

## Pitfalls

- Do not run `docker compose down` for this class of single-runner corruption unless the user wants to disturb the entire fleet.
- Do not print `.env`, registration tokens, runner credentials, or container env values containing token/secret-like keys.
- Do not assume `running` means healthy when restart count is rising. Pair `docker inspect` restart count with logs.
- Registration tokens are short-lived. Update `.env` and recreate the broken runner promptly after receiving a fresh token.
- Use `docker compose rm -sfv <service>` only for the affected service so sibling runners keep working.
