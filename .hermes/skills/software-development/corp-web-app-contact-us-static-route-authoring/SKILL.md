---
name: corp-web-app-contact-us-static-route-authoring
description: Refactor corp-web-app contact-us routes into static app routes with route-local authoring, locale-specific pages, and a root EN wrapper pattern matching /plans.
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
- route-local page authoring in `page.tsx`
- root English route acting like `/plans`
- form behavior separated from page composition
- no local dev server unless the user explicitly asks
- verify with targeted tests, lint, and build

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
