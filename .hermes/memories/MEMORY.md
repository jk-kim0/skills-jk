In the skills-jk repo, Hermes runtime/setup facts are: portable state lives in tracked `.hermes/config.yaml`, `.hermes/memories/`, `.hermes/skills/`, and repo `skills/`; session-like records remain machine-local; runtime artifacts such as checkpoints, sessions, logs, caches, generated `.hermes/.env`, and other transient state stay untracked; the active runtime in this setup uses `HERMES_HOME=~/workspace/skills-jk/.hermes`, with session files under `.hermes/sessions`; the local Hermes CLI is git-installed under `~/.hermes/hermes-agent` and exposed via `~/.local/bin/hermes`.
§
In the skills-jk repo, PR creation uses the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` via `workflow_dispatch`; it is the preferred PR creation path for this repo.
§
In corp-web-v2, the user expects each PR task to start from a fresh worktree and fresh branch; do not continue new requested work on a previously used PR branch because it can cause rebase conflicts and stale PR state.
§
In querypie-docs, confluence-mdx is a Python-based bidirectional Confluence↔MDX pipeline. Main forward flow: bin/fetch_cli.py (Confluence API/local cache -> var/) -> bin/convert_all.py (batch over var/pages.<sync_code>.yaml) -> bin/converter/cli.py (single-page XHTML -> MDX, generates mapping.yaml and _meta.ts).
§
In querypie-docs confluence-mdx, important data directories are var/ and cache/. var/ is the active working dataset with one directory per Confluence page_id plus pages.qm.yaml catalog and reverse-sync artifacts; each page directory commonly contains page.v1.yaml, page.v2.yaml, children.v2.yaml, attachments.v1.yaml, page.xhtml/html/adf, and mapping.yaml. cache/ mirrors page-level source data for reuse when fetching attachments/content.
§
In querypie-docs confluence-mdx, reverse sync is centered on bin/reverse_sync_cli.py plus bin/reverse_sync/*. It diffs original vs edited MDX, maps changes back to XHTML using sidecar mapping.yaml, writes reverse-sync.* artifacts under var/<page_id>/, forward-converts patched XHTML to verify.mdx, and validates round-trip before optional Confluence push. docs/architecture.md and docs/analysis-reverse-sync-refactoring.md document this as a major, actively evolving subsystem.
§
In querypie-docs confluence-mdx, container usage is standardized through compose.yml and scripts/entrypoint.sh. The container exposes fetch_cli.py, convert_all.py, converter/cli.py, full, full-all, and status commands; it mounts ../src/content/{ko,en,ja} and ../public onto target/ symlink destinations, and uses ATLASSIAN_USERNAME plus ATLASSIAN_TOKEN from .env/environment for API access.
§
In querypie-docs confluence-mdx reverse_sync, build_patches in bin/reverse_sync/patch_builder.py is the main decision engine: it classifies each MDX block change into direct/containing/list/table/skip, relies on sidecar lookup plus roundtrip sidecar v3 identity fallback, and produces modify/delete/insert/replace_fragment patches while collecting skipped_changes reasons like no_mapping, missing_roundtrip_sidecar, preserved_anchor_table, and unsafe_html_table_edit.
§
In querypie-docs confluence-mdx reverse-sync planning, the user considers current table support sufficient for now; prioritize verifier-side handling so whitespace differences or column-width-only differences are treated as matches rather than mismatches.
§
In querypie-docs confluence-mdx reverse-sync planning, the user supports using planner / strategy / proof as the main axis for codebase cleanup and architectural reorganization.
§
In querypie-docs confluence-mdx reverse-sync planning, treat `tests/reverse-sync/pages.yaml` as straightforward and non-core: in real-data usage it is just a reference metadata catalog for reverse-sync, and extra fields exist only for testcase implementation; do not overcomplicate its role.
§
When investigating legacy corp-web-contents blog/localization history, the user expects ID-based pattern matching across all historical path families and related MDX/meta files, not just current canonical `content.mdx` paths. Search broad `blog` + `/<id>/` matches first, then classify EN/JA/KO MDX vs meta.
§
In querypie-docs confluence-mdx reverse-sync planning, the user prefers verifier taxonomy to be classified in more detail.
§
In corp-web-v2, the built-in CMS is not a fully browser-operated remote CMS in practice: it behaves more like a GUI editor for file-based content, and edits still require running a local CMS server plus committing/pushing the resulting file changes.
§
In corp-web-v2 content gating discussions, the user prefers an explicit in-body marker/cut point (e.g. MDX/Tiptap markup) over percentage-based gating levels, because it makes the preview boundary clear and intentional.

In corp-web-v2, before creating a new PR branch, update from origin/main and verify the branch merge-base is origin/main (or its tip ancestor) so merged commits from stale branches are not accidentally included in the PR.
§
In corp-web-v2, blog and white-paper MDX migration is already present under src/content/mdx; do not treat those families as still pending migration work.
§
In corp-web-v2, git worktrees keep per-worktree `node_modules` / `package-lock` state rather than a shared install, so fresh or older worktrees can show false baseline errors like `Cannot find module mermaid`; however, targeted Vitest runs may still resolve dependencies from the parent repo-root `node_modules`, so a separate worktree-local install is not always required.
§
In corp-web-japan missing-path redirect work, check runtime-log 404 candidates against corresponding querypie.com paths first; add redirects only for targets that return 200 and are not already namespace-covered. Legacy intro download aliases are `/features/documentation/aip-introduction-download -> /introduction-deck/1/querypie-aip` and `/features/documentation/acp-introduction-download -> /introduction-deck/2/querypie-acp`.
§
In corp-web-v2 demo routing, canonical detail paths use short public routes: ACP `/demo/acp/:id/:slug`, AIP `/demo/aip/:id/:slug`, use-cases `/demo/use-cases/:id/:slug`, and webinars `/webinars/:id/:slug`; the AIP Google OAuth page is `/demo/aip/1/google-oauth-demo`, and older `/features/demo/**` or `/demo/webinar/**` paths should be treated as legacy/history rather than current canonical paths.
§
In corp-web-v2 author-box work, the component file was renamed from src/components/mdx-layout/ArticleAuthorBox.tsx to src/components/mdx-layout/AuthorBox.tsx per user preference for shorter names.
§
In corp-web-v2, article author profile assets live under public/crew/*, and locale author registry data now lives in src/features/mdx/authors/{en,ko,ja}.yaml with profileImage paths like crew/<file>; the server-only authors module parses the YAML at runtime.
§
In corp-web-v2 demo migration work, keep ACP MDX routes/rendering fully separate from CMS-managed demo content, source demo detail content from ../corp-web-contents original EN/KO/JA MDX files rather than CMS-authored Tiptap/HTML data, and do not modify the existing CMS-managed `src/app/[locale]/features/demo/[slug]/page.tsx` rendering path when working on ACP MDX migration.
§
In corp-web-contents, demo MDX source lives under pages/features/demo/{aip-features,use-cases,webinars,acp-features}/<id>/<slug>/<locale>/content.mdx; current counts are AIP 1, use-cases 29, webinars 26, ACP 26. The frontmatter commonly uses legacy category slugs, hideOgImage, ogImage paths under public/demo/* or public/webinar/*, and relatedPosts paths pointing at legacy /features/demo/... URLs; referenced assets come from public/demo, public/customer-success-cases, public/webinar, and for older ACP also public/tutorial.
§
In corp-web-v2 content migration audits, the user considers content migration complete only when the content is actually migrated to MDX; non-MDX managed content/HTML/Tiptap routes should be treated as not yet completed migration.
§
In corp-web-v2 Solutions parity work, legacy canonical content lives under corp-web-contents/pages/solutions/{aip,acp}/** with 11 canonical routes total; locale gaps exist for acp/ko and aip/integrations/ko, where legacy behavior effectively falls back to English.
§
For corp-web-v2 Solutions page migration, required legacy public assets come mainly from corp-web-contents/public/{aip,acp,products,tutorial,introducing-querypie,key-feature-icon,integration-icon}, while /assets/dac-analyzer.json comes from corp-web-app/public/assets rather than corp-web-contents.
§
In corp-web-v2, do not assume `npm run lint` / `npx eslint` are available as standard verification steps; first verify the repo's package scripts and ESLint config, and otherwise rely on the repo’s actual test/typecheck/build checks.
§
In corp-web-v2 wiki migration planning, the user wanted duplicate planning/readiness pages removed entirely after consolidation, not just marked as superseded; Home/wiki should be rewritten around the latest canonical docs.
§
In corp-web-v2 public content routing, list-page paths and individual content-detail paths should share the same prefix. Canonical naming uses singular `/blog`, plural `/white-papers`, plural `/demo/use-cases`, top-level `/webinars`, and short fixed demo segments `/demo/acp` and `/demo/aip`; older `/demo/webinar/**` or `/features/**` demo routes are legacy/history rather than current canonical paths.
§
In corp-web-v2 Solutions follow-up work, the user wants inline images/assets reorganized under route-aligned public paths matching page structure, e.g. assets referenced by a Solutions page should live under public/path/solutions/<slug>/... rather than broad shared folders like public/aip or public/products.
§
In corp-web-v2 demo migration follow-up, the user does not want legacy URL redirects included in the current PR; redirect rules should be audited and implemented later in a separate batch.
§
In corp-web-v2 demo/content asset normalization, the user wants thumbnail filenames standardized to thumbnail.png when locale-agnostic and thumbnail-<locale>.png when locale-specific (e.g. thumbnail-en.png, thumbnail-ko.png, thumbnail-ja.png).
§
In corp-web-v2 on Vercel, API routes that access generic `process.cwd()/public` paths can cause output tracing to bundle large unrelated public assets and exceed serverless size limits. Prefer narrowing file access to explicit subdirectory roots (e.g. specific `public/demo` or `public/documentation` paths) rather than generic public-root joins.
§
In corp-web-v2 wiki documentation, the user prefers related route-policy follow-up details such as mismatch tables to be appended under the existing canonical wiki page rather than split into a separate page.
§
In corp-web-v2 migration work, the user wants stage-v2.querypie.com validated by directly visiting the live stage site and the results documented as a GitHub wiki E2E verification report, not inferred only from code or inventory tables.
§
In corp-web-v2 demo MDX migration work, the user wants CMS-connected demo files left untouched: do not modify `src/app/[locale]/features/demo/page.tsx`, `src/app/[locale]/features/demo/[slug]/page.tsx`, admin demo pages, or content-state/authored-server flows unless explicitly requested.
§
In corp-web-v2 Solutions parity work, the user does not want placeholder or legacy alias redirects included in the migration PR; for an unopened site, updating GNB/header/footer links to canonical Solutions pages is sufficient, and redirect rules should be analyzed/applied separately later.
§
In corp-web-v2, when squashing an open PR branch after origin/main has advanced, use the PR branch's merge-base with origin/main as the soft-reset point, not current origin/main, or unrelated main-only changes can be pulled into the squashed commit.
§
In corp-web-v2, Solutions parity is implemented via src/app/[locale]/solutions/[[...slug]]/page.tsx with content under src/content/solutions/** and route mapping in src/features/solutions/routes.ts.
§
In corp-web-v2, if `src/content/mdx` contains only blog and white-paper families, treat demo MDX source as not yet migrated in that repo snapshot.
§
In corp-web-v2 route-policy follow-up work, when renaming canonical public content paths like white-paper -> white-papers, the user wants code routes, MDX links, and public asset/image directories updated consistently in one pass to match the wiki naming convention.
§
In corp-web-v2 Solutions work, the user wants `/solutions/**` pages implemented as individual static `page.tsx` routes rather than an MDX-rendered catch-all, because most Solutions content is considered unsuitable for MDX.
§
In corp-web-v2 wiki/content migration audits, /features/** should be treated as legacy-only paths. A family counts as implemented only if it is exposed on a separate non-/features public URI; /features presence alone does not count.
§
For corp-web-v2 content restoration, the user wants missing MDX locale files and related assets recovered from corp-web-contents git history when possible, not recreated speculatively.
§
In corp-web-v2, the Public-Content-URL-Naming-Convention requires the white-paper public route family to use plural `/white-papers` with aligned app routes, MDX source/public asset paths, and related internal links; do not keep singular `/white-paper` for that family.
§
In corp-web-v2 Solutions static-page work, the user wants file/directory structure for localized page-content modules to mirror the nested src/app route slug structure and avoid flat legacy names such as acp-database-access-controller.
§
In corp-web-v2 route-policy work, the user wants the webinars family to use top-level `/webinars` for the public list route as well, not `/demo/webinars`; align code and the Public-Content-URL-Naming-Convention wiki in the same batch.
§
In corp-web-app MDX migration, tutorials and manuals are distinct; tutorials from `page-archives/learn/tutorials/**` use `src/content/tutorials/<category>/<id>-<slug>.{locale}.mdx` and `public/tutorials/<category>/<id>/...`, not manuals or flat `dac-1` paths.
§
In corp-web-v2 Public-Content-URL-Naming-Convention updates, treat src/app/[locale]/features/demo/page.tsx and src/app/[locale]/features/documentation/page.tsx as legacy-only paths; do not count them as migration targets or implementation results.
§
In corp-web-v2 blog/white-paper MDX, the canonical upstream slug from corp-web-contents is now stored explicitly as frontmatter `slug` in each `src/content/mdx/blog/<id>/<locale>.mdx` and `src/content/mdx/white-papers/<id>/<locale>.mdx`, while the directory name remains the numeric content ID.
§
In corp-web-japan, repo-internal docs/guidance/comments and PR titles/descriptions should be in English; the site itself is Japanese-only unless the user explicitly reintroduces i18n. The preferred final resource index URIs are `/blog`, `/whitepapers`, and `/events`, with blog/whitepaper articles linking to querypie.com/ja by default. Because the site is not publicly launched yet, preserving existing local content/data or adding legacy redirects for old public URLs is not a default requirement. In review/doc text, `~~Text~~` means do not use that text and `~~Old~~ => New` means replace the old text with the new text.
§
In corp-web-japan, deployment/governance facts are: staging URL `https://stage.querypie.ai`; representative production URL `https://querypie.ai` with alternate URLs redirecting there; JK owns deployment secrets/vars and is rollback authority; major deploy/rollback issues go to `#jp-marketing`; broader-impact production deploys require approval from either Keizo or Brant, while minor general-change deploys can proceed on the judgment of Chikako, Jane, or JK.
§
In corp-web-japan, the user does not want repository documentation added for operational facts that are already clear internally unless there is a strong need.
§
The corp-web-japan GitHub wiki repository is locally cloned at ../corp-web-japan.wiki relative to the main repo.
§
In corp-web-japan, the `/events` route currently exists as a functional page shell before content is ready; it is not part of the current public launch scope.
§
Hermes session files for this setup are stored under ~/workspace/skills-jk/.hermes/sessions, and direct file inspection there can reveal recent Telegram sessions beyond what session_search returns.
§
For searching all historical file paths in a git repo and filtering by substring, the user uses the one-liner: git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep '<substring>'.
§
In corp-web-japan blog migration work, the user does not want broad synthetic labels like 'multilingual route support'; prefer explicit per-locale facts such as 'EN/JA/KO detail pages and public blog list route are implemented.'
§
In corp-web-japan whitepaper migration work, external download CTA links are intentionally correct for at least whitepapers 24 and 30; do not remove them as regressions. Treat proper support for external whitepaper download CTA behavior as a follow-up implementation concern rather than deleting the CTA.
§
For repo-specific E2E/stage assertions, first verify the current workspace via cwd/pwd and do not mix corp-web-v2, corp-web-app, and corp-web-japan environments.
§
E2E stage targets are repo-specific: corp-web-v2 -> https://stage-v2.querypie.com, corp-web-app -> https://stage.querypie.com, corp-web-japan -> https://stage.querypie.ai.
§
In corp-web-japan, follow the repo AGENTS rule that PR titles/descriptions (and repo-internal docs/guidance/comments) must be written in English, even if the user's broader repo preference elsewhere may differ.
§
For this user, when they say 'repo 의 workspace 정리' or similar, interpret it as repo-local cleanup only: clean the current repository's stale worktrees/branches and local residue, not the whole ~/workspace. Keep going across follow-up turns until the repo is as clean as safely possible, including cleaning root-local residue and fast-forwarding root main to origin/main when safe.
§
In corp-web-japan about-us preview work, the user prefers the migrated static assets under public/about-us rather than public/t/about-us, even when the preview route itself is /t/about-us.
§
In corp-web-japan, when a refactor workflow is likely to be repeated across sessions/pages, the user wants it generalized into a repo-local skill under `.agents/skills/` and delivered as a PR rather than kept only as an ad hoc prompt.
§
In corp-web-japan static-page route-local authoring, docs/code-location-conventions.md can be outdated; the user's desired target pattern is current src/app/page.tsx on latest main, src/app/solutions/ai-dashi/page.tsx is only partially refactored toward that goal, and src/app/solutions/ai-crew/page.tsx is the archetypal pre-refactor anti-pattern.
§
In corp-web-japan static-page authoring, src/app/**/page.tsx should contain the copy text and the calls/composition that use components, while src/components/sections/** should define the components used by page.tsx and hold the style/UI/UX implementation details such as classes, JavaScript, and styling behavior.
§
In corp-web-japan main as of 2026-05-03, local `next build --webpack` fails on an existing baseline CSS Modules error in `src/components/layout/site-header.module.css`: `:root` selector is not pure. This is independent of the use-cases MDX migration branch.
§
In corp-web-japan static-page route-local authoring work, the user wants PR 155–158 style section-scoped migration: move one section's copy ownership into page.tsx per PR, keep temporary shared shells if needed, and do not implement by passing giant raw JSX section blobs as props from the route.
§
In corp-web-japan static-page route-local authoring, the user does not consider it sufficient to move prose-heavy top-level arrays into large local helper functions inside page.tsx (e.g. SupportSection/ReleaseFlowSection). The route body itself should remain readable: reviewers should be able to see migrated section heading/body/CTA/composition directly from the default export body, not just opaque helper calls.
§
In corp-web-japan latest main, the shared gradient CTA button component is `src/components/ui/brand-gradient-cta-button.tsx` exporting `BrandGradientCtaButton`; if the user refers to a shared 'Brant/Brand gradient CTA button', this is the component to use.
§
In corp-web-japan, for resource/documentation migration work, the user does not want glossary, introduction-deck, and manuals grouped under a single generic `documentation` type. Treat them as distinct content types like blog/whitepaper/event. If shared logic is needed, prefer a common `resource` abstraction layer (e.g. TypeScript abstract base class + concrete per-type implementations) rather than one merged `documentation-publications.ts` style loader.
§
In corp-web-japan resource preview/publication work, the user explicitly does not want the source content directory name `documentation` used for these families either; avoid paths like `src/content/documentation/**` and prefer route/resource-aligned roots such as `src/content/resources/<family>`.
§
In corp-web-japan section-scoped static-page refactors, preserve the original rendered section order. If extracting a later section (e.g. use-cases) would move it ahead of an earlier section still trapped in a shared shell (e.g. platform), refactor the earlier section first or split the shared shell before extracting the later one.
§
In corp-web-japan CTA primitive refactors, the user prefers the section wrapper to be named `SimpleCtaSection` rather than the more generic `CtaSection`, while keeping child primitive names like `CtaContent`, `CtaCopy`, `CtaTitle`, `CtaDescription`, and `CtaActions` unchanged.
§
In corp-web-japan preview-site parity work, the user wants the preview website to keep a standard 16px root rem setup; when matching a live site that uses a 15px root, adjust component token sizes/spacing for visual parity rather than changing the preview site's root font-size.
§
In corp-web-japan preview page imports from querypie.com/ja or /en, source pages may use html root 15px while corp-web-japan should keep root 16px; do not blindly copy computed px values—recover rem/token intent first and convert for the 16px-root preview environment. Repo-local skill: `.agents/skills/preview-root-rem-parity/SKILL.md`.
§
In corp-web-japan MDX/resource docs, the user prefers family-separated content roots and collection inventories covering endpoints, src/content roots, public asset roots, loader sources, frontmatter support, and legal pages separately.
§
In corp-web-japan preview resource publication work, the user is concerned about slug-as-id patterns like `glossary/glossary` and leans toward stable numeric content IDs/files (e.g. `src/content/glossary/1.mdx` with `id: "1"` and separate canonical `slug`) for `/t/introduction-deck`, `/t/glossary`, and `/t/manuals` detail routes.
§
In corp-web-japan PR follow-up work, gh pr view can briefly lag after push; verify the actual remote branch tip with `git ls-remote origin refs/heads/<pr-branch>` before assuming the PR head failed to update.
§
In corp-web-japan typography work, the user prefers site-wide consistency over route-local parity exceptions: do not keep `/t/about-us` as a special text-color or body-typography exception; align it to shared site defaults instead. Current documented defaults are route-level `main` `text-slate-950`, ordinary descriptive/body copy `text-slate-600`, and for marketing/company body copy the preferred default is `15px/28px` (`text-[15px] leading-7`) unless a different shared pattern is explicitly required.
§
In corp-web-japan route policy, use-case list and detail routes are top-level `/use-cases` and `/use-cases/:id/:slug`; AIP/ACP demo list/detail routes remain under `/demo/aip` and `/demo/acp`.
§
In corp-web-japan, .github/workflows/ci.yml and deploy-preview.yml both support workflow_dispatch. If a PR branch push updates head SHA but GitHub does not attach new synchronize runs, manual dispatch on the PR branch can still validate the current head.
§
In corp-web-japan manuals work, the real replacement target for legacy /api-docs.html is https://docs.querypie.com/ja/api-reference.
§
In corp-web-japan, Vercel WAF custom rules are now managed as a repo-committed source of truth under ops/vercel-firewall/, with a project-specific JSON payload plus README, and applied project-scoped via full PUT to /v1/security/firewall/config for corp-web-japan.
§
In corp-web-japan news rollout, direct redirects/opening to external media pages for local news items are intentionally avoided because external media links often break; local /news detail rendering is preferred over direct external card navigation.
§
In corp-web-japan event MDX, add `eventDate` only when the body explicitly states a concrete event date; do not infer it from frontmatter `date` or add it to hidden shadow redirect records without explicit source evidence.
§
Repo-specific rule for corp-web-japan: promoted/replaced preview /t/* endpoints should be removed entirely by default, not preserved as redirects. Only keep a /t/* route if the user explicitly requests that exact compatibility path.
§
In corp-web-japan sitemap policy, hidden MDX records should be excluded from sitemap.xml by default, but hidden records with redirectUrl must still be exposed in sitemap.xml so bot-indexable local canonical detail pages remain discoverable.
§
In corp-web-japan repo-local blog/whitepaper posting skills, preserve the explicit contract that files are named `src/content/{blog,whitepapers}/<id>-<slug>.mdx` and that the canonical route slug source of truth remains frontmatter `slug`; do not replace this with vague 'route-readable filename' guidance.
§
In corp-web-japan migration/status planning, existing blog/whitepaper hidden/redirect/gated records are intentional and should not be resurfaced as generic cleanup work unless the user explicitly asks to revisit that policy or there is a concrete regression.
§
In corp-web-japan migration planning, do not surface content-volume/completeness concerns like small AIP demo corpus as remaining work unless the user explicitly asks; evaluate from the migration/route-replacement lens, not content-richness.
§
In corp-web-japan migration-status docs, evaluate only whether existing querypie.com/ja content/functionality is migrated/replaced locally; do not frame content richness or intentional hidden/redirect/gated states as gaps. Keep Website-Migration-Plan* and Route-Local-Authoring* consistent when latest-main route statuses change.
§
In corp-web-japan whitepapers, downloadable PDF CTA metadata is now modeled explicitly in MDX frontmatter as `downloadCta: { href, label, external }`, and route-aligned local PDF assets live under `public/whitepapers/<id>/download.pdf`.
§
In corp-web-japan publication-helper planning, the user wants the current low-level duplication between create-standard-publication-post-loader.ts and create-gated-publication-post-loader.ts kept as-is for now; only consider further refactoring later if duplicated code grows materially.
§
In corp-web-japan legal preview work, route-local self-contained placement under src/app/t/<route>/ can be preferable to broad src/content/legal-preview + src/lib/legal-preview indirection; for versioned privacy-policy previews, the user expects `src/app/t/privacy-policy/[slug]/page.tsx` to own page composition while `src/app/t/privacy-policy/page.tsx` may remain a thin latest-version wrapper that derives the last document date.
§
In corp-web-japan, for standalone static/legal preview pages like terms-of-service, the user prefers route-local MDX colocation: keep page.tsx and content.mdx in the same route directory (e.g. src/app/t/terms-of-service/) rather than placing the MDX under src/content.
§
In the repo-local Hermes setup at ~/workspace/skills-jk/.hermes/config.yaml, mcp_servers.chrome-devtools is configured with npx chrome-devtools-mcp@latest and Hermes reports it enabled via `hermes mcp list`.
§
In corp-web-japan whitepaper download flow, the user wants `gated: true` whitepapers to show a CTA near the start of the visible article body that links to a dedicated `/whitepapers/:id/:slug/download` gating page; that download page should use the portrait PDF cover image (not the article thumbnail), and Preview Toggle should bypass the download gating form and open the PDF directly.
§
In corp-web-japan publication UX, the user expects introduction-deck gated download CTA buttons to appear in the unlocked gated section directly below the `資料ダウンロード` explanatory copy, not above the gating form; also treat whitepaper article-body CTA links to `/whitepapers/{id}/{slug}/download` as an intentional second gating step rather than a direct PDF-download link.
§
In corp-web-japan mobile resource/demo sidebar UX, after comparing alternatives the user chose the bottom-sheet/drawer navigation pattern over the block-list/grid pattern as the preferred final direction.
§
In corp-web-japan service preview parity work, when the user asks to fix multiple `/t/services/*` pages together (such as ACP and FDE), they want each page handled in its own fresh worktree and its own separate PR, not bundled into one combined PR.
§
The user wants the repeated repo-local stale-branch/worktree audit workflow encoded as a reusable skills-jk skill: classify non-open-PR branches by synthetic squash of current local state vs latest origin/main, test disposable rebase onto latest main, preserve meaningful local patches, and delete only clearly stale branches/worktrees.
§
In corp-web-japan PR follow-up or route-local review work, if a requested route/file is missing on current main/PR head, do not assume it should be restored from history. Report the absence first and confirm scope before reviving an old route subtree.
§
In the repo-local Hermes config at ~/workspace/skills-jk/.hermes/config.yaml, checkpoints.enabled is currently false while stale historical checkpoint repos can still remain on disk under .hermes/checkpoints until manually deleted.
§
In corp-web-japan, the user wants remaining legacy `/posts/` route/code/content remnants removed entirely rather than preserved for event compatibility.
§
In corp-web-japan path taxonomy work, the user wants the temporary `t-` prefix kept only in app route paths; do not use `t-` in component or test family names. Use neutral family names like `aip`, `acp`, and `fde` instead of `t-services-aip`, `t-services-acp`, or `t-services-fde`.
§
In corp-web-japan path taxonomy naming, the user wants a single canonical family name chosen on general convention rather than current code habit; use `home` instead of `top-page` for the homepage component/test family.
§
In the repo-local Hermes setup under ~/workspace/skills-jk/.hermes/, the user wants the openai-codex credential labeled `gpt4` to be prioritized first in the credential pool (ahead of gpt3/gpt8/gpt11) while keeping `credential_pool_strategies.openai-codex=fill_first`.
§
In corp-web-japan, default text content width is 1200px unless a side-by-side image/media layout narrows it; for legal/document preview pages, `max-w-[920px]` is incorrect and should not be preserved.
§
In corp-web-japan test structure work, the user wants only genuinely reusable infra helpers kept in shared test helper locations; page-specific or page-family-specific helpers should be colocated near the relevant mirrored test paths instead of centralized under tests/helpers.
§
corp-web-japan main requires `Detect changed scope`, but ci.yml pull_request ignores docs/README/AGENTS/public md/skills md changes, so docs-only PRs can miss the required check.
§
Mac Studio LLM1 is `qp-test@10.11.1.11` (`Mac-Studio-LLM1.local`). Existing runner dirs: `/Users/qp-test/actions-runner` chequer-io native launchd, `/Users/qp-test/Workspace/github-runner` chequer-io Docker ARM64. QueryPie runners are installed at `/Users/qp-test/Workspace/github-runners-for-querypie-org`: 6 Linux ARM64 Compose runners, group `mac-studio-llm1-linux-arm64`, all `purpose:ci`, runners 1-3 also `purpose:build`.
§
In skills-jk repeated local-sweep cleanup, if requested scoped files (.hermes/config.yaml, .hermes/memories/MEMORY.md, USER.md) are already identical to latest main but the session creates skill-library residue, split that into a narrow follow-up PR instead of claiming the scoped PR changed.
§
In corp-web-app PR follow-up, `/[locale]/t` preview routes are additive review entrypoints; they must not modify existing public home route files or add new public locale entries unless explicitly requested, and tests should mirror route paths.
§
In corp-web-app route-local routing, the user prefers unprefixed English public URLs (e.g. /plans, /plans/aip, /company/contact-us) to be handled by middleware default-locale rewrite to internal /en/... [locale] routes, instead of separate src/app/<path>/page.tsx or page-compatibility route.ts files; non-English default-path requests should still redirect to /ko or /ja canonical paths.
