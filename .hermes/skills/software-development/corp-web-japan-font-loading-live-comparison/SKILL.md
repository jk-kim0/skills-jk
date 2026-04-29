---
name: corp-web-japan-font-loading-live-comparison
description: Compare live font loading behavior between corp-web-japan production and stage pages, avoid redirect-target mistakes, run repeated browser trials, and verify whether a font optimization PR is actually deployed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, fonts, performance, browser, stage, production, github, issue-writing]
    related_skills: [systematic-debugging, github-issues, github-pr-workflow, corp-web-japan-font-stack-regression-debugging]
---

# corp-web-japan font loading live comparison

Use this when the user reports that custom fonts feel faster/slower between `www.querypie.com/ja/...` and `stage.querypie.ai`, or asks for a live browser-based comparison and a documented GitHub issue.

## Key lesson: compare the exact requested route, not an assumed canonical host

Do **not** collapse the user's request into `querypie.ai` or another canonical host unless the exact requested URL actually redirects there.

Always start by opening the exact production URL the user named.

Example:
- `https://www.querypie.com/ja` may redirect elsewhere in some cases
- but `https://www.querypie.com/ja/solutions/aip` stayed on `www.querypie.com/ja/...`
- If you compare the wrong host, the entire conclusion can be invalid

## Proven investigation flow

### 1. Open the exact production URL and stage URL in a live browser

Use browser navigation on both targets separately.

For each page, extract via browser JS:
- final `location.href`
- `document.title`
- computed `font-family` for `body`, visible `h1`, and a visible paragraph
- `document.fonts` entries
- `link[rel="preload"][as="font"]`
- `@font-face` declarations from stylesheets
- font resource timing entries from `performance.getEntriesByType('resource')`
- navigation timing (`DOMContentLoaded`, `load`)

Recommended JS shape:
- collect only font-like resources (`.woff2`, `.woff`, `.ttf`, `.otf`)
- include `name`, `initiatorType`, `transferSize`, `encodedBodySize`, `duration`, `startTime`, `responseEnd`

### 2. Inspect HTTP headers separately from browser timing

Use terminal `requests`/`curl` checks for:
- HTML response headers
- main font asset headers

Capture at least:
- `Cache-Control`
- `Age`
- `X-Vercel-Cache`
- `ETag`
- `Last-Modified`
- `Content-Length`
- `Content-Type`

Important interpretation:
- same `Cache-Control` does **not** mean same real-world performance
- `Age` can reveal very different CDN warmth between production and stage

### 3. Do not trust a single browser run

A one-off run can be misleading.

For live production vs stage font/performance comparisons, run **at least 3 independent browser trials** before stating a directional conclusion.

Why:
- cold/warm edge state varies
- different third-party resources can skew `load`
- single-run Pretendard/Mona timings may reverse on later runs

### 4. Aggregate the numbers before concluding

Compute per-metric:
- raw per-trial table
- production mean
- stage mean
- difference (`stage - production`)
- count of trials where stage was faster

Recommended tracked metrics:
- Mona Sans duration
- JP font duration (Pretendard variable or subset file, depending on deployment state)
- `DOMContentLoaded`
- `load`

If variance is high, say so explicitly.
Do not overclaim statistical significance from just 3 runs; report the direction and the noise level.

## Important interpretation rules

### A. Same font-family and same cache headers do not prove same user experience

Even when these match:
- `font-display: swap`
- same `font-family`
- same `Cache-Control: public,max-age=31536000,immutable`

real timing can still differ because of:
- edge cache warmth (`Age`)
- different origin/browser cache separation
- different route-level assets
- different page weight / embedded content

### B. Apples-to-apples route comparison matters

A production deep detail page vs a stage homepage can create page-specific differences unrelated to environment-level font configuration.

Explicitly call this out if the compared routes are different content surfaces.

### C. Extra font preloads matter

In this investigation, `www.querypie.com/ja/solutions/aip` preloaded an extra JetBrains Mono font that was not visibly used in normal page text.

If production preloads extra fonts and stage does not, mention that as route-specific overhead.

## Verifying whether a font optimization PR is really deployed

When the user says a PR was merged and asks whether stage has it:

### 1. Confirm the PR merge and checks

Use GitHub CLI to inspect:
- merge state
- mergedAt
- merge commit
- checks/deploy status

### 2. Verify on the live stage site, not just from GitHub

Open `stage.querypie.ai` and inspect live CSS/font behavior.

For the JP subset rollout from PR #125, the proof of deployment was:
- `@font-face` rules for
  - `/fonts/PretendardJPSubset-400.woff2`
  - `/fonts/PretendardJPSubset-500.woff2`
  - `/fonts/PretendardJPSubset-600.woff2`
  - `/fonts/PretendardJPSubset-700.woff2`
- `document.fonts` showing `Pretendard JP Subset` loaded across those weights
- resource timing entries for those subset files

### 3. Check whether the live preload behavior matches the PR description

Do not assume the deployed site matches every stated PR detail.

In this case, PR #125 described preloading `PretendardJPSubset-600.woff2`, but on the live stage page we observed:
- Mona Sans preload link in HTML
- no visible subset preload link in DOM/HTML
- subset fonts loaded via CSS/resource timing instead

So the correct conclusion was:
- the core subset-font deployment was live
- but the expected `600` preload behavior was not confirmed on the live site

## Writing the GitHub issue report

When documenting results in an issue:

### Structure
1. English report first
2. Japanese translation second
3. Include numeric comparison tables
4. If a related PR exists, mention it near the conclusion/follow-up section

### Include in the issue
- exact compared URLs
- whether the production URL redirected or did not redirect
- structural findings (`font-family`, `@font-face`, preload differences, cache headers)
- 3-trial raw data table
- aggregated statistics table
- careful conclusion with caveats
- follow-up section referencing the implementation PR
- if PR not yet measured on live stage, say that follow-up measurement is still needed

### Good wording pattern for PR follow-up
- state that PR `<number>` was created to address the issue
- summarize the optimization approach
- state expected effect
- clearly say the report should be updated after post-deploy remeasurement

## Done criteria

- exact requested production route was used in the comparison
- at least 3 browser trials were run for the final directional conclusion
- raw and aggregated numbers were documented
- route-level differences were distinguished from environment-level differences
- if a PR was mentioned, live deployment status was verified from the stage site itself
- any mismatch between PR description and live behavior was explicitly called out
