---
name: corp-web-app-contact-form-query-prefill
description: Add stable query-string prefills to the corp-web-app ContactSales form while preserving locale-specific submitted values.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, contact-form, query-string, prefill, locale, forms]
---

# corp-web-app contact form query prefill

Use this when adding CTA-driven default selections to `/company/contact-us` in `corp-web-app`.

## Goal

Support URLs like:
- `/company/contact-us?inquiry=download`
- `/ja/company/contact-us?inquiry=demo-request&product=ai-dashi&product=aip`

while keeping:
- query params locale-independent and stable
- displayed option labels locale-specific
- submitted Salesforce values locale-specific text, not the stable keys

## Proven approach

### 1. Put stable keys on form options in `messages.ts`

File:
- `src/components/widget/form/lib/messages.ts`

Add an optional `key` field to each select / multi-checkbox option.
Use a helper like:

```ts
const buildOption = (key: string, value: string, label = value) => ({ key, value, label })
```

Recommended query keys:
- inquiry: `ai-consulting`, `download`, `demo-request`, `quote-request`, `technical-question`, `partnership`, `other`
- product: `ai-crew`, `ai-dashi`, `aip`, `acp`, `fde`, `partnership`

Important: keep `value` as the locale-specific human-readable string so Salesforce still receives localized text.

### 2. Add a locale-aware mapping helper in `messages.ts`

Also in `src/components/widget/form/lib/messages.ts`, add a helper that:
- reads `inquiry` and repeated `product` params
- finds matching options by `key`
- writes `initialValue` using matched option `value`
- ignores unmatched keys silently

Pattern:

```ts
applyContactSalesQueryPrefill(items, searchParams)
```

The helper should only transform:
- `Objective__c` select
- `Product` multiCheckbox

### 3. Read query params in the client, not via MDX/server plumbing

Best insertion point found:
- `src/components/widget/form/ui/form-ui.component.tsx`

Use `useSearchParams()` and memoize transformed items.
Only apply when `submitAction === 'contact-sales'` so other forms do not accidentally consume these params.

Pattern:

```ts
const searchParams = useSearchParams()
const items = useMemo(() => {
  if (submitAction !== 'contact-sales') return i18n.formItems
  return applyContactSalesQueryPrefill(i18n.formItems, searchParams)
}, [i18n.formItems, searchParams, submitAction])
```

Why this approach worked better than server-side propagation:
- avoids threading props through MDX/server component layers
- keeps the behavior local to the actual form UI
- matches existing app usage of `useSearchParams`

### 4. Fix `FormItem` so `initialValue` actually updates rendered state

File:
- `src/components/widget/form/ui/form-item.component.tsx`

Two necessary fixes were required:

1. Sync internal state when `initialValue` changes:

```ts
useEffect(() => {
  setValue(initialValue ?? (type !== 'multiCheckbox' ? '' : []))
}, [initialValue, type])
```

2. For multi-checkbox inputs, bind `checked`:

```tsx
checked={Array.isArray(value) && value.includes(option.value)}
```

Without the `checked` binding, product prefills do not appear visually even if state is initialized.

### 5. Update tests in the right locations

`vitest.config.mts` only includes:
- `src/**/__tests__/**/*.{test,spec}.{js,ts,tsx}`

So test files must live under `__tests__` directories. Standalone `*.test.ts` beside files will be ignored.

Working test locations:
- `src/components/widget/form/lib/__tests__/messages.test.ts`
- `src/components/widget/form/ui/__tests__/form-item.component.test.tsx`
- `src/components/widget/form/ui/__tests__/form-ui.component.test.tsx`
- existing `src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx`

Recommended coverage:
- helper maps stable keys to localized JA values
- helper ignores keys missing in current locale option set
- `FormItem` select respects `initialValue`
- `FormItem` multi-checkbox renders checked state from `initialValue`
- `FormUI` applies prefill only for `contact-sales`
- contact-sales option tests reflect `key + value + label`

## Pitfalls found

1. `FormItem` was originally semi-uncontrolled for checkbox prefills.
   - State initialized, but checkbox UI not checked.
   - Must add `checked` binding.

2. `initialValue` changes need syncing.
   - If `FormUI` recomputes items after mount, `FormItem` must react.

3. New tests must be under `__tests__/` because of repo Vitest include globs.

4. Keep query params as stable keys, not localized strings.
   - Otherwise CTA links become locale-coupled and fragile.

5. Do not submit stable keys to Salesforce.
   - Always convert key -> locale-specific `value` before assigning `initialValue`.

## Verification commands

Run targeted tests:

```bash
npx vitest run \
  src/components/widget/form/lib/__tests__/messages.test.ts \
  src/components/widget/form/ui/__tests__/form-item.component.test.tsx \
  src/components/widget/form/ui/__tests__/form-ui.component.test.tsx \
  src/components/widget/contact-sales/__tests__/contact-sales.component.test.tsx
```

## Browser QA notes for contact-us prefills

When validating the live contact form, test the public stable query API, not the internal Salesforce field name.

Use URLs like:
- `https://www.querypie.com/ja/company/contact-us?inquiry=demo-request`
- `https://www.querypie.com/ja/company/contact-us?inquiry=ai-consulting`
- `https://www.querypie.com/ja/company/contact-us?inquiry=download`

Important live finding:
- `?inquiry=...` prefilled the visible `お問い合わせの種類` select correctly on the live page.
- Testing `?Objective__c=...` can produce a false negative even though prefill support exists, because the intended public interface is the stable `inquiry` key.

## Live validation note for contact-us prefills

When validating CTA-driven contact-us prefills on the live site, test the stable query keys introduced by this pattern, not the Salesforce field name directly.

Use URLs like:
- `?inquiry=demo-request`
- `?inquiry=ai-consulting`
- `?inquiry=download`

Do not treat `?Objective__c=<localized text>` as the primary verification path.
A later investigation confirmed that the live JP contact-us page prefilled correctly for stable `inquiry=` keys while direct `Objective__c` query-string tests still showed the placeholder state.

Practical implication:
- for CTA inventory or stakeholder docs, describe the implemented prefill route using stable `inquiry=` URLs
- if a direct `Objective__c` test appears broken, do not conclude prefill is unsupported until you test the stable keys

## Browser QA notes for gated download pages

When validating a live gated download page (for example `https://www.querypie.com/ja/features/documentation/aip-introduction-download`):

1. Check prefill behavior on the live URL with query params.
2. Separately verify the original gating behavior still works:
   - fill the required fields
   - use a business email address
   - submit the form
   - confirm the PDF viewer or download target opens

Important live finding:
- The form rejects public email providers such as Gmail with `Please enter a business email address.`
- Use a business-style domain (for example `qa-check@openai.com`) when browser-testing actual submission.
- On successful submit for the AIP introduction JP page, the result opened the PDF viewer for:
  - `https://www.querypie.com/public/downloads/intro-decks/QueryPie_AIP_Intro_JP.pdf`

This is useful for distinguishing two failure modes:
- prefill not applied
- submit/download flow itself broken

## Typical follow-up work

After this feature lands, update CTA links in content or page components to pass params such as:
- `?inquiry=download`
- `?inquiry=demo-request`
- `?inquiry=demo-request&product=aip`
- repeated product params for multi-select defaults
