# Header/GNB local data implementation notes (corp-web-app PR #660)

Session task: apply the same change as `https://github.com/querypie/corp-web-app/pull/657` to GNB/header, specifically using local files rather than remote files.

## Baseline facts

- PR #657 was already merged into `origin/main`.
- Footer local-data pattern on main:
  - `src/components/layout/footer/footer-data.ts`
  - `src/components/layout/footer/data/en.json`
  - `src/components/layout/footer/data/ja.json`
  - `src/components/layout/footer/data/ko.json`
  - `src/components/layout/footer/__tests__/footer-data.test.ts`
- `src/app/layout.tsx` still fetched header data remotely via:
  - `fileQuery.getLayoutData<HeaderType>(FileType.HEADER, locale)`
- Cookie banner still used remote layout data and was intentionally left unchanged.

## Remote data recovery technique

The current remote file metadata was available at:

```bash
python3 - <<'PY'
import urllib.request,json
url='https://www.querypie.com/api/data?branch=main'
with urllib.request.urlopen(url,timeout=30) as r:
    data=json.load(r)
for f in data.get('files',[]):
    if f.get('pathname','').startswith('main/layout/') and f.get('pathname','').endswith('/header.json'):
        print(f['pathname'], f.get('url'))
PY
```

The session found:

- `main/layout/ja/header.json`
- `main/layout/ko/header.json`
- `main/layout/en/header.json`

Each `url` was downloaded and written to:

- `src/components/layout/header/data/en.json`
- `src/components/layout/header/data/ja.json`
- `src/components/layout/header/data/ko.json`

## Code shape used

Added `src/components/layout/header/header-data.ts` mirroring footer:

```ts
import { Locale } from 'src/models/locale';
import { HeaderType } from 'src/models/layout-data';

import enHeaderData from './data/en.json';
import jaHeaderData from './data/ja.json';
import koHeaderData from './data/ko.json';

const headerDataByLocale: Record<Locale, HeaderType> = {
  [Locale.EN]: enHeaderData as HeaderType,
  [Locale.JA]: jaHeaderData as HeaderType,
  [Locale.KO]: koHeaderData as HeaderType,
};

const getHeaderData = (locale: Locale): HeaderType => headerDataByLocale[locale] ?? headerDataByLocale[Locale.EN];

export default getHeaderData;
```

Updated `src/app/layout.tsx` to:

- import `getHeaderData`
- remove `HeaderType` import
- remove `FileType.HEADER` from the `Promise.all`
- set `const headerData = getHeaderData(locale);`
- leave `withPreviewNavigation(...)` wrapping unchanged for header menus and mobile buttons

## Verification used

Targeted test command:

```bash
npx vitest run src/components/layout/header/__tests__/header-data.test.ts src/components/layout/footer/__tests__/footer-data.test.ts
```

Result in the session: both header and footer data tests passed.

## PR result

- Branch: `refactor/local-gnb-header-data`
- Commit: `19cab51881d71040ab1ad8a363a42b21d034a940`
- PR: `https://github.com/querypie/corp-web-app/pull/660`
- CI attached after PR creation: Deploy and Validate jobs were in progress when reported.
