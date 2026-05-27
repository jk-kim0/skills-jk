# Tailwind internal index sync

Use this when updating `src/app/(tailwind)/[locale]/internal/tailwind` in `corp-web-app`.

## Goal

Keep the internal Tailwind index aligned with the actual `(tailwind)` route group on current `main`, and present migrated families in a reviewer-friendly format.

## Workflow

1. Confirm the live repo state from `main`.
2. Run the inventory and filter to Tailwind-group pages:

```bash
node scripts/inventory-tailwind-pages.ts --json \
  | jq '[.[] | select(.page | startswith("src/app/(tailwind)/"))]'
```

3. Treat the inventory output as the source of truth for which routes are currently under `(tailwind)`.
4. In `src/app/(tailwind)/[locale]/internal/tailwind/tailwind-pages.ts`, group families so `listing` and `detail` appear side by side when both exist.
5. If a family does not have both shapes yet, keep the missing side explicit in the UI rather than implying full migration.
6. Put true one-off pages such as `/[locale]/internal/tailwind` in a standalone section instead of forcing them into the pair layout.
7. Verify route coverage by comparing `routePattern` values in `tailwind-pages.ts` against the inventory output.
8. Keep source-tree scanning out of the deployed page runtime. If you need to discover routes from `src/app/(tailwind)/**`, do that in `scripts/inventory-tailwind-pages.ts` or in a test helper, then keep `tailwind-pages.ts` as deployment-safe static data.

## Notes from current main

As of the investigated `main` head in this session, the Tailwind group inventory contained 24 routes, including list routes that were easy to miss by memory alone:

- `/[locale]/t/blog`
- `/[locale]/t/events`
- `/[locale]/t/glossary`
- `/[locale]/t/introduction-deck`
- `/[locale]/t/manuals`
- `/[locale]/t/news`
- `/[locale]/t/privacy-policy`
- `/[locale]/t/whitepapers`
- `/[locale]/t/demo/acp`
- `/[locale]/t/demo/aip`
- `/[locale]/t/demo/use-cases`

## Pitfalls

- Do not rely on the older hard-coded internal index data without re-running the inventory; list routes may have been migrated since the last edit.
- Do not assume only detail pages are in `(tailwind)`; several list routes were already migrated on `main`.
- Do not call `fs.readdirSync` or similar source-directory traversal from the route module at request/render time. That can work locally while failing on stage/production because the deployed runtime does not guarantee a browsable `src/app/(tailwind)` tree.
- If the page uses a static route inventory for deployment safety, preserve parity by adding a targeted test that compares the static `routePattern` set against the real `page.tsx` routes under `src/app/(tailwind)`.
- For this user, the page should be easy to scan visually: paired `listing` / `detail` presentation is preferred over a flat mixed card list when the family naturally has both.
