---
name: corp-web-app-contact-us-static-route-authoring
description: Refactor corp-web-app contact-us routes into static app routes with route-local authoring, locale-specific pages, and safe unprefixed route handling via either a root EN wrapper or route-level redirect.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, contact-us, static-route, route-local-authoring, locale]
---

# corp-web-app contact-us static route authoring

Use this when the user wants `/company/contact-us` moved away from catch-all handling and implemented like `/plans`, with authored page structure visible in route `page.tsx` files.

## Goal

Implement contact-us as explicit static app routes:
- `/company/contact-us`
- `/en/company/contact-us`
- `/ko/company/contact-us`
- `/ja/company/contact-us`

with these principles:
- route-local page authoring in locale `page.tsx` files
- unprefixed `/company/contact-us` handled explicitly, either by a root English wrapper or by a route-level redirect when the wrapper is intentionally removed
- form behavior separated from page composition
- no local dev server unless the user explicitly asks
- verify with targeted tests, lint, CI, and Preview Deployment when route behavior changes

## Proven structure

### 1. Match the `/plans` pattern for English

Reference pattern:
- `src/app/plans/page.tsx` wraps `src/app/en/plans/page.tsx`

For contact-us, use:
- `src/app/en/company/contact-us/page.tsx` → real English authored page
- `src/app/company/contact-us/page.tsx` → thin wrapper importing EN page

Recommended wrapper shape:

```ts
import ContactUsPageEn, { generateMetadata as generateMetadataEn } from 'src/app/en/company/contact-us/page'
import { Metadata } from 'next'

export async function generateMetadata(): Promise<Metadata> {
  return await generateMetadataEn()
}

export default function ContactUsPageDefault() {
  return <ContactUsPageEn />
}
```

Important finding:
- Do not force a custom `urlPath?: string` signature on app-route `generateMetadata()` unless the route actually uses that abstraction consistently.
- Next build type-checking rejected the ad-hoc EN contact-us `generateMetadata(urlPath?: string)` shape.
- For this route, plain `generateMetadata(): Promise<Metadata>` was safer.

### 2. Keep locale-specific authored pages explicit

Create:
- `src/app/en/company/contact-us/page.tsx`
- `src/app/ko/company/contact-us/page.tsx`
- `src/app/ja/company/contact-us/page.tsx`

Each locale page should:
- author its own intro copy / checklist / contact emails directly in route JSX
- render the shared contact-us form component with locale

Pattern:

```tsx
<ContactUsFormPanel>
  <ContactSalesForm locale={Locale.JA} />
</ContactUsFormPanel>
```

### 3. Extract route-local section primitives

Create route-local section helpers near the route, for example:
- `src/app/company/contact-us/contact-us-page-section.component.tsx`
- `src/app/company/contact-us/contact-us-page-section.module.css`

Keep these small and page-specific:
- `ContactUsSection`
- `ContactUsIntro`
- `ContactUsLead`
- `ContactUsChecklist`
- `ContactUsChecklistItem`
- `ContactUsContacts`
- `ContactUsContactItem`
- `ContactUsFormPanel`

This mirrors the successful corp-web-japan PR style where the route reads like authored page structure instead of hiding composition inside a large widget.

### 4. Separate form behavior from page composition

Successful split:
- route `page.tsx` owns intro / contacts / panel layout
- `ContactSalesForm` owns form behavior and submit flow
- `contact-us-form-ui.component.tsx` owns the contact-us-specific UI branch that used to live inside `form-ui.component.tsx`

Useful file split:
- `src/components/widget/contact-sales/contact-sales-form.component.tsx`
- `src/components/widget/form/ui/contact-us-form-ui.component.tsx`
- `src/components/widget/contact-sales/contact-sales.i18n.tsx`

### 5. Extract shared contact-sales i18n cleanly

If `contact-sales.component.tsx` contains long locale-specific form config, move it to:
- `src/components/widget/contact-sales/contact-sales.i18n.tsx`

Export:

```ts
export type ContactSalesI18n = { ... }
export const getContactSalesI18n = (locale: Locale): ContactSalesI18n => contactSalesI18nMessages[locale]
```

Important pitfall found during CI/local verification:
- A partial/manual extraction can accidentally leave old component code (`ContactSales`, `CenterSection`, `FormUI`) inside the new i18n file.
- This caused CI lint/build failures like:
  - `CenterSection is not defined`
  - `FormUI is not defined`
  - duplicate `getContactSalesI18n` declarations
- After extraction, re-open the entire file and verify it contains only:
  - imports for React, Locale, form messages, form types
  - `getHelperText`
  - `contactSalesI18nMessages`
  - `ContactSalesI18n` type
  - `getContactSalesI18n`

### 6. Remove dynamic route overlap

If catch-all static params include contact-us, remove the root contact-us entry from:
- `src/app/[...slug]/page.tsx`

Specifically remove:

```ts
{ slug: ['company', 'contact-us'] }
```

This avoids overlapping responsibility once the explicit static route exists.

Note:
- locale-specific `/ko/company/contact-us` and `/ja/company/contact-us` can be served by their explicit static route files directly.

### 6.5. Deleting the unprefixed root wrapper requires an explicit route-level redirect

A later PR follow-up showed that `src/app/company/contact-us/page.tsx` can be deleted, but not by deletion alone.

Why:
- `src/middleware.ts` only redirects unprefixed requests when the resolved user locale is not EN.
- For EN/default requests, middleware does **not** rewrite `/company/contact-us` to `/en/company/contact-us`.
- If the root wrapper is simply deleted, `/company/contact-us` can fall through to the legacy catch-all and 404.
- The user does **not** want this handled through `next.config.ts`; keep the behavior route-local under `src/app/company/contact-us/`.

Safe deletion pattern:
1. Delete `src/app/company/contact-us/page.tsx`.
2. Add `src/app/company/contact-us/route.ts` as a thin redirect route handler.
3. Locale selection in this route handler must use this priority:
   - selected locale cookie (`USER_SELECTED_LOCALE_COOKIE_KEY`)
   - browser `Accept-Language`
   - English fallback
4. Reuse the existing middleware locale helper when possible, and remove internal middleware plumbing such as `BASE_URL_KEY` from the user-facing redirect URL:
   ```ts
   import type { NextRequest } from 'next/server';
   import { NextResponse } from 'next/server';
   import { BASE_URL_KEY } from 'src/constants';
   import getUserLocale from 'src/utils/middleware/get-user-locale';

   const CONTACT_US_PATH = '/company/contact-us';

   export function GET(request: NextRequest) {
     const locale = getUserLocale(request);
     const redirectUrl = request.nextUrl.clone();
     redirectUrl.pathname = `/${locale}${CONTACT_US_PATH}`;
     redirectUrl.searchParams.delete(BASE_URL_KEY);

     return NextResponse.redirect(redirectUrl, 307);
   }
   ```
5. Replace the old root-wrapper render test with a route-handler redirect test under:
   - `src/__tests__/app/company/contact-us/redirect.test.ts`
6. Test all locale-priority cases:
   - selected-locale cookie wins over browser language
   - browser language is used when no selected-locale cookie exists
   - English is used when neither a supported cookie nor a supported browser language exists
   - query string is preserved
   - internal `baseUrl` query is stripped from the redirect `Location`
7. Keep the locale route/page tests under:
   - `src/__tests__/app/[locale]/company/contact-us/page.test.tsx`
   - `src/__tests__/app/[locale]/company/contact-us/page.en.test.tsx`
   - `src/__tests__/app/[locale]/company/contact-us/page.ko.test.tsx`
   - `src/__tests__/app/[locale]/company/contact-us/page.ja.test.tsx`
8. Update `docs/inventories/global-route-endpoint-inventory.md` so `/company/contact-us` is documented as a route handler redirect at `src/app/company/contact-us/route.ts`, not as a Next config redirect.

Verification for this pattern:
- source test: call `GET(new NextRequest(...))` and assert `307` plus `Location` for cookie/browser/fallback cases
- HTTP on Preview Deployment:
  ```bash
  curl -sS -o /dev/null -D - "$PREVIEW/company/contact-us?inquiry=demo-request&product=aip&baseUrl=https%3A%2F%2Fwww.querypie.com" \
    | awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^location:/ {print}'
  ```
  Expected examples:
  - no locale hints -> `location: /en/company/contact-us?...`
  - `Cookie: user-selected-locale=ja` -> `location: /ja/company/contact-us?...`
  - `Accept-Language: ko-KR,ko;q=0.9` -> `location: /ko/company/contact-us?...`
  - the `baseUrl` parameter must not appear in the `Location` header
- Browser check on the exact Preview Deployment should confirm the contact form renders and stable query prefills still work.

CI pitfall:
- New or moved contact-us tests must be assigned in `scripts/ci/test-groups.mjs` or `npm run test:smoke` / CI can fail with `Unassigned test files` even when Vitest itself passes.
- With the `[locale]` route structure, assign locale page tests with a matcher like:
  ```js
  /^src\/__tests__\/app\/\[locale\]\/company\/contact-us\/page(?:\.(?:en|ja|ko))?\.test\.tsx$/
  ```
- Assign the root redirect test to the routing group:
  ```js
  /^src\/__tests__\/app\/company\/contact-us\/redirect\.test\.ts$/
  ```
- If latest `origin/main` changes `scripts/ci/test-groups.mjs`, rebase conflicts are likely; preserve main's existing matcher additions and add only the contact-us redirect matcher.

## Session references

- `references/pr-706-root-contact-us-route-redirect.md` records the PR 706 follow-up where deleting the unprefixed `page.tsx` was made safe with a route handler, locale-priority redirect tests, Preview HTTP checks, and `baseUrl` leakage prevention.

## Testing strategy that worked

Because the user does not want dev-server verification unless explicitly requested, verify with:

### Route-level tests
Create:
- `src/__tests__/app/company/contact-us/page.test.tsx`
- `src/__tests__/app/ko/company/contact-us/page.test.tsx`
- `src/__tests__/app/ja/company/contact-us/page.test.tsx`

For the root wrapper test, mock the EN page module and assert delegation:

```ts
vi.mock('src/app/en/company/contact-us/page', () => ({
  generateMetadata: vi.fn(async () => ({ title: 'Contact Us - QueryPie' })),
  default: () => <div data-testid="contact-us-page-en" />,
}))
```

Then verify:
- root page renders EN page
- root `generateMetadata()` delegates to EN `generateMetadata()`

### Form-level tests
Keep / add:
- `src/components/widget/contact-sales/__tests__/contact-sales-form.component.test.tsx`
- `src/components/widget/form/ui/__tests__/form-ui.component.test.tsx`
- `src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx`

### Verification commands
Run targeted tests first:

```bash
npm run test:run -- \
  src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx \
  src/components/widget/contact-sales/__tests__/contact-sales-form.component.test.tsx \
  src/components/widget/form/ui/__tests__/form-ui.component.test.tsx \
  src/__tests__/app/company/contact-us/page.test.tsx
```

Then locale route tests:

```bash
npm run test:run -- \
  src/__tests__/app/company/contact-us/page.test.tsx \
  src/__tests__/app/ko/company/contact-us/page.test.tsx \
  src/__tests__/app/ja/company/contact-us/page.test.tsx \
  src/components/widget/contact-sales/__tests__/contact-sales-form.component.test.tsx
```

Then full local verification if the user explicitly requests local verification or asks to fix CI through local checks:

```bash
npm run lint
npm run build
```

## Important experiential findings

### A. Do not start a dev server unless explicitly requested
The user explicitly wants no dev-server-based verification unless they ask for it.
Prefer:
- targeted tests
- `npm run lint`
- `npm run build`
- PR/CI status

### B. Worktree dependency issues can look like product bugs
In this repo, worktree-local environments produced misleading local failures such as missing:
- `remark-gfm`
- `mermaid`

These were environment/dependency resolution issues, not necessarily contact-us implementation bugs.
If local build fails with unrelated module resolution, distinguish:
- code regression
- worktree dependency state

### C. Root repo install may be needed for local build verification
A successful local verification path included running `npm install` at the repo root before re-running build checks, because missing root dependencies prevented local build reproduction.

### D. EN authored page text must satisfy lint rules
In `src/app/en/company/contact-us/page.tsx`, apostrophes in JSX copy triggered `react/no-unescaped-entities`.
Use escaped forms such as:
- `you&apos;ll`

### E. Build-time `generateMetadata` signature matters
An EN page-local helper signature like `generateMetadata(urlPath?: string)` caused Next type errors in app routing.
For this route, plain app-route `generateMetadata()` was the safe form, and the root wrapper delegated to it without arguments.

## Recommended end-state summary for PR body
When describing the finished PR, summarize the final architecture, not the step-by-step history:
- static routes for company/en/ko/ja contact-us
- root EN wrapper pattern matching `/plans`
- route-local authoring
- separated contact-us form UI / behavior modules
- local lint/build and targeted tests passed

## When to reuse this skill
Use this skill when:
- a corp-web-app page currently rides through `DynamicPage` / catch-all but the user wants an explicit app route
- the user asks to match an existing root-wrapper + EN page pattern like `/plans`
- the page should read like authored route composition rather than a monolithic widget
- the user wants locale routes handled consistently with explicit pages
