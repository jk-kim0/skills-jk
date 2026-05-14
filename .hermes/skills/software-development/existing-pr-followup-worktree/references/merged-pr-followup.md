When a user references a PR number from earlier work, confirm the PR state before deciding branch reuse.

Rules:
- OPEN PR: use a fresh worktree on the existing PR branch and update that PR.
- MERGED or CLOSED PR: do not revive the old branch by default.
- If the user asks to supplement docs or continue work that originally landed in a merged PR, start from latest origin/main in a fresh worktree, with a fresh branch and a fresh PR.

Why:
- once the original PR is merged, the active review target is gone
- trying to keep working on the old branch creates misleading ancestry and stale PR assumptions
- the safer default is a clean follow-up PR that references the merged PR in the body
