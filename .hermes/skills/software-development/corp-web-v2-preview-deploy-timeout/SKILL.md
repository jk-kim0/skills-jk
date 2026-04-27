---
name: corp-web-v2-preview-deploy-timeout
description: Diagnose and fix Preview Deploy GitHub Actions failures in corp-web-v2 when Vercel stays BUILDING and the local polling script times out.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-v2, github-actions, vercel, preview-deploy, ci, debugging]
---

# corp-web-v2 Preview Deploy Timeout

Use when a corp-web-v2 PR shows:
- `Deploy on Preview` failed
- validate/typecheck/test passed
- failed log contains `Deployment polling timed out after 600s`

## Root cause pattern

This failure can be a polling-threshold problem, not an application build failure.

In this repo, the key files are:
- `.github/workflows/deploy-preview.yml`
- `scripts/deploy/index.js`

The workflow runs `npm run deploy` under `scripts/deploy/`.
The script creates a Vercel deployment, then polls status until READY.
If Vercel remains `BUILDING` longer than the hardcoded timeout, GitHub Actions fails even though the deployment itself may still be progressing normally.

## Investigation steps

1. Confirm only preview deploy failed:
   - `gh pr checks <PR_NUMBER> --repo querypie/corp-web-v2`
   - If build/test/typecheck are green and only `Deploy` failed, inspect the deploy workflow.

2. Read failed logs:
   - `gh run list --repo querypie/corp-web-v2 --branch <branch> --limit 10`
   - `gh run view <RUN_ID> --repo querypie/corp-web-v2 --log-failed`

3. Look for this signature:
   - repeated `Deployment status: BUILDING`
   - final error `Deployment polling timed out after 600s`

4. Verify the timeout source:
   - read `scripts/deploy/index.js`
   - check `POLL_TIMEOUT_MS`

## Recommended fix

Prefer a minimal fix in a separate PR when the original PR is feature/content work.

Update `scripts/deploy/index.js` to:
- raise the default timeout (20 minutes worked for this case)
- make timeout configurable with `DEPLOY_POLL_TIMEOUT_MS`
- validate invalid timeout values early

Reference shape:

```js
const POLL_INTERVAL_MS = 5_000;
const DEFAULT_POLL_TIMEOUT_MS = 20 * 60 * 1_000;
const POLL_TIMEOUT_MS = Number(process.env.DEPLOY_POLL_TIMEOUT_MS || DEFAULT_POLL_TIMEOUT_MS);

if (!Number.isFinite(POLL_TIMEOUT_MS) || POLL_TIMEOUT_MS <= 0) {
  throw new Error('DEPLOY_POLL_TIMEOUT_MS must be a positive number of milliseconds');
}
```

## Verification

From `scripts/deploy/`:

```bash
npm ci
node --check index.js
DEPLOY_POLL_TIMEOUT_MS=abc node --input-type=module -e "import('./index.js').catch(err => { console.error(err.message); process.exit(1); })"
```

Expected:
- syntax check passes
- invalid env test exits non-zero and prints the validation error

## PR guidance

If the failing PR is unrelated to deployment infrastructure:
1. create a new branch from latest `main`
2. commit only the deploy-timeout fix
3. open a separate PR with root cause clearly stated
4. keep the original feature PR clean

Suggested PR framing:
- Title: `fix: prevent preview deploy polling timeouts`
- Root cause: Vercel deployment stayed `BUILDING` longer than the script's hardcoded 10 minute timeout
- Clarify that validate/build/test checks were green, so the issue was polling behavior rather than app correctness

## Pitfalls

- Do not assume preview deploy failure means Next.js build failure; check validate jobs first.
- Do not mix CI infrastructure fixes into an unrelated content/feature PR if a clean separate PR is feasible.
- If local verification fails with missing `@vercel/sdk`, run `npm ci` inside `scripts/deploy/` first.
