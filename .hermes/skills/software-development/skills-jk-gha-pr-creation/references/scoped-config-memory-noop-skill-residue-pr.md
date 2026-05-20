# Scoped config/memory no-op with surviving skill residue

Use this note when the user asks to update `main`, inspect local changes, create a PR for a scoped Hermes subset such as `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, and `.hermes/memories/USER.md`, and also asks for repo-local workspace cleanup.

## Signal pattern

- Root checkout is `skills-jk` on `main` and behind `origin/main`.
- The user explicitly names `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, and `.hermes/memories/USER.md` as expected PR payload.
- Direct comparison against latest `origin/main` shows the scoped files have no surviving diff.
- Root still has many `.hermes/skills/**` local changes, often mixed between:
  - meaningful SKILL.md additions and new `references/*.md` files;
  - stale bundled-skill churn such as `.hermes/skills/.bundled_manifest`, broad hash changes, generated rollback/deletion noise, or removed support files.
- There may also be a clean stale worktree whose remote branch is gone and whose PR is already merged.

## Safe handling

1. Prove the scoped files are no-ops against latest main before creating a PR:

```bash
git fetch origin --prune
git diff --name-status origin/main -- .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md
```

If this is empty, do not manufacture a config/memory PR.

2. Inspect the broader local skill changes, but separate meaningful learnings from generated residue:

```bash
git diff --stat -- .hermes/skills
git diff -- .hermes/skills/.bundled_manifest | sed -n '1,120p'
git diff -- <representative SKILL.md paths> | sed -n '1,200p'
git ls-files --others --exclude-standard
```

3. Create a fresh latest-main worktree for only the meaningful skill/reference payload:

```bash
git worktree add -b docs/<topic> .worktrees/<topic> origin/main
git diff -- <selected tracked skill files> > /tmp/<topic>.patch
git -C .worktrees/<topic> apply --3way /tmp/<topic>.patch
cp <selected new reference files> .worktrees/<topic>/<same-path>
```

4. Stage only the selected payload. Exclude broad `.bundled_manifest` hash churn and generated rollback/deletion residue unless the user explicitly asks for a bundled-skill sync PR.

5. In the PR body, state explicitly that the named scoped config/memory files were checked and had no surviving diff, while the PR contains the separate surviving skill/reference residue.

6. After the branch is pushed and PR-created, restore the same local skill residue in root and fast-forward root `main` so the repo ends clean.

7. If a stale worktree/branch is clean, tracks a gone upstream, and `gh pr list --head <branch> --state all` shows the PR is merged, remove that worktree and delete the local branch after verifying it has no diff versus latest `origin/main`.

## Pitfalls

- Do not claim that a scoped config/memory PR was created when those files have no diff.
- Do not silently discard meaningful untracked skill reference files; classify and either include them in the skill-residue PR or explain why they were excluded.
- Do not include `.hermes/skills/.bundled_manifest` just because skill files changed. In local sweeps it often reflects generated churn rather than intentional review scope.
- Do not let root `main` stay dirty after opening the residue PR; restore or remove the copied local files, pull `main --ff-only`, and verify `git status --short --branch` is clean.
