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

When asked which URI path an old content page or PR-migrated page had in a sibling content repo, do not stop at the current filesystem. Content trees are often deleted or moved. Use git history and the consuming app's routing rules together:

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
