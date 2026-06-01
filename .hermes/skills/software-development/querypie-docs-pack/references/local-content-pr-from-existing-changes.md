# Local content-change PR from existing working-tree changes

Use this reference when the user asks to turn existing local querypie-docs changes into a PR, especially when the current checkout is already `main` with uncommitted changes.

## Pattern

1. Confirm current branch, upstream sync, and local changes:
   - `git fetch origin --prune`
   - `git status --short --branch --untracked-files=all`
   - `git rev-list --left-right --count origin/main...HEAD`
   - `git diff --stat` and `git diff --name-status --find-renames`
2. If `main` is at `origin/main` and only local changes exist, create the PR branch from the current state before committing.
3. Inspect generated/content diffs for mechanical leftovers before staging:
   - `#link-error` placeholders after route/file renames.
   - `_meta.ts` key/title mismatches after renaming release-note files.
   - Product-version links that still point to the old release-note slug.
   - Markdown ordered-list numbering mistakes introduced by appended sections.
4. If the user says an attached/new file is a renamed tracked file, make Git see the rename by removing the old tracked path and staging both paths. Verify with `git diff --cached --name-status --find-renames`.
5. Run `git diff --cached --check` before commit. Fix trailing blank lines or whitespace warnings immediately.
6. Commit with repo convention from `docs/commit-pr-guide.md`:
   - MDX content changes use `mdx:` prefix.
   - PR title/body should be Korean, polite, concise.
   - Use `--body-file` for multiline PR bodies.
   - Include `🤖 Generated with Codex` when Codex was used.
7. Push and create the PR. Do not run local build/test unless explicitly requested; for document-only PRs, note that local build/test was skipped and monitor GitHub checks briefly.

## Notes

- `confluence-mdx/target/{lang}` is a symlink to `src/content/{lang}`; commit source content paths, not duplicate symlink paths.
- For release-note range updates, keep the route slug, page title, Confluence mapping, product-version links, and `_meta.ts` label consistent.
