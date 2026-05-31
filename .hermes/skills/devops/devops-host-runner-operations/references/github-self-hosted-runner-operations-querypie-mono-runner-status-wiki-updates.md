# querypie-mono runner status wiki update workflow

Use this reference when updating the `chequer-io/querypie-mono` GitHub wiki runner status pages.

## Page naming convention

For per-runner status pages, use short runner-first wiki page names:

- `SVR-L2-RUNNER-1-Status`
- `SVR-L2-RUNNER-2-Status`
- `SVR-L2-RUNNER-3-Status`
- `SVR-L2-RUNNER-4-Status`
- `SVR-L2-RUNNER-5-Status`
- `SVR-L2-RUNNER-6-Status`
- `SVR-L3-RUNNER-1-Status`

Avoid long slugs such as `Self-Hosted-Runner-Status-SVR-L2-RUNNER-1` for detail pages. Keep the main index page as `Self‐Hosted-Runner-Status`.

## User-preferred workflow

The user explicitly wants one server handled at a time:

1. Start with `SVR-L2-RUNNER-1-Status`.
2. Collect fresh diagnostics for that one server only.
3. Update that one detail page.
4. Update the main `Self‐Hosted-Runner-Status` index row for that server.
5. Commit and push the wiki repo.
6. Then proceed to the next runner.

Do not batch all runner pages into one large rewrite when the user asks for sequential updates.

## Wiki clone location

The maintained local wiki clone for this work is:

```text
/Users/jk/workspace/querypie-mono.wiki
```

Prefer that clone over `/tmp/querypie-mono.wiki`. Keep local raw diagnostic files under an ignored directory such as `.runner-audit/` and do not commit raw logs.

## QueryPie host/IP mapping confirmed in the session

- `[DC] SVR-L2-RUNNER-1` -> `10.11.12.2`
- `[DC] SVR-L2-RUNNER-2` -> `10.11.12.3`
- `[DC] SVR-L2-RUNNER-3` -> `10.11.12.4`
- `[DC] SVR-L2-RUNNER-4` -> `10.11.12.5`
- `[DC] SVR-L2-RUNNER-5` -> `10.11.12.6`
- `[DC] SVR-L2-RUNNER-6` -> `10.11.12.7`
- `[DC] SVR-L3-RUNNER-1` -> `10.11.13.2`
- `[DC] SVR-L3-RUNNER-2` -> `10.11.13.3`

The L2 hosts were reachable as `ubuntu@<ip>` via:

```bash
ssh \
  -o BatchMode=yes \
  -o ConnectTimeout=8 \
  -o StrictHostKeyChecking=accept-new \
  -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' \
  ubuntu@10.11.12.2 \
  'hostname; whoami; uname -srm'
```

## Access-blocked documentation pattern

If a fresh diagnostic attempt is blocked by QueryPie, update the affected runner page instead of silently leaving stale data. Add a `최신 재진단 시도` section near the top with:

- timestamp
- exact sanitized error text
- whether QueryPie Workflow shows a pending access request
- statement that older numeric resource values below are from the last successful SSH audit

Example error seen:

```text
qpctl: error: [QPM-0010] Server 'sec.querypie.io' channel error: Server role selection is required
Connection closed by UNKNOWN port 65535
```

For `SVR-L3-RUNNER-1`, `ubuntu@10.11.13.2` previously failed with QueryPie authentication errors, so document access state rather than inventing resource numbers.

## Main index update pattern

On `Self‐Hosted-Runner-Status`, keep detailed findings in per-runner pages and update only the row summary:

```md
| `[DC] SVR-L2-RUNNER-1` | `10.11.12.2` | 조사 완료: YYYY-MM-DD HH:MM KST | [SVR-L2-RUNNER-1](SVR-L2-RUNNER-1-Status) | Docker volumes ..., Docker images ... |
```

If blocked:

```md
| `[DC] SVR-L2-RUNNER-1` | `10.11.12.2` | 재진단 차단: YYYY-MM-DD HH:MM KST | [SVR-L2-RUNNER-1](SVR-L2-RUNNER-1-Status) | QueryPie role selection/접근 권한 Pending. 기존 조사: ... |
```

## Diagnostic data to collect per server

Collect read-only data only unless the user explicitly approves cleanup:

- identity: `hostnamectl`, `whoami`, `date -Is`, `uptime`, `uname -a`
- CPU/memory: `nproc`, `lscpu`, `free -h`, `top -b -n1`
- disk/inodes: `df -hT`, `df -ih`
- runner process: `ps` filtered for `actions.runner`, `runsvc`, `Runner.Listener`, `Runner.Worker`
- Docker: `docker ps -a`, `docker stats --no-stream`, `docker system df`, `docker system df -v`, `docker volume ls`
- volume sizes: inspect each Docker volume mountpoint and `du -sh`, but wrap expensive calls with `timeout`
- major disk consumers: `du -xhd1 /home/ubuntu`, `/`, `/var/lib/docker`, plus `/tmp`, `/var/tmp`, `/var/cache/apt`, `/var/log/journal`

Use timeouts around `du` and verbose Docker commands because some runner hosts can otherwise exceed a few minutes.
