---
name: refresh-repository-guides-from-code
description: Update repository guidance documents by reconciling recent commits with the current codebase, workflows, routes, and tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [documentation, git, repository-maintenance, readme, workflow]
---

# Refresh repository guides from code

Use when the user asks to bring repository guidance up to date with the current implementation.

## Goals

1. Review the recent change window first.
2. Identify the project-owned guidance files that actually exist.
3. Reconstruct the current contract from code, tests, and workflows.
4. Update the guidance docs so they match reality.

## Procedure

### 1. Start from the latest main-based branch

- Confirm the target repository and active branch/worktree.
- Fetch `origin --prune`.
- Create a fresh docs branch from `origin/main` unless the user explicitly wants a different base.
- Verify the merge-base matches `origin/main` before editing.

Example:
```bash
git fetch origin --prune
git checkout -b docs/refresh-guides origin/main
git merge-base HEAD origin/main
git rev-parse origin/main
```

### 2. Inspect recent commits before reading docs

Default to the last 7 days unless the user gives a different window.

Start with the commit summary view:
```bash
git log --since='7 days ago' --date=short --pretty=format:'%h %ad %an %s' --decorate --all
```

Then inspect the actual touched files, not just subjects. A docs refresh can be wrong if you rely only on commit titles.

Example:
```bash
for c in $(git log --since='7 days ago' --pretty=format:'%H' --reverse); do
  echo '---'
  git show --stat --format='%h %ad %an %s' --date=short --compact-summary --name-only --no-patch "$c"
  git diff-tree --no-commit-id --name-only -r "$c"
done
```

Look for themes such as:
- route additions/removals
- canonical URL changes
- content-source migrations
- workflow/CI/deploy changes
- testing-policy changes
- previous docs commits that may already be stale again

Important lesson:
- The changed-file list often reveals scope splits that commit titles hide, such as "detail route added" versus "list page still gated" or "detail page made local while list cards still link upstream".

### 3. Inventory only project-owned guidance files that really exist

Do not assume a `docs/` tree exists.
Do not treat worktree copies, vendored package docs, or generated markdown as repository guidance.

Common in-scope files:
- top-level project guide
- top-level agent/instructions guide
- a real `docs/` directory if present
- intentional markdown notes for retained assets or operations

Important lesson:
- When the request mentions a docs directory that is absent, narrow scope to the project-owned markdown files that actually exist and state that explicitly.

### 4. Reconstruct the live contract from implementation

Check the files that define real behavior:
- `package.json`
- route/page files under the app tree
- redirect/API route files
- sitemap/robots/metadata files
- content loaders and source directories
- tests that encode current policy
- GitHub Actions workflow files

Use tests as evidence when they clearly assert intended behavior.

Questions to answer:
- Which public routes really exist now?
- Which paths are pages versus redirects?
- Which routes are launch-gated or intentionally excluded from the sitemap?
- Are detail pages canonicalized by `id`, slug, or both?
- Are list pages and detail pages following the same model, or is there a mixed contract (for example local detail rendering but upstream list-card hrefs)?
- Are any legacy compatibility routes intentionally retained for only one content family?
- What files are the actual content source of truth?
- Which commands in the docs are still valid?
- Do the docs mention files or setup paths that no longer exist?

### 5. Fix the most common stale-doc patterns

#### Old setup/tooling references

Remove or rewrite references to:
- setup commands that no longer exist
- guides or companion files that are missing
- local config/skill paths that are not actually present in the repo

#### URI policy drift

Align docs with the real route model:
- canonical index paths
- detail routes
- redirect-only surfaces
- launch-gated pages
- sitemap expectations
- legacy compatibility routes that intentionally remain for only a subset of content
- mixed list/detail behavior where index cards still point upstream even though local detail routes now exist

#### Content-source drift

Document the actual source of truth:
- source directories
- frontmatter/data contracts
- gating markers or content split markers
- loader paths that matter to editors
- redirect allowlist behavior when unmatched-path handling is part of the user-visible contract

#### Verification drift

Do not leave generic "always run a dev server" guidance if the project really uses CI or preview deployments first.

### 6. Keep statements concrete

Prefer implementation-backed statements such as:
- a route is local and MDX-backed
- a path is redirect-only
- a page is intentionally excluded from sitemap coverage
- a query string is preserved across a redirect

Avoid vague prose that will drift quickly.

### 7. Verify the doc update itself

Before finishing:
- run `git diff --check`
- search for stale phrases you intended to remove
- confirm every referenced file, route, and command still exists
- confirm you did not document worktree-only or vendor-tree state as if it were repo state

Helpful commands:
```bash
git diff --check
git status --short
```

### 8. Commit and push

Use a focused docs commit.

Example:
```bash
git add <changed-doc-files>
git commit -m "docs: refresh repository guides for current implementation"
git push -u origin HEAD
```

## Reporting checklist

Report:
- recent change themes reviewed
- which guidance files were actually in scope
- the main contract changes reflected in docs
- verification performed
- branch and commit pushed

## Practical lessons

- Verify whether a docs directory really exists before promising to update it.
- Guidance refreshes should be grounded in current code, tests, and workflows rather than prior prose.
- Route-policy docs often lag behind migration work; reconcile them against live routes and sitemap behavior.
- Verification instructions should match the repository’s real workflow instead of generic local-server advice.
- Ignore markdown under worktrees, dependency directories, and other generated/vendor trees when identifying the real project documentation set.
