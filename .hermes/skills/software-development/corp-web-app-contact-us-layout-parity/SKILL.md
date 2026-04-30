---
name: corp-web-app-contact-us-layout-parity
description: Update corp-web-app /company/contact-us to visually track a reference contact page by converting the shared ContactSales form UI into a contact-sales-only two-column layout with a right-side form card, without affecting other FormUI consumers.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, contact-us, layout, form-ui, nextjs, css, pr-workflow]
---

# corp-web-app contact-us layout parity

Use this when the user asks to make `corp-web-app` `/company/contact-us` match a live reference page more closely in layout, form width, and form position.

## When this skill applies
- The page uses `ContactSales` / `FormUI`
- The requested change is mostly visual parity: two-column composition, intro text placement, form width, and right-side alignment
- Other `FormUI` consumers must not regress

## Proven approach

### 1. Inspect the live reference first
Use browser tools on the reference URL and capture these exact facts:
- whether the layout is single-column or two-column
- whether the intro text is left-aligned or centered
- approximate total content width
- whether the form is centered or offset right
- approximate form card width
- whether fields remain single-column inside the form

For `https://querypie.ai/contact-us`, the effective reference pattern was:
- two-column desktop layout
- left-aligned intro text on the left
- right-offset form card
- form card roughly ~500–560px wide
- fields still stacked in a single vertical column

### 2. Start from latest `origin/main` in a fresh worktree and fresh branch
If the current branch points to an already merged PR or stale topic branch, do not continue there.
Use:
- fresh worktree from `origin/main`
- fresh branch for the new PR

This matched the user's expectation for new independent repo work.

### 3. Trace the real implementation path before editing
Relevant files discovered for this page:
- `src/components/widget/contact-sales/contact-sales.component.tsx`
- `src/components/widget/form/ui/form-ui.component.tsx`
- `src/components/widget/form/ui/form-ui.module.css`
- tests in `src/components/widget/form/ui/__tests__/form-ui.component.test.tsx`
- tests in `src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx`

Important finding:
- `ContactSales` itself is thin; the actual page layout is owned by shared `FormUI`
- therefore layout changes must be isolated to `submitAction === 'contact-sales'`

### 4. Keep the change contact-sales-only
In `form-ui.component.tsx`, derive a boolean like:

```ts
const isContactSalesLayout = submitAction === 'contact-sales'
```

Use that boolean for both:
- query-prefill logic gating
- layout/style gating

Do not globally change `FormUI` container behavior for all submit actions.

### 5. Apply the layout in `FormUI`, not `ContactSales`
Proven structure:
- keep the existing title/description block
- add contact-sales-only container classes
- wrap the form in a contact-sales-only card container
- pass `whiteBackground={isContactSalesLayout}` to `Form`

Pattern:

```tsx
<div className={cn(styles.container, { [styles.contactSalesContainer]: isContactSalesLayout })}>
  <div className={cn(styles.text, { [styles.contactSalesText]: isContactSalesLayout })}>
    ...
  </div>

  <div className={cn(styles.formBox, { [styles.contactSalesFormBox]: isContactSalesLayout })}>
    <div className={cn({ [styles.contactSalesFormCard]: isContactSalesLayout })}>
      <Form ... whiteBackground={isContactSalesLayout} />
    </div>
  </div>
</div>
```

Why this worked:
- `ContactSales` stays simple
- layout concerns remain localized to the shared UI layer that already owns title + form composition
- other form pages still use the old layout path

### 6. Use CSS to create parity, but do not change field structure
In `form-ui.module.css`, the proven styling was:
- smaller default gap than before
- contact-sales-only desktop grid at `min-width: 1024px`
- left text column with constrained max width
- right form column with capped width (`~35rem`)
- white card with light border, rounded corners, and soft shadow

Representative pattern:

```css
.contactSalesContainer {
    gap: var(--rem-48px);
}

.contactSalesText {
    max-width: 34rem;
}

.contactSalesFormCard {
    padding: clamp(1.5rem, 1.0417rem + 1.0417vw, 2rem);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: var(--rem-24px);
    background: var(--bg-white);
    box-shadow: 0 24px 64px rgba(15, 23, 42, 0.08);
}

@media (min-width: 1024px) {
    .contactSalesContainer {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(32rem, 35rem);
        align-items: start;
    }

    .contactSalesFormBox {
        justify-self: end;
        width: min(100%, 35rem);
    }
}
```

Important constraint:
- keep the actual form fields single-column inside `Form`
- the reference page changed composition, not the internal field grouping

### 7. Reuse `Form.whiteBackground` for internal input contrast
The outer card becomes white, so the internal form should switch to its existing white-background variant.
Passing:

```tsx
whiteBackground={isContactSalesLayout}
```

lets the form reuse its existing gray input/background behavior without rewriting `Form` internals.

### 8. Update tests in the shared `FormUI` test, not only contact-sales tests
`contact-sales.component.test.tsx` alone is not enough because the isolation behavior lives in `FormUI`.

Useful assertion pattern:
- for `submitAction="contact-sales"`, the mocked `Form` receives `whiteBackground=true`
- for another submit action, the mocked `Form` receives `whiteBackground=false`
- query-prefill behavior still works only for `contact-sales`

Mock shape that worked:

```tsx
Form: ({ items, whiteBackground }) => (
  <div data-testid="form-props" data-white-background={whiteBackground ? 'true' : 'false'}>
    <pre data-testid="form-items">{JSON.stringify(items, null, 2)}</pre>
  </div>
)
```

### 9. If route-local authoring is requested later, extract the contact-us UI out of `FormUI`
A later proven refinement was:
- keep generic `FormUI` for shared/non-contact forms
- move the contact-us-specific branch out of `src/components/widget/form/ui/form-ui.component.tsx`
- create `src/components/widget/form/ui/contact-us-form-ui.component.tsx`
- let `FormUI` do only:

```ts
if (submitAction === 'contact-sales') {
  return <ContactUsFormUI title={title} description={description} i18n={i18n} />
}
```

Why this was worth doing:
- removes contact email rows / prefill logic / white-card composition from the generic shared form UI file
- makes it obvious that contact-us has a specialized layout path
- reduces the risk of future generic `FormUI` changes accidentally regressing contact-us behavior

Useful follow-up verification after this extraction:
- `src/components/widget/form/ui/__tests__/form-ui.component.test.tsx`
- `src/components/widget/contact-sales/__tests__/contact-sales-form.component.test.tsx`
- `src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx`
- route-level page tests if route-local authoring exists

### 10. If the user wants `/plans`-style app routes, split root and EN routes explicitly
Important follow-up finding:
- creating only `src/app/company/contact-us/page.tsx` does NOT make `/en/company/contact-us` use the same static route pattern as `/plans`
- without an explicit EN route file, `/en/company/contact-us` is still served by `src/app/[...slug]/page.tsx` -> `src/app/dynamic-page.tsx`
- this happens because `getAvailableLocaleAndSlugs()` treats `en` as a locale prefix and forwards the remainder (`company/contact-us`) to the catch-all path

If the user says "do it like `/plans`", the more faithful pattern is:
- `src/app/en/company/contact-us/page.tsx` = actual EN authored page
- `src/app/company/contact-us/page.tsx` = root wrapper that imports the EN page, just like `src/app/plans/page.tsx`
- `src/app/ko/company/contact-us/page.tsx` and `src/app/ja/company/contact-us/page.tsx` = locale-authored pages if those should also be static and route-local

Recommended structure:

```tsx
// src/app/company/contact-us/page.tsx
import ContactUsPageEn, { generateMetadata as generateMetadataEn } from '../../en/company/contact-us/page'
import { Metadata } from 'next'

export async function generateMetadata(): Promise<Metadata> {
  return generateMetadataEn('/company/contact-us')
}

export default function ContactUsPageDefault() {
  return <ContactUsPageEn />
}
```

And the EN page should own the real authored structure, similar to `src/app/en/plans/page.tsx`.

Practical implication:
- if the user later asks "who answers `/en/company/contact-us`?", check whether `src/app/en/company/contact-us/page.tsx` exists
- if it does not, the answer is still the catch-all dynamic route, not the root wrapper page
- if the goal is full `/plans` parity, add the EN static route explicitly rather than stopping at the root wrapper

### 11. Route-local authoring can be reused across locales with a shared section primitive file
A useful pattern after introducing static routes was:
- keep shared layout primitives in `src/app/company/contact-us/contact-us-page-section.component.tsx` and matching CSS module
- author locale-specific copy in:
  - `src/app/company/contact-us/page.tsx`
  - `src/app/ko/company/contact-us/page.tsx`
  - `src/app/ja/company/contact-us/page.tsx`
- reuse `ContactSalesForm locale={Locale.EN | Locale.KO | Locale.JA}` per route

This keeps:
- route-local copy ownership
- shared visual structure
- locale-specific form behavior via shared i18n/form config

Useful route-level regression tests:
- `src/__tests__/app/company/contact-us/page.test.tsx`
- `src/__tests__/app/ko/company/contact-us/page.test.tsx`
- `src/__tests__/app/ja/company/contact-us/page.test.tsx`

Those tests should verify:
- heading and intro copy come from the route file
- contact email rows are present in the route output
- the route wires the expected locale into `ContactSalesForm`

### 12. Prefer targeted tests over spending time on local dev if the worktree environment is noisy
Targeted verification that passed:

```bash
npm run test:run -- \
  src/components/widget/form/ui/__tests__/form-ui.component.test.tsx \
  src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx
```

After route-local authoring / contact-us module extraction, the broader targeted set that stayed useful was:

```bash
npm run test:run -- \
  src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx \
  src/components/widget/contact-sales/__tests__/contact-sales-form.component.test.tsx \
  src/components/widget/form/ui/__tests__/form-ui.component.test.tsx \
  src/__tests__/app/company/contact-us/page.test.tsx
```

Observed local-environment pitfall:
- starting a dev server from the fresh worktree could surface unrelated module-resolution noise such as `Module not found: Can't resolve 'remark-gfm'`
- when that happens, do not burn time debugging unrelated workspace/worktree dependency behavior for a scoped layout PR unless the user explicitly asks
- instead, keep the change isolated, verify with targeted tests, and move to PR/CI

This matches the user's preference to avoid spending time on local dev verification when CI is the real gate.

## Recommended workflow summary
1. Inspect reference page with browser tools
2. Create fresh worktree from latest `origin/main`
3. Confirm `ContactSales` delegates to shared `FormUI`
4. Gate all layout changes on `submitAction === 'contact-sales'`
5. Add desktop two-column grid + right-side form card in `form-ui.module.css`
6. Pass `whiteBackground` only for contact-sales
7. Add/adjust `FormUI` tests to verify the isolation
8. If the page later needs route-authored intro/contact structure, split that path into a route-local page + dedicated `ContactSalesForm`, and then extract the remaining contact-us-specific `FormUI` branch into `contact-us-form-ui.component.tsx`
9. Run targeted Vitest checks
10. Commit, push, open Draft PR, and monitor CI

## Success criteria
- `/company/contact-us` visually shifts from stacked layout toward the two-column reference
- the form width is narrower and visually anchored on the right on desktop
- the internal field stack remains unchanged
- other `FormUI` consumers are unaffected
- tests confirm both contact-sales behavior and non-contact-sales isolation
