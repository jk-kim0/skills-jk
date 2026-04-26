---
name: corp-web-v2-solutions-parity
description: Migrate the missing QueryPie Solutions parity area into corp-web-v2 by porting legacy AIP/ACP solution families, multilingual MDX content, route-aligned assets, navigation links, tests, and Draft PR verification.
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

For corp-web-v2 Solutions parity, the reusable default is:
- implement the canonical `/solutions/**` pages
- migrate multilingual MDX content and route-aligned public assets
- update GNB/header/footer links to canonical Solutions URLs
- exclude placeholder redirects and legacy alias redirects unless the user explicitly asks for them

Reason:
- for this repo, the user preferred a clean pre-launch migration PR without redirect policy mixed in
- redirect analysis and rollout are better handled as a separate follow-up if ever needed

## Recommended repo workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Read the migration wiki page and inspect current placeholders in `src/constants/navigation.ts`.
3. Confirm whether current work belongs on a fresh branch or an existing PR branch.
4. Use TDD:
   - route registry tests first
   - loader tests first
   - navigation tests first
   - MDX component behavior tests for custom solution widgets
5. After implementation, run:
   - `npm run test:run`
   - `npm run typecheck`
   - `npm run build`
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

### 2) Use one canonical dynamic App Router page

Implement a single page for canonical solution rendering:
- `src/app/[locale]/solutions/[[...slug]]/page.tsx`

Responsibilities:
- validate locale
- resolve slug via route registry
- load metadata + MDX source
- render with solution-specific MDX components
- `notFound()` for unknown slugs

### 3) Reuse legacy MDX content directly

Copy legacy source into:
- `src/content/solutions/**`

Expected layout:
- `src/content/solutions/<family>/<optional-child>/<locale>/meta.json`
- `src/content/solutions/<family>/<optional-child>/<locale>/content.mdx`

Use corp-web-contents as the source of truth for content.

### 6) Build a dedicated solutions loader

A simple file-based loader is enough, but one important rule was learned:
- fallback to English only on `ENOENT`
- do NOT swallow all filesystem errors

If locale file is missing, try `en`.
If there is another error like permission or transient I/O error, rethrow it.

This avoids masking real production failures.

### 7) Implement a lightweight solutions-specific MDX component layer

Legacy solutions MDX used many custom tags. A full 1:1 port of corp-web-app widgets was unnecessary.
A lightweight/fallback renderer in `src/features/solutions/mdxComponents.tsx` was sufficient.

Tags encountered in legacy solutions MDX:
- `Box`
- `CenterSection`
- `DarkBadge`
- `FileImage`
- `Integrations`
- `IntroducingQueryPie`
- `KeyFeature`
- `KillerFeature`
- `KillerFeatureCategory`
- `KillerFeatures`
- `LearnMoreLink`
- `Link`
- `LottiePlayer`
- `MainFeatureDescription`
- `SplitView`
- `SplitView.View`
- `StaticBody`
- `StaticH1`
- `StaticH2`
- `StaticH4`
- `StaticHeader`
- `ThreeColumnList`
- `ThumbnailYoutube`
- `Youtube`

Important practical choices:
- localize internal hrefs with `getLocalePath()`
- keep external links external
- use graceful fallback for `LottiePlayer`
- render `Integrations` from props and `?category=` query string
- convert `public/...` asset props into `/...` URLs
- simple marker-component approach works for `KillerFeatures` trees

### 8) Update navigation/footer links to canonical solutions URLs

Do not leave Solutions menu/footer pointing at placeholders.
Use canonical href generation from the route registry.

## Tests worth adding

Recommended test files:
- `src/features/solutions/routes.test.ts`
- `src/features/solutions/loader.test.ts`
- `src/features/solutions/mdxComponents.test.tsx`
- `src/constants/navigation.test.ts`

Verify at minimum:
- canonical entry count and slug lookup
- placeholder -> canonical mapping
- alias -> canonical mapping
- locale-aware href generation
- loader locale fallback to EN on `ENOENT`
- loader rethrows non-`ENOENT` errors
- internal MDX links get locale prefix
- integrations category filtering works
- navigation/footer now use canonical solutions paths

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
