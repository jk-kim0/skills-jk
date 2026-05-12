---
name: corp-web-japan-static-page-convention-refactor
description: Refactor corp-web-japan static marketing pages so page.tsx becomes the primary readable implementation surface, while keeping only small reusable or interactive helpers extracted.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, static-pages, code-location-conventions, refactor]
    related_skills: [corp-web-japan-origin-main-worktree-safety]
---

# corp-web-japan static-page convention refactor

Use this when cleaning up static marketing pages in `corp-web-japan` to match `docs/code-location-conventions.md` section 1.

## Goal

Make the route file itself the primary readable implementation surface:
- `src/app/<route>/page.tsx` should show the main copy, section order, and page-specific JSX
- `src/app/<route>/page.tsx` should contain the copy text and the explicit calls/composition that use section components
- `src/components/sections/**` should define the components used by `page.tsx` and hold the style/UI/UX implementation details such as classes, JavaScript, and styling behavior
- reduce dependence on page-specific wrapper components under `src/components/sections/**`
- reduce dependence on page-specific content registries under `src/content/**`
- keep only truly reusable primitives or small interactive helpers extracted

## When auditing which pages do or do not fit this convention

Do not limit the analysis to the explicit examples named in `docs/code-location-conventions.md`.
Those examples are illustrative, not an exhaustive registry of every current static page.

For a compliance audit on latest `origin/main`:
- enumerate the current candidate static marketing routes from `src/app/**/page.tsx`
- include preview/static marketing routes under `/t/**` when they are mostly authored local pages
- exclude publication/detail/list routes and clearly data-backed feature routes that belong under the thin-route convention instead
- then compare each candidate against the actual route-local-authoring criteria in this skill

Practical implication learned from repo follow-up:
- routes such as `/t/about-us`, `/t/certifications`, and `/t/services/**` may already satisfy the route-local authoring goal even if they are newer than the examples in the docs
- the main current non-compliant pages can therefore be a smaller set than “all static-looking pages,” especially when newer preview pages were authored directly in `page.tsx`
- do not treat documentation labels like "partial" or "wrong / pre-refactor" as authoritative without checking the live code on latest `origin/main`; those labels can lag behind after a sequence of section-scoped PRs merges
- when a page is explicitly called out in docs as non-compliant, verify the current `page.tsx`, current `src/components/sections/**` files, and recent git history for that route before recommending more route-local-authoring work
- practical example: `src/app/solutions/ai-crew/page.tsx` was still described in docs as a wrong/pre-refactor example even after multiple merged PRs had already moved most section copy and composition into the route; the correct conclusion was that the docs had become stale, not that the page still needed the same refactor class
- additional `/t/*` audit lesson from latest-main issue rewriting:
  - count the real current `src/app/t/**/page.tsx` routes before writing a broad cleanup conclusion
  - in one verified latest-main snapshot, 15 `/t/*` page routes existed, 13 were already route-local-authoring / section-composition pages, and only the privacy-policy pair remained as thin document wrappers
  - treat that kind of result as evidence that the broad migration is largely complete; do not keep writing the repo state as if all `/t/*` pages still need the same route-localization work
  - if the only remaining thin routes are document-style pages like privacy-policy, verify whether they are intentional shared-document exceptions rather than unfinished static-page debt

## When this applies

Typical targets:
- top page
- solution landing pages like AI Crew / AI Dashi
- other mostly static marketing pages with little or no data fetching

Do NOT apply this pattern to:
- publication/detail/list routes that should stay thin
- feature routes whose implementation belongs in `src/lib/**` + shared sections
- CMS or data-backed pages unless the user explicitly asks

## Baseline workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Read:
   - `README.md`
   - `docs/code-location-conventions.md`
   - the current `page.tsx`
   - the extracted section component
   - the page-specific content module
3. Compare with an in-repo aligned example such as `src/app/solutions/ai-dashi/page.tsx`.
4. Before editing, lock the intended PR shape:
   - whole-page final refactor, or
   - section-scoped refactor, or
   - one-section comparison/experiment PR
5. Name the hero section explicitly and list which neighboring sections should remain minimally changed.
6. Move the main copy, constants, section order, and page-specific JSX into `page.tsx` only within that approved scope.
7. Keep extracted only:
   - reusable shared components already used elsewhere
   - tiny interactive/client-only sections that would otherwise force the whole page to become a client component
8. Re-run type checking.

## Section-complete-first rule

For this repo, one narrowly scoped PR with a single fully completed section is better than a broad PR with many half-finished sections.

When the user wants a section-scoped refactor:
- finish that section to the intended end-state standard
- keep the rest of the page as unchanged as practical
- do not mix unrelated partial cleanups into the same PR just because they are nearby

If the branch already accumulated broader changes than the user actually wants:
- stop widening the scope
- identify the hero section of the PR
- revert or remove non-hero-section refactor changes unless they are strictly required support work
- keep only the minimal surrounding edits needed for the hero section to function and remain reviewable

Practical lesson from AI Dashi follow-up work:
- if a comparison section becomes the only truly completed result, prefer rewriting the PR so that comparison section is the only showcased refactor outcome
- do not leave unrelated extracted section files in the branch just because they were already written once

Additional stale-PR lesson from PR 210 follow-up:
- if the open PR branch was created before later sibling route-local-authoring PRs merged, do not continue editing that stale branch shape in place just because the PR is still open
- first inspect latest `origin/main` and identify which neighboring sections are now already route-localized on main
- then rebuild the old PR's surviving unique scope only on top of latest main, preserving the newer merged route-local sections exactly as they now exist
- in practice this often means: keep the latest-main `page.tsx` structure, insert only the target section's route-local JSX back into the correct place, remove the old section data from shared content files, and keep newly merged neighboring sections untouched
- for section-scoped static-page PRs, this reconstruction is usually safer and clearer than trying to replay the old branch commit-for-commit with a normal rebase
- practical follow-up from AI Crew PR 218 rewrite: if the stale PR tried to localize one section (for example `results`) but also re-externalized already-migrated neighboring sections back into `src/content/**` or a shared `*Sections` wrapper, throw away that stale branch shape
- rebuild from latest `origin/main`, preserve the latest-main route-local sections exactly as they are, add only the target section's route-local JSX to `page.tsx`, create a UI-only section component file for that target section if needed, remove only that target section's rendering from the shared wrapper, and delete only that target section's content blob from the shared content module
- after that rewrite, update the structure test so it asserts the latest-main route-local sections plus the newly localized target section together, instead of weakening the test contract to permit the old wrapper/content regression
- important section-order lesson from AI Crew platform/use-cases follow-up: when a shared wrapper still contains a section that appears *before* the target section in the rendered page order, do not localize the later middle section first by rendering it outside that wrapper. Doing so can silently reorder the page even if the copied JSX is otherwise correct.
- practical example: on AI Crew, the `platform` section (`実務での安全なAI活用を支える...`) appears before `use-cases`. Localizing `use-cases` first while `platform` still lived inside the shared shell caused the preview page to render `process -> use-cases -> platform -> results` instead of `process -> platform -> use-cases -> results`.
- safe rule: for section-scoped PRs, either (a) localize sections in actual render order, or (b) split the shared shell around the target section first so the target can be reinserted in the exact original slot. If neither is done, treat the PR plan as structurally unsafe before editing.
- review check for this failure mode: after moving one section, compare the live/latest-main section order against the new `page.tsx` render order explicitly. Do not assume preserving the copied JSX preserves the page order.
- practical follow-up from AI Crew PRs 219 and 224: when the page still contains a shared shell that renders multiple later sections in order, do **not** localize a section from the middle/end of that shell first if pulling it out will change the rendered section order
- concrete example: if the shared shell currently renders `platform -> use-cases`, moving `use-cases` out to `page.tsx` before `platform` is localized or before the shell is split will often produce `use-cases -> platform` on preview, even if each section works in isolation
- before choosing the next section-scoped PR, inspect the live/current route order and identify whether the candidate section has a still-shared predecessor in the same shell
- if yes, either:
  - localize the predecessor section first, or
  - split the shell into explicit before/after pieces so the extracted section can be reinserted at the exact original slot
- treat "preserve relative section order on the rendered page" as a hard done criterion, not a nice-to-have verification step after the refactor

## Preferred extraction rule

Ask: “If I open only `page.tsx`, can I understand the page quickly?”

If no, pull more structure back into the route.

Good to keep extracted:
- `RevealOnScroll`
- shared showcases already used elsewhere
- a small client component for isolated interactivity, e.g. a tabbed roadmap section
- section-scoped semantic wrapper components under `src/components/sections/**` when they let `page.tsx` read as authored composition, for example `SectionCard`, `SectionTitle`, `SectionBody`, `PromoCard`, or `PromoAction`
- small semantic child slots for card-like UI when they move marketing copy ownership into the route, for example `CardHeading` and `CardBody`

Important semantic-slot rule learned from AI Crew design-elements follow-up:
- if a route-local section still passes its main marketing sentence through props like `heading="..."`, `title="..."`, or similar string/ReactNode props, that section is still hiding key authored copy behind a component API
- prefer a composition like:
  - `<Card>`
  - `<CardHeading>マーケティング見出し</CardHeading>`
  - `<CardBody><p>説明文</p></CardBody>`
  - `</Card>`
- this keeps the actual heading/body copy visible in `page.tsx` while leaving styling, spacing, icon chrome, and layout implementation in the extracted section component file
- practical example: replacing `AICrewDesignElementCard label="業務定義" heading="任せる業務と期待する成果を明確にする">...</AICrewDesignElementCard>` with `AICrewDesignElementHeading` + `AICrewDesignElementBody` children made the route read more like authored JSX and matched the user's preferred method better
- apply the same rule to section wrappers themselves: if a route-local section still does `title={<>...</>}` or similar prop-passing for the main section heading, that title is still being hidden behind a component API
- prefer wrapper composition like:
  - `<Section>`
  - `<SectionTitle>見出し <strong>強調句</strong></SectionTitle>`
  - `<SectionGrid>...</SectionGrid>`
  - `</Section>`
- practical follow-up from AI Crew design-elements work: replacing `AICrewDesignElementsSection title={...}` with `AICrewDesignElementsTitle` + `AICrewDesignElementsGrid` made the route easier to review because the main section heading and its emphasized phrase were visible directly in `page.tsx` instead of being passed through a prop

Bad to keep extracted:
- a giant page-specific `<SomethingSections />` wrapper that hides most of the route
- a large `src/content/<page>.ts` object whose main job is to store the page’s marketing copy and section composition
- the same large content registry merely split into many top-level route constants such as `const hero = { ... }`, `const roles = { ... }`, and `const contact = { ... }` while the route still reads as `data blob first, JSX second`
- an external wrapper mechanically copied into `page.tsx` as a large local helper like `function AICrewSections()` when it still hides most of the authored page structure
- a large local section helper such as `function SupportSection()` or `function ReleaseFlowSection()` when it still owns that section's real headings, prose-heavy arrays, CTA text, and JSX structure together
- relocating a former top-level blob into `function SomeSection() { const items = [...] ... }` while the route body now only shows `<SomeSection />`
- leaving a section-specific file as only a thin outer container while the real section layout, animation wrappers, heavy Tailwind classes, background images, and CTA/button implementation still live inline in `page.tsx`

Important anti-regression rule from AI Dashi follow-up work:
- moving `const supportItems = [...]` or `const releaseFlow = [...]` out of file scope is not enough if the same prose-heavy data and section markup are merely re-hidden inside a local helper such as `function AIDashiSupportSection()`
- that reduces top-level clutter, but it does not yet make the route body the primary readable authoring surface
- if the default export body becomes less readable because the section collapsed to a single helper call, treat the refactor as still incomplete
- when localizing a pre-existing card/list section into route-local JSX, preserve the exact existing icon components unless the user explicitly asks for a visual change
- do not replace established Lucide icons with ad hoc inline `<svg>` markup just because the section is being rewritten into direct JSX
- practical regression found in AI Dashi wall-cards follow-up: a refactor-only PR accidentally changed `Users` and `Settings` icons to custom SVGs even though the task was only authoring relocation; the correct fix was to restore the original icon components so the refactor remained visually identical

- when a route-localized section is still a large raw JSX/class blob in `page.tsx`, treat the refactor as incomplete even if the copy has already been removed from `src/content/**`
- the next step is usually to promote that section file from a thin container into several semantic section components, while keeping the actual user-facing sentences and CTA labels authored in `page.tsx`
- practical pattern confirmed in AI Crew lost-section follow-up: move `RevealOnScroll`, background-image rendering, card geometry, and CTA button implementation into `src/components/sections/<section>.tsx`, then let `page.tsx` read as `<LostProblemCard>`, `<LostProblemTitle>`, `<LostProblemBody>`, `<LostWhitepaperCard>`, and `<LostWhitepaperAction href={...}>...`

## Practical pattern used successfully

### Cross-page standardization audit heuristic

When the task is not to migrate one page but to review several existing static/preview pages for shared UI primitives, audit them by **page family first**, not by route path alone.

Recommended clustering learned from the `/t/about-us`, `/t/certifications`, `/t/cookie-preference`, `/t/privacy-policy`, `/t/eula`, `/t/terms-of-service`, `/t/plans`, `/t/services/*`, and `/t/solutions/aip/*` review:

1. **Shared CTA family first**
   - check whether the pages already converge on `src/components/sections/simple-cta-section.tsx`
   - if many pages already use that CTA shell, treat it as the existing standard instead of inventing a new one
   - prefer absorbing page-local CTA wrappers into that shared CTA primitive with small variants for spacing, title size, content width, or button treatment

2. **Product / solution marketing hero family**
   - typical members: `/t/services/aip`, `/t/services/acp`, `/t/services/fde`, `/t/services/aip/integrations`, `/t/solutions/aip/usage-based-llm`, `/t/solutions/aip/mcp-gateway`, `/t/solutions/aip/fde-services`
   - common shape often includes:
     - content width around `max-w-[1200px]`
     - hero title around `60/72`
     - lead around `18/28`
     - centered copy
     - large section gaps around `80px`
   - this family is a good candidate for shared `MarketingHero*` primitives

3. **Info / static intro family**
   - typical members: `/t/about-us`, `/t/certifications`, `/t/plans`
   - these often share width, color, and intro rhythm, but not one identical hero layout
   - extract only loose intro primitives such as title/lead/container unless the actual structure is truly the same

4. **Legal / document header family**
   - typical members: `/t/privacy-policy`, `/t/terms-of-service`, sometimes `/t/eula`
   - prefer a document-page header primitive with narrower body width and smaller title scale than marketing hero pages
   - however, do not force pages into one legal header family if one route is structurally different

Important exception handling:
- treat `/t/cookie-preference` as an intentional style variant, not the baseline for the whole site
- treat `/t/eula` as a potential legal-family outlier when its header scale/structure differs from `/t/privacy-policy` and `/t/terms-of-service`
- treat `/t/about-us` as sharing some intro/title tokens with other info pages, but keep its two-column hero layout separate unless another route truly matches it

Audit output rule:
- prefer conclusions like "CTA can be standardized immediately; hero needs 3 families" over vague statements like "some parts look reusable"
- explicitly separate:
  - reusable typography tokens
  - reusable width/padding wrappers
  - reusable full-layout compounds
- do not recommend one giant universal hero component when the evidence really supports a small set of family-specific primitives

### Recommended staged approach for static marketing pages

When the user wants a cleaner route-level static page but also wants reusable section/UI extraction first, prefer this order:

1. Primitive-extraction PR first
   - stay on latest `origin/main`
   - keep the route thin for now
   - identify repeated section-level patterns such as:
     - intro/header blocks
     - pills / badges
     - elevated bordered surfaces
     - icon frames
     - repeated CTA button treatments
   - extract those into small reusable components under `src/components/sections/**`
   - if a giant content object exists, begin decomposing it into section-level exports instead of one monolithic registry
   - do not move the full page implementation into `src/app/.../page.tsx` yet in this PR

2. Route-localization PR second
   - start again from the latest `origin/main` after the primitive PR merges
   - move the static page implementation into `src/app/<route>/page.tsx`
   - reuse the already-extracted primitives so the route mostly reads like:
     - `<SectionPrimitive>`
     - `<h2>マーケティング文句</h2>`
     - `<p>説明文</p>`
   - keep only small interactive/client helpers extracted, e.g. a roadmap tab section

This staged approach is especially useful when the current page has both:
- repeated styling patterns worth extracting
- a giant page-specific content object that should eventually be dismantled

### Important latest-main discipline for staged refactors

In fast-moving repos, do not keep executing a long static-page refactor plan against a worktree if `origin/main` advanced materially while you were preparing or partially editing a previous attempt.

If a prerequisite PR merged and advanced `origin/main`:
- stop
- fetch latest main again
- create a fresh worktree from the new tip
- re-read the now-current files
- then continue the next stage from that new baseline

Do not assume an earlier fresh worktree is still fresh enough after upstream movement.

### For server route pages

If the page is mostly static and currently imports:
- `page-specific sections component`
- `page-specific content module`

then refactor to:
- import shared layout components in `page.tsx`
- prefer putting section copy close to the JSX that renders it
- define a local `function <Page>Sections()` inside `page.tsx` for the page body if that improves readability
- render that local function from the default export page component

This keeps `page.tsx` readable without forcing everything into one giant JSX return.

### Naming extracted UX-semantic components

When extracting top-page-specific UX-semantic components, prefer names that describe the user-facing choice being presented rather than lower-level implementation structure.

### Production-ready naming for `/t/*` routes

Important naming rule learned from `/t/cookie-preference` follow-up:
- even when a route still lives under `/t/*`, do not encode `Preview` semantics in the route component name or its page-specific section/helper names unless the user explicitly asks for that wording
- treat the implementation as a production-ready page shape and use neutral names such as `CookiePreferencePage`, `CookiePreferenceCtaSection`, or `CookiePreferenceHeroSection`
- avoid names like `CookiePreferencePreviewPage` or `CookiePreferencePreviewCtaSection`
- the `/t/*` path itself is enough to signal preview scope; repeating that status in symbol names adds noise and conflicts with the user's preferred end-state direction

Practical review check:
- after refactoring a `/t/*` route, search the touched route and related section files for `Preview` in exported symbol names
- if the route is meant to be production-ready in structure, remove those `Preview` names before finalizing unless they are part of an intentionally preview-specific global surface such as Preview Toggle UI

Practical example from top-page solution cards:
- prefer `SolutionChoice*`
- avoid longer or less direct names like `TopPageSolutionPath*`

Good examples:
- `SolutionChoiceCard`
- `SolutionChoiceHeader`
- `SolutionChoiceBadge`
- `SolutionChoiceTitle`
- `SolutionChoiceSubtitle`
- `SolutionChoiceDescription`
- `SolutionChoiceAction`

Why:
- the file path already gives top-page context, so repeating `TopPage` in every exported symbol adds noise
- `Choice` reads more clearly than `Path` for a landing-page UI where the user is choosing between alternatives
- shorter UX-semantic names make `page.tsx` read more like content structure and less like implementation plumbing

Important nuance learned from PR follow-up:
- Do **not** merely replace `src/content/<page>.ts` with a giant top-level `const pageContent = { ... }` inside `page.tsx` and consider the job done.
- That still leaves markup and Japanese marketing copy logically separated, just in a different file location.
- The better direction is:
  - inline the most important page copy directly in JSX where practical, or
  - at minimum, move page-specific content objects down into the local page/body function scope so the structure and copy are read together in one implementation surface.
- If a reviewer/user says the route still feels like `markup + content registry`, treat that as valid feedback and keep collapsing the distance between copy and JSX.

Practical follow-up from `src/app/solutions/ai-dashi/page.tsx` refactor work:
- when a page is already partly route-local but still starts with several large top-level arrays/objects, a good incremental refactor is to move those blobs into small route-local section helper functions such as `function <Page><Section>NameSection()`
- inside each section helper, keep only the small data that belongs to that section (for example comparison rows, support cards, release steps, risk cards)
- then call those helpers from the main page return in section order
- this is useful when the user wants the route to read more like a page without forcing a risky full visual rewrite
- preserve shared URLs/imported route constants and existing tests while doing this; the improvement goal is reducing `data blob first, JSX second`, not changing page behavior
- however, do not stop at a mechanical relocation where the default export body degrades into opaque calls like `<SupportSection />` and `<FlowSection />` while the section's headings, prose-heavy arrays, CTA copy, and JSX structure are all re-hidden inside those helpers
- use this self-check: if collapsing local helpers makes the default export body too sparse to review the migrated section's narrative and composition, the helper is too large and the refactor is still incomplete

### For isolated client interactivity

If only one subsection needs `useState` / client behavior:
- keep `page.tsx` as a server component
- extract only that subsection into a tiny dedicated client component
- pass the minimum data in as props

This worked well for the top page roadmap tab section.

Practical service-preview pattern learned from `/t/services/acp` follow-up:
- if a static preview page has one interactive showcase/browser section, do **not** let that one interactive widget force the whole page-specific section module to become `"use client"`
- keep the route-owned section heading, intro sentence, and overall section composition visible in `page.tsx`
- keep server-safe layout primitives in a normal section file such as `src/components/sections/<page>-service-page.tsx`
- move only the truly interactive widget into a dedicated client file such as `src/components/sections/<page>-feature-browser.tsx`
- update structure tests so they assert:
  - the main section heading/copy lives in `page.tsx`
  - the static section primitive file is not marked `"use client"`
  - the dedicated interactive widget file *is* marked `"use client"`
- practical example: on `/t/services/acp`, `QueryPie ACPができること` belonged in the route, while the category tab/prev-next feature browser was split into its own client component; leaving both concerns together in one `"use client"` page-section module made the route less readable and widened the client boundary unnecessarily

Important App Router build pitfall learned from follow-up refactors:
- if an extracted helper uses React client-only APIs such as `createContext`, `useContext`, `useState`, `useEffect`, or other client hooks, mark that extracted file with `"use client"`
- do not assume that because the parent page is mostly static, Next/Turbopack will tolerate `createContext` in an unmarked component imported by `page.tsx`
- a typical failure looks like:
  - `You're importing a module that depends on createContext into a React Server Component module`
- practical example: `SolutionChoiceCard` used `createContext/useContext`, so the component file itself needed `"use client"` after being imported from `src/app/page.tsx`

Important client-boundary scope rule learned from `/t/services/acp` follow-up review:
- when one section on an otherwise static marketing page needs client interactivity, do not let that force the entire page-specific section module into a single `"use client"` file if that file also contains many static layout primitives
- keep the client boundary as narrow as practical:
  - route-owned section heading, body copy, CTA labels, and section order should stay visible in `page.tsx`
  - static section primitives can stay in a server-safe section module
  - the interactive widget itself should be isolated in a dedicated client component file when practical
- practical anti-pattern: a route imports one large page-specific `sections/*.tsx` file marked `"use client"` only because one feature browser/tabbed widget inside that file uses `useState`, while the same file also exports hero wrappers, section shells, and other static primitives
- why this is undesirable:
  - it hides too much of the route-local authored structure behind one interactive wrapper layer
  - it widens the client boundary unnecessarily
  - it makes the route read like `one opaque interactive section call` instead of a page with visible authored section ownership
- review check for this failure mode:
  - if the main feature section heading (for example `QueryPie ACPができること`) is rendered inside the client widget file rather than in `page.tsx`, treat the route-local refactor as only partial
  - if `page.tsx` only renders something like `<FeatureBrowser categories={...} />` for a major marketing section, inspect whether the section heading and surrounding authored narrative should move back into the route while the tab/browser logic remains extracted

## Cautions from experience

- Do not try to mechanically auto-merge section/content files into page files without checking multiline imports and local helper constants; broken imports are easy to introduce.
- When copying from a large section component, ensure these local definitions are preserved if still referenced:
  - icon arrays
  - theme/style constant objects
  - small text rendering helpers
  - `isExternalHref` style helpers
- If you extract one small interactive subsection, also remove the old inlined client-only state logic from the server page.
- Prefer direct `Link` usage over click-wrapper + `router.push` when the card can simply be a link.
- Most important practical cleanup rule learned from PR follow-up: if content truly moved into `page.tsx`, delete or stop using the old page-specific source files as part of the same change. Otherwise the refactor is only a copy, not a move.
- After moving static-page content into route files, explicitly search for leftover imports/usages of the old modules such as:
  - `src/components/sections/<page>-sections.tsx`
  - `src/content/<page>.ts`
- Typical residual consumers may be adjacent support surfaces like `not-found.tsx`, floating guides, or tests that still import old CTA constants.
- After the move, either inline those remaining small constants locally where used, or re-home them into a still-valid shared module. Do not leave dead page-content files around just because one small helper still imports them.
- Update structure/assertion tests in the same batch. Repository tests may explicitly read old files by path, so deleting the obsolete files without updating tests can fail CI even when runtime code is correct.

## Strongly recommended two-PR test strategy

When the repository already contains structure tests that read exact source files such as:
- `src/content/top-page.ts`
- `src/content/home.ts`
- `src/components/sections/top-page-sections.tsx`
- `src/components/sections/home-page-sections.tsx`

prefer this order:

1. Test-only PR first
   - change only tests/helpers
   - make tests validate the same user-facing content/CTA/structure invariants whether the implementation still lives in old content/section files or has already moved into route files
   - do not change production code in this PR
2. Refactor PR second
   - move/delete the old content and section files
   - keep the already-generalized tests green

Why:
- If you refactor runtime code and test expectations in the same PR, it becomes harder to prove behavior equivalence.
- A separate test-only PR preserves a cleaner signal: the tests become location-agnostic first, then the implementation is free to move.

### Practical helper pattern for compatibility tests

A reusable pattern is to extend test helpers with functions like:

```js
export function sourceExists(relativePath) { ... }
export function readFirstExistingSource(relativePaths) { ... }
```

Then assertions can prefer old canonical paths first and fall back to new route-local paths:

```js
const topPageDataSource = readFirstExistingSource([
  "src/content/top-page.ts",
  "src/app/page.tsx",
]);
```

Use this for tests that should verify equivalence of:
- CTA targets
- section markers / anchor ids
- required copy fragments
- security / download / contact route wiring
- route-level readability invariants

Important nuance:
- These tests should validate stable semantics, not one exact implementation location.
- Only assert exact file-path absence/presence when the specific PR goal is cleanup of dead source files.
- For transition-safe tests, prefer “old OR new location contains the invariant” instead of “must exist only here.”

## Preview company-info static routes under `/t/*`

## Preview company-info static routes under `/t/*`

When migrating a legacy `corp-web-contents` company/info page into a local preview route such as `/t/certifications` in `corp-web-japan`:

- keep the implementation route-local in `src/app/t/<slug>/page.tsx`
- prefer a fully static page component rather than MDX when the user explicitly asks for `page.tsx`
- keep `SiteHeader` and `SiteFooter` in the route, and keep the main readable page structure in that file
- if a public non-`/t` route such as `/certifications` already exists as a redirect surface, do not replace or widen that scope unless the user explicitly asks; adding the local `/t/...` preview page does not itself authorize changing the public redirect behavior
- when source badges or illustrations come from `../corp-web-contents/public/...`, do not assume the preview route prefix `/t` must also appear in the final public asset path. If the user asks for a cleaner or shorter asset root, use a direct path such as `public/<slug>/...` and update the page image references accordingly. Example learned from certifications work: the page route stayed `/t/certifications`, while the accepted asset root became `public/certifications/*` with image URLs like `/certifications/<file>`.
- for live-parity follow-up on static preview pages, verify both the deployed preview URL and the live reference URL in the browser, then compare computed styles for the exact target elements instead of relying only on visual guesswork. In the certifications page, useful checks were:
  - header span vs main content span
  - intro paragraph `font-size`, `line-height`, `font-weight`, and `letter-spacing`
  - certification card `border-radius`, title size, detail size, and grid geometry
  - CTA button `border-radius`, `font-size`, `font-weight`, `line-height`, padding, and border color
- a practical pattern for this comparison is to inspect the live page with `getComputedStyle()` and `getBoundingClientRect()` for the exact elements, then translate those values into the current repo's Tailwind classes or arbitrary values. This is especially effective when the goal is “match the rendered result” rather than “approximate the structure”.

Important source-of-truth rule learned from `/t/certifications` work:
- treat `../corp-web-contents` primarily as the content/composition source
- treat `../corp-web-app` as the style/widget implementation source when the legacy MDX page uses shared foundation/widget components such as `StaticHeader`, `CenterSection`, `ButtonLink`, or `Certifications`
- do not assume the MDX file alone tells you the real rendered spacing, radii, text metrics, or card layout; those often come from `corp-web-app` widget CSS/modules and design-token variables
- practical example: `../corp-web-app/src/components/widget/certifications/certifications.component.tsx` and `certifications.module.css` provided the real grid, radius, and card spacing behavior for the certifications page, while `corp-web-contents/pages/company/certifications/ja/content.mdx` only described the content structure and which widget was used

Important browser-verification rule learned from the same work:
- when the user asks for the preview page to match the existing `querypie.com` rendering, open both the live URL and the preview URL in the browser and inspect the actual rendered result before deciding layout structure
- do not rely only on assumptions from neighboring local preview pages such as `/t/news` or `/t/about-us`
- if your initial structural assumption is wrong, change course immediately based on browser evidence
- practical example: for `/ja/company/certifications`, the live page did **not** have a left company-info sidebar inside the main content area even though a sidebar seemed plausible from other local preview patterns; the correct follow-up was to remove the preview sidebar and match the live single-column 1200px content span instead

Use browser computed-style measurement for high-fidelity follow-up polish:
- measure live and preview computed styles for the exact intro paragraph, card title/detail text, CTA headings, buttons, and card containers
- compare `font-size`, `font-weight`, `line-height`, `letter-spacing`, `padding`, `border`, `border-radius`, `width`, and left/right alignment against the header span
- when the user asks for “same rendering / UX design,” prefer matching these measured values over rough visual approximation
- especially useful for pages like certifications where the remaining differences are small but visible: intro text size, card radius, CTA button radius, CTA heading weight, and inner section padding

This pattern is especially useful for one-off company/info migrations where the user wants:
- Japanese content copied from `../corp-web-contents`
- no MDX
- a reviewable static route with route-local copy and markup
- the preview rendering to closely match the existing `querypie.com` live page, not just the content inventory

### Important live-parity rule for company/info static migrations

When the user asks for the local `/t/...` route to match the live `querypie.com/ja/company/...` page visually, do not assume the intended structure from neighboring local preview routes such as `/t/news`.

Instead:
1. inspect the live page directly in the browser
2. measure the real DOM/computed styles of the exact target elements
3. prefer those live measurements over assumptions from repo-local patterns

Practical lessons from `/t/certifications` follow-up work:
- the live page did **not** have the expected left company-info sidebar in the main content area, even though the local repo already had sidebar-like patterns in related preview surfaces
- in that situation, matching live appearance was more important than reusing the local sidebar pattern
- use browser DOM inspection (`getBoundingClientRect`, `getComputedStyle`) to verify:
  - whether a sidebar truly exists on the live page
  - the header content span (for example logo-left to CTA-right)
  - the actual content start/end x positions
  - intro copy `font-size`, `line-height`, and `font-weight`
  - button and card `border-radius`
- when the target is alignment to the header span, distinguish between:
  - the outer section/container width
  - inner content inset caused by section padding
  A page can already have the correct outer `max-width` while still looking too narrow because inner `px-*` padding shifts the real content start/end inward.
- for exact live parity, prefer measured values such as `16.875px`, `26.25px`, `5.625px`, or `9.375px` when the live site uses them, rather than rounding everything to the nearest Tailwind default token

## Small repeated `/t/*` production-ready cleanups: batch by defect family, not page

Important lesson from the `/t/*` production-ready naming cleanup follow-up:
- when many routes share the same low-risk, mechanical defect class, do **not** default to one PR per page
- if the change is essentially the same across pages, prefer one grouped cleanup PR so review and CI overhead stay proportional to the real code change

Typical examples that should usually be batched together:
- default export names like `AboutUsPreviewPage`, `PlansPreviewPage`, `AipServicePreviewPage`
- helper names like `renderEulaPreviewMdx` when a neutral production-ready name is sufficient
- metadata descriptions that still say `preview`, `プレビュー`, or similar temporary-state wording
- small paired test updates that simply prevent those preview-only names/phrases from returning

Only split into separate page PRs when one or more of these are true:
- implementation shape differs materially across pages
- one page needs extra non-mechanical code changes beyond naming/text cleanup
- verification differs materially by page
- reviewer value genuinely comes from isolated page-by-page review

Practical rule:
- `same defect family + same fix pattern + low risk` -> batch into one PR
- `different implementation concerns or meaningful page-specific reasoning` -> split

## Verification

A practical follow-up learned from `/t/certifications` work:
- matching the route container `max-w-[1200px]` to the header span is not sufficient by itself
- if the section also has inner horizontal padding such as `px-6 lg:px-10`, the *effective* content edges become narrower than the header span even though the outer section width still measures 1200px
- in one real case, the section measured `left=40 right=1240 width=1200`, but the visible title/grid content started at `x=80` and ended at `x=1200` because of the extra inner padding

When the user asks for the content area to align with the header edges:
1. measure the live/preview header span in the browser from the left logo edge to the right CTA edge
2. measure the actual visible content edges (for example the `h1`, card grid, or primary section content)
3. compare those values, not just the outer section box
4. if the section width already matches but the content is inset, remove or reduce the inner horizontal padding on that section instead of changing `max-width`

For typical corp-web-japan desktop layouts, a useful sanity check is:
- viewport width 1280px
- header content span often measures `left=40`, `right=1240`, `width=1200`
- the target page content should visually start and end on those same x positions when the user explicitly asks for header-edge alignment

## Verification

Minimum verification for this refactor class:

```bash
npm run typecheck
```

If the user explicitly wants more verification or the change affects broader rendering risk, then also run:

```bash
npm run test:ci
npm run build
```

But for this user, prefer the lightest meaningful verification first.

## Done criteria

- `page.tsx` is the primary readable implementation surface
- page-specific content registry dependence is reduced or removed
- giant page-specific wrapper dependence is reduced or removed
- only small reusable/shared or isolated interactive helpers remain extracted
- `npm run typecheck` passes
