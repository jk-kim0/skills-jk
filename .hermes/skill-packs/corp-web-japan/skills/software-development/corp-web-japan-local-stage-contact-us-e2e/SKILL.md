---
name: corp-web-japan-local-stage-contact-us-e2e
description: Add and run local-only Playwright E2E checks for corp-web-japan /t/contact-us against stage.querypie.ai without including them in CI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, playwright, e2e, local-only, stage, contact-us]
---

# corp-web-japan local stage contact-us E2E

Use this when the user wants a real browser E2E check for `corp-web-japan` against the deployed stage site, especially for `/t/contact-us`, but does **not** want the E2E suite to run in CI.

## When to use
- The user asks to verify a deployed stage result directly on `https://stage.querypie.ai`
- The task is specifically about `/t/contact-us` preview behavior
- The user wants Playwright/browser-style E2E code added to the repo
- The user explicitly wants the E2E flow to remain local-only and excluded from `test:ci`

## Proven approach

### 1. Start from latest `origin/main`
For new work after a PR merge, create a fresh worktree from the latest `origin/main`.

Important finding from this task:
- local `main` may be dirty and block `git pull --ff-only`
- in that case, do **not** force local `main`
- instead, create the new worktree directly from `origin/main`

Safe pattern:

```bash
git fetch origin main --quiet
git worktree add .worktrees/feat-contact-us-stage-e2e -b feat/contact-us-stage-e2e origin/main
```

## 2. Verify the deployed stage behavior first
Before writing the test, check the real deployed page.

For this task the live stage observations were:
- `https://stage.querypie.ai/t/contact-us` rendered normally
- page title was `お問い合わせ | QueryPie AI`
- stable query prefills worked
- actual submit currently failed with visible Japanese error text
- direct POST to `https://stage.querypie.ai/contact-us/submit` returned `502`
- body:
  - `{"success":false,"message":"お問い合わせの送信に失敗しました。しばらくしてから再度お試しください。"}`

Important lesson:
- the deployed stage outcome may be `server-error` even when the page itself is healthy
- write the E2E test so the expected submit outcome is configurable instead of hardcoding success

## 3. Keep local-only E2E separate from repo CI tests
Do **not** put these Playwright tests under the repo's normal `tests/` tree if `test:ci` or CI discovers that tree automatically.

Use a separate local-only directory, for example:

```text
tests-local/src/app/t/contact-us/page.e2e.mjs
```

This keeps the path aligned with the source route while still making the local-only nature obvious.

## 4. Add a dedicated local Playwright config
Create a dedicated config file such as:

```text
playwright.local.config.mjs
```

Important details that mattered here:
- set `testMatch: ['**/*.e2e.mjs']`
- otherwise Playwright may report `No tests found`
- set a local-only output directory such as `.playwright-local/results`
- use `baseURL` from env with a safe default of `https://stage.querypie.ai`

Suggested shape:

```js
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: ['**/*.e2e.mjs'],
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  timeout: 60_000,
  use: {
    baseURL: process.env.CONTACT_US_E2E_BASE_URL ?? 'https://stage.querypie.ai',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  outputDir: '.playwright-local/results',
});
```

## 5. Add the Playwright dependency explicitly
Even if `npx playwright --version` works globally, the repo still needs the package dependency for imports like `@playwright/test`.

Required repo change:

```bash
npm install -D @playwright/test
```

Without this, a local config that imports `@playwright/test` fails with:
- `ERR_MODULE_NOT_FOUND: Cannot find package '@playwright/test'`

## 6. Keep the E2E script local-only in package.json
Add a dedicated script, but do **not** wire it into `test`, `test:ci`, or GitHub Actions.

Example:

```json
{
  "scripts": {
    "e2e:local:contact-us:stage": "npx playwright test tests-local/src/app/t/contact-us/page.e2e.mjs --config=playwright.local.config.mjs"
  }
}
```

Important rule:
- `test:ci` must remain unchanged except for unrelated repo evolution
- the local-only E2E script should be opt-in only

## 7. Ignore local Playwright artifacts
Add to `.gitignore`:

```gitignore
.playwright-local/
```

This keeps traces/screenshots/videos local.

## 8. Make the submit assertion environment-driven
This was the most important experiential learning from the task.

Do **not** assume the current stage submit will succeed.

Parameterize the submit expectation with an env var such as:
- `CONTACT_US_EXPECTED_SUBMIT_OUTCOME`

Supported values used here:
- `server-error`
- `success`

Recommended test flow:
- always test page render
- always test query prefills
- for submit:
  - if `success`, assert success state UI
  - if `server-error`, assert the visible failure banner text

The exact stage failure text observed in this task was:
- `お問い合わせの送信に失敗しました。しばらくしてから再度お試しください。`

## 9. Keep the E2E file route-aligned
For `/t/contact-us`, use:

```text
tests-local/src/app/t/contact-us/page.e2e.mjs
```

This matches the repo's preferred principle that test code paths should mirror the source path as closely as practical.

## 10. Proven test coverage for this route
The following three checks worked well and were fast enough for local-only use:

1. Page render sanity
- navigate to `/t/contact-us`
- verify title
- verify the heading
- verify key fields exist
- verify submit button starts disabled

2. Stable query prefills
- navigate with `?inquiry=demo-request&product=aip&product=ai-dashi`
- verify inquiry select value
- verify AIP and AI Dashi are checked

3. Submit flow
- fill all required fields
- select a valid inquiry/product/timeline
- submit
- assert either `success` or `server-error` based on env

## 11. Root-cause pattern when stage submit returns 502

During this task, the stage submit failure was not caused by the E2E code itself.
The root cause was malformed Vercel runtime env in `corp-web-japan`.

### What was observed
- `/t/contact-us` page render was healthy
- direct POST to `/contact-us/submit` returned `502`
- Slack API calls failed with `invalid_auth`
- Vercel env values for `corp-web-japan` had been copied in a bad state:
  - plain values contained extra wrapping quotes, for example:
    - `SLACK_CHANNEL_ALERT_WEBSITE_BUSINESS_INQUIRIES="\"C083Y0300M7\""`
    - `SALESFORCE_ENDPOINT="\"https://...\""`
  - sensitive Slack token values could not be recovered from `vercel env pull` / `vercel env run`; those surfaces only exposed masked / empty values

### Useful diagnosis commands
Inspect effective env layout via API:

```bash
python3 - <<'PY'
import os, json, urllib.request
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
headers={'Authorization': f'Bearer {token}'}
url=f'https://api.vercel.com/v10/projects/<project-id>/env?teamId={team}&limit=100'
req=urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as r:
    data=json.load(r)
for e in data.get('envs', []):
    if e.get('key') in ('SLACK_BOT_OAUTH_TOKEN','SLACK_CHANNEL_ALERT_WEBSITE_BUSINESS_INQUIRIES','SALESFORCE_ENDPOINT'):
        print(json.dumps({
          'key': e['key'],
          'target': e.get('target'),
          'customEnvironmentIds': e.get('customEnvironmentIds'),
          'value': e.get('value'),
        }, ensure_ascii=False))
PY
```

Check what a linked local checkout actually receives:

```bash
vercel env pull .env.staging.local --environment preview --git-branch main
python3 - <<'PY'
from pathlib import Path
for line in Path('.env.staging.local').read_text().splitlines():
    if line.startswith(('SLACK_BOT_OAUTH_TOKEN=','SLACK_CHANNEL_ALERT_WEBSITE_BUSINESS_INQUIRIES=','SALESFORCE_ENDPOINT=')):
        print(repr(line))
PY
```

Check whether a source project can expose sensitive values through `env run`:

```bash
vercel env run --environment=preview -- env | grep -E '^(SLACK_BOT_OAUTH_TOKEN|SLACK_CHANNEL_ALERT_WEBSITE_BUSINESS_INQUIRIES|SALESFORCE_ENDPOINT)='
```

Important finding:
- `vercel env run` may still show an empty sensitive value for `SLACK_BOT_OAUTH_TOKEN`
- do not assume you can reconstruct sensitive tokens from CLI output alone

### Reliable corrective actions
1. Fix recoverable plain values with the Vercel CLI:

```bash
vercel env update SLACK_CHANNEL_ALERT_WEBSITE_BUSINESS_INQUIRIES production --value C08JNAZDU5A --yes
vercel env update SLACK_CHANNEL_ALERT_WEBSITE_BUSINESS_INQUIRIES preview --value C083Y0300M7 --yes
vercel env update SALESFORCE_ENDPOINT production --value https://querypie.my.site.com/... --yes
vercel env update SALESFORCE_ENDPOINT preview --value https://querypie--dev.sandbox.my.site.com/... --yes
```

2. Add code-level normalization so malformed quoted env values do not break the runtime:
- add a shared helper like `normalizeEnvironmentValue()` under `src/lib/forms/server/environment.ts`
- strip repeated outer quote layers from plain env values before use

3. For non-production only, make Slack non-fatal if env is missing/invalid:
- production should still treat Slack as required
- stage/preview can proceed after Salesforce best-effort even if Slack auth is broken

This allows stage E2E to validate the rest of the submit path while secrets are being corrected.

## 12. Useful current commands
Run local-only E2E against current stage state:

```bash
CONTACT_US_EXPECTED_SUBMIT_OUTCOME=server-error npm run e2e:local:contact-us:stage
```

If stage later becomes healthy:

```bash
CONTACT_US_EXPECTED_SUBMIT_OUTCOME=success npm run e2e:local:contact-us:stage
```

Standard CI-safe verification still remains:

```bash
npm run test:ci
```

## Pitfalls found

1. `npx playwright test ...` can say `No tests found`
- fix by adding `testMatch: ['**/*.e2e.mjs']` in the local config

2. Global Playwright availability is not enough
- the repo still needs `@playwright/test` in `devDependencies`

3. Stage may currently fail submit even after route deployment
- do not write the test as unconditional success
- make the expected outcome configurable

4. Keep E2E out of CI by structure and script wiring
- local-only directory
- dedicated script
- no inclusion in `test:ci`
- no GitHub Actions wiring

5. If local `main` is dirty, do not try to force-update it just to branch
- create the worktree directly from `origin/main`

## Done criteria
- deployed stage page behavior has been verified manually first
- local-only Playwright config exists
- route-aligned E2E file exists under `tests-local/src/...`
- `@playwright/test` is added as a devDependency
- local-only script exists in `package.json`
- local Playwright artifacts are gitignored
- `npm run test:ci` still passes without running the E2E suite
- the local-only E2E run passes against the current expected stage outcome
