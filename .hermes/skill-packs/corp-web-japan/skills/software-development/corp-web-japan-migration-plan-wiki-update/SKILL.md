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
7. rewrite the wiki page so conclusions reflect the new state
8. update all timestamp references consistently, not just the baseline header
9. commit/push in the separate `.wiki.git` repo

## Specific corp-web-japan heuristics

### 2026-05-17 latest-main baseline lesson (`ec651e16a2ea65978023bc415645ebedbc65a479`)

When refreshing `Website-Migration-Plan*` from latest main at or after this baseline, do not preserve older May 8/May 13 conclusions mechanically:

- Company and legal are no longer redirect-only:
  - `src/app/about-us/page.tsx` and `src/app/certifications/page.tsx` are public local pages.
  - `src/app/cookie-preference/page.tsx`, `src/app/eula/page.tsx`, `src/app/privacy-policy/page.tsx`, `src/app/privacy-policy/[slug]/page.tsx`, and `src/app/terms-of-service/page.tsx` are public local pages.
- Platform/service status changed substantially:
  - `/platforms/aip`, `/platforms/aip/integrations`, `/platforms/aip/usage-based-llm`, `/platforms/aip/mcp-gateway`, `/platforms/acp`, `/platforms/acp/integrations`, and `/services/fde` are public local pages.
  - `/services/acp`, `/platform/ai/aip`, `/platform/ai/aip/fde-services`, `/platform/ai/aip/usage-based-llm`, and `/platform/ai/aip/mcp-gateway` redirect locally to canonical routes.
  - `/services/aip` and `/platform/ai/aihub` still redirect upstream and should be recorded as alias-policy / remaining upstream dependencies.
  - `/platform/security/{database-access-controller,kubernetes-access-controller,system-access-controller,web-access-controller}` still redirect upstream while matching `/t/platforms/acp/*` preview pages exist; these are the main remaining ACP child public-rollout candidates.
- Preview `/t/*` scope is now narrow:
  - Remaining preview/local-only entrypoints are `/t/platforms/acp/*` four child pages plus `/t/plans`, `/t/plans/aip`, and `/t/plans/acp`.
  - Do not keep `/t/about-us`, `/t/certifications`, `/t/services/*`, `/t/platforms/aip`, or `/t/platforms/acp` as current remaining previews if latest main still matches this baseline.
- Readiness counts used in the refreshed May 17 migration-plan pages were:
  - 28 major public local entrypoints
  - 6 public routes still redirecting upstream
  - 7 remaining `/t/*` preview/local-only entrypoints
  - 11 local/public detail-route families, including `/privacy-policy/:slug`
- Keep intentional hidden/redirect/gated publication records out of remaining-blocker lists unless the user explicitly asks to revisit those policies.

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

### Latest-main audit lessons from 2026-05-17 night baseline

When updating `Website-Migration-Plan*`, re-check these routes before preserving older blocker wording:

- ACP child pages
  - If latest main has `src/app/platforms/acp/{database-access-controller,kubernetes-access-controller,system-access-controller,web-access-controller}/page.tsx`, classify those ACP child pages as `migrated`, not `partial`.
  - If `src/app/platform/security/*/route.ts` redirects to `/platforms/acp/*`, treat those legacy `/platform/security/*` paths as local compatibility redirects, not upstream replacement blockers.
  - If those `/platforms/acp/*` routes are present in `src/app/sitemap.ts`, mention that sitemap/indexing has been aligned for the ACP child pages.
- Plans / pricing
  - If latest main has `src/app/plans/page.tsx`, `src/app/plans/aip/page.tsx`, and `src/app/plans/acp/page.tsx`, classify plans/pricing as `migrated`, not `preview only` or `scope decision needed`.
  - If `src/app/pricing/route.ts` redirects to `/plans`, document `/pricing` as a local compatibility redirect.
  - Keep `src/app/pricing/calculator/page.tsx` calling `notFound()` as a helper/non-implementation unless a real public calculator is added.
- `/t/*` backlog
  - Do not leave `/t/platforms/acp/*` or `/t/plans/*` in the remaining preview/local-only migration backlog after they are promoted to public routes.
  - In the 2026-05-17 night baseline, the remaining `/t/*` migration entrypoint count became `0`.
- Remaining blockers
  - On that baseline, the main upstream public replacement gaps narrowed to `/services/aip` and `/platform/ai/aihub`.
  - Keep `key-values` as a scope decision, not a migration blocker, unless latest main adds a required local/public page or the user changes the scope.

## Latest-main audit lessons from 2026-05-18 baseline

When updating `Website-Migration-Plan*` after commit `558a679ab8e22be5e07d6ee8d75e3b975e1a4235`, remove older blocker/follow-up wording that no longer applies:

- AIP legacy/service aliases
  - `src/app/services/aip/route.ts`, `src/app/platform/ai/aihub/route.ts`, and `src/app/platform/ai/aip/route.ts` all redirect to local `/platforms/aip`.
  - Do not keep `/services/aip`, `/platform/ai/aihub`, or `/platform/ai/aip` as upstream public replacement blockers.
- Company legacy aliases
  - `src/app/company/route.ts` redirects `/company` to local `/about-us`.
  - `src/app/company/news/route.ts` redirects `/company/news` to local `/news`.
  - `/ja/company/news` also redirects locally to `/news`; treat this as local replacement behavior, not upstream dependency.
- Legal sitemap/indexing
  - `src/app/sitemap.ts` explicitly documents `/privacy-policy` and `/terms-of-service` as public local legal pages that are intentionally noindex and omitted from the sitemap.
  - Do not leave “confirm sitemap/indexing policy” as a remaining migration follow-up for those two routes on this baseline.
- Remaining blockers
  - Major upstream public replacement blockers should be `0` unless a newer main reintroduces one.
  - `key-values` should be documented as covered by the value section on `/platforms/aip`; preserving the exact `/key-values` URL is an optional long-tail route-policy decision, not a migration blocker.
- Translation/sidebar hygiene
  - Keep `Website-Migration-Plan`, `Website-Migration-Plan-ko`, and `Website-Migration-Plan-ja` synchronized on the same baseline SHA and conclusions.
  - If adding or renaming a language variant, update `_Sidebar.md` in the same wiki commit.

### Latest-main audit lessons from 2026-05-18 baseline

When refreshing `Website-Migration-Plan*` after PRs around legacy redirects and legal sitemap policy, do not preserve older blocker/follow-up wording without checking these latest-main facts:

- Legacy content redirects
  - If `src/app/services/aip/route.ts`, `src/app/platform/ai/aihub/route.ts`, and `src/app/platform/ai/aip/route.ts` redirect to `/platforms/aip`, classify AIP legacy/service aliases as local compatibility redirects, not upstream blockers.
  - If `src/app/company/route.ts` redirects to `/about-us` and `src/app/company/news/route.ts` redirects to `/news`, document company legacy paths as local replacement redirects.
  - If `src/app/ja/[[...path]]/route.ts` special-cases `/ja/company/news` to `/news`, include that only as local redirect evidence; do not reclassify the whole `/ja/**` catchall as migrated.
  - If `src/app/api-docs.html/route.ts` redirects to `https://docs.querypie.com/ja/api-reference`, treat it as the real external replacement target for that legacy API docs path.
- Legal / sitemap policy
  - If `src/app/sitemap.ts` explicitly comments that `/privacy-policy` and `/terms-of-service` are public local legal pages but intentionally noindex and omitted from sitemap, remove older “sitemap/indexing policy needs confirmation” follow-up language.
  - Classify legal/policy pages as `migrated` with intentional noindex/sitemap exclusion, not as `Done / follow-up`, unless latest code changes the policy again.
- Remaining blockers
  - With the AIP aliases local and legal sitemap policy explicit, the major public replacement blocker count should be `0`.
  - Keep `key-values` as `covered` by the `/platforms/aip` value-card section when latest AIP page contains the same section content; only the exact `/key-values` endpoint is an optional long-tail route-policy decision.
- Translation sync
  - Update `Website-Migration-Plan-ko.md`, `Website-Migration-Plan.md`, and `Website-Migration-Plan-ja.md` from the same baseline and conclusion set in one wiki commit.
  - After editing, grep the three files for stale baseline SHAs and stale phrases such as older upstream blocker claims, “sitemap/indexing policy confirmation,” `mostly migrated`, or `scope decision needed`.

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
