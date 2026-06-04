# News MDX type labels

Use when evaluating or implementing labels for `src/content/news` records such as official announcements, press releases, and general news/media coverage.

## Current implementation shape

- News MDX files already commonly include a free-form `sourceLabel` frontmatter field, with localized values such as:
  - KO: `미디어 보도`, `공식 발표`, `보도자료`
  - EN: `Media coverage`, `Official announcement`, `Press release`
  - JA: `メディア掲載`, `公式発表`, `プレスリリース`
- `sourceLabel` is not currently part of `ResourceRecord` in `src/lib/resources/resource-collection.ts` and is not propagated into `ResourceCollectionListItem` / `ResourceListItem`.
- News list rendering in `src/components/sections/resource-list/resource-list-section.component.tsx` currently uses `NewsListItems`, which renders date/title/description/image but not the generic resource badge pill.
- News detail rendering in `src/app/(tailwind)/[locale]/news/[id]/[slug]/news-detail-post-page.tsx` currently shows the fixed family badge via `getPublicationFamilyBadge('news', locale)`.
- `src/lib/resources/resource-list.ts` maps the `news` family badge to `News` / `뉴스` / `ニュース`, so every news item currently has the same list item badge when converted through `toPublicationResourceItems`.

## Recommendation

Do not rely on localized free-form `sourceLabel` as the canonical type key. Add a normalized enum-style field, for example:

```yaml
newsType: official-announcement
```

Allowed values:

```ts
'official-announcement' | 'press-release' | 'news'
```

Map these to locale labels in code:

| `newsType` | EN | KO | JA |
| --- | --- | --- | --- |
| `official-announcement` | Official Announcement | 공식발표 or 공식 발표 | 公式発表 |
| `press-release` | Press Release | 보도자료 | プレスリリース |
| `news` | News | 뉴스 | ニュース |

If the user requests exactly three labels (`공식발표`, `보도자료`, `뉴스`), map existing media-coverage-style records (`미디어 보도`, `Media coverage`, `メディア掲載`) to `news` unless they explicitly ask to keep `media-coverage` as a fourth type.

## Implementation checklist

1. Add `newsType` or a similarly normalized field to `ResourceRecord` and `ResourceCollectionListItem` in `src/lib/resources/resource-collection.ts`.
2. Parse it from MDX frontmatter in `readRecord()`.
3. Extend `ResourceListItem` in `src/lib/resources/resource-list.ts` so item badges can be record-specific rather than only family-specific.
4. Add a news-specific mapping helper, e.g. `getNewsTypeBadge(newsType, locale)`, and use it in `listNewsPublicationItems()`.
5. Render the label on public news list cards in `NewsListItems`.
6. Replace the detail page's fixed `getPublicationFamilyBadge('news', locale)` with the record-specific news type label.
7. Add `newsType` frontmatter to all `src/content/news/*.mdx`; keep or remove `sourceLabel` explicitly rather than leaving it as a shadow field.
8. Update tests that assert list-card fields and detail badges, especially:
   - `src/__tests__/app/[locale]/internal/translations/news/page.test.tsx`
   - `src/__tests__/app/[locale]/news-public-route.test.tsx`
   - `src/lib/resources/__tests__/news-migration.test.ts`

## Pitfalls

- Do not treat existing `sourceLabel` as already functional UI state; it is content-only unless the loader is extended.
- Avoid using localized strings as logic keys. They make filtering, tests, and cross-locale parity brittle.
- Hidden press releases can still need detail rendering and related links; do not exclude them from detail lookup just because they are hidden from lists.
