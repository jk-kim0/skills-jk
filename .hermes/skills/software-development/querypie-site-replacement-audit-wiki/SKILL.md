---
name: querypie-site-replacement-audit-wiki
description: Audit whether corp-web-v2 can replace the current querypie.com site, using latest main from corp-web-v2/corp-web-app/corp-web-contents plus Vercel logs, Google Search Console, and GA4, then publish the findings to the corp-web-v2 GitHub wiki.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [querypie, corp-web-v2, corp-web-app, corp-web-contents, migration, wiki, vercel, gsc, ga4]
    related_skills: [github-wiki-update-from-main, vercel-runtime-log-audit]
---

# QueryPie site replacement audit wiki

Use this when the user asks for a wiki document analyzing what is still required for `corp-web-v2` to replace the current `querypie.com` website implemented by `corp-web-app` + `corp-web-contents`.

This skill is specifically for:
- replacement-readiness audits
- full migration scope / priority docs
- 404-prevention redirect-rule docs
- route/content/function inventory docs

## Core framing

Default migration framing for this repo family:
1. `corp-web-v2` should replace the whole `querypie.com` public site
2. the two strategic improvements are:
   - consolidating the split repo architecture into one app/repo
   - applying the design renewal
3. outside those two improvements, pages and user-facing functions should default to **migrate**, not **drop**
4. exclusions should be placed in a review-needed bucket for user decision, not silently removed

## Inputs / sources of truth

Always use these sources together:
- latest `origin/main` of `querypie/corp-web-v2`
- latest `main` of `querypie/corp-web-app`
- latest `main` of `querypie/corp-web-contents`
- current operational evidence:
  - Vercel logs
  - Google Search Console
  - GA4

Do not base the wiki on stale local state.

## Required workflow

### 1. Refresh latest main and wiki context

Inside `corp-web-v2`:

```bash
git fetch origin main
git rev-parse FETCH_HEAD
git log --oneline -1 FETCH_HEAD
env -u GITHUB_TOKEN gh repo view querypie/corp-web-v2 --json nameWithOwner,defaultBranchRef,url,hasWikiEnabled,isPrivate
```

Clone or refresh the wiki repo:

```bash
git clone git@github.com:querypie/corp-web-v2.wiki.git /tmp/corp-web-v2.wiki
# or if already present
cd /tmp/corp-web-v2.wiki && git fetch origin master
```

List existing wiki pages before deciding whether to create a new page or update one.

### 2. Get legacy repo heads

Use GitHub CLI to record authoritative SHAs:

```bash
env -u GITHUB_TOKEN gh api repos/querypie/corp-web-app/commits/main --jq '.sha'
env -u GITHUB_TOKEN gh api repos/querypie/corp-web-contents/commits/main --jq '.sha'
```

If `corp-web-app` needs local file inspection, a shallow clone to `/tmp` is acceptable:

```bash
env -u GITHUB_TOKEN gh repo clone querypie/corp-web-app /tmp/corp-web-app -- --depth 1
```

For `corp-web-contents`, prefer GitHub API tree listing over a full clone when possible.

### 3. Inventory legacy content families from `corp-web-contents`

Use the recursive git tree API:

```bash
env -u GITHUB_TOKEN gh api repos/querypie/corp-web-contents/git/trees/main?recursive=1 --jq '.tree[].path'
```

Key patterns to inventory:
- `pages/company/**/content.mdx`
- `pages/features/demo/**/content.mdx`
- `pages/features/documentation/**/content.mdx`
- `pages/features/documentation/blog/**/content.mdx`
- `pages/features/documentation/white-paper/**/content.mdx`
- `pages/solutions/**/content.mdx`
- `pages/search/**/content.mdx`
- `pages/querypie/license/community/apply/**/content.mdx`

Important insight from use:
- treat `solutions/*` and `search` as real migration scope, not optional extras
- count distinct content-entry directories, not raw locale files, when comparing parity

### 4. Inventory legacy app shell from `corp-web-app`

Inspect page and route handlers under:

```bash
/tmp/corp-web-app/src/app
```

Collect:
- `page.tsx` routes
- `route.ts` handlers
- notable public utility surfaces like:
  - `api/search`
  - `chat/publication/[[...path]]`
  - `docs/*`
  - `wiki/*`
  - `public/[...pathname]`
  - `sitemap.xml`

Also inspect `package.json` for feature/integration signals such as:
- GA / analytics
- Hotjar
- Vercel Blob
- Google APIs
- rrweb

### 5. Inventory current `corp-web-v2` latest-main route surface

Do not trust a dirty working tree.
Use a clean archive snapshot of `origin/main`:

```bash
tmpdir=$(mktemp -d)
git -C ~/workspace/corp-web-v2 archive --format=tar origin/main | tar -xf - -C "$tmpdir"
```

Inspect public routes in:

```bash
$tmpdir/src/app/[locale]
```

Key check:
- if `src/constants/navigation.ts` still points Solutions to `aip-not-found`, `acp-not-found`, or `fdes-not-found`, treat Solutions as a top-tier blocker

### 6. Collect operational evidence

#### Google Search Console

Use the local QueryPie CLI in `skills-jk`:

```bash
~/workspace/skills-jk/bin/gsc sites
~/workspace/skills-jk/bin/gsc query "https://www.querypie.com/" --by-date --days 90
~/workspace/skills-jk/bin/gsc query "https://www.querypie.com/" --by-country --days 90
~/workspace/skills-jk/bin/gsc query "https://www.querypie.com/" --by-device --days 90
~/workspace/skills-jk/bin/gsc pages "https://www.querypie.com/" --days 90 --limit 30
```

Important findings to preserve in docs:
- top landing pages often include `/solutions/*`, `/api-docs.html`, and many `/chat/publication/*` URLs
- historical entry points are part of migration scope because they still drive search clicks

#### Google Analytics GA4

Use the local QueryPie GA CLI in `skills-jk`:

```bash
~/workspace/skills-jk/bin/ga accounts
~/workspace/skills-jk/bin/ga report 451239708 --days 90
~/workspace/skills-jk/bin/ga sources 451239708 --days 90
```

Property observed during use:
- `QueryPie Homepage` property ID: `451239708`

Important insight:
- direct + organic are major traffic sources
- LLM referrals like ChatGPT / Gemini / Claude / Perplexity can appear and should not be broken by weak redirects

#### Vercel runtime logs

Check both:
- `corp-web-v2` production
- legacy `corp-web-app` production

Useful commands:

```bash
vercel logs --project corp-web-v2 --environment production --since 24h --json --no-branch --limit 20
vercel logs --project corp-web-v2 --environment production --since 24h --search 'status:404' --json --no-branch --limit 100
vercel logs --project corp-web-v2 --environment production --since 24h --level error --json --no-branch --limit 100

vercel logs --project corp-web-app --environment production --since 24h --json --no-branch --limit 20
vercel logs --project corp-web-app --environment production --since 24h --search 'status:404' --json --no-branch --limit 120
vercel logs --project corp-web-app --environment production --since 24h --level error --json --no-branch --limit 100
```

Important experiential findings:
- `corp-web-v2` production may show only light/static traffic if it is not yet the main public workload
- legacy `corp-web-app` production logs are often the true center of gravity for current user traffic and 404 evidence
- use sampled 404 families to drive redirect-rule docs

### 7. Recommended wiki page set

Good page breakdown:
1. `corp-web-v2 Replacement Readiness Audit`
2. `404 Prevention Redirect Rules`
3. `querypie.com Full Migration Scope and Priorities`
4. `querypie.com Migration Inventory and Execution Plan`
5. optionally later: `querypie.com Page and Function Inventory`

### 8. Recommended migration buckets

Use these buckets consistently:
- `P0 Must migrate`
- `P1 Strongly recommended`
- `P2 Review needed`
- `P3 Likely excludable, pending review`

Important lesson from this task:
- when the user says whole-site replacement is the goal, Solutions, Search, permalink continuity, and tracking parity all move into `P0` or near-`P0`
- do not frame unmigrated legacy families as optional unless the user explicitly agrees

## Documentation guidance

### Language and wiki-hub rules for `corp-web-v2`

For `corp-web-v2` wiki planning/audit work, default to Korean unless the user explicitly asks otherwise.

Also treat `Home.md` as an active navigation hub, not a static landing page.
When you add or materially reorganize migration-analysis pages:
- update `Home.md` with a Korean reading guide
- explicitly say which page should be read first
- summarize the role of each major page
- keep the current progress / next-step section visible from Home

Important lesson from use:
- users reviewing long-running migration analysis want to understand the document set from the wiki Home alone
- the most useful Home structure is: language rule -> what to read first -> recommended reading order -> page purpose summary -> current progress

### Stage-update rule

When the user asks for ongoing analysis/planning, do not publish a single final document and stop.
At each major stage completion, update the relevant planning page(s) and refresh progress status.

Recommended pattern:
- maintain a `진행 상태` / progress section in the main migration-plan page
- after creating a new major page, update the main plan page to mention what just completed and what the next major step is
- if the reading order changes, update `Home.md` too

This is especially important when the user wants to track progress and review incrementally from the wiki.

### Overlap-consolidation rule for wiki planning docs

When the user says multiple migration/readiness wiki pages are overlapping, duplicated, or stale, do not just refresh each page independently.
Instead, prefer a deliberate consolidation pass:

1. choose one page as the canonical plan page
2. merge the overlapping scope/readiness/execution content into that page
3. reorganize the canonical page around the user's requested axes
   - for example `콘텐츠 관점` vs `기능 관점`
4. convert the superseded pages into short reference/stub pages that:
   - state they were consolidated
   - link to the canonical page first
   - preserve minimal historical context instead of deleting everything silently
5. update `Home.md` so the new reading order points to the canonical page first

Recommended default for `corp-web-v2` migration docs:
- use the execution-plan style page as the canonical hub when it can absorb both readiness and scope content
- keep redirect rules and detailed comparison tables as separate supporting pages
- explicitly distinguish between:
  - latest merged `origin/main` implementation state
  - comparison-table or draft-PR planning state that may be ahead of main

Why this matters:
- otherwise three pages drift and repeat the same conclusions with different commit SHAs
- users reviewing the wiki want one current source of truth, not parallel summaries
- preserving the old pages as short stubs keeps existing links useful while making the new canonical reading path obvious

### Content-comparison table split rule

When a content migration comparison page becomes too large, keep one hub page and split large content families into dedicated wiki pages instead of leaving one huge table.

Recommended pattern:
- keep `querypie-com-Content-Migration-Comparison-Table` as the hub document
- leave summary counts and links in the hub page for split-out families
- create separate detail pages for review-heavy families such as Demo, Blog, White Paper, and Legal
- put a short `집계 요약` section at the top of every split page
- keep the same 4 table columns the user requested unless they explicitly ask to change them

Recommended split-page structure:
1. title
2. `최종 업데이트`
3. `원본 기준 문서`
4. `집계 요약`
5. `문서 목적`
6. the extracted table section

Important implementation lesson:
- compute counts from actual table rows only; exclude the markdown header/separator rows when summarizing
- after splitting, re-read both the new page and the hub page to verify that no header rows were duplicated and that the summary counts stayed correct
- when adding another family later (for example Legal after Demo/Blog/White Paper), follow the same hub-plus-summary pattern instead of redesigning the structure

### Replacement-readiness audit page should include
- the three source-of-truth SHAs
- current vs target architecture explanation
- codebase comparison findings
- operational evidence from GSC/GA/Vercel
- explicit conclusion: ready or not yet
- blocker list

### 404 redirect rules page should include
- rule precedence
- status-code guidance (`308`, `307`, `410`, keep `404`)
- family rules for:
  - whitepaper
  - resources/learn
  - blog
  - chat/publication
  - news/company aliases
  - product/platform/security aliases
- explicit no-redirect rules for scanner/probe traffic

### Full migration scope/priorities page should include
- the user’s framing verbatim in spirit:
  - full querypie.com migration first
  - repo consolidation and design renewal as strategic improvements
  - exclusions only after review
- P0/P1/P2/P3 categorization

### Migration inventory/execution plan page should include
- legacy family counts
- current v2 route surface
- traffic/404 evidence that affects scope
- phased execution plan (inventory -> parity -> functional parity -> editorial maturity -> review)

## Pitfalls

- treating Solutions as optional when nav still advertises them
- ignoring Search because it is only one route family
- writing docs from local dirty files instead of latest main snapshots
- assuming blog/whitepaper route families are “done” just because v2 has route shells; permalink continuity still matters
- redirecting scanner/probe garbage to the homepage
- underweighting `/chat/publication/*` because they are not classic marketing pages; they can be top search landing pages

## Verification

After writing each wiki page:

```bash
cd /tmp/corp-web-v2.wiki
git add <page>.md
git commit -m "<message>"
git push origin master
git fetch origin master
git rev-parse HEAD origin/master
git show origin/master:<page>.md | sed -n '1,40p'
```

Report back to the user with:
- wiki page URL
- source-of-truth SHAs used
- wiki commit SHA
- concise summary of the planning conclusion
