# Deployed dev-server E2E workflow pattern

Use this reference when adding or repairing GitHub Actions workflows that run browser E2E tests against the three already-deployed Outbound Agent dev servers.

## Durable lesson

When the user asks to run E2E tests on the three dev servers, interpret the target as existing deployed environments, not three Actions-local Next.js servers and not deployment jobs. The workflow should test the selected environment in-place.

## Recommended workflow shape

- Trigger: `workflow_dispatch` only, unless the user explicitly asks for automatic runs.
- Target input: a choice among the three dev environments:
  - `outbound-dev` -> `https://outbound-dev.vercel.app`
  - `tencent/outbound-seoul` -> `https://outbound-seoul.dev.querypie.io`
  - `tencent/outbound-tokyo` -> `https://outbound-tokyo.dev.querypie.io`
- Branch input: optionally allow checkout branch/ref, defaulting to `main`.
- Naming: if requested, apply the exact requested prefix to workflow/job/step display names and workflow YAML filename.
- Do not start Next.js, PostgreSQL, or Docker services in the E2E workflow when the purpose is deployed-server validation.
- Do not run Prisma migrate/seed/generate as part of deployed-server E2E unless the user explicitly requested a white-box DB-backed workflow.
- Avoid SSH tunnels and DB secrets for black-box deployed-server E2E.
- Set the Playwright base URL from the selected target and disable local webServer startup, for example via `E2E_BASE_URL` and `E2E_SKIP_WEB_SERVER=true`.
- Upload Playwright report and test-results artifacts. If target names contain `/`, avoid using the raw target string in artifact names; use `github.run_id` or a sanitized value.

## Seed account and auth boundary

For black-box E2E, prefer a pre-seeded E2E user in the dev seed fixture over DB setup helpers in the test. The test can then log in through `/login`, create an isolated Team, create pre-auth entities, and clean up through the UI.

Email Sender / Gmail OAuth setup is a separate non-interactive auth problem. Until a durable automated sender-auth path exists, run the scenario only up to the Email Sender boundary and leave the sender-auth-dependent continuation as an explicit skipped TODO.

## CI debugging pattern from PR workflow repair

If regular PR CI fails after adding a seed user or E2E spec:

1. Use `gh pr checks <pr>` and `gh run view <run-id> --log-failed` to get the exact failing job and line.
2. Fix syntax/lint failures first; generated TypeScript test files often fail because raw newlines were accidentally inserted inside string literals. Use escaped `\n` inside strings or template literals intentionally.
3. If a seed fixture changes, update repository contract tests that intentionally assert the fixture inventory.
4. Re-run lightweight static checks before pushing: `git diff --check`, YAML parse, and `actionlint` for the workflow file.
5. Push and monitor the latest head until `Front app CI` and the aggregate `CI result` finish.
