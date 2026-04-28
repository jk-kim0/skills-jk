---
name: historical-preview-draft-pr-from-commit
description: Create a Draft PR and Preview Deployment from a historical commit by branching from the target snapshot and adding only a minimal non-functional trigger change.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, github, vercel, preview, historical, draft-pr, regression, comparison]
---

# Historical Preview Draft PR from Commit

Use this when the user wants to compare the current site/app against an older implementation state without re-implementing that old state manually.

Typical requests:
- "복원해서 Preview 띄워줘"
- "지난주 삭제 전 상태로 Draft PR 만들어줘"
- "old rendering 과 current rendering 비교용 Preview 필요"
- "적절한 commit 시점에서 간단한 문서 변경 PR만 만들어줘"

## Core idea

Instead of reconstructing old behavior on top of current `main`, do this:

1. Identify the exact historical commit that already contains the desired behavior.
2. Create a fresh branch/worktree directly from that commit.
3. Add only a tiny non-functional change (usually a docs file) so GitHub/Vercel treats it as a new PR branch.
4. Open a Draft PR against `main`.
5. Use the resulting Preview Deployment for visual/behavioral comparison.

This is much safer and faster than re-adding old code manually.

## When this is the right method

Choose this method when:
- the goal is comparison, not immediate merge
- the old behavior clearly existed in git history
- the user explicitly wants a historical restoration preview
- large code edits would be wasteful or risky
- a Vercel/GitHub preview is enough for evaluation

Do NOT use this when:
- the user wants the old behavior merged back into current main immediately
- the historical commit is too old to build/deploy with current infra
- secrets, env shape, or platform contract changed so much that the old commit is non-runnable

## Workflow

### 1. Find the removal/change point

Search recent history around the affected paths and keywords.

Examples:
```bash
git fetch origin --prune
git log --since='14 days ago' --oneline --decorate --graph --all --grep='blog\|publication\|resource'
git log --since='14 days ago' --oneline --decorate --graph --all -- path/to/affected/files
```

Then inspect the candidate removal commit:
```bash
git show --stat <removal-commit>
```

Important pattern:
- If commit `R` removed the behavior, the restoration baseline is often `R^`.
- Verify by listing relevant files at `R^`.

Examples:
```bash
git rev-parse <removal-commit>^
git ls-tree -r --name-only <removal-commit>^ | grep 'relevant/path'
git show <removal-commit>^:path/to/file
```

### 2. Verify the chosen baseline really contains the target behavior

Before branching, confirm the historical snapshot has the exact routes/files/content you want to compare.

Examples:
```bash
git ls-tree -r --name-only <baseline-commit> | grep '^src/app/blog\|^src/app/posts\|^content/source-posts/blog'
git show <baseline-commit>:src/app/posts/[category]/[slug]/page.tsx
```

Do not guess. The whole value of this method is using the real historical state.

### 3. Create a fresh worktree and branch from the historical commit

Use a new worktree so the old snapshot does not contaminate current working branches.

```bash
git worktree add .worktrees/<topic> -b <branch-name> <baseline-commit>
cd .worktrees/<topic>
git status -sb
git rev-parse HEAD
git branch --show-current
```

Recommended branch naming:
- `docs/restore-pre-<change>-preview`
- `preview/<feature>-historical-compare`

Even if the branch name is `docs/...`, it can still carry the historical code snapshot because the real content comes from the branch base commit.

### 4. Add only a minimal non-functional trigger change

Preferred method: add a tiny markdown file under `docs/` explaining the branch purpose.

Why:
- triggers PR/preview cleanly
- makes branch intent obvious to reviewers
- avoids accidental behavioral deltas beyond the historical baseline

Example content:
- what historical commit this branch is based on
- which removal/change commit it precedes
- that the branch exists only for preview comparison
- that the docs file is the only new change on top of the historical snapshot

Use `write_file` rather than shell heredocs when possible.

### 5. Commit and push

```bash
git add docs/<note>.md
git commit -m "docs: trigger preview for historical restore"
git push -u origin <branch-name>
```

Keep the commit message explicit that this is only a preview/restore trigger.

### 6. Open a Draft PR

Use a Draft PR so nobody mistakes it for a normal merge-ready implementation PR.

PR body should include:
- this restores a historical snapshot for comparison
- the exact baseline commit SHA and subject
- the removal/change commit it is meant to compare against
- that only a minimal docs file was added on top
- that the PR is not intended for direct merge without follow-up review

Example structure:
```md
## Summary
- restore the pre-removal website/app state from historical commit `<sha>`
- add a minimal docs-only change to trigger Preview Deployment
- use this Draft PR only for comparison against the current implementation

## Historical baseline
- branch base commit: `<sha>` (`<subject>`)
- comparison target: the last state before `<removal commit subject>`

## Notes
- this PR intentionally restores an older state for preview comparison
- the only new change on top of that historical snapshot is `docs/...md`
- this is not intended for merge as-is without explicit follow-up direction
```

### 7. Capture Preview Deployment

After PR creation:
```bash
gh pr checks <pr-number>
gh run list --branch <branch-name> --limit 5
gh pr view <pr-number> --comments
```

Useful observation:
- `gh pr checks` often returns non-zero while checks are still pending; read the table, do not treat the exit code alone as failure.
- The Vercel PR comment often contains the clean Preview URL even before every GitHub check is green.

Record both:
- PR URL
- Preview URL

## Practical findings from corp-web-japan blog-rendering restore

In the April 2026 corp-web-japan case:
- the removal commit was `7ebeed6` (`fix: keep blog index and remove local blog detail content (#56)`)
- the correct restoration baseline was `f7afba3`, i.e. `7ebeed6^`
- using the parent commit was cleaner than trying to revert the removal on top of modern `main`
- a single docs file was enough to create PR #100 and trigger a working Vercel Preview

This pattern is broadly reusable whenever a user wants "the site as it looked right before X was removed".

## Pitfalls

- Branching from current `main` and trying to cherry-pick historical behavior manually
- Choosing the removal commit itself instead of its parent
- Adding functional edits on top of the historical baseline, which muddies the comparison
- Forgetting to state clearly in the PR body that the branch exists only for preview comparison
- Interpreting pending `gh pr checks` exit codes as hard failure

## Done criteria

- exact historical baseline identified and verified from git
- fresh branch/worktree created from that baseline
- only a minimal non-functional trigger change added
- draft PR created successfully
- preview deployment URL captured and shared
