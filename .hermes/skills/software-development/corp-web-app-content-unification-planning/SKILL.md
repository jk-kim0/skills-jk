---
name: corp-web-app-content-unification-planning
description: Plan corp-web-app migration from corp-web-contents/Vercel Blob toward repo-local content management, borrowing structural lessons from corp-web-japan without copying Japan-only assumptions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, content-migration, mdx, planning, documentation, nextjs]
---

# corp-web-app content unification planning

Use this skill when writing or updating plans for corp-web-app to:

- keep corp-web-app as the global website implementation,
- migrate useful corp-web-japan functionality back into corp-web-app,
- retire corp-web-contents as the required content source,
- move content source, assets, loaders, tests, and route contracts into corp-web-app.

This is a planning/documentation and architecture skill. For implementation follow-up, pair it with the normal PR/worktree skills.

## Required context checks

1. Verify the active repo and branch before editing.
   - `pwd`
   - `git rev-parse --show-toplevel`
   - `git status --short --branch`
2. If updating an existing PR, update the same PR branch in a worktree; do not open a new PR unless the user asks.
3. Read relevant corp-web-japan docs when borrowing structural guidance:
   - `docs/code-location-conventions.md`
   - `docs/static-page-route-local-authoring.md`
   - `docs/route-aligned-mdx-authoring-for-developers.md` or `.ko.md`
4. Do not treat corp-web-japan's current implementation as a literal copy source. Extract the pattern and adapt it to corp-web-app's global multilingual site requirements.

## Guiding principle for corp-web-japan transfer

The core transfer rule is:

- Move implementation patterns and validated features from corp-web-japan into corp-web-app.
- Do not move Japanese copy itself as the migration target.

When writing plans or migration docs, phrase corp-web-japan as a source of proven structure, behavior, and workflow patterns — not as a source of global-site copy. This distinction is important enough to state explicitly in planning documents.

## Phase 0: import corp-web-japan guides, guidance, and repo-local skills first

Before planning or implementing feature endpoint migrations or MDX collection migrations, make the first concrete workstream a guidance/skill import from corp-web-japan into corp-web-app.

Why this must come first:

- The user wants corp-web-app work to refer to the proven corp-web-japan guides, instructions, and repo-local skills before implementation begins.
- If the reference system is imported after implementation PRs start, different agents may follow different structure, route-local refactoring, MDX, asset, and rollout conventions.
- The guidance import is not a cosmetic docs task; it is the operating baseline for all later endpoint and collection work.

Scope to inventory from corp-web-japan:

1. Repo-level working guidance.
   - `AGENTS.md` or equivalent guidance files.
   - Rules for PR/commit language, worktrees, main-checkout safety, CI/Preview behavior, and review expectations.
2. Structure and authoring docs.
   - Code location conventions.
   - Static/semi-static route-local refactoring guidance.
   - Route-aligned MDX authoring guidance.
   - Public asset / route-aligned asset placement rules.
3. Content and route policy docs.
   - MDX collection naming, frontmatter, ID/slug/canonical policy.
   - Hidden/redirect/gated publication policy.
   - Sitemap, metadata, canonical, and locale fallback policy.
4. Repo-local skills.
   - `.agents/skills/**` entries for migration/refactoring/release workflows that will recur in corp-web-app.
   - Adapt them for the global multilingual site; do not copy Japan-only routes, launch assumptions, or Japanese content as-is.

Use a tracked import manifest so future sessions can quickly detect whether corp-web-japan has changed and whether reimport is needed. A starter template is available at `templates/corp-web-japan-guidance-import-manifest.md`.

The manifest should record at least:

- source path in corp-web-japan,
- target path in corp-web-app,
- last imported corp-web-japan commit SHA,
- disposition: `copy as-is`, `adapt`, or `exclude`,
- local adaptation notes,
- reimport check result/date.

Fast reimport check pattern:

```bash
# In corp-web-japan, for each manifest source path:
git log -1 --format=%H -- <source-path>
```

Compare that SHA with the manifest's `last imported commit`. If it differs, inspect only the changed source path(s), not the entire corp-web-japan docs tree.

## Target directory model

For planning docs, describe the target corp-web-app shape with these roles:

```text
corp-web-app
  ├─ src/app/**                 # App Router routes, route-level page composition, route handlers
  │   ├─ <route>/page.tsx        # thin wrapper: locale selection, fallback, metadata wiring, page module dispatch
  │   └─ <route>/page.{locale}.tsx # route-local i18n authoring source: copy, section order, CTA, metadata
  ├─ src/components/
  │   ├─ sections/**            # page/section UI implementation, layout, interaction
  │   ├─ ui/**                  # reusable UI primitives
  │   └─ layout/**              # site-wide layout, header, footer
  ├─ src/lib/**                 # reusable non-UI logic: loaders, repositories, route resolution, integration
  ├─ src/content/**             # publication and explicit document-family content source
  ├─ public/**                  # route-aligned static assets
  ├─ tests/**                   # repo-level contract, route, content inventory, E2E tests
  ├─ src/**/__tests__/**         # tests tightly coupled to source modules
  ├─ docs/**                    # architecture, operations, migration docs
  ├─ scripts/**                 # inventory, migration, deployment helper scripts
  └─ .agents/skills/**          # repo-local skills for repeated workflows
```

## Code-location classification from corp-web-japan

When writing corp-web-app planning docs, do not only say "follow corp-web-japan". Spell out the directory responsibilities from corp-web-japan's `docs/code-location-conventions.md`, `docs/static-page-route-local-authoring.md`, and `docs/route-aligned-mdx-authoring-for-developers.md`, adapted to corp-web-app:

| Location | corp-web-japan responsibility | corp-web-app planning application |
| --- | --- | --- |
| `src/app/**` | Route entry, route-local metadata, page composition, route handlers | `page.tsx` is the thin route entry; route-local i18n targets use `page.{locale}.tsx` as the real authoring surface. API/route handlers focus on request/response wiring. |
| `src/components/sections/**` | Page- or domain-specific composed UI, section layout, styling, interaction | Section/component implementation details live here. Do not let these files become giant wrappers that hide marketing narrative or long copy. |
| `src/components/ui/**` | Reusable UX primitives and functional UI text | Keep only functional labels/status/error/helper text here. Do not put product explanations, sales messaging, or page-specific descriptive copy in shared UI primitives. |
| `src/components/layout/**` | Site-wide layout, header, footer | Own global layout/navigation chrome only; do not own page narrative or collection loaders. |
| `src/lib/**` | Reusable non-UI logic | Loaders, repositories, canonical route resolution, frontmatter parsing, MDX rendering, gated/hidden/redirect rules, and external integrations live here. |
| `src/content/**` | Route-aligned publication/document source content | Explicit family MDX/frontmatter source for blog, whitepapers, news, events, glossary, manuals, etc. Do not use it as a hidden content registry for static marketing pages. |
| `public/**` | Route-aligned static assets | Images, PDFs, thumbnails, and other assets should align to the public route/content family rather than broad catch-all buckets. |
| `tests/**`, `src/**/__tests__/**` | Route/content contracts and source-near tests | Repo-level route/content contracts go under `tests/**`; tests tightly coupled to a source module can live source-near. |

`src/features/**` is not part of the target classification. For new implementation and migration work, choose among `src/app/**`, `src/components/**`, `src/lib/**`, and `src/content/**` based on responsibility instead of introducing new code under `src/features/**`.

## Authoring-surface rules

1. Static/semi-static marketing pages and singleton route-owned documents:
   - Route-local i18n authoring is a required implementation design for corp-web-app, not a preference or optional refactor.
   - For every route URI in this class, create locale-specific authoring modules such as `<route>/page.en.tsx`, `<route>/page.ko.tsx`, and `<route>/page.ja.tsx`.
   - The real authoring surface is `src/app/**/page.{locale}.tsx` for each supported locale.
   - `page.{locale}.tsx` owns the real copy, locale-specific markup, section order, CTA composition, route metadata, and the choice of which layout/common components to compose.
   - `src/app/**/page.tsx` is only the framework-recognized route entry and should remain a thin wrapper for locale selection, fallback, metadata wiring, and dispatching to the locale-specific page module.
   - Common UI, layout shells, cards, buttons, forms, and section primitives should be extracted to `src/components/sections/**` or `src/components/ui/**`, but caller-authored text and locale-specific markup should be passed from `page.{locale}.tsx` via children/slot-style composition.
   - Locale-specific differences in component order, emphasis markup, helper copy, legal copy, or layout/component choice are valid localization requirements. Do not force them into JSON dictionaries, a central content registry, or condition-heavy shared page code.
   - Do not hide page-specific marketing narrative in a shared component, a central content registry, a giant props blob, `src/content/**`, or route-adjacent `content.mdx`.
   - Reviewers should be able to understand each locale's route narrative and composition from the route-local `page.{locale}.tsx`, even when section UI primitives live elsewhere.

2. Publication/detail families:
   - Route files stay thin.
   - MDX owns long-form body content and frontmatter.
   - `src/lib/**` owns loader/repository/route-resolution behavior.
   - `src/components/sections/**` or shared shells render consistent publication/document UI.

3. Versioned document families:
   - Use a dedicated explicit family root, not a vague catch-all.
   - Example shape: `src/app/privacy-policy/[slug]/page.tsx` + `src/content/privacy-policy/<slug>.{locale}.mdx`.

## Content family naming rules

For corp-web-app content-unification planning, the repo-local MDX collection names should be taken from corp-web-japan's actual `src/content/**` collection names. Do not re-decide, rename, or normalize those collection names by asking the user one-by-one unless the user explicitly reopens naming policy.

Confirmed collection roots to carry over as names:

- `src/content/blog/**`
- `src/content/whitepapers/**`
- `src/content/news/**`
- `src/content/events/**`
- `src/content/glossary/**`
- `src/content/manuals/**`
- `src/content/introduction-deck/**`
- `src/content/privacy-policy/**`
- `src/content/use-cases/**`
- `src/content/demo/aip/**`
- `src/content/demo/acp/**`

Do not create vague catch-all content roots such as:

- `src/content/resources/**` as a new broad migration collection
- `src/content/documentation/**`
- `src/content/docs/**`

Corp-web-japan paths that should not become independent migration collections:

- `authors`: publication metadata/support data, not content collection source.
- `internal`: internal/demo verification content, not public migration scope.
- `resources`: currently a narrow support-data path such as `src/content/resources/events.ts`; do not expand it into a generic content family.

Naming pitfalls:

- Do not rename `whitepapers` to `white-papers` in repo-local content planning.
- Do not rename or absorb `events` into `webinars` unless the user explicitly changes policy; corp-web-japan uses `events` as the collection.
- Do not ask the user to choose route/family names when the intended instruction is to mirror corp-web-japan collection names. Inspect corp-web-japan first and update the plan from the observed names.

If shared logic is needed across glossary/manuals/introduction-deck, keep the shared abstraction in code (`src/lib/**`), not by flattening their content roots into a generic directory.

## Multilingual MDX file contract

For multilingual publication/detail family content, use collection-flat locale-specific `<id>-<slug>.{locale}.mdx` files:

```text
src/content/{collection}/<id>-<slug>.{locale}.mdx
```

Examples:

```text
src/content/blog/9-data-discovery-privacy-management.en.mdx
src/content/blog/9-data-discovery-privacy-management.ko.mdx
src/content/blog/9-data-discovery-privacy-management.ja.mdx
```

Rules:

- Keep all MDX records for one collection directly under that collection root, such as `src/content/blog/`; do not introduce per-record MDX subdirectories like `src/content/blog/<id>-<slug>/content.en.mdx`.
- Keep `id` stable across locales.
- Keep the route slug visible in the collection-flat filename for human discoverability.
- Put locale in the MDX filename suffix: `<id>-<slug>.{locale}.mdx`.
- Treat frontmatter `slug` as the canonical route slug source of truth.
- Loader behavior should explicitly handle missing locale, fallback, hidden records, redirects, and gated records.

## Asset placement rules

Use route-aligned `public/**` paths:

```text
public/blog/<id>/thumbnail.png
public/whitepapers/<id>/download.pdf
public/events/<id>/thumbnail.ja.png
```

Locale-specific asset filenames use the same suffix convention as multilingual MDX:

```text
filename.{locale}.extension
```

Examples: `thumbnail.ja.png`, `cover.en.webp`.

Avoid dumping page-specific content assets into broad shared folders such as `public/assets` unless the file is intentionally long-lived external/shared infrastructure.

## Migration unit: endpoint or MDX collection, never whole-site batch

When writing corp-web-app migration plans, make the work unit explicit:

1. Feature replacement happens by feature endpoint or independent public behavior.
   - Examples: gated download flow, contact form, sitemap generation, canonical detail route, a product/solution page endpoint.
2. Content migration happens by MDX collection.
   - Examples: `blog`, `whitepapers`, `events`, `news`, `glossary`, `manuals`, `introduction-deck`, `use-cases`, `demo/aip`, `demo/acp`.
3. Do not describe the program as a whole-site conversion/replacement, a full website cutover, or a giant content move.
4. Each PR should be independently reviewable and should include only the code, content, assets, tests, and dependency removals for that endpoint or collection.
5. If an endpoint and a collection are related but can be validated separately, split them; keep public-release PRs especially small.

## Migration matrix document shape

When rewriting or maintaining `docs/inventories/mdx-collection-migration-matrix.md` or similar inventory-to-plan documents:

- Prefer a Korean, collection-by-collection section structure over one huge wide Markdown table. A wide table is acceptable only for compact summaries.
- Start with shared contracts: collection-flat content path, `/t/<locale>/<family>` verification route policy, public locale route policy, fallback behavior, and Blob/corp-web-contents scope boundary.
- Include a concise priority summary table, then one section per collection with a small `Field | Value` table plus short narrative notes.
- For every collection section, include at least: target collection, current source, target source, target assets when relevant, verification routes, final public routes, ID policy, locale risk, policy risk, and priority.
- Keep non-collection work separate. Static marketing pages, singleton route-owned documents, and feature endpoints belong in a `Non-collection endpoint work` section and must not be forced into `src/content/**` MDX collection rows.
- Use explicit target source paths such as `src/content/blog/<id>-<slug>.{locale}.mdx`; avoid vague `src/content/<family>/**` unless the source audit truly has not determined record shape yet.
- Keep legacy corp-web-contents source paths as evidence/source paths even when they use `<locale>/content.mdx`; do not confuse source-path examples with target repo-local contract.
- If you include a forbidden-path example, label it clearly as a negative example so grep-based checks can distinguish it from target guidance.

## Production-ready `/t/*` verification rollout

When planning App Router page implementations or content-family migrations, use the rollout pattern the user endorsed from corp-web-japan:

1. Implement the feature endpoint or MDX collection migration, route code, content, loaders, metadata, tests, and assets to production-ready quality first.
2. Expose the new endpoint/collection initially behind a locale-explicit `/t/*` verification endpoint, using `/t/<locale>/<family>` or `/t/<locale>/<family>/:id/:slug` (for example `/t/en/blog`, `/t/ko/blog/:id/:slug`, `/t/ja/whitepapers`, or `/t/en/introduction-deck`). Do not use query-string locale selection or `/en/t/...` route shape unless the user explicitly reopens this decision.
3. Keep `main` deployable at all times. Before validation is complete, do not disturb the existing public endpoint, public navigation, public sitemap, or canonical behavior.
4. Validate endpoint-by-endpoint on the `/t/*` URL: visual/content parity, SEO metadata, assets, forms/gating, hidden/redirect behavior, and route-level tests.
5. After validation, create a small public-release PR that connects the already production-ready implementation to the public route and minimally updates navigation, sitemap, canonical, and redirect policy.
6. In that public-release PR, remove the corresponding `/t/*` verification endpoint. Do not preserve `/t/*` as a compatibility path, and do not add redirects for it.
7. Treat public release as a separate step from implementation/migration. Do not wait for the entire site migration to finish; release validated feature endpoints and MDX collections sequentially.
8. The `/t/*` endpoint itself is a verification vehicle, not a Japan-only route policy to copy blindly. Use it to preserve deployability and staged validation in corp-web-app.

## Confirmed decision record for corp-web-app content unification

Detailed session records:

- `references/content-unification-decisions-2026-05-15.md`
- `references/collection-flat-matrix-rewrite-2026-05-15.md` — collection-flat MDX target correction and readable migration-matrix rewrite pattern.

When the user asks to document or implement follow-up work from the content-unification plan, carry these decisions forward unless they explicitly reopen them:

1. corp-web-japan guidance import
   - Inventory all corp-web-japan docs/guidance/repo-local skills.
   - Classify each as `copy as-is`, `adapt`, or `exclude`.
   - Use manifest path `docs/imports/corp-web-japan-guidance-manifest.md`.
   - Target docs/guidance under `docs/`; target repo-local skills under `.agents/skills/`.
2. Public route and collection policy
   - Treat `/features/**` as legacy, not as the canonical public route family for new/migrated implementations.
   - English canonical routes include the `/en` prefix; do not use unprefixed English canonicals such as `/blog`.
   - Use corp-web-japan's implemented MDX collection names and family distinctions as the target baseline. Do not re-decide or rename them based on corp-web-contents legacy paths.
   - Canonical families for English include `/en/blog`, `/en/whitepapers`, `/en/events`, `/en/news`, `/en/glossary`, `/en/manuals`, `/en/introduction-deck`, `/en/privacy-policy`, `/en/demo/use-cases`, `/en/demo/aip`, and `/en/demo/acp`.
   - Existing corp-web-contents paths may differ, but Phase 1 inventories/migration matrices should map them into corp-web-japan target families (e.g. legacy `discover/webinars` -> target `events`, legacy `learn/tutorials` -> target `manuals`, legacy `discover/white-paper` -> target `whitepapers`).
   - Korean and Japanese canonical routes use the same family path with `/ko` and `/ja` prefixes, e.g. `/ko/blog`, `/ja/blog`.
   - When a canonical route is publicly released, route matching legacy `/features/**` should initially redirect with `307 Temporary Redirect`; permanent redirect conversion is a later separate decision.
3. Content ID policy
   - Preserve existing corp-web-contents numeric IDs.
   - Default assumption: corp-web-japan numeric IDs and corp-web-contents numeric IDs are identical.
   - Verify ID equality per collection migration PR; if mismatched, do not silently renumber. Investigate/root-cause and split resolution separately.
4. Locale fallback policy
   - Public routes allow English fallback.
   - `/t/*` verification routes expose missing locales as 404.
   - Public fallback detail pages should use the English canonical URL.
   - Public locale list pages should hide missing-locale content; direct detail URL access may fallback to English.
5. `/t/*` verification policy
   - Every endpoint/collection migration is first exposed through locale-explicit `/t/*` (`/t/<locale>/<family>`), then connected to canonical public routes in a separate public-release PR.
   - `/t/*` routes are excluded from sitemap, use the final public URL as canonical, and are not linked from public navigation.
   - After publish/public release, remove the corresponding `/t/*` endpoints. Do not preserve `/t/*` compatibility paths and do not add redirects for them.
6. Blob/corp-web-contents operational scope
   - Blob Storage and corp-web-contents operational cleanup is completely out of migration scope.
   - Do not target Blob removal, env-var deletion, corp-web-contents archive/read-only/delete, upload workflow deletion, or residual-reference cleanup.
   - Even if references remain after endpoint/collection migration, ignore them for this migration scope unless the user explicitly requests separate operational cleanup.

## Blob/corp-web-contents scope framing

When documenting Blob/corp-web-contents in corp-web-app content-unification plans, be precise about scope:

- The plan may describe the current problem: MDX/frontmatter/list records and branch preview data currently flow through corp-web-contents and Blob-based content-source/content-list delivery.
- The plan should focus on replacing endpoints and MDX collections with repo-local content, loaders, assets, tests, and route contracts.
- Do **not** create a separate phase, final milestone, or PR stream for removing Blob Storage, archiving corp-web-contents, deleting environment variables, or deleting upload workflows.
- The user corrected that these paths should become unused naturally as endpoint/collection replacement accumulates, and further clarified that operational cleanup is not merely deferred but completely out of this migration scope: leftover references may remain and should be ignored unless explicitly requested later.
- Do **not** frame the plan as removing Blob Storage entirely. Blob Storage may remain appropriate for large binary asset serving such as video files.

Preferred wording and planning model:

1. Phrase the goal as making corp-web-contents no longer required for new feature/content work, not as a planned deletion project.
2. Say that endpoint/collection replacement will naturally stop using content-source/content-list Blob paths where those replacements take over.
3. Avoid action items such as "disable Blob dependency", "delete upload workflow", "remove environment variables", "archive corp-web-contents", or "run a residual dependency cleanup PR" in the core plan.
4. Large video files or other Git-unsuitable binary assets may continue to be served from Blob/object storage; repo-local content should store only metadata such as canonical URL, poster, caption, alt/description, and route usage.
5. If an operational cleanup decision becomes necessary later, treat it as a separate follow-up outside the content-unification plan, not as Phase 5 or a completion condition.
6. Completion should be described as: corp-web-app can manage feature implementation, content source, metadata, tests, and deploy previews in one repo; corp-web-contents is no longer the required path for new content work; Blob/corp-web-contents final removal is not required for plan completion.

## Planning doc update checklist

When updating a planning PR/document:

1. If the plan covers migration sequencing, make corp-web-japan guide/guidance/repo-local skill import the first concrete workstream and require a source/target/commit manifest. Use `templates/corp-web-japan-guidance-import-manifest.md` as the starter.
2. If the user resolves open decision items from the plan, create a separate decision-record document rather than burying the decisions only in chat. For this plan, use `docs/global-site-upgrade-content-unification-decisions.md`, link it from the original plan, and add it to the README docs index.
   - After the decision record exists, do not leave the original plan section titled or worded as if decisions are still pending. Rename sections such as `주요 의사결정 필요 항목` to a decision-results summary such as `주요 의사결정 결과`.
   - Keep the full decision details in the decision record. In the plan, include only a compact summary and explicitly say implementation PRs should treat the decision record as the priority source.
   - Do not fully merge the decision record back into the plan unless the user explicitly asks; plan and decision record have different review roles.
3. Replace generic `resource` language with explicit family names.
4. Ensure examples use collection-flat `src/content/{collection}/<id>-<slug>.{locale}.mdx` for multilingual MDX, with all MDX records directly under the collection root and no per-record MDX subdirectories.
5. Ensure locale-specific public assets use `filename.{locale}.extension`, not hyphenated locale suffixes such as `thumbnail-ja.png`.
6. Mention `src/lib/**` for loaders/repositories and state that new implementation/migration work should not use `src/features/**`; route entries/composition belong in `src/app/**`, UI in `src/components/**`, non-UI logic in `src/lib/**`, and content source in `src/content/**`.
7. Include the production-ready locale-explicit `/t/*` verification rollout when planning endpoint/collection migrations: implementation first behind `/t/<locale>/<family>`, endpoint validation, then a small public-release PR.
8. For static/semi-static marketing page endpoints and singleton route-owned documents, state route-local i18n authoring as a must-have implementation design: each route URI has locale-specific `page.{locale}.tsx` authoring modules; `page.{locale}.tsx` owns copy, locale-specific markup, section order, CTA, metadata, and layout/component composition; `page.tsx` is only the thin locale/fallback/metadata wrapper; common UI is extracted and text/markup is passed from the caller via children/slot-style composition.
9. Describe Blob/corp-web-contents as a scope boundary: endpoint/collection replacement should make corp-web-contents no longer required for new content work, but do not add a Phase 5, residual-dependency PR, archive/read-only decision, environment-variable deletion, or upload-workflow deletion to the plan unless the user explicitly asks for operational cleanup. If the user has confirmed scope exclusion, say leftover references are ignored for the migration scope.
10. Keep corp-web-japan references as pattern sources, not literal route/copy sources.
11. Add or update the repository README/document index if a new planning or decision-record document is added.
12. For docs-only changes, run fast checks instead of local build unless requested:
   - `git diff --check`
   - a line-prefix contamination check for copied `read_file` output.
   - a target-contract grep that allows legacy source-path examples and explicitly labelled negative examples, but fails on stale target guidance such as `<id>-<slug>/content.{locale}.mdx` or unlabelled `content.en.mdx` target examples.
13. Commit, push, and verify the PR head SHA and attached checks.

## Pitfalls

- Do not start corp-web-app feature endpoint or MDX collection implementation before importing the relevant corp-web-japan guidance/skills and recording a manifest. The user corrected that this reference import is the first step, not an optional later cleanup.
- Do not introduce `src/content/resources/**` just because corp-web-japan has resource-like pages. The user explicitly rejected ambiguous `resources` under corp-web-app content planning; corp-web-japan's current `resources` path is support data, not a collection naming model.
- Do not ask the user to make individual route/family naming decisions when they have already instructed that corp-web-japan MDX collection names should be copied as-is. Treat repeated corrections like “corp-web-japan의 mdx collection 이름을 그대로 가져오라니까” as a stop signal: stop clarifying, inspect corp-web-japan's actual `src/content/**` directories, and update the planning docs from observed names.
- Do not rename corp-web-japan collection names while adapting to corp-web-app. In particular, keep `whitepapers` (not `white-papers`) and `events` (not `webinars`) as repo-local MDX collection names unless the user explicitly reopens naming policy.
- Do not leave two alternate multilingual MDX layouts in the plan. The chosen contract is collection-flat locale-specific files directly under the collection root: `<id>-<slug>.{locale}.mdx`.
- Do not write publication/detail planning around route-adjacent `content.mdx` or `<id>-<slug>/content.{locale}.mdx`. The corrected contract is collection-flat `<id>-<slug>.{locale}.mdx`, with all MDX records for one collection directly under that collection root so the collection remains visible in one directory.
- Do not claim all copy belongs in `src/content/**`. Static/semi-static marketing pages and singleton route-owned documents should use locale-specific route-local authoring in `page.{locale}.tsx`, with `page.tsx` kept as a thin wrapper.
- Do not introduce or preserve route-adjacent `<route>/content.mdx` as the singleton document exception in corp-web-app planning; the user corrected this to `<route>/page.{locale}.tsx` authoring plus thin `<route>/page.tsx`.
- Do not copy Japan-only route policy or Japanese-only content decisions into the global site plan without explicit adaptation. The exception is the endorsed `/t/*` verification rollout pattern: use `/t/*` to stage production-ready corp-web-app implementations before endpoint-by-endpoint public release.
- Do not bundle a separate phase-scope, guidance-import, or other planning document into a focused plan/decision PR just because it is present as untracked root-checkout residue. Verify whether the file came from another branch/agent first; if it did, leave it to that PR and keep the current diff to the requested plan/decision documents.
- Do not make Blob/corp-web-contents cleanup a phase or completion condition in the plan. The user corrected that this is outside the planning scope: as endpoints/collections move to repo-local content, the old content-source paths will naturally stop being used. Avoid Phase 5, residual dependency PRs, archive/read-only decisions, env-var deletion, and upload-workflow deletion unless explicitly requested as separate operational cleanup.
- Do not make the Blob/corp-web-contents scope sound like removing Blob Storage as a platform. Blob Storage can remain for video file serving or other large binary asset delivery; the plan should focus on endpoint/collection replacement, not Blob platform retirement.
- Do not plan or phrase corp-web-app migration as a whole-site batch conversion/replacement. The user corrected that existing-feature replacement and content migration must proceed independently by endpoint and by MDX collection.
- Do not rewrite MDX collection migration matrices as a single huge wide table when the user asks for a document rewrite. Use readable Korean collection sections with small field/value tables, a priority summary, and a separate non-collection endpoint section.
- Do not describe `src/features/**` as an independent feature-domain destination or as merely "not the default". The corrected corp-web-app planning rule is stronger: do not use `src/features/**` for new implementation/migration work; map code to `src/app/**`, `src/components/**`, `src/lib/**`, or `src/content/**` by responsibility.
- Do not say code layout "follows corp-web-japan" without spelling out the adapted code-location classification. The user corrected that the plan must reflect corp-web-japan's directory responsibility split: route entry/composition in `src/app/**`, page/domain UI in `src/components/sections/**`, reusable primitives in `src/components/ui/**`, non-UI logic in `src/lib/**`, explicit source content in `src/content/**`, route-aligned assets in `public/**`, and tests under `tests/**` or source-near `__tests__`.
- Do not make route-local i18n authoring sound like a nice-to-have, a naming experiment, or only one possible authoring surface for static/semi-static marketing pages. The user corrected that this is a required corp-web-app implementation design: each route URI should have `page.{locale}.tsx` authoring files, those files own text/markup/order/CTA/metadata/layout choice, `page.tsx` is only a thin wrapper, and shared UI should receive caller-authored text/markup via children/slots.