# Docs Contract Follow-up Implementation PR

Use this pattern when an Outbound Agent docs/OpenSpec PR records a contract or Product Owner decision and the user asks to perform the code changes implied by that PR.

## Pattern

1. Inspect the source docs PR first with `gh pr view <number> --json ...` and identify the active tasks/checklist items that became implementation requirements.
2. Update local `main` to `origin/main` before starting work.
3. Create a repo-local `.worktrees/<topic>` worktree from the docs PR head, not directly from stale local state.
4. Implement only the follow-up items implied by the docs PR unless the user explicitly broadens scope.
5. Add source-level regression tests that encode the contract. For auth/identity changes, prefer testing the linking/claim rule directly rather than only testing UI route behavior.
6. Mark only the implementation checklist items actually completed in the related `openspec/changes/**/tasks.md`; do not mark live smoke/deploy items complete unless they were run.
7. Rebase the implementation branch onto latest `origin/main` before push.
8. If the docs PR is still open, create a stacked implementation PR with `--base <docs-pr-head-branch>` so reviewers see only the code follow-up diff.
9. If the stacked PR reports dirty/unknown merge state because the docs PR branch is behind current `main`, update the docs PR branch to the rebased docs commit with `git push --force-with-lease origin <rebased-docs-commit>:<docs-branch>`, then re-check both PRs.
10. Report both PR URLs, the stacked base/head, changed file scope, targeted tests, and whether CI checks were created or skipped.

## Pitfalls

- Do not open the implementation PR directly against `main` when the docs PR is still open unless the user asks for a non-stacked PR; it will mix docs and code diffs.
- Do not mark environment/live smoke tasks complete from local unit tests.
- Do not treat a transient Node/runtime failure as a code failure before retrying with the repo-supported Node major.
- Do not leave `.agents/tmp/` or other repo-local runtime temp files untracked after writing PR bodies.