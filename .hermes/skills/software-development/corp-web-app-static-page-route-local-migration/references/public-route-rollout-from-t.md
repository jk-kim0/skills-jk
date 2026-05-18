# Public route rollout from `/t` verification routes

Session pattern: corp-web-app about-us was already implemented and reviewed under
`src/app/[locale]/t/company/about-us/**`. The rollout PR promoted it to the
public route and added a reusable repo guide at `docs/public-route-rollout.md`.

Use this as the concrete checklist when publishing another static/semistatic
route-local verification page.

## Files commonly touched

- Move route implementation:
  - from `src/app/[locale]/t/<route>/**`
  - to `src/app/[locale]/<route>/**`
- `src/lib/internal-preview-routes.ts`
  - remove the static `/t/<route>` preview listing.
- `src/lib/preview-navigation.ts`
  - remove the mapping that rewrites the public path to the `/t` path.
- `src/lib/__tests__/preview-navigation.test.ts`
  - assert the promoted public path stays public when preview navigation is on.
- `src/app/[...slug]/page.tsx`
  - remove any legacy catch-all static-param entry for the promoted route.
- `src/middleware.ts`
  - add the unprefixed public path to `DEFAULT_LOCALE_REWRITE_PATHS` when the
    implementation lives under `src/app/[locale]/...` and English `/route`
    should internally render `/en/route`.
- Route-local tests under `src/__tests__/app/**`
  - update imports/source reads from `[locale]/t/<route>` to `[locale]/<route>`.
  - change the legacy dynamic-page assertion from present-before-release to
    absent-after-release.
- Route README/provenance files
  - update target routes and implementation paths to the public location.

## About-us example

The about-us rollout made these changes:

- `git mv src/app/[locale]/t/company/about-us src/app/[locale]/company/about-us`
- Removed `{ slug: ['company', 'about-us'] }` from
  `src/app/[...slug]/page.tsx`.
- Added `/company/about-us` to `DEFAULT_LOCALE_REWRITE_PATHS` and tested that
  English `/company/about-us` rewrites internally to `/en/company/about-us`.
- Removed the about-us preview route from `src/lib/internal-preview-routes.ts`.
- Removed the `/company/about-us` preview-navigation mapping so header/footer
  public links no longer become `/en/t/company/about-us`.

## Verification used

Targeted checks were enough; no local dev server was started:

```bash
npx vitest run \
  src/__tests__/app/company-about-us-route-local.test.tsx \
  src/__tests__/middleware.test.ts \
  src/lib/__tests__/preview-navigation.test.ts

npx vitest run src/__tests__/app/[locale]/internal/preview/page.test.tsx

git diff --check
```

## Pitfalls

- Do not leave preview-navigation pointing at a deleted `/t` route; header/footer
  links can keep sending reviewers to a now-removed endpoint.
- Do not keep the route in `src/app/[...slug]/page.tsx` static params after the
  dedicated public App Router route exists, or ownership stays ambiguous.
- Do not add compatibility redirects for removed `/t/*` endpoints by default;
  `/t` routes are verification entrypoints unless the user explicitly asks to
  preserve one.
- Keep the authoring files untouched except for path/provenance changes. A
  rollout PR should not refactor already-reviewed copy into a different shape.
