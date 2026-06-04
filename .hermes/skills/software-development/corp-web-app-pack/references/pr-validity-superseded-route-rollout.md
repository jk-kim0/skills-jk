# PR Validity Review for Superseded Route/Public-Rollout PRs

Use this reference when reviewing whether an old corp-web-app PR is still valid, especially for public route rollout, preview route removal, or route-group migration work.

## Pattern

1. Fetch both latest main and the PR head before judging validity:

```bash
git fetch origin main pull/<PR_NUMBER>/head:refs/remotes/origin/pr-<PR_NUMBER> --prune
```

2. Compare age and unique work:

```bash
git merge-base origin/main origin/pr-<PR_NUMBER>
git rev-list --left-right --count origin/main...origin/pr-<PR_NUMBER>
git diff --stat origin/main...origin/pr-<PR_NUMBER>
git diff --name-status origin/main...origin/pr-<PR_NUMBER>
```

3. Check whether the PR goal is already implemented on main under a different route group or newer module path.
   - In App Router, route groups such as `(tailwind)` and `(legacy)` are URL-transparent.
   - Do not conclude that a public URL is missing just because `src/app/[locale]/...` is absent; also inspect `src/app/(tailwind)/[locale]/...` and `src/app/(legacy)/[locale]/...`.
   - For resource/publication migrations, check for current `src/lib/resources/**` and `src/lib/publications/**` replacements before treating older `src/lib/repo-content/**` imports as valid.

4. Reproduce mergeability locally against fetched `origin/main` instead of relying only on GitHub's cached `mergeStateStatus`:

```bash
tmp=$(mktemp -d)
git worktree add --detach "$tmp" origin/main
(
  cd "$tmp"
  git merge --no-commit --no-ff origin/pr-<PR_NUMBER>
  git status --short
)
git worktree remove --force "$tmp"
```

5. Inspect current main tests and recent merged PRs for superseding evidence.
   - If main already has a stronger route/publication test for the same behavior, cite that path.
   - Use merged PR history to identify the replacement PR when possible.

## Decision Signals

Treat an old PR as obsolete/superseded when most of these are true:

- The stated goal is already implemented on `origin/main`.
- Main uses newer canonical locations such as `src/app/(tailwind)/**` or `src/lib/resources/**` while the PR adds older ungrouped/legacy paths.
- The PR is many commits behind main with only a small unique diff.
- A local merge into `origin/main` produces conflicts or duplicate URL ownership.
- Current main tests already enforce the intended behavior.

## Reporting Shape

For the user, keep the conclusion direct:

- Verdict: valid / invalid / obsolete / needs rework.
- Evidence: current PR state, behind/ahead count, local merge result, current main files/tests that supersede it.
- Recommendation: close, rebase/rewrite, or keep open.

Do not close a PR unless the user explicitly asks to close it.