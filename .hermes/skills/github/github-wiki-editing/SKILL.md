---
name: github-wiki-editing
description: Edit a GitHub repository wiki by using the separate `.wiki.git` repository, updating markdown from the live codebase, and pushing directly. Use when asked to create or revise GitHub wiki pages such as Sitemap, docs indexes, or operational runbooks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Wiki, Documentation, Markdown]
    related_skills: [github-auth, github-repo-management]
---

# GitHub Wiki Editing

GitHub wikis are separate git repositories. Do not try to edit them through the main repo working tree. Use the wiki repo, edit markdown there, then commit and push.

## When to use

Use this skill when the user asks to update a GitHub wiki page, rewrite a wiki document, or keep wiki content aligned with the current codebase.

## Core workflow

1. Confirm GitHub auth works.

```bash
gh auth status
```

2. Use the repository's wiki git remote in a dedicated temporary directory.

Wiki remote pattern:

```text
https://github.com/<owner>/<repo>.wiki.git
```

Notes:
- The wiki remote is separate from the main repo.
- Wiki default branch is commonly `master`; verify after cloning instead of assuming.
- Prefer a fresh temp directory for wiki work so edits stay isolated.

3. Read the existing wiki page before changing it.

Common page filename rule:
- Wiki page `Sitemap` -> file `Sitemap.md`
- Other pages usually follow the visible page name with `.md`

4. If the wiki content depends on the app/site structure, read the live code first.

Preferred source-of-truth order:
- route `src/app/**/page.tsx`
- referenced content files such as `src/content/*.ts`
- existing wiki page only for structure, not truth

5. Rewrite or patch the wiki markdown.

Recommended approach:
- keep existing sections unless the user asked for a full rewrite
- update formatting rules inside the document if the user is shaping a reusable convention
- prefer explicit formatting instructions in the wiki itself so future updates can follow them reliably

6. Verify the final markdown locally.

Check for:
- requested section names and ordering
- correct base URLs
- links attached only where requested
- exact page titles sourced from implementation
- consistent bullet or nested bullet structure

7. Commit and push the wiki repo.

Typical git steps:
- inspect status
- stage the changed wiki page
- create a clear commit message
- push to the wiki repo's active branch
- verify the push with `git status --short --branch`, `git log -1 --oneline`, and `git ls-remote origin refs/heads/<wiki-branch>`; GitHub REST repo/ref endpoints for `.wiki` repositories can return `404` even when the git push succeeded

## Practical lessons

- `gh repo view` helps confirm the main repo, but wiki editing itself is usually plain `git` against `.wiki.git`.
- Important repo-context pitfall: once your shell cwd is inside the wiki clone, `gh` commands that infer the current repository (for example `gh pr list`, `gh pr view`, or even some `gh repo` operations) can target `<owner>/<repo>.wiki` instead of the product repository and fail with errors like `Could not resolve to a Repository with the name '<owner>/<repo>.wiki'`.
- The same cwd trap can affect product-code inspection too: file reads/searches that use relative paths after you have `cd`'d into the wiki clone can silently hit the wiki repo (or fail with missing-path errors) instead of the product repo.
- When you still need product-repo GitHub data or source inspection during wiki work, either run commands from the product repo checkout, pass `--repo <owner>/<repo>` explicitly for `gh`, use a terminal command with an explicit `workdir` pointing at the product repo, or use absolute product-repo file paths.
- If the repository already has a local wiki clone that the user expects you to use, prefer that existing clone over making a fresh temp clone. Verify it is clean enough to work in, then edit there and push from there.
- When using Hermes file-editing tools on a cloned wiki repository, prefer absolute paths over `~/...` paths and immediately re-read the file before committing. Path expansion can be inconsistent across tool contexts, so verify the final markdown from disk before `git add`.
- Wiki repos can change remotely while you are editing. If `git push` is rejected with a non-fast-forward error, fetch the wiki remote, inspect the new remote commits, then `git pull --rebase origin <wiki-branch>` (commonly `master`) or equivalently rebase onto `origin/<wiki-branch>`, and push again. Do not force-push unless explicitly required.
- When a user wants a wiki page to remain maintainable, update the page's own `Writing guidelines` section, not just the content section.
- For sitemap-style docs, if the user cares about site structure readability, a path-first nested bullet list is clearer than a flat sentence-style bullet list.
- If links must use a specific base URL, encode that rule in the document's guidelines and in every generated entry.
- If titles are dynamic in page metadata, trace back to the content source that feeds the metadata before documenting titles.
- When validating sitemap completeness, compare the wiki against `src/app/**/page.tsx`, then explicitly exclude routes that are only content-detail catchalls or pages that immediately call `notFound()`.
- If the user says the wiki must reflect the latest `main` branch, create a detached worktree from `origin/main` and read routes/content from that worktree instead of the current feature branch. This avoids documenting branch-local or stacked-PR changes by accident.
- If `origin/main` advances during the conversation, refresh or recreate that detached worktree before rewriting the wiki. Do not assume an earlier `main` worktree is still current.
- If the repo keeps separate comparison wiki pages for content indexes like Blog, WhitePapers, or Events, clarify whether those index routes should still appear in the main sitemap; capture that policy in `Writing guidelines` so later updates stay consistent.
- When the user wants the wiki to remain self-maintaining, rewrite `Writing guidelines` to encode concrete formatting rules such as: path-first nested bullets, which field gets the link, title source-of-truth, base URL, and which route categories are excluded.
- If the user specifies a wiki-local formatting rule for links (for example markdown `[path](url)` in tables), apply it consistently to every actual link cell in the page instead of mixing raw URLs and markdown links.
- GitHub wiki right-side navigation can be customized with a dedicated `_Sidebar.<extension>` page. Treat it as normal wiki content: use Markdown nested bullet lists for manual hierarchy. This supports a tree-like visual grouping of links, but it is not an auto-generated, collapsible file-tree sidebar; future pages must be added to `_Sidebar` manually.
- When the user says a wiki page was deleted or renamed, update `_Sidebar.md` in the same commit: remove stale links to the deleted page slug/name, then search the sidebar for the old slug/name before committing.

- For site-navigation audit issues that feed wiki work, if you need to recommend external reference URLs, verify them from the live site header/footer and sitemap rather than inferring from labels alone.

- Before rebasing or pushing wiki changes, run `git status --short` in the wiki repo. If unrelated local modifications are present from earlier work, restore or otherwise isolate them before `pull --rebase`; otherwise the rebase can fail even when your target page commit is clean.
- If the repository already has a maintained local wiki clone, prefer reusing that clone instead of creating a fresh temp clone. Check `git status --short --branch` first, make your page edits there, then commit and push.
- If `git push` is rejected because `origin/master` advanced, prefer `git fetch` + `git pull --rebase origin master` and then push again, rather than force-pushing wiki history.
- When the user wants markdown links in wiki docs, apply the requested `[path](url)` format consistently everywhere links appear: table cells, bullet lists, and section headings that include route paths. Do not leave bare URLs in those places unless the user explicitly wants raw URLs.
- GitHub wiki right-side navigation can be customized by creating `_Sidebar.md` in the wiki repo. If `_Sidebar.md` does not exist, creating it replaces the default auto-generated page list with your custom sidebar.
- `_Sidebar.md` is plain Markdown, so hierarchical navigation is achieved with nested bullet lists. This is suitable for grouping many related pages (for example, multiple dated operational reports under a single parent label), but it is not a real collapsible folder tree.

## Example: path-first sitemap format

```md
## Main pages
- [`/`](https://stage.example.com/)
  - Original title: ...
  - Korean translation: ...
- [`/solutions/foo`](https://stage.example.com/solutions/foo)
  - Original title: ...
  - Korean translation: ...
```

## Pitfalls

- Do not edit wiki files inside the main repo; they are not the same repository.
- Do not assume the wiki page content is current; verify against code.
- Do not assume page titles from route names; read `metadata.title` or the source content feeding it.
- Do not attach links to labels other than the exact field the user requested.
- Do not forget to push the wiki repo after committing; local wiki edits are otherwise invisible.

## Verification checklist

- Wiki repo location isolated from the main repo
- Target page exists or was created with the expected filename
- Content reflects the current code implementation
- Formatting matches the user's requested structure
- Links use the required base URL
- Commit and push completed successfully
