---
name: corp-web-japan-contact-us-preview-form
description: Implement a local /t/contact-us preview form in corp-web-japan while keeping the public /contact-us redirect unchanged until rollout.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, contact-us, preview, nextjs, salesforce, query-prefill]
---

# corp-web-japan contact-us preview form

Use this when the user wants local contact-us form functionality implemented in `corp-web-japan`, but does **not** want to open it on the public `/contact-us` route yet.

## Goal

Implement the form on an isolated preview path such as:
- `/t/contact-us`

while keeping:
- existing `/contact-us` redirect behavior unchanged
- stable CTA query-string prefills working (`inquiry`, repeated `product`)
- rollout safety for environments that do not yet have upstream submission secrets configured

## Proven approach

### 1. Keep `/contact-us` redirect-only

Do not modify:
- `src/app/contact-us/route.ts`

This route should continue to 307 redirect to the Japan contact page and preserve the query string.

Reason:
- the user explicitly wanted the current redirect behavior preserved until the new implementation is sufficiently tested

### 2. Add a separate preview page under `/t/contact-us`

Create:
- `src/app/t/contact-us/page.tsx`

Recommended page behavior:
- render a local form UI
- set `robots.index = false` and `robots.follow = false`
- use canonical `/t/contact-us`
- keep the existing site header/footer for realistic validation

### 3. Put form option definitions and query-prefill helpers in a shared lib

Create a repo-local helper like:
- `src/lib/contact-us.ts`

Include:
- form state type
- inquiry options using stable keys
- product options using stable keys
- `getPrefilledContactUsFormState(searchParams)`
- submit body builder for the Salesforce-style upstream request
- client/server shared validation helper

Recommended stable inquiry keys:
- `ai-consulting`
- `download`
- `demo-request`
- `quote-request`
- `technical-question`
- `partnership`
- `other`

Recommended stable product keys:
- `ai-crew`
- `ai-dashi`
- `aip`
- `acp`
- `fde`
- `partnership`

Important:
- store keys in the URL/query layer
- convert keys to Japanese labels only when building the upstream request body

### 4. In Next.js App Router, do prefill resolution on the server page, not with `useSearchParams()` in the client form

Initial attempt using `useSearchParams()` inside the client form caused build issues:
- `useSearchParams() should be wrapped in a suspense boundary at page "/t/contact-us"`

A follow-up effect-based sync also triggered lint failure:
- `react-hooks/set-state-in-effect`

Working fix:
- let `page.tsx` accept `searchParams`
- convert them into `URLSearchParams`
- call `getPrefilledContactUsFormState(urlSearchParams)` on the server
- pass the result to the client form as `initialPrefills`

Pattern:

```tsx
type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ContactUsPreviewPage({ searchParams }: PageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const urlSearchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(resolvedSearchParams)) {
    if (Array.isArray(value)) value.forEach(item => urlSearchParams.append(key, item));
    else if (typeof value === 'string') urlSearchParams.set(key, value);
  }

  const initialPrefills = getPrefilledContactUsFormState(urlSearchParams);

  return <ContactUsPreviewForm initialPrefills={initialPrefills} />;
}
```

This avoids both:
- suspense bailout build failure
- setState-in-effect lint failure

### 5. Keep the preview form client-side, but submit through the production-ready endpoint

In the current approved rollout shape:
- the preview/public test page stays at `/t/contact-us`
- the submit endpoint should be `/contact-us/submit`

The page and submit endpoint are intentionally split.
Do **not** keep a separate `/t/contact-us/submit` endpoint once the production-ready submit path is in place.

Recommended behavior for the client form component (currently `src/components/sections/contact-us-form.tsx`):
- initialize form state from `initialPrefills`
- keep Japanese labels consistent with the upstream JP contact form
- disable submit until required fields are valid
- POST to `/contact-us/submit`
- include `referrerUrl`
- forward UTM attribution when present, preferring the current URL query and otherwise falling back to the `utm-attribution` cookie

### 6. Implement a thin `/contact-us/submit` route plus reusable shared server-side form modules

### 6.5. Add structured external API outcome logging in the shared form-server layer

Once Slack / Salesforce integrations are shared under `src/lib/forms/server/`, keep their operational logging shared too.

Recommended pattern:
- add a small shared helper such as:
  - `src/lib/forms/server/external-api-log.ts`
- log structured JSON-like entries through the correct console level:
  - success -> `console.info`
  - skipped -> `console.warn`
  - failed -> `console.error`

Recommended fields:
- `service`: `slack` | `salesforce` | `license`
- `endpointName`: for example `contact-us` or `gating-form`
- `requestPath`: for example `/contact-us/submit` or `/api/gating-form/unlock`
- `outcome`: `success` | `skipped` | `failed`
- `reason`: such as `missing_credentials`, `missing_endpoint`, `http_500`, `request_error`
- `remoteUrl`
- `statusCode`
- `recordUUID` when available

Important implementation lesson:
- do not leave outcome logs as ad-hoc string prefixes like `[contact-us] salesforce: ...`
- prefer one shared structured format so Vercel Runtime Logs can be filtered consistently across endpoint families

Caller-side rule:
- pass `endpointName` and `requestPath` explicitly from each submit caller into the shared Slack / Salesforce helpers
- practical examples:
  - contact-us -> `endpointName: "contact-us"`, `requestPath: "/contact-us/submit"`
  - gating-form -> `endpointName: "gating-form"`, `requestPath: "/api/gating-form/unlock"`

### 6.6. Preserve and surface the request URI explicitly in both Salesforce and Slack

The current form flows already have the submission page URL available via `referrerUrl` / `Referrer_URL__c`.
To make debugging and manual triage easier, keep that value in the payload and also expose it in human-readable surfaces.

Recommended behavior:
- Salesforce:
  - keep `Referrer_URL__c`
  - also prepend a readable line to `Description`, for example:
    - `Request URI: https://stage.querypie.ai/contact-us?...`
- Slack:
  - do not hide `Referrer_URL__c` completely from the visible message
  - instead render it under a friendlier label such as:
    - `• *Request URI*: https://stage.querypie.ai/contact-us?...`

Important experiential finding:
- keeping the raw Salesforce field alone is not enough for fast operational debugging
- support/marketing reviewers benefit from seeing the originating website URL directly in the Slack message body and in the readable Salesforce description

Use a thin route:
- `src/app/contact-us/submit/route.ts`

and keep the contact-us-specific orchestration in:
- `src/lib/contact-us-submit.ts`

Then split the reusable cross-form primitives into shared server modules under:
- `src/lib/forms/server/sanitize.ts`
- `src/lib/forms/server/email-deliverability.ts`
- `src/lib/forms/server/utm-attribution.ts`
- `src/lib/forms/server/slack-notification.ts`
- `src/lib/forms/server/salesforce-delivery.ts`

Reason:
- the user explicitly said `contact-us` is only one external-contact surface
- the same backend pieces should be reusable for gating forms, quote/estimate-request forms, and similar future entrypoints
- route files should stay thin, while integration behavior is composed from shared server primitives

Recommended responsibility split:
- `src/app/contact-us/submit/route.ts`
  - parse JSON
  - call the contact-us orchestrator
  - translate result into JSON response
- `src/lib/contact-us-submit.ts`
  - contact-us-specific validation/result orchestration
  - compose the shared modules below
- `sanitize.ts`
  - sanitize outbound text fields
  - sanitize string-valued records before transport
- `email-deliverability.ts`
  - perform MX-based email validation
- `utm-attribution.ts`
  - convert encoded attribution into Salesforce `pi__*` fields
- `slack-notification.ts`
  - shared Slack posting helper
  - environment-tag behavior such as `[TEST]` should use `is-production.ts`
- `salesforce-delivery.ts`
  - best-effort Salesforce POST helper with configurable success-id field and log prefix

Important experiential finding:
- a thin route + contact-specific orchestrator + shared server modules was the right long-term compromise
- it preserved the user’s route/code-structure preference
- it also created a reusable foundation for other external-contact forms instead of leaving all logic trapped in `contact-us-submit.ts`

### 7. Match the `corp-web-v2` operational model selectively, without copying the whole stack

The minimal reusable production-ready parity set that proved useful was:
- Slack notification path
- Salesforce best-effort delivery
- MX validation
- outbound sanitization
- UTM forwarding

Do not over-copy unrelated `corp-web-v2` infrastructure.
In this repo, a focused local helper is easier to review and better aligned with the user’s scope preferences.

### 8. Update repo-local regression tests to lock the split route structure and reusable module boundaries

The lightweight route coverage tests should assert the current approved structure:
- `/t/contact-us` page is `noindex`
- canonical is `/t/contact-us`
- stable query keys exist in the helper
- the form submits to `/contact-us/submit`
- `src/app/contact-us/submit/route.ts` exists
- the old `src/app/t/contact-us/submit/route.ts` no longer exists
- `src/lib/contact-us-submit.ts` exists as the contact-specific orchestrator
- shared form-server modules exist under `src/lib/forms/server/`
- the orchestrator composes those shared modules
- `processType: "LEAD_MS"` still exists in the request builder

Important structure lesson learned:
- keep test paths aligned with the source paths they verify
- do **not** leave new contact-us tests as top-level generic files like `tests/t-contact-us-route.test.mjs` once the source structure is clear
- mirror the source tree under `tests/src/...`, not under a flatter `tests/app/...` shortcut
- preferred examples for this feature:
  - `src/app/t/contact-us/page.tsx` -> `tests/src/app/t/contact-us/page.test.mjs`
  - `src/app/contact-us/submit/route.ts` -> `tests/src/app/contact-us/submit/route.test.mjs`
  - `src/lib/contact-us-submit.ts` -> `tests/src/lib/contact-us-submit.test.mjs`

### 9. Add direct tests for the reusable server modules under `src/lib/forms/server/`

Once the shared server modules exist, do not rely only on string-based route coverage.
Prefer file-by-file tests whose paths and basenames mirror the source files exactly:
- `src/lib/forms/server/sanitize.ts` -> `tests/src/lib/forms/server/sanitize.test.mjs`
- `src/lib/forms/server/email-deliverability.ts` -> `tests/src/lib/forms/server/email-deliverability.test.mjs`
- `src/lib/forms/server/utm-attribution.ts` -> `tests/src/lib/forms/server/utm-attribution.test.mjs`
- `src/lib/forms/server/slack-notification.ts` -> `tests/src/lib/forms/server/slack-notification.test.mjs`
- `src/lib/forms/server/salesforce-delivery.ts` -> `tests/src/lib/forms/server/salesforce-delivery.test.mjs`

What to cover directly:
- `sanitize.ts`
  - strips HTML/control chars
  - preserves non-string values in record sanitization
- `utm-attribution.ts`
  - valid encoded attribution -> correct Salesforce `pi__*` fields
  - malformed attribution -> empty object
- `slack-notification.ts`
  - non-production environment tag behavior
  - outbound payload shape
  - filtering of hidden/internal keys from the human-facing message
- `salesforce-delivery.ts`
  - missing endpoint path
  - success with `recordUUID`
  - missing success id / request error paths
- `email-deliverability.ts`
  - MX record present vs absent

Practical test-runner finding:
- the repo’s old `npm test` script only matched top-level `tests/*.test.mjs`
- once tests are reorganized to mirror source paths, update the script to recurse, for example:
  ```bash
  find tests -name '*.test.mjs' -print | sort | xargs node --test
  ```
- without this, source-aligned nested test files are silently skipped

Practical implementation finding:
- this repo’s default tests are Node-based `.mjs` files, and the shared modules are TypeScript files not directly runnable by Node in that setup
- a small test-local TypeScript loader harness worked well:
  - read the `.ts` source
  - transpile with `typescript.transpileModule(..., module=CommonJS)`
  - execute with `vm.runInNewContext(...)`
  - support `@/` imports and targeted mocks (for example `node:dns/promises`)
- when comparing objects returned from that VM context, normalize through JSON first (for example `JSON.parse(JSON.stringify(value))`) before `deepEqual`, or prototype/context differences can cause false negatives
- if the tested module reads `fetch`, bind the harness context as `fetch: (...args) => global.fetch(...args)` rather than capturing `global.fetch` once; this lets the test replace `global.fetch` later and have the module observe the mock correctly
- avoid naming a local variable literally `module` in the `.mjs` test harness, because the repo’s ESLint config flags that; use a different name such as `cjsModule`

## Verification steps that worked

Run from the worktree:

```bash
npm run test:ci
npm run build
```

Do not start local preview by default for this user.

Important user/environment finding:
- local dev servers consume too many resources in this environment and interfere with work
- prefer PR + Preview Deployment validation over local `npm run dev`
- only start a local dev server if the user explicitly instructs it

If the user explicitly asks for local verification, then use:

```bash
npm run dev
```

Useful browser checks when local verification is explicitly requested:
- `http://localhost:3003/t/contact-us`
- `http://localhost:3003/t/contact-us?inquiry=demo-request&product=ai-dashi&product=aip`

Expected browser result for the second URL:
- inquiry select prefilled to `デモを依頼`
- product checkboxes for `AI Dashi` and `AIP` checked

## Pitfalls found

1. `useSearchParams()` in the preview page path triggered a build-time suspense requirement.
   - Do not keep prefill resolution purely in the client unless you intentionally wrap the page with suspense.
   - Server-side `searchParams` handling was cleaner here.

2. Syncing prefills with `setState()` in `useEffect()` triggered `react-hooks/set-state-in-effect` lint errors.
   - Prefer server-derived initial state props instead.

3. This repo may not have `node_modules` installed yet.
   - `npm run test:ci` and `npm run build` can fail with `command not found` for `eslint`/`next` until dependencies are installed.
   - Installing once at the repo root may be enough for worktree verification.

4. `npm run test:ci` can still print unrelated existing warnings.
   - Example observed: an existing `@next/next/no-img-element` warning in `src/components/sections/zoomable-figure.tsx`.
   - If there are no errors, this does not block the feature work.

5. Browser verification is useful here because checkbox/select prefill correctness is easiest to confirm visually.

### 10. Final rollout: switch the public route from `/t/contact-us` to `/contact-us`

### 10.1 Route removal nuance discovered after rollout follow-up

If the user does **not** want temporary compatibility for the old preview path, you do not need to keep `/t/contact-us` as a redirect route.

In that case the cleaner final state is:
- `/contact-us` serves the real local form page
- `src/app/t/contact-us/page.tsx` is gone
- `src/app/t/contact-us/route.ts` is also gone
- tests should assert that `/t/contact-us` route files no longer exist

Practical lesson:
- do not preserve a legacy preview-path redirect by habit
- if the site is not publicly launched yet, the simpler end state is often full removal rather than compatibility redirect retention

Use this when the user explicitly says the preview phase is over and asks to connect the real public route.

### Target end state

- `/contact-us` becomes the real local contact form page
- the submit endpoint stays `/contact-us/submit`
- `/t/contact-us` is **not** required after rollout unless the user explicitly wants a temporary compatibility path

Important user-preference finding:
- do not assume `/t/contact-us` should remain as a redirect after rollout
- if the user does not explicitly ask to preserve it, removing `/t/contact-us` entirely is acceptable and may be preferred

### Minimal safe rollout approach

1. Move the page implementation:
- from `src/app/t/contact-us/page.tsx`
- to `src/app/contact-us/page.tsx`

2. Remove the old public redirect implementation:
- delete `src/app/contact-us/route.ts`

3. Decide `/t/contact-us` handling based on explicit user scope:
- if compatibility is explicitly desired, replace it with a local redirect route to `/contact-us`
- otherwise, remove it entirely and do not leave a redirect-only `src/app/t/contact-us/route.ts`

4. Update page metadata for the public route:
- canonical should become `/contact-us`
- remove the preview-only `robots: { index: false, follow: false }` block unless the user explicitly wants the public form to remain non-indexed

5. Update `src/app/sitemap.ts`:
- add `/contact-us` as a real public route
- do not add `/t/contact-us` to the sitemap

### Test and repo-maintenance findings from rollout

1. Source-mirrored tests should move with the route move.
- move `tests/src/app/t/contact-us/page.test.mjs`
- to `tests/src/app/contact-us/page.test.mjs`
- if `/t/contact-us` is kept as a redirect, add a redirect test for `tests/src/app/t/contact-us/route.test.mjs`
- if `/t/contact-us` is fully removed, delete that redirect test and replace it with an assertion that the route file does not exist

2. Stage E2E path should move too.
- move `tests-local/src/app/t/contact-us/page.e2e.mjs`
- to `tests-local/src/app/contact-us/page.e2e.mjs`
- update the visited URL from `/t/contact-us` to `/contact-us`

3. The repo test script may silently skip nested source-mirrored tests.
- if `package.json` still uses `node --test tests/*.test.mjs`, nested tests under `tests/src/**` will not run
- safer recursive script:

```bash
find tests -name '*.test.mjs' -print | sort | xargs node --test
```

This mattered during rollout because the moved contact-us tests would otherwise appear present but never execute.

4. When moving mirrored tests deeper in the tree, fix relative helper imports carefully.
- `tests/src/app/contact-us/page.test.mjs` should import helpers from `../../../helpers/source-readers.mjs`
- if a redirect test still exists under `tests/src/app/t/contact-us/route.test.mjs`, it should import helpers from `../../../../helpers/source-readers.mjs`

This was an actual failure encountered during rollout: the recursive test runner correctly picked up the new nested tests, then helper import paths were initially one level off.

5. Update README / representative-file references if they still describe `/contact-us` as a redirect endpoint.

6. If `/t/contact-us` is removed entirely, also remove it from:
- redirect endpoint inventory tests
- route-coverage tests
- any launch-readiness assertions that still expect `src/app/t/contact-us/route.ts`

### 11. Shared external API outcome logging for contact-us and gating-form

When the user wants operational visibility for external calls, keep the logging logic in the shared helpers under:
- `src/lib/forms/server/`

A reusable pattern that worked here:
- add a tiny shared helper such as `src/lib/forms/server/external-api-log.ts`
- emit structured JSON through normal console methods so Vercel Runtime Logs keep the severity
- use:
  - `console.info(...)` for success
  - `console.warn(...)` for skipped calls
  - `console.error(...)` for failed calls

Recommended structured fields:
- `service`: `slack` | `salesforce` | future values such as `license`
- `endpointName`: logical caller name such as `contact-us` or `gating-form`
- `requestPath`: route path such as `/contact-us/submit` or `/api/gating-form/unlock`
- `outcome`: `success` | `skipped` | `failed`
- optional detail fields like `reason`, `recordUUID`, `remoteUrl`, `statusCode`

Important implementation finding:
- caller code should pass `endpointName` and `requestPath` into the shared helpers instead of hardcoding only a generic log prefix
- this made Vercel Runtime Logs much easier to inspect after staging submissions

Recommended caller wiring that proved useful:
- contact-us caller:
  - `endpointName: "contact-us"`
  - `requestPath: "/contact-us/submit"`
- gating-form caller:
  - `endpointName: "gating-form"`
  - `requestPath: "/api/gating-form/unlock"`

Behavioral finding:
- returning a result object from the Slack helper (`{ ok: true } | { ok: false, reason }`) was cleaner than throwing for every non-success path once skip/success/fail logging had to be explicit
- callers can then map `missing_credentials` to a `500` and other Slack failures to a `502` without duplicating log formatting

### 12. Request URI exposure: keep Salesforce fielding, add human-visible labels carefully

The repo already had two distinct URL-related concepts:
- `Referrer_URL__c`: current submit/request URL for the form submission
- UTM attribution fields such as `pi__first_touch_url__c`: marketing attribution / first-touch landing info

Important lesson:
- these are not the same thing and should not be conflated
- `Referrer_URL__c` should continue to be preserved exactly as the explicit current request URL field
- UTM/attribution fields should remain intact for marketing analysis

What worked well here:
- keep `Referrer_URL__c` in the Salesforce request body as before
- also include a human-readable line in Salesforce `Description`:
  - `RequestURI: <url>`
- in Slack, do not expose the raw key name `Referrer_URL__c`
- instead render a human-facing visible entry:
  - `RequestURI: <url>`

Practical wording preference learned from the user:
- prefer the exact compact label `RequestURI`
- do not use `Request URI` with a space once the user has clarified the preferred label

Test coverage that proved valuable:
- Slack visible message contains `RequestURI`
- Salesforce body still preserves `Referrer_URL__c`
- Salesforce `Description` also contains `RequestURI: ...`

### Rollout verification used successfully

Run from the worktree:

```bash
npm run test
```

For this user, this was the preferred local verification because it is fast and avoids unnecessary long local build waits.
If broader deployment-sensitive verification is explicitly desired later, CI can cover the heavier checks.

### Post-merge E2E recheck on latest main

When the user later asks to rerun the contact-us E2E after the rollout PR has already merged:

1. Inspect the latest `origin/main` test file before assuming another route update is needed.
   - In this rollout, the merged file already targeted `/contact-us`:
     - `tests-local/src/app/contact-us/page.e2e.mjs`
   - Do not create a follow-up PR just because earlier history once used `/t/contact-us`.
   - First confirm whether latest main already reflects the final `/contact-us` path.

2. If the task is only "rerun the E2E and verify", and latest main already has the correct `/contact-us` path, there may be **no code change to make**.
   - In that case, execute the E2E, report the result, and do not open a PR.

3. Fresh worktrees may not have Playwright installed even if `package.json` declares it.
   - If `npm run e2e:local:contact-us:stage` fails with:
     - `Cannot find package '@playwright/test'`
   - a practical low-impact workaround is:

```bash
npm install --no-save @playwright/test
npm run e2e:local:contact-us:stage
```

   - This allows executing the E2E without intentionally changing tracked dependency manifests.

4. After the merged rollout reached latest main and stage caught up, the stage E2E passed against:
   - `https://stage.querypie.ai/contact-us`

   with the existing 3 checks:
   - page renders core form fields
   - stable query prefills work
   - submit flow succeeds

5. If the rerun succeeds and `git diff` is empty, explicitly conclude:
   - no code change needed
   - no PR should be created

This avoids unnecessary no-op PRs after a merged rollout.

## Two-column top-alignment pitfall

For the `/contact-us` page layout, if the right-side form panel appears visually lower than the left-side title/intro column, first verify the actual rendered y-positions in the browser before changing spacing values. In one stage check, the measured `h1` top and form-panel top were already equal, but relying on default grid stretching still left the layout vulnerable to future content/size changes.

Preferred hardening for this user:
- on the two-column grid container, set `items-start`
- on the right-side form panel wrapper, set `self-start`
- prefer this explicit alignment fix before tweaking arbitrary top margin/padding values

Why:
- it expresses the actual layout contract directly: both columns start at the same top edge
- it avoids accidental regressions when either the intro copy or the form contents change height
- it is a smaller, more stable fix than compensating with ad hoc spacing offsets

Practical example:
- `src/components/sections/contact-us-page-section.tsx`
  - grid wrapper -> `items-start`
  - `ContactUsFormPanel` -> `self-start`

### Post-PR-461 company-page primitive nuance

After the company-page header/layout refactor, `/contact-us` may be built on shared primitives such as:
- `CompanyPageSection`
- `CompanyPageLayout preset="equalColumns"`
- a contact-us-only `ContactUsFormPanel`

In that shape, split spacing responsibilities carefully:
- horizontal/two-column alignment belongs to `CompanyPageLayout`
- contact-us-only right-column visual nudges belong to `ContactUsFormPanel`
- footer gap belongs to the outer `CompanyPageSection` bottom padding, not to the form panel

What worked well in a later follow-up:
- if the user explicitly wants the right form column to sit slightly lower on desktop for visual balance, a contact-us-only class like `lg:mt-[10px]` on `ContactUsFormPanel` is acceptable
- do not push that kind of offset down into the shared `CompanyPageLayout`, because that primitive is also used by other company pages such as about-us, certifications, and news

Important footer-gap lesson:
- if the user asks for the distance from the last visible content block to the start of the footer to be a specific value (for example 78px), the correct control point is the outer section padding in the shared company-page primitive, not `mb-*` on the last card/component
- after the PR 461 company-page primitive shape, treat changes to `CompanyPageSection`, `CompanyPageIntro`, and `CompanyPageTitle` spacing as shared company-page behavior by default, not as contact-us-only exceptions
- only keep truly contact-us-specific right-column visual nudges in `ContactUsFormPanel` (for example a desktop-only `lg:mt-[10px]` offset when the user explicitly wants the form column slightly lower)
- do not add a contact-us-only `CompanyPageSection` preset like `compactFooter` unless the user explicitly asks for a page-specific permanent exception that should not affect sibling company pages
- in the verified follow-up, the better end state was:
  - shared `CompanyPageSection` default desktop bottom padding updated to the desired common value
  - shared `CompanyPageIntro` owning the common intro spacing tweak
  - only `ContactUsFormPanel` keeping the contact-us-only desktop offset
- avoid faking footer distance with inner card padding or card bottom margin; that mixes component-internal spacing with page-level vertical rhythm and makes future layout reuse harder

## Done criteria

Preview-phase done criteria:
- `/contact-us` redirect remains unchanged until final rollout
- `/t/contact-us` renders the working preview form
- stable `inquiry` and repeated `product` query prefills work
- the form submits to `/contact-us/submit`
- `src/app/contact-us/submit/route.ts` stays thin and delegates to shared submit logic
- the shared submit logic covers Slack, Salesforce best-effort, MX validation, sanitization, and UTM forwarding

Final-rollout done criteria:
- `/contact-us` serves the real local form page
- `/contact-us/submit` remains unchanged
- `/contact-us` canonical metadata points to `/contact-us`
- `/contact-us` is included in `src/app/sitemap.ts`
- moved/mirrored tests and local E2E paths are updated to the public route
- if the user did not request compatibility, `/t/contact-us` route artifacts are removed entirely
- `npm run test` passes with the recursive nested test discovery in place
- staged/CI verification confirms the public route works
