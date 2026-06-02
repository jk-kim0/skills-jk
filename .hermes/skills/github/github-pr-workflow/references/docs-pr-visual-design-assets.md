# Docs PR visual-design asset workflow

Use this reference when an existing PR needs a visual-design mock-up image added to documentation.

## Pattern

1. Confirm the existing PR is still open and identify its head branch.

```bash
gh pr view <pr-number> --json state,headRefName,baseRefName,title,url
git status --short --branch
```

2. Work in the existing PR worktree/branch, not the root checkout or a new unrelated branch.
3. Inspect the docs image convention and place the new asset next to related images, commonly under `docs/**/img/`.
4. Generate a committed image asset, usually PNG, and link it from the Markdown document with a relative path.
5. For a quick static mock-up when browser rendering or graphics dependencies are not available, author an SVG, render it to PNG, and commit only the PNG if the SVG is just an intermediate.

macOS example:

```bash
qlmanage -t -s 2880 -o "$tmpdir" docs/ui/img/example.svg
cp "$tmpdir"/*.png docs/ui/img/example.png
sips -c 1800 2880 docs/ui/img/example.png >/dev/null
sips -g pixelWidth -g pixelHeight docs/ui/img/example.png
```

6. Add the docs link:

```md
![Short descriptive alt text](./img/example.png)
```

7. Verify and push:

```bash
git diff --check
git add docs/path.md docs/path/img/example.png
git commit -m "docs: add visual design mock-up"
git fetch origin main --prune
git rebase origin/main
git push
```

If the rebase rewrites PR-branch commits, the push can be rejected as non-fast-forward. After confirming the branch is the intended PR head, use:

```bash
git push --force-with-lease origin <branch>
```

## Pitfalls

- Do not attach the image only in chat or the PR body when the design doc should be self-contained.
- Do not leave temporary SVG/source files committed unless the repository convention keeps editable sources.
- Do not skip the PR-open check before adding follow-up commits to an existing PR.
- Do not use `--force` when `--force-with-lease` is sufficient for a rebased PR branch.
