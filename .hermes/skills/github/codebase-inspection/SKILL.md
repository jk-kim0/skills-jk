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

## 0D. Node.js Major Upgrade Necessity Check

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
