# Company news legacy redirect query-string handling

Use when changing the legacy company news redirect routes in `corp-web-app`:

- Unprefixed route: `src/app/(legacy)/company/news/route.ts`
- Locale-prefixed route: `src/app/(legacy)/[locale]/company/news/route.ts`
- Mirrored tests:
  - `src/__tests__/app/company/news/redirect.test.ts`
  - `src/__tests__/app/[locale]/company/news/redirect.test.ts`

## Query-string removal pattern

These route handlers create a `URL` from `request.url` and mutate `pathname`. That preserves the original `search` by default. If the redirect target must not carry query parameters, explicitly clear `search` before returning the redirect:

```ts
const targetUrl = new URL(request.url);
targetUrl.pathname = '/news';
targetUrl.search = '';

return NextResponse.redirect(targetUrl, { status: 307 });
```

For the locale-prefixed variant, keep the locale-preserving pathname replacement and then clear `search`:

```ts
const targetUrl = new URL(request.url);
targetUrl.pathname = targetUrl.pathname.replace(/\/company\/news\/?$/, '/news');
targetUrl.search = '';
```

## Verification

Run the focused redirect tests rather than a full build unless explicitly requested:

```bash
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null && \
  npx vitest run \
    src/__tests__/app/company/news/redirect.test.ts \
    src/__tests__/app/'[locale]'/company/news/redirect.test.ts
```

Update test case wording and expected `location` headers from “preserves query parameters” to “drops query parameters” when the intended behavior is to strip query strings.