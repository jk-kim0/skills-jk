# Tencent Seoul active deploy triage pattern

Use this note when the user asks whether Dev Seoul is currently deploying the latest container image and what state the server is in.

## Decision flow

1. Establish the target revision from `origin/main` and the newest relevant GitHub Actions runs.
   - Prefer GitHub Actions evidence before SSH: list recent runs for Tencent deploy/container-image workflows and inspect the run jobs/steps.
   - A top-level workflow can be `in_progress` even when the Seoul job is already done or waiting behind another target; inspect job status and step names, not only the run conclusion.
   - Identify the immutable image tag or git SHA the run is building/deploying before comparing server state.

2. If the deployment run has completed successfully for Seoul, verify the VM and then smoke-test.
   - SSH to the Seoul VM and read deployed revision/image metadata from `/opt/outbound-agent/deployments/current-image`, `/opt/outbound-agent/deployments/current-revision`, and `/opt/outbound-agent/repo/.deployed-revision`.
   - Check service/container health with systemd and Docker/Compose status.
   - After exact-version proof is established, run the normal public runtime smoke for `https://outbound-seoul.dev.querypie.io/login` and any requested authenticated/DB-backed smoke.

3. If the deployment run is still in progress or ambiguous, SSH and report live VM state instead of waiting silently.
   - Report current deployed image/revision, container uptime/status, exposed ports, and whether the target image differs from the in-flight workflow image.
   - Inspect recent container logs and systemd journal for errors. Separate historical errors from errors after the current container start time.
   - Do not claim the new deployment is complete until GitHub Actions and VM metadata agree.

## Suggested evidence commands

GitHub Actions:

```bash
gh run list --workflow 'Deploy Tencent container image' --limit 10 --json databaseId,status,conclusion,headSha,createdAt,displayTitle,event
# Then inspect the candidate run:
gh run view <run-id> --json status,conclusion,headSha,jobs
# If job/step status is ambiguous or the user explicitly asked for Action-log evidence,
# inspect the Seoul job log and cite the image/revision/pull/restart/smoke lines:
gh run view <run-id> --job <job-id> --log
```

VM checks, via the repository's established SSH/QueryPie access path:

```bash
sudo test -f /opt/outbound-agent/deployments/current-image && sudo cat /opt/outbound-agent/deployments/current-image
sudo test -f /opt/outbound-agent/deployments/current-revision && sudo cat /opt/outbound-agent/deployments/current-revision
sudo test -f /opt/outbound-agent/repo/.deployed-revision && sudo cat /opt/outbound-agent/repo/.deployed-revision
systemctl is-active outbound-front nginx
sudo docker ps --filter name=outbound --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
sudo docker logs --since 30m outbound-front 2>&1 | tail -200
sudo journalctl -u outbound-front --since '30 min ago' --no-pager | tail -200
```

Adjust container/service names if the VM layout differs; verify actual names from `docker ps` or the repo deploy scripts before treating a missing name as a failure.

## Reporting format

Keep the report short and evidence-oriented:

- Latest target SHA/image from `origin/main` and GHA.
- GHA deployment state: run id, status/conclusion, Seoul job/step status.
- VM deployed SHA/image and whether it matches the target.
- Service/container state and uptime.
- Log findings: no recent errors, or grouped error excerpts with timestamps.
- If complete: smoke-test result.
- If still running: what is in flight and what is currently serving traffic.
