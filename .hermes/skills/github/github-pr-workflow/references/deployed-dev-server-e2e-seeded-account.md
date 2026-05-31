# Deployed dev-server E2E with seeded account only

Use this when adding a manual GitHub Actions workflow for an existing Playwright E2E suite that must run against already-deployed development servers.

## Correct model

- Treat named dev servers such as `outbound-dev`, `tencent/outbound-seoul`, and `tencent/outbound-tokyo` as deployed runtime targets, not as local server slots.
- The workflow should not deploy the app, start `next dev`, create a local PostgreSQL service, open SSH DB tunnels, or inject Prisma helpers unless the user explicitly asks for white-box DB-backed E2E.
- Seed only the prerequisite account through the dev deployment seed path when that is enough for login.
- The Playwright spec should create a fresh Team through the UI and proceed through all available UI setup steps.
- If later steps require external sender authentication such as Gmail OAuth, stop at that boundary and mark the remaining test as `test.skip` / TODO rather than fabricating sender rows through the DB.

## Workflow shape

- `workflow_dispatch` only when the user asks for manual execution.
- Add a choice input for the deployed target, e.g. `outbound-dev`, `tencent/outbound-seoul`, `tencent/outbound-tokyo`.
- Map each choice to `E2E_BASE_URL`.
- Set `E2E_SKIP_WEB_SERVER=true` so the Playwright config does not start a local server.
- Install dependencies and Playwright browsers, then run the existing E2E script against the deployed URL.
- Upload Playwright report and test-results with artifact names that do not contain `/` from target names; use `github.run_id` or sanitize the target.

## Playwright config shape

- Keep local defaults working: when `E2E_BASE_URL` is absent, use `http://127.0.0.1:<port>` and allow the local webServer.
- When `E2E_SKIP_WEB_SERVER=true`, set `webServer` to `undefined`.
- Do not import DB-only helpers into the deployed-target config if the deployed spec no longer uses them.
- Preserve Vercel protection bypass headers if the deployed URL may be protected.

## Pitfalls

- Do not reinterpret “3개 Dev 서버” as three local dev-server ports unless the user explicitly says to run isolated local servers.
- Do not add DB secrets, SSH tunnel setup, PostgreSQL service containers, migration steps, or Prisma client generation just because an older local E2E helper used DB access.
- If the E2E originally created sender identities through Prisma to avoid Gmail OAuth, remove that white-box setup for deployed black-box E2E and skip the sender-authenticated part until a proper non-interactive sender setup exists.
- Make PR text explicit: the workflow tests already-deployed servers only; any Preview Deploy check attached to the PR is from existing repository workflows, not from the new E2E workflow.
