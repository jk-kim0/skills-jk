# Locale-prefixed `/t` home rollout pattern

Use this reference when a corp-web-app route-local home page has already been reviewed under `src/app/[locale]/t/page.tsx` and the user asks to publish or roll it out as the public locale-prefixed home route.

## Scenario

The reviewed implementation lives under:

- `src/app/[locale]/t/page.tsx`
- `src/app/[locale]/t/page.en.tsx`
- `src/app/[locale]/t/page.ja.tsx`
- `src/app/[locale]/t/page.ko.tsx`

The rollout target is the public locale-prefixed route:

- `/en`
- `/ja`
- `/ko`

The root `/` dynamic home and any production-only `/ja` redirect may still be intentionally unchanged.

## Proven minimal rollout shape

Add `src/app/[locale]/page.tsx` as a thin public entry that reuses the reviewed locale modules from `./t/page.{locale}`:

```tsx
import type { Metadata } from 'next';
import type React from 'react';
import { notFound } from 'next/navigation';
import HomeEnglishPage, { createHomeMetadata as createEnglishHomeMetadata } from './t/page.en';
import HomeJapanesePage, { createHomeMetadata as createJapaneseHomeMetadata } from './t/page.ja';
import HomeKoreanPage, { createHomeMetadata as createKoreanHomeMetadata } from './t/page.ko';
import { Locale } from 'src/models/locale';

export const revalidate = 3600;

type PageProps = {
  params: Promise<{ locale: string }>;
};

type HomePageEntry = {
  component: () => React.ReactElement;
  createMetadata: (canonical: string) => Metadata;
};

const homePages: Record<Locale, HomePageEntry> = {
  [Locale.EN]: { component: HomeEnglishPage, createMetadata: createEnglishHomeMetadata },
  [Locale.JA]: { component: HomeJapanesePage, createMetadata: createJapaneseHomeMetadata },
  [Locale.KO]: { component: HomeKoreanPage, createMetadata: createKoreanHomeMetadata },
};

function parseHomeLocale(value: string): Locale | null {
  if (value === Locale.EN || value === Locale.JA || value === Locale.KO) return value;
  return null;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale: localeParam } = await params;
  const locale = parseHomeLocale(localeParam);
  if (!locale) return {};
  return homePages[locale].createMetadata(`/${locale}`);
}

export default async function HomePage({ params }: PageProps) {
  const { locale: localeParam } = await params;
  const locale = parseHomeLocale(localeParam);
  if (!locale) notFound();
  const LocalePage = homePages[locale].component;
  return <LocalePage />;
}
```

## Test pattern

Update the existing `/[locale]/t/page.test.tsx` (or add a mirrored test if one does not exist) to cover both contracts:

- The new public `src/app/[locale]/page.tsx` renders the same reviewed EN/JA/KO page content.
- Public metadata canonicals are `/en`, `/ja`, and `/ko`.
- The preview `/[locale]/t` metadata remains route-specific, e.g. `/ko/t`, so the review entrypoint still identifies itself correctly.
- Existing root dynamic home and production-only `/ja` redirect remain unchanged if they are intentionally out of scope.

Example assertions:

```tsx
import HomePage, { generateMetadata as generateHomeMetadata } from 'src/app/[locale]/page';
import HomePreviewPage, { generateMetadata as generatePreviewMetadata } from 'src/app/[locale]/t/page';

render(await HomePage({ params: Promise.resolve({ locale: 'ko' }) }));
expect(screen.getByRole('heading', { name: 'AI That Gets How You Work' })).toBeInTheDocument();

await expect(generateHomeMetadata({ params: Promise.resolve({ locale: 'ko' }) })).resolves.toMatchObject({
  alternates: { canonical: '/ko' },
});

await expect(generatePreviewMetadata({ params: Promise.resolve({ locale: 'ko' }) })).resolves.toMatchObject({
  alternates: { canonical: '/ko/t' },
});
```

## Pitfalls

- Do not delete or rename the `/[locale]/t` preview route automatically; keep it if reviewers may still need comparison URLs.
- Do not change root `/` dynamic home or production-only `/ja` redirect unless the user explicitly includes them in rollout scope.
- Do not start a dev server for this user's repo workflow unless explicitly requested; run the targeted Vitest and rely on CI/preview deploy after push.
- Keep the rollout PR narrow: one public route entry plus the route contract test is usually enough when the user has already completed UI parity verification.
