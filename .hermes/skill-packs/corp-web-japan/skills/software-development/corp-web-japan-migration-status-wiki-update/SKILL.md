---
name: corp-web-japan-migration-status-wiki-update
description: Update corp-web-japan Website-Migration-Plan wiki pages from latest origin/main using a strict migration-completeness lens, not content-richness or speculative cleanup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, wiki, migration, latest-main, documentation]
    related_skills: [github-wiki-update-from-main, github-wiki-editing]
---

# corp-web-japan migration-status wiki update

Use this when updating `Website-Migration-Plan-ko`, `Website-Migration-Plan-ja`, or `Website-Migration-Plan` in the corp-web-japan wiki.

## Core lens

Evaluate only this question:

- Has existing `querypie.com/ja` content/functionality been fully migrated and locally replaced in `corp-web-japan`?

Do **not** frame these as migration gaps unless the user explicitly asks:
- content richness / corpus size / “only 1 item exists” style concerns
- intentional hidden / redirect / gated records in blog or whitepapers
- speculative cleanup ideas that do not change whether the old public surface is locally replaced

## What counts as real remaining migration work

Typical real blockers:
- a public route is still an external redirect instead of a local canonical page
- only a preview `/t/*` page exists, not the public canonical route
- a public list/detail surface still cannot serve the equivalent role of the old site
- legal pages remain redirect-only and the local-replacement scope is still undecided

Typical non-blockers:
- hidden/redirect/gated MDX records that are intentionally part of the current policy
- small corpus size when the relevant public route family is already migrated
- internal refactors, file renames, helper-path moves, or loader reshuffles that do not change the public replacement status

## Required workflow

1. Fetch latest `origin/main`.
2. Read the current wiki page.
3. If the page already records an older baseline SHA, diff old SHA vs latest `origin/main` under `src/app`, `src/content`, and `src/lib`.
4. Re-audit only route/status changes that affect migration completeness.
5. Update:
   - baseline timestamp/SHA
   - local public entrypoint count
   - remaining redirect-backed entrypoint count
   - preview-only `/t/*` inventory
   - migrated vs partial vs not-yet-migrated status
   - remaining blockers and priorities
6. Commit/push the wiki repo and verify with `git show origin/master:<page>.md`.

## Practical corp-web-japan lessons

- `events` should be treated as incomplete only while the public `/events` list is still gated or absent. Once `/events` is a canonical public list, do not keep describing events as a remaining migration blocker.
- `resources`, `introduction-deck`, `glossary`, and `manuals` count as migrated once they have real public canonical list/detail routes; do not keep describing them as preview/redirect families after rollout.
- When latest `main` changes do not alter migration status, it is acceptable to update only the baseline timestamp/SHA and any directly affected inventories/counts.
- From the migration-status perspective, `services` and `company` stay open blockers as long as their public routes are still redirect-backed and only `/t/*` local previews exist.
- Treat `legal` as `scope decision needed` unless the user explicitly decides those pages must be fully localized and locally replaced.
- When counting preview-only `/t/*` surfaces, include newly added preview migration pages such as `/t/cookie-preference`, but do not let their existence by itself inflate the list of migration blockers unless they correspond to still-unmigrated public site surfaces.
- Some live `querypie.com/ja` URLs are app-level section routes rather than standalone authored pages. Example: `/ja/key-values` is the AIP value-card section and can be classified as covered when the local AIP public page already includes the same section; see `references/key-values-aip-section-classification.md`.
- When a latest-main update changes legacy redirect endpoints from upstream `querypie.com/ja` targets to local canonical routes, treat that as a migration-readiness status change, not just a redirect cleanup. Example: if `src/app/services/aip/route.ts` and `src/app/platform/ai/aihub/route.ts` now redirect to `/platforms/aip`, update `Website-Migration-Plan-ko` to show 0 upstream public replacement blockers and move remaining concerns to indexing/long-tail compatibility follow-up.

## Recommended wording patterns

Use migrated-state wording like:
- `migrated`
- `local public list + local detail family`
- `public canonical route`

Use incomplete-state wording like:
- `not yet migrated`
- `public route still redirects`
- `only preview /t/* page exists`
- `scope decision needed`

Avoid wording like:
- `content too thin`
- `needs cleanup` for intentional policy states
- `should revisit hidden/redirect/gated` unless the user asked to revisit that policy

## Verification checklist

- Baseline SHA matches latest `origin/main`
- The page does not list intentional blog/whitepaper hidden/redirect/gated states as remaining migration work
- The page does not list corpus-size complaints as remaining migration work
- Remaining blockers are limited to real public-surface replacement gaps
- Remote wiki file matches the committed result
