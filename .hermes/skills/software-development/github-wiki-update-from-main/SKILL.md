---
name: github-wiki-update-from-main
description: Create or update a GitHub wiki page from the latest repository main branch, using the wiki git remote as the source of truth for writes and verification. Handles private repos where public wiki URLs may return 404.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Wiki, Documentation, Main-branch-audit, Private-repo]
    related_skills: [github-auth, github-repo-management]
---

# GitHub wiki update from latest main

Use this when the user asks to create or update a GitHub wiki page and the content must reflect the latest repository `main` branch rather than stale local state.

## When to use

- Create a new page in `https://github.com/<owner>/<repo>/wiki/...`
- Update an existing wiki page without modifying the product repo itself
- Build documentation from the latest `origin/main`
- Private repository wikis where browser/HTTP checks may misleadingly return 404 when unauthenticated

## Core rule

Treat the repository `main` branch and the separate wiki git repository as two different sources of truth:

1. Content source of truth: latest `origin/main` of the product repo
2. Write target / publish source of truth: `<repo>.wiki.git`

Do not assume the current local checkout is up to date.
Do not assume the wiki can be modified through the product repo.

## Required workflow

### 1. Read repository context first

Inside the product repo:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status -sb
git remote -v
git fetch origin main
git rev-parse FETCH_HEAD
git log --oneline -1 FETCH_HEAD
```

Use `FETCH_HEAD` or `origin/main` as the documentation basis, not the possibly dirty working tree.

### 2. Check GitHub auth and wiki availability

Always follow the GitHub CLI safety rule:

```bash
gh auth status -h github.com
gh repo view <owner>/<repo> --json nameWithOwner,defaultBranchRef,url,hasWikiEnabled,isPrivate
```

Important:
- `hasWikiEnabled: true` only confirms wiki support exists.
- The actual wiki content lives in a separate git repository.

### 3. Clone the wiki repository directly

Do not edit wiki content through the product repo.
Clone the dedicated wiki repo.
Prefer a fresh unique temporary directory instead of a reused hard-coded path:

```bash
tmpdir=$(mktemp -d "/tmp/<repo>.wiki.XXXXXX")
git clone git@github.com:<owner>/<repo>.wiki.git "$tmpdir"
```

Why this is safer:
- avoids collisions with an existing stale clone
- avoids accidental reuse of dirty wiki state from a previous run
- makes it easy to abandon and recreate the clone if the first attempt fails

If you intentionally want a stable workspace path, first check whether it already exists and whether reusing it is actually helpful.
Do not keep retrying the exact same blocked clone command/path combination when a fresh temp directory would solve the issue more cleanly.

Useful checks:

```bash
git ls-remote --heads git@github.com:<owner>/<repo>.wiki.git
git status -sb
```

If the wiki repo is empty or has a different default branch, inspect before writing.
Common wiki branch is `master`.

### 4. Inspect existing wiki pages before writing

List current files in the wiki clone and read the existing relevant page if present.

Typical page mapping:
- `Page Name` -> `Page-Name.md`

Example:

```bash
find . -maxdepth 1 -type f | sort
```

If the user asked for a new page, create a new `.md` file and leave the old one untouched.

### 5. Build content from latest main, not from stale local files

If the request says “current link”, “latest main”, or similar, inspect `FETCH_HEAD` / `origin/main` directly.
Do not trust `read_file` against the checked-out working tree when the repo is dirty or behind remote — local edits can silently diverge from the real latest-main state.

Preferred authoritative patterns:

```bash
git show origin/main:path/to/file
# or
git show FETCH_HEAD:path/to/file
```

Use the archive/extract approach when you need to inspect many files together or search across a clean snapshot.
A reliable pattern is to archive the fetched commit to a temporary directory and inspect that snapshot:

```bash
tmpdir=$(mktemp -d)
git archive --format=tar FETCH_HEAD | tar -xf - -C "$tmpdir"
```

Then read the relevant files from that extracted snapshot.

This avoids contamination from:
- dirty local changes
- unrelated in-progress work
- being behind `origin/main`

## Key lesson for CTA / route inventories

When documenting implemented links in `corp-web-japan`-style repos, treat local redirect endpoints and local path/query values as the current implemented links if that is what the latest main branch uses.

### Important mismatch-inventory lesson from content-route audits

When adding a "current code vs target canonical" inventory to a wiki page, do not assume an older or previously discussed route still exists on latest `origin/main`.

Audit the latest code snapshot and classify each family carefully:
- exact match already exists
- legacy/transitional route exists and differs from target canonical
- no dedicated family route exists yet; current behavior is still served from a shared hub plus query/category filtering

This distinction matters because a misleading mismatch table can imply the app currently uses a route like `/white-paper/...` when latest main may actually have no dedicated white-paper family route at all and still serve that content under `/features/documentation`.

For content-family audits, explicitly check:
- route files under `src/app/[locale]`
- public href builders such as `getPublicListHref` / `getPublicDetailHref`
- category config hrefs and query-string filters
- sitemap entries and metadata canonicals

In the final wiki table, prefer wording like:
- "current route is `/features/demo`" when that route exists
- "current implementation has no dedicated route; uses `/features/documentation?category=blogs` and `/features/documentation/:slug`" when family routes are not yet split

This produces a more accurate migration inventory and avoids documenting nonexistent intermediate routes as if they were real current behavior.

Examples:
- Current link can be `/contact-us`
- Current link can be `/contact-us?inquiry=ai-consulting&product=ai-crew`
- Current link can be `/demo/use-cases`
- Current link can be an external documentation path-style label such as `/ja/features/documentation/...`

Note separately when a local endpoint redirects to a final external destination such as `https://www.querypie.com/ja/company/contact-us`.
Do not collapse these two concepts unless the user explicitly wants only final destinations.

Also verify whether routes that used to be pages are now redirect endpoints.
Example pattern:
- old local page removed
- new `route.ts` added
- documentation should say the current link is the local endpoint and mention the redirect destination

### Important content-family audit lesson: local index, local detail, and upstream card hrefs can diverge

For publication-family wiki pages such as Blog / WhitePapers / Events, do not assume there is only one "current route" per item.
A latest-main audit may reveal three different surfaces that all matter:

1. local public index/list route
2. local canonical detail route
3. current visible card href from the public index, which may still point upstream or elsewhere

A common failure mode is to document only the local detail route and miss that the user-facing public list currently links to a different destination.
This makes the wiki look cleaner than the actual implementation and hides important transition state.

When auditing a content family, explicitly inspect:
- the public list page route file
- the preview/local list page route file if one exists
- the list-item source or href-builder used by the public list
- the local detail route files and redirect behavior
- robots/canonical metadata on local detail pages
- any hidden/shadow records used only for redirects

Recommended wiki structure when this divergence exists:
- implementation status summary
- current route behavior by surface
- per-item inventory that lists:
  - local canonical detail route
  - current public list card link
  - upstream equivalent if different
- separate hidden/shadow redirect section when needed

This is especially important when:
- the local detail flow exists but is `noindex,nofollow`
- the public list is local but intentionally links to upstream content
- preview/local MDX routes exist alongside the public list
- a hidden record preserves an old ID while redirecting to another visible canonical record

### Important CTA-inventory lesson from later main-branch updates

Do not preserve stale wiki `Current link` cells based on older design assumptions like `#contact` when latest `origin/main` has since centralized the real href values into exported constants.

In `corp-web-japan`, re-audit these common sources on latest main before editing the wiki:
- `src/content/top-page.ts`
- `src/content/home.ts`
- `src/content/ai-dashi-links.ts`
- page entrypoints such as `src/app/page.tsx`, `src/app/solutions/ai-crew/page.tsx`, `src/app/solutions/ai-dashi/page.tsx`
- component-level CTA surfaces such as `ai-dashi-faq`, `ai-crew-floating-guide`, and `resource-post-page`
- regression tests such as `tests/launch-readiness-coverage.test.mjs`

Why this matters:
- latest main may move from local anchors like `#contact` to concrete links like `/contact-us?...`
- a wiki page can stay stale even after the product code and tests have been updated
- `Current link` should reflect the actual implemented href on latest main, not the older intended target or a previous audit conclusion

### Updating an existing CTA inventory page without rewriting other columns

If the user asks to update only the `Current link` column of an existing wiki page:
- preserve `Target link`, comments, notes, and table structure unless the user explicitly asks otherwise
- use latest `origin/main` as the sole source of truth for current-link values
- use any newer wiki pages (for example `CTA-Inventory-v2` or `CTA-Inventory-Shared-CTAs`) only as cross-checks, not as the write target unless requested

Recommended approach:
1. fetch latest `origin/main`
2. inspect the real source files on `origin/main`
3. map each CTA row back to the owning file / route / anchor
4. patch only the `Current link` cell in the existing wiki page
5. preserve `Target link`, comments, and any Chikako guidance unless the user explicitly asked to rewrite them
6. leave rows whose structure would require a broader content-model rewrite unless the user asked for that broader rewrite

Formatting rule learned from `corp-web-japan` CTA inventory maintenance:
- in the `Current link` column, prefer path/anchor-style visible text such as `#contact`, `/contact-us?inquiry=...`, `/demo/use-cases`, or `/ja/features/...`
- avoid showing a raw full external URL as the visible link text when a cleaner path-style label is available
- it is fine for the markdown destination to remain the full external URL; the important part is that the displayed text stays concise and inventory-like
- this rule applies especially to documentation, whitepaper, and use-case detail links where older wiki pages may show the entire `https://www.querypie.com/...` string in the cell

Why this matters:
- older inventory pages often mix local anchors, redirect endpoints, and live external URLs in one table
- a full rewrite can accidentally alter `Target link` guidance or Chikako comments that the user wanted preserved
- shared CTA inventories and page-specific inventories may intentionally diverge in scope, so use them for validation but not blind copy-over

## Reusable-component link inventory rule

When documenting a shared CTA component that is instantiated on multiple pages, do not infer the page-specific target from the section name or earlier documentation.
Verify each page in two places on the latest `origin/main` snapshot:

1. the component call site (for example `FloatingConversionCta href="..."`)
2. the actual anchor definition on that page (for example `id="contact"`)

Recommended audit pattern:

```bash
git show origin/main:path/to/page.tsx | nl -ba | sed -n '<relevant-range>p'
git show origin/main:path/to/section-file.tsx | rg 'id="contact"|id="..."'
```

Why this matters:
- shared components may keep the same label while their per-page `href` values change
- older wiki pages often preserve stale assumptions like `#final-cta` or other legacy anchors
- page copy may describe a “final CTA box” even though the real implemented anchor is now `#contact`

If a user explicitly questions whether a documented current link is really latest-main-accurate, re-audit from `origin/main` immediately instead of trusting the existing wiki content or your previous summary.

## Editing rules

### Prefer targeted edits for existing wiki pages

When updating an existing wiki page, prefer targeted edits (`patch` tool or careful line-based replacements) over a full rewrite generated from `read_file` output.

Reason:
- some file-reading tools return line-number-prefixed content for display
- copying that displayed output back into the file can accidentally write the line numbers into the markdown

Safe pattern:
- inspect current content
- apply narrow replacements for the changed commit SHA, links, notes, and source-file list
- re-read the affected lines and diff before commit

Use full-file rewrite only when you are generating the page content from scratch and you are certain the source text is raw markdown without display prefixes.

### Recovery rule when the wiki file is already contaminated

If the existing wiki page already contains display artifacts such as line-number prefixes (`1|`, `2|`, etc.), do not keep patching that displayed text mechanically.

Safer recovery pattern:
1. Fetch the remote wiki file to inspect whether the contamination is already in `origin/master`
2. Reconstruct the intended markdown from authoritative sources (latest `origin/main`, your notes, or a clean local draft)
3. Overwrite the wiki page with the reconstructed raw markdown
4. Re-read the saved file and verify the first lines are plain markdown, not numbered display output

This is safer than incremental patching because once the remote page itself contains numbered lines, simple search/replace can preserve or reintroduce the artifact.

## Verification rules

### Verify publish by git, not only by browser URL

After writing the wiki file:

```bash
git add <page>.md
git commit -m "<message>"
git push origin master
```

#### Concurrent wiki edit pitfall: push races are common

GitHub wiki repos are small and often edited directly by humans or other agents. Even right after a successful `pull --ff-only` or `pull --rebase`, your `git push origin master` can still be rejected with a non-fast-forward error because someone else pushed in the meantime.

Treat this as a normal concurrency case, not a failure of your content.

Preferred recovery loop:

```bash
git status -sb
git fetch origin master
git log --oneline --left-right --graph --max-count=20 HEAD...origin/master
git pull --rebase origin master
git push origin master
```

If another new remote commit appears before the retry push finishes, repeat the fetch/rebase/push cycle until the push succeeds.

Important:
- Re-check that the remote-only commit touched unrelated wiki files before assuming your page needs manual conflict resolution.
- If the remote change is on the same page, do not blindly keep either side. First inspect `origin/master:<page>.md` to understand the newly updated baseline, then re-apply only your intended delta (for example: one restored item, updated counts, one route correction) onto that latest remote content, and continue the rebase.
- When the same page changed on both sides, prefer reconstructing the final markdown from the remote page plus your verified new facts instead of editing conflict markers in-place for long tables.
- After the final successful push, verify local `HEAD` and `origin/master` are identical.

Then verify with git-based checks:

```bash
git rev-parse HEAD
git log --oneline -1
git fetch origin master
git show origin/master:<page>.md | sed -n '1,40p'
```

This is the authoritative verification that the wiki page exists remotely.

### Important private-repo pitfall

For private repos, unauthenticated HTTP checks like:

```bash
curl -I https://github.com/<owner>/<repo>/wiki/<Page-Name>
```

may return `404` even when the page exists.
Do not treat that as publish failure if the wiki git remote contains the committed file.

## Multi-repo replacement-audit note

When the wiki page is a readiness audit or redirect-planning document for replacing one production site with another, do not limit yourself to a single repo snapshot.

Use all relevant sources of truth explicitly and record them in the page header:
- target repo latest `origin/main` SHA
- legacy app repo latest `main` SHA if the live site still runs there
- legacy content repo latest `main` SHA if routing/content is split across repos
- operational evidence windows such as Vercel Runtime Logs, Google Search Console, and GA4 date ranges

Recommended structure for these pages:
1. source-of-truth commit SHAs for every repo inspected
2. operational evidence window(s)
3. current-state findings
4. derived task list or redirect rules
5. cutover blockers / first batch recommendation

Important lesson from replacement-readiness wiki work:
- the most useful redirect/readiness docs are driven by both code inspection and live traffic/error evidence
- Vercel 404 samples help prioritize redirect families
- GSC top pages identify SEO-sensitive legacy URLs that need exact redirects
- GA source/traffic data shows whether the current production surface is still centered on the legacy site
- if the user asks for a separate wiki page, create a new page and leave prior audit pages untouched

### Important stale-plan rewrite lesson after latest-main merges

When rewriting a planning or migration-status wiki page after a large feature has merged to `origin/main`, do not just update commit SHAs and preserve the old narrative.

### Historical incident page follow-up rule

When updating an existing operational snapshot page such as a Vercel runtime-log incident page, do not automatically rewrite the whole document as if the original incident never happened.

Recommended pattern:
1. preserve the original incident window, sampled findings, and historical conclusions as the primary record
2. add a clearly labeled follow-up section with:
   - latest `origin/main` SHA used for re-checking
   - relevant route/code history if the incident was tied to a specific implementation path
   - live production and stage HTTP verification of the exact affected URLs
   - recent runtime-log re-check for those exact paths
3. if the issue is now fixed, update the page's later conclusion / next-action wording so it explicitly says the incident was real but is now resolved
4. keep the distinction explicit:
   - historical incident evidence
   - current live behavior

This avoids two opposite mistakes:
- erasing a real incident from the historical record just because it is fixed now
- leaving the wiki sounding like an active unresolved production bug after the fix has already landed

Useful verification pattern for exact-path incident follow-up:
- inspect latest `origin/main` route code
- inspect route git history for the relevant file
- `curl -I -L` the exact production and stage URLs mentioned in the incident
- query recent Vercel logs for those exact paths to confirm whether they still produce `500` or now return normal `307` / `200` behavior

Re-audit whether the feature changed the document's core thesis.
Typical examples:
- a page framed around "largest missing blocker" may become outdated once the blocker is implemented on main
- a plan page may need to become a "current state + remaining follow-up" page instead of a pre-implementation proposal
- a portfolio-level migration inventory may need blocker priorities reordered after the merge

Recommended rewrite pattern:
1. identify the old document's key assumptions
2. verify each assumption against latest `origin/main`
3. explicitly call out which earlier claims are no longer true
4. rewrite conclusions and priorities, not just evidence sections
5. note when related split wiki pages are now stale because they still reflect older branches or pre-merge status

This avoids a common failure mode where a wiki page cites the newest commit SHA but still describes the pre-merge world.

### Practical acceleration trick for stale wiki rewrites

If the wiki page already records an older baseline SHA, diff that old SHA against the new `origin/main` SHA before rewriting the page narrative.

### Incident-follow-up wiki update rule: preserve the original snapshot, then add a clearly separated resolution update

For operational pages such as Vercel runtime-log reports, later updates may happen after the originally logged incident has already been fixed on `origin/main` and on the live site.
Do not rewrite the page as if the original incident never happened.

Recommended pattern:
1. keep the original audit window and original finding language intact enough to preserve historical truth
2. relabel time-sensitive statements like `active issue` or `currently reproduces` so they are explicitly scoped to the original audit time
3. add a new `Last updated` timestamp and a second latest-main SHA for the follow-up update
4. verify the latest fix directly from `origin/main` with `git log`, `git show`, and a focused diff against the older recorded SHA
5. verify the current live behavior separately with direct HTTP/browser checks
6. rewrite conclusions and next actions so the page distinguishes:
   - what was true in the original incident snapshot
   - what is true now after the fix

Recommended wording pattern:
- `the May 8 clean sample captured a real production 500, but the issue is now resolved`
- `at the time of the original audit ...`
- `later follow-up verification after latest main moved to commit ...`

Why this matters:
- incident pages are both historical records and current-status references
- blindly replacing the old narrative with the new one destroys the value of the original log evidence
- blindly leaving `active` wording unchanged makes the wiki stale and misleading after the fix

Recommended pattern:

```bash
git diff --name-status <old-sha>..<new-sha> -- src/app src/content src/lib
git diff --stat <old-sha>..<new-sha> -- <most-relevant-subtrees>
```

Why this helps:
- it quickly reveals which route families or content inventories actually changed since the last wiki snapshot
- it exposes when a route changed shape entirely (for example redirect `route.ts` replaced by local `page.tsx`)
- it prevents preserving stale blocker language just because the old wiki page sounded plausible
- it helps target the re-audit on the exact files that invalidate old counts, rollout status, or priority ordering

Use this especially for migration dashboards, rollout plans, and route-readiness pages where a few merged PRs can completely invert the document's conclusions.

## Consolidation and wiki-IA cleanup rule

When the user says several wiki pages are duplicated, stale, or should be reorganized around the latest canonical document, do not limit yourself to editing one page in isolation.

Recommended approach:
1. inspect the overlapping wiki pages together
2. identify one canonical page that should become the main source of truth
3. merge the overlapping status/scope/readiness content into that canonical page
4. simplify `Home.md` so it points to the canonical page first, then to supporting detail pages
5. if the user explicitly wants duplicate pages removed, actually delete the old wiki files and commit the deletions instead of leaving placeholder stubs

Important distinction:
- if the user says to consolidate but does not ask for deletion, a short superseded note page can be acceptable
- if the user later says to delete duplicates, remove the files from the wiki repo and verify the deletion on `origin/master`

Useful reporting pattern after this kind of cleanup:
- name the canonical page that now owns the topic
- list any deleted pages explicitly
- mention any new supporting pages created for implementation plans or inventories

## Suggested response notes to user

When reporting completion, include:
- that a new wiki page was created or updated
- whether the old page was left untouched
- the source-of-truth product commit SHA used for the audit
- the wiki commit SHA used for publication
- any notable latest-main findings, such as redirect endpoints replacing previous page routes

## Minimal checklist

- product repo README/AGENTS context checked
- `origin/main` fetched
- latest main SHA recorded
- wiki enabled confirmed
- `.wiki.git` cloned
- existing wiki page inspected
- content built from latest main snapshot
- new or updated wiki `.md` file written
- committed and pushed to wiki repo
- remote wiki file verified with `git show origin/<branch>:<file>`
- user informed that browser 404 can be expected for private repos without auth

## Pitfalls

- Editing only the product repo and forgetting the wiki is separate
- Using stale local checkout instead of `origin/main`
- Treating redirect destinations as the implemented current link when the current implementation is a local endpoint
- Assuming `/wiki/<Page>` HTTP 404 means the page failed to publish in a private repo
- Accidentally updating the old wiki page when the user explicitly requested a new page name
