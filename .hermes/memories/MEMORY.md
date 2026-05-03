User stores personal Hermes runtime secrets in 1Password item `skills-jk-hermes-local` in the Private vault.
§
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
In corp-web-japan missing-path redirect work, the user wants runtime-log 404 candidates checked against the corresponding https://www.querypie.com path first; only paths that actually return 200 OK should be added as redirects, and paths already covered by existing namespace rules should not get redundant exact-path rules.
§
In corp-web-v2 demo routing, canonical detail paths use short public routes: ACP `/demo/acp/:id/:slug`, AIP `/demo/aip/:id/:slug`, use-cases `/demo/use-cases/:id/:slug`, and webinars `/webinars/:id/:slug`; the AIP Google OAuth page is `/demo/aip/1/google-oauth-demo`, and older `/features/demo/**` or `/demo/webinar/**` paths should be treated as legacy/history rather than current canonical paths.
§
In corp-web-v2 author-box work, the component file was renamed from src/components/mdx-layout/ArticleAuthorBox.tsx to src/components/mdx-layout/AuthorBox.tsx per user preference for shorter names.
§
In corp-web-v2, article author profile assets live under public/crew/*, and locale author registry data now lives in src/features/mdx/authors/{en,ko,ja}.yaml with profileImage paths like crew/<file>; the server-only authors module parses the YAML at runtime.
§
In corp-web-v2 author-data work, the user is okay with converting YAML to JSON at runtime but does not want generated JSON author data files committed to git or managed in the repository.
§
In corp-web-v2 MDX author data, the user prefers the structure src/features/mdx/authors/{en,ko,ja}.yaml with a server-only authors/index.ts runtime YAML loader, rather than flat locale files or git-tracked generated JSON.
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
In corp-web-v2 worktrees under the repo root, targeted Vitest runs can resolve dependencies from the parent repo-root node_modules, so a separate worktree-local node_modules install is not always required.
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
User's Hermes CLI is git-installed under ~/.hermes/hermes-agent, with ~/.local/bin/hermes symlinked to ~/.hermes/hermes-agent/venv/bin/hermes, and current config lives in ~/workspace/skills-jk/.hermes/.
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
The active Hermes runtime uses HERMES_HOME=~/workspace/skills-jk/.hermes in this setup; treat that as the primary home for session state, logs, and agent-local artifacts unless evidence shows a different profile/home.
§
Hermes session files for this setup are stored under ~/workspace/skills-jk/.hermes/sessions, and direct file inspection there can reveal recent Telegram sessions beyond what session_search returns.
§
User asked to roll back git-installed Hermes from unstable main HEAD to a recent stable release; local Hermes repo was checked out at tag v2026.4.16 and the gateway was restarted.
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
In this Hermes setup with provider openai-codex and a ChatGPT account, a session that switches in-place from gpt-5.4 to open-ai/codex can later fail auxiliary compression/child-session startup with HTTP 400 "The 'codex' model is not supported when using Codex with a ChatGPT account." Other sessions can still work if their session model remains gpt-5.4.