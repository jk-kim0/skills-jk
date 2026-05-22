# Migrated memory and user context for corp-web-japan

These entries were moved out of global Hermes memory/user profile because they are repository- or platform-specific. Keep them here or split them into narrower workflow skills as they evolve.


## From MEMORY.md


### MEMORY entry 1

In corp-web-japan missing-path redirect work, check runtime-log 404 candidates against corresponding querypie.com paths first; add redirects only for targets that return 200 and are not already namespace-covered. Legacy intro download aliases are `/features/documentation/aip-introduction-download -> /introduction-deck/1/querypie-aip` and `/features/documentation/acp-introduction-download -> /introduction-deck/2/querypie-acp`.


### MEMORY entry 2

In corp-web-japan, repo-internal docs/guidance/comments and PR titles/descriptions should be in English; the site itself is Japanese-only unless the user explicitly reintroduces i18n. The preferred final resource index URIs are `/blog`, `/whitepapers`, and `/events`, with blog/whitepaper articles linking to querypie.com/ja by default. Because the site is not publicly launched yet, preserving existing local content/data or adding legacy redirects for old public URLs is not a default requirement. In review/doc text, `~~Text~~` means do not use that text and `~~Old~~ => New` means replace the old text with the new text.


### MEMORY entry 3

In corp-web-japan, deployment/governance facts are: staging URL `https://stage.querypie.ai`; representative production URL `https://querypie.ai` with alternate URLs redirecting there; JK owns deployment secrets/vars and is rollback authority; major deploy/rollback issues go to `#jp-marketing`; broader-impact production deploys require approval from either Keizo or Brant, while minor general-change deploys can proceed on the judgment of Chikako, Jane, or JK.


### MEMORY entry 4

In corp-web-japan, the user does not want repository documentation added for operational facts that are already clear internally unless there is a strong need.


### MEMORY entry 5

The corp-web-japan GitHub wiki repository is locally cloned at ../corp-web-japan.wiki relative to the main repo.


### MEMORY entry 6

In corp-web-japan, the `/events` route currently exists as a functional page shell before content is ready; it is not part of the current public launch scope.


### MEMORY entry 7

In corp-web-japan blog migration work, the user does not want broad synthetic labels like 'multilingual route support'; prefer explicit per-locale facts such as 'EN/JA/KO detail pages and public blog list route are implemented.'


### MEMORY entry 8

In corp-web-japan whitepaper migration work, external download CTA links are intentionally correct for at least whitepapers 24 and 30; do not remove them as regressions. Treat proper support for external whitepaper download CTA behavior as a follow-up implementation concern rather than deleting the CTA.


### MEMORY entry 9

In corp-web-japan, follow the repo AGENTS rule that PR titles/descriptions (and repo-internal docs/guidance/comments) must be written in English, even if the user's broader repo preference elsewhere may differ.


### MEMORY entry 10

In corp-web-japan about-us preview work, the user prefers the migrated static assets under public/about-us rather than public/t/about-us, even when the preview route itself is /t/about-us.


### MEMORY entry 11

In corp-web-japan, when a refactor workflow is likely to be repeated across sessions/pages, the user wants it generalized into a repo-local skill under `.agents/skills/` and delivered as a PR rather than kept only as an ad hoc prompt.


### MEMORY entry 12

In corp-web-japan static-page route-local authoring, docs/code-location-conventions.md can be outdated; the user's desired target pattern is current src/app/page.tsx on latest main, src/app/solutions/ai-dashi/page.tsx is only partially refactored toward that goal, and src/app/solutions/ai-crew/page.tsx is the archetypal pre-refactor anti-pattern.


### MEMORY entry 13

In corp-web-japan static-page authoring, src/app/**/page.tsx should contain the copy text and the calls/composition that use components, while src/components/sections/** should define the components used by page.tsx and hold the style/UI/UX implementation details such as classes, JavaScript, and styling behavior.


### MEMORY entry 14

In corp-web-japan main as of 2026-05-03, local `next build --webpack` fails on an existing baseline CSS Modules error in `src/components/layout/site-header.module.css`: `:root` selector is not pure. This is independent of the use-cases MDX migration branch.


### MEMORY entry 15

In corp-web-japan static-page route-local authoring work, the user wants PR 155–158 style section-scoped migration: move one section's copy ownership into page.tsx per PR, keep temporary shared shells if needed, and do not implement by passing giant raw JSX section blobs as props from the route.


### MEMORY entry 16

In corp-web-japan static-page route-local authoring, the user does not consider it sufficient to move prose-heavy top-level arrays into large local helper functions inside page.tsx (e.g. SupportSection/ReleaseFlowSection). The route body itself should remain readable: reviewers should be able to see migrated section heading/body/CTA/composition directly from the default export body, not just opaque helper calls.


### MEMORY entry 17

In corp-web-japan latest main, the shared gradient CTA button component is `src/components/ui/brand-gradient-cta-button.tsx` exporting `BrandGradientCtaButton`; if the user refers to a shared 'Brant/Brand gradient CTA button', this is the component to use.


### MEMORY entry 18

In corp-web-japan, for resource/documentation migration work, the user does not want glossary, introduction-deck, and manuals grouped under a single generic `documentation` type. Treat them as distinct content types like blog/whitepaper/event. If shared logic is needed, prefer a common `resource` abstraction layer (e.g. TypeScript abstract base class + concrete per-type implementations) rather than one merged `documentation-publications.ts` style loader.


### MEMORY entry 19

In corp-web-japan resource preview/publication work, the user explicitly does not want the source content directory name `documentation` used for these families either; avoid paths like `src/content/documentation/**` and prefer route/resource-aligned roots such as `src/content/resources/<family>`.


### MEMORY entry 20

In corp-web-japan section-scoped static-page refactors, preserve the original rendered section order. If extracting a later section (e.g. use-cases) would move it ahead of an earlier section still trapped in a shared shell (e.g. platform), refactor the earlier section first or split the shared shell before extracting the later one.


### MEMORY entry 21

In corp-web-japan CTA primitive refactors, the user prefers the section wrapper to be named `SimpleCtaSection` rather than the more generic `CtaSection`, while keeping child primitive names like `CtaContent`, `CtaCopy`, `CtaTitle`, `CtaDescription`, and `CtaActions` unchanged.


### MEMORY entry 22

In corp-web-japan preview-site parity work, the user wants the preview website to keep a standard 16px root rem setup; when matching a live site that uses a 15px root, adjust component token sizes/spacing for visual parity rather than changing the preview site's root font-size.


### MEMORY entry 23

In corp-web-japan preview page imports from querypie.com/ja or /en, source pages may use html root 15px while corp-web-japan should keep root 16px; do not blindly copy computed px values—recover rem/token intent first and convert for the 16px-root preview environment. Repo-local skill: `.agents/skills/preview-root-rem-parity/SKILL.md`.


### MEMORY entry 24

In corp-web-japan MDX/resource docs, the user prefers family-separated content roots and collection inventories covering endpoints, src/content roots, public asset roots, loader sources, frontmatter support, and legal pages separately.


### MEMORY entry 25

In corp-web-japan preview resource publication work, the user is concerned about slug-as-id patterns like `glossary/glossary` and leans toward stable numeric content IDs/files (e.g. `src/content/glossary/1.mdx` with `id: "1"` and separate canonical `slug`) for `/t/introduction-deck`, `/t/glossary`, and `/t/manuals` detail routes.


### MEMORY entry 26

In corp-web-japan PR follow-up work, gh pr view can briefly lag after push; verify the actual remote branch tip with `git ls-remote origin refs/heads/<pr-branch>` before assuming the PR head failed to update.


### MEMORY entry 27

In corp-web-japan typography work, the user prefers site-wide consistency over route-local parity exceptions: do not keep `/t/about-us` as a special text-color or body-typography exception; align it to shared site defaults instead. Current documented defaults are route-level `main` `text-slate-950`, ordinary descriptive/body copy `text-slate-600`, and for marketing/company body copy the preferred default is `15px/28px` (`text-[15px] leading-7`) unless a different shared pattern is explicitly required.


### MEMORY entry 28

In corp-web-japan route policy, use-case list and detail routes are top-level `/use-cases` and `/use-cases/:id/:slug`; AIP/ACP demo list/detail routes remain under `/demo/aip` and `/demo/acp`.


### MEMORY entry 29

In corp-web-japan, .github/workflows/ci.yml and deploy-preview.yml both support workflow_dispatch. If a PR branch push updates head SHA but GitHub does not attach new synchronize runs, manual dispatch on the PR branch can still validate the current head.


### MEMORY entry 30

In corp-web-japan manuals work, the real replacement target for legacy /api-docs.html is https://docs.querypie.com/ja/api-reference.


### MEMORY entry 31

In corp-web-japan, Vercel WAF custom rules are now managed as a repo-committed source of truth under ops/vercel-firewall/, with a project-specific JSON payload plus README, and applied project-scoped via full PUT to /v1/security/firewall/config for corp-web-japan.


### MEMORY entry 32

In corp-web-japan news rollout, direct redirects/opening to external media pages for local news items are intentionally avoided because external media links often break; local /news detail rendering is preferred over direct external card navigation.


### MEMORY entry 33

In corp-web-japan event MDX, add `eventDate` only when the body explicitly states a concrete event date; do not infer it from frontmatter `date` or add it to hidden shadow redirect records without explicit source evidence.


### MEMORY entry 34

Repo-specific rule for corp-web-japan: promoted/replaced preview /t/* endpoints should be removed entirely by default, not preserved as redirects. Only keep a /t/* route if the user explicitly requests that exact compatibility path.


### MEMORY entry 35

In corp-web-japan sitemap policy, hidden MDX records should be excluded from sitemap.xml by default, but hidden records with redirectUrl must still be exposed in sitemap.xml so bot-indexable local canonical detail pages remain discoverable.


### MEMORY entry 36

In corp-web-japan repo-local blog/whitepaper posting skills, preserve the explicit contract that files are named `src/content/{blog,whitepapers}/<id>-<slug>.mdx` and that the canonical route slug source of truth remains frontmatter `slug`; do not replace this with vague 'route-readable filename' guidance.


### MEMORY entry 37

In corp-web-japan migration/status planning, existing blog/whitepaper hidden/redirect/gated records are intentional and should not be resurfaced as generic cleanup work unless the user explicitly asks to revisit that policy or there is a concrete regression.


### MEMORY entry 38

In corp-web-japan migration planning, do not surface content-volume/completeness concerns like small AIP demo corpus as remaining work unless the user explicitly asks; evaluate from the migration/route-replacement lens, not content-richness.


### MEMORY entry 39

In corp-web-japan migration-status docs, evaluate only whether existing querypie.com/ja content/functionality is migrated/replaced locally; do not frame content richness or intentional hidden/redirect/gated states as gaps. Keep Website-Migration-Plan* and Route-Local-Authoring* consistent when latest-main route statuses change.


### MEMORY entry 40

In corp-web-japan whitepapers, downloadable PDF CTA metadata is now modeled explicitly in MDX frontmatter as `downloadCta: { href, label, external }`, and route-aligned local PDF assets live under `public/whitepapers/<id>/download.pdf`.


### MEMORY entry 41

In corp-web-japan publication-helper planning, the user wants the current low-level duplication between create-standard-publication-post-loader.ts and create-gated-publication-post-loader.ts kept as-is for now; only consider further refactoring later if duplicated code grows materially.


### MEMORY entry 42

In corp-web-japan legal preview work, route-local self-contained placement under src/app/t/<route>/ can be preferable to broad src/content/legal-preview + src/lib/legal-preview indirection; for versioned privacy-policy previews, the user expects `src/app/t/privacy-policy/[slug]/page.tsx` to own page composition while `src/app/t/privacy-policy/page.tsx` may remain a thin latest-version wrapper that derives the last document date.


### MEMORY entry 43

In corp-web-japan, for standalone static/legal preview pages like terms-of-service, the user prefers route-local MDX colocation: keep page.tsx and content.mdx in the same route directory (e.g. src/app/t/terms-of-service/) rather than placing the MDX under src/content.


### MEMORY entry 44

In corp-web-japan whitepaper download flow, the user wants `gated: true` whitepapers to show a CTA near the start of the visible article body that links to a dedicated `/whitepapers/:id/:slug/download` gating page; that download page should use the portrait PDF cover image (not the article thumbnail), and Preview Toggle should bypass the download gating form and open the PDF directly.


### MEMORY entry 45

In corp-web-japan publication UX, the user expects introduction-deck gated download CTA buttons to appear in the unlocked gated section directly below the `資料ダウンロード` explanatory copy, not above the gating form; also treat whitepaper article-body CTA links to `/whitepapers/{id}/{slug}/download` as an intentional second gating step rather than a direct PDF-download link.


### MEMORY entry 46

In corp-web-japan mobile resource/demo sidebar UX, after comparing alternatives the user chose the bottom-sheet/drawer navigation pattern over the block-list/grid pattern as the preferred final direction.


### MEMORY entry 47

In corp-web-japan service preview parity work, when the user asks to fix multiple `/t/services/*` pages together (such as ACP and FDE), they want each page handled in its own fresh worktree and its own separate PR, not bundled into one combined PR.


### MEMORY entry 48

In corp-web-japan PR follow-up or route-local review work, if a requested route/file is missing on current main/PR head, do not assume it should be restored from history. Report the absence first and confirm scope before reviving an old route subtree.


### MEMORY entry 49

In corp-web-japan, the user wants remaining legacy `/posts/` route/code/content remnants removed entirely rather than preserved for event compatibility.


### MEMORY entry 50

In corp-web-japan path taxonomy work, the user wants the temporary `t-` prefix kept only in app route paths; do not use `t-` in component or test family names. Use neutral family names like `aip`, `acp`, and `fde` instead of `t-services-aip`, `t-services-acp`, or `t-services-fde`.


### MEMORY entry 51

In corp-web-japan path taxonomy naming, the user wants a single canonical family name chosen on general convention rather than current code habit; use `home` instead of `top-page` for the homepage component/test family.


### MEMORY entry 52

In corp-web-japan, default text content width is 1200px unless a side-by-side image/media layout narrows it; for legal/document preview pages, `max-w-[920px]` is incorrect and should not be preserved.


### MEMORY entry 53

In corp-web-japan test structure work, the user wants only genuinely reusable infra helpers kept in shared test helper locations; page-specific or page-family-specific helpers should be colocated near the relevant mirrored test paths instead of centralized under tests/helpers.


### MEMORY entry 54

corp-web-japan main requires `Detect changed scope`, but ci.yml pull_request ignores docs/README/AGENTS/public md/skills md changes, so docs-only PRs can miss the required check.


## From USER.md


### USER entry 1

User says there is no policy that the Japanese site's default font must be Pretendard JP; do not treat that as a constraint.


### USER entry 2

For corp-web-app/corp-web-japan route-local authoring, user wants visible JSX copy/links/composition, not JSON-like registries; corp-web-app GitHub wiki docs are Korean by default.


### USER entry 3

For corp-web-japan, user prefers CI over local builds/dev servers unless requested. For QueryPie micro-sites, user prefers monorepo and clear routing/assets over hidden middleware rewrites.


### USER entry 4

When documenting corp-web-japan issues or link audit tables, the user prefers all links written in markdown [path](url) format, wants a Korean translation column next to Japanese labels, and when showing Japanese text to the user expects a Korean translation in parentheses immediately after it.


### USER entry 5

Whenever showing Japanese text to the user, include the Korean translation immediately after it in parentheses.


### USER entry 6

For corp-web-japan contact-us rollout, keep `/t/contact-us` as the feature-flag public form route until final validation/testing is complete; only at the very end should the existing `/contact-us` public entry be switched with a minimal route change. The approved structure is: use `/contact-us/submit` as the submit endpoint, keep app route code thin, and place backend implementation in reusable shared locations such as `src/lib` or `src/components` rather than route-local heavy logic.


### USER entry 7

When cleaning stale corp-web-japan worktrees, a worktree whose only remaining dirt is .hermes/ local runtime state and whose remote branch/PR is already merged should be deleted rather than preserved.


### USER entry 8

For top-page refactors in corp-web-japan, the user's key requirement is not just moving copy into page.tsx, but authoring it as direct JSX like <Component>marketing text</Component> rather than large JSON-like props/objects in page.tsx.


### USER entry 9

When the user points to a specific Preview Deployment URL and reports a visual discrepancy, verify that exact deployed URL directly in the browser; local render alone is not sufficient because preview and local spacing/UX can differ.


### USER entry 10

In corp-web-japan static-page route-local authoring refactors, even when the scope is reduced to one or a few sections, the user expects each targeted section to be fully refactored: section implementation should be extracted under src/components/sections, while page.tsx should retain the section copy/data/composition. Page-local helper section components inside page.tsx are not considered complete.


### USER entry 11

In corp-web-japan static-page route-local authoring refactors, the user expects refactor-only PRs to preserve the existing UI exactly unless they explicitly request a design change. Preserve box/button wrapper classes, icons, spacing, and overall visual parity rather than re-styling while moving copy ownership.


### USER entry 12

In corp-web-japan static-page route-local authoring refactors, the user does not want section components to infer highlighted marketing copy by string matching; highlighted words/phrases should be authored explicitly in page.tsx JSX so copy emphasis ownership stays route-local.


### USER entry 13

In corp-web-japan route-local authoring, the user prefers section/card subtitles and similar small marketing copy to be authored as child elements in page.tsx rather than passed via prop fields like subtitle=.


### USER entry 14

For corp-web-japan static marketing copy, the user prefers semantic emphasis in route-local JSX via `<strong>...</strong>` rather than presentation-heavy inline `<span className=...>` markup; visual highlight styling should live in the wrapper/section component.


### USER entry 15

In corp-web-japan resource-list refactors, the user wants page.tsx to keep route-authored hero (`ResourceListHeroSection`, `ResourceListHeroTitle`, `ResourceListHeroDescription`) and CTA sections visible, while only the repeated sidebar block may be extracted. For naming, prefer context-specific React terms and names over vague ones: keep `ResourceListSidebar*` primitives rather than renaming them to `Generic*`, and prefer a specific composed name like `ResourceCategorySidebar`/`ResourceListCategorySidebar` over broad names like `PublicResourceSidebar` when possible.


### USER entry 16

In corp-web-japan PR follow-up scope, removing demo /t entrypoints does not imply removing the general Preview Toggle UI or its API route. Keep that scope narrow unless the user explicitly asks to remove the global preview toggle.


### USER entry 17

When reviewing corp-web-japan publication/routing changes, the user expects priority on finding missing hidden-posting or redirect configuration/canonicalization gaps, not just whether a PR is stale or mergeable.


### USER entry 18

In corp-web-japan copy/content follow-up work, if the user asks to correct a mistaken title/label in an existing content item, prefer preserving the item and fixing the exact wording rather than deleting the page or replacing it with a broader structural change.


### USER entry 19

In corp-web-japan publication/routing audits, the user wants review focus on actual missing redirects and wrong redirect targets on the latest origin/main baseline, not on 'shrink/removal candidates.' Evidence should be prioritized from latest main code, route implementation, and stage/live behavior.


### USER entry 20

In corp-web-japan, when preview /t/* routes are promoted or replaced, the user does not want the /t/* endpoints kept at all and does not want redirect compatibility left behind, unless they explicitly ask for a specific /t/* path to remain. Default policy: remove /t/* route files entirely, not redirect them.


### USER entry 21

For querypie.com/ja page migrations in corp-web-japan, the user wants the existing page copied as-is without invented preview explanation text, rewritten title/description copy, or new CTA sections unless explicitly requested.


### USER entry 22

For corp-web-japan and similar repo work, any reusable migration/workflow skill should be provided as a repo-local skill under .agents/skills/, not only as a built-in/global skill.
