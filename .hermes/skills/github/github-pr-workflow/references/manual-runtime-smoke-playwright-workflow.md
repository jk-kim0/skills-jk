# Manual deployed-URL Playwright runtime smoke workflow

Use this pattern when adding a GitHub Actions workflow that runs Playwright against an already deployed application URL, especially when the repository also has local Playwright E2E that starts a dev server.

## Recommended shape

- Add a separate Playwright config for deployed runtime smoke instead of reusing the local E2E config when the existing config has `webServer`.
  - Example: `front/playwright.runtime-smoke.config.ts`
  - The deployed-runtime config should require `E2E_BASE_URL` or `PLAYWRIGHT_BASE_URL` and should not start `next dev`.
- Add a narrow package script for the deployed smoke suite.
  - Example: `"test:e2e:runtime-smoke": "playwright test --config=playwright.runtime-smoke.config.ts"`
- Add a `workflow_dispatch` workflow named after the user-visible check, for example `E2E - Runtime Smoke`.
  - Expose a required `base_url` input.
  - Map `base_url` to `E2E_BASE_URL` in the job env.
  - For nested apps, set `defaults.run.working-directory` to the nested app directory and use the nested lockfile for npm cache.
- Install dependencies and browsers in the workflow:
  - `npm ci`
  - Prefer `npx playwright install --with-deps chromium` on Linux/self-hosted runners so browser OS packages such as `libnspr4`, `libnss3`, and `libasound2` are present before Chromium launch.
  - Use plain `npx playwright install chromium` only when the runner image is already known to include Playwright system dependencies.
  - `npm run test:e2e:runtime-smoke`
- Upload `playwright-report/` and `test-results/` with `if: always()`.

## Vercel Deployment Protection

If Preview or Production may be protected, support a secret-backed bypass header in the Playwright config:

```ts
const protectionBypassSecret = process.env.E2E_VERCEL_PROTECTION_BYPASS_SECRET;

use: {
  baseURL,
  extraHTTPHeaders: protectionBypassSecret
    ? {
        "x-vercel-protection-bypass": protectionBypassSecret,
        "x-vercel-set-bypass-cookie": "true",
      }
    : undefined,
}
```

In the workflow, map the repository secret to that env var, for example:

```yaml
env:
  E2E_BASE_URL: ${{ inputs.base_url }}
  E2E_VERCEL_PROTECTION_BYPASS_SECRET: ${{ secrets.VERCEL_AUTOMATION_BYPASS_SECRET }}
```

## Minimal runtime-smoke assertions

Runtime smoke should catch deployed runtime/server failures without mutating much data:

- Assert representative routes return a response and status is `< 500`.
- Load `/login` through `page.goto()` and assert stable visible controls such as heading and submit button.
- If seed credentials are stable and intended for the environment, submit the login form and assert the first authenticated route response is `< 500` and the expected heading appears.
- Keep this separate from deep product-flow E2E; runtime smoke is for catching schema mismatch/runtime 500s quickly.

## Verification for workflow PRs

For this class of PR, static verification is usually enough before push when local dependencies are absent:

```sh
actionlint .github/workflows/*.yml
python3 - <<'PY'
from pathlib import Path
import yaml
for p in sorted(Path('.github/workflows').glob('*.yml')):
    yaml.safe_load(p.read_text())
print('workflow yaml ok')
PY
node -e "JSON.parse(require('fs').readFileSync('front/package.json','utf8')); console.log('package.json ok')"
git diff --check
```

After opening the PR, verify that automatic PR checks attached to the current head SHA. Do not expect the new `workflow_dispatch` runtime-smoke workflow to run automatically unless the user asked for an automatic trigger.
