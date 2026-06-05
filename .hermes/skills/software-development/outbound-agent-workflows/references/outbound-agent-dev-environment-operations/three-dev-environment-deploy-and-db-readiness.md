# Three dev environment deploy and DB readiness

Use this note when checking whether all Outbound Agent development environments are on the latest `main` and have current DB schema.

## Environments

- Vercel/Incheon: `https://outbound-dev.vercel.app/login`
- Tencent Seoul: `https://outbound-seoul.dev.querypie.io/login`
- Tencent Tokyo: `https://outbound-tokyo.dev.querypie.io/login`

## Session-derived checklist

1. Establish latest target SHA from GitHub, not from the local checkout alone.
   - `git fetch origin main --prune`
   - `git rev-parse origin/main`
   - Local root `main` may be behind and should not be treated as the deploy target if `origin/main` advanced.
2. Check recent GitHub Actions runs for `main`.
   - Vercel: `Deploy outbound-dev Production`
   - Tencent image build/deploy: `PR Cache-Only Build Validation / Main Deploy outbound-front image`
   - DB migrations: `Apply outbound-dev DB Migration`, `Apply tencent/outbound-seoul DB Migration`, `Apply tencent/outbound-tokyo DB Migration`
   - DB schema checks: `Check outbound-dev DB Schema`, `Check tencent/outbound-seoul DB Schema`, `Check tencent/outbound-tokyo DB Schema`
3. Apply DB migrations with reset disabled first.
   - Use `reset_database=false` for all three environments.
   - Run schema checks after migrations.
   - Escalate to reset only if migration, schema check, or runtime smoke fails.
4. Verify runtime.
   - `curl -I <env>/login` confirms public HTTP health only.
   - For Vercel, use the deployment ID from the production deploy log and `vercel inspect <deployment-id> --scope querypie` to confirm `Ready`, aliases, and region.
   - For Tencent VMs, SSH and read `/opt/outbound-agent/deployments/current-image` and `/opt/outbound-agent/deployments/current-revision`; these are more authoritative than hashes found in rendered HTML.
5. If GitHub run status appears stuck but public service is healthy, inspect job steps and/or VM state before declaring failure.
   - `gh run view <run-id> --json jobs`
   - SSH checks: `systemctl is-active outbound-front`, `systemctl is-active nginx`, current image/revision files.

## Pitfalls reinforced by the session

- Arbitrary 40-character hashes scraped from `/login` HTML may not be the deployed revision.
- Reset should not be run proactively when migrate-only plus schema check succeeds.
- Tencent main-push image deployment is ordered Seoul then Tokyo; verify both deploy jobs or each VM directly.
