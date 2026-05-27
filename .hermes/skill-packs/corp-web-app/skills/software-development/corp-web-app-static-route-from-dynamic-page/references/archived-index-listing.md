# Archived index listing pattern

Use this note when maintaining `corp-web-app` archived route-local pages under `src/app/[locale]/archived/**` and the unprefixed English shim under `src/app/archived/**`.

## Durable lesson

The `/archived` index page is allowed to exist as a link hub for migrated archived child pages, but the index itself should not be promoted as a search landing page.

Recommended metadata for the index route only:

```ts
robots: 'noindex, follow'
```

Why:
- `noindex` keeps the index page itself out of Google search results.
- `follow` still allows crawlers to discover the archived child page links from the index.
- Do not apply this as a blanket rule to archived child pages unless the user explicitly asks; child pages may remain indexable.

## Listing completeness check

When adding or repairing the archived index:

1. Enumerate localized child authoring files under `src/app/[locale]/archived/**/page.{en,ko,ja}.tsx`.
2. Exclude the index route itself: `src/app/[locale]/archived/page.{en,ko,ja}.tsx`.
3. Confirm every localized child page has a corresponding entry in `archivedPageGroups`.
4. Include only locales that actually have a `page.<locale>.tsx` file. For example, a page with only `page.en.tsx` and `page.ja.tsx` should not list a `/ko/...` href.
5. Keep the unprefixed `/archived` page as the English/default shim, but do not list `/archived` itself as a child page.

## Targeted regression test pattern

A lightweight Vitest can protect the contract without running a dev server:

- Walk `src/app/[locale]/archived` recursively.
- Collect each `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` child route.
- Compare the collected routes to the flattened `archivedPageGroups[*].pages[*].hrefByLocale` list.
- Assert the index metadata returns `robots: 'noindex, follow'` for default, EN, KO, and JA index entries.
- Assert representative child links are present and the index paths `/en/archived`, `/ko/archived`, `/ja/archived` are not treated as child records.

This catches the common drift where new archived pages are added but the index listing omits them.
