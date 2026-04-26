---
name: skills-jk-gha-pr-creation
description: Create pull requests in the skills-jk repository via the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` instead of direct `gh pr create`, to avoid local shell quoting issues and follow repo convention.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, github-actions, workflow-dispatch, skills-jk]
---

# skills-jk GHA PR Creation

Use this skill when creating a PR in the `skills-jk` repository.

## Why this exists

`skills-jk` has a repository-standard PR creation workflow at `.github/workflows/create-pr.yml`.
It accepts `branch`, `title`, and `body` via `workflow_dispatch`, then creates the PR in GitHub Actions.
This is safer than local `gh pr create --body "..."` when the body contains backticks, paths, or multiline markdown that can be mangled by shell quoting.

## When to use

Trigger this skill when:
- working inside the `skills-jk` repository
- a new PR needs to be opened
- the branch is already committed and pushed
- the PR body is multiline markdown

## Procedure

1. Confirm you are in `skills-jk` and that the work branch is pushed.
   - Check current branch with `git branch --show-current`
   - Check remote tracking with `git status -sb`

2. Confirm whether a PR already exists for the branch.
   - Use `gh pr status`
   - If a PR already exists, edit that PR instead of creating a new one

3. Prepare the PR body in a file first.
   - Write the full markdown body to a temporary file
   - Avoid inline shell interpolation of multiline markdown

4. Trigger the repository workflow instead of calling `gh pr create` directly.
   - Use `gh workflow run .github/workflows/create-pr.yml`
   - Pass:
     - `-f branch=<branch>`
     - `-f title=<title>`
     - `--raw-field body="$(cat <body-file>)"`

5. Wait for the workflow run to appear and finish.
   - Use `gh run list --workflow create-pr.yml --limit 5`
   - In this repo, the dispatched `create-pr.yml` run may appear with `headBranch` shown as `main` in `gh run list`, even when it creates a PR for another branch. Do not try to identify the run by filtering on the feature branch name.
   - If you need to inspect the run, take the newest `create-pr.yml` run and use `gh run view <run-id>` or `gh run watch <run-id>`.

6. Verify the PR was created.
   - Prefer `gh pr status` or `gh pr view --head <branch>` to confirm the resulting PR.
   - Do not rely on `gh run list --branch <branch>` to prove the PR-creation workflow ran; that branch filter may show nothing for this workflow even when PR creation succeeded.
   - Report the PR number and URL

## If a PR already exists

Do not dispatch the create workflow again unless intentionally creating a replacement PR.
Instead:
- use `gh pr edit <number> --title ...`
- or `gh pr edit <number> --body-file <file>`

## Pitfalls

- Follow the active repository/global GitHub CLI safety policy when invoking `gh`. In this environment that means using `env -u GITHUB_TOKEN gh ...` rather than raw `gh ...`.
- Do not pass complex markdown directly to `gh pr create --body` in this repo unless there is a strong reason
- `create-pr.yml` targets `main` as the base branch
- The workflow appends a GitHub Actions bot footer to the body
- If the branch has an existing open PR, the workflow may fail or create duplicate intent; check first
- After dispatching the PR-creation workflow, verify completion with `gh run watch` and then confirm the resulting PR with `gh pr view` or `gh pr status`
- `gh pr checks` may legitimately report no checks for the new PR branch; if so, also inspect `gh run list --branch <branch>` before concluding that no CI ran

## Evidence from use

Observed in `skills-jk`:
- direct local `gh pr create --body` caused shell quoting issues with markdown/backticks
- `.github/workflows/create-pr.yml` already exists and is the repo-preferred PR creation path

## Completion checklist

- branch pushed
- existing PR checked
- workflow dispatched
- workflow completed successfully
- resulting PR number and URL verified
