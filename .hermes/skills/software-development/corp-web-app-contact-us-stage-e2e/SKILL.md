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

For stage-hosted E2E tasks that are not specifically Contact Us form behavior, load the broader `corp-web-app-stage-e2e` skill instead or alongside this one.

## Current status warning

As of PR #624 follow-up (`docs: 무효 문서와 E2E 검증 범위 정리`), the repo keeps the verified `@playwright/test` E2E specs under `tests/e2e/` instead of deleting the runner. Before removing any E2E spec, run it individually against the intended target and classify failures per test case.

Current verified shape:
- `tests/e2e/contact-us.spec.ts` is maintained for shell rendering, query prefill, unknown-prefill handling, required-field gating, and a real hosted submission completion check.
- `tests/e2e/utm-tracking.spec.ts` is maintained for UTM cookie first/recent behavior plus Contact Us page/form usability with the UTM cookie present.
- `tests/e2e/issue-551-demo-menu.spec.ts` is maintained for legacy `/features/demo` category navigation regression while that route still works.
- Do not delete E2E coverage just because a hosted submission assertion is flaky. First verify the live stage site directly and split responsibilities if needed: Contact Us owns real submit completion; UTM owns attribution persistence and form readiness.

## Why this skill exists

A common failure mode is to mix up:
- `corp-web-app`
- `corp-web-v2`
- `corp-web-japan`

These repos have different stage domains, different page shells, and different existing E2E patterns.

For `corp-web-app` specifically:
- stage domain is `https://stage.querypie.com`
- Contact Us currently renders the public shell with:
  - H1 `Contact Us`
  - lead copy including `We're here to help with product consultations, resource requests, and technical inquiries.`
  - bullet copy including `Talk with the right team for your product and rollout stage.`
  - submit button label `Proceed`
  - helper link text `Terms of Use`
- the repo already has a Playwright runner under `tests/`
- Contact Us belongs in a dedicated `tests/e2e/contact-us.spec.ts`; UTM behavior belongs in `tests/e2e/utm-tracking.spec.ts`
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
- browser title: `QueryPie Contacts`
- H1: `Contact Us`
- lead text containing:
  - `We're here to help with product consultations, resource requests, and technical inquiries.`
  - `Fill out the form on the right, and our team will review your inquiry and contact you within one business week.`
- bullet text containing:
  - `Talk with the right team for your product and rollout stage.`
  - `Receive introduction materials and implementation consultation tailored to your inquiry.`
  - `Receive follow-up by email after our team reviews your inquiry.`
- submit button: `Proceed`
- helper link text: `Terms of Use`

If your assertions expect `Submit`, `Terms`, or the old `corp-web-v2` shell, you are in the wrong repo or using the wrong reference. If they expect `Reach out today!`, re-check live stage because that was an older shell.

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
- lead contains `We're here to help with product consultations, resource requests, and technical inquiries.`
- bullet contains `Talk with the right team for your product and rollout stage.`
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
Fill a valid Contact Us form and assert current hosted success state:
- use an overrideable email/message (`CONTACT_US_E2E_EMAIL`, `CONTACT_US_E2E_MESSAGE`) so future runs can avoid hard-coded addresses if needed
- fill optional phone (`010-1234-5678` worked on stage)
- choose inquiry `Request for Product Demo`
- check `AI Platform QueryPie AIP`
- choose planned date `Within 3 months`
- optionally check the marketing/news checkbox
- after clicking `Proceed`, wait up to about 45s for the hosted server action to complete
- success heading `Submission Complete`
- success copy `Our team will review it and get back to you shortly.`
- success link `Go to Home`

### UTM + Contact Us split
Do not duplicate the real hosted submission assertion inside `tests/e2e/utm-tracking.spec.ts` unless the user explicitly asks and live stage has been re-verified.
During PR #624 follow-up, direct Contact Us submission passed, but the UTM spec variant that first landed with `utm-attribution` and then submitted Contact Us did not reach the completion screen within 45s. The useful stable split was:
- `contact-us.spec.ts`: owns real hosted submit completion
- `utm-tracking.spec.ts`: owns UTM cookie creation, first/recent attribution, cookie persistence after navigating to `/company/contact-us`, and form gating/enabled-state with UTM present

This still verifies that E2E coverage performs real checks against `https://stage.querypie.com/` without making the UTM spec a duplicate hosted-submission flake.

## Practical pitfalls

- Do not treat `stage.querypie.com` as `corp-web-v2`; it is `corp-web-app`
- Do not reuse `corp-web-japan` Japanese assertions here
- Do not assume the old Contact Us submit verification inside `tests/e2e/utm-tracking.spec.ts` is sufficient documentation or structure for new Contact Us work
- Do not delete hosted-submit E2E coverage solely because an old combined UTM+submit case fails; first run a direct Contact Us submission against stage and split coverage by responsibility if direct submit works
- When checking unknown inquiry prefills, expect `''`, not the placeholder label
- For GitHub Actions failures on self-hosted Linux runners, distinguish browser-binary install from browser OS dependency install. If logs show `Host system is missing dependencies to run browsers` and name packages like `libnspr4`, `libnss3`, or `libasound2`, update the workflow to use a CI script such as `npx playwright install --with-deps chromium` instead of only `npx playwright install chromium`. Keep the local lightweight script if useful, but make workflow jobs use the `--with-deps` variant.
- `workflow_dispatch` E2E runs may not attach as PR checks automatically. After pushing a workflow fix, manually dispatch the workflow on the PR branch and report the run URL plus the key step result. If the original dependency-install step passes but the hosted E2E body keeps running, do not wait passively for the full timeout; schedule or perform a later status check and label any later failure as a downstream E2E issue, not the original missing-OS-dependency issue.
- If the Contact Us spec later fails with selector timeouts but the artifact `error-context.md` or screenshot shows `Vercel Security Checkpoint`, `Failed to verify your browser`, `Code 21`, or HTTP 403, classify it as stage edge/WAF/bot-protection blocking the E2E browser, not a Contact Us form regression. Re-run the same spec from the local workstation to separate E2E validity from hosted runner blocking; local pass plus CI checkpoint means the fix belongs in Vercel/WAF allowlisting or bypass, while the test should fail fast with a clear checkpoint diagnostic.
- For Vercel browser verification blocks, the official stable fix is Vercel Protection Bypass for Automation: create a project bypass secret in Vercel, add it to GitHub Actions as `VERCEL_AUTOMATION_BYPASS_SECRET`, and configure Playwright `extraHTTPHeaders` with `x-vercel-protection-bypass: process.env.VERCEL_AUTOMATION_BYPASS_SECRET` plus `x-vercel-set-bypass-cookie: true`. Vercel docs state this bypasses Bot Protection challenges, but not active DDoS/security mitigations. See `references/vercel-protection-bypass-for-automation.md` for API and workflow details.
- Do not conclude that Vercel CLI is unavailable just because the Hermes non-interactive terminal environment lacks `VERCEL_TOKEN`. In this user's setup the token may be loaded only by interactive zsh; verify with `zsh -ic 'printf "%s %s\n" "${VERCEL_TOKEN:+set}" "${#VERCEL_TOKEN}"'` and run Vercel commands as `zsh -ic 'vercel ... --token "$VERCEL_TOKEN"'` when needed.
- Empirical corp-web-app finding: switching from Playwright Chromium to Firefox on Linux ARM allowed several initial stage Contact Us checks to pass, but repeated isolated contexts/navigations eventually triggered `Vercel Security Checkpoint`; Chrome stable is not available on Linux ARM64 (`ERROR: not supported on Linux Arm64`). Treat browser-engine changes as mitigation, not the durable solution.
- See `references/stage-e2e-playwright-system-deps.md` for the saved CI failure signature and remediation pattern.
- `tests/` has its own `package.json`; install and run Playwright there:
```bash
cd tests
npm install
npm run install:browsers
npm run test:e2e:contact-us:stage
```

## References

- `references/pr-624-e2e-revival.md`: session note for reviving real Contact Us submission coverage while splitting UTM attribution coverage.

## Done criteria
- branch/worktree is based on latest `origin/main`
- dedicated Contact Us spec exists under `tests/e2e/`
- stage execution script exists in `tests/package.json` when adding a new dedicated command
- docs are added and referenced
- `BASE_URL=https://stage.querypie.com npx playwright test --config=e2e/playwright.config.ts e2e/contact-us.spec.ts --reporter=line` passes from `tests/`
- when touching the overall runner, `BASE_URL=https://stage.querypie.com npx playwright test --config=e2e/playwright.config.ts --reporter=line` passes from `tests/`
- PR body does not contain stale claims such as “real submit removed” if current coverage now verifies `Submission Complete`
