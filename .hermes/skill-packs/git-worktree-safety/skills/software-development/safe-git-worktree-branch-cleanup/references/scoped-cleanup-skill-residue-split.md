# Scoped cleanup when only skill-library residue remains

Use this note when a user asks for a scoped cleanup/update such as `.hermes/config.yaml` or memory files, but the requested scoped files are already identical to latest `origin/main` and the session has produced unrelated skill-library changes.

## Rule

Do not claim the scoped cleanup changed anything, and do not bundle unrelated `.hermes/skills/**` residue into the scoped PR.

Instead:

1. Fast-forward root `main` to latest `origin/main` and verify the requested scoped files against `origin/main`.
2. If the requested scoped files are identical, report that there is no scoped payload.
3. Restore the unrelated skill residue from the root checkout before declaring the root clean.
4. If the skill residue is valuable, split it into a narrow follow-up PR from a fresh worktree/branch.
5. Keep merged stale PR worktrees/branches cleanup separate from the follow-up skill PR payload.

## Verification

- `git status --short --branch` at root is clean after restoring/splitting residue.
- Each requested scoped file is `cmp`-identical to `git show origin/main:<path>`.
- Any follow-up skill PR contains only the intended skill files/references.
- Open PR worktrees remain; merged/remote-gone worktrees are removed safely.
