# querypie-mono self-hosted runner inventory status table

Use this reference when updating the querypie-mono GitHub wiki Self-Hosted Runner Status page with a front-of-document inventory table.

## Goal

Before detailed investigation notes, add a compact status table that answers:

- Runner name
- Hostname of the computer running the runner
- IP address
- OS
- Optional execution form/details such as native service vs Docker container when it helps interpret cleanup or cache risk

This table should be placed at the very top of the status page so stakeholders see fleet topology before per-runner findings.

## Evidence hierarchy

Prefer live, read-only evidence over inferred wiki text:

1. GitHub runner metadata from `gh` or the GitHub UI/API for runner names, groups, labels, and online/offline state.
2. QueryPie host inventory / `qpctl host list` mapping for hostnames and reachable IPs.
3. SSH probe evidence from the actual host:
   - `hostname` for host hostname.
   - `hostname -I` or `ip addr` for host IPs on Linux.
   - `sw_vers` / `uname -a` on macOS.
   - `/etc/os-release` / `uname -m` on Linux.
4. Docker container metadata only for containerized runner details; do not treat a container hostname as the physical host hostname.

If a host cannot be reached, keep the row but mark the missing cells as not verified rather than guessing.

## QueryPie access patterns seen in this audit class

- Use `qpctl host list/use` and `qpctl ssh-proxy` for QueryPie runner/server access. Do not switch to browser/Web Terminal access without asking the user.
- L2 runners commonly use SSH user `ubuntu`.
- L3 native runners commonly use SSH user `deploy`.
- Some L3 Dockerized runners on host `10.11.0.13` were verified via `ubuntu@10.11.0.13` with `qpctl ssh-proxy`.
- Mac Studio LLM1 is known as `qp-test@10.11.1.11` / `Mac-Studio-LLM1.local`, but if live access fails, report that the table row is based on existing inventory/wiki metadata and note what was not live-verified.

## Important topology/correctness note

One physical host can run many self-hosted runner instances. For example, the L3 Dockerized host `10.11.0.13` was observed running many runner containers such as `github-actions-runner-1-1` through `github-actions-runner-10-1` plus mini runners.

Do not overstate the implication:

- Docker cleanup is host-wide when runner containers bind-mount the same `/var/run/docker.sock`; `docker system prune` can affect sibling runner jobs on the same host/daemon.
- Workspace cleanup is runner-local when each container has its own `/runner` volume. Do not claim that cleaning `/runner/_work` inside one such container directly deletes sibling runner workspaces. The safer rationale for leaving workspace cleanup disabled by default is that it deletes repository checkout directories rather than disposable cache/temp data.

## Suggested wiki table shape

Place this before detailed findings:

```md
## Self-Hosted Runner Inventory

| Runner | Hostname | IP Address | OS | Execution form | Notes |
|---|---|---|---|---|---|
| `SVR-L3-DOCKERIZED-RUNNER-1` | `ip-10-11-0-13` | `10.11.0.13` | Ubuntu 20.04 / Linux x64 | Docker container on shared host daemon | Live-verified; container has runner-local `/runner` volume. |
```

Keep the note column terse. Put detailed disk/cache findings in each runner detail section/page, not in this front table.

## Verification checklist before pushing wiki edits

- Confirm the page being edited is the wiki repo page, not the source repo README.
- Put the inventory table at the top, above investigation-result prose.
- Use host hostname, not container hostname, for `Hostname`.
- Mark unavailable evidence explicitly (`not live-verified`, `access blocked`, etc.).
- Commit and push the wiki repository update.
