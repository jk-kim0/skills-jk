---
name: corp-web-v2-stage-content-e2e-wiki-report
description: Validate migrated corp-web-v2 content directly on stage-v2.querypie.com by content type, then publish a GitHub wiki E2E report with pass/fail findings and follow-up gaps.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-v2, stage, e2e, wiki, qa, migration]
    related_skills:
      - dogfood
      - github-wiki-update-from-main
      - writing-plans
---

# corp-web-v2 stage content E2E wiki report

Use this when the user asks to verify whether migrated content is actually working on `https://stage-v2.querypie.com/` and to document the result in the repo wiki.

## Goal

Produce a wiki page that is not just a code audit, but a live stage-site verification report.
The report should answer: “Which migrated content families actually render on stage right now, and which still fail or look incomplete?”

## When to use

- User explicitly wants validation by visiting the live stage site
- User wants migration status summarized by content type
- User wants the result recorded as a wiki document
- User wants evidence that stage reflects `main` HEAD behavior

## Required inputs / assumptions

- Product repo available locally, typically `~/workspace/corp-web-v2`
- Wiki repo available or clonable as `<repo>.wiki.git`
- Stage URL: `https://stage-v2.querypie.com/`
- Comparison-table wiki pages exist and can be used to choose representative migrated content samples

## Core workflow

### 1. Load the right context first

Always load:
- `dogfood`
- `github-wiki-update-from-main`
- any migration inventory / comparison-table pages relevant to the requested families

Minimum repo/source checks:

```bash
cd ~/workspace/corp-web-v2
git fetch origin main
echo MAIN_SHA=$(git rev-parse origin/main)
git log --oneline -1 origin/main
```

Also check wiki state before writing:

```bash
cd /tmp/corp-web-v2.wiki
git status -sb
git log --oneline -1
```

Record the exact `origin/main` SHA in the report header.

### 2. Select validation samples by content type

Do not browse stage randomly.
Choose sample URLs using the migration comparison tables and current route conventions.

Recommended minimum families:
- Home
- one static company/corporate page
- Documentation list
- Documentation detail
- Demo list
- Demo detail by subtype if relevant (`acp`, `aip`, `use-case`, `webinar`)
- Blog detail
- White Paper detail
- Legal versioned document
- Community License form if present in current public site

Also include at least a few legacy-to-canonical checks when routes were changed.
Examples:
- legacy demo path -> short canonical route
- old documentation-family blog/white-paper path -> current canonical path

Important:
- If comparison tables imply a route family exists but stage returns 404, document that directly.
- For corp-web-v2 demo migration, verify each subtype separately; do not generalize from ACP to AIP/use-case/webinar.

### 3. Validate on the live stage site with browser tools

For each chosen URL:
1. `browser_navigate(url)`
2. Inspect page state with `browser_console(expression=...)`
3. Check console/runtime errors with `browser_console(clear=true)` after navigation
4. Use `browser_vision(...)` when visual quality or 404 confirmation matters

Minimum checks per page:
- Did the page load?
- Is it a branded 404 page?
- Is there an H1 or clear page identity?
- Is the main content actually present?
- Are there immediate console errors?

Useful expression pattern:

```js
(() => ({
  url: location.href,
  title: document.title,
  h1: [...document.querySelectorAll('h1')].map(e => e.textContent.trim()),
  notFound: /404|not found/i.test(document.body.innerText),
  text: document.querySelector('main')?.innerText?.slice(0, 500) || null
}))()
```

### 4. Pay attention to quality issues, not only route existence

A page can “load” but still fail the migration-quality bar.
Document issues such as:
- obvious test data in public lists
- placeholder or blank-looking thumbnails
- visually broken cards
- missing embeds or obviously incomplete content
- runtime exceptions even when the page appears usable

For suspicious visual cases, use `browser_vision` to confirm whether the issue is actually visible.

### 5. Classify results clearly

Use a simple triage:
- `통과` — route loads and content appears correct enough for the sampled check
- `조건부 통과` — route loads but quality/runtime issues need follow-up
- `실패` — route is 404, empty, or clearly broken

Recommended summary table columns:
- 유형
- 샘플 URL
- 결과
- 관찰 내용

Also add a separate table for legacy path / canonical path checks.

### 6. Write the wiki report as an E2E evidence document

Recommended title pattern:
- `stage-v2 콘텐츠 E2E 검증 보고서`

Recommended sections:
1. title
2. last updated + verification timestamp
3. source SHAs + stage URL
4. related wiki pages
5. document purpose
6. validation method
7. executive summary
8. type-by-type results table
9. legacy/canonical path checks
10. key observations
11. directly tested URL list
12. prioritized follow-up actions
13. conclusion

Important framing:
- explicitly state that this is live-stage verification, not just code inspection
- distinguish “main reflects ACP only” versus “full target migration state” when stage behavior proves that gap

### 7. Update Home when the report should be discoverable

If the report is a meaningful new reference page, add it to `Home.md` under a section such as:
- `검증 / E2E`

Also add it to the recommended reading order near the main migration plan.

### 8. Publish with normal wiki concurrency handling

Commit and push the wiki change.
If push is rejected because remote wiki changed first, treat it as normal concurrency:

```bash
git fetch origin master
git log --oneline origin/master..HEAD
git log --oneline HEAD..origin/master
git pull --rebase origin master
git push origin master
```

Repeat until push succeeds.
Then verify local HEAD equals `origin/master`.

## Reporting guidance specific to corp-web-v2

### Demo-family lesson

When checking Demo migration status on stage:
- verify `acp`, `aip`, `use-cases`, and `webinars` independently
- do not assume all short canonical routes are live just because one subtype works
- use the currently intended canonical patterns when sampling:
  - `/demo/acp/:id/:slug`
  - `/demo/aip/:id/:slug`
  - `/demo/use-cases/:id/:slug`
  - `/webinars/:id/:slug`
- if only ACP works on stage, say exactly that

If `aip` / `use-cases` / `webinars` return 404 on stage, do one more root-cause pass before concluding it is a deployment bug:
1. fetch latest `origin/main`
2. inspect `origin/main` directly with `git ls-tree` / `git cat-file -e` to confirm whether the relevant route files, demo catalog, and MDX source files actually exist on `main`
3. compare against any open migration PR branch (for example `origin/feat/demo-mdx-migration-all`) to see whether the missing implementation is still only on the PR branch
4. check current public helpers such as `src/features/content/data.ts` and `src/app/sitemap.ts` to see whether demo URLs are still generated from legacy `/features/demo/:slug` flows on `main`

Important lesson from use:
- stage can correctly reflect `main` even when the wiki/planning docs or open PR already describe a broader target state
- for this repo, `ACP` short-route support was merged first, while `AIP` / `use-cases` / `webinars` remained on open PR `#41 feat/demo-mdx-migration-all`; in that situation, stage 404 is expected and should be reported as `main 미반영`, not as an unexplained deployment failure

### Post-merge expectation checklist lesson

When the user asks "after this PR merges, which URLs should be alive on stage?", do not guess from earlier docs or from ad hoc route naming.
Use the migration PR branch itself as the authoritative future-state source.

Recommended method:
1. inspect the PR branch route files directly with `git show` / `git cat-file -e`
2. use the shared demo catalog implementation as the canonical URL source, not a wiki table or earlier assistant memory
3. extract the pathname rules from the catalog helper (for example `getDemoMdxPathname()` in `src/features/demo/catalog.ts`)
4. record category counts from the catalog so the checklist distinguishes route-family smoke tests from full expected totals
5. note locale expectations from the catalog visibility fields instead of assuming all entries have `en,ko,ja`

For `feat/demo-mdx-migration-all`, this produced the reliable checklist basis:
- canonical route families:
  - AIP: `/demo/aip/:id/:slug`
  - Use Cases: `/demo/use-cases/:id/:slug`
  - Webinars: `/webinars/:id/:slug`
- category totals on the PR branch:
  - AIP: `1`
  - Use Cases: `29`
  - Webinars: `26`
- sample locale nuance:
  - AIP `1/google-oauth-demo` had `en,ja`
  - many Use Cases / Webinars had `en,ko,ja`

Important reporting rule:
- explicitly correct earlier trial URLs if they were only exploratory and not canonical
- in this repo, `/demo/use-case/...` and `/demo/webinar/...` were exploratory checks during E2E, but the PR-implemented canonical paths were `/demo/use-cases/...` and `/webinars/...`
- when handing the user a smoke-test checklist, separate:
  - P0 direct-open URLs that must stop 404ing after merge
  - list/homepage/sitemap integration checks that should also reflect the new canonical routes

### Documentation-family lesson

For `/features/documentation`, inspect both route health and visible content quality.
A page can technically render while still exposing:
- stray test cards
- placeholder thumbnails
- mixed-quality public content

Those should be reported as `조건부 통과`, not silently counted as success.

### Legal-family lesson

For legal pages, validate both rendering and console state.
If localized content renders correctly but console captures runtime exceptions, record it as `조건부 통과` with a note that the issue may be non-user-visible but still needs follow-up.

## Pitfalls

- Treating code migration as equivalent to live stage readiness
- Sampling only one demo subtype and generalizing the result
- Checking only route existence without inspecting visible content quality
- Forgetting console checks after each navigation
- Forgetting to add the report to `Home.md`
- Assuming wiki push rejection means the content is wrong; often it is just a concurrent edit race

## Minimal checklist

- fetch latest `origin/main`
- record `origin/main` SHA
- read relevant migration comparison tables
- choose representative sample URLs by family
- visit each sample on live stage
- capture pass/conditional/fail result with notes
- verify a few legacy/canonical mappings
- write a new wiki report page
- link it from `Home.md`
- commit, rebase if needed, push, verify remote
