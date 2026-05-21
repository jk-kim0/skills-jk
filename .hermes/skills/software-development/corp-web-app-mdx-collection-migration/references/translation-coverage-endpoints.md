# Translation coverage endpoints for MDX collections

Use this reference when adding an internal translation-coverage page for a repo-local MDX publication family, such as `/translations/events` and `/:locale/translations/events`.

## Pattern proven in corp-web-app events

Goal:
- show all records for one MDX family, grouped by stable numeric ID
- sort by ID descending
- show one title per record, not one row per locale
- expose EN/JA/KO availability as explicit status/link columns
- omit thumbnails when the page is a coverage/inventory tool, not a publication list

Recommended implementation split:
- Server loader under `src/lib/translations/<family>.ts`
  - scan the collection root such as `src/content/events/*.mdx`
  - parse frontmatter with `js-yaml`
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
- Shared page component under `src/app/translations/<family>/_components/...`
  - mostly server component
  - uses a nested client table only if hover/focus interactivity is required

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
