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

## News coverage on stage

When the user asks for browser E2E around the local news flow, keep the coverage in two separate files rather than one mixed publication file:

- `tests-local/src/app/t/news/page.e2e.mjs`
- `tests-local/src/app/news/page.e2e.mjs`
- helper fixture file: `tests-local/helpers/news-stage-fixtures.mjs`

Recommended script names:
- `e2e:local:news-list:stage`
- `e2e:local:news-detail:stage`

Recommended assertions for the list file:
- `/t/news` title and primary heading are visible
- the page description is visible
- representative cards point to local `/news/:id/:slug` hrefs rather than directly to external destinations

Recommended assertions for the detail file:
- for one redirect-backed post (for example news 12), verify both `/news/:id` and `/news/:id/:slug` resolve to the configured external target
- for local-body posts (currently news 13 and 14), verify:
  - `/news/:id` redirects to the canonical local slug route
  - a mismatched slug redirects to the canonical local slug route
  - the canonical local route renders the local MDX body instead of redirecting away
  - author metadata and a representative body heading are visible
  - the related-news heading is visible

Important practical lesson from this work:
- respect the exact stage target the user names and verify it literally before encoding assertions or scripts
- if the requested stage host/path currently returns a not-found page or serves a different app than expected, do not silently substitute another host in the final implementation without calling it out
- if the user later corrects the exact target, update the scripts and docs to match that exact host

## Publication blog/whitepaper coverage on stage

When the user asks for browser E2E around blog/whitepaper rendering on `https://stage.querypie.ai`, keep blog and whitepaper coverage in separate files rather than grouping them into generic publication list/detail files.

Recommended structure:
- `tests-local/src/app/blog/page.e2e.mjs`
- `tests-local/src/app/whitepapers/page.e2e.mjs`
- `tests-local/helpers/blog-stage-fixtures.mjs`
- `tests-local/helpers/whitepaper-stage-fixtures.mjs`
- shared utility file such as `tests-local/helpers/stage-page-helpers.mjs`

Recommended script names:
- `e2e:local:blog:stage`
- `e2e:local:whitepapers:stage`

Stage-backed fixtures that were verified as useful:
- visible blog list card sample:
  - title: `AI攻撃ツールが55カ国のファイアウォール600台を突破──ファイアウォールの先にある"データ"をどう守るか`
  - current href on stage: `/blog/29/ai-attack-tool-firewall-breach-data-protection`
- visible blog detail sample:
  - `/blog/1/agentless-philosophy`
  - title: `QueryPieがAgentless哲学にこだわる理由`
- hidden blog sample that stays directly reachable while excluded from `/blog`:
  - `/blog/23/querypie-payroll-partnership`
  - title: `株式会社ペイロールとQueryPieがAIセキュリティ分野で技術提携`
- gated whitepaper sample:
  - `/whitepapers/24/ai-transformation-japan`
  - title: `なぜ今、日本企業がAIトランスフォーメーションに取り組むべきなのか`
  - cookie: `qp-gated-whitepaper-24=1`
- hidden redirect whitepaper sample:
  - `/whitepapers/25/ai-transformation-japan`
  - redirects to `/whitepapers/24/ai-transformation-japan`

Important stage findings:
- blog hidden posts are intentionally absent from the list but still render on direct local detail URLs
- whitepaper hidden redirect shadow records are absent from the list
- current whitepaper list cards still point to upstream `querypie.com/ja` hrefs rather than local detail URLs, so list tests should assert the actual hosted href contract, not assume local links
- the whitepaper gating form on the real detail page uses custom select markup; generic selectors like `select[name="inquiry"]` may fail there even if they work on other forms
- a robust gating fill helper for the current stage page is:
  - `page.locator('form select').first().selectOption('demo-request')`
  - `page.getByLabel('社内業務効率化｜AI Crew').check()`
  - `page.locator('form select').nth(1).selectOption({ label: '3ヶ月以内' })`

Recommended assertions for the blog file:
- list page title `ブログ | QueryPie AI`
- list heading is visible
- a representative visible card is present and its local href matches the current stage route
- a representative hidden blog title is absent from the list
- `/blog/:id` redirects to the canonical `/blog/:id/:slug` route
- a mismatched slug also redirects to the canonical route
- visible blog detail renders title, author metadata, a representative body heading, and the related-posts section
- hidden blog detail remains directly reachable and renders like a normal article page

Recommended assertions for the whitepaper file:
- list page title `ホワイトペーパー | QueryPie AI`
- list heading is visible
- a representative visible card is present and its href matches the current upstream QueryPie destination
- a representative hidden redirect/shadow whitepaper title is absent from the list
- `/whitepapers/:id` redirects to the canonical `/whitepapers/:id/:slug` route
- a mismatched slug also redirects to the canonical route
- gated whitepaper preview renders title, author metadata, CTA link, preview copy, and `全文を読む` before submit
- submit starts disabled, becomes enabled after filling the required fields, and reveals gated-only content on success
- unlock cookie is set and unlocked state persists after reload
- hidden redirect whitepaper shadow record lands on the canonical local whitepaper route

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
