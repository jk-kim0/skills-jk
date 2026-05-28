When a user references a PR number from earlier work, confirm the PR state before deciding branch reuse.

Rules:
- OPEN PR: use a fresh worktree on the existing PR branch and update that PR.
- MERGED or CLOSED PR: do not revive the old branch by default.
- If the user asks to supplement docs or continue work that originally landed in a merged PR, start from latest origin/main in a fresh worktree, with a fresh branch and a fresh PR.

Additional merged-root-dirty follow-up rule:
- the current dirty checkout may still be sitting on the old merged branch even after the prior PR has landed
- in that case, treat the old branch only as the source of current local file state, not as the branch to continue using
- first refresh refs and update local main to latest origin/main
- then create a brand-new worktree/branch from latest origin/main
- transplant the meaningful local files into that fresh worktree
- trust the post-copy collapsed diff there as the real PR payload, because latest main may already contain much of what looked dirty in the stale checkout

Reporting rule:
- report these as separate facts:
  1. local main was updated
  2. the previous PR/branch was already merged or obsolete
  3. the new PR contains only the surviving diff still unique on top of latest origin/main

Why:
- once the original PR is merged, the active review target is gone
- trying to keep working on the old branch creates misleading ancestry and stale PR assumptions
- the safer default is a clean follow-up PR that references the merged PR in the body
- separating root dirty state from the fresh latest-main PR payload prevents overstating what the new PR actually contains
