# Iterative root residue after scoped cleanup

Use this when a `skills-jk` cleanup request asks for a narrow scoped PR, but after preserving/restoring one local residue bucket and attempting to fast-forward root `main`, another tracked `.hermes/skills/**` residue appears and blocks the fast-forward.

## Pattern

1. First classify the user-requested scoped files directly against latest `origin/main`.
   - For example: `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, `.hermes/memories/USER.md`.
   - If they are byte-identical to `origin/main`, do not create a fake scoped PR.

2. Promote only meaningful surviving residue to a fresh latest-main PR worktree.
   - Start from `origin/main`.
   - Apply tracked root deltas with `git apply --3way` instead of blindly copying over latest-main files.
   - Copy only genuinely new untracked support files.

3. After the PR branch is pushed, restore the same root paths and re-check root status before fast-forwarding.
   - Do not assume the first restore made root clean.
   - A dirty root checkout can reveal another `.hermes/skills/**` bucket after earlier files are restored.

4. If newly revealed residue belongs to the same skill-library cleanup scope:
   - Apply it to the existing follow-up PR worktree.
   - Commit with `git commit --amend --no-edit` when the PR is intended as one clean residue commit.
   - Push with `--force-with-lease`.
   - Update the PR body so the payload list and verification claims match the amended head.
   - Verify local HEAD equals `git ls-remote origin refs/heads/<branch>`.

5. Restore the newly handled root residue, then repeat the root status loop.
   - Only run `git merge --ff-only origin/main` once root is clean.
   - Then remove only stale merged/remote-gone worktrees; keep open PR worktrees.

## Verification commands

```bash
git status --short --branch
for p in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
  cmp -s "$p" <(git show "origin/main:$p") && echo "$p identical"
done

git -C "$PR_WT" diff --check
git -C "$PR_WT" grep -n '<<<<<<<\|=======\|>>>>>>>' -- <touched-files> || true
git -C "$PR_WT" rev-parse HEAD
git -C "$ROOT" ls-remote origin refs/heads/<branch>
```

## Reporting rule

Report three facts separately:

- the requested config/memory scoped files were identical to latest main and produced no scoped PR payload;
- the actual PR contains only the surviving skill-library residue;
- root `main` was fast-forwarded and stale merged worktrees/branches were removed, while open PR worktrees remain.
