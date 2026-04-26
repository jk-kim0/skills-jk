---
name: querypie-com-content-migration-type-wiki-update
description: Update corp-web-v2 wiki migration inventory pages to classify legacy querypie.com content as static-page or MDX, using latest origin/main as source of truth and publishing changes to the separate wiki repo.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-v2, wiki, content-migration, MDX, static-page, classification]
    related_skills: [github-wiki-update-from-main]
---

# querypie.com content migration type wiki update

Use this when the user asks whether legacy `querypie.com` content can be migrated with two formats — per-page static implementation vs MDX — and wants the classification written back into the `corp-web-v2` GitHub wiki tables.

## Goal

Update the migration comparison wiki pages so every legacy content row is marked with a recommended migration type:
- `정적 페이지`
- `MDX`

Also create or update a separate strategy page explaining why the two-format approach is sufficient and what the pros/cons are.

## Required source of truth

Always use latest `origin/main` of `querypie/corp-web-v2`.
Also record the latest main SHAs for:
- `querypie/corp-web-app`
- `querypie/corp-web-contents`

The wiki must be edited through the separate `.wiki.git` repo, not the product repo.

## Expected wiki pages

Usually update these pages together:
- `querypie-com-Content-Migration-Comparison-Table.md`
- `querypie-com-Demo-Content-Migration-Comparison-Table.md`
- `querypie-com-Blog-Content-Migration-Comparison-Table.md`
- `querypie-com-White-Paper-Content-Migration-Comparison-Table.md`
- `querypie-com-Legal-Content-Migration-Comparison-Table.md`

Usually create or update this separate strategy page:
- `querypie-com-Content-Migration-Type-Strategy.md`

## Classification rule used in this repo

### Classify as `정적 페이지`

Use for routes where the page-level UX and component composition are the core implementation:
- home
- company pages (`about-us`, `certifications`, `contact-us`, `news` list)
- plans
- listing/index pages (`/features/demo`, `/features/documentation`)
- solutions pages
- search
- community-license
- cookie preference

These usually correspond to dedicated `page.tsx` files with bespoke section composition, CTA orchestration, filtering, forms, or interactive UI.

### Classify as `MDX`

Use for document/detail-style content where the primary asset is the body content and a shared layout can render it:
- demo detail content
- documentation detail content
- blog
- white paper
- most legal documents

In this repo, strong MDX evidence includes:
- `src/content/mdx/**`
- route loaders like `src/features/mdx/loader.ts`
- detail routes such as:
  - `src/app/[locale]/blog/[id]/[[...rest]]/page.tsx`
  - `src/app/[locale]/white-paper/[id]/[[...rest]]/page.tsx`

For documentation/demo managed content, still classify as `MDX` when the desired future migration style is document-body oriented, even if current implementation reads managed HTML/Tiptap content instead of files under `src/content/mdx/**`.

### Important interpretation rule

Do NOT treat these as separate migration formats:
- download aliases
- redirect endpoints
- locale fallback
- gating wrappers

They are delivery/routing behaviors layered on top of either static-page or MDX content.

## Recommended repo inspection workflow

### 1. Fetch latest main

In product repo:

```bash
git fetch origin main
git rev-parse FETCH_HEAD
git log --oneline -1 FETCH_HEAD
```

### 2. Build a clean latest-main snapshot

Use archive extraction so local worktree state cannot pollute the audit:

```bash
tmpdir=$(mktemp -d)
git archive --format=tar FETCH_HEAD | tar -xf - -C "$tmpdir"
```

Inspect the extracted snapshot, not a dirty local tree.

### 3. Confirm implementation patterns in latest main

Read at minimum:
- `src/features/content/config.ts`
- `src/features/content/authored.server.ts`
- `src/features/mdx/loader.ts`
- `src/app/[locale]/blog/[id]/[[...rest]]/page.tsx`
- `src/app/[locale]/white-paper/[id]/[[...rest]]/page.tsx`
- representative static routes such as:
  - `src/app/[locale]/page.tsx`
  - `src/app/[locale]/company/about-us/page.tsx`
  - `src/app/[locale]/company/contact-us/page.tsx`
  - `src/app/[locale]/plans/page.tsx`
  - legal routes

### 4. Check MDX file coverage

Inspect:
- `src/content/mdx/blog/**`
- `src/content/mdx/white-paper/**`

This gives strong evidence for blog/white-paper classification.

### 5. Record legacy-repo SHAs

If local clones are unavailable, use `git ls-remote`:

```bash
git ls-remote git@github.com:querypie/corp-web-app.git refs/heads/main
git ls-remote git@github.com:querypie/corp-web-contents.git refs/heads/main
```

## Wiki editing pattern

### Main comparison page

Add or update:
- latest update date
- latest `corp-web-v2` SHA
- a short `이관 형식 분류 기준` section
- a link to the separate strategy page
- summary counts for `정적 페이지` and `MDX`
- `추천 이관 유형` column in each table that still lives in the main page

### Split pages

For demo/blog/white-paper/legal pages:
- add a short `추천 이관 유형 요약` section
- add `추천 이관 유형` column to the comparison table
- classify every row individually, not just the category header

### Separate strategy page

Document:
- conclusion that two formats are sufficient
- why static-page is needed
- why MDX is needed
- how shared MDX components absorb mixed content needs
- selection criteria table
- pros/cons of each format
- repo-specific summary counts
- handling of exceptions such as download routes, redirects, locale fallback, legal content

## Efficient edit method

When many wiki rows need the same extra column, use a scripted transformation instead of manual patching row-by-row.
A safe approach is:
- read the raw wiki markdown from the cloned wiki repo
- transform table headers/separators/rows programmatically
- write files back as plain markdown
- re-read and diff before commit

This is especially useful when adding the same `추천 이관 유형` column across multiple large tables.

## Known classification outcome from the 2026-04-26 audit

Using `querypie/corp-web-v2` main `12bab42d798dcc7e499254f755aac06142a4c6f7`:
- total legacy public rows: `210`
- `정적 페이지`: `22`
- `MDX`: `188`

Category-level outcome:
- core/static content: mostly `정적 페이지`
- demo detail: all `MDX`
- documentation detail: all `MDX`
- blog: all `MDX`
- white paper: all `MDX`
- solutions: all `정적 페이지`
- legal: only `cookie preference` is `정적 페이지`; the rest are `MDX`

## Important demo-route audit lesson from later main updates

Do not conflate `추천 이관 유형 = MDX` with `현재 공개 canonical path가 short route로 이미 전환되었다`.

For demo wiki updates, these are separate questions:
1. migration type classification (`MDX` vs `정적 페이지`)
2. latest-main current public route actually implemented today

Latest-main finding from `querypie/corp-web-v2` `origin/main` `e634bcfa51d10468bfd31b886d09ec16e264a372`:
- `ACP Features`: short MDX route is implemented at `/demo/acp/:id/:slug`
- legacy ACP route `/features/demo/acp-features/:id/:slug` redirects to that canonical short route
- `AIP Features`, `Use Cases`, `Webinars`: still resolve through managed-content detail route `/features/demo/[slug]`
- therefore these rows are still classified as `MDX`, but their current public path should remain `/features/demo/<slug>` until short routes are actually implemented on latest main

When rewriting `querypie-com-Demo-Content-Migration-Comparison-Table`:
- keep `추천 이관 유형` as `MDX` for all demo detail rows
- audit route implementation separately from migration-type strategy
- explicitly note when a short-route plan exists conceptually but is not yet present on latest main
- preserve unmatched rows as `—` rather than guessing the intended future path

## Verification

After editing wiki files:

```bash
git add ...
git commit -m "docs: classify content migration by static page vs mdx"
git push origin master
git fetch origin master
git rev-parse HEAD
git rev-parse origin/master
```

Then verify remote file contents with `git show origin/master:<page>.md`.

## Pitfalls

- Do not assume current local repo state equals latest main.
- Do not edit only the product repo; the wiki is separate.
- Do not invent a third migration type for redirects/downloads.
- Do not classify listing/filter/form pages as MDX just because they are content-related.
- For legal content, keep `cookie preference` as static-page and treat versioned document pages as MDX-style document migration.
