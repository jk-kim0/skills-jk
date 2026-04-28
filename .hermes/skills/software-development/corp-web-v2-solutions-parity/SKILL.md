---
name: corp-web-v2-solutions-parity
description: Migrate the missing QueryPie Solutions parity area into corp-web-v2 by porting legacy AIP/ACP solution families into individual static page.tsx routes, route-aligned assets, navigation links, tests, and Draft PR verification.
---

# corp-web-v2 Solutions parity migration

Use this when corp-web-v2 still links Solutions items to placeholders or is missing legacy querypie.com Solutions pages that exist in corp-web-app + corp-web-contents.

## Scope to treat as one migration unit

Do not interpret this as only three placeholder pages.

Legacy parity means these canonical route families in corp-web-v2:

- AIP
  - `/solutions/aip`
  - `/solutions/aip/usage-based-llm`
  - `/solutions/aip/mcp-gateway`
  - `/solutions/aip/fde-services`
  - `/solutions/aip/integrations`
- ACP
  - `/solutions/acp`
  - `/solutions/acp/database-access-controller`
  - `/solutions/acp/system-access-controller`
  - `/solutions/acp/kubernetes-access-controller`
  - `/solutions/acp/web-access-controller`
  - `/solutions/acp/integrations`

Treat `FDES` as the legacy `FDE Services` page, not as an independent family:
- `/fdes-not-found` -> `/solutions/aip/fde-services`

## Scope boundary learned in practice

Do not assume legacy alias redirects belong in this migration PR.

For corp-web-v2 Solutions parity, first determine which of these two targets the user wants:
- MDX-backed parity on canonical `/solutions/**` routes
- full static-page replacement where each canonical route is an individual `page.tsx` and Solutions no longer depends on MDX source/meta loaders

Current learned preference for this repo:
- if the user says Solutions content is not suitable for MDX, treat that as a request for full static-page replacement
- implement the canonical `/solutions/**` pages
- update GNB/header/footer links to canonical Solutions URLs
- exclude placeholder redirects and legacy alias redirects unless the user explicitly asks for them

Reason:
- for this repo, the user preferred a clean pre-launch migration PR without redirect policy mixed in
- the user also explicitly preferred individual static `page.tsx` routes for Solutions because most of the content is not appropriate for MDX
- redirect analysis and rollout are better handled as a separate follow-up if ever needed

## Recommended repo workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Read the migration wiki page and inspect current placeholders in `src/constants/navigation.ts`.
3. Before trusting any wiki statement about "already migrated" status, verify the actual checked-out tree and current branch tip with live repo inspection:
   - `git branch --show-current`
   - `git rev-parse HEAD`
   - search for `src/app/[locale]/solutions/**`, `src/features/solutions/**`, and `src/content/solutions/**`
   - search `src/constants/navigation.ts` for placeholder routes like `/aip-not-found`, `/acp-not-found`, `/fdes-not-found` or for a route helper such as `getSolutionHref()`
   This repo has had periods where wiki pages described a newer `origin/main` state while the current checkout/branch still reflected older placeholder-link structure.
4. Confirm whether current work belongs on a fresh branch or an existing PR branch.
5. Use TDD:
   - route registry tests first
   - static content registry tests first
   - navigation tests first when links change
   - component behavior tests only for reusable solution UI pieces that still matter after the static-page conversion
5. After implementation, run the fastest relevant verification first:
   - targeted `npm run test:run -- <changed tests>`
   - `npm run typecheck` if needed, while separating pre-existing baseline failures from your change
   - prefer PR CI for full validation when the user wants fast execution over long local verification
6. If routes were removed and typecheck still references deleted pages, clear `.next` and rerun typecheck.
7. Open a Draft PR in Korean and check CI.

## Implementation pattern that worked

### 1) Centralize route knowledge

Create a dedicated route registry, e.g. `src/features/solutions/routes.ts`, containing:
- canonical solution entry list
- helper to resolve entry by slug
- helper to build locale-aware canonical href

Keep this registry focused on canonical navigation and page lookup.
Do not bake redirect policy into it unless the user explicitly requests redirect support for the same task.

### 2) Default to individual static App Router pages when the user wants true static pages

Do not assume Solutions should keep one canonical dynamic App Router page.
If the user says the content is not suitable for MDX or explicitly asks for static pages, the reusable default is:
- remove `src/app/[locale]/solutions/[[...slug]]/page.tsx`
- create one `page.tsx` per canonical route under `src/app/[locale]/solutions/**`
- share metadata/rendering through a small helper such as `src/features/solutions/staticPage.tsx`
- keep route selection explicit at the file-system level, not through a catch-all

This matched the user expectation better than the earlier catch-all + MDX runtime approach.

### 3) Convert legacy MDX into static TSX content modules instead of rendering MDX at runtime

Use corp-web-contents MDX as migration input, not necessarily as runtime source.
A practical conversion path that worked was:
- inspect the existing MDX and note that much of it is already JSX-like component composition
- move each canonical page into locale-specific TSX modules
- reuse existing presentational components where helpful, but remove MDX loading/rendering from the request path

This preserves content structure while making the public route implementation genuinely static.

Important learned placement rule:
- do not keep locale page-body TSX under a generic `features/solutions/static-content/**` tree if the files are really page presentation
- for this repo, prefer route-aligned colocated files directly under `src/app/[locale]/solutions/**`
- mirror the route slug nesting 1:1, for example:
  - `src/app/[locale]/solutions/aip/page.tsx`
  - `src/app/[locale]/solutions/aip/content.en.tsx`
  - `src/app/[locale]/solutions/aip/content.ko.tsx`
  - `src/app/[locale]/solutions/aip/content.ja.tsx`
  - `src/app/[locale]/solutions/acp/database-access-controller/page.tsx`
  - `src/app/[locale]/solutions/acp/database-access-controller/content.en.tsx`
  - `src/app/[locale]/solutions/acp/database-access-controller/content.ko.tsx`
  - `src/app/[locale]/solutions/acp/database-access-controller/content.ja.tsx`
- for this repo's static-page preference, do not add a separate route-local `metadata.ts` by default unless the user explicitly asks for that split
- current preferred pattern for Solutions static pages is: locale-specific metadata values live in each `content.<locale>.tsx`, while `page.tsx` imports those metadata objects and keeps only the thin `generateMetadata` selection logic
- keep `page.tsx` thin in terms of rendering flow and avoid embedding large locale metadata literals there when the metadata is page-local content
- do not keep thin indirection layers like `_shared/pageHelpers.tsx` when they only hide small per-route logic; favor route-local explicitness even if 11 routes repeat short selection/render blocks
- keep only truly reusable helpers in shared locations; if a helper is just reducing a few lines of page-local code for Solutions routes, remove it instead of centralizing it
- do not introduce central page-body registries or metadata registries when the files are page-local and compare/review better in place
- keep `src/features/solutions/**` for route knowledge like canonical entry lists and href helpers, not route-local page body or route-local metadata files

Additional learned requirement:
- do not stop at replacing only the page body
- remove remaining Solutions-specific MDX/meta loader dependencies as well
- after the conversion, verify that Solutions-specific references to `content.mdx`, `meta.json`, `loadSolutionMeta`, and `loadSolutionMdxSource` are gone from the Solutions feature
- replace older tests for centralized static content / metadata registries with tests that validate each canonical route has its own colocated `content.<locale>.tsx`, `metadata.ts`, and working `generateMetadata`
### 6) Route helpers should support explicit page generation

A dedicated route registry is still useful, but after moving to individual static pages it should also support explicit page mapping.
Add helpers such as:
- helper to resolve entry by slug
- helper to resolve entry by stable route id
- helper to build locale-aware canonical href

The route id lookup simplifies static-content registries and tests.

### 7) Reuse existing UI components without keeping the MDX runtime

Even after removing runtime MDX loading, reusing `src/features/solutions/mdxComponents.tsx` or similar presentational components can still be the fastest safe path.
Important distinction learned in practice:
- reusing JSX components is fine
- keeping MDX as the route-rendering runtime is not required if the user wants static pages

So preserve useful UI building blocks, but move page composition into TSX modules and individual route files.

### 8) Update navigation/footer links to canonical solutions URLs

Do not leave Solutions menu/footer pointing at placeholders.
Use canonical href generation from the route registry.

## Tests worth adding

Recommended test files:
- `src/features/solutions/routes.test.ts`
- `src/features/solutions/staticContent.test.tsx`
- `src/features/solutions/contentComponents.test.tsx` when those reusable content components remain in use
- `src/features/solutions/solutionMetadata.test.ts` when metadata is statically inlined
- `src/constants/navigation.test.ts` when navigation or footer links change

Verify at minimum:
- canonical entry count and slug lookup
- stable route-id lookup for page generation
- locale-aware href generation
- each canonical route resolves to static content for supported locales
- internal JSX links still get locale prefix when routed through shared link components
- navigation/footer now use canonical solutions paths when touched

## Asset migration notes

Legacy solutions pages referenced assets mostly under these public directories:
- `public/aip`
- `public/acp`
- `public/products`
- `public/tutorial`
- `public/integration-icon`
- `public/key-feature-icon`
- `public/introducing-querypie`

Also copy:
- `public/assets/dac-analyzer.json` from `corp-web-app/public/assets` (not corp-web-contents)

## Verification notes

Besides tests/typecheck/build, verify representative browser paths:
- canonical page like `/solutions/aip`
- locale page like `/ko/solutions/acp`
- alias redirect like `/products/web-application-access-controller`
- placeholder redirect like `/aip-not-found`

Check browser console for JS errors.

## PR notes

For corp-web-v2, write PR title/body in Korean.
Mention explicitly if lint could not run because the repo has no lint script/config, while test/typecheck/build did pass.
