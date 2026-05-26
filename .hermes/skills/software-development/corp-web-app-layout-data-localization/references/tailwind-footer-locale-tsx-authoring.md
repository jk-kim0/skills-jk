# Tailwind footer locale TSX authoring

## Context

When improving corp-web-app `(tailwind)` route-group footer, a narrow link fix can accidentally leave the footer authored through a central data/helper pattern. The user's expected direction for route-local-style layout chrome is cleaner locale-specific TSX authoring, not ad-hoc locale variables.

## Preferred shape

Use the same authoring principle as route-local pages for site-wide layout chrome when the task asks about locale-specific footer/header content:

- `tailwind-footer.tsx` should be a thin selector that maps `Locale.EN`, `Locale.JA`, and `Locale.KO` to locale modules.
- Locale modules should own visible menu copy and destinations directly:
  - `src/components/layout/tailwind-footer.en.tsx`
  - `src/components/layout/tailwind-footer.ja.tsx`
  - `src/components/layout/tailwind-footer.ko.tsx`
- Shared UI/frame primitives can live in a separate file such as `tailwind-footer-primitives.tsx`.
- Do not reintroduce central arrays or helper-generated locale content for visible footer authoring.

## Pitfall to avoid

Avoid "almost localized" helper patterns such as:

```ts
const docsLocale = locale === Locale.EN ? '' : `/${locale}`;
const getTryAipLabel = (locale: Locale) => locale === Locale.KO ? 'AIP 시작하기' : 'Try AIP Now';
const getLocalePlanHref = (locale: Locale, plan: 'aip' | 'acp') => `/${locale}/plans/${plan}`;
function createFooterColumns(locale: Locale) { ... }
```

These keep locale-specific menu wording and routes hidden behind shared logic. Prefer direct JSX in each locale file, for example:

```tsx
<TailwindFooterLink label="AIPを試す" href="https://app.querypie.com" external />
<TailwindFooterLink label="AIP" href={tailwindFooterHref('/ja/plans/aip', props)} />
<TailwindFooterLink label="ACP" href={tailwindFooterHref('/ja/plans/acp', props)} />
```

## Verification pattern

Add source-level tests that assert:

- `tailwind-footer.tsx` imports and selects `tailwind-footer.en`, `.ja`, and `.ko`.
- Locale modules contain the expected visible labels and explicit locale-prefixed plan links.
- Central helper names such as `docsLocale`, `getTryAipLabel`, `getLocalePlanHref`, and `createFooterColumns` are absent from the Tailwind footer authoring surface.
- Query-string plan links such as `/plans?aip` and `/plans?acp` are absent from footer source files.
