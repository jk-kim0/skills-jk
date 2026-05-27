# PR 706 root contact-us redirect follow-up

Context: In corp-web-app PR 706, the user asked whether `src/app/company/contact-us/page.tsx` could be deleted and wanted the result committed, pushed, and verified on Preview Deployment.

Reusable findings:

- Deleting the unprefixed `/company/contact-us` `page.tsx` alone is unsafe. Middleware only redirects unprefixed paths for non-EN resolved locales, so default/EN traffic can fall through to legacy catch-all or 404.
- The user rejected solving this through `next.config.ts` redirects. Keep this compatibility behavior route-local under `src/app/company/contact-us/`.
- Safe replacement is `src/app/company/contact-us/route.ts` with a `GET(request)` handler returning `NextResponse.redirect(..., 307)`.
- Locale priority must match the existing middleware helper contract:
  1. `user-selected-locale` cookie (`USER_SELECTED_LOCALE_COOKIE_KEY`)
  2. browser `Accept-Language`
  3. `en` fallback
- Reuse `src/utils/middleware/get-user-locale.ts` instead of duplicating locale parsing.
- Preserve user-facing query params for form prefill, such as `inquiry=demo-request` and `product=aip`.
- Strip internal middleware query plumbing from the redirect URL, especially `BASE_URL_KEY` / `baseUrl`, before returning the redirect. Preview HTTP verification caught this leak after initial implementation.

Representative route handler shape:

```ts
import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { BASE_URL_KEY } from 'src/constants';
import getUserLocale from 'src/utils/middleware/get-user-locale';

const CONTACT_US_PATH = '/company/contact-us';

export function GET(request: NextRequest) {
  const locale = getUserLocale(request);
  const redirectUrl = request.nextUrl.clone();
  redirectUrl.pathname = `/${locale}${CONTACT_US_PATH}`;
  redirectUrl.searchParams.delete(BASE_URL_KEY);

  return NextResponse.redirect(redirectUrl, 307);
}
```

Testing pattern:

- Replace root wrapper render tests with `src/__tests__/app/company/contact-us/redirect.test.ts` that calls `GET(new NextRequest(...))` directly.
- Cover:
  - cookie `user-selected-locale=ja` wins over `Accept-Language: ko-KR,...`
  - no cookie + `Accept-Language: ko-KR,...` redirects to `/ko/company/contact-us`
  - unsupported cookie/browser language falls back to `/en/company/contact-us`
  - query params are preserved
  - `baseUrl` is removed from `Location`
- Add the new redirect test to `scripts/ci/test-groups.mjs` under the routing group, or smoke/CI can fail with unassigned tests.

Preview verification commands:

```bash
curl -sS -o /dev/null -D - \
  -H 'Cookie: user-selected-locale=ja' \
  -H 'Accept-Language: ko-KR,ko;q=0.9,en;q=0.8' \
  "$PREVIEW/company/contact-us?inquiry=demo-request&product=aip&baseUrl=https%3A%2F%2Fwww.querypie.com" \
  | awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^location:/ {print}'
```

Expected:
- HTTP 307
- Location path uses the selected locale, e.g. `/ja/company/contact-us?...`
- `inquiry` and `product` remain present
- `baseUrl` is absent

Also open the exact Preview Deployment in a browser and verify the final localized contact-us page renders and the query prefill still reaches the form.
