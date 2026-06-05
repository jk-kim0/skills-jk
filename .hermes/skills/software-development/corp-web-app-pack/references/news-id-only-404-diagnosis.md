# News ID-only 404 diagnosis and redirect implementation in corp-web-app

Use when a reported stage/production URL like `/<locale>/news/<id>` returns 404 while the news item may exist, or when implementing compatibility for ID-only news URLs.

## Diagnostic pattern

1. Probe the reported URL and the expected canonical candidate with headers:

```bash
curl -sS -I https://stage.querypie.com/en/news/14
curl -sS -I https://stage.querypie.com/en/news/14/top-50-software-ceos-of-2024
```

2. Compare `x-matched-path`:
- `x-matched-path: /[locale]/news/[id]/[slug]` means the App Router news detail route matched.
- `x-matched-path: /[...slug]` means the request fell through to the legacy catch-all, so the news detail route did not match.

3. Check current route shape:
- Expected public detail route: `src/app/(tailwind)/[locale]/news/[id]/[slug]/page.tsx`
- ID-only route is absent unless `src/app/(tailwind)/[locale]/news/[id]/page.tsx` exists.

4. Check content existence and canonical slug:
- `src/content/news/<id>-<slug>.<locale>.mdx`
- frontmatter `id` and `slug`

5. Check generated list href contract:
- `src/lib/publications/news/records.ts` or repository list mapping should generate `/${locale}/news/${record.id}/${record.slug}`.
- `src/lib/resources/resource-collection.ts` `getDetail` requires both `id` and matching `slug`; slug mismatch returns `not-found`.

## Interpretation

If content exists and `/<locale>/news/<id>/<slug>` returns 200, but `/<locale>/news/<id>` returns 404 with `x-matched-path: /[...slug]`, the cause is not missing content. The cause is that the ID-only shortcut URL is not implemented or redirected.

## Implementation pattern

If ID-only URLs must be supported for external/backward compatibility, add a thin App Router page at:

```text
src/app/(tailwind)/[locale]/news/[id]/page.tsx
```

Pattern:

```tsx
import { notFound, redirect } from 'next/navigation';
import { newsPublicationRepository } from 'src/lib/resources/news';
import { Locale } from 'src/models/locale';

type PageProps = {
  params: Promise<{
    locale: string;
    id: string;
  }>;
};

function parseLocale(value: string): Locale | null {
  if (value === Locale.EN || value === Locale.KO || value === Locale.JA) {
    return value;
  }

  return null;
}

export default async function NewsIdRedirectPage({ params }: PageProps) {
  const { locale: localeParam, id } = await params;
  const locale = parseLocale(localeParam);

  if (!locale) {
    notFound();
  }

  const record = newsPublicationRepository.getById({
    id,
    locale,
    allowFallback: false,
  });

  if (!record) {
    notFound();
  }

  redirect(`/${locale}/news/${record.id}/${record.slug}`);
}
```

Notes:
- Keep this route thin; do not render the article body from the ID-only path.
- Use `allowFallback: false` to preserve explicit locale state. If a locale is missing, return 404 rather than silently redirecting to English unless the product decision explicitly changes.
- Redirect to the canonical slug-bearing URL, not to a guessed slug or list page.

## Test pattern

Extend the news public route test near the existing list/detail route assertions:

```tsx
import { redirect } from 'next/navigation';
import NewsPublicIdRedirectPage from 'src/app/(tailwind)/[locale]/news/[id]/page';

vi.mock('next/navigation', () => ({
  notFound: vi.fn(() => {
    throw new Error('NEXT_NOT_FOUND');
  }),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
  // keep any existing hooks used by the tested components
}));

it('keeps the news ID-only redirect route public', () => {
  expect(fs.existsSync(path.join(process.cwd(), 'src/app/(tailwind)/[locale]/news/[id]/page.tsx'))).toBe(true);
  expect(fs.existsSync(path.join(process.cwd(), 'src/app/(legacy)/[locale]/news/[id]/page.tsx'))).toBe(false);
});

it('redirects ID-only news requests to the canonical ID and slug route', async () => {
  await expect(
    NewsPublicIdRedirectPage({
      params: Promise.resolve({
        locale: Locale.EN,
        id: '14',
      }),
    }),
  ).rejects.toThrow('NEXT_REDIRECT:/en/news/14/top-50-software-ceos-of-2024');

  expect(redirect).toHaveBeenCalledWith('/en/news/14/top-50-software-ceos-of-2024');
});
```

## Verification

Preferred quick checks:
- Source-level route existence and redirect unit test for `src/__tests__/app/[locale]/news-public-route.test.tsx`.
- After deploy, verify headers:

```bash
curl -sS -I https://stage.querypie.com/en/news/14
```

Expected after deploy:
- a redirect response to `/en/news/14/top-50-software-ceos-of-2024`, or the final canonical URL returns 200 when following redirects.

## Reporting wording

State the distinction clearly:
- "The content exists; the canonical URL returns 200."
- "The reported URL is an unsupported ID-only shape, so it falls through to the catch-all and 404s."
- If implemented: "The ID-only compatibility route now resolves the record by id and redirects to the canonical id/slug URL."
