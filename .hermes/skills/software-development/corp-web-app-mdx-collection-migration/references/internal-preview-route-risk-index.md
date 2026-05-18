# Internal preview route risk index

Session-derived pattern for corp-web-app work that asks for an internal page listing every `/{locale}/t/*` preview/document route and preventing dead links.

## Pattern

- Add a single source of truth under `src/lib/**` for the internal preview inventory, rather than hardcoding separate page and test lists.
  - Example shape: `src/lib/internal-preview-routes.ts` exports `getInternalPreviewRouteGroups(locale)` and `getInternalPreviewRoutes(locale)`.
- The internal page can live at `src/app/[locale]/internal/preview/page.tsx` and render the inventory for `/en`, `/ko`, and `/ja`.
- Keep the page explicitly internal:
  - metadata `robots: { index: false, follow: false }`
  - no public navigation/sitemap changes unless explicitly requested.
- For publication/document families, generate detail links from repo-local repositories/records and exclude records that should not create local detail links:
  - `hidden === true`
  - `redirectUrl` present
  - `noindex === true`
- Include list routes explicitly even when no detail records exist for a locale, because list route existence is a separate contract.
- For nested families, do not rely only on generic `family` names when building route files. Keep route-source path and public base path explicit:
  - use cases: `/t/demo/use-cases` -> `src/app/[locale]/t/demo/use-cases/page.tsx`
  - AIP demo: `/t/demo/aip`
  - ACP demo: `/t/demo/acp`
  - tutorials: `/t/tutorials/:category/:id/:slug`

## Dead-link test contract

Add a mirrored route test such as `src/__tests__/app/[locale]/internal/preview/page.test.tsx` that:

1. Renders `/{locale}/internal/preview` and checks representative links.
2. Iterates `internalPreviewLocales` and `getInternalPreviewRoutes(locale)`.
3. Asserts every href starts with `/${locale}/t`.
4. Asserts no duplicate hrefs.
5. Converts each listed href to the expected App Router route file and verifies that file exists.

This catches stale inventory entries and prevents a PR from adding an internal preview link that points at a missing `page.tsx`.

## Verification

Use focused Vitest instead of a dev server:

```bash
npx vitest run src/__tests__/app/[locale]/internal/preview/page.test.tsx
```

If full `tsc --noEmit` fails in a fresh worktree because of existing unrelated test/mock type errors, report it as baseline and keep the focused route contract test as the verification for this change.
