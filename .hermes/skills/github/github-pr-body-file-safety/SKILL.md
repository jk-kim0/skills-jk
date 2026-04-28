---
name: github-pr-body-file-safety
description: Use gh PR body files instead of inline shell strings when markdown contains backticks or shell-sensitive content.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, gh, markdown, shell]
    related_skills: [github-pr-workflow, github-pr-body-file-and-stacked-rebase]
---

# GitHub PR body-file safety

Use this when creating or editing a PR with `gh` and the body contains markdown that may be unsafe to embed directly in a shell string.

## When to use
- the PR body includes backticks
- the PR body includes code spans like `src/app/page.tsx`
- the PR body includes fenced code blocks
- the PR body includes multiline markdown copied from notes
- the inline `gh pr create --body` result looks truncated or mangled

## Safe default
Prefer `--body-file` over inline `--body` for any non-trivial markdown body.

## Create a PR safely
```bash
cat > /tmp/pr-body.md <<'EOF'
## Summary
- restore the local `/events` index page
- update `src/app/events/page.tsx`

## Test Plan
- `npm run test:ci`
- `npm run build`
EOF

gh pr create \
  --title "fix: restore events index page copy" \
  --body-file /tmp/pr-body.md
```

## Repair a PR body after creation
If you created the PR with inline `--body`, immediately verify it.

```bash
gh pr view --json title,body,url
```

If the body is corrupted, rewrite it from a file:

```bash
gh pr edit <PR_NUMBER> --body-file /tmp/pr-body.md
```

## Why this matters
Shell command substitution can break PR bodies that contain backticks. The PR may still be created successfully, but the markdown body can lose content or render incorrectly.

## Minimal checklist
- write the body to a temporary markdown file
- use `gh pr create --body-file`
- inspect the created PR with `gh pr view --json body`
- if needed, repair with `gh pr edit --body-file`
