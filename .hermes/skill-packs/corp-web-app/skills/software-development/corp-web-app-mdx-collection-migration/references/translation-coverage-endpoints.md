# Translation coverage endpoints for MDX collections

Use this reference when adding an internal translation-coverage page for a repo-local MDX publication family, such as `/translations/events` and `/:locale/translations/events`.

## Pattern proven in corp-web-app events and blog

Goal:
- show all records for one MDX family, grouped by stable numeric ID
- sort by ID descending
- show one title per record, not one row per locale
- expose EN/JA/KO availability as explicit status/link columns
- omit thumbnails when the page is a coverage/inventory tool, not a publication list, unless the user explicitly asks for list-card parity

Preflight before coding:
- Read `docs/code-location-conventions.md` whenever the task creates new `src/app/**` routes or route-local support components, even if the main task sounds like MDX/publication work.
- Inspect the existing family publication module first, such as `src/lib/publications/blog/records.ts`, before creating any new `src/lib/translations/<family>.ts` file.
- In Next.js App Router, route folders whose names start with `_` are private and do not create public routes. Do not implement `/translations/<family>` as `src/app/_translations/<family>`; use `src/app/translations/<family>` unless the requested URL literally requires an underscore, in which case use the URL-encoded segment form (`%5F...`) deliberately.

Recommended implementation split:
- First inspect the family’s existing loader/list code.
  - If it already exposes visible list entries with the same public/list-card contract, call it per locale and group those returned items by `id`.
  - Example: blog should reuse `listBlogPublicationItems(Locale.EN|JA|KO)` rather than reimplementing `blogPublicationRepository.records` filtering, listDescription fallback, date formatting, badge selection, and href construction.
  - Add a new translation loader only for cross-locale grouping or fields the existing loader does not expose. Example: events may need a dedicated loader when the coverage page must prefer `eventDate ?? date` and the generic publication list item does not carry `eventDate`.
- Server loader under `src/lib/translations/<family>.ts` only when needed
  - scan the collection root such as `src/content/events/*.mdx`, or reuse existing family list loaders per locale
  - parse frontmatter with `js-yaml` only when no existing repository/list loader exposes the required data
  - group entries by `id`
  - keep each locale entry's `title`, `slug`, `date`, optional `eventDate`, and detail `href`
  - compute display date as `eventDate ?? date` when the family supports event dates
  - return items sorted by `Number(id)` descending
- Route page under `src/app/translations/<family>/page.tsx`
  - unprefixed internal endpoint
  - `robots: { index: false, follow: false }`
- Locale route under `src/app/[locale]/translations/<family>/page.tsx`
  - parse only supported locales and `notFound()` unsupported values
  - pass `currentLocale` into the shared page component
- Route-local support components
  - check `docs/code-location-conventions.md` / `docs/static-page-route-local-authoring.md` before adding route support UI
  - do not add new `src/app/**/_components/**` folders; in Next App Router, underscore folders are private and also conflict with the repo's route-local component placement convention
  - when the component is used only by that route, place it as a sibling like `src/app/translations/<family>/<family>-translations-table.component.tsx`
  - move reusable section/UI implementations to `src/components/sections/**` or `src/components/ui/**` instead

## Title contract

For locale-prefixed pages, the visible title should match the page URI locale when available:
- `/ko/translations/events` -> KO title if present
- `/ja/translations/events` -> JA title if present
- `/en/translations/events` -> EN title if present

Fallback order when the current locale title is missing:
1. EN
2. KO
3. JA

For unprefixed `/translations/<family>`, use the same EN -> KO -> JA fallback.

If the user asks for language-preview behavior:
- each available language badge/link should update the left title column to that locale's title on hover
- also support keyboard focus/blur, not only mouse hover
- when hover/focus leaves, reset to the current page locale title fallback
- keep the status link navigable to the actual locale detail route

## Test expectations

Add a mirrored route test, for example:

```text
src/__tests__/app/translations/events/page.test.tsx
```

Assert:
- total grouped row count equals unique record IDs, not raw MDX file count
- IDs are sorted descending
- thumbnails/images are absent
- unprefixed route renders the coverage table
- locale-prefixed route uses the current locale title by default
- missing locale cells render a missing marker
- available locale cells link to `/<locale>/t/<family>/<id>/<slug>` while still in preview mode
- hover/focus over another locale's Available link swaps the title cell, and mouse leave/blur resets it

## Verification notes

- Running a focused Vitest route test may create a tiny worktree-local `node_modules` cache directory even when dependencies are resolved from the parent checkout. Remove it before commit if the user does not want worktree-local `node_modules` residue.
- `node scripts/ci/assert-test-groups.mjs` can change counts after adding a new test; verify the new file is assigned exactly once.
- Avoid broad local typecheck/build if the user prefers relying on CI, but record any attempted baseline failures separately from the PR-caused checks.
