# corp-web-app internal index and MDX guide links

Session-derived pattern for `src/app/[locale]/internal` index work.

## Context

The user asked to rewrite `/{locale}/internal` using the visual/card structure from `/{locale}/archived`, then asked for `/{locale}/internal/mdx-guide` child pages to be exposed directly on the internal index.

## Durable pattern

- Treat `src/app/[locale]/internal/page.tsx` as a thin locale selector, matching the archived index route pattern.
- Keep locale copy in `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx`.
- Put the card-grid renderer and CSS beside the route, e.g.:
  - `src/app/[locale]/internal/internal-index-page.tsx`
  - `src/app/[locale]/internal/internal-index-page.module.css`
  - `src/app/[locale]/internal/internal-pages.ts`
- Reuse the `/{locale}/archived` card UX when the user says the archived UI composition looks good.

## Link inventory rule

When a stage-only/internal guide page already exists but the local branch does not clearly expose its route files by filename search, inspect the exact stage URL before inventing links.

For `https://stage.querypie.com/ko/internal/mdx-guide`, the observed child links were:

- `/ko/internal/mdx-guide/basic-syntax` — Basic Syntax
- `/ko/internal/mdx-guide/images` — Images
- `/ko/internal/mdx-guide/tables` — Tables
- `/ko/internal/mdx-guide/layout-components` — Layout Components
- `/ko/internal/mdx-guide/notes-and-alerts` — Notes & Alerts
- `/ko/internal/mdx-guide/inline-components` — Inline Components
- `/ko/internal/mdx-guide/mermaid-diagrams` — Mermaid Diagrams

For the index data model, prefer `hrefByLocale` over a single `href` when some internal links are locale-aware and others are English-only:

```ts
hrefByLocale: {
  [Locale.EN]: '/en/internal/mdx-guide/basic-syntax',
  [Locale.KO]: '/ko/internal/mdx-guide/basic-syntax',
  [Locale.JA]: '/ja/internal/mdx-guide/basic-syntax',
}
```

Render by filtering missing locale hrefs:

```ts
const pages = group.pages.flatMap(page => {
  const href = page.hrefByLocale[locale];
  return href ? [{ ...page, href }] : [];
});
```

This keeps English-only component demo pages from leaking broken `/ko` or `/ja` links while still exposing MDX guide child pages directly for every locale.

## Exclusion and route-inventory regressions

If the user asks to remove index items, add a source-level test asserting the removed labels/hrefs do not appear, but distinguish label-level removals from live route-level inventory.

Important correction from follow-up work:
- `MDX Preview` / `Live MDX editor` was a removed index entry label, but the route `/{locale}/internal/preview` itself is a live internal child page and should be exposed as `Preview Route Index` when the user asks the internal index to list all live children.
- Do not keep a blanket `not.toContain('/internal/preview')` assertion after the route is intentionally restored. Instead, assert the removed editor labels are absent and add a positive test for `/en/internal/preview`, `/ko/internal/preview`, and `/ja/internal/preview`.
- Use a separate group such as `Internal route tools` for the live preview route so it is not confused with the deleted MDX editor entry.

Route inventory workflow for `src/app/[locale]/internal`:
1. Enumerate route files under `src/app/[locale]/internal/**/page.tsx`.
2. Check current/stage HTTP status by locale before adding locale-specific links.
3. Add `hrefByLocale` for routes that are live in every locale.
4. For English-only internal demos, keep links pointed at the actual supported English route or omit unsupported locales rather than generating broken `/ko` or `/ja` hrefs.
5. Update tests in both directions: positive assertions for restored/live routes and negative assertions for explicitly removed labels.

Observed status pattern from the internal index follow-ups:
- `preview`: `/en/internal/preview`, `/ko/internal/preview`, `/ja/internal/preview` all returned 200 and should be listed.
- `plans`: only `/en/internal/plans` returned 200 during the session; KO/JA wrappers returned 404, so locale index links should not claim localized pricing-plan support unless that changes.
- English-only component examples such as `usage`, `key-values`, `risks`, `main-feature-description`, `killer-features`, and `compare-table` should be separated from every-locale groups in tests.

In the original rewrite session the removed entries were:

- `MDX Preview` / `Live MDX editor`
- `Pricing Plans` as a generic all-locale index entry
- language-selector entries: `English`, `Japanese`, `Korean`
