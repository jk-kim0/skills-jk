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

## Exclusion regression

If the user asks to remove index items, add a source-level test asserting the removed labels/hrefs do not appear. In this session the removed entries were:

- `MDX Preview` / `Live MDX editor`
- `Pricing Plans`
- language-selector entries: `English`, `Japanese`, `Korean`
- `/internal/preview`
- `/internal/plans`
