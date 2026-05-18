# Default-locale rewrite wrapper removal

Use this reference when a corp-web-app static/semistatic page already has a real `src/app/[locale]/<route>/page.tsx` implementation and the remaining `src/app/<route>/page.tsx` file is only an unprefixed English wrapper.

## Durable pattern

For unprefixed English public URLs such as `/company/certifications`, do not keep a duplicate English wrapper route solely to preserve the public URL. Prefer:

1. Add the unprefixed path to `DEFAULT_LOCALE_REWRITE_PATHS` in `src/middleware.ts`.
2. Add/update middleware tests proving the request keeps `location === null` and rewrites internally to `/en/<route>` through `x-middleware-rewrite`.
3. Delete the wrapper `src/app/<route>/page.tsx`.
4. Update route-local page tests so EN rendering and metadata are tested through `src/app/[locale]/<route>/page.tsx` with `Locale.EN` params.
5. Update the route migration README/provenance note to say the unprefixed URL is preserved through default-locale middleware rewrite.

## Concrete example

PRs from the 2026-05-18 certifications work:

- Implementation PR: removed `src/app/company/certifications/page.tsx`, added `/company/certifications` to `DEFAULT_LOCALE_REWRITE_PATHS`, and updated route/middleware tests.
- Docs PR: added `docs/default-locale-route-refactoring.md` as a standalone Korean guide for this class of refactor.

Key test shape:

```ts
it('rewrites default English certifications to the internal /en route', async () => {
  const response = await middleware(
    createRequest({
      pathname: '/company/certifications',
      acceptLanguage: 'en-US,en;q=0.9',
    }),
  );

  expect(response.headers.get('location')).toBeNull();
  expect(response.headers.get('x-middleware-rewrite')).toBe(
    'https://www.querypie.com/en/company/certifications?baseUrl=https%3A%2F%2Fwww.querypie.com',
  );
});
```

## Pitfalls

- Do not delete the unprefixed wrapper before adding middleware rewrite; otherwise the request can fall through to the catch-all dynamic page and 404.
- Treat this as rewrite, not redirect: the browser URL remains unprefixed while the internal route is `/en/...`.
- Do not change non-English locale redirect behavior as part of this cleanup.
- Keep docs-only guide updates in a separate PR when the user asks for a separate documentation PR.
