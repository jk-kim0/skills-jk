# PR follow-up triage when GitHub state looks stale

Use this when the user says things like:
- `fix PR 444, 445`
- `PR 123 고쳐줘`
- `review 반영해줘`

and the PR may already have been refreshed recently.

## Problem pattern

A follow-up request does not guarantee:
- review comments exist
- code changes are still needed
- GitHub `mergeStateStatus` is trustworthy at that exact moment

Right after a push or PR refresh, GitHub can temporarily show `DIRTY`, `BEHIND`, `BLOCKED`, or `UNSTABLE` while the actual branch graph is already clean on latest `origin/main`.

## Triage sequence

For each PR:
1. Inspect review comments.
   - `gh api repos/<owner>/<repo>/pulls/<number>/comments --paginate`
2. Inspect issue/PR conversation comments.
   - `gh api repos/<owner>/<repo>/issues/<number>/comments --paginate`
3. Inspect checks.
   - `gh pr checks <number>`
4. Inspect PR metadata.
   - `gh pr view <number> --json mergeStateStatus,commits,headRefName,baseRefName,updatedAt,url`
5. Verify the actual remote head SHA.
   - `git ls-remote origin refs/heads/<head-branch>`
6. Open a fresh detached follow-up worktree directly from the PR branch tip.
7. Compare that checkout to latest `origin/main` with:
   - `git rev-parse HEAD`
   - `git rev-parse origin/main`
   - `git merge-base HEAD origin/main`
   - `git rev-list --left-right --count HEAD...origin/main`

## Interpretation

If all of the following are true:
- there are no actionable review comments
- the branch is already ahead of latest `origin/main` with merge-base equal to `origin/main`
- the remote branch SHA matches the local follow-up worktree HEAD
- checks are rerunning or settling after a recent push

then the needed follow-up may be PR metadata cleanup rather than code edits.

## Common metadata fix

A stacked PR can become stale after its parent merges.

Typical symptom:
- PR body still says `Base branch: <old-parent-branch>` or links a parent PR that has already landed
- actual branch is now cleanly based on `main`

Correct action:
- remove or rewrite the stale stacked-parent section in the PR body
- do not invent extra code edits just because the user said `fix PR`
- monitor the rerun checks briefly and report whether the PR is now clean or only waiting on CI

## Reporting guidance

When this pattern happens, tell the user explicitly:
- whether the branch was actually stale or not
- whether you changed code vs only PR metadata
- whether anything remains besides CI completion
