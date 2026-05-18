# corp-web-japan GA implementation detail

Session-specific reference for adding hardcoded GA4 tracking to `corp-web-japan`.

## Final GA ID

`G-DGKPWV2DP2`

## Repo-specific decisions

- Use a code constant, not Vercel env vars or `NEXT_PUBLIC_*`.
- Reuse `src/lib/is-production.ts` for production-only loading.
- Place the loader under `src/components/analytics/google-analytics.tsx`.
- Place App Router navigation tracking under `src/components/analytics/google-analytics-page-view-tracker.tsx`.
- Mount `<GoogleAnalytics />` once in `src/app/layout.tsx` inside `<body>`.
- Keep the GA config call responsible for the initial page view.
- Have the client tracker skip its first render and emit `page_view` only after App Router pathname/search changes.

## CI lesson

This repo enforces test grouping through `scripts/ci/assert-test-groups.mjs`. When adding `tests/src/components/analytics/google-analytics.test.mjs`, also add a matcher under `scripts/ci/test-groups.mjs` (the `assetsShell` group was suitable here) or Smoke fails even if the targeted test and typecheck pass.

## Verification used

- `node --test tests/src/components/analytics/google-analytics.test.mjs`
- `npm run typecheck`
- `npm run test:smoke`
