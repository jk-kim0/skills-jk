---
name: corp-web-app-static-route-from-dynamic-page
description: Split a corp-web-app path out of the catch-all dynamic page into a dedicated app-route page.tsx wrapper while preserving existing DynamicPage rendering and metadata.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, static-route, dynamic-page, followup-pr]
---

# corp-web-app static route from DynamicPage

Use this when a corp-web-app path currently resolves through `src/app/[...slug]/page.tsx` and the user wants a dedicated static app route like `/plans` or `/company/contact-us`.

## When to use
- The path is currently handled by `src/app/dynamic-page.tsx` through the catch-all route.
- The user wants a real `src/app/.../page.tsx` file added.
- The page content/metadata can still be sourced from the existing dynamic-page pipeline.

## Proven pattern

Example target:
- `/company/contact-us`

### 1. Confirm the current route is catch-all based
Check:
- `src/app/[...slug]/page.tsx`
- whether `generateStaticParams()` contains the slug, e.g. `{ slug: ['company', 'contact-us'] }`

### 2. Inspect an existing dedicated root route wrapper
Good references:
- `src/app/plans/page.tsx`
- `src/app/page.tsx`

Important finding:
- Not every dedicated route in this repo has its own standalone implementation.
- For routes still backed by the file/content pipeline, the safest move is a thin wrapper around `DynamicPage`, not a rewrite.

### 3. Create a dedicated app route page
Create a file such as:
- `src/app/company/contact-us/page.tsx`

Working wrapper pattern:

```ts
import DynamicPage, { generateMetadata as generateMetadataFn, PageRequest } from 'src/app/dynamic-page';
import { Metadata } from 'next';

type StaticPageProps = Pick<PageRequest, 'searchParams'>;

const createPageRequest = (searchParams: StaticPageProps['searchParams']): PageRequest => ({
  params: Promise.resolve({ slug: ['company', 'contact-us'] }),
  searchParams,
});

export const revalidate = 3600;

export async function generateMetadata({ searchParams }: StaticPageProps): Promise<Metadata> {
  return generateMetadataFn(createPageRequest(searchParams));
}

export default async function ContactUsPage({ searchParams }: StaticPageProps) {
  return DynamicPage(createPageRequest(searchParams));
}
```

Why this worked:
- keeps the existing `DynamicPage` render path intact
- keeps existing metadata behavior intact
- introduces a true static app-route `page.tsx`
- avoids a risky content migration or duplicate page implementation

### 4. Remove the path from catch-all static params
Edit `src/app/[...slug]/page.tsx` and remove the matching entry from `generateStaticParams()`.

Example removal:

```ts
{ slug: ['company', 'contact-us'] },
```

Reason:
- avoids overlap/confusion between the dedicated route and the catch-all's pre-generated slug list

## Route-local authoring variant

If the user wants the result to read like a route-authored page (similar to a marketing/contact page refactor), do not stop at the thin wrapper.
A proven next step is:

1. keep the dedicated static route file
2. move intro copy / checklist / contact details / section composition into the route directory
3. split the form into a dedicated component that owns only form UI + submission behavior
4. extract shared form/i18n config out of the old widget wrapper so both the legacy dynamic path and the new route-local path can reuse it

Important meaning of "route-local refactoring" for this repo/user:
- Do not merely move JSON data into TS/TSX object literals. That is still data-registry style and does not satisfy the request.
- Locale files such as `page.en.tsx`, `page.ja.tsx`, `page.ko.tsx` — or layout analogues like `footer.en.tsx` — should own visible copy/composition as JSX, not as giant JSON-like arrays/objects consumed by a mapper.
- If an existing component renders from `FooterType`/`HeaderType`/menu arrays, a route-local/layout-local refactor should introduce JSX section primitives or composed locale components so reviewers can see the authored navigation/copy directly in the locale TSX file.
- For footer/header chrome, a thin locale selector component plus shared rendering primitives is acceptable only if `footer.en.tsx` / `footer.ja.tsx` / `footer.ko.tsx` own the actual JSX links/copy/composition; the selector must not feed a central data map into array renderers.
- Before implementing corp-web-app route-local work, explicitly inspect the repo-local skill index and relevant skill under `.agents/skills/` (especially `.agents/skills/static-page-route-local-authoring/SKILL.md`) because this repo may not have `AGENTS.md` wiring those skills into the session automatically.

### Proven structure for `/company/contact-us`

Useful file layout for a dedicated unprefixed page entry:

- `src/app/company/contact-us/page.tsx`
- `src/app/company/contact-us/contact-us-page-section.component.tsx`
- `src/app/company/contact-us/contact-us-page-section.module.css`
- `src/components/widget/contact-sales/contact-sales-form.component.tsx`
- `src/components/widget/contact-sales/contact-sales-form.module.css`
- `src/components/widget/contact-sales/contact-sales.i18n.tsx`

Important newer variant: if the public English canonical should stay unprefixed but the implementation should live only under `src/app/[locale]/company/contact-us`, prefer the default-locale middleware rewrite pattern instead of adding `src/app/company/contact-us/page.tsx` or keeping `src/app/company/contact-us/route.ts`. See `references/default-locale-middleware-rewrite.md`.

### Practical refactor pattern

- Let `page.tsx` directly author:
  - page heading
  - lead copy
  - checklist bullets
  - contact email rows
  - left/right section composition
- Let `ContactSalesForm` own only:
  - `useSearchParams()` prefill application
  - `<Form ... />` props
  - submit success state
- Let `contact-sales.i18n.tsx` own the reused locale-specific form items, labels, helper text, and after-submit copy.
- Update the old `src/components/widget/contact-sales/contact-sales.component.tsx` to consume `getContactSalesI18n(locale)` from the shared module instead of embedding all i18n/config inline.

Why this worked well:
- the route file becomes easy to read and review like the actual page structure
- the form component stays focused on form behavior
- dynamic/MDX consumers of `ContactSales` keep working
- route-local changes no longer require pushing layout/copy concerns into generic `FormUI`

## Locale-route extension pattern

If the same path also exists under localized prefixes, mirror the dedicated static route for each locale instead of leaving only the default route split out.

For contact-us, the proven follow-up set was:
- `src/app/company/contact-us/page.tsx`
- `src/app/ko/company/contact-us/page.tsx`
- `src/app/ja/company/contact-us/page.tsx`

Working locale wrapper pattern:

```ts
const createContactUsPageRequest = (searchParams: StaticPageProps['searchParams']): PageRequest => ({
  params: Promise.resolve({ slug: ['ko', 'company', 'contact-us'] }),
  searchParams,
})
```

and equivalently for JA:

```ts
params: Promise.resolve({ slug: ['ja', 'company', 'contact-us'] })
```

Practical route-authoring rule that worked well:
- reuse shared section primitives from the default route directory, e.g.
  - `src/app/company/contact-us/contact-us-page-section.component.tsx`
- keep locale-specific intro/checklist copy inside each locale page file
- reuse the same `ContactSalesForm locale={Locale.KO}` / `Locale.JA` component so form behavior stays centralized while page authoring remains route-local

Recommended locale tests:
- `src/__tests__/app/ko/company/contact-us/page.test.tsx`
- `src/__tests__/app/ja/company/contact-us/page.test.tsx`

Keep these tests focused on:
- localized heading / lead copy
- shared contact email rows
- correct form locale prop (`data-locale="ko"`, `data-locale="ja"` in mocks)

## Layout chrome route-local authoring pattern

Use this when the target is site-wide layout chrome such as header/GNB/footer rather than an ordinary app route page, especially when the user asks to do it "like" a previously merged route-local authoring PR.

Proven corp-web-app pattern:
- Treat a referenced merged PR as a pattern source, not as a branch to update. First check PR `state`; if it is `MERGED`, inspect its final diff/merged files on latest `origin/main`, then apply the same architecture to the current open PR branch.
- Do not stop at converting JSON files into TS object modules. For route-local-style authoring, the visible locale copy/link composition should live in locale-specific TSX modules.
- For footer/header layout chrome, use sibling locale modules near `src/components/layout`, e.g.:
  - `src/components/layout/footer.en.tsx`, `footer.ja.tsx`, `footer.ko.tsx`
  - `src/components/layout/header.en.tsx`, `header.ja.tsx`, `header.ko.tsx`
- Keep the existing exported UI entry (`Header` / `Footer`) as a thin locale selector that chooses the locale module from `currentLocale`.
- Move shared layout chrome, responsive/client behavior, link wrappers, preview-navigation URL rewriting, CTA wrappers, and icon rendering into `src/components/layout/<family>/ui/<family>-primitives.component.tsx`.
- Remove obsolete `data/*.json`, `*-data.ts`, data-shape tests, and array-mapper components when their only job was rendering the old registry shape.
- Keep public navigation values unchanged unless explicitly requested; the refactor should preserve labels, hrefs, external flags, preview-navigation behavior, promotion/copy, and CTA behavior.
- If `src/app/layout.tsx` only loaded local header data to pass it into the header, remove that data-loading responsibility once the header selects locale modules itself. For `Main`, prefer a simple structural flag such as `hasHeader` over passing a removed header data object only to decide spacing.
- Add source-level regression tests that assert locale TSX modules exist, old JSON data files do not, and representative menu/copy labels are visibly present in those locale modules.
- Useful verification:
  - targeted source test, e.g. `npm run test:run -- src/components/layout/header/__tests__/header-authoring.test.ts`
  - targeted `next lint --file ...` over the edited layout/header/footer files
  - optional `tsc --noEmit --pretty false --project tsconfig.json`, but separate new diagnostics in touched layout/header/footer files from known baseline test typing errors elsewhere.

## Migration reference notes

When adding a README or migration note for a route-local/static page, colocate it with the actual page authoring files, not with the legacy/source route name.

Example from a why-querypie archived migration:
- Good: `src/app/archived/why-querypie-acp/README.md` next to `page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`, and page utilities.
- Bad: `src/app/why-querypie/README.md` after the runtime page files have moved elsewhere.

Reason:
- The README is used when future agents edit or repair the current page implementation.
- Even if the README documents legacy `corp-web-contents` source paths, its operational home should be the current route-local implementation directory.

For migration/source READMEs, include:
- current route paths and route-entry file paths
- original content and metadata source paths
- original asset source paths
- source commit or history lookup command when the upstream files are deleted on current main
- original URI path vs migrated/current URI path
- MDX-to-TSX mapping approach
- metadata and canonical handling
- asset relocation policy
- commands to inspect the historical source
- warnings about redirects or old public route revival being out of scope unless explicitly requested

## Migration provenance README

When the static/semistatic route is migrated from `corp-web-contents`, `corp-web-japan`, or historical MDX/source content into route-local `page.{locale}.tsx`, include a maintainer-facing migration provenance README in the same directory as the migrated locale authoring files. The README should capture the original source repository/path/commit, old and new URI paths, metadata/frontmatter mapping, component mapping, asset moves, and source recovery commands. Do not place this only in a legacy/stale source-style route directory; colocate it with the actual migrated page files. See `references/migration-provenance-readme.md` for the checklist and the why-querypie ACP example shape.

## Migration provenance README

When a corp-web-app route-local/static marketing page is migrated from `corp-web-contents`, `corp-web-japan`, or a historical/deleted source tree, include a migration provenance README when future edits would need the original source location or conversion method.

Rules:
- Put the README beside the actual route-local authoring files, not in a stale legacy source directory or broad docs-only location.
- For pages implemented as `page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`, colocate `README.md` in that same directory.
- Example pattern: if the page files live under `src/app/archived/why-querypie-acp/page.{en,ko,ja}.tsx`, the migration notes belong at `src/app/archived/why-querypie-acp/README.md`, not `src/app/why-querypie/README.md`.
- Include source repository/path/commit, original URI path, new target URI path, target implementation files, metadata/frontmatter conversion notes, MDX/component mapping notes, asset source/target paths, recovery commands, and future-edit scope boundaries.
- If this convention is newly established or changed, update the higher-level plan/docs in a separate docs PR rather than bundling plan governance changes into the feature PR unless the user explicitly asks to bundle them.

## Archived route index/listing pattern

Use this when maintaining `corp-web-app` archived route-local pages under `src/app/[locale]/archived/**`, especially when the user asks for an `/archived` page that lists child pages.

Core rules:
- The `/archived` index page itself may be a `noindex` link hub, but do not assume archived child pages should also be noindexed.
- Prefer `robots: 'noindex, follow'` on the index metadata so Google can skip the index page while still following child links.
- Keep the index listing in sync with actual localized child authoring files: enumerate `src/app/[locale]/archived/**/page.{en,ko,ja}.tsx`, exclude the index route itself, and include only locales that actually exist.
- Add a targeted Vitest that compares the flattened index list against the filesystem-discovered localized child routes.

Reference: `references/archived-index-listing.md`.

## Preview-route component-parity refactor pattern

Use this variant when the user asks to refactor an existing `src/app/[locale]/t/**` verification route to match a corp-web-japan equivalent page or to adopt a shared section primitive such as `simple-cta-section`.

Key rules:
- Treat the named `/<locale>/t/*` route literally as the target unless the user explicitly asks for public rollout. Do not modify sibling public routes such as `src/app/[locale]/company/certifications/**`, middleware, navigation, sitemap, redirects, or canonicals by implication.
- Inspect the corp-web-japan equivalent page and copy its component/markup structure conceptually, but adapt imports and styling to corp-web-app conventions such as CSS Modules and existing ButtonLink/FileImage/Image usage.
- If the equivalent page uses shared primitives that do not exist in corp-web-app, add class-level section primitives under `src/components/sections/**` rather than burying the structure inside the route file or a route-local CSS blob.
- Keep locale files (`page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`) as the visible authoring surfaces: headings, lead copy, trust-center text, CTA labels, and the `SimpleCtaSection` composition should be readable there.
- Remove obsolete route-local CSS and wrappers once the page moves to shared section primitives, and update any colocated README/provenance notes so they no longer point at the old widget/render path.
- Update focused source tests to assert the new primitive usage and the removal of the old route-specific/wrapper implementation, but avoid changing unrelated public-route tests unless public rollout is explicitly in scope.

Reference: `references/preview-route-component-parity-refactor.md` records a certifications verification-route example.

## Locale-prefixed `/t` home public rollout pattern

Use this variant when a corp-web-app home page has already been reviewed under `src/app/[locale]/t/page.tsx` and the user asks to publish/roll out `/ko/t` or `/{locale}/t` to the public locale-prefixed home route.

Proven minimal shape:
- add `src/app/[locale]/page.tsx` as a thin public entry
- import the reviewed locale modules from `./t/page.en`, `./t/page.ja`, and `./t/page.ko`
- generate public canonical metadata as `/${locale}` rather than `/${locale}/t`
- keep the `/[locale]/t` preview route and preview-route canonical metadata intact unless the user explicitly asks to remove it
- preserve root `/` dynamic home and production-only `/ja` redirect when they are out of scope
- update the existing `/[locale]/t/page.test.tsx` or a mirrored test to assert both the new public route contract and the preserved preview contract

Reference: `references/locale-t-home-rollout.md`.

## Middleware default-locale rewrite variant

Use this variant when the user wants to make `src/app/<path>/page.tsx` unnecessary for an English default route while preserving an unprefixed English canonical URL.

Public/runtime contract:
- English canonical remains unprefixed, e.g. `/plans`, `/plans/aip`, `/company/contact-us`.
- Non-English canonical remains locale-prefixed, e.g. `/ko/plans`, `/ja/plans`.
- Middleware rewrites allowlisted English/default requests internally to `/en/<path>` so `src/app/[locale]/<path>/page.tsx` runs with `params.locale = 'en'`.
- Middleware still redirects KO/JA users from unprefixed `/path` to `/<locale>/path`.
- Direct `/en/<path>` may render, but English metadata should still use the unprefixed canonical unless the URL policy says otherwise.

Workflow:
1. Confirm the matching `src/app/[locale]/<path>/page.tsx` exists before deleting `src/app/<path>/page.tsx` or `src/app/<path>/route.ts`.
2. Inspect the unprefixed file: if it only wraps/imports the English locale page and shared bottom/layout chrome, classify it as an English shim rather than a real content owner.
3. Check `src/middleware.ts` for an explicit default-locale rewrite allowlist entry for the path. If absent, the shim is still required for the unprefixed English URL.
4. Add the route to an explicit middleware allowlist; do not rewrite all unprefixed paths globally.
5. Apply the rewrite before `rewriteRequest(request)` so internal `baseUrl` is still added once.
6. Delete redundant unprefixed page/handler files only after tests cover the new middleware behavior.
7. Update metadata and legacy query redirects so the public English target remains unprefixed and internal `baseUrl` does not leak.
8. Update docs/inventories that still claim `src/app/<path>/page.tsx` or route-specific handlers own the route.

Reference: `references/default-locale-middleware-rewrite.md`.

## Verification

Additional references:
- `references/repo-local-skills-and-route-local-authoring.md` records the correction that corp-web-app route-local authoring requires visible locale TSX/JSX composition, not merely JSON-to-object conversion, and notes the `.agents/skills/` discovery pitfall.
- `references/route-local-shared-section-style-followups.md` records the pattern for small visual follow-ups on route-local pages: change the shared section primitive CSS when the user asks for common-component style changes, keep locale page files content-focused, and assert the CSS contract in a lightweight source test.

Minimum verification without running a dev server:
Minimum verification without running a dev server:
1. read the new `page.tsx` and confirm it hardcodes the intended slug
2. confirm the slug was removed from `src/app/[...slug]/page.tsx`
3. if route-local authoring was requested, confirm intro/contact/layout copy now lives in the route directory rather than only inside a shared widget
4. if localized variants are in scope, confirm matching dedicated locale route files exist and each passes the correct localized slug to `DynamicPage`
5. add targeted tests for:
   - the dedicated form component (query-prefill + `whiteBackground` / form props)
   - the route page (intro copy, contact emails, route-local composition)
   - locale route pages when added
6. push to the existing PR branch and rely on CI unless the user explicitly requests local dev-server validation

### Important test pitfall found

When testing a new static route page that imports `generateMetadata` from `src/app/dynamic-page`, Vitest can fail early on transitive imports such as `remark-gfm` from `dynamic-page.tsx`, especially in worktree environments.

For route-level authoring tests that only need to verify page composition, mock `src/app/dynamic-page` before importing the route module:

```ts
vi.mock('src/app/dynamic-page', () => ({
  generateMetadata: vi.fn(),
  default: vi.fn(),
}));
```

This keeps the test focused on route-local authoring and avoids unrelated dependency-resolution failures.

## Pitfalls

0. When refactoring or rebuilding a corp-web-app internal/index page, preserve existing internal inventory unless the user explicitly names removals.
   - Do not infer that old demo/sample entries should disappear just because the UI is being rewritten.
   - Before finalizing an internal index, inspect existing route files and stage/current route behavior for named legacy entries.
   - In the internal index case, `Sample Article` should be restored as locale-aware links (`/en/internal/sample-article`, `/ko/internal/sample-article`, `/ja/internal/sample-article`) when requested, while `Sample Pricing Plans` may need to point all locales at the actually supported route (`/en/internal/plans`) if the localized route wrappers still `notFound()` for KO/JA.
   - English-only internal examples such as `usage`, `key-values`, `risks`, `main-feature-description`, `killer-features`, and `compare-table` should still be visible from KO/JA internal indexes when the user asks to show all available subpages. Link those cards to the existing English route (`/en/internal/...`) instead of hiding them or linking to known 404 localized routes.
   - Verify the intended route matrix against stage/current route behavior when the user provides or requests 200/404 evidence: keep locale-specific links only for routes that actually return 200, and use an English fallback link for English-only examples if visibility matters more than localization.
   - Update route-local index tests to assert both restored entries and intentionally removed entries so future UI rewrites do not silently drop inventory. Include tests that KO/JA indexes expose English-only examples via `/en/internal/...` and do not point at known `/ko/internal/...` or `/ja/internal/...` 404 routes.
   - Do not conflate a removed index label with a removed live route. In the internal index follow-up, `MDX Preview` / `Live MDX editor` stayed removed, but the live `/{locale}/internal/preview` child route needed to be restored under a neutral `Preview Route Index` entry. See `references/internal-index-mdx-guide-links.md`.
   - Detailed fallback-link notes for English-only internal pages live in `references/internal-index-locale-fallback-links.md`. 
   - For partially localized internal routes, keep the index useful in every locale while avoiding dead links: verify which locale paths return 200/404, then link each locale index to an actually supported route. If a page exists only at `/en/internal/<slug>`, expose that card from KO/JA indexes too, but point KO/JA cards at `/en/internal/<slug>` rather than nonexistent `/ko` or `/ja` routes. Add tests that assert both the restored cross-locale visibility and the absence of known 404 locale hrefs. See `references/internal-index-partial-locale-links.md`.

1. Do not rewrite the page UI unless the user asked for a new implementation.
   - If the page is already rendered correctly through `DynamicPage`, use a wrapper.

2. Do not leave the old catch-all static param entry in place.
   - The dedicated route should own that path.

3. Do not start a local dev server unless the user explicitly requested it.
   - For this repo/user workflow, prefer commit/push and CI.

4. In PR follow-up work, use a fresh worktree on the existing PR branch and push back to the same branch.

5. Do not introduce dynamic product routes when the requested reference pattern uses explicit directories.
   - If the user says to follow the corp-web-japan `/plans/aip` and `/plans/acp` implementation, create explicit app route directories such as `src/app/plans/aip/page.tsx`, `src/app/plans/acp/page.tsx`, `src/app/[locale]/plans/aip/page.tsx`, and `src/app/[locale]/plans/acp/page.tsx`.
   - Do not use `src/app/plans/[product]/page.tsx` or `src/app/[locale]/plans/[product]/page.tsx` for that request, even if the implementation would be smaller.
   - Keep legacy query compatibility such as `/plans?aip` and `/plans?acp` by redirecting from the index page while preserving unrelated query parameters.

6. Do not treat `route.ts` as the default compatibility endpoint for public route-local pages.
   - For static/semistatic marketing routes that have moved to route-local i18n authoring, the route-local contract is `page.tsx` as thin framework entry plus `page.{locale}.tsx` as authoring surfaces.
   - A public compatibility redirect like `/company/contact-us` -> `/<locale>/company/contact-us` may still be required, but a standalone `src/app/company/contact-us/route.ts` can be an awkward leftover once the page is route-local.
   - Prefer reviewing whether it should become a `src/app/company/contact-us/page.tsx` redirect entry, with tests updated away from direct `GET` route-handler imports, rather than preserving a route handler just because it already exists.

## Typical commit message

```bash
git commit -m "fix: contact-us를 static app route로 분리"
```
