---
name: corp-web-app-static-route-from-dynamic-page
description: Split a corp-web-app path out of the catch-all dynamic page into a dedicated app-route page.tsx wrapper while preserving existing DynamicPage rendering and metadata.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, static-route, dynamic-page, followup-pr]
---

# corp-web-app static route from DynamicPage

Use this when a corp-web-app path currently resolves through `src/app/[...slug]/page.tsx` and the user wants a dedicated static app route like `/plans` or `/company/contact-us`.

## When to use
- The path is currently handled by `src/app/dynamic-page.tsx` through the catch-all route.
- The user wants a real `src/app/.../page.tsx` file added.
- The page content/metadata can still be sourced from the existing dynamic-page pipeline.

## Proven pattern

Example target:
- `/company/contact-us`

### 1. Confirm the current route is catch-all based
Check:
- `src/app/[...slug]/page.tsx`
- whether `generateStaticParams()` contains the slug, e.g. `{ slug: ['company', 'contact-us'] }`

### 2. Inspect an existing dedicated root route wrapper
Good references:
- `src/app/plans/page.tsx`
- `src/app/page.tsx`

Important finding:
- Not every dedicated route in this repo has its own standalone implementation.
- For routes still backed by the file/content pipeline, the safest move is a thin wrapper around `DynamicPage`, not a rewrite.

### 3. Create a dedicated app route page
Create a file such as:
- `src/app/company/contact-us/page.tsx`

Working wrapper pattern:

```ts
import DynamicPage, { generateMetadata as generateMetadataFn, PageRequest } from 'src/app/dynamic-page';
import { Metadata } from 'next';

type StaticPageProps = Pick<PageRequest, 'searchParams'>;

const createPageRequest = (searchParams: StaticPageProps['searchParams']): PageRequest => ({
  params: Promise.resolve({ slug: ['company', 'contact-us'] }),
  searchParams,
});

export const revalidate = 3600;

export async function generateMetadata({ searchParams }: StaticPageProps): Promise<Metadata> {
  return generateMetadataFn(createPageRequest(searchParams));
}

export default async function ContactUsPage({ searchParams }: StaticPageProps) {
  return DynamicPage(createPageRequest(searchParams));
}
```

Why this worked:
- keeps the existing `DynamicPage` render path intact
- keeps existing metadata behavior intact
- introduces a true static app-route `page.tsx`
- avoids a risky content migration or duplicate page implementation

### 4. Remove the path from catch-all static params
Edit `src/app/[...slug]/page.tsx` and remove the matching entry from `generateStaticParams()`.

Example removal:

```ts
{ slug: ['company', 'contact-us'] },
```

Reason:
- avoids overlap/confusion between the dedicated route and the catch-all's pre-generated slug list

## Route-local authoring variant

If the user wants the result to read like a route-authored page (similar to a marketing/contact page refactor), do not stop at the thin wrapper.
A proven next step is:

1. keep the dedicated static route file
2. move intro copy / checklist / contact details / section composition into the route directory
3. split the form into a dedicated component that owns only form UI + submission behavior
4. extract shared form/i18n config out of the old widget wrapper so both the legacy dynamic path and the new route-local path can reuse it

### Proven structure for `/company/contact-us`

Useful file layout:

- `src/app/company/contact-us/page.tsx`
- `src/app/company/contact-us/contact-us-page-section.component.tsx`
- `src/app/company/contact-us/contact-us-page-section.module.css`
- `src/components/widget/contact-sales/contact-sales-form.component.tsx`
- `src/components/widget/contact-sales/contact-sales-form.module.css`
- `src/components/widget/contact-sales/contact-sales.i18n.tsx`

### Practical refactor pattern

- Let `page.tsx` directly author:
  - page heading
  - lead copy
  - checklist bullets
  - contact email rows
  - left/right section composition
- Let `ContactSalesForm` own only:
  - `useSearchParams()` prefill application
  - `<Form ... />` props
  - submit success state
- Let `contact-sales.i18n.tsx` own the reused locale-specific form items, labels, helper text, and after-submit copy.
- Update the old `src/components/widget/contact-sales/contact-sales.component.tsx` to consume `getContactSalesI18n(locale)` from the shared module instead of embedding all i18n/config inline.

Why this worked well:
- the route file becomes easy to read and review like the actual page structure
- the form component stays focused on form behavior
- dynamic/MDX consumers of `ContactSales` keep working
- route-local changes no longer require pushing layout/copy concerns into generic `FormUI`

## Locale-route extension pattern

If the same path also exists under localized prefixes, mirror the dedicated static route for each locale instead of leaving only the default route split out.

For contact-us, the proven follow-up set was:
- `src/app/company/contact-us/page.tsx`
- `src/app/ko/company/contact-us/page.tsx`
- `src/app/ja/company/contact-us/page.tsx`

Working locale wrapper pattern:

```ts
const createContactUsPageRequest = (searchParams: StaticPageProps['searchParams']): PageRequest => ({
  params: Promise.resolve({ slug: ['ko', 'company', 'contact-us'] }),
  searchParams,
})
```

and equivalently for JA:

```ts
params: Promise.resolve({ slug: ['ja', 'company', 'contact-us'] })
```

Practical route-authoring rule that worked well:
- reuse shared section primitives from the default route directory, e.g.
  - `src/app/company/contact-us/contact-us-page-section.component.tsx`
- keep locale-specific intro/checklist copy inside each locale page file
- reuse the same `ContactSalesForm locale={Locale.KO}` / `Locale.JA` component so form behavior stays centralized while page authoring remains route-local

Recommended locale tests:
- `src/__tests__/app/ko/company/contact-us/page.test.tsx`
- `src/__tests__/app/ja/company/contact-us/page.test.tsx`

Keep these tests focused on:
- localized heading / lead copy
- shared contact email rows
- correct form locale prop (`data-locale="ko"`, `data-locale="ja"` in mocks)

## Verification

Minimum verification without running a dev server:
1. read the new `page.tsx` and confirm it hardcodes the intended slug
2. confirm the slug was removed from `src/app/[...slug]/page.tsx`
3. if route-local authoring was requested, confirm intro/contact/layout copy now lives in the route directory rather than only inside a shared widget
4. if localized variants are in scope, confirm matching dedicated locale route files exist and each passes the correct localized slug to `DynamicPage`
5. add targeted tests for:
   - the dedicated form component (query-prefill + `whiteBackground` / form props)
   - the route page (intro copy, contact emails, route-local composition)
   - locale route pages when added
6. push to the existing PR branch and rely on CI unless the user explicitly requests local dev-server validation

### Important test pitfall found

When testing a new static route page that imports `generateMetadata` from `src/app/dynamic-page`, Vitest can fail early on transitive imports such as `remark-gfm` from `dynamic-page.tsx`, especially in worktree environments.

For route-level authoring tests that only need to verify page composition, mock `src/app/dynamic-page` before importing the route module:

```ts
vi.mock('src/app/dynamic-page', () => ({
  generateMetadata: vi.fn(),
  default: vi.fn(),
}));
```

This keeps the test focused on route-local authoring and avoids unrelated dependency-resolution failures.

## Pitfalls

1. Do not rewrite the page UI unless the user asked for a new implementation.
   - If the page is already rendered correctly through `DynamicPage`, use a wrapper.

2. Do not leave the old catch-all static param entry in place.
   - The dedicated route should own that path.

3. Do not start a local dev server unless the user explicitly asks.
   - For this repo/user workflow, prefer commit/push and CI.

4. In PR follow-up work, use a fresh worktree on the existing PR branch and push back to the same branch.

## Typical commit message

```bash
git commit -m "fix: contact-us를 static app route로 분리"
```
