---
name: corp-web-japan-website-migration-plan-wiki
description: Create or refresh a corp-web-japan GitHub wiki migration-plan dashboard that shows what is already local, what still depends on querypie.com/ja, and what should be migrated next in priority order.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, wiki, migration, dashboard, replacement-readiness]
    related_skills: [github-wiki-editing, github-wiki-update-from-main]
---

# corp-web-japan website migration plan wiki

Use this when the user asks for a GitHub wiki page that explains how far `corp-web-japan` has progressed toward replacing `https://www.querypie.com/ja`, especially as a readable migration dashboard rather than a prose-only plan.

## Goal

Produce a wiki page that answers, at a glance:
- what is already publicly owned by `corp-web-japan`
- what is only partially migrated
- what still redirects to `querypie.com/ja`
- what should be migrated next, in priority order

The most useful output is a replacement-readiness dashboard, not a generic architecture memo.

## When to use

- "Write a migration plan on the corp-web-japan wiki"
- "Show completed vs remaining migration scope"
- "Can corp-web-japan replace querypie.com/ja yet?"
- "Summarize migration progress as of latest main or a specific date"

## Core framing

For this repo, the most important distinction is usually not just content existence but public-entrypoint ownership.

A family may have:
1. local detail routes already implemented
2. preview `/t/*` list/page implementations already available
3. but the public entrypoint still redirecting to `querypie.com/ja`

In that case, treat the family as only partially migrated and usually prioritize it highly.

## Required workflow

### 1. Confirm repo and source-of-truth branch

In the product repo:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git fetch origin --prune
```

If the user specifies a historical baseline date such as "latest main on 2026-05-05", do not document current `origin/main` blindly.
Resolve the exact commit first:

```bash
git rev-list -n 1 --before='2026-05-05 23:59:59' origin/main
```

Record that SHA in the wiki page.

If the user truly wants the current latest main, then use `origin/main` after fetch.

### 2. Use the separate wiki repo, preferably through a worktree if a maintained local clone already exists

If the user/repo setup already has a stable local wiki clone such as `../corp-web-japan.wiki`, prefer reusing it.
A clean pattern is:
- keep the maintained wiki clone as the base checkout
- create a dedicated git worktree from that wiki repo for the page edit
- commit in the worktree branch
- fast-forward the base wiki branch and push from the base clone

This avoids mixing wiki edits into an existing local wiki checkout while still respecting the user's established local clone.

### 3. Gather the current route surface from code

Use these files as the main sources of truth:
- `README.md`
- route files under `src/app/**`
- `src/app/sitemap.ts`
- content loaders and href builders under `src/lib/publications/**`
- repo-local wiki pages like `Sitemap.md`, `Blog.md`, `WhitePapers.md`, `Events.md` only as supporting references

For this task, classify routes into four buckets:
1. public local entrypoints
2. public redirect-backed entrypoints
3. preview/local-only `/t/*` entrypoints
4. local detail-route families

This classification is usually more valuable than a flat route list.

### 4. Quantify migration status from code, not intuition

Useful counts to collect:
- number of public local entrypoints
- number of public redirect-backed entrypoints
- number of preview `/t/*` entrypoints
- number of local detail-route families
- MDX/content counts per family

Useful family roots include:
- `src/content/blog`
- `src/content/whitepapers`
- `src/content/news`
- `src/content/use-cases`
- `src/content/demo/aip`
- `src/content/demo/acp`
- `src/content/events`
- `src/content/documentation/manuals`
- `src/content/documentation/introduction-deck`
- `src/content/documentation/glossary`

If the baseline is a historical main snapshot, count from that exact git revision rather than the live working tree.
A reliable pattern is either:

```bash
git ls-tree -r --name-only <sha> <path>
git show <sha>:path/to/file
```

or archive that commit to a temp directory and inspect the extracted snapshot.

### 5. Important corp-web-japan interpretation rules

Use these audit rules consistently:

- `/blog`, `/whitepapers`, `/news`, `/contact-us`, `/`, `/solutions/ai-crew`, and `/solutions/ai-dashi` can count as public-local when implemented as actual pages on the baseline snapshot.
- `/demo/use-cases`, `/demo/aip`, `/demo/acp` should be treated as partial if the public routes still redirect even when local detail routes already exist.
- `/events` should be treated as partial if the page exists but is launch-gated or returns `notFound()` without an unblock condition.
- `/about-us`, `/certifications`, `/services/*`, and resource hubs like `/resources`, `/manuals`, `/glossary`, `/introduction-deck` should be treated as partial when public routes still redirect but `/t/*` preview pages exist.
- legal pages such as `/cookie-preference`, `/terms-of-service`, `/privacy-policy`, and `/eula` should usually be shown as redirect-only / scope-decision items unless local pages have actually been implemented.
- If a local list is public but many detail records still redirect externally by `redirectUrl`, label that family as partially local or mixed, not fully local.

### 6. Recommended page structure

A clear migration dashboard page usually works best with this structure:

1. Purpose
2. Baseline
3. Executive summary
4. Dashboard table
5. Family-by-family detail
6. Recommended migration order
7. Optional swim-lane or mermaid chart
8. Practical conclusion
9. Related pages

Recommended dashboard columns:
- Area
- Public status on the baseline date
- Baseline evidence
- Replacement readiness
- Next action
- Priority

### 7. Priority model that works well in corp-web-japan

Use:
- `P0` = replacement blockers at the public-entrypoint layer
- `P1` = deepen local ownership inside already-local families
- `P2` = optional or explicit-scope decisions

Typical `P0` candidates:
- services public rollout
- company public rollout
- demo list public rollout
- events public rollout
- resource hub public rollout

Typical `P1` candidates:
- news detail localization where many records still redirect externally
- cleanup of blog or whitepaper shadow/redirect records if full local ownership is desired

Typical `P2` candidates:
- legal-page localization
- long-tail compatibility cleanup

## Important experiential lessons

### Historical-baseline lesson

If the user asks for "May 5 latest main" or a similar date-specific snapshot, the correct basis is not today's `origin/main`.
Resolve the historical main commit with `git rev-list --before` and use that SHA consistently in both counts and conclusions.

### Wiki-worktree lesson

When a stable local wiki clone already exists, a wiki worktree is a good compromise between a fresh temp clone and editing the base wiki checkout directly.
It keeps the edit isolated, makes review/diff clearer, and still lets you fast-forward the main local wiki clone before pushing.

### Replacement-readiness lesson

The most useful conclusion for corp-web-japan replacement audits is usually:
- content migration may be far along
- but replacement is still blocked by redirect-backed top-level public entrypoints

Spell this out clearly instead of only listing migrated MDX counts.

### Redirect/shadow interpretation lesson

Do not frame hidden redirect records or shadow records as cleanup candidates by default.
In this repo, they often exist intentionally to preserve legacy entrypoints, avoid 404s, and route old links toward the correct current canonical content.

Important audit rule:
- treat compatibility-preserving redirects as a positive protection layer unless evidence shows they are wrong or unnecessary
- do not recommend reducing or removing them just to increase "local ownership purity"
- only flag them when one of these is true:
  - the redirect target is missing or broken
  - the redirect points to the wrong content family or materially wrong content
  - there is evidence the redirect is obsolete, such as verified zero-traffic / fully-updated-link guarantees explicitly accepted by the user

When documenting migration status, describe these records as legacy-preservation or canonicalization support, not as blockers or cleanup debt unless you have concrete evidence.

Useful wording patterns:
- "hidden redirect record preserves a legacy entrypoint and forwards to the current canonical local page"
- "shadow record supports compatibility / canonical consolidation"
- avoid wording like "should be reduced" or "remaining cleanup" unless the user explicitly asks for cleanup planning and the evidence supports it

### Count-verification lesson

Before finalizing summary counts like preview entrypoints, verify them from actual route files.
It is easy to overcount `/t/*` surfaces by memory.
Use a small script or exact file listing and correct the page before publish if needed.

### Cross-language source-of-truth lesson

When the user explicitly says one wiki language page is the latest source of truth (for example `Website-Migration-Plan-ko`) and asks you to update sibling pages from it, do not re-derive JA/EN content from `origin/main` unless the user also asks for a fresh audit.

Preferred approach:
1. read the designated source wiki page first
2. update the sibling wiki pages to match that source page's conclusions, counts, baseline timestamp, and baseline SHA
3. preserve the designated source page's snapshot framing even if the product repo's current `origin/main` has advanced since that page was written
4. still verify and push through the wiki git repo normally

Why this matters:
- these migration-plan pages can intentionally lag the latest code until the canonical source page is refreshed
- if you silently re-audit from current `origin/main`, JA/EN can diverge from KO again instead of being synchronized
- in this workflow, the user asked for translation/synchronization against the canonical wiki page, not a new repository-state assessment

### Route-kind verification lesson

When classifying public redirect-backed entrypoints on latest `main`, do not check only for `page.tsx`.
In `corp-web-japan`, many redirect-backed public entrypoints are implemented as `route.ts` redirect handlers instead of pages.
For migration dashboards, audit each candidate route directory for at least:
- `page.tsx`
- `route.ts`

This matters especially for:
- `/services/*`
- `/demo/*` list entrypoints
- `/resources`, `/glossary`, `/manuals`, `/introduction-deck`
- `/about-us`, `/certifications`
- legal entrypoints such as `/privacy-policy`

If you check only for `page.tsx`, you can incorrectly report zero redirect-backed public entrypoints even though the redirect routes are present on latest `main`.

### Resource-content root lesson

For resource preview/publication migration summaries in `corp-web-japan`, do not assume the local content roots are already flattened to top-level `src/content/<family>` paths.
On the current mainline snapshot, introduction deck / glossary / manuals content may still live under:
- `src/content/documentation/introduction-deck`
- `src/content/documentation/glossary`
- `src/content/documentation/manuals`

Audit the actual latest-main tree before writing corpus counts or source-root notes into the wiki page.

## Verification checklist

- baseline SHA recorded correctly
- route classification reflects the code snapshot, not assumptions
- public-local vs redirect-backed vs preview-only split is explicit
- priority table highlights replacement blockers first
- any numeric summaries were rechecked from files/scripts
- wiki file committed and pushed successfully
- Home/wiki index updated if the new page should be discoverable

## Pitfalls

- treating preview-complete families as fully migrated when the public route still redirects
- documenting current main when the user requested a historical main date
- counting local detail routes as equivalent to public replacement readiness
- forgetting that many news/blog/whitepaper records may still use `redirectUrl`
- editing the base wiki clone directly when a worktree would keep the change safer and cleaner
