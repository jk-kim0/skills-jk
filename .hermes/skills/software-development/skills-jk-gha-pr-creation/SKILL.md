---
name: skills-jk-gha-pr-creation
description: Create pull requests in the skills-jk repository via the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` instead of direct `gh pr create`, while delegating generic PR and cleanup decisions to the canonical workflow skills.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, github-actions, workflow-dispatch, skills-jk]
    related_skills: [github-pr-workflow, git-worktree-safety-pack]
---

# skills-jk GHA PR Creation

## Purpose

Use this skill only for the `skills-jk` repository's repo-specific PR creation mechanism.

`skills-jk` opens normal review PRs through `.github/workflows/create-pr.yml` so the PR author is `github-actions[bot]` and multiline Markdown bodies avoid local shell quoting problems.

This skill is intentionally a thin wrapper. Do not duplicate generic branch/worktree cleanup or general GitHub PR lifecycle procedures here.

Canonical owners:

- General PR lifecycle, branch creation, commit/push, CI interpretation, issue-linking policy, and `gh` compatibility: `github-pr-workflow`.
- Local main/worktree cleanup, dirty-root preservation, stale branch/worktree classification, and repeated workspace sweep logic: `git-worktree-safety-pack`.
- This skill: the `skills-jk` bot-authored PR creation workflow and its repo-specific verification quirks.

## When to use

Trigger this skill when all are true:

- the repository is `skills-jk`
- the work branch is already committed and pushed
- a normal review PR should be opened or updated
- the PR should be bot-authored through `.github/workflows/create-pr.yml`

If the task is still about discovering, preserving, or classifying local changes before a PR exists, load `git-worktree-safety-pack` first and return here only after the branch payload is ready.

## Procedure

1. Confirm branch and remote ref.

```bash
branch=$(git branch --show-current)
git status --short --branch
git rev-parse HEAD
git ls-remote origin "refs/heads/$branch"
```

2. Confirm no open PR already exists for the branch.

```bash
env -u GITHUB_TOKEN gh pr list --head "$branch" --state open --json number,url,title
```

If an open PR exists, update that PR body/title instead of dispatching the workflow again.

3. Prepare a PR body in a repo-external file.

```bash
cat >/tmp/skills-jk-pr-body.md <<'EOF'
## 요약
- ...

## 검증
- ...
EOF
```

4. Dispatch the repo-standard PR creation workflow.

```bash
env -u GITHUB_TOKEN gh workflow run .github/workflows/create-pr.yml \
  -f branch="$branch" \
  -f title="<PR title>" \
  --raw-field body="$(cat /tmp/skills-jk-pr-body.md)"
```

5. Watch only the create-PR workflow run long enough to verify PR creation.

```bash
env -u GITHUB_TOKEN gh run list --workflow create-pr.yml --limit 5 --json databaseId,status,conclusion,createdAt,headBranch,displayTitle
env -u GITHUB_TOKEN gh run watch <run-id> --exit-status --interval 5
```

In this repo, `gh run list` may show the workflow run's `headBranch` as `main` even when it creates a PR for another branch. Identify the newest `create-pr.yml` run rather than filtering by feature branch.

6. Verify PR object, author, and payload.

```bash
env -u GITHUB_TOKEN gh pr list --head "$branch" --state open --json number,url,title,author,headRefName,baseRefName,headRefOid
git rev-parse HEAD
git ls-remote origin "refs/heads/$branch"
git diff --name-only origin/main...HEAD | sort
```

Report the PR number and URL.

## If a PR already exists

Do not dispatch `create-pr.yml` again unless intentionally replacing an incorrect PR.

Use:

```bash
env -u GITHUB_TOKEN gh pr edit <number> --title "..."
env -u GITHUB_TOKEN gh pr edit <number> --body-file /tmp/skills-jk-pr-body.md
```

After editing or pushing, verify the remote branch ref directly before trusting PR metadata, because `gh pr view` / `gh pr status` can lag briefly.

## Repo-specific pitfalls

- Use `env -u GITHUB_TOKEN gh ...` in this environment unless a task explicitly requires the inherited token.
- Do not use direct local `gh pr create` for normal `skills-jk` review PRs. The repository-standard path is `create-pr.yml`, which creates a bot-authored PR.
- If a PR was accidentally created directly by a human account, do not silently accept it as equivalent. Preserve the branch tip, create a replacement bot-authored PR through the workflow, and do not close the mistaken PR unless the user explicitly asks.
- `create-pr.yml` targets `main` as the base branch and appends a GitHub Actions bot footer to the body.
- `gh pr view --head <branch>` is not supported by all `gh` versions; for lookup use `gh pr list --head <branch>` or pass the branch name positionally to `gh pr view`.
- `gh pr view --json mergeStateStatus,statusCheckRollup` can show `mergeStateStatus: BLOCKED` with an empty check rollup for fresh docs/skill/config PRs. Verify whether checks are actually attached before calling it a failure.
- The dispatch command with `--raw-field body="$(cat body.md)"` is reliable for normal Korean/English Markdown bodies. For unusually long or YAML-heavy bodies, inspect the created PR body after creation and edit with `--body-file` if needed.
- If `.github/workflows/create-pr.yml` itself is being changed, the PR creation run still uses the default branch's old workflow until the PR merges; one final warning from the old workflow is not evidence that the branch diff failed.

## Local workspace sweep routing

Older versions of this skill contained a large local workspace sweep playbook. That logic now belongs to `git-worktree-safety-pack` and its detailed references.

Use these routing rules instead of copying the old playbook here:

- Dirty root checkout, stale worktrees, repeated `workspace 정리`, behind-main no-op collapse, or preservation branches -> `git-worktree-safety-pack`.
- General branch/PR creation, issue-linking policy, PR body file safety, CI/check interpretation, merged PR follow-up, or existing PR updates -> `github-pr-workflow` plus the inactive `github-pr-workflow` pack.
- Only after a clean branch has been pushed should this skill handle the `skills-jk` bot PR dispatch.

The remaining references under this skill are intentionally narrow:

- `references/dirty-root-preserve-pr-cleanup-loop.md` — repo-specific quirks for bot-authored preservation PRs after the generic cleanup procedure has been selected.
- `references/create-pr-workflow-node-runtime-upgrade.md` — default-branch workflow-dispatch nuance when changing `.github/workflows/create-pr.yml` itself.
- `references/repeated-cleanup-old-active-skill-port.md` — porting stale active-skill residue into current `.hermes/skill-packs/**` paths.
- `references/sed-conflict-strip-pitfall.md` — append-only markdown conflict-resolution pitfall.
- `references/squash-merged-pr-worktree-cleanup.md` — tree-diff rule for squash-merged PR worktree cleanup.

Do not add another local-sweep incident note here.
If the lesson is generic cleanup, update `git-worktree-safety-pack`; if it is generic PR lifecycle, update `github-pr-workflow`.

## Completion checklist

- branch pushed
- existing PR checked
- create-PR workflow dispatched
- workflow completed successfully
- resulting PR number, URL, bot author, base branch, head SHA, and payload file list verified
