---
name: corp-web-app-static-page-route-local-migration
description: Migrate or maintain corp-web-app static/semistatic pages as route-local App Router pages, preserving legacy source provenance, locale-specific authoring, route-aligned assets, and existing PR workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, static-page, route-local-authoring, migration, provenance]
---

# corp-web-app Static Page Route-Local Migration

Use this skill when migrating, relocating, or maintaining a static/semistatic corp-web-app marketing page as route-local App Router files, especially pages that came from legacy `corp-web-contents` / historical `contents/**` sources.

## Triggers

- User asks to migrate a static page into `src/app/**` route-local files.
- User asks to change the public route of an already migrated static page.
- User asks to move page-specific `public/**` assets into a route-aligned location.
- User asks to document migration source/provenance for a migrated page.
- User asks to delete or decommission an unused public static page or locale-prefixed static route.
- User asks to add a lightweight index/list page for migrated static routes, such as `/archived` or locale-prefixed archived pages.
- Existing PR follow-up for a route-local static page in corp-web-app.
- User asks to plan or introduce a Tailwind-based layout/header/GNB/footer alongside the existing chrome, especially when endpoints will opt in one by one.

For follow-up work on an open PR, also load `existing-pr-followup-worktree`.
If the referenced PR is already merged or closed, do not revive its branch; start a new branch and PR from latest `origin/main`.

## Core workflow

1. Confirm repository and PR state.
   - Run `pwd`, `git rev-parse --show-toplevel`, `git status --short --branch`.
   - If this is PR follow-up, check `gh pr view <number> --json state,headRefName,headRefOid,baseRefName`.
   - Use a fresh worktree or an isolated detached worktree at the PR branch head when the branch is already checked out elsewhere.
2. Locate legacy source provenance before editing.
   - Search current tree first.
   - If source is no longer present, search historical paths:
     `git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep -Ei '<page-slug>|<asset-name>'`
   - Inspect candidate historical files with `git show <rev>:<path>`.
3. Implement route-local authoring.
   - Keep `page.tsx` thin: metadata handoff, locale selection/fallback, wrapper call.
   - Put real locale copy and section order in `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` when those locales exist.
   - Use small route-local adapters or `src/components/**` only for UI/rendering details, not hidden page copy registries.
4. Align public assets with the route.
   - Move page-specific images under a route-aligned root such as `public/<route-family>/<page>/...` or the exact path requested by the user.
   - Preserve subfolders that have meaning, e.g. `benefits/`.
   - Do not accidentally move shared form/UI assets such as `public/partners/form/*` unless explicitly requested.
5. Update metadata and tests.
   - Update canonical URLs, Open Graph/Twitter image URLs, and alternate locale URLs to match the final public route.
   - Place `src/app/**/page.tsx` route tests under `src/__tests__/app/**/page.test.tsx`, mirroring the route path instead of colocating tests inside the App Router tree.
   - Avoid flat route-test names such as `src/__tests__/app/company-bounty-route-local.test.tsx`; they hide the source route and encourage inconsistent placement.
   - If one flat test covers multiple page entrypoints, split it by route when possible. Example: split a bounty-program test into `src/__tests__/app/archived/bounty-program/page.test.tsx` and `src/__tests__/app/archived/bounty-program/terms-of-use/page.test.tsx`.
   - Update/import tests to target the route-local files after relocation.
   - Prefer targeted Vitest checks for the changed route.
6. Rebase and push.
   - Before updating the PR branch, rebase onto latest `origin/main` when the PR branch is behind.
   - If the PR branch is so stale that `origin/main...HEAD` shows broad unrelated files, do not keep building on that branch. Create a clean temporary worktree from latest `origin/main`, copy or reconstruct only the intended route-local changes, run the targeted checks there, commit once, and force-with-lease that clean commit back to the same open PR branch. Verify the PR file list no longer contains unrelated stale files.
   - Use `--force-with-lease` for rewritten PR follow-up branches.
   - Verify remote head with `git ls-remote origin refs/heads/<branch>` and report CI status without long passive waits.

## Tailwind layout chrome planning

When the user asks to add Tailwind-based layout, header, GNB, or footer while keeping the existing corp-web-app chrome, treat it as a parallel site-chrome foundation and endpoint opt-in plan, not as an immediate root layout replacement.

Key rules:

- Add the new Tailwind chrome as a separate component family under `src/components/layout/**` beside the existing layout/header/footer code.
- Do not delete, rewrite, or replace the existing root layout/header/GNB/footer in the foundation PR.
- Keep Tailwind page/content migration separate from Tailwind layout chrome migration. A page can migrate its body shell first, then opt in to the new chrome in a later PR.
- Endpoint adoption should be explicit via a wrapper such as `TailwindSiteLayout` or a URL-neutral route group; do not silently switch all routes.
- Navigation targets, middleware, sitemap, canonical metadata, redirects, and CMS-managed data are forbidden scope unless explicitly requested.
- Plan root layout default replacement only after multiple endpoint-level Preview checks prove desktop header, mobile menu, GNB/dropdown behavior, footer links, sticky header spacing, reset/preflight computed styles, and mobile overflow.
- For docs-only planning updates, patch the living plan document, run `git diff --check`, and open a docs PR from a fresh latest-main worktree.

See `references/tailwind-layout-chrome-opt-in-plan.md` for the concrete plan shape and PR split.

## Decommissioning unused static routes

When the user asks to delete an unused static page such as `/{locale}/<route>` or `src/app/[locale]/<route>`, treat it as narrow public-route decommissioning, not a broad cleanup. Identify the exact route owner, delete only the requested public route files, update any explicit route inventories, and preserve similarly named internal/demo routes unless explicitly included in scope. Verify with `git diff --check` plus a post-delete search for the removed public path and route directory. See `references/decommission-unused-static-route.md` for the concrete checklist and the `key-values` pattern.

## Locale dynamic route relocation

When consolidating explicit locale directories such as `src/app/en/**`, `src/app/ko/**`, and `src/app/ja/**` into a dynamic `src/app/[locale]/**` route, preserve the unprefixed default public route as a thin EN wrapper unless the user explicitly asks to change public URL policy. Move the real authored pages to `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` under the `[locale]` route and add a thin locale dispatcher at `page.tsx`.

If the user asks whether an unprefixed English wrapper such as `src/app/<route>/page.tsx` is unnecessary after the `[locale]` route exists, first check whether the public `/<route>` URL is already preserved by `src/middleware.ts` `DEFAULT_LOCALE_REWRITE_PATHS`. If it is not, the wrapper is still routing-significant. The clean refactor is to add `/<route>` to `DEFAULT_LOCALE_REWRITE_PATHS`, add/update a middleware test proving `/<route>` rewrites internally to `/en/<route>` without redirecting, then delete the wrapper and update route tests/README provenance so tests import the `[locale]` route entry instead of the removed wrapper. See `references/default-locale-rewrite-wrapper-removal.md` for the concrete certifications pattern and test shape.

For route families preserved by middleware prefix rewrites, such as archived pages with `DEFAULT_LOCALE_REWRITE_PREFIXES = ['/archived']`, root wrapper deletion is safe only after proving every removed `src/app/archived/**/page.tsx` has a matching `src/app/[locale]/archived/**/page.tsx`, middleware still rewrites/redirects `/archived/**` correctly, and tests/docs no longer import the deleted root wrappers. Move mirrored tests to `src/__tests__/app/[locale]/archived/**` rather than leaving them under the deleted root-route mirror. See `references/archived-root-wrapper-removal.md` for the checklist and verification commands.

Important pitfall: do not leave the old explicit locale route files in place if the goal is a real relocation. In Next.js App Router, explicit static segments can continue to handle `/en/...`, `/ko/...`, and `/ja/...` instead of the new `[locale]` route. See `references/locale-dynamic-route-relocation.md` for the contact-us review pattern and verification notes.

## Locale-prefixed `/t` preview routes

When the user asks for a static page PR to work under preview review paths such as `/en/t/`, `/ja/t/`, and `/ko/t/`, treat the `/[locale]/t` directory as the route-local authoring surface, not merely as a wrapper that imports source files from elsewhere.

Pattern:

- Put the real locale-authored files under `src/app/[locale]/t/<route>/page.en.tsx`, `page.ja.tsx`, and `page.ko.tsx` (or directly under `src/app/[locale]/t/page.{locale}.tsx` for a home-page preview route).
- Keep `src/app/[locale]/t/<route>/page.tsx` thin: parse/validate `params.locale`, choose the locale module, and hand off metadata.
- If existing public route entries like `src/app/page.tsx`, `src/app/en/page.tsx`, or `src/app/ko/page.tsx` must keep working before rollout, make them thin wrappers that import from the `/[locale]/t` authoring files. Do not leave duplicate authored copies at the old route root.
- Update README/provenance notes, tests, and PR body to name the `/[locale]/t` files as the canonical review surface.
- Search for stale imports such as `src/app/page.en`, `./page.en`, or `../page.en` after moving files; old wrapper imports are a common source of broken preview deploys or misleading review structure.

This came up on a home route-local PR: creating `/[locale]/t/page.tsx` while leaving `src/app/page.{locale}.tsx` in place made preview work technically, but the authoring surface was wrong. The corrected structure moved `page.en.tsx`, `page.ja.tsx`, and `page.ko.tsx` into `src/app/[locale]/t/` and changed `src/app/page.tsx`, `src/app/en/page.tsx`, and `src/app/ko/page.tsx` into thin imports from that location. See `references/home-preview-t-authoring.md` for the concrete checklist.

## Publishing `/t` verification routes to public routes

When the user explicitly asks to remove the `/t` verification prefix and publish a route-local page, treat the work as a public route rollout, not just a directory move:

- Move `src/app/[locale]/t/<route>/**` to `src/app/[locale]/<route>/**`, including locale files, route-local components, CSS modules, and README/provenance notes.
- Keep the route-local authoring contract unchanged: thin `page.tsx`; visible locale copy and composition in `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx`; no new copy registries.
- Remove the promoted route from preview-only indexes such as `src/lib/internal-preview-routes.ts`, and update the internal preview route index test if needed.
- Remove any `src/lib/preview-navigation.ts` mapping that rewrites the public path to `/<locale>/t/<route>`, then update `src/lib/__tests__/preview-navigation.test.ts` so the promoted route remains public when preview navigation is enabled.
- If the old public path was still listed in `src/app/[...slug]/page.tsx` `generateStaticParams()`, remove that legacy dynamic-page ownership and update the route-local test to assert it is absent after public release.
- For unprefixed English public URLs handled by `src/app/[locale]/...`, add the public path to `DEFAULT_LOCALE_REWRITE_PATHS` in `src/middleware.ts` and add middleware coverage for internal `/en/...` rewriting.
- Review public navigation, canonical metadata, sitemap behavior, and redirects explicitly. Do not preserve or redirect the removed `/t/*` endpoint unless the user explicitly asks for that compatibility path.
- Prefer targeted route, middleware, preview-navigation, and internal-preview-index Vitest checks. Do not start a local dev server unless requested.

See `references/public-route-rollout-from-t.md` for the about-us rollout pattern.

## Shared Simple CTA section transfer and application

When the user asks to port a common CTA section from corp-web-japan into corp-web-app, treat it as a reusable component migration first and a page adoption second. If they ask for separate PRs, keep the component/library PR and the route usage PR separate.

Steps:

1. Inspect the source repo implementation named `SimpleCtaSection` and port the component shape into a shared corp-web-app component location; do not invent a new API unless the target repo's primitives require a small adapter.
2. Inspect `corp-web-contents` source pages such as `/ko/` and `/en/` for bottom CTA behavior above the footer before deciding a corp-web-app route-local page is complete.
3. For `/{locale}/t/` preview/home pages, ensure the Simple CTA appears as a bottom page landmark immediately before the footer/layout boundary.
4. Keep route-local copy/composition visible in the page file when route-local authoring applies; the shared component should provide reusable section layout/style, not a hidden marketing copy registry.
5. Reuse existing corp-web-app button/link primitives for the CTA action when they already match canonical visual behavior, instead of cloning nested button/icon/focus CSS from another repo.
6. Verify with targeted route/component tests and, for visual acceptance, a browser pass over the exact preview URL.

See `references/simple-cta-section-port-and-preview-application.md` for the PR split, provenance checks, and bottom-of-page verification checklist.

## Stage vs production parity after route-local conversion

When a user asks to compare a stage route-local page against the production route, verify the rendered page before changing code:

- Clear or set cookie-preference cookies consistently on both hosts. If the cookie banner overlays first-viewport content on both stage and production, treat it as shared overlay behavior, not a stage-only route regression.
- Use browser DOM geometry to quantify spacing rather than relying on screenshots alone. For example, a route-local `CenterSection paddingTopSize="lg"` can make a converted page's first card grid start about one spacing token higher than production; restoring `"xl"` can be the narrow fix.
- Compare metadata/title parity as part of static-page migration quality. Route-local rewrites can accidentally change the browser title even when visible H1 copy stays the same.
- Prefer fixing the converted route's changed spacing/metadata before touching global layout components such as cookie preference banners.

See `references/certifications-stage-production-parity.md` for a concrete certifications page comparison and fix pattern.

## Wiki status documentation

When asked to create or refresh corp-web-app route-local authoring wiki documentation, keep the wiki page Korean by default unless the user explicitly requests another language. Base the inventory on latest `origin/main`, not an in-progress branch, and keep it concise: classify static/semistatic marketing pages as route-local, preview/rollout candidate, partial/scope decision, or excluded. Do not turn the page into a full migration dashboard, and explicitly exclude MDX/publication families such as blog, whitepapers, news, events, demo details, glossary, manuals, tutorials, and introduction deck. See `references/route-local-authoring-wiki-status.md` for the recommended command sequence and page shape.

## Route-local authoring wiki and i18n status docs

When updating corp-web-app wiki pages such as `Route-Local-Authoring` or `Route-Local-Authoring-i18n`, keep the wiki Korean by default, read the latest `origin/main` implementation rather than stale wiki prose, and use the endpoint list in `Route-Local-Authoring` as the baseline for i18n status. Do not create or modify `_Sidebar.md` unless the user explicitly asks for a custom sidebar. For i18n status, do not trust `page.ko.tsx` / `page.ja.tsx` existence alone; inspect actual visible copy and mark pages that remain English-centered as not ready. See `references/route-local-authoring-wiki-i18n-status.md` for the concise workflow, status labels, and edge cases such as redirect-only pricing routes and privacy-policy content records.

## Migration README requirement

When a static page migration may need future corrections, add a colocated `README.md` next to `page.en.tsx` / `page.ko.tsx` / `page.ja.tsx`.

The README should include:

- current public route(s), including localized routes;
- current implementation files and responsibilities;
- original migration source paths for each locale;
- historical asset source paths;
- useful commit(s) for `git show <rev>:<path>` inspection;
- concise migration method, including component-name substitutions or adapter usage;
- asset mapping from old public paths to new route-aligned public paths;
- explicit exclusions for similarly named shared assets that were not moved;
- follow-up checklist for future edits.

See `references/become-a-partner-archived-route-readme.md` for a concrete pattern from PR 671.

## Pitfalls

- Do not delete similarly named internal/demo routes when decommissioning an unused public static route unless the user explicitly includes those routes. Search for both public references (`/<locale>/<route>`, `[locale]/<route>`) and internal references (`/internal/<route>`) and preserve internal index/test coverage when it points to the internal route.
- Lightweight index/list pages still need explicit route-local styling. In corp-web-app, the root layout already wraps children in `src/components/layout/main`; adding another `<main>` inside a route-local index can become a flex child that shrinks to content width. Also, global CSS resets plain `a` and `ul` styles, so plain links/lists can look like unclickable text unless styled. See `references/archived-index-route.md`.
- Do not infer that all similarly named assets are page-specific. Verify whether assets are shared by unrelated form/layout flows before moving them.
- Do not silently normalize a user-specified route spelling. If the user asks for `/archived/become-a-parter`, preserve that spelling unless they correct it.
- Do not leave old imports, canonical URLs, or OG image URLs pointing at the pre-migration route or asset path.
- Do not add `/<locale>/t/*` verification endpoints automatically when the page already exists as a public static route and the user asks to review/refactor it under route-local authoring. In that case, keep or introduce the real public route shape and refactor the existing page into route-local files instead. For plans/pricing pages specifically, prefer product-specific public routes such as `/plans/aip` and `/plans/acp` with locale-prefixed counterparts, and preserve known legacy query-string entry points such as `/plans?acp` with redirects.
- When the user says to reference the corp-web-japan plans implementation, treat the directory shape as part of the requirement: use explicit static route directories like `src/app/plans/aip/page.tsx`, `src/app/plans/acp/page.tsx`, `src/app/[locale]/plans/aip/page.tsx`, and `src/app/[locale]/plans/acp/page.tsx`. Do **not** implement this as a variable route such as `src/app/plans/[product]/page.tsx` or `src/app/[locale]/plans/[product]/page.tsx`; `[product]` hides the intended explicit route-local structure and will be rejected.
- When adding explicit plans product routes, also preserve the existing plans index entrypoints: `src/app/plans/page.tsx` and `src/app/[locale]/plans/page.tsx`. Add legacy query-string redirects at both levels so `/plans?acp`, `/plans?aip`, `/en/plans?acp`, `/ko/plans?aip`, etc. redirect to the matching explicit product route while preserving unrelated query params.
- Do not add new flat `src/__tests__/app/*-route-local.test.tsx` files for static App Router pages. Mirror the route path under `src/__tests__/app/**/page.test.tsx`; if the CI grouping script only matches the old flat pattern, update `scripts/ci/test-groups.mjs` in the same PR.
- In corp-web-app fresh worktrees, targeted Vitest can fail for CSS/PostCSS-loading suites because the worktree has no local `node_modules` and even the root checkout may lack the required package (for example `@tailwindcss/postcss`). If the user prefers CI over local installs, do not spend time installing dependencies; record the exact partial pass/failure and rely on CI after push.
- Do not use `python` blindly on macOS; this user's environment may only have `python3`.
- When a PR branch is already checked out in another worktree, a detached fresh worktree at `origin/<branch>` is acceptable for follow-up work; push `HEAD:<branch>` with force-with-lease after rebase.

## Verification

Minimum checks:

- `git status --short --branch`
- search for old route and asset references after relocation
- targeted test, e.g. `npm run test:run -- src/__tests__/app/<route-test>.test.tsx`
- `git ls-remote origin refs/heads/<branch>` after push
- `gh pr view <number> --json statusCheckRollup,headRefOid,mergeStateStatus`
