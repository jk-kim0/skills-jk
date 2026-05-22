# Temporary draft worktree cleanup after existing-PR consolidation

Use this note when a skill-library or cleanup session starts on a temporary draft branch/worktree, then later discovers an existing open PR that already covers the same umbrella skill or review scope.

## Pattern

1. Treat the existing open PR branch as the authoritative review surface when the scope overlaps.
2. Reapply or port the useful draft changes into that PR branch instead of opening a second PR.
3. Verify the PR branch after push:
   - local HEAD equals `git ls-remote origin refs/heads/<branch>`
   - PR payload includes the intended changed/added files
   - PR body mentions the new scope when needed
4. Only after that verification, remove the abandoned local draft worktree and branch.

## Why

Leaving the abandoned draft worktree/branch behind makes later `workspace 정리` or skill-library review sessions harder: it looks like another possible source of truth even though the actual payload already moved to the open PR.

## Pitfalls

- Do not delete the draft branch before confirming the existing PR branch contains the transferred file changes and support files.
- If the draft branch was pushed or has a PR, inspect that PR before cleanup; this note only covers local abandoned draft branches/worktrees.
- Report cleanup as local workspace hygiene, not as part of the PR payload.
