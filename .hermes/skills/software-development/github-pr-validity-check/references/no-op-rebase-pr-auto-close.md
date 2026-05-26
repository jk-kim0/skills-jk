# No-op rebase can auto-close an open PR

## Trigger

Use this note when an open PR is rebased onto the latest base branch and conflict resolution shows that every original delta is either:

- already present on the latest base branch,
- invalid against the latest implementation contract, or
- out of scope for the PR after newer main-branch changes.

In that case the correct code resolution may be to keep the latest base version of every conflicted file, leaving the branch with no code diff.

## GitHub behavior to avoid

If you force-push the PR branch so that `headRefOid == baseRefOid`, GitHub may automatically close the PR. It can then refuse `gh pr reopen` because there is no head/base difference.

This matters for users who explicitly require that PRs are only closed after their approval.

## Safe sequence

1. Resolve conflicts by preserving latest base where the PR delta is duplicate/invalid.
2. Verify the code diff is empty:
   ```bash
   git diff --name-status origin/main...HEAD
   git rev-list --oneline origin/main..HEAD
   ```
3. If the user did not ask to close the PR, keep the PR branch distinct with an empty commit before pushing:
   ```bash
   git commit --allow-empty -m "chore: keep PR branch open after rebase"
   git push --force-with-lease origin <head-branch>
   ```
4. Update the PR body using a body file. State clearly:
   - latest main was preserved,
   - original deltas were dropped as duplicate/invalid,
   - changed files/additions/deletions are `0 / 0 / 0`,
   - the only remaining commit is code-change-free if applicable.
5. Final sanity check:
   ```bash
   git ls-remote origin refs/heads/<head-branch>
   gh pr view <number> --json state,closed,headRefOid,baseRefOid,mergeStateStatus,changedFiles,additions,deletions,statusCheckRollup
   gh pr diff <number> --name-only || true
   ```

## Reporting language

Say that the PR is open but has no code delta, and that the original improvement is not valid as a merge target. Do not describe the empty commit as a code fix.
