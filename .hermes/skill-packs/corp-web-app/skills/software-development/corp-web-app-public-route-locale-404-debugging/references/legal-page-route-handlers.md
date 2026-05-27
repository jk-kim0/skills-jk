# Legal page route-handler replacement notes

Context: corp-web-app legal shortcuts such as `/terms-of-service`, `/en/terms-of-service`, `/privacy-policy`, and `/:locale/privacy-policy` can be implemented either as `next.config.ts` rewrites or as App Router route handlers.

## Observed failure pattern

- `/terms-of-service` and `/en/terms-of-service` returned 404 on both stage and production.
- `/ko/terms-of-service`, `/ja/terms-of-service`, and checked privacy-policy variants returned 200.
- The old English rewrite destination `/terms-of-service-en` returned 404.
- The actual English content route `/en/terms-of-service-en` returned 200.

## App Router replacement shape

When the user wants to move legal shortcuts out of `next.config.ts`:

1. Remove the legal shortcuts from `next.config.ts` `rewrites`.
2. Add localized route handlers under `src/app/[locale]/.../route.ts`, for example:
   - `src/app/[locale]/terms-of-service/route.ts`
   - `src/app/[locale]/privacy-policy/route.ts`
   - `src/app/[locale]/privacy-policy-en/route.ts`
   - `src/app/[locale]/privacy-policy-ko/route.ts`
3. Add a shared helper such as `src/app/[locale]/_legal/redirect.ts` that maps locales to the backing dynamic content routes and exports `HEAD = GET` in each route handler.
4. Add unprefixed public shortcuts to `DEFAULT_LOCALE_REWRITE_PATHS` in `src/middleware.ts`, for example:
   - `/terms-of-service`
   - `/privacy-policy`
   - `/privacy-policy-en`
   - `/privacy-policy-ko`
   This lets `/terms-of-service` internally rewrite to `/en/terms-of-service` for English/default users, while non-English users can still redirect to `/:locale/...` and hit the localized route handler.
5. Add route-handler tests for locale-prefixed paths and middleware tests for unprefixed paths.
6. Update config tests to assert legal handling is no longer in `next.config.ts` rewrites.

## Comment requirement

If a redirect destination has no dedicated endpoint code under `src/app/[locale]/`, document that directly in the route helper. The correct interpretation is that these destinations are corp-web-contents-backed dynamic content paths resolved by the App Router catch-all page, not missing route-handler files.

Suggested comment:

```ts
// These redirect targets are corp-web-contents-backed dynamic content paths.
// They do not have dedicated endpoint code under src/app/[locale]/; the
// App Router catch-all page resolves them from corp-web-contents.
```

## Verification

Focused checks used successfully:

```bash
npx vitest run \
  src/__tests__/app/[locale]/legal/redirect.test.ts \
  src/__tests__/middleware.test.ts \
  src/__tests__/next-config-audit-points-route.test.ts
node scripts/ci/assert-test-groups.mjs
```

Caveat: `write_file`/`patch` lint hooks in this environment can surface broad pre-existing TypeScript declaration errors from shared `node_modules`; do not treat those as introduced by the route-handler change when focused Vitest passes.
