# Component Name Debug marker authoring in corp-web-japan

Use this when following up on the platform Component Name Debug capability after the overlay/control infrastructure exists but most pages show no labels.

## Core contract

- Component Name Debug labels appear only for DOM nodes with `data-component-name` markers.
- Use the helper from `src/lib/component-name-debug.ts`:
  - `componentNameDebugProps("ReactComponentName")`
- Marker names must be non-empty React-style identifiers without whitespace.
- Add markers to existing meaningful UI ownership boundaries only.
- Do not add wrapper-only components or route-local shells just to make labels appear.

## Good marker targets

Prioritize broad reviewer-useful boundaries first:

1. Common layout surfaces
   - `SiteHeader` / `SiteHeaderNav` / `SiteHeaderActions` may already exist from the base implementation.
   - Add `SiteFooter` and other persistent layout surfaces when missing.
2. Route-level page roots
   - Add markers to existing route `<main>` roots such as `HomePage`, `AICrewPage`, `AIDashiPage`.
3. Major section component roots
   - Home hero / solution overview / CTA sections.
   - Solution page hero, results, values, process, support, etc.
   - Platform pages such as AIP/FDE shell and hero sections.
4. Publication/list/detail page boundaries
   - Add markers to the existing detail page section and article/body container, e.g. `PublicationPostPage`, `PublicationPostArticle`.
   - For MDX-backed collection/list follow-ups, mark both route-level `<main>` roots and shared list sections so reviewers can identify the page and the repeated list surface:
     - route pages such as `BlogPage`, `WhitepapersPage`, `ResourcesPage`, `UseCasesPage`, `AipDemoPage`, `AcpDemoPage`, `NewsPage`, `EventsPage`, `IntroductionDeckPage`, `GlossaryPage`, `ManualsPage`
     - shared list surfaces such as `ResourceListHeroSection`, `ResourceListContentSection`, `ResourceListLoadMore`, `ResourceListItems`, `ResourceListItemCard`, `NewsListSection`, `NewsArticleLoadMore`, `NewsArticleList`, `NewsArticleCard`
   - For MDX-backed detail route follow-ups, mark the route-level `<main>` with type-specific names in addition to shared `PublicationPostPage` markers, e.g. `BlogPostPage`, `WhitepaperPostPage`, `NewsPostPage`, `EventPostPage`, `UseCasePostPage`, `AipDemoPostPage`, `AcpDemoPostPage`, `IntroductionDeckPostPage`, `GlossaryPostPage`, `ManualPostPage`.
5. Company/about static page boundaries
   - For company-style pages, mark existing shared primitives and page-specific section roots rather than adding wrapper components, e.g. `CompanyPageSection`, `CompanyPageIntro`, `CompanyPageLayout`, `AboutUsPage`, `AboutUsHeroCopy`, `AboutUsHeroImage`, `AboutUsSection`, `AboutUsTimeline`, `AboutUsLeaderCard`, `AboutUsLocationGrid`, `AboutUsLocationCard`.
6. Repeated cards/panels when reviewer navigation benefits from the labels.

## Implementation notes

- Prefer editing the component implementation file so every usage receives the marker.
- For route-local page roots, adding `componentNameDebugProps("PageName")` to the existing `<main>` in `src/app/**/page.tsx` is appropriate.
- If a shared primitive such as `PlatformPageShell` does not pass through `data-*` props, extend it minimally to accept and spread non-class props rather than wrapping it.
- Avoid broad automated rewrites over many TSX files. One-line-return components can make regex/autofix scripts attach the wrong component name to a later element. Use exact targeted replacements or review every generated diff.

## Tests / verification

- Follow source-level TDD for marker coverage:
  1. Add failing assertions to `tests/component-name-debug.test.mjs` for the expected marker names.
  2. Run `node --test tests/component-name-debug.test.mjs` and confirm RED.
  3. Add markers to existing roots.
  4. Re-run the test and the owning CI group.
- `tests/component-name-debug.test.mjs` is mapped to the `assetsShell` group in `scripts/ci/test-groups.mjs`.
- Component marker changes can also affect existing source-contract tests outside `assetsShell`, especially when they regex-match exact prop-less JSX such as `<section className="...">` or `article className="..."`.
  - If the product/layout contract is still correct and only `data-*`/debug props were added, update those tests narrowly to allow optional props before `className`, e.g. `<section[^>]*className="...">`.
  - Do not remove the marker or weaken the test to a broad substring when the intended class/layout contract can still be asserted.
  - In this repo, run the changed-scope groups that CI selects for touched route/static files, not only `assetsShell`; for broad public route markers this commonly includes `staticPages` and `routingSeo`.
- Useful checks:
  - `node --test tests/component-name-debug.test.mjs`
  - `node scripts/ci/run-node-tests.mjs assetsShell`
  - `node scripts/ci/run-node-tests.mjs staticPages`
  - `node scripts/ci/run-node-tests.mjs routingSeo`
  - `git diff --check`
- If local `npm run typecheck` fails because of unrelated existing files, verify whether the output mentions the changed files before treating it as a blocker.
