User stores personal Hermes runtime secrets in 1Password item 'skills-jk-hermes-local' in the Private vault.
§
In the repo-local Hermes setup, `hermes gateway install/start/restart/status` are the supported service controls, and only one gateway instance should run per `HERMES_HOME`; additional `hermes gateway run` attempts with the same home compete or are refused.
§
In the skills-jk repository, the local `skills/` directory currently has 35 top-level discovered skills, plus one nested duplicate path under `skills/cc-codex-debate-review/skills/cc-codex-debate-review`. The repo's AGENTS rules require per-turn skill discovery from `skills/` and system skills.
§
In corp-web-japan, the user prefers local-only worktree configuration on their PC rather than shared repo changes; do not add scripts for this. Use repo-local git aliases instead, with worktrees under corp-web-japan/.worktrees.
§
In the skills-jk repo, portable Hermes state should live in tracked `.hermes/config.yaml`, tracked markdown memories under `.hermes/memories/`, tracked skills under both `.hermes/skills/` and the repo `skills/` tree; runtime artifacts like `.hermes/checkpoints/`, `.hermes/sessions/`, logs, `state.db*`, caches, and generated `.hermes/.env` should stay untracked/ignored.
§
For portable Hermes setups in skills-jk, session-like records should remain local to each machine/instance and should not be migrated between PCs; only durable memories and config should be synced.
§
In the skills-jk repo, PR creation uses the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` via `workflow_dispatch`; it is the preferred PR creation path for this repo.
§
In corp-web-v2, managed public content is currently loaded from authored files under src/content/** via src/features/content/authored.server.ts and contentState.server.ts, not from src/content/state/content-state.json.
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
In querypie-docs confluence-mdx reverse-sync planning, the user treats `tests/reverse-sync/pages.yaml` complexity as non-core: in real data it is just a reference metadata catalog for reverse-sync, and extra fields were added only for testcase implementation; do not overcomplicate this point.
§
In querypie-docs confluence-mdx reverse-sync planning, the user views `tests/reverse-sync/pages.yaml` as straightforward: for reverse-sync it is just a reference metadata catalog based on real data, and extra fields only exist for testcase implementation; do not overcomplicate its role.
§
In querypie-docs confluence-mdx reverse-sync planning, the user considers pages.yaml straightforward in real-data usage: for reverse-sync it is just a reference metadata catalog; extra fields only exist for test-case implementation, so this should not be overcomplicated.
§
In querypie-docs confluence-mdx reverse-sync planning, the user prefers verifier taxonomy to be classified in more detail.
§
In corp-web-v2, the current CMS workflow still results in file changes that require git commit and push; it functions more like a GUI editor for file-based content than a fully git-free CMS.
§
In corp-web-v2 content gating discussions, the user prefers an explicit in-body marker/cut point (e.g. MDX/Tiptap markup) over percentage-based gating levels, because it makes the preview boundary clear and intentional.
§
In corp-web-v2, the built-in CMS is not a fully browser-operated remote CMS in practice: content edits still require running a local CMS server and then committing/pushing the resulting file changes.
§
In corp-web-v2, branch `fix/public-route-metadata-audit` corresponded to merged PR #35; treat it as stale and create a fresh branch before new commit/push if found checked out again.
§
In corp-web-v2, before creating a new PR branch, update from origin/main and verify the branch merge-base is origin/main (or its tip ancestor) so merged commits from stale branches are not accidentally included in the PR.
§
In corp-web-v2, origin/main already contains the blog and white-paper MDX migration from corp-web-contents: source/target counts matched at 62 blog locale files and 76 white-paper locale files under src/content/mdx.
§
In corp-web-v2, git worktrees use per-worktree local node_modules/package-lock state rather than a shared install. Fresh or older worktrees may have missing or stale dependencies, causing false baseline errors like 'Cannot find module mermaid'; run npm install inside the specific worktree before judging test/typecheck failures.
§
In corp-web-japan missing-path redirect work, the user wants runtime-log 404 candidates checked against the corresponding https://www.querypie.com path first; only paths that actually return 200 OK should be added as redirects, and paths already covered by existing namespace rules should not get redundant exact-path rules.
§
In corp-web-v2 origin/main (12bab42), public managed content is currently read from authored files under src/content/** via src/features/content/contentState.server.ts and authored.server.ts; src/content/state/content-state.json is absent in this repo snapshot.
§
In corp-web-v2 demo routing, the user wants the AIP Google OAuth demo canonical path shortened to /demo/aip/1/google-oauth-demo, with old /features/demo/aip-features/1/google-oauth-demo and /features/demo/google-oauth-demo treated as legacy paths.
§
In corp-web-v2 author-box work, the component file was renamed from src/components/mdx-layout/ArticleAuthorBox.tsx to src/components/mdx-layout/AuthorBox.tsx per user preference for shorter names.
§
In corp-web-v2 public demo routing, ACP uses /demo/acp/:id/:slug, AIP uses /demo/aip/:id/:slug, and use-cases use singular /demo/use-case/:id/:slug with legacy feature paths redirecting to the short canonical route.
§
corp-web-v2 demo migration PR branch feat/demo-acp-mdx-migration remains the active follow-up branch for additional short-route changes on PR #40.
§
In corp-web-v2 demo routing, the user wants managed AIP demo canonical paths shortened to /demo/aip/:id/:slug, with legacy /features/demo/aip-features/:id/:slug and /features/demo/:slug redirected to the short canonical path.
§
In corp-web-v2 demo routing, the user wants use-cases demo canonical detail paths shortened to singular /demo/use-case/:id/:slug, with legacy /features/demo/use-cases/:id/:slug and /features/demo/:slug redirected to the short canonical path.
§
In corp-web-v2, article author profile assets live under public/crew/*, and locale author registry data now lives in src/features/mdx/authors/{en,ko,ja}.yaml with profileImage paths like crew/<file>; the server-only authors module parses the YAML at runtime.
§
In corp-web-v2 author-data work, the user is okay with converting YAML to JSON at runtime but does not want generated JSON author data files committed to git or managed in the repository.
§
In corp-web-v2, the user prefers PR titles, descriptions, and review comments to be written in Korean.
§
In corp-web-v2 MDX author data, the user prefers the structure src/features/mdx/authors/{en,ko,ja}.yaml with a server-only authors/index.ts runtime YAML loader, rather than flat locale files or git-tracked generated JSON.
§
In corp-web-v2 PR #40 follow-up, the user required ACP MDX routes/rendering to remain fully separate from CMS-managed demo content: do not couple new demo page routes to `readContentItem/readContentState` for AIP/use-cases/webinars or modify the existing CMS-managed `src/app/[locale]/features/demo/[slug]/page.tsx` rendering path when working on ACP MDX migration.
§
In corp-web-v2 demo migration work, the user wants demo detail content to be sourced from ../corp-web-contents original EN/KO/JA MDX content and not from CMS-authored Tiptap/HTML data files.
§
In corp-web-v2, PR #40 for ACP MDX was merged into origin/main at commit e634bcf; new follow-up work should branch from latest origin/main after that merge.
§
In corp-web-v2, current full demo MDX migration work is being done in fresh worktree branch feat/demo-mdx-migration-all based on origin/main e634bcf, with corp-web-contents cloned locally at ~/workspace/corp-web-contents (origin/main 0ecd280).
§
In corp-web-contents, demo detail MDX source already exists under pages/features/demo/{aip-features,use-cases,webinars,acp-features}/... with counts: AIP 1, use-cases 29, webinars 26, ACP 26. The MDX frontmatter commonly uses legacy category slugs, hideOgImage, ogImage paths under public/demo/* or public/webinar/*, and relatedPosts paths pointing at legacy /features/demo/... URLs.
§
In corp-web-v2 content migration audits, the user considers content migration complete only when the content is actually migrated to MDX; non-MDX managed content/HTML/Tiptap routes should be treated as not yet completed migration.
§
In corp-web-v2 Solutions parity work, legacy canonical content lives under corp-web-contents/pages/solutions/{aip,acp}/** with 11 canonical routes total; locale gaps exist for acp/ko and aip/integrations/ko, where legacy behavior effectively falls back to English.
§
For corp-web-v2 Solutions page migration, required legacy public assets come mainly from corp-web-contents/public/{aip,acp,products,tutorial,introducing-querypie,key-feature-icon,integration-icon}, while /assets/dac-analyzer.json comes from corp-web-app/public/assets rather than corp-web-contents.
§
In corp-web-contents, demo MDX source lives under pages/features/demo/{aip-features,use-cases,webinars,acp-features}/<id>/<slug>/<locale>/content.mdx, and referenced demo assets come from public/demo, public/customer-success-cases, public/webinar, and (for older ACP) public/tutorial paths.
§
In corp-web-v2 origin/main around e634bcf, package.json has no lint script and the repo lacks an ESLint config file, so `npm run lint` / `npx eslint` are not available as standard verification steps; rely on the repo’s existing test/typecheck/build checks unless linting is added later.
§
In corp-web-contents, remaining demo MDX source lives under pages/features/demo/{aip-features,use-cases,webinars}/<id>/<slug>/<locale>/content.mdx, and corp-web-v2 demo MDX migration normalizes demo inline/OG assets to public/demo/<segment>/<id>/... while using short canonical routes /demo/aip/:id/:slug, /demo/use-case/:id/:slug, and /demo/webinar/:id/:slug.
§
In corp-web-v2 wiki migration planning, the user wanted duplicate planning/readiness pages removed entirely after consolidation, not just marked as superseded; Home/wiki should be rewritten around the latest canonical docs.
§
In corp-web-v2 public content routing, the user wants list-page paths and individual content-detail paths to share the same prefix. Canonical naming should use singular /blog, plural /white-papers, plural /demo/use-cases, and plural /demo/webinars; ACP/AIP demo routes keep short fixed segments /demo/acp and /demo/aip.
§
In corp-web-v2 Solutions follow-up work on PR #42, the user wants inline images/assets reorganized under route-aligned public paths matching page structure, e.g. assets referenced by a Solutions page should live under public/path/solutions/<slug>/... rather than broad shared folders like public/aip or public/products.
§
In corp-web-v2 demo routing follow-up, the user wants webinar detail content to use canonical /webinars/:id/:slug paths instead of /demo/webinar/:id/:slug, with demo/webinar treated as legacy/redirect-only if present.
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