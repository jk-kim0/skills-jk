# Latest main churn during 3-dev-server verification

Use this reference when verifying/deploying all three Outbound Agent dev environments while PRs are actively merging into `main`.

## Durable lessons

- Treat `origin/main` as unstable during active merge windows. Re-fetch immediately before declaring a revision latest, and re-check after any long-running deploy/migration finishes.
- Tencent image deploy workflow has `concurrency.cancel-in-progress: true` for the `main` deploy group. A newer `main` push can cancel an in-progress Tencent deploy after Seoul succeeds but before Tokyo starts/finishes. In that case, do not report partial success as latest; switch to the newest run for the newest `origin/main` SHA.
- Some documentation-only or ignored-path changes can move `origin/main` without automatically triggering every environment’s production deploy. If the user asks whether the three servers are on the literal latest `main`, manually dispatch the relevant deploy workflow for environments that did not auto-deploy because of path filters.
- Prefer short status checks over long passive waits. If a workflow is still running after a short poll, report which exact job is running and why rather than silently waiting.

## Recommended sequence

1. `git fetch origin main --prune` and record full `origin/main` SHA.
2. Check latest deploy workflows for:
   - `Deploy outbound-dev Production`
   - `PR Cache-Only Build Validation / Main Deploy outbound-front image`
3. If a run for an older SHA was cancelled, inspect whether a newer run for current `origin/main` is in progress.
4. Verify exact versions:
   - Vercel: successful production deploy run head SHA and `vercel inspect https://outbound-dev.vercel.app --scope querypie` status Ready.
   - Tencent: `/opt/outbound-agent/deployments/current-revision`, `/opt/outbound-agent/deployments/current-image`, `systemctl is-active outbound-front`, `systemctl is-active nginx`.
5. Run migrations only after the target deploy SHA is settled enough to avoid doing work against a just-obsoleted revision. If main moves again, rerun migrate/schema checks on the newest SHA.
6. Run schema checks for all three environments.
7. Smoke:
   - public `/login` for all three.
   - DB-backed authenticated route for Tencent by reading the `sales-demo` user id from VM-local PostgreSQL and calling `/<teamSlug>/home` with `Cookie: outbound_session=<uuid>`.
8. Escalate to reset only with evidence such as seed drift or schema/runtime incompatibility.

## Seed drift reset signal

For Tencent seed drift, compare counts such as:

- `User`
- `Team`
- `TeamMembership`
- `EmailTemplate`
- `EmailTemplateVersion`

A pattern like `EmailTemplate=0`, `EmailTemplateVersion=0`, and missing `querypie-jp/querypie-kr/querypie-us` teams after migrate-only is evidence to run the target migration workflow with `reset_database=true`.

## Reporting guidance

Report final state with exact SHA, workflow run IDs, reset decisions, and smoke results. If a reset was needed, state the before/after counts and why reset was justified.