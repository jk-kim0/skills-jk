# querypie-mono runner resource audit wiki pattern

Session context: the user asked to investigate `[DC] SVR-L2-RUNNER-1` through `-6`, `[DC] SVR-L3-RUNNER-1`, and a duplicate `SVR-L2-RUNNER-2`, then document disk/CPU/memory/container/volume/reclaimable resources in the querypie-mono GitHub wiki.

## User workflow preference

- Do not write one large all-at-once report.
- Investigate one runner at a time.
- Create one separate wiki page per runner.
- Keep the main `Self‐Hosted-Runner-Status` wiki page as an index with links and concise reclaimable-resource summaries.
- If the input contains duplicate runner names, treat the duplicate as one runner and mention it in the index notes.

## Wiki repo location and page shape

Preferred local wiki clone:

```text
~/workspace/querypie-mono.wiki
```

Main page:

```text
Self‐Hosted-Runner-Status.md
```

Runner detail pages:

```text
Self-Hosted-Runner-Status-SVR-L2-RUNNER-1.md
Self-Hosted-Runner-Status-SVR-L2-RUNNER-2.md
...
Self-Hosted-Runner-Status-SVR-L3-RUNNER-1.md
```

Main page index columns used successfully:

```md
| Runner | Host/IP | Status | 상세 문서 | 핵심 회수 후보 |
|---|---|---|---|---|
```

## QueryPie connection mapping used

From QueryPie ACP connection inventory under `[DC] Github Runner`:

| QueryPie connection | Host/IP | SSH account verified |
|---|---|---|
| `[DC] SVR-L2-RUNNER-1` | `10.11.12.2` | `ubuntu` |
| `[DC] SVR-L2-RUNNER-2` | `10.11.12.3` | `ubuntu` |
| `[DC] SVR-L2-RUNNER-3` | `10.11.12.4` | `ubuntu` |
| `[DC] SVR-L2-RUNNER-4` | `10.11.12.5` | `ubuntu` |
| `[DC] SVR-L2-RUNNER-5` | `10.11.12.6` | `ubuntu` |
| `[DC] SVR-L2-RUNNER-6` | `10.11.12.7` | `ubuntu` |
| `[DC] SVR-L3-RUNNER-1` | `10.11.13.2` | current user lacked seamless SSH auth |
| `[DC] SVR-L3-RUNNER-2` | `10.11.13.3` | not in requested audit; current user lacked seamless SSH auth during probe |

If local DNS names such as `svr-l2-runner-1` do not resolve, use the QueryPie inventory IPs and explicit OpenSSH ProxyCommand:

```sh
ssh \
  -o BatchMode=yes \
  -o ConnectTimeout=8 \
  -o StrictHostKeyChecking=accept-new \
  -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' \
  ubuntu@10.11.12.2 \
  'hostname; whoami; uname -srm'
```

## Browser inventory fallback

When the QueryPie UI is logged in, the connection list can be queried from the browser without copying sensitive cookies:

```js
async () => {
  const resp = await fetch('/engine-grpc/api.user.sac.access_control.AccessControlService/GetConnectionList', {
    method: 'POST',
    headers: {
      'content-type': 'application/grpc-web-text',
      'accept': 'application/grpc-web-text',
      'x-grpc-web': '1',
    },
    body: 'AAAAAAA=',
  });
  const text = await resp.text();
  const bin = atob(text.replace(/\r?\n/g, ''));
  const strings = [];
  let cur = '';
  for (let i = 0; i < bin.length; i++) {
    const c = bin.charCodeAt(i);
    if (c >= 32 && c <= 126) cur += String.fromCharCode(c);
    else { if (cur.length >= 3) strings.push(cur); cur = ''; }
  }
  if (cur.length >= 3) strings.push(cur);
  return strings.filter(s => /SVR-L[23]-RUNNER|SVR-L3|Github Runner|10\.11\.1[23]/.test(s));
}
```

Do not print request headers, cookies, or tokens.

## Remote audit sections

Collect at least these read-only sections per runner:

- identity: `hostnamectl`, `whoami`, `date -Is`, `uptime`, `uname -a`
- CPU: `nproc --all`, selected `lscpu` fields
- memory: `free -h`, `free -m`
- disk: `df -hT`, `df -ih`
- processes: `top -b -n1`, top processes by RSS/CPU, runner processes
- runner dirs: likely `actions-runner` and `_work`
- Docker: `docker ps -a`, `docker stats --no-stream`, `docker system df`, `docker system df -v`, `docker volume ls`
- volume sizes: `docker volume inspect` mountpoints plus `du -sh`
- compose files under `/home/ubuntu`
- top disk consumers: `/home/ubuntu`, `/`, `/var/lib/docker`, apt/journal/tmp

For large/slow hosts, wrap expensive commands with bounded `timeout`, especially:

```sh
timeout 40s docker system df -v
timeout 20s sudo du -sh "$volume_mountpoint"
timeout 40s sudo du -xhd1 /home/ubuntu
timeout 40s sudo du -xhd1 /
timeout 40s sudo du -xhd1 /var/lib/docker
timeout 20s sudo du -sh /var/cache/apt /var/log/journal /tmp /var/tmp
```

This prevents a single runner from stalling the whole sequential audit.

## Detail page sections

A useful runner detail page structure:

1. Metadata: 조사 시각, QueryPie connection, Host/IP, SSH account, hostname, kernel, GitHub runner status/busy/labels, runner root, uptime.
2. 요약: disk pressure and top reclaimable categories.
3. 자원 현황 table: vCPU, CPU model, memory, root disk, load average, CPU snapshot.
4. Docker/container status with code blocks for `docker ps` and `docker stats`.
5. Docker space usage table from `docker system df`.
6. Docker volumes table with size, mountpoint, and `LINKS=0` reclaim-candidate note.
7. Filesystem top usage tables for `/home/ubuntu`, `/`, `/var/lib/docker`, apt/journal/tmp.
8. Compose files found.
9. 회수 가능 자원 후보 with priority, estimated amount, and risk.
10. 권장 정리 순서: verify runner `busy=false`; prune dangling images; verify/remove unused volumes; then tmp/cache cleanup.
11. Local raw-data path, if kept outside git.

## Access-blocked runner handling

If GitHub shows the runner online but QueryPie seamless SSH fails, still create the per-runner wiki page rather than omitting it. Document:

- QueryPie connection and Host/IP from inventory.
- GitHub runner metadata from `gh api orgs/chequer-io/actions/runners`.
- Exact bounded SSH probe command.
- Redacted error class, e.g. `Authentication failed` or `Custom account not supported on seamless SSH`.
- Clear statement that internal resource/reclaimable-space data was not collected and should not be guessed.
- Required follow-up: grant/check QueryPie SAC account permission, then rerun the same diagnostic set.

## Local raw output hygiene

Store raw command output outside committed wiki files, for example:

```text
~/workspace/querypie-mono.wiki/.runner-audit/<runner>.raw.txt
```

Add `.runner-audit/` to the wiki repo's `.git/info/exclude` so raw diagnostics and helper scripts do not dirty the wiki working tree or get committed accidentally.
