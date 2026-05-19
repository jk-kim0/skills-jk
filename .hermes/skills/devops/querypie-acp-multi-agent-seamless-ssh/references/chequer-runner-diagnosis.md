# Chequer GitHub Runner Diagnosis via QueryPie ACP

Session-derived reference for diagnosing Chequer/QueryPie self-hosted runners through QueryPie ACP Multi Agent Seamless SSH.

## Authoritative wiki handoff

The operator-facing guide lives at:

https://github.com/chequer-io/querypie-mono/wiki/How-to-Diagnose-GitHub-Self%E2%80%90Hosted-Runners

It was written for humans or AI agents without Hermes skills/memory and includes login/setup, QueryPie ACP server lookup, SSH connection patterns, Docker/volume diagnosis, cleanup-candidate classification, and reporting format.

## Useful runner mapping observed from QueryPie SAC

QueryPie group: `[DC] Github Runner`

| QueryPie connection | Host/IP |
| --- | --- |
| `[DC] SVR-L2-RUNNER-1` | `10.11.12.2` |
| `[DC] SVR-L2-RUNNER-2` | `10.11.12.3` |
| `[DC] SVR-L2-RUNNER-3` | `10.11.12.4` |
| `[DC] SVR-L2-RUNNER-4` | `10.11.12.5` |
| `[DC] SVR-L2-RUNNER-5` | `10.11.12.6` |
| `[DC] SVR-L2-RUNNER-6` | `10.11.12.7` |
| `[DC] SVR-L3-RUNNER-1` | `10.11.13.2` |
| `[DC] SVR-L3-RUNNER-2` | `10.11.13.3` |

Treat this mapping as a convenience snapshot, not a permanent source of truth. Re-check QueryPie ACP before acting.

## Proven connection pattern

For automation, prefer explicit OpenSSH ProxyCommand over direct `qpctl ssh`:

```sh
ssh \
  -o BatchMode=yes \
  -o ConnectTimeout=8 \
  -o StrictHostKeyChecking=accept-new \
  -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' \
  ubuntu@10.11.12.5 \
  'hostname; whoami; uname -srmo'
```

This successfully verified `SVR-L2-RUNNER-4` as `ubuntu` and avoided `qpctl ssh` remote-command argument ordering issues.

## Observed access caveat

L2 runner hosts accepted `ubuntu` through QueryPie Seamless SSH in this session. L3 runner hosts were visible in QueryPie and online in GitHub, but `ubuntu` Seamless SSH returned `[QueryPie] Authentication failed`; other tested custom accounts returned `Custom account not supported on seamless SSH`.

Do not encode that as a permanent inability to reach L3. For future sessions, report it as an access/permission state to verify in QueryPie ACP rather than as a host outage.
