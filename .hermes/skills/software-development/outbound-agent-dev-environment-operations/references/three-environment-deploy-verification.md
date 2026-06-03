# Three-environment deploy verification pattern

Use this as a concise example for verifying a freshly merged `main` deployment across outbound-dev Vercel and Tencent Seoul/Tokyo.

## Durable lessons

- Establish the exact `origin/main` SHA first and re-fetch once before final reporting.
- Vercel deploy workflow logs may not print the deployment URL. When the workflow succeeds but no URL is visible, query Vercel deployments by commit metadata:
  - `vercel ls outbound-dev --scope querypie --prod --meta githubCommitSha=<full-sha> --no-color`
  - Then run `vercel inspect <deployment-url> --scope querypie --no-color`.
- For latest Vercel deployment logs with filters, use `vercel logs <deployment-url> --scope querypie --no-follow --since 15m --level error --json`.
- `gh run view ... --json jobs` can be slow or hang during active runs, and `gh run view --job <id> --log` may refuse logs while a job is still in progress. Prefer the REST API for lightweight polling:
  - `gh api repos/querypie/outbound-agent/actions/runs/<run-id> --jq '{id,status,conclusion,head_sha,updated_at,html_url}'`
  - `gh api repos/querypie/outbound-agent/actions/runs/<run-id>/jobs --paginate --jq '.jobs[] | {id,name,status,conclusion,started_at,completed_at}'`
- The Tencent main deploy workflow may automatically smoke dev-seoul after deploy while dev-tokyo only proceeds through deploy/cleanup/result jobs. If Tokyo exact deploy succeeds but no Tokyo smoke job appears, dispatch `E2E - Runtime Smoke` manually with `base_url=https://outbound-tokyo.dev.querypie.io`.
- Separate exact-version proof from health proof:
  - workflow SHA and deploy job success prove deployment target/version;
  - `/login` 200 proves public availability;
  - runtime smoke proves login/authenticated DB-backed behavior.

## Evidence shape used in the session

- Vercel:
  - `Deploy outbound-dev Production` succeeded for the exact SHA.
  - `vercel ls ... --meta githubCommitSha=<sha>` found the production deployment.
  - `vercel inspect` verified status `Ready`, aliases, target `production`, and region `icn1`.
  - `/login` returned 200 and recent error logs were empty.
  - A separate `E2E - Runtime Smoke` run succeeded against `https://outbound-dev.vercel.app`.
- Tencent Seoul:
  - image build/publish, deploy, cleanup, and workflow smoke all succeeded for the exact SHA.
- Tencent Tokyo:
  - deploy and cleanup succeeded for the exact SHA;
  - because no Tokyo smoke job appeared in the main deploy workflow, a manual `E2E - Runtime Smoke` run was dispatched and succeeded.
