# Pre-push PR state guard

Use this guard when committing, amending, pushing, or force-pushing work that is intended to update an existing GitHub PR.

## Problem pattern

A PR can be merged while a local worktree still has its old head branch checked out. If the agent then commits and pushes to that old branch name, GitHub may accept the push and recreate/update the remote branch even though the merged PR no longer tracks it. The pushed commit will not update the merged PR and may leave stray remote state.

## Guard steps

1. Before editing or pushing against a named PR, check the PR lifecycle state:

   ```bash
   gh pr view <pr> --json state,closed,mergedAt,headRefName,headRefOid,url
   ```

2. Verify the local and remote branch tip you intend to push:

   ```bash
   git rev-parse HEAD origin/<branch>
   ```

3. If the PR is `MERGED` or closed, do not push to the old PR branch name.

4. For follow-up work after a PR merged, choose one of these instead:
   - find the active follow-up PR/branch with `gh pr list --head <branch>` or keyword search;
   - create a fresh branch from latest `origin/main`;
   - if an existing related open PR covers the same class of change, update that PR branch and amend its body.

5. If an accidental remote branch was recreated from a merged PR branch and no open PR uses it, delete it after preserving the intended changes elsewhere:

   ```bash
   gh pr list --head <branch> --json number
   git push origin --delete <branch>
   ```

## Verification

After the correct branch is pushed:

```bash
gh pr view <pr> --json state,headRefName,headRefOid,mergeStateStatus,statusCheckRollup
git status --short --branch
git rev-parse HEAD origin/<branch>
```

The PR head SHA should match the pushed branch tip before reporting CI status.
