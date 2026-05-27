---
name: corp-web-japan-route-local-authoring-wiki-scope
description: Update the corp-web-japan Route-Local-Authoring wiki page with the correct non-MDX scope, excluding content families already migrated through the separate MDX/publication pipeline.
---

# corp-web-japan Route-Local-Authoring wiki scope

Use this when updating these wiki pages in `corp-web-japan.wiki`:
- `Route-Local-Authoring`
- `Route-Local-Authoring-ko`
- future language variants of the same page

## Core rule

This wiki page is **not** the general migration inventory for all content.
It should track only the remaining **non-MDX** public page migration scope.

Do **not** include families that are already handled by the separate MDX/publication migration system.

## Explicitly exclude from this wiki page

Treat these as out of scope for `Route-Local-Authoring*`:
- blog
- whitepapers
- webinars / event-style document postings
- news
- use-cases
- AIP demo
- ACP demo
- introduction deck
- glossary
- manuals
- resources hub

Even if those surfaces still matter for the overall site migration, they belong to the publication / MDX migration track, not to route-local authoring scope.

## What this wiki page should track instead

Focus on non-MDX static/service/policy/company pages such as:
- home
- about-us
- certifications
- cookie-preference
- contact-us
- services landing pages (`AIP`, `ACP`, `FDE`)
- AIP / ACP non-MDX solution subpages
- legal / policy pages like `eula`, `privacy-policy`, `terms-of-service`
- any `corp-web-app` public pages that still need an explicit decision before local replacement, such as `plans`, `key-values`, or pricing-related pages

## Recommended wording

Frame the document around this question:
- which Japan-site pages still need to be finished as local non-MDX public pages in `corp-web-japan`?

Useful phrasing:
- "This page tracks the remaining non-MDX page migration scope"
- "Document-style MDX families are intentionally excluded"
- "Preview-only or redirect-backed static pages are the main remaining route-local authoring scope"

## Practical page structure

Recommended sections:
1. Purpose
2. Scope rule / explicit exclusions
3. Source-of-truth snapshots (`corp-web-japan`, `corp-web-app`, `corp-web-contents` SHAs)
4. Non-MDX static/service/policy inventory table
5. Current priority order
6. Reference routes already aligned enough
7. Conclusion

## Important repo-specific lesson

If a route family is already migrated through the local MDX/publication system, do not keep listing it here just because it still has detail routes or a list page.
This wiki page should stay narrow and actionable; otherwise it turns back into a generic migration dashboard.

## Latest-main audit lessons to preserve

When rewriting `Route-Local-Authoring*` from latest `origin/main`, do not preserve older classifications mechanically.
Re-audit these specific cases because they changed over time and are easy to describe incorrectly:

- top page route-local baseline
  - Do not keep describing the home page using older `src/content/home.ts`-driven wording if latest main has already removed that file.
  - If `src/content/home.ts` is gone and `src/app/page.tsx` now owns the visible copy/composition directly, explicitly note that the top page became a stronger route-local authoring reference point.
- route-local convention docs
  - Before updating the wiki, check whether `docs/static-page-route-local-authoring.md` and `docs/code-location-conventions.md` were updated on latest main.
  - If they now align with the intended route-local authoring split, mention that the repository guidance has caught up with the current implementation instead of leaving the wiki framed as if only the code changed.
- legacy `/posts/**` routes
  - Do not leave deleted legacy `/posts/**` routes sounding like remaining public migration candidates.
  - If latest main removed them, explicitly record that they are no longer part of the remaining non-MDX public-page inventory.
- section-file reorganization
  - If preview/static section implementations were reorganized into `src/components/sections/<family>/...`, treat that as supporting structure cleanup rather than a route-status change by itself.
  - Mention it when summarizing what changed on latest main, but do not let the inventory table imply that public/preview rollout status changed unless the routes themselves changed.

- `privacy-policy`
  - Do not leave this as only a `scope decision needed` item if latest main already has local preview implementation and local content versions.
  - On the audited baseline from 2026-05-10, latest main had `/t/privacy-policy`, `/t/privacy-policy/[slug]`, and local `src/content/privacy-policy/*.mdx` version records, so the correct status was `partial` with remaining public-rollout work.
- AIP integrations
  - Do not describe `/ja/solutions/aip/integrations` as redirect-only if latest main already has `/t/services/aip/integrations`.
  - If that preview route exists, classify it as `partial`, not `not yet migrated`.
- FDE route family
  - Check for both `/t/services/fde` and `/t/solutions/aip/fde-services` before writing the inventory.
  - If both preview routes exist while the public route is still redirect-only, explicitly note the duplicate-preview state and that canonical public rollout still needs to be decided.
- Contact us
  - Verify whether `/contact-us` is a real local page plus submit flow, not just a redirect endpoint.
  - If `src/app/contact-us/page.tsx` and `src/app/contact-us/submit/route.ts` both exist, treat it as already migrated.

## Static/info family-boundary lessons

When updating route-local authoring docs or long-lived taxonomy issues such as issue #397, do not collapse every static/info page into one universal primitive family just because route-local authoring is complete.

Maintain at least these explicit family boundaries:
- Legal / document family
  - Representative routes: `/t/eula`, `/t/privacy-policy`, `/t/privacy-policy/[slug]`, `/t/terms-of-service`
  - Treat this as a separate family with legal document wrappers, legal body/MDX primitives, versioned policy content, document headers, long-form legal copy, and stable reading-width requirements.
  - Do not compare or merge it mechanically with `MarketingPageSection` / company-intro primitives.
- Company-intro / company family
  - Representative routes: `/t/about-us`, `/t/certifications`
  - Treat these as company identity / trust-context pages. They may share marketing shells where the layout contract actually matches, but this is not automatic.
- Adjacent static/info routes
  - `/t/cookie-preference` should be classified first by its settings / consent interaction contract.
  - `/t/plans` should be classified first by its pricing / comparison / CTA semantics.
  - Do not list these as unfinished company-intro commonization merely because they are static/informational.

If this boundary is being recorded in repository docs, update both the detailed route-local authoring guide and the short code-location conventions page when present.

## Latest-main audit lessons from Route-Local Authoring wiki rewrites

When rewriting `Route-Local-Authoring*`, always re-audit latest `origin/main` instead of preserving prior classifications. Recent rewrites showed these specific traps:

### 2026-05-14 baseline (`87a7f583fdd2af747a624d83f4f81cc8a993b187`)

- `/about-us` and `/certifications`
  - Do not classify them as `/t/*` preview-only or public upstream redirects if latest main has `src/app/about-us/page.tsx`, `src/app/certifications/page.tsx`, canonical metadata, and sitemap entries.
  - Treat them as migrated public local non-MDX pages and as current company-page route-local references.
- AIP / ACP preview route taxonomy
  - Do not preserve older `/t/services/aip` or `/t/services/acp` wording as current state.
  - Latest main uses `/t/platforms/aip` and `/t/platforms/acp` for the preview route files.
  - Keep `/t/services/fde` separate; FDE remains a service route rather than an AIP child route in the current taxonomy.
- Route-local developer docs
  - Latest main added `docs/route-local-refactoring-for-developers.md` and `docs/route-local-refactoring-for-developers.ko.md`; mention these alongside `docs/static-page-route-local-authoring.md`, `docs/code-location-conventions.md`, and `.agents/skills/static-page-route-local-authoring/SKILL.md`.
  - The new developer guide names `src/app/page.tsx`, `src/app/about-us/page.tsx`, and `src/app/t/platforms/acp/page.tsx` as direct current references.
  - If the user asks for a stronger developer-facing route-local explainer, do not keep everything in one short intro page. Split it into:
    1. a concise introduction / principle guide, and
    2. a separate long-form examples document in both Korean and English.
  - In that examples document, prefer real before/after code excerpts of at least roughly 30–50 lines, and include not only `page.tsx` but also the referenced module structure that the route depends on.
  - When citing repository code in the examples document, use commit-pinned GitHub blob links rather than branch-relative links so the documentation stays stable after later refactors.
  - Explicitly include at least one concrete `Big JSON Props` / compound-alias / top-level-data-blob example, and explain the practical maintenance failure mode: a small copy or ordering change can force synchronized multi-file or multi-array edits and increase the risk of rendering or contract mistakes.
  - If the user asks for references or terminology, do not default to generic refactoring references first. Prioritize page-architecture references that explain page-level vs lower UI layers, such as:
    - Next.js `page` / `layout` / project-structure docs for route-leaf and shared-UI concepts
    - React component-hierarchy references for top-level vs child-component composition
    - Feature-Sliced Design `Pages`, `Shared`, and `ui` segment terminology for generalized layer naming
    - Atomic Design or presentational/container references for lower-level UI vocabulary
  - In that kind of document, add a short terminology-mapping section that generalizes repo-local names like `page.tsx` and `src/components/sections/**` into broader terms such as `route-level page component`, `page composition layer`, `section component layer`, `presentational component`, `shared UI primitive`, and `screen component`.
- Wiki rewrite shape
  - The English `Route-Local-Authoring` page should be rewritten to match the same latest-main scope as `Route-Local-Authoring-ko`, not left as an older narrow static-marketing-candidate audit.
  - When translating or syncing `Route-Local-Authoring-ko` into `Route-Local-Authoring`, compare the heading outline of both files before committing; a prior sync missed the Korean `Route-local authoring 평가 결과` section in the English page even though most surrounding content matched.
  - Keep the document framed as a non-MDX page-authoring/public-rollout tracker, not as a generic content migration dashboard.

### 2026-05-15 baseline (`d0c32d876cfc7fd5746a2151e84b83b0ea3d45d5`)

- Legal and cookie pages changed status substantially; do not leave them as preview-only or redirect-only:
  - `src/app/cookie-preference/page.tsx` exists and `/cookie-preference` is a public local page.
  - `src/app/eula/page.tsx` and `src/app/eula/content.mdx` exist; `/eula` is a public local legal page.
  - `src/app/terms-of-service/page.tsx` and `src/app/terms-of-service/content.mdx` exist; `/terms-of-service` is a public local legal page.
  - `src/app/privacy-policy/page.tsx`, `src/app/privacy-policy/[slug]/page.tsx`, and `src/content/privacy-policy/*.mdx` exist; `/privacy-policy` and `/privacy-policy/:slug` are public local versioned legal pages.
- Sitemap nuance matters:
  - Latest `src/app/sitemap.ts` includes `/cookie-preference` and `/eula` static routes.
  - `/privacy-policy` and `/terms-of-service` are public local pages but were not static sitemap entries on this baseline; record this as a follow-up/policy check rather than assuming absence means the pages are not public.
- ACP child pages changed status:
  - `/t/platforms/acp/database-access-controller`, `/kubernetes-access-controller`, `/system-access-controller`, `/web-access-controller`, and `/integrations` preview pages exist.
  - Public `/platform/security/*` routes still redirect upstream, so classify these as `partial` preview-local/public-redirect, not `not yet migrated`.
  - ACP integrations has preview implementation but still needs public canonical route decision.
- Pricing nuance:
  - `src/app/t/plans/page.tsx` exists as preview.
  - `src/app/pricing/calculator/page.tsx` only calls `notFound()` and should not be documented as a public pricing implementation.
- Developer/guidance docs expanded:
  - Mention `docs/route-local-refactoring-examples.md`, `docs/route-local-refactoring-examples.ko.md`, `docs/company-page-layout-contract.md`, `docs/legal-mdx-refactoring-rules.md`, `docs/route-aligned-mdx-authoring-for-developers.md`, `docs/route-aligned-mdx-authoring-for-developers.ko.md`, and `docs/browser-render-parity-comparison.md` when summarizing current repository guidance.
- Priority order changed:
  - Remove legal/cookie public rollout from the remaining priority list once these are public local pages.
  - Focus remaining Route-Local Authoring priorities on platform/service public taxonomy, AIP/ACP preview-to-public rollout, ACP integrations route decision, and pricing/key-values scope decisions.

### 2026-05-17 baseline (`62cd9dc800df86c90eca967e8fb4fe37464394e5`)

- ACP child pages and plans/pricing changed status substantially; do not leave `Route-Local-Authoring*` on the older `ec651e16...` baseline:
  - `src/app/platforms/acp/database-access-controller/page.tsx`, `kubernetes-access-controller/page.tsx`, `system-access-controller/page.tsx`, and `web-access-controller/page.tsx` exist as public local pages.
  - Public `/platform/security/*` routes redirect to the matching local `/platforms/acp/*` canonical routes, not upstream `querypie.com/ja`.
  - `src/app/plans/page.tsx`, `src/app/plans/aip/page.tsx`, and `src/app/plans/acp/page.tsx` exist as public local plans pages.
  - `src/app/pricing/route.ts` redirects `/pricing` to `/plans`; `src/app/pricing/calculator/page.tsx` remains a `notFound()` helper page, not a public calculator implementation.
  - `src/app/sitemap.ts` includes `/plans`, `/plans/aip`, `/plans/acp`, and the four `/platforms/acp/*` child pages.
- When updating `Website-Migration-Plan*` from this baseline, also update `Route-Local-Authoring*`; otherwise the two wiki families can contradict each other.
- In `Route-Local-Authoring*`, remove stale classifications that say:
  - ACP child pages are preview-only, partial, or still pending public local rollout.
  - `/platform/security/*` routes are upstream redirect-only.
  - plans/pricing is only `/t/plans*` preview or still needs public route strategy.
  - ACP integrations is "High after open PR" after the cleanup PR has already merged.
- Remaining route-local authoring priorities after this baseline should focus on `/services/aip`, `/platform/ai/aihub`, `key-values`, and sitemap/indexing follow-up for public legal pages.

### 2026-05-18 baseline (`558a679ab8e22be5e07d6ee8d75e3b975e1a4235`)

- AIP legacy/service aliases changed status; do not keep them as upstream blockers:
  - `src/app/services/aip/route.ts` redirects `/services/aip` to local `/platforms/aip`.
  - `src/app/platform/ai/aihub/route.ts` redirects `/platform/ai/aihub` to local `/platforms/aip`.
  - `src/app/platform/ai/aip/route.ts` redirects `/platform/ai/aip` to local `/platforms/aip`.
- Company legacy aliases changed status:
  - `src/app/company/route.ts` redirects `/company` to local `/about-us`.
  - `src/app/company/news/route.ts` redirects `/company/news` to local `/news`.
  - `/ja/company/news` also redirects locally to `/news` through the localized route handler.
- Legal sitemap/indexing wording changed:
  - `src/app/sitemap.ts` explicitly comments that `/privacy-policy` and `/terms-of-service` are public local legal pages but intentionally noindex, so they are omitted from the sitemap.
  - Do not list privacy/terms sitemap absence as a route-local follow-up or migration gap on this baseline.
- Remaining route-local authoring priorities after this baseline should shrink to optional route-policy only:
  - `key-values` exact legacy URL preservation, because the content is already covered by the value section on `/platforms/aip`.
  - Other long-tail redirects only when real 404/wrong-target evidence appears.
- If adding a new translation variant such as `Route-Local-Authoring-ja`, update `_Sidebar.md` in the same wiki commit under the Migration / Authoring section.

### 2026-05-16 baseline (`9833fda3c1b4a0624b06b9b0bfa3633260d34e61`)

- MDX collection inventory docs were added, but they do **not** expand the scope of `Route-Local-Authoring*`:
  - Mention `docs/mdx-collection-inventory.md` and `docs/mdx-collection-inventory.ko.md` only as adjacent references.
  - Keep publication/content families excluded from the route-local non-MDX backlog.
- Public redirect aliases changed for platform landing pages:
  - `src/app/platforms/aip/route.ts` exists and redirects upstream to the AIP solution page.
  - `src/app/platforms/acp/route.ts` exists and redirects upstream to the ACP solution page.
  - When documenting current public aliases for preview `/t/platforms/aip` and `/t/platforms/acp`, include `/platforms/aip` and `/platforms/acp` alongside older `/services/*` and `/platform/ai/*` aliases where present.
- Plans/pricing preview split changed:
  - Latest main has `src/app/t/plans/aip/page.tsx` and `src/app/t/plans/acp/page.tsx`.
  - `src/app/t/plans/page.tsx` defaults to the AIP view and redirects legacy `?aip` / `?acp` query usage to the corresponding child preview route.
  - Do not describe plans as one undifferentiated `/t/plans` preview only; inventory and priority lists should include `/t/plans/aip` and `/t/plans/acp`.
  - `src/app/pricing/calculator/page.tsx` still only calls `notFound()`, so it remains **not** a public pricing implementation.
- Route exclusion correction:
  - For use-case publications, use canonical `/use-cases` and `/use-cases/:id/:slug` in the excluded MDX/publication scope. Treat `/demo/use-cases*` as legacy redirect wording unless latest main changes the route policy again.
- Practical verification detail:
  - Some local environments do not have `python` as a command alias. If using a quick script to verify wiki file contents, prefer `python3` or plain shell checks before commit/push.

### 2026-05-17 baseline (`ec651e16a2ea65978023bc415645ebedbc65a479`)

- ACP platform pages were published publicly:
  - `src/app/platforms/acp/page.tsx` exists and is the current public local ACP landing page with canonical `/platforms/acp`.
  - `src/app/platforms/acp/integrations/page.tsx` exists and is the current public local ACP integrations page with canonical `/platforms/acp/integrations`.
  - `src/app/services/acp/route.ts` now redirects locally to `/platforms/acp`.
  - Do not leave ACP landing or ACP integrations classified as `/t/platforms/acp` preview-only, public-redirect-only, or route-decision items.
- AIP and FDE public status should also be re-audited against this baseline:
  - `src/app/platforms/aip/page.tsx` and `src/app/platforms/aip/integrations/page.tsx` are public local pages; `/platform/ai/aip` redirects locally to `/platforms/aip`, while `/services/aip` may still redirect upstream.
  - `src/app/services/fde/page.tsx` is the public local FDE page; `/platform/ai/aip/fde-services` redirects locally to `/services/fde`.
  - Do not keep `/t/platforms/aip`, `/t/platforms/aip/integrations`, or `/t/services/fde` as current remaining public-rollout blockers if latest main still matches this baseline.
- ACP child pages remain a separate partial state:
  - `/t/platforms/acp/{database-access-controller,kubernetes-access-controller,system-access-controller,web-access-controller}` preview pages exist.
  - Public `/platform/security/*` routes still redirect upstream, so these are still partial public-local-rollout candidates.
- Sitemap changed again:
  - `src/app/sitemap.ts` includes `/platforms/aip`, `/platforms/aip/integrations`, `/platforms/acp`, `/platforms/acp/integrations`, `/platforms/aip/usage-based-llm`, `/platforms/aip/mcp-gateway`, and `/services/fde`.
  - Continue to record `/privacy-policy` and `/terms-of-service` as public local pages even if they are not static sitemap entries.

## Recommended verification queries

Before finalizing the wiki page, explicitly inspect these latest-main files when relevant:

- `src/app/page.tsx`
- `src/app/about-us/page.tsx`
- `src/app/certifications/page.tsx`
- `src/app/sitemap.ts`
- `src/app/contact-us/page.tsx`
- `src/app/contact-us/submit/route.ts`
- `src/app/privacy-policy/route.ts`
- `src/app/t/privacy-policy/page.tsx`
- `src/app/t/privacy-policy/[slug]/page.tsx`
- `src/app/services/aip/route.ts`
- `src/app/services/acp/route.ts`
- `src/app/services/fde/route.ts`
- `src/app/t/platforms/aip/page.tsx`
- `src/app/t/platforms/acp/page.tsx`
- `src/app/t/services/fde/page.tsx`
- `src/app/t/platforms/aip/integrations/page.tsx`
- `src/app/t/platforms/aip/usage-based-llm/page.tsx`
- `src/app/t/platforms/aip/mcp-gateway/page.tsx`
- `src/app/t/plans/page.tsx`
- `docs/route-local-refactoring-for-developers.md`
- `docs/route-local-refactoring-for-developers.ko.md`
- `docs/static-page-route-local-authoring.md`
- `docs/code-location-conventions.md`
- `.agents/skills/static-page-route-local-authoring/SKILL.md`

Also inspect route-only redirects for these public paths before classifying them as migrated:

- `/cookie-preference`
- `/services/aip`
- `/services/acp`
- `/services/fde`
- `/platform/ai/aip/*`
- `/platform/security/*`
- `/eula`
- `/privacy-policy`
- `/terms-of-service`

Do not put `/about-us` or `/certifications` in the route-only redirect checklist unless current latest main actually removes their public local `page.tsx` routes.
