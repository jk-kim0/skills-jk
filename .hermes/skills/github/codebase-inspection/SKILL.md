---
name: codebase-inspection
description: Inspect and analyze codebases using lightweight file/content search and pygount for LOC counting, language breakdown, and code-vs-comment ratios. Use when asked to find repo documents/files, check lines of code, repo size, language composition, or codebase stats.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository]
    related_skills: [github-repo-management]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection with pygount

Analyze repositories for targeted documents/files, lines of code, language breakdown, file counts, and code-vs-comment ratios. Prefer the lightest inspection that answers the user’s actual question; use `pygount` only for repo metrics.

## When to Use

- User asks to find a document or file in a repo, especially under a specific directory
- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions

## When NOT to Use

- Do **not** run pygount just because the user asked for a general project overview, architecture summary, or quick reconnaissance.
- For "understand this project" requests, prefer a lightweight inspection first: `package.json`, top-level config files, README/docs, and a narrow directory listing of key source folders.
- Only run repo-wide LOC/language scans when the user explicitly asks about size/composition, or when those metrics materially affect the answer.
- On content-heavy repos (docs, CMS exports, cached API payloads, generated data, large `var/` trees), repo-wide scans are often unnecessary and disproportionately slow.

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

If the `pygount` shell command is missing but the Python package is installed, use the module entrypoint below instead. On some environments, `python3 -m pygount` does not work because the package has no `__main__`; `python3 -m pygount.command` is the reliable fallback.

## 0. Lightweight Document/File Lookup

When the user asks to “find the goal doc under docs” or similar, do not stop at filename matching. Use a two-pass lookup:

1. Search filenames in the requested subtree for the literal clue and common variants.
2. If filename search is empty or ambiguous, search Markdown headings and nearby content for the same clue.
3. Report concise results with exact path and line numbers. If no filename matches, say that explicitly and distinguish it from content/heading matches.

Example shape:

```bash
# filename clue
find docs -iname '*goal*' -type f

# heading/content clue
rg -n --glob '*.md' '^(#+ .*\b[Gg]oals?\b)|\b[Gg]oals?\b' docs
```

For user-facing replies, prefer a short answer like:

```text
docs/plans/example.md
- line 5: ## Goal
- line 7: <one-line summary>

파일명에 goal이 들어간 문서는 없습니다.
```

## 0A. Page-Type Classification in Next.js App Router Repos

When a user asks for a list of "static pages", "marketing pages", or similar under a route branch (e.g. `/t/*`), do **not** default to returning every `page.tsx` file in that subtree. Next.js App Router repos commonly mix several page kinds under the same prefix. Classify before listing.

1. **Static marketing pages** — thin `page.tsx` files that directly compose JSX sections or import route-local locale modules. They usually have no URL params, no content loaders, and no MDX rendering pipeline. In the user's vocab they are often called "static marketing page" or just "marketing page".

2. **MDX publication / resource pages** — parametric routes (`[id]/[slug]/page.tsx`) or list wrappers (`page.tsx` with a loader) that render checked-in MDX. Common families: `blog`, `whitepapers`, `news`, `events`, `demo`, `glossary`, `introduction-deck`, `tutorials`, `privacy-policy`, `manuals`.

3. **CMS / dynamic pages** — routes that fetch remote CMS data, render Tiptap/HTML, or rely on a catch-all dynamic page router.

4. **Archived / removed pages** — routes that exist in git history but have been deleted from the current filesystem.

**Verification commands**

```bash
# 1) List current filesystem routes under a prefix
find src/app/[locale]/t -type f -name 'page.tsx' | sort

# 2) Distinguish parametric (MDX detail) vs flat (marketing or list) paths
find src/app/[locale]/t -type f -name 'page.tsx' | grep -E '/\[id\]/|\[slug\]/|\[category\]/' | sort

# 3) Check for deleted/archived routes via git history
git log --all --name-only --pretty=format: -- src/app/\[locale\]/t/ |
  sed '/^$/d' | sort -u |
  grep 'page.tsx'
```

If the user's request is ambiguous ("static page" can mean "statically rendered" in Next.js jargon vs "static marketing copy page" in product terms), ask which family they mean before producing a list. If they react with "that is not what I asked for", immediately switch classification lenses instead of repeating the same directory listing.

## 0B. Historical Content Route / URI Lookup

When asked which URI path an old content page or PR-migrated page had in a sibling content repo, do not stop at the current filesystem. Content trees are often deleted or moved. Use git history and the consuming app's routing rules together.

Also use this workflow when a user asks to remove or edit links/copy from a legacy dynamic page that is rendered by the app but whose source content may live in a sibling content repository. In corp-web-app-style setups, `src/app/[...slug]/page.tsx` may only delegate to a dynamic renderer while the actual page body, such as `/internal`, comes from sibling `corp-web-contents/pages/.../content.mdx` or Blob-backed content. If the route file is absent in the app repo, search the sibling content repo before concluding the page does not exist.

1. Confirm the current repo and sibling repo roots:
   ```bash
   pwd
   git rev-parse --show-toplevel
   git -C ../content-repo rev-parse --show-toplevel
   ```
2. Identify the PR branch when the question references a PR:
   ```bash
   gh pr view <number> --json number,title,headRefName,baseRefName,state,url
   git fetch origin pull/<number>/head:refs/remotes/origin/pr/<number>
   git diff --name-only origin/main...origin/pr/<number> | rg '<slug-or-page-name>'
   ```
3. Search all historical paths in the content repo before reading files:
   ```bash
   git -C ../content-repo log --all --name-only --pretty=format: |
     sed '/^$/d' | sort -u | rg '<slug-or-id>'
   ```
4. If current files are gone, inspect the parent of the deleting commit or a known historical commit:
   ```bash
   git -C ../content-repo log --all --oneline -- <path>
   git -C ../content-repo ls-tree -r --name-only <commit>^ -- <path>
   git -C ../content-repo show <commit>^:<path>/<locale>/meta.json
   ```
5. Derive the public URI from the source path and verify against the app's locale-routing contract. For corp-web-app-style dynamic routing, a source path like `pages/why-querypie/{en,ko,ja}/content.mdx` maps to `/why-querypie`, `/ko/why-querypie`, and `/ja/why-querypie` because the locale segment is stripped from the content path and non-English locales are prefixed in the public URI.
6. Cross-check any existing inventory/tests in the consuming app, especially route-local migration tests that assert canonical URLs.

Report concise evidence: historical source path, derived URI(s), and whether the files exist on current main or only in git history.

## 0B. Verifying Whether a Page Is Actually a Section of Another Page

When asked whether a named route/page is an independent page or a section embedded in another page, verify by content identity rather than filename or route existence alone:

1. Locate the explicit route/page implementation in the current or source repo:
   ```bash
   rg -n "<slug>|<distinct heading>|<distinct CTA text>" src app pages docs
   find src app pages -path '*<slug>*' -type f
   ```
2. Read the full route file and identify distinctive anchors: page heading, section heading, card titles, CTAs, and internal links.
3. Search for those distinctive strings across related repos and content sources, including sibling source repos such as `corp-web-contents` and migrated app repos. Prefer 2-4 highly specific phrases over broad terms like `values`.
4. Compare the component/section boundary:
   - If the page route renders only one section component and the same section appears inside a broader product/solution page, classify it as a standalone URL that duplicates or extracts a section.
   - If the broader page contains the same section plus additional hero/features/CTA content, classify the named page as section-level content, not a full replacement page.
5. Check live/stage behavior with headers and, when useful, body string probes:
   ```bash
   for url in <candidate-urls>; do
     echo "--- $url"
     curl -sS -I "$url" | awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^location:/ {print}'
   done
   python3 - <<'PY'
   import requests
   for url in ["<url1>", "<url2>"]:
       html = requests.get(url, timeout=20).text
       print("---", url, "len", len(html))
       for needle in ["<distinct heading>", "<distinct card title>"]:
           print(needle, html.find(needle))
   PY
   ```
6. Report the conclusion in two dimensions:
   - URL/routing status: whether the route exists and returns 200/redirect/404.
   - Content/site-architecture status: whether the content is unique, duplicated, or absorbed as a section of another page.

Pitfall: do not conclude “independent page” from HTTP 200 alone. A URL can exist solely as a standalone rendering of a section that has already been absorbed into a canonical product/solution page.

## 0C. Legacy Asset-Shaped 404 Triage

When asked whether a 404 for an old-looking public asset path needs action, distinguish a real first-party regression from external/bot/old-cache traffic before proposing fixes:

1. Confirm repo and branch first:
   ```bash
   pwd
   git rev-parse --show-toplevel
   git status --short --branch
   ```
2. Search the current code/content for the exact URL and basename. If no current first-party page emits it, treat the issue as a legacy asset-shaped 404 unless other evidence says otherwise:
   ```bash
   rg -n '/assets/images/07-blog/event-thumb-2\.png|event-thumb-2\.png|07-blog' .
   find public src -name '*event-thumb-2*' -print
   ```
3. Check historical file existence and deletion/addition commits:
   ```bash
   git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep -F 'event-thumb-2.png' || true
   git log --all --name-status -- public/assets/images/07-blog/event-thumb-2.png
   ```
4. If a route-aligned replacement likely exists, verify current content points there and the file exists (for example, event ID 2 now using `heroImageSrc: "/events/2/thumbnail.png"` plus `public/events/2/thumbnail.png`). Do not assume the legacy file and replacement are byte-identical; compare hashes only if compatibility restoration is being considered.
5. Optionally verify stage/production HTTP status for the exact path, but do not turn a confirmed 404 into an action item unless a current first-party emitter exists or compatibility restoration has a documented reason.

Report shape:
- current first-party references: present/absent
- current asset presence and route-aligned replacement, if any
- git history: when the legacy file was added/deleted
- conclusion: no-action vs fix current emitter vs restore compatibility asset

Pitfall: do not add redirects or restore deleted legacy public assets just because runtime logs show 404s. For asset-shaped 404s, the default is no-action when the current site does not emit the exact URL. Restore a compatibility file only for a repeated/high-value external compatibility case with explicit evidence.

## 0D. Next.js Tailwind Adoption / CSS Modules Migration Review

When asked whether a Next.js/React website should adopt Tailwind CSS, or to compare Tailwind against CSS Modules for implementation efficiency and sibling-repo reuse, inspect the live repos before giving a strategic opinion. Check `package.json`, PostCSS/Tailwind entrypoints, `globals.css`, CSS Modules usage, Tailwind `className` usage, and any route inventory or migration plan docs. Then answer separately: whether Tailwind is necessary, whether it is practical/efficient for this site, and what migration shape is safe. When introducing a Tailwind route group into a legacy/CSS Modules app, prefer a truly minimal group-local `globals.css` first (often just `@import "tailwindcss";`) and add base/theme rules only when repeated need is proven; inspect sibling Tailwind repos for reference, but do not copy their shadcn tokens/imports/font/animation globals unless the target repo actually needs that class of global.

See `references/tailwind-adoption-review.md` for the detailed evidence checklist, reuse lens, global CSS baseline guidance, and pitfalls from corp-web-app/corp-web-japan Tailwind review work.

## 0F. Technology Stack Decision / Reference-Repo Stack Review

When asked to choose a technology stack for a repository, especially with references to sibling/internal repositories, inspect the actual reference repos before writing recommendations. Do not rely only on memory, README summaries, or generic framework preferences.

Minimum evidence to collect:

```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
# in each reference repo
cat AGENTS.md 2>/dev/null || true
cat package.json 2>/dev/null || true
find . -maxdepth 3 \( -name 'next.config.*' -o -name 'postcss.config.*' -o -name 'eslint.config.*' -o -name 'vitest.config.*' -o -name 'playwright.config.*' -o -name 'schema.prisma' \) -print
rg -n "DATABASE_URL|POSTGRES|postgresql|provider =|Prisma|Tailwind|React|Next" . --glob '!node_modules/**' --glob '!*.svg'
```

Decision-doc shape:
- State the inspected reference stacks explicitly.
- Separate quick prototype, web application, backend/job pipeline, and database choices.
- If the user prefers PostgreSQL or PostgreSQL-compatible SaaS, make PostgreSQL compatibility the durable decision and treat Supabase/Vercel Postgres/Neon/Railway/Render/RDS as interchangeable candidates unless the user selects one.
- Prefer internal stack continuity when it does not conflict with product needs; for example, if reference repos already use Next.js/React/TypeScript/Tailwind and Prisma/PostgreSQL, start from that rather than inventing a different default.
- Distinguish “initial scaffold” from “later extraction”: do not require a separate FastAPI service on day one if Next.js + Prisma can cover the first reviewable prototype, but document the trigger for moving AI enrichment or long-running jobs into workers.

Pitfall: do not let a convenient BaaS name become the decision. Capture the underlying contract (PostgreSQL-compatible DB, pooled/direct connection handling, ORM/migration model, worker access) so the project can switch SaaS providers later.

## 0E. Technology Stack Decision / Rationale Docs

When asked to decide or document a repository's technology stack, inspect the actual repo and relevant sibling/reference repos before recommending. Do not answer from generic framework preference alone.

1. Confirm the active repo, branch, and whether an existing PR/worktree should be updated.
2. Inspect the target repo's existing docs first (`README.md`, `docs/**`, `AGENTS.md`) to understand product scope, MVP boundaries, and existing architecture terms.
3. Inspect reference repos the user names by reading their `AGENTS.md`/repo guide, `package.json`, `next.config.*`, `postcss.config.*`, Prisma schema, test configs, and deployment notes. Summarize the actual stack from files, not memory.
4. If the user states a durable technical preference (for example PostgreSQL or PostgreSQL-compatible SaaS), record it in the decision doc as a first-class constraint and shape the recommendation around it.
5. Prefer two docs when the user wants rationale to be managed over time:
   - `docs/technology-stack-decision.md` — concise decision, phased plan, and current recommendation.
   - `docs/technology-stack-rationale.md` — per-technology entries with 1-3 line summary, pros, cons, and rationale/status (`Adopt`, `Adopt later`, `Evaluate`, `Avoid for MVP`).
6. Link the rationale doc from the decision doc and README design-doc index.
7. For repo work, commit/push the docs and update the existing PR branch rather than leaving local-only documentation.

Pitfalls:
- Do not overfit to a sibling repo's legacy stack when the new product has no legacy constraint (for example, prefer Tailwind/shadcn for a new UI even if a reference app still has CSS Modules for legacy areas).
- Do not make Supabase the decision if the user's durable constraint is PostgreSQL compatibility; phrase Supabase as one PostgreSQL-compatible SaaS candidate among Vercel Postgres/Neon, Railway/Render Postgres, AWS RDS/Aurora, etc.
- Do not force a separate Python backend into the first scaffold when Next.js + Prisma + PostgreSQL can validate the core entity/review UI first; document Python/FastAPI worker extraction as a later step when enrichment or long-running jobs justify it.

## 0F. Node.js Major Upgrade Necessity Check

When asked whether a repo needs to upgrade to a specific Node.js major, do not answer from general lifecycle intuition alone. Inspect the live repo, CI/runtime pins, dependency engine ranges, hosting/runtime support, and the official Node release schedule.

1. Confirm the active repo and current local toolchain:
   ```bash
   pwd
   git rev-parse --show-toplevel 2>/dev/null || true
   node -v 2>/dev/null || true
   npm -v 2>/dev/null || true
   ```
2. Find repo-level runtime pins and CI/deploy runtime versions:
   ```bash
   for f in package.json .nvmrc .node-version .tool-versions vercel.json Dockerfile docker/Dockerfile .github/workflows/*.yml .github/workflows/*.yaml; do
     [ -e "$f" ] && echo "$f"
   done
   rg -n "node-version|setup-node|NODE_VERSION|engines|node:" package.json vercel.json .github/workflows Dockerfile docker 2>/dev/null || true
   ```
3. Read `package.json` and any workflow files that pin Node. Distinguish root `engines.node` from transitive `package-lock.json` package engine metadata.
4. Check the official Node schedule/current versions rather than relying on memory:
   ```bash
   python3 - <<'PY'
   import json, urllib.request
   schedule = json.load(urllib.request.urlopen('https://raw.githubusercontent.com/nodejs/Release/main/schedule.json', timeout=20))
   index = json.load(urllib.request.urlopen('https://nodejs.org/dist/index.json', timeout=20))
   latest = {}
   for row in index:
       latest.setdefault(row['version'].split('.')[0], row)
   for major in ['v20','v22','v24','v25','v26']:
       print(major, 'schedule=', schedule.get(major), 'latest=', latest.get(major))
   PY
   ```
5. Check important package engine ranges when they materially affect the answer:
   ```bash
   npm view next engines --json
   npm view prisma engines --json
   npm view vitest engines --json
   ```
6. For Vercel-hosted projects, verify Vercel's currently supported Node majors before recommending a major bump. Vercel can lag newly released majors; if the target major is not supported, say so clearly.

Recommended answer shape:
- Direct conclusion first: required / not required / not recommended yet.
- Evidence bullets: repo pins, CI/deploy pins, package engine compatibility, Node LTS/EOL status, hosting support.
- If an upgrade is reasonable but not the requested major, name the safer candidate (for example, Node 24 LTS instead of a non-LTS/unsupported Node 26) and recommend a separate PR/check cycle.

Pitfalls:
- Do not treat a newly released even-numbered Node major as automatically safe; confirm whether it is LTS yet and whether the host supports it.
- Do not recommend changing CI to a major the deployment platform cannot run.
- Do not confuse transitive dependency `engines` in lockfiles with this repo's own Node contract.

## 0F. Sibling-Repo Configuration Precedent Audit

When the user points to a sibling repo as precedent for provider setup, GCP/OAuth, 1Password, deployment secrets, or similar configuration, treat it as a codebase/documentation inspection task with a secret-safety boundary.

1. Confirm both repo roots and branch/status before drawing conclusions.
2. Search the sibling repo for exact provider names, account/project identifiers, setup docs, deploy env examples, and repo-local skills/context directories.
3. Read the authoritative docs/config snippets rather than only grep output. For OAuth/GCP work, inspect consent/auth-platform docs, redirect URI patterns, scopes, env var names, and deployment examples.
4. If a credential manager is involved, verify only accessibility and field structure unless the task explicitly requires runtime injection. Report item title/field labels/presence/length, not secret values.
5. When documenting findings in the target repo, separate: precedent copied from the sibling repo, decisions still required for the target product, and secret retrieval procedures. Never commit credentials, refresh tokens, OAuth client secrets, or generated encryption secrets.
6. If adding a repo-local skill, keep it class-level for the recurring procedure (for example provider credential access), and point target docs to the skill rather than embedding secret-handling commands everywhere.

Useful answer shape:
```text
참조 근거:
- <sibling path>: <what it proves>

대상 repo 정리:
- <target doc/skill paths>

Secret safety:
- <what was verified without revealing values>
```

Pitfalls:
- Do not equate a sibling repo's OAuth client or consent copy with the target product's final production setup; mark reuse vs target-specific decisions explicitly.
- Do not paste credential-manager `--reveal` output into docs, PRs, issues, or chat.
- Do not encode an environment-specific credential item as a global memory fact; keep it in repo docs/skills.

## 0G. Implementation Status Audit

When the user asks to report the implementation status of a feature, do a code-backed status audit rather than summarizing design docs alone.

1. Confirm the active repo and branch first:
   ```bash
   pwd
   git status --short --branch
   ```
2. Search for the feature across code, schema, API routes, UI routes, tests, and docs. Prefer targeted searches for domain terms plus provider/library names.
3. Read the actual implementation files, not just planning docs. For a web app feature, inspect at least:
   - persistence schema/models
   - service/domain logic
   - route handlers/server actions
   - UI entry points
   - focused unit/API/e2e tests
   - README or public docs that state deployment/runtime boundaries
4. Separate status into clear buckets:
   - implemented and reachable through product flow
   - implemented only as lower-level service/adapter code
   - mocked/fake-local/test-only behavior
   - documented future/out-of-scope work
   - missing UI/API/onboarding/configuration surface
5. Run a narrow focused test command when it is cheap and directly relevant. Do not run repo-wide slow verification unless the user explicitly asks.
6. If the audit is being used to refresh a GitHub issue or planning tracker, base the refresh on latest `origin/main` rather than an old local branch. A temporary detached worktree at `origin/main` is a safe pattern for read-only inspection; remove it after updating the issue/tracker. Keep the root checkout unchanged unless the user asked for workspace cleanup or branch updates.
7. For provider-delivery features such as email sending, explicitly distinguish: configured credentials/docs, OAuth/connect routes, sender identity listing, user-selectable sender UI, approval-time sender locking, fallback/test sender paths, and actual external-provider smoke evidence. A feature can have schema/services/tests and still be incomplete if onboarding, selection, locking, or live-send evidence is missing.
8. For docs or planning PR follow-ups that ask to make a seed/demo scenario include “all assets needed for email sending,” audit both the canonical document and the current implementation/schema/seed surface before editing. Search for domain models and fixture creation paths such as `EmailTemplate`, `EmailTemplateVersion`, `Message`, `SendRun`, `SendAttempt`, `TestEmailEventLedger`, `SuppressionEntry`, `EmailEngagementEvent`, `Response`, `HumanFollowUpTask`, recipient-preview/snapshot fields, and sender credential/status models. Then document missing assets as seed acceptance criteria, not optional backlog, and state that reviewers should not need to add fixture/DB rows manually to run the demo flow.
9. When converting a GitHub issue / living blocker document into a feature-status doc, do not copy the issue body as-is. Re-audit latest `origin/main` and reclassify stale blockers: items that landed since the issue was written become current implementation evidence, while live provider smoke or external credential evidence can remain the conservative `In-Progress` boundary.
9. For feature-status docs that sit beside feature plans (for example `docs/feature/status-*.md`), add or update the local feature index when one exists so the status document is discoverable, but keep the status doc focused on implementation state and promotion criteria rather than a long task narrative.
10. If an aggregate status document already contains detailed rows for the same feature, avoid maintaining two competing sources of detail. Move or keep the detailed inventory in the per-feature status document, and replace aggregate rows with concise links/summaries that point to it.
11. Report concise evidence with exact paths and the current behavior. Avoid overstating capability: code for an adapter is not the same as a complete user-facing production flow.

See `references/feature-status-doc-authoring.md` for a reusable per-feature status-document workflow, suggested template, and duplication pitfalls.

Useful answer shape:
```text
결론: <one-line status>

구현됨:
- <capability> — <path/evidence>

부분 구현/제한:
- <capability> — <why not complete>

미완성:
- <missing surface>

검증:
- <command> — <result>
```

Pitfalls:
- Do not equate design/proposal documents with implementation.
- Do not say a feature is production-ready just because unit tests cover a provider adapter.
- For provider integrations, distinguish credential/config support, OAuth/onboarding UI, actual provider calls, and fake/test sender paths.

## 0H. UI Placement / Product Rationale Audit

When the user asks why a UI entry point exists in a certain product area (for example, a settings button that appears to belong under a different entity), answer from implemented code plus canonical design decisions, not from naming intuition alone.
For provider-backed sender settings, be especially careful to separate a Team-scoped credential/sender-identity registry from the Sales Person business persona and sender selection; see `openspec-decision-management` reference `references/outbound-agent-sales-person-gmail-sender-decision.md` for the Outbound Agent pattern.

1. Confirm repo/branch and inspect the exact route/page that renders the questioned UI copy.
2. Locate the target route/action and read what it actually manages: domain entity fields, provider credentials, registry/listing, OAuth/connect flow, admin policy, etc.
3. Search docs/specs/OpenSpec decisions for the route, copy, and domain terms. Treat accepted decisions as intent evidence, but distinguish them from current UX quality.
4. Compare product concepts explicitly:
   - primary domain owner (for example Sales Person decides the From persona/address)
   - backing operational registry (for example Team-scoped Gmail credential/sender identity)
   - actual send-time resolution/locking behavior in service code
5. If the UI is technically intentional but product-confusing, say both: “this exists because …” and “the confusion is valid because …”. Do not defend the implementation as correct merely because tests/specs assert it.
6. If the user's follow-up clarifies or changes the product policy, treat it as a Product Owner decision: update the canonical design/spec record first, then the UI/schema/source tests that encode the policy.
7. When applying a small follow-up in an already-active PR worktree, check for unrelated dirty files before committing. Stage only the files that belong to the follow-up and explicitly report any unrelated local changes left uncommitted.
8. Recommend a naming/navigation cleanup in product terms, such as moving the main CTA to the domain entity screen or renaming an admin registry to avoid conflicting with the entity setting.

Useful answer shape:
```text
결론: <why it is there / whether it is intentional>

현재 구현:
- <route/copy> → <target and behavior>
- <service/schema evidence> → <actual product boundary>

설계 근거:
- <doc/spec path> → <accepted decision>

제품 판단:
- <what belongs to entity screen>
- <what belongs to team/admin registry>
- <recommended cleanup>
```

Pitfalls:
- Do not answer only from the live page label; inspect both route code and design/spec records.
- Do not blur “credential/connection inventory” with “business sender persona”. If they differ, name the two layers clearly.
- Do not overstate that all settings belong in one place when the code has separate send-time binding and OAuth/credential ownership boundaries.

## 0I. Domain Ownership Boundary Audit

When a user states that a domain concept or attribute must exist only on one owning entity (for example Team-only market/country/language) and asks whether other entities still expose it, treat it as a repo-wide ownership-boundary audit across implementation, docs, and UI design.

1. Confirm the active repo/branch and, for PR follow-up after a merge, start from the latest main or rebase the active PR worktree before editing.
2. Identify the canonical owner and all forbidden aliases/legacy names. Include synonyms and older field names, not just the exact current term (for example `country`, `language`, `market`, `targetMarket`, `locale`, “Market”, “국가”, “언어”).
3. Inspect persistence/schema and API contracts first. Verify non-owner models, DTOs, form schemas, seed data, fixtures, and tests do not define or accept the forbidden fields.
4. Inspect UI sources and design docs for non-owner display, selection, or input affordances. Remove stale copy that tells users to choose the attribute on child entities such as Campaign, Audience, Product, Sales Person, Contact List, or Template when the owner is Team.
5. Update canonical requirements/spec docs to state the boundary positively and operationally: the concept belongs only to the owner; partitioning by that concept is achieved by creating separate owner entities, not by configuring child entities.
6. Use targeted searches after edits to prove the remaining hits are either owner-scoped implementation or the new requirement text itself. Do not rely on a single grep; scan both code and docs/design paths.
7. For a fuller checklist and report template, see `references/domain-ownership-boundary-audit.md`.
8. Commit only the files relevant to the boundary cleanup and report:
   - canonical requirement/spec paths updated
   - implementation paths verified or changed
   - stale UI/form/design references removed
   - remaining search hits and why they are acceptable

Useful search shape:
```bash
rg -n "country|language|targetMarket|\bmarket\b|Market|국가|언어" prisma src docs openspec tests
```

Pitfalls:
- Do not stop after confirming the database schema. Stale design docs and form copy can still instruct users to configure the attribute on the wrong entity.
- Do not replace child-entity fields with inherited child fields unless the user asked for that. For a strict ownership boundary, child entities should use the owner context implicitly.
- Do not leave ambiguous phrasing like “Campaign market” when the actual product rule is “Campaign belongs to a Team, and Team defines market”.

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

Fallback when the `pygount` executable is unavailable:

```bash
python3 -m pygount.command --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
5. **Stop quickly if the scan is slower than expected** — if a repo-wide scan on a docs/content-heavy repo does not return promptly, interrupt it and switch to a narrower inspection. Do not keep waiting on a long-running analysis when a lighter method would answer the user’s actual question.
7. **Do not equate filename misses with document misses** — when a user asks for a “goal doc” or similarly named document, a filename-only search may return nothing while the real target has a `## Goal` heading. Follow filename search with heading/content search before reporting no result.
