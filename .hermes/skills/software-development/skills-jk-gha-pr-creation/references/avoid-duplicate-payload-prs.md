# Avoid duplicate payload PRs during repeated cleanup sweeps

Use this when repeated `workspace 정리` / local sweep work in `skills-jk` finds new untracked skill/reference files and you are about to create a bot-authored PR.

## Pattern

A previous cleanup pass may already have created another branch and PR carrying the exact same file tree, but the branch name may differ. This can happen when:

- root `main` is clean except for newly generated reference files
- a fresh branch is created for those files
- another helper branch/worktree with the same payload already exists
- a create-PR workflow finishes shortly after an earlier check, so the duplicate PR is easy to miss

## Required preflight before dispatching `create-pr.yml`

Before creating a new PR for a small local sweep payload:

1. List existing open PR branches:
   ```bash
   env -u GITHUB_TOKEN gh pr list --state open --json number,headRefName,url,title
   ```
2. For each plausible existing cleanup/follow-up branch, compare the payload tree against the candidate branch:
   ```bash
   git diff --name-status <existing-branch>..<candidate-branch>
   ```
3. If the diff is empty and the existing branch has an open bot PR, do **not** dispatch another create-PR workflow.
4. Reuse/report the existing PR and delete only local duplicate branches/worktrees if they have no PR metadata.
5. If both branches already have open PRs, do not close either PR without explicit user approval. Report the duplicate and preserve both until the user chooses which PR to close.

## Why

`skills-jk` PR creation is intentionally bot-authored through `.github/workflows/create-pr.yml`, but repeated cleanup loops can accidentally create two bot PRs for the same two-file reference payload. Payload comparison by branch tree is the fastest way to catch this before dispatching another workflow.
