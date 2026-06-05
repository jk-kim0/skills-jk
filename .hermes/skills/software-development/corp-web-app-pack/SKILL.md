---
name: corp-web-app-pack
description: Use when working in corp-web-app, especially route-local authoring, Tailwind migration, content unification, or stage E2E tasks. Thin active entrypoint that points to the inactive repo-specific skill pack index instead of injecting every detailed skill into the default skills index.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-skill-pack, corp-web-app, prompt-size]
    related_skills: []
---
# corp-web-app Pack

## Overview

This is a thin active entrypoint for the `corp-web-app` repo-specific skill pack. The detailed skills live outside active `.hermes/skills/` at:

`.hermes/skill-packs/corp-web-app/`

Keeping the detailed skills outside `.hermes/skills/` prevents their full name/description index from being injected into every default Hermes request.

## When to Use

- Use when working in corp-web-app, especially route-local authoring, Tailwind migration, content unification, or stage E2E tasks.
- The user explicitly mentions `corp-web-app` or a task clearly belongs to that repository/workstream.
- You need repo-specific historical workflow, route/content, visual parity, CI, or PR guidance for this area.

## Required First Step

First check whether this repository exposes repo-local checked-in skills under `.agents/skills/`.

In the current `corp-web-app` setup, treat `.agents/skills/README.md` as the first local index and load only the minimum matching repo-local skills from `.agents/skills/<name>/SKILL.md`.

If a future checkout instead uses the external pack layout, read the pack index before selecting detailed skills:

`.hermes/skill-packs/corp-web-app/INDEX.md`

Then read only the specific `SKILL.md` files referenced by the index that match the current task.

## Task References

- `references/japanese-news-company-name-and-press-contact.md` — Japanese news rule: company-reference `QueryPie` should be `QueryPie AI`, Japanese press-release QueryPie Website/URL lines should use `https://querypie.ai`, older `本件に関するお問い合わせ先` sections must be included, and `docs/news.md` locale examples outside Japanese should not be changed unless explicitly scoped.
- `references/introduction-deck-mdx-gating.md` — proven pattern for fixing gated introduction-deck MDX detail pages by splitting at `<GatingCut />`, rendering the post-cut content behind `GatingFormWrapper`, and using a temporary root `node_modules` symlink for fast fresh-worktree verification when appropriate.
- `references/publication-author-data-location.md` — author/profile data placement and PR follow-up pattern for blog/whitepaper detail author cards.
- `references/author-profile-image-validation.md` — investigation and hardening pattern for broken publication author profile images: resolve MDX `author` through locale YAML, verify the referenced `public/crew/*` asset and deployed raw/`/_next/image` URLs, and compare against corp-web-japan's `src/content/authors/ja.yaml` + `public/crew/*` + validation-test pattern.
- `references/blog-mdx-translation-coverage.md` — workflow for finding and filling missing blog MDX locale files from historical corp-web-contents inventories, preserving hidden redirect contracts, protecting MDX/HTML syntax during translation, and verifying EN/KO/JA coverage parity.
- `references/news-mdx-live-list-id-realignment.md` — workflow for aligning `src/content/news` MDX IDs/assets/tests with live KO/EN/JA company-news lists so default id-desc ordering equals date-desc/live ordering, with narrow replacement and verification guardrails.
- `references/news-mdx-source-body-completion.md` — follow-up workflow for enriching news MDX bodies from linked media coverage: identify PR-added MDX files, parse source articles, fix mismatched source links, and write faithful rewritten summaries instead of verbatim article copies.
- `references/news-pr-rebase-mdx-id-guardrails.md` — PR rebase workflow for news/press-release docs that must be moved onto latest main and aligned with the current maximum `src/content/news` MDX id before force-push.
- `references/news-mdx-type-labels.md` — guidance for implementing news MDX type labels (`official-announcement`, `press-release`, `news`) without relying on localized free-form `sourceLabel` strings.
- `references/news-hero-image-metadata.md` — pattern for improving `/<locale>/news` and news detail metadata so Open Graph/Twitter images use MDX/list hero images, with focused Vitest verification.
- `references/news-id-only-404-diagnosis.md` — diagnostic and implementation pattern for reported `/<locale>/news/<id>` 404s: compare `x-matched-path`, confirm canonical `/<locale>/news/<id>/<slug>` route/content, and add a thin ID-only redirect route when external/backward compatibility requires it.
- `references/archived-tailwind-exclusion.md` — Tailwind migration planning rule for archived routes: keep `src/app/(legacy)/[locale]/archived/**` as legacy preservation/redirect targets, audit the archived index for IA completeness and stage 200s, and close archived Tailwind conversion PRs rather than treating them as migration backlog.
- `references/metadata-title-brand-suffix-parity.md` — review pattern for `metadata.title` / Open Graph title changes when comparing `corp-web-app` against `corp-web-japan`; verify source implementation and live rendered title, and prefer source-site `Page Title | QueryPie AI` parity when explicitly requested.
- `references/app-router-locale-route-shadowing.md` — debugging/fix pattern for App Router dynamic locale routes such as `/[locale]/news` shadowing unprefixed legacy/public routes such as `/company/news`; inspect `x-matched-path`, middleware default-locale rewrites, route tree, and catch-all behavior before diagnosing content as missing.
- `references/news-thumbnail-background-matching.md` — asset-only workflow for matching news/publication SVG thumbnail backgrounds to an existing reference PNG by sampling border/corner pixels, removing rounded-card layers, and verifying SVG/XML plus target attributes before commit.
- `references/company-news-legacy-redirect-query.md` — route/test pattern for legacy `/company/news` and `/{locale}/company/news` redirects when query strings must be stripped by clearing `targetUrl.search`.
- `references/news-type-frontmatter-rebase-ci.md` — CI/debugging pattern for news MDX PR rebases where `newsType` frontmatter exists but publication tests render generic news badges or see `post.newsType` as `undefined`; preserve the current `newsType` contract through `ResourceRecord` and news detail UI rather than weakening tests or reintroducing `sourceLabel`.
- `references/mdx-resource-id-rebase.md` — workflow for rebasing corp-web-app PRs that add MDX-backed resources/publications with numeric frontmatter ids: verify the exact PR number, rebase onto latest `origin/main`, assign new entries after the current max id, check duplicates, and verify the pushed PR head.
- `references/news-mdx-rebase-ci-newsType-assets.md` — follow-up pattern for news MDX PRs after rebase/squash: keep latest-main `newsType` loader/UI contracts, diagnose CI failures where frontmatter fields are not preserved into `ResourceRecord`, replace route-aligned news assets cleanly, apply article image display constraints with `ArticleFileImage`, and verify new PR head status after amend/force-push.
- `references/news-sitemap-blob-augmentation.md` — pattern for augmenting the Blob-backed public `sitemap.xml` with repo-local news list/detail routes, including origin selection, dedupe, hidden/noindex exclusion via repository candidates, and Vitest placement outside dotted route directories.
- `references/mdx-collection-sitemap-index.md` — pattern for replacing one-off sitemap augmentation with `/sitemap.xml` as a sitemap index, `/sitemap/legacy.xml`, and concrete `/sitemap/<collection>.xml` endpoints for repo-local MDX/resource collections; includes rebase guidance when narrower sitemap PRs already landed.
- `references/news-mdx-localized-boilerplate-sync.md` — workflow for making multilingual news company boilerplate and media-contact sections exactly match another PR/article while keeping the sync in a separate latest-main PR.
- `references/japanese-news-querypie-ai-company-name.md` — Japanese news copy rule: use `QueryPie AI` when referring to the company, preserve product names such as `QueryPie AIP` and `QueryPie AI Platform`, and verify with a standalone-`QueryPie` regex check.
- `references/news-localized-hero-image-publication.md` — pattern for applying language-specific draft/Open Graph images to localized news MDX hero images, adding missing EN/KO/JA MDX files, and verifying public URL paths against `public/news/<id>/...` assets.
- `references/news-mdx-translation-locale-counts.md` — workflow for adding missing localized news MDX translation files for an existing ID, preserving frontmatter contracts, updating news migration record/list counts, and using lightweight source-level verification before PR.
- `references/news-internal-translations-hidden-coverage.md` — pattern for keeping public news lists hidden-filtered while showing hidden URL-accessible records with a `Hidden` label on `/{locale}/internal/translations/news`.
- `references/news-internal-translation-coverage-test-drift.md` — CI/debugging pattern for `Test routing` failures when the internal news translation coverage tests hard-code stale record counts, first-row IDs, or missing-locale samples after new news MDX records land.
- `references/news-visible-mdx-addition.md` — pattern for adding a visible news MDX item from latest main: allocate the next id, use route-aligned `public/news/<id>/` assets, set `hidden: false`, avoid default translation beyond the supplied locale, and verify frontmatter/lightweight source checks before PR.
- `references/press-release-subtitle-mdx-formatting.md` — pattern for representing a press-release subtitle/deck as centered italic MDX (`<Box center>` + centered `<p>` + `<em>`) instead of unintended `##` section headings/TOC entries across localized news files.
- `references/pr-validity-superseded-route-rollout.md` — pattern for reviewing old corp-web-app PRs that may be superseded by route-group/public-rollout work: fetch latest main and PR head, compare ahead/behind, account for URL-transparent `(tailwind)`/`(legacy)` route groups, locally merge to verify conflicts, and cite current main tests/replacement PRs before recommending close/rewrite.
- For PR follow-up in this repo, apply the GitHub workflow `references/pre-push-pr-state-guard.md` guard before pushing: verify the target PR is still open and its head SHA/ref matches the branch. If a PR has already merged, update a relevant open follow-up PR or create a fresh branch from latest `origin/main`; do not push to the old merged PR branch name.

## Common Pitfalls

1. For corp-web-app PR description-only updates, inspect the live PR files/commits with `gh pr view` and rewrite from that evidence; apply via `gh pr edit --body-file` and verify by re-reading the PR body. Keep PR descriptions in Korean for this user's repo-work convention unless explicitly asked otherwise.
2. For repo PR scope-splitting work, do not leave extracted schema/content-model changes in the original PR. Create a fresh main-based branch for the extracted change, remove the feature completely from the original PR, and verify both source-tree and PR-diff residue checks. When grepping PR diffs for removed fields, match added lines explicitly such as `grep '^+sourceLabel:'`; a plain `grep 'sourceLabel'` also matches deletion lines and can create false residue alarms. See `github-pr-workflow` reference `references/pr-feature-extraction-and-scope-splitting.md`.
2. Do not assume these detailed skills are available through `skill_view`; they are intentionally outside active skill discovery.
2. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
3. If this pack is needed frequently in a dedicated profile, symlink or copy `.hermes/skill-packs/corp-web-app/skills/*` into that profile's active `.hermes/skills/` instead of re-expanding the default profile.
4. For publish/public-route conflict reviews in `corp-web-app`, do not stop at filesystem route existence. Also inspect the legacy catch-all route, preview-navigation mappings, URL-transparent route groups such as `src/app/(tailwind)/**` and `src/app/(legacy)/**`, and live production responses/redirects, because a public path can already be behaviorally occupied even when no dedicated ungrouped App Router file exists. For old PR validity checks, verify against latest `origin/main` with a local merge attempt; GitHub's displayed merge state can be stale or less informative than the current fetched main.
5. In this repo, the active skill source may be `.agents/skills/**` rather than `.hermes/skill-packs/**`; verify the real local skill root before assuming the pack layout.
6. For gated introduction-deck MDX, do not render the entire body with `GatingCut: () => null`; split at the marker first so the post-cut content and download CTA stay behind the form.
7. Treat localized author/profile JSON as publication content, not utility implementation. In corp-web-app it belongs under `src/content/authors/{en,ja,ko}.json`; utilities such as `composeAuthors` should import from that content path rather than keeping data under `src/utils/**/data`.
8. During PR follow-up on resource/publication work, expect latest `main` to have renamed `src/lib/repo-content/**` to `src/lib/resources/**`. On rebase conflicts, preserve the latest-main `src/lib/resources` import paths and reapply only the PR's scoped author/rendering changes.
9. For blog MDX missing-locale recovery, do not invent translations when the user asked for source recovery only. First exhaust historical corp-web-contents inventories and sibling/canonical publication records; only directly translate unfound content if the user explicitly changes scope to permit direct translation.
10. For metadata title reviews in `corp-web-app`, apply the current app-level default first: ordinary page metadata should use `Page Title | QueryPie` across `metadata.title`, `openGraph.title`, and `twitter.title` when present. When `corp-web-japan` is cited, inspect the Japan source/live title as source evidence, but treat `Page Title | QueryPie AI` as an explicit parity exception rather than the default. Avoid slogan-like `QueryPie AI: Page Title` for ordinary subpages unless a documented page-family/product policy requires it.
11. For news MDX live parity work, do not force a 1:1 translated collection. Live KO/EN/JA company-news lists can have different item counts and missing locales. Assign ids by logical article identity, not blindly by live image number, and sort news lists by date when semantic ids are non-monotonic. See `references/news-mdx-live-company-news-parity.md`.
12. When an App Router locale-route shadowing fix or legacy compatibility redirect is discovered during an unrelated feature PR, split it into a separate PR unless the user explicitly asks to bundle it. For route-handler redirect fixes, also follow the repo CI test-group naming convention documented in `references/app-router-locale-route-shadowing.md`.
13. When adding visible news MDX records, update the source-based publication tests alongside the content: distinct news id count, total localized record count, locale-specific list counts, and list image assertions. Do not leave tests hard-coded to the previous collection size or to `thumbnail.(png|svg)` only when the new record intentionally uses route-aligned localized hero assets such as `/news/<id>/hero-ja.png`. Keep the assertion broad enough to enforce `public/news/<id>/...` while allowing valid localized hero filenames.
14. For collection sitemap PRs, follow `references/mdx-collection-sitemap-index.md`: keep `/sitemap.xml` as a sitemap index, add concrete `/sitemap/<collection>.xml` route files, exclude privacy-policy from sitemap targets, and update `scripts/ci/test-groups.mjs` when new sitemap tests live under a new `__tests__` subtree. If only some child sitemap families are public, keep a complete endpoint registry but add an explicit index-exposure filter such as `includeInSitemapIndex` / `mdxSitemapIndexCollections` so `/sitemap.xml` does not advertise `/<locale>/t/*` verification-route families.
15. When `Test routing` fails in the internal news translation coverage test after news MDX records changed, do not patch only stale numeric literals. Follow `references/news-internal-translation-coverage-test-drift.md`: use `listNewsTranslationItems()` as the expected count/order source and choose locale-preview samples by data shape.
16. When rewriting a docs-only PR that establishes future press-release company boilerplate/media-contact rules from another PR, keep the document narrowly normative: reference the source PR as the baseline, delete candidate copy/source-summary/ID-allocation notes unless explicitly requested, and verify the exact localized section headings from the reference PR diff before documenting them (for example, do not guess the Japanese `About QueryPie` heading).

## Verification Checklist

- [ ] `.hermes/skill-packs/corp-web-app/INDEX.md` was read when present, otherwise repo-local `.agents/skills/README.md` was used.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.
- [ ] Publication author/profile data changes keep JSON under `src/content/authors/`, with `composeAuthors` API stable unless the task explicitly changes the content model.
