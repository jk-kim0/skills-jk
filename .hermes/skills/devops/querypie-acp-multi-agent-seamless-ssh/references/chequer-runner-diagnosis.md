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

## Physical host access and runner placement

Known physical server connections registered in `sec.querypie.io` include `[DC] 10.11.0.11`, `[DC] 10.11.0.12`, `[DC] 10.11.0.13`, `[DC] 10.11.0.14`, and `[DC] 10.11.1.13`. Treat these as QueryPie connection names for physical hosts and verify the actual access account before running diagnostics.

Verified on 2026-05-19 through QueryPie ACP seamless SSH:

| Host | SSH target | Remote hostname | OS | Role |
| --- | --- | --- | --- | --- |
| L2 physical host | `ubuntu@10.11.0.12` | `ip-10-11-0-12` | Ubuntu 20.04.6 LTS | KVM host for `SVR-L2-RUNNER-1` through `SVR-L2-RUNNER-6`; `sudo -n virsh list --all` also shows `SVR-L2-RUNNER-7` shut off. |
| L3 physical host | `ubuntu@10.11.0.13` | `ip-10-11-0-13` | Ubuntu 20.04.6 LTS | Docker host for `SVR-L3-DOCKERIZED-RUNNER-1` through `10` and `SVR-L3-MINI-DOCKERIZED-RUNNER-1` through `5`; `sudo -n virsh list --all` shows legacy `SVR-L3-RUNNER-*` libvirt VMs shut off. |
| L3 standalone VM 1 | `deploy@10.11.13.2` | `SVR-L3-RUNNER-1` | Ubuntu/Linux x64 | GitHub runner VM. |
| L3 standalone VM 2 | `deploy@10.11.13.3` | `SVR-L3-RUNNER-2` | Ubuntu/Linux x64 | GitHub runner VM. |

Use the physical hosts only for placement/host-level diagnosis (`virsh list`, `docker ps`, redacted `docker inspect`). Do not stop/restart/delete VMs or containers without explicit approval.

## Observed access caveat

L2 runner hosts accepted `ubuntu` through QueryPie Seamless SSH. L3 standalone runner VMs accepted `deploy` through QueryPie Seamless SSH on 2026-05-19. If `ubuntu` on an L3 standalone runner fails with `[QueryPie] Authentication failed`, use the documented `deploy` account or re-check QueryPie server/account permissions.

Do not encode a transient authentication failure as host outage; report it as an access/permission state to verify in QueryPie ACP.
