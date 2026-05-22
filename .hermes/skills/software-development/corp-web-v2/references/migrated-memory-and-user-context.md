# Migrated memory and user context for corp-web-v2

These entries were moved out of global Hermes memory/user profile because they are repository- or platform-specific. Keep them here or split them into narrower workflow skills as they evolve.


## From MEMORY.md


### MEMORY entry 1

In corp-web-v2, the user expects each PR task to start from a fresh worktree and fresh branch; do not continue new requested work on a previously used PR branch because it can cause rebase conflicts and stale PR state.


### MEMORY entry 2

When investigating legacy corp-web-contents blog/localization history, the user expects ID-based pattern matching across all historical path families and related MDX/meta files, not just current canonical `content.mdx` paths. Search broad `blog` + `/<id>/` matches first, then classify EN/JA/KO MDX vs meta.


### MEMORY entry 3

In corp-web-v2, the built-in CMS is not a fully browser-operated remote CMS in practice: it behaves more like a GUI editor for file-based content, and edits still require running a local CMS server plus committing/pushing the resulting file changes.


### MEMORY entry 4

In corp-web-v2 content gating discussions, the user prefers an explicit in-body marker/cut point (e.g. MDX/Tiptap markup) over percentage-based gating levels, because it makes the preview boundary clear and intentional.

In corp-web-v2, before creating a new PR branch, update from origin/main and verify the branch merge-base is origin/main (or its tip ancestor) so merged commits from stale branches are not accidentally included in the PR.


### MEMORY entry 5

In corp-web-v2, blog and white-paper MDX migration is already present under src/content/mdx; do not treat those families as still pending migration work.


### MEMORY entry 6

In corp-web-v2, git worktrees keep per-worktree `node_modules` / `package-lock` state rather than a shared install, so fresh or older worktrees can show false baseline errors like `Cannot find module mermaid`; however, targeted Vitest runs may still resolve dependencies from the parent repo-root `node_modules`, so a separate worktree-local install is not always required.


### MEMORY entry 7

In corp-web-v2 demo routing, canonical detail paths use short public routes: ACP `/demo/acp/:id/:slug`, AIP `/demo/aip/:id/:slug`, use-cases `/demo/use-cases/:id/:slug`, and webinars `/webinars/:id/:slug`; the AIP Google OAuth page is `/demo/aip/1/google-oauth-demo`, and older `/features/demo/**` or `/demo/webinar/**` paths should be treated as legacy/history rather than current canonical paths.


### MEMORY entry 8

In corp-web-v2 author-box work, the component file was renamed from src/components/mdx-layout/ArticleAuthorBox.tsx to src/components/mdx-layout/AuthorBox.tsx per user preference for shorter names.


### MEMORY entry 9

In corp-web-v2, article author profile assets live under public/crew/*, and locale author registry data now lives in src/features/mdx/authors/{en,ko,ja}.yaml with profileImage paths like crew/<file>; the server-only authors module parses the YAML at runtime.


### MEMORY entry 10

In corp-web-v2 demo migration work, keep ACP MDX routes/rendering fully separate from CMS-managed demo content, source demo detail content from ../corp-web-contents original EN/KO/JA MDX files rather than CMS-authored Tiptap/HTML data, and do not modify the existing CMS-managed `src/app/[locale]/features/demo/[slug]/page.tsx` rendering path when working on ACP MDX migration.


### MEMORY entry 11

In corp-web-contents, demo MDX source lives under pages/features/demo/{aip-features,use-cases,webinars,acp-features}/<id>/<slug>/<locale>/content.mdx; current counts are AIP 1, use-cases 29, webinars 26, ACP 26. The frontmatter commonly uses legacy category slugs, hideOgImage, ogImage paths under public/demo/* or public/webinar/*, and relatedPosts paths pointing at legacy /features/demo/... URLs; referenced assets come from public/demo, public/customer-success-cases, public/webinar, and for older ACP also public/tutorial.


### MEMORY entry 12

In corp-web-v2 content migration audits, the user considers content migration complete only when the content is actually migrated to MDX; non-MDX managed content/HTML/Tiptap routes should be treated as not yet completed migration.


### MEMORY entry 13

In corp-web-v2 Solutions parity work, legacy canonical content lives under corp-web-contents/pages/solutions/{aip,acp}/** with 11 canonical routes total; locale gaps exist for acp/ko and aip/integrations/ko, where legacy behavior effectively falls back to English.


### MEMORY entry 14

For corp-web-v2 Solutions page migration, required legacy public assets come mainly from corp-web-contents/public/{aip,acp,products,tutorial,introducing-querypie,key-feature-icon,integration-icon}, while /assets/dac-analyzer.json comes from corp-web-app/public/assets rather than corp-web-contents.


### MEMORY entry 15

In corp-web-v2, do not assume `npm run lint` / `npx eslint` are available as standard verification steps; first verify the repo's package scripts and ESLint config, and otherwise rely on the repo’s actual test/typecheck/build checks.


### MEMORY entry 16

In corp-web-v2 wiki migration planning, the user wanted duplicate planning/readiness pages removed entirely after consolidation, not just marked as superseded; Home/wiki should be rewritten around the latest canonical docs.


### MEMORY entry 17

In corp-web-v2 public content routing, list-page paths and individual content-detail paths should share the same prefix. Canonical naming uses singular `/blog`, plural `/white-papers`, plural `/demo/use-cases`, top-level `/webinars`, and short fixed demo segments `/demo/acp` and `/demo/aip`; older `/demo/webinar/**` or `/features/**` demo routes are legacy/history rather than current canonical paths.


### MEMORY entry 18

In corp-web-v2 Solutions follow-up work, the user wants inline images/assets reorganized under route-aligned public paths matching page structure, e.g. assets referenced by a Solutions page should live under public/path/solutions/<slug>/... rather than broad shared folders like public/aip or public/products.


### MEMORY entry 19

In corp-web-v2 demo migration follow-up, the user does not want legacy URL redirects included in the current PR; redirect rules should be audited and implemented later in a separate batch.


### MEMORY entry 20

In corp-web-v2 demo/content asset normalization, the user wants thumbnail filenames standardized to thumbnail.png when locale-agnostic and thumbnail-<locale>.png when locale-specific (e.g. thumbnail-en.png, thumbnail-ko.png, thumbnail-ja.png).


### MEMORY entry 21

In corp-web-v2 on Vercel, API routes that access generic `process.cwd()/public` paths can cause output tracing to bundle large unrelated public assets and exceed serverless size limits. Prefer narrowing file access to explicit subdirectory roots (e.g. specific `public/demo` or `public/documentation` paths) rather than generic public-root joins.


### MEMORY entry 22

In corp-web-v2 wiki documentation, the user prefers related route-policy follow-up details such as mismatch tables to be appended under the existing canonical wiki page rather than split into a separate page.


### MEMORY entry 23

In corp-web-v2 migration work, the user wants stage-v2.querypie.com validated by directly visiting the live stage site and the results documented as a GitHub wiki E2E verification report, not inferred only from code or inventory tables.


### MEMORY entry 24

In corp-web-v2 demo MDX migration work, the user wants CMS-connected demo files left untouched: do not modify `src/app/[locale]/features/demo/page.tsx`, `src/app/[locale]/features/demo/[slug]/page.tsx`, admin demo pages, or content-state/authored-server flows unless explicitly requested.


### MEMORY entry 25

In corp-web-v2 Solutions parity work, the user does not want placeholder or legacy alias redirects included in the migration PR; for an unopened site, updating GNB/header/footer links to canonical Solutions pages is sufficient, and redirect rules should be analyzed/applied separately later.


### MEMORY entry 26

In corp-web-v2, when squashing an open PR branch after origin/main has advanced, use the PR branch's merge-base with origin/main as the soft-reset point, not current origin/main, or unrelated main-only changes can be pulled into the squashed commit.


### MEMORY entry 27

In corp-web-v2, Solutions parity is implemented via src/app/[locale]/solutions/[[...slug]]/page.tsx with content under src/content/solutions/** and route mapping in src/features/solutions/routes.ts.


### MEMORY entry 28

In corp-web-v2, if `src/content/mdx` contains only blog and white-paper families, treat demo MDX source as not yet migrated in that repo snapshot.


### MEMORY entry 29

In corp-web-v2 route-policy follow-up work, when renaming canonical public content paths like white-paper -> white-papers, the user wants code routes, MDX links, and public asset/image directories updated consistently in one pass to match the wiki naming convention.


### MEMORY entry 30

In corp-web-v2 Solutions work, the user wants `/solutions/**` pages implemented as individual static `page.tsx` routes rather than an MDX-rendered catch-all, because most Solutions content is considered unsuitable for MDX.


### MEMORY entry 31

In corp-web-v2 wiki/content migration audits, /features/** should be treated as legacy-only paths. A family counts as implemented only if it is exposed on a separate non-/features public URI; /features presence alone does not count.


### MEMORY entry 32

For corp-web-v2 content restoration, the user wants missing MDX locale files and related assets recovered from corp-web-contents git history when possible, not recreated speculatively.


### MEMORY entry 33

In corp-web-v2, the Public-Content-URL-Naming-Convention requires the white-paper public route family to use plural `/white-papers` with aligned app routes, MDX source/public asset paths, and related internal links; do not keep singular `/white-paper` for that family.


### MEMORY entry 34

In corp-web-v2 Solutions static-page work, the user wants file/directory structure for localized page-content modules to mirror the nested src/app route slug structure and avoid flat legacy names such as acp-database-access-controller.


### MEMORY entry 35

In corp-web-v2 route-policy work, the user wants the webinars family to use top-level `/webinars` for the public list route as well, not `/demo/webinars`; align code and the Public-Content-URL-Naming-Convention wiki in the same batch.


### MEMORY entry 36

In corp-web-v2 Public-Content-URL-Naming-Convention updates, treat src/app/[locale]/features/demo/page.tsx and src/app/[locale]/features/documentation/page.tsx as legacy-only paths; do not count them as migration targets or implementation results.


### MEMORY entry 37

In corp-web-v2 blog/white-paper MDX, the canonical upstream slug from corp-web-contents is now stored explicitly as frontmatter `slug` in each `src/content/mdx/blog/<id>/<locale>.mdx` and `src/content/mdx/white-papers/<id>/<locale>.mdx`, while the directory name remains the numeric content ID.


### MEMORY entry 38

For repo-specific E2E/stage assertions, first verify the current workspace via cwd/pwd and do not mix corp-web-v2, corp-web-app, and corp-web-japan environments.


### MEMORY entry 39

E2E stage targets are repo-specific: corp-web-v2 -> https://stage-v2.querypie.com, corp-web-app -> https://stage.querypie.com, corp-web-japan -> https://stage.querypie.ai.


## From USER.md


### USER entry 1

User currently wants corp-web-v2 demo use-cases and webinars to use plural route-aligned naming consistently: detail routes should use `/demo/use-cases/:id/:slug`, and MDX content directories should mirror actual public URI naming such as `src/content/mdx/demo/use-cases/**` and `src/content/mdx/demo/webinars/**`.


### USER entry 2

In corp-web-v2 asset migration work, the user prefers non-image assets like animation JSON files to be colocated under route-aligned public paths with the related page assets (e.g. under public/solutions/<route>/) rather than left in generic shared roots like public/assets when they are page-specific.


### USER entry 3

In corp-web-v2, the user wants repeated local npm install in fresh worktrees avoided when possible because it causes significant delay.


### USER entry 4

In corp-web-v2, the user does not want node_modules kept inside worktrees.


### USER entry 5

In corp-web-v2, the user does not want CMS/public managed route/data files such as src/app/[locale]/features/demo/page.tsx or src/content/documentation/** modified unless they explicitly authorize that exact file or subtree; route, canonical, link, or naming cleanup requests do not imply permission to edit CMS-managed files.


### USER entry 6

In corp-web-v2 stage/content verification, the user treats /features/** as legacy paths that should not count as implemented. If content is not exposed on a separate non-/features public URI, it should be considered not yet implemented.


### USER entry 7

For Solutions static-pages follow-up, the user wants remaining Solutions MDX documents fully reimplemented and replaced in the PR, not left as source artifacts.


### USER entry 8

In corp-web-v2 wiki and migration audits, the user wants `/features/**` treated as legacy across documents, and any content exposed only under `/features/**` should be considered not yet implemented until it has a separate non-legacy public URI.


### USER entry 9

In corp-web-v2 demo work, the user does not want src/features/demo/** touched for image-path consistency fixes unless explicitly requested.


### USER entry 10

In corp-web-v2 route-policy changes, the user wants the GitHub wiki naming-convention document and the corresponding code updates done together in the same batch, not separately.


### USER entry 11

When a requested cleanup would require touching a previously forbidden scope like `src/features/demo/**`, the user expects the assistant to stop and ask before making even a minimal supporting change; do not widen scope just to complete a cleanup.


### USER entry 12

In corp-web-v2 static-page work, the user prefers each page's content to stay colocated in one directory for easy comparison, does not want copy/data/helper split into separate directories, and wants static page.tsx files to remain very thin with minimal logic.


### USER entry 13

The user is open to challenging existing corp-web-v2 repository conventions and does not consider the current overall structure inherently authoritative when evaluating better file placement.


### USER entry 14

In corp-web-v2 follow-up work, the user does not want a new PR or reviewer requests created unless they explicitly ask for that PR/review action for the current scoped task; do not infer PR/reviewer permission from earlier broader requests.


### USER entry 15

In corp-web-v2 static-page work, the user wants metadata/SEO data kept route-local with each page rather than centralized in a shared registry; avoid central metadata registries for static pages.


### USER entry 16

In corp-web-v2 static-page work, the user prefers removing even thin shared helpers like route-specific page helpers when they reduce route-local explicitness; favor fully self-contained page.tsx files.


### USER entry 17

When the user says not to touch a scope like src/features/demo/**, do not change even a single line there for cleanup or path fixes without explicit permission, even if it seems like the minimal way to avoid a broken reference.


### USER entry 18

In corp-web-v2, do not modify CMS-related code or legacy URL/redirect behavior unless the user explicitly instructs that exact scope; route/list-page requests alone do not authorize CMS or legacy URL changes.


### USER entry 19

In corp-web-v2 migration comparison wiki tables, the user wants memo/description cells kept concise and information-dense; do not include legacy-route explanatory prose when current canonical routes are the real subject.


### USER entry 20

사용자는 corp-web-v2에서 CMS 관련 코드/경로와 공개 MDX 경로 분석을 완전히 별개로 취급하길 원한다. MDX 목록/공개 경로 원인 분석에서는 /features/** 등 CMS legacy 경로와 CMS 관련 코드 전체를 아예 분석 대상에서 제외하고 언급도 하지 말 것.


### USER entry 21

For corp-web-v2 documentation sidebar requests, preserve the exact ordered structure literally as specified by the user. Current required order: CMS label -> All -> Introduction -> Glossary -> Manuals -> White Papers -> Blogs -> separator -> MDX label -> White Papers -> Blogs. Do not omit CMS White Papers/Blogs, and do not reinterpret the request as either CMS-only or MDX-only.
