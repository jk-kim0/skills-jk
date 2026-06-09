# Three-environment post-merge deploy verification

Use this reference when checking `querypie/outbound-agent` after a merged PR moves `main`, especially when the user asks for Vercel/outbound-dev plus Tencent dev-seoul/dev-tokyo status.

## Sequence

1. Establish the latest remote main SHA.
   - `git fetch origin main --prune`
   - `git rev-parse origin/main`
   - Do not rely on the root checkout branch being current; it may be `main...origin/main [behind N]`.
2. List recent main runs and separate the three concerns:
   - `Deploy outbound-dev Production` for Vercel.
   - `CI` for source/build checks.
   - `PR Cache-Only Build Validation / Main Deploy outbound-front image` for Tencent image build, Seoul/Tokyo deploy, cleanup, and post-deploy smoke.
3. For active or large workflow runs, prefer REST polling when `gh run view` is slow or blocks:
   - `gh api repos/querypie/outbound-agent/actions/runs/<run-id> --jq '{id,status,conclusion,head_sha,updated_at,html_url}'`
   - `gh api repos/querypie/outbound-agent/actions/runs/<run-id>/jobs --paginate --jq '.jobs[] | {id,name,status,conclusion,started_at,completed_at}'`
4. For Vercel exact deployment proof, if the workflow log does not print a URL, use commit metadata:
   - `vercel ls outbound-dev --scope querypie --prod --meta githubCommitSha=<full-sha> --no-color`
   - `vercel inspect <deployment-url> --scope querypie --no-color`
   - `vercel logs <deployment-url> --scope querypie --no-follow --since 20m --level error --json`
5. Check public `/login` for all three environments, but report it only as health evidence, not exact-version proof.
6. Confirm runtime smoke for every environment that should be considered ready. If the main Tencent deploy workflow only smokes Seoul, manually dispatch `E2E - Runtime Smoke` for Tokyo after Tokyo deploy completes.

## Important classification rules

- A successful Vercel `Deploy outbound-dev Production` plus `vercel inspect` Ready means the deployment/alias is healthy, but it does not mean DB-backed smoke passed.
- A Tencent deploy job can succeed for dev-seoul and then fail in the dev-seoul smoke job. In that case downstream dev-tokyo deploy jobs may be skipped. Classify Tokyo as "service health may be OK, but latest SHA was not deployed" even if `/login` returns 200.
- If Vercel and dev-seoul runtime smoke fail with the same assertion after login reaches `/.../home`, treat it as likely smoke-test/UI-data assertion drift before resetting DB or redeploying.
- Example drift observed: `front/tests/runtime-smoke.spec.ts` expected `getByRole('heading', { name: 'Setup checklist' })`; after a later main update, Vercel and Seoul both reached the Home route and showed an H1, but the `Setup checklist` heading was absent. That is not evidence of a Vercel/Tencent server 500 by itself.
- Do not let the top-level Tencent workflow conclusion hide per-target facts. Report image build, Seoul deploy, Seoul smoke, Tokyo deploy, Tokyo cleanup, and Tokyo smoke separately.
- Local root `main` may be behind; do not treat it as the deploy target when `origin/main` advanced.
- If GitHub run state looks stuck while public service is healthy, inspect job steps and VM state before declaring failure. For Tencent, read `/opt/outbound-agent/deployments/current-image`, `/opt/outbound-agent/deployments/current-revision`, service state, and public `/login`; rendered HTML hashes are not authoritative deployed revisions.

## Concise report shape

- 기준 SHA: `<full-sha>`
- Vercel/outbound-dev: deploy run, deployment ID/URL, alias, Ready/error logs, `/login`, smoke result.
- Dev Seoul: image/deploy/cleanup status, `/login`, smoke result and failure reason if any.
- Dev Tokyo: exact latest deployed or skipped, `/login`, smoke result if run.
- Diagnosis: distinguish deployment failure, runtime server error, smoke assertion drift, and exact-version mismatch.
