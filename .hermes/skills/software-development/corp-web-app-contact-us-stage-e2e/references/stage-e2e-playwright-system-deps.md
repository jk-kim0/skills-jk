# Stage E2E Playwright system dependency failure

## When this applies

Use this reference when a corp-web-app stage Playwright workflow runs on a self-hosted Linux runner and every browser test fails before page interaction begins.

## Failure signature

Observed on `E2E - Contact Us Stage`:

- job reaches the Playwright test step, so checkout, Node setup, `npm ci`, and browser binary install succeeded
- all Chromium tests fail at `browserType.launch`
- Playwright prints:
  - `Host system is missing dependencies to run browsers.`
  - suggested command: `sudo npx playwright install-deps`
  - apt packages such as `libnspr4`, `libnss3`, and `libasound2`
- this is not a Contact Us page assertion failure; the browser never launched

## Root cause

The workflow installed only the browser binary with:

```bash
npx playwright install chromium
```

On fresh or minimal self-hosted Linux runners, Chromium also needs OS packages. Playwright can install both binary and system packages via `--with-deps`.

## Recommended repo fix

Keep a lightweight local script if desired, and add a CI/self-hosted runner script in `tests/package.json`:

```json
{
  "scripts": {
    "install:browsers": "npx playwright install chromium",
    "install:browsers:with-deps": "npx playwright install --with-deps chromium"
  }
}
```

Then make self-hosted Linux workflow jobs call:

```yaml
- name: Install Playwright browser and system dependencies
  run: npm run install:browsers:with-deps
```

Apply this to any workflow that launches Playwright Chromium on the same runner class, not only the first workflow where the failure appeared.

## Verification pattern

1. Validate syntax cheaply:

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('tests/package.json','utf8')); console.log('tests/package.json ok')"
ruby -e "require 'yaml'; YAML.load_file('.github/workflows/e2e-contact-us-stage.yml'); puts 'workflow yaml ok'"
```

2. Push the branch and manually dispatch the workflow on that branch, because these E2E workflows are `workflow_dispatch` and may not attach as PR checks automatically.
3. Confirm the install step `Install Playwright browser and system dependencies` succeeds.
4. If the later E2E body still fails or hangs, classify it separately as a downstream hosted E2E/page/server issue; do not conflate it with the original missing browser OS dependency failure.

## Reporting guidance

Report the original run/job URL, the missing dependency signature, the PR URL, and the manual verification run URL. Avoid long passive waits; if the test body exceeds the expected quick feedback window, schedule or perform a later status check and state that the original dependency-install issue has already been cleared.
