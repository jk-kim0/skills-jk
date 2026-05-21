# Translation coverage internalization example

Session context: corp-web-app PR #796 added links from `/internal` to translation coverage pages for events and blog. The user clarified that translation coverage pages are not externally exposed pages and must be treated as internal pages.

## Corrected route model

Use internal locale-scoped routes:

```text
/en/internal/translations/events
/ko/internal/translations/events
/ja/internal/translations/events
/en/internal/translations/blog
/ko/internal/translations/blog
/ja/internal/translations/blog
```

Do not expose public-looking routes:

```text
/translations/events
/translations/blog
/en/translations/events
/ko/translations/events
/ja/translations/events
/en/translations/blog
/ko/translations/blog
/ja/translations/blog
```

## File movement pattern used

Route pages:

```text
src/app/[locale]/translations/events/page.tsx
  -> src/app/[locale]/internal/translations/events/page.tsx

src/app/[locale]/translations/blog/page.tsx
  -> src/app/[locale]/internal/translations/blog/page.tsx
```

Top-level route entrypoints removed:

```text
src/app/translations/events/page.tsx
src/app/translations/blog/page.tsx
```

Internal-only components moved under the internal route subtree:

```text
src/app/translations/events/events-translations-page.component.tsx
  -> src/app/[locale]/internal/translations/events/_components/events-translations-page.tsx

src/app/translations/events/events-translations-table.component.tsx
  -> src/app/[locale]/internal/translations/events/_components/events-translations-table.tsx

src/app/translations/blog/blog-translations-page.component.tsx
  -> src/app/[locale]/internal/translations/blog/_components/blog-translations-page.tsx

src/app/translations/blog/blog-translations-gallery.component.tsx
  -> src/app/[locale]/internal/translations/blog/_components/blog-translations-gallery.tsx
```

Tests moved to mirror route paths:

```text
src/__tests__/app/translations/events/page.test.tsx
  -> src/__tests__/app/[locale]/internal/translations/events/page.test.tsx

src/__tests__/app/translations/blog/page.test.tsx
  -> src/__tests__/app/[locale]/internal/translations/blog/page.test.tsx
```

## Metadata contract

Each internal translation page exported:

```ts
export const metadata: Metadata = {
  title: '...',
  description: '...',
  robots: {
    index: false,
    follow: false,
  },
};
```

Tests asserted both noindex and no canonical alternate:

```ts
expect(metadata).toMatchObject({
  robots: {
    index: false,
    follow: false,
  },
});
expect(metadata).not.toHaveProperty('alternates');
```

## Sitemap/search audit commands used

```bash
git diff --check

git ls-files | grep -E '(^src/app/(\[locale\]/)?translations|^src/__tests__/app/translations)' \
  && exit 1 \
  || echo 'no public translations route files tracked'
```

Also checked source/static references for public translation paths:

```bash
git grep -nE '/(en|ko|ja)/translations/(events|blog)|/translations/(events|blog)' -- src public || true
```

Expected surviving references after the fix are only internal paths such as `/en/internal/translations/events`.

## Verification outcome

Targeted translation route tests passed:

```bash
npx vitest run \
  'src/__tests__/app/[locale]/internal/translations/events/page.test.tsx' \
  'src/__tests__/app/[locale]/internal/translations/blog/page.test.tsx'
```

Test group assignment check passed:

```bash
node scripts/ci/assert-test-groups.mjs
```

A broader internal index test still failed at collection in the fresh worktree because local dependencies lacked `@tailwindcss/postcss`; no local install was run because the user prefers avoiding repeated worktree-local npm installs.
