# News `newsType` frontmatter rebase/CI pattern

Use this when rebasing or updating corp-web-app PRs that touch `src/content/news/**`, news detail/list UI, or publication repository tests.

## Durable lesson

News MDX `newsType` is a content contract, not just display copy. During rebases against main branches that added or removed news-label work, do not only preserve the frontmatter in MDX files. Verify that the shared resource loader still carries the field through to `ResourceRecord` and that the news UI consumes it.

A common failure shape:

- CI `Test publications` fails while `Validate Test` fails only as the aggregate job.
- `src/__tests__/app/[locale]/news-public-route.test.tsx` expects a localized news type label such as `メディア掲載`, but the rendered detail badge is the generic family label `ニュース`.
- `src/lib/resources/__tests__/news-migration.test.ts` expects `post.newsType` such as `press-release`, but receives `undefined`.
- The MDX files themselves already contain `newsType: media-coverage`, `press-release`, or `official-announcement`.

Root cause to check before editing tests:

1. Inspect `src/lib/resources/resource-collection.ts`.
2. Confirm `ResourceRecord` includes `newsType: string | null` or an equivalent typed field.
3. Confirm `readRecord()` maps `frontmatter.newsType` into the returned record.
4. Inspect the news detail/list UI path and confirm it uses `post.newsType` or list item `newsType` for localized labels, falling back to the generic `News/뉴스/ニュース` family badge only when the field is absent.

## Minimal fix pattern

If frontmatter has `newsType` but repository/UI tests see `undefined` or generic badges:

```ts
export type ResourceRecord = {
  // ...existing fields
  newsType: string | null;
};

function readRecord(sourcePath: string, locale: Locale): ResourceRecord {
  // ...frontmatter parsing
  return {
    // ...existing fields
    newsType: typeof frontmatter.newsType === 'string' ? frontmatter.newsType : null,
  };
}
```

For news detail badges, use a small localized map and fallback to `getPublicationFamilyBadge('news', locale)` only when `newsType` is missing or unknown:

```ts
const newsTypeBadges: Record<string, Record<Locale, string>> = {
  'official-announcement': {
    [Locale.EN]: 'Official Announcement',
    [Locale.KO]: '공식 발표',
    [Locale.JA]: '公式発表',
  },
  'press-release': {
    [Locale.EN]: 'Press Release',
    [Locale.KO]: '보도자료',
    [Locale.JA]: 'プレスリリース',
  },
  'media-coverage': {
    [Locale.EN]: 'Media Coverage',
    [Locale.KO]: '미디어 보도',
    [Locale.JA]: 'メディア掲載',
  },
};
```

## Verification

Run the focused publication tests that encode the contract:

```bash
npx vitest run src/__tests__/app/[locale]/news-public-route.test.tsx src/lib/resources/__tests__/news-migration.test.ts
```

Also verify:

- `git diff --check`
- no conflict markers remain
- PR head and remote branch match after push
- GitHub checks are re-read after push, because `Validate Test` may only reflect dependency-job aggregation while the actionable failure is in `Test publications`.

## Pitfalls

- Do not fix this by weakening tests to accept generic `뉴스/News/ニュース` badges when MDX `newsType` is present. That hides a loader contract regression.
- Do not reintroduce old `sourceLabel` frontmatter when main uses `newsType`; preserve the current main contract and migrate/rebase PR content onto it.
- When latest main added new news IDs, assign PR-added news after the current max ID and update assets, hidden related links, and tests together.
