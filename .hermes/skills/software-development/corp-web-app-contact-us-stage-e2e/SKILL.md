---
name: corp-web-app-contact-us-stage-e2e
description: Add or update corp-web-app Playwright E2E coverage for the public Contact Us page on stage.querypie.com, using the repo's existing tests/ runner instead of inventing a separate local-only harness.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, playwright, e2e, contact-us, stage, query-prefill]
---

# corp-web-app Contact Us stage E2E

Use this when the user asks for E2E coverage of `corp-web-app` Contact Us on `https://stage.querypie.com`.

## Why this skill exists

A common failure mode is to mix up:
- `corp-web-app`
- `corp-web-v2`
- `corp-web-japan`

These repos have different stage domains, different page shells, and different existing E2E patterns.

For `corp-web-app` specifically:
- stage domain is `https://stage.querypie.com`
- Contact Us currently renders the newer public shell with:
  - H1 `Contact Us`
  - lead copy including `Reach out today!`
  - submit button label `Proceed`
  - helper link text `Terms of Use`
- the repo already has a Playwright runner under `tests/`
- there is already a mixed UTM + Contact Us spec at `tests/e2e/utm-tracking.spec.ts`
- Contact Us supports stable query prefills via `inquiry` and repeatable `product` query params

Do NOT copy the `corp-web-japan` local-only Playwright harness pattern into this repo unless the user explicitly asks for a separate local-only structure.

## Preconditions

Before editing anything:
1. confirm the target repo is really `corp-web-app`
2. confirm the requested work should continue on an existing PR branch or start from latest `origin/main`
3. verify whether the current local branch is actually based on latest `origin/main`

Useful checks:
```bash
git fetch origin --prune
git rev-parse origin/main
git merge-base HEAD origin/main
git rev-list --oneline origin/main..HEAD | sed -n '1,20p'
gh pr list --state open --limit 50 --json number,title,headRefName,baseRefName,url,isDraft
```

If the local branch is stale, untracked remotely, or not rebased onto latest main, do NOT continue there.
Create a fresh worktree/branch from `origin/main`.

## Existing implementation sources of truth

Read these first:
- `src/app/en/company/contact-us/page.tsx`
- `src/components/widget/contact-sales/contact-sales-form.component.tsx`
- `src/components/widget/contact-sales/contact-sales.i18n.tsx`
- `src/components/widget/form/lib/messages.ts`
- `tests/e2e/utm-tracking.spec.ts`
- `tests/e2e/playwright.config.ts`
- `tests/package.json`

## Important implementation facts

### Current page shell on stage.querypie.com
The English Contact Us page currently uses:
- H1: `Contact Us`
- lead text containing:
  - `Connect with our experts. Accelerate your success.`
  - `Quick, friendly guidance for your business—answers you'll appreciate, support you'll trust.`
  - `Reach out today!`
- submit button: `Proceed`
- helper link text: `Terms of Use`

If your assertions expect `Submit`, `Terms`, or the old `corp-web-v2` shell, you are in the wrong repo or using the wrong reference.

### Existing Playwright runner
`corp-web-app` already has a separate Playwright workspace under `tests/`:
- config: `tests/e2e/playwright.config.ts`
- default base URL: `process.env.BASE_URL || 'https://www.querypie.com'`
- execution happens through `tests/package.json`

So for Contact Us E2E:
- add a dedicated spec under `tests/e2e/`
- add a script in `tests/package.json`
- document it in `docs/` and `tests/README.md`
- do not create a new root-level Playwright harness unless explicitly requested

### Query prefill contract
Stable query params are defined in `src/components/widget/form/lib/messages.ts`:
- `inquiry`
- repeatable `product`

Current stable keys include:
- inquiry:
  - `demo-request`
  - `quote-request`
  - `technical-question`
  - `partnership`
  - `other`
- product:
  - `aip`
  - `acp`
  - `fde`
  - `partnership`

The prefill logic is applied by:
- `applyContactSalesQueryPrefill()`
- consumed inside `ContactSalesForm`

Important finding:
- unknown inquiry keys leave the `<select>` value empty (`''`)
- do NOT expect the placeholder string as the actual value
- repeated valid products should not create duplicate checked expectations; just assert the correct boxes are checked

## Recommended workflow

1. verify repo and branch state
2. create a fresh worktree from `origin/main` if needed
3. inspect current Contact Us implementation and existing `tests/e2e/utm-tracking.spec.ts`
4. extract Contact Us coverage into a dedicated spec, e.g.:
   - `tests/e2e/contact-us.spec.ts`
5. add a stage script in `tests/package.json`, e.g.:
```json
"test:e2e:contact-us:stage": "BASE_URL=https://stage.querypie.com npx playwright test --config=e2e/playwright.config.ts e2e/contact-us.spec.ts"
```
6. add a focused doc, e.g.:
   - `docs/contact-us-e2e.md`
7. add doc references from:
   - `README.md`
   - `tests/README.md`
8. run the dedicated stage E2E from `tests/`
9. commit, push, and open a Draft PR

## Good assertions for the dedicated Contact Us spec

### Shell render
- title is `QueryPie Contacts`
- H1 is `Contact Us`
- lead contains `Connect with our experts. Accelerate your success.`
- lead contains `Reach out today!`
- `Proceed` is disabled initially
- `Terms of Use` link is visible

### Query prefills
For:
- `?inquiry=demo-request&product=aip&product=fde`

Assert:
- inquiry select value becomes `Request for Product Demo`
- AIP checkbox checked
- FDE checkbox checked
- ACP unchecked

### Unknown prefills
For:
- `?inquiry=unknown&product=unknown&product=acp&product=acp&product=partnership`

Assert:
- inquiry select value is `''`
- ACP checked
- Partnership checked
- AIP unchecked
- checked checkbox count reflects the valid unique selections you intend to verify

### Required-field gating
With inquiry/product prefilled, fill required text fields only first:
- first name
- last name
- business email
- company name
- department/title
- textarea

Assert:
- `Proceed` still disabled
- after selecting planned implementation date, `Proceed` becomes enabled

### Submit flow
Fill a valid form and assert current hosted success state:
- success heading `Submission Complete`
- success copy `Our team will review it and get back to you shortly.`

## Practical pitfalls

- Do not treat `stage.querypie.com` as `corp-web-v2`; it is `corp-web-app`
- Do not reuse `corp-web-japan` Japanese assertions here
- Do not assume the old Contact Us submit verification inside `tests/e2e/utm-tracking.spec.ts` is sufficient documentation or structure for new Contact Us work
- When checking unknown inquiry prefills, expect `''`, not the placeholder label
- `tests/` has its own `package.json`; install and run Playwright there:
```bash
cd tests
npm install
npm run install:browsers
npm run test:e2e:contact-us:stage
```

## Done criteria
- branch/worktree is based on latest `origin/main`
- dedicated Contact Us spec exists under `tests/e2e/`
- stage execution script exists in `tests/package.json`
- docs are added and referenced
- `cd tests && npm run test:e2e:contact-us:stage` passes against `https://stage.querypie.com`
