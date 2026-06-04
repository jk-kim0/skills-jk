# News PR rebase and MDX id guardrails

Use when rebasing a corp-web-app PR that touches news/press-release docs or prepares future `src/content/news` MDX records.

## Workflow

1. Fetch latest main and inspect the PR head with `gh pr view <pr> --json headRefName,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup`.
2. Check whether the PR branch is already checked out via `git worktree list --porcelain` or `git branch -vv`. If it is already attached to a worktree, operate in that worktree rather than creating a duplicate checkout.
3. Rebase the PR branch onto `origin/main`.
4. Determine the current news MDX id ceiling from both filenames and frontmatter:
   - filenames: `src/content/news/<id>-<slug>.<locale>.mdx`
   - frontmatter: `id: "<id>"`
   - ensure the max values agree.
5. If the PR is a draft/docs precursor for a future news MDX item, record the next available id in the relevant doc so the eventual MDX addition starts after the current max id.
6. If the PR already contains actual `src/content/news` MDX files that collide with latest main IDs, first finish the rebase conflict resolution while preserving the PR's logical records, then perform one scoped renumbering pass after the rebase completes:
   - move only the PR-owned MDX files from stale IDs to the next available IDs,
   - move only their route-aligned assets (for example `public/news/<old>/thumbnail.svg`) to matching `public/news/<new>/...`,
   - update frontmatter `id`, `heroImageSrc`, paired `relatedIds`, public route test params/hrefs, and list/translation test expectations,
   - avoid broad search-and-replace that changes unrelated latest-main records using the same old IDs.
7. After renumbering, explicitly verify both filename and frontmatter ceilings and search for stale PR-specific references such as old `*-iso-42001*` filenames, old SVG asset paths, and old paired `relatedIds` before committing.
8. For docs-only changes, run the lightest checks: `git diff --check` and Prettier on the changed markdown/guidance files.
9. After any `git commit --amend`, always run `git status --short --branch` before push. If a desired edit remains unstaged, stage it and amend again before force-pushing.
10. Push with `git push --force-with-lease origin <branch>` and immediately re-query PR head/checks.

## Notes

- Do not create or edit actual `src/content/news` MDX files unless the task explicitly asks to publish/add a news record.
- For current main-derived news collections, assign ids by the latest collection state, not by stale PR branch state.
- If local `main` is not checked out in any worktree, it is safe to fast-forward/reset the local `main` ref to `origin/main` after fetching.