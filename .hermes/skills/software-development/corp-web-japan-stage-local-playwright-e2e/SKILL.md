---
name: corp-web-japan-stage-local-playwright-e2e
description: Add or update local-only Playwright E2E checks against deployed stage pages in corp-web-japan without wiring them into CI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, playwright, e2e, stage, local-only, testing]
---

# corp-web-japan stage local-only Playwright E2E

Use this when the user asks for browser E2E coverage against a deployed `stage.querypie.ai` page in `corp-web-japan`, especially for flows that cannot be proven by the repo's normal source-level Node tests.

## When to use
- the target is a real deployed stage URL, not just local source structure
- the flow is interactive and browser-state-dependent (form submit, unlock, cookie persistence, redirect behavior)
- the user wants verification, but not full CI integration
- the repo already has `playwright.local.config.mjs` and `tests-local/` patterns available

## Key findings
- This repo's default CI path is still `npm run test:ci` plus build; stage browser checks should stay local-only unless the user explicitly asks to add CI wiring.
- The existing pattern is to place stage-only browser tests under `tests-local/src/app/**` and expose them via explicit `package.json` scripts such as:
  - `e2e:local:contact-us:stage`
  - `e2e:local:whitepaper-gating:stage`
- `playwright.local.config.mjs` should use a single generic base URL override:
  - `process.env.LOCAL_E2E_BASE_URL`
  - default to `https://stage.querypie.ai`
- The repo now documents local-only browser checks in `docs/local-e2e.md`.
  - When adding or updating a local stage E2E, keep that document aligned with the current inventory, commands, base URL policy, and test scope.
- A fresh worktree may not have `@playwright/test` installed locally even when the root repo has normal dependencies.
- To avoid putting `node_modules` inside the worktree, a practical pattern is:
  1. install `@playwright/test` once at the repo root with `npm install --no-save @playwright/test`
  2. run tests from the worktree
  3. if browsers are missing, run `npx playwright install chromium`
- For the current whitepaper gating demo, the deployed internal reference route is:
  - `/internal/whitepaper-gating-demo`
- Current successful gating submit payload behavior on stage:
  - `POST /api/gating-form/unlock` returns `200`
  - sets cookie `qp-gated-internal-whitepaper-gating-demo=1`
  - unlock persists across reload

## Recommended workflow
1. Start from latest `origin/main` in a fresh worktree.
2. Confirm the actual deployed stage path before writing assertions.
   - Do not assume the route from memory.
   - Probe likely paths or inspect source if needed.
3. Verify whether a similar local-only Playwright pattern already exists:
   - `playwright.local.config.mjs`
   - `tests-local/src/app/**`
   - `package.json` `e2e:local:*` scripts
4. Decide whether the new E2E belongs in the shared local Playwright config or needs a route-specific config.
   - Prefer reusing `playwright.local.config.mjs`.
5. Add the test file under `tests-local/src/app/<route>/page.e2e.mjs`.
6. Add a dedicated script in `package.json`.
7. Keep it out of `test:ci` and GitHub Actions unless the user explicitly asks for CI integration.
8. Run:
   - `npm run <new-e2e-script>`
   - `npm run test:ci`
9. Commit, push, and open a Draft PR if requested.

## Whitepaper gating demo assertions
For `/internal/whitepaper-gating-demo`, good baseline checks are:

### Initial gated state
- title is `Internal Whitepaper Gating Demo | QueryPie AI`
- preview heading `Gating form demo` is visible
- preview body copy is visible
- unlock heading `全文を読む` is visible
- submit button is disabled initially
- hidden gated heading `Hidden section` is absent initially

### Unlock flow
Fill:
- `*姓`
- `*名`
- `*ビジネス用メールアドレス`
- `*会社名`
- `*部署／役職`
- optional phone
- inquiry = `demo-request`
- one product checkbox, e.g. `社内業務効率化｜AI Crew`
- timeline = `3ヶ月以内`

Then assert:
- submit becomes enabled
- click submit
- heading `Hidden section` becomes visible
- hidden content copy becomes visible
- `全文を読む` heading disappears

### Cookie persistence
After unlock:
- inspect browser cookies for `qp-gated-internal-whitepaper-gating-demo=1`
- reload the page
- hidden section remains visible
- gating form / `全文を読む` does not reappear

## Example script additions
`package.json`

```json
{
  "scripts": {
    "e2e:local:whitepaper-gating:stage": "npx playwright test tests-local/src/app/internal/whitepaper-gating-demo/page.e2e.mjs --config=playwright.local.config.mjs"
  }
}
```

`playwright.local.config.mjs`

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
    baseURL:
      process.env.LOCAL_E2E_BASE_URL ??
      process.env.CONTACT_US_E2E_BASE_URL ??
      'https://stage.querypie.ai',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  outputDir: '.playwright-local/results',
});
```

## Contact-us stage findings

For `https://stage.querypie.ai/contact-us`, the current deployed behavior supports a richer E2E contract than the original baseline.

Useful assertions that were confirmed on stage:
- valid prefill query example:
  - `?inquiry=demo-request&product=aip&product=ai-dashi`
  - expected result: inquiry select value becomes `demo-request`, and both `#contact-us-product-aip` and `#contact-us-product-ai-dashi` are checked
- invalid/duplicate prefill query example:
  - `?inquiry=invalid-key&product=unknown&product=acp&product=acp&product=partnership`
  - expected result: inquiry remains empty, unknown product is ignored, valid products are checked, and checked product count is `2`
- partial prefill must not bypass other required fields:
  - even when inquiry/product are prefilled, submit should stay disabled until the remaining required inputs are completed, including timeline
- free email validation is active on stage:
  - using `gmail.com` currently shows `会社または教育機関のメールアドレスを入力してください。`
  - submit remains disabled until the email is replaced with a business or educational address
- current hosted submit path succeeds on stage:
  - after valid completion, the page shows `送信が完了しました。`
  - confirmation copy includes `担当チームより追ってご連絡いたします。`

Recommended contact-us helper shape:
- add a small `gotoContactUs(page, baseURL, query = '')`
- add a reusable `fillRequiredFields(page, { email, message })`
- keep the final submit-flow test separate from prefill/validation tests so failures are easier to localize

## Practical pitfalls
- A local main branch can be behind origin; create the worktree from `origin/main`, not local `main`.
- In this repo specifically, local E2E files such as `tests-local/` and `playwright.local.config.mjs` may exist on latest `origin/main` even when they are absent from a stale local `main`; verify from a fresh worktree before assuming the setup is missing.
- `gh pr create` can warn about uncommitted changes if you leave a temporary PR body file in the worktree.
- In a fresh worktree, Playwright may fail twice in sequence:
  1. missing `@playwright/test`
  2. missing Chromium browser binary
- The fix is usually:
  - `npm install --no-save @playwright/test` at the repo root
  - `npx playwright install chromium`
- Keep local-only stage E2E separate from standard CI to avoid flaky or environment-coupled pull request checks.

## Verification checklist
- Target stage route was verified directly in the browser.
- New E2E test passes against the deployed stage page.
- `npm run test:ci` still passes.
- The new script name clearly indicates local-only stage scope.
- CI workflow remains unchanged unless the user explicitly requested CI integration.
