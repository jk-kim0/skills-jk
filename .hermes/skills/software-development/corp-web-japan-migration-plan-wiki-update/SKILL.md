---
name: corp-web-japan-migration-plan-wiki-update
description: Update corp-web-japan Website-Migration-Plan wiki pages from latest origin/main using a strict migration-completeness lens, not content-richness or generic cleanup heuristics.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, wiki, migration, documentation, latest-main]
    related_skills: [github-wiki-editing, github-wiki-update-from-main, corp-web-japan-origin-main-worktree-safety]
---

# corp-web-japan migration-plan wiki update

Use this when updating these wiki pages:
- `Website-Migration-Plan-ko`
- `Website-Migration-Plan-ja`
- `Website-Migration-Plan`

## Core rule

Evaluate only this question:
- Has the existing `https://www.querypie.com/ja` public content/functionality been fully migrated and replaced locally in `corp-web-japan`?

Do **not** drift into:
- content richness / corpus size / “too few items” arguments
- generic cleanup ideas for intentional hidden/redirect/gated records
- speculative product-quality or editorial completeness concerns

This is a migration/replacement audit, not a content-strategy review.

## Required lens

Classify each surface by whether the old site is functionally replaced:
- `migrated`
- `partial`
- `not yet migrated`
- `scope decision needed`

Good examples:
- public canonical local route exists and replaces old surface -> `migrated`
- detail routes exist but list surface is still gated -> `partial`
- public route still redirects to old site while preview/local page exists elsewhere -> `not yet migrated`
- legal/policy pages where the team has not decided whether local replacement is required -> `scope decision needed`

## What NOT to list as remaining work

Unless the user explicitly asks to revisit these policies, do not surface them as migration gaps:
- intentional blog/whitepaper hidden records
- intentional redirect records
- intentional gated whitepaper behavior
- small corpus size, e.g. only one AIP demo item
- generic “cleanup” of already-migrated families

Those may be valid product/content follow-ups, but they are not migration blockers.

## Latest-main workflow

1. `git fetch origin main`
2. record `FETCH_HEAD` / `origin/main` SHA
3. inspect the current wiki page
4. diff the old recorded SHA in the wiki page against latest `origin/main` when possible
5. inspect latest-main route files directly with `git show FETCH_HEAD:path`
6. inspect latest-main content counts / route existence
7. decide whether latest-main changes actually alter migration-completeness conclusions
8. if conclusions changed, rewrite the affected sections so the narrative matches the new state
9. if conclusions did not change, do a baseline-only refresh: update the recorded snapshot time, SHA, and every duplicated timestamp reference in the page, but keep the migration-status conclusions intact
10. commit/push in the separate `.wiki.git` repo

### Baseline-only refresh rule

A large share of later `origin/main` changes are CI, refactor, or implementation-detail changes that do not materially change the migration-completeness judgment.

In that case:
- do not invent new blockers or cleanup items just because main moved
- do not rewrite the status dashboard unnecessarily
- do update every repeated timestamp/string that claims the page is based on a particular latest-main moment

At minimum re-check and update consistently:
- baseline snapshot line
- baseline SHA line
- summary lead timestamp
- dashboard header timestamp
- any final interpretation / conclusion section that restates the audit timestamp

## Specific corp-web-japan heuristics

### Repo-context trap during wiki work
Once you `cd` into the wiki clone, relative file reads/searches can accidentally hit the wiki repo instead of the product repo.
For product inspection during wiki updates, prefer:
- product-repo `workdir` on terminal commands
- `git show FETCH_HEAD:path/to/file`
- absolute product-repo paths when using file tools

### Count local public entrypoints
Count only real public local surfaces that replace old public pages.
Do not count preview `/t/*` routes as migrated public entrypoints.

### Redirect-backed surfaces
If a public route still redirects to `querypie.com/ja`, treat that family as not fully migrated even if a preview/local page exists elsewhere.

### Events
If `/events` list still requires a gate or returns `notFound()` without a query flag, treat events as `partial` even if detail pages and corpus exist.
If `/events` becomes the public canonical list route and preview `/t/events` is removed, reclassify events as `migrated` and remove events from the remaining-blocker section.

### Resources / intro deck / glossary / manuals
If public canonical routes exist directly at `/resources`, `/introduction-deck`, `/glossary`, `/manuals`, count them as migrated public surfaces. Do not keep calling them preview-only once those routes are on main.

### News
If local news detail pages are in sitemap and indexed, record that as a latest-main fact. But do not automatically turn that into a “remaining task” unless the user asks for policy review.

## Recommended output structure

- Purpose
- Baseline snapshot + SHA
- Executive summary / 핵심 결론
- Readiness counts
- What changed since previous baseline
- Dashboard table
- Family-by-family detail
- Remaining migration blockers only
- Evidence files checked

## Practical wording guardrails

Prefer wording like:
- “not yet migrated” for redirect-backed public surfaces
- “partial” for gated or otherwise incomplete replacements
- “migrated” for already-replaced local canonical surfaces
- “scope decision needed” for legal/policy areas

Avoid wording like:
- “content is too thin”
- “needs cleanup” when the state is intentional
- “should probably revisit” unless the user explicitly asked for policy review

## Best-effort checklist

Before finishing:
- baseline SHA updated
- counts updated
- conclusions updated, not just evidence
- no corpus-richness concerns listed as migration blockers
- no intentional hidden/redirect/gated policy surfaced as generic remaining work
- pushed to wiki remote and verified via `git show origin/master:<page>.md`
