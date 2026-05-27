# Production-only root redirect pattern

Use this when a corp-web-app root-level route such as `/ja` must redirect externally on production, but staging/preview/test environments should still render the site's own page through the normal App Router/catch-all flow.

## Context

A dedicated App Router route handler like `src/app/ja/route.ts` applies in every environment. If it unconditionally returns `NextResponse.redirect('https://querypie.ai/', 307)`, then `stage.querypie.com/ja` and preview deployments cannot show the local Japanese root page.

## Safer pattern

1. Remove the unconditional route handler for the root path.
   - Example: delete `src/app/ja/route.ts` when its only job is environment-agnostic external redirect.
2. Add the redirect to `src/middleware.ts` behind the existing production gate.
   - corp-web-app already exposes `src/utils/env/is-production`, which checks `process.env.VERCEL_TARGET_ENV === 'production'`.
3. Match the exact root path only.
   - Use `request.nextUrl.pathname === '/ja'`, not `startsWith('/ja')`, so `/ja/...` pages keep rendering normally.
4. Place the redirect before the normal locale/default rewrite logic.
5. Add middleware tests for both branches:
   - production `/ja` redirects to `https://querypie.ai/`
   - stage-like `/ja` has no `location` header and rewrites through the normal local rendering path with `baseUrl` preserved.

## Example

```ts
if (request.nextUrl.pathname === '/ja' && isProduction()) {
  return NextResponse.redirect('https://querypie.ai/', 307);
}
```

## Test harness notes

For `src/__tests__/middleware.test.ts`, keep `isProduction` mock state mutable so individual tests can exercise production and non-production behavior in one suite:

```ts
const envMock = vi.hoisted(() => ({
  isProduction: false,
}));

vi.mock('src/utils/env/is-production', () => ({
  default: () => envMock.isProduction,
}));

beforeEach(() => {
  envMock.isProduction = false;
});
```

If tests need to emulate stage, allow `createRequest` to accept an `origin` parameter so the expected `x-middleware-rewrite` includes `https://stage.querypie.com/...` rather than the default production host.

## Verification

Run the narrow middleware test instead of a dev server:

```bash
npx vitest run src/__tests__/middleware.test.ts
```

Also verify the PR file list stays narrow: `src/middleware.ts`, `src/__tests__/middleware.test.ts`, and the removed unconditional route handler if applicable.
