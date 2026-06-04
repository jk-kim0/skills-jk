# App Router locale route shadowing during public route rollout

## Trigger

Use this reference when a `corp-web-app` preview/public route rollout adds or moves a route under `src/app/(tailwind)/[locale]/**`, especially collection routes such as `/<locale>/news`.

## Symptom

A legacy or public unprefixed route such as `/company/news` returns 404 even though related locale-prefixed routes work.

Useful deployed-response evidence:

```bash
curl -sS -o /dev/null -D - "$URL/company/news" \
  | awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^x-matched-path:/ || /^location:/ || /^set-cookie:/ {print}'
```

If the response includes `x-matched-path: /[locale]/news`, Next.js matched `/company/news` as:

```text
/[locale]/news
locale = company
```

Then the route-local locale parser rejects `company` and calls `notFound()`.

## Root cause pattern

App Router dynamic locale routes can shadow older unprefixed/catch-all routes. For example, adding `src/app/(tailwind)/[locale]/news/page.tsx` makes `/company/news` look like a valid structural match for `/[locale]/news` before the legacy catch-all gets a chance to render it.

This often appears after a `/<locale>/t/<family>` preview route is promoted to `/<locale>/<family>` public route.

## Checks

1. Compare exact paths, do not substitute redirected paths:
   - `/company/news`
   - `/en/company/news`
   - `/ko/company/news`
   - `/ja/company/news`
   - active preview path if one exists, e.g. `/en/t/company/news`
2. Inspect `x-matched-path` for each response.
3. Inspect `src/middleware.ts`:
   - `DEFAULT_LOCALE_REWRITE_PATHS`
   - `DEFAULT_LOCALE_REWRITE_PREFIXES`
4. Inspect the route tree for new dynamic route conflicts under `src/app/(tailwind)/[locale]/**`.
5. Inspect legacy catch-all routes such as `src/app/(legacy)/[...slug]/page.tsx` when an unprefixed route used to work.

## Fix options

Smallest compatibility fix:

- Add the affected unprefixed default-English path, e.g. `/company/news`, to `DEFAULT_LOCALE_REWRITE_PATHS` so middleware rewrites it to `/en/company/news` before App Router can misinterpret `company` as a locale.

Legacy-route compatibility fix:

- If the user explicitly asks for a route handler in the legacy route group, add concrete handlers under `src/app/(legacy)/**` for every requested legacy path shape instead of relying only on middleware.
- For an unprefixed legacy alias such as `/company/news -> /news`, add `src/app/(legacy)/company/news/route.ts`, implement `GET(request: Request)` with `NextResponse.redirect(targetUrl, { status: 307 })`, set `targetUrl.pathname = '/news'`, and preserve existing query parameters by mutating `new URL(request.url)` rather than constructing a bare string.
- For locale-prefixed aliases such as `/{locale}/company/news -> /{locale}/news`, add `src/app/(legacy)/[locale]/company/news/route.ts` and replace only the suffix, e.g. `targetUrl.pathname = targetUrl.pathname.replace(/\/company\/news\/?$/, '/news')`, so `/ko/company/news?utm=1` becomes `/ko/news?utm=1`.
- Export `HEAD = GET` so HEAD probes and link checkers get the same redirect behavior.
- Add focused route-handler tests for GET, HEAD, and query-string preservation for both unprefixed and locale-prefixed handlers. Keep test paths mirrored under `src/__tests__/app/.../redirect.test.ts` so repo CI test-group assignment recognizes them as routing tests.
- This kind of compatibility redirect is a cross-route routing fix; when discovered during an unrelated feature PR, split it into a separate PR unless the user explicitly asks to include it in the feature PR.

Full public rollout fix:

- Move the intended page to an explicit locale-prefixed public route, e.g. `src/app/(tailwind)/[locale]/company/news/page.tsx`.
- Keep `/company/news` wired through default-English middleware rewrite to `/en/company/news`.
- Update preview navigation mappings and tests alongside the route move.

## Test coverage to add or verify

- Middleware test for `/company/news` with English Accept-Language expecting rewrite to `/en/company/news`.
- For route-handler redirects, add a focused test that imports the handler and verifies GET, HEAD, and query-string preservation.
- Name redirect tests so the repo CI test-group matcher assigns them to routing, e.g. `src/__tests__/app/company/news/redirect.test.ts`; avoid one-off names like `company-news-redirect-route.test.ts` that `scripts/ci/assert-test-groups.mjs` treats as unassigned.
- Route existence/rendering test for the intended public page route.
- A deployed smoke check that confirms `/company/news` no longer reports `x-matched-path: /[locale]/news`.
