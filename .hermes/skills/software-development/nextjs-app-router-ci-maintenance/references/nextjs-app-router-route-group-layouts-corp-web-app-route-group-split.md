# corp-web-app route group split session note

Context: corp-web-app needed a PR that split App Router pages into `(legacy)` and `(tailwind)` route groups. The Tailwind group initially contained only a smoke endpoint at `/internal/tailwind`.

Key implementation decisions:

- Move `src/app/layout.tsx` to `src/app/(legacy)/layout.tsx`; keeping a top-level layout would still wrap every route group.
- Move existing page route trees under `(legacy)`, including:
  - `src/app/page.tsx`
  - `src/app/[locale]/**`
  - `src/app/[...slug]/page.tsx`
  - `src/app/search/**`
  - `src/app/cookie-preference/**`
- Keep layout-independent top-level route handlers/assets in place unless explicitly scoped:
  - `src/app/api/**`
  - `src/app/sitemap.xml/**`
  - `src/app/docs/**`
  - `src/app/wiki/**`
  - `src/app/public/**`
  - `src/app/aip/**`
  - `src/app/globals.css`, `fonts.ts`, icons
- Fix moved legacy layout imports:
  - `./globals.css` -> `../globals.css`
  - brittle relative shared component imports -> absolute `src/...` imports
- Add `src/app/(tailwind)/layout.tsx` returning its own `<html>` and `<body>`, copying only needed global providers/cookie UI/dimmed layer and excluding legacy Header/Main/Footer.
- Add `src/app/(tailwind)/internal/tailwind/page.tsx` as the smoke page.
- Update middleware so `/internal/tailwind` remains unprefixed even for non-English Accept-Language/cookie states; otherwise middleware can redirect to `/ja/internal/tailwind`, which was not the requested endpoint.
- Update source-level imports/tests from `src/app/[locale]/...` to `src/app/(legacy)/[locale]/...` where they import moved route modules.
- Avoid broad README/doc path rewrites. A broad replacement touched moved README files, but those were restored to avoid review noise.

Useful verification commands from the session:

```bash
git diff --check
npx next typegen
npm test -- --run \
  src/__tests__/middleware.test.ts \
  src/__tests__/app/route-groups-route-local.test.tsx \
  src/__tests__/app/[locale]/legal/redirect.test.ts \
  src/__tests__/app/[locale]/chat/publication/redirect.test.ts
node scripts/ci/assert-test-groups.mjs
```

Observed caveats:

- `npx next typegen` succeeded and was a good quick route-tree validation after the move. It emitted a multiple-lockfile warning in the worktree, but route types generated successfully.
- A broad `npm run test:routing` in a fresh worktree failed during CSS/PostCSS collection because `@tailwindcss/postcss` was not resolved from the worktree. Targeted route-group/middleware tests passed; rely on CI for full dependency-installed verification when the user wants to avoid local installs.
- The PR had many file renames, but the conceptual change was mostly route tree movement plus a small new Tailwind root/smoke page.
