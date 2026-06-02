# Workflow-dispatch PR creation verification during cleanup

Use this note when a repo prefers creating PRs through a GitHub Actions `workflow_dispatch` workflow during a local cleanup/preservation sweep.

## Pattern

Some PR-creation workflows are dispatched from the default branch even when the input `branch` is a feature branch. In `gh run list`, those runs can show `headBranch: main`, so filtering run history with `--branch <feature-branch>` may return `[]` even though the workflow ran and created the PR.

## Verification sequence

1. Push the preservation branch and verify the remote head directly:
   - `git rev-parse HEAD`
   - `git ls-remote origin refs/heads/<branch>`
2. Dispatch the repo-preferred PR workflow. If the workflow input is named `body`, do not pass `-f body-file=...`; `gh workflow run` treats that as an unexpected workflow input unless the workflow explicitly defines `body-file`. Read the file into a shell variable and pass `-f body="$body"` instead.
3. If `gh run list --workflow <workflow> --branch <branch>` is empty, re-query without the branch filter:
   - `gh run list --workflow <workflow> --limit 5 --json databaseId,status,conclusion,displayTitle,headBranch,createdAt,url`
4. Inspect the newest run log when needed:
   - `gh run view <run-id> --log`
5. Verify the PR by head branch, not by run branch:
   - `gh pr list --state all --head <branch> --json number,state,title,url,headRefOid,baseRefName`
6. If the workflow succeeded but PR lookup is still empty after inspecting logs, only then fall back to direct `gh pr create`, after one final duplicate check.

## Why this matters

During cleanup, a branch-filtered run lookup can falsely suggest the workflow did not run. The durable signal is the run log plus `gh pr list --head <branch>` and the remote branch head SHA.
