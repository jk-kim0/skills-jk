# Local skill follow-up preservation during main update

Use this reference during repo-local `main 업데이트` / `workspace 정리` sweeps when the root checkout is on `main`, behind `origin/main`, and contains meaningful `.hermes/skills/**` or repo-managed guidance changes.

## Pattern

1. Do not commit the dirty payload directly to `main` as final state.
2. Inspect the dirty payload and classify obvious runtime/cache files separately from authored skill/reference/script changes.
3. Create a fresh preservation branch from the dirty root state, stage only the meaningful repo-managed guidance payload, and commit it.
4. Rebase that preservation branch onto the freshly fetched `origin/main` before pushing or creating a PR.
5. Resolve rebase conflicts in skill entrypoints/reference registries by preserving both valid main-side additions and valid local additions; do not take one side wholesale.
6. Run `git diff --check` after conflict resolution. For conflict-marker searches, use anchored marker patterns and ignore known existing documentation separator lines that are not in changed files.
7. Push the preservation branch and create the PR through the repository-preferred PR mechanism. In `skills-jk`, `.github/workflows/create-pr.yml` is dispatched on `main`, so verify the workflow run by run id or recent `create-pr.yml` runs and then re-query `gh pr list --head <branch>`; do not assume `gh run list --branch <feature-branch>` will show the dispatch run.
8. Switch the root checkout back to `main` and fast-forward it to `origin/main` only after the dirty payload is safely preserved.
9. Re-run branch/worktree cleanup after the PR is created.

## Stale branch cleanup after preservation

A merged or closed local branch can still show unique local commits or a non-empty two-dot diff against latest `origin/main` after upstream has moved. Before deleting it:

- Check whether a newer open PR branch now represents the same or richer payload under a different branch name.
- Compare the stale local branch against likely successor open PR branches with `git diff <old>..<new>` and inspect file scope, not only PR state.
- If the successor open PR contains the relevant payload in a newer form, delete the old clean worktree/branch as superseded residue.
- If no successor PR or current worktree preserves the unique payload, promote it to a fresh latest-main branch/PR instead of deleting it.

## Useful labels

- `root main dirty payload preserved on latest-main PR branch`
- `skill reference registry conflict resolved by preserving both valid additions`
- `merged/closed local branch superseded by newer open follow-up PR`
