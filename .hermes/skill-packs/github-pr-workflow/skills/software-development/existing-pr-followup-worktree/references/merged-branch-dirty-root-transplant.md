# Dirty root checkout on a merged PR branch

Use this note when the user's current dirty workspace is still checked out on a branch whose PR already merged or closed.

Rule:
- do not keep committing on that old branch
- do not treat the dirty workspace as an open-PR follow-up
- fast-forward local `main`
- create a brand-new worktree/branch from latest `origin/main`
- transplant the current meaningful root changes into that fresh worktree
- trust the fresh worktree's post-copy working-tree status as the real surviving payload

Why:
- the root checkout can stay dirty long after its old PR merged
- latest `origin/main` may already contain most of the apparent root diff
- after copying files into the fresh worktree, many paths can collapse to no-op immediately

Practical reporting pattern:
1. local `main` updated to latest `origin/main`
2. previous branch/PR checked and confirmed merged or otherwise obsolete
3. new PR contains only the surviving diff that still remains unique on top of latest `origin/main`

This avoids misreporting the stale root candidate set as though it were the new PR payload.
