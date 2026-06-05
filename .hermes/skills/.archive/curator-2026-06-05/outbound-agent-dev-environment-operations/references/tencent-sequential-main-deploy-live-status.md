# Tencent sequential main deploy live-status triage

Use when a main `PR Cache-Only Build Validation / Main Deploy outbound-front image` run is active and the user asks for dev-seoul/dev-tokyo deployment status.

## Pattern

1. Establish the target SHA from `origin/main` and the active main deploy run.
2. Inspect the run at job level, not just the top-level status:
   - `gh run view <run-id> --json workflowName,status,conclusion,headSha,updatedAt,url,jobs`
   - Seoul jobs usually finish before Tokyo jobs start.
   - A top-level run may show `queued` or `in_progress` while completed Seoul jobs already prove Seoul deploy/smoke success.
3. Separate four states per target:
   - exact revision deployed
   - service health
   - public `/login` health
   - post-deploy smoke/migration status
4. For Tencent VMs, verify exact served revision directly when SSH is available:
   - `/opt/outbound-agent/deployments/current-image`
   - `/opt/outbound-agent/deployments/current-revision`
   - `/opt/outbound-agent/repo/.deployed-revision`
   - `systemctl is-active outbound-front`
   - `systemctl is-active nginx`
   - `docker ps` for `outbound-front` and `outbound-agent-postgres`
5. Classify Tokyo carefully during sequential deploys:
   - If Tokyo public `/login` is 200 but VM metadata still shows an older SHA and the Tokyo deploy job is queued, report `healthy but not latest yet`, not failure.
   - If Seoul deploy/smoke/migration succeeded, report Seoul as clean even while the top-level run waits for Tokyo.
6. Avoid long passive waits. Poll once or twice, then either report the in-progress job or start a short background watcher with notify-on-complete and return control.

## Concise status language

- `Dev Seoul: latest SHA deployed and smoke-clean; DB migration succeeded.`
- `Dev Tokyo: public health is OK, but VM still serves <old-sha>; latest deploy job is queued/in progress.`
- `Vercel/outbound-dev: Ready, aliases attached, /login 200, recent error logs empty.`

## Pitfall

Do not call a target `latest` from public HTTP 200 alone. Public health only proves the currently served deployment is alive.