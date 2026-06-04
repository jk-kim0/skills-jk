# Worktree-safe PR body temp files

When creating or editing GitHub PRs/comments from a linked git worktree, avoid writing temporary PR bodies under `.git/`.

## Why

In linked worktrees, `.git` is usually a file that points to the real gitdir, not a directory. A path like `.git/pr-body.md` can fail with `Not a directory`.

## Safe pattern

Prefer `/tmp` for one-off PR bodies:

```bash
cat > /tmp/<repo>-pr-body.md <<'EOF'
...
EOF
env -u GITHUB_TOKEN gh pr create --body-file /tmp/<repo>-pr-body.md
```

If the temp file should live under the repository gitdir, resolve the path first:

```bash
body_file="$(git rev-parse --git-path pr-body.md)"
cat > "$body_file" <<'EOF'
...
EOF
env -u GITHUB_TOKEN gh pr edit <pr> --body-file "$body_file"
```

Keep using `--body-file` when bodies contain backticked paths or commands so the shell does not perform command substitution.
