# skills-jk repeated cleanup after follow-up PR creation

Use this reference when the user repeats `main branch 업데이트하고, 로컬 변경사항 파악하여 PR 작성해줘 ... workspace 정리해줘` after a previous sweep already created or merged a follow-up PR.

## Observed session pattern

1. First sweep created/updated a broad Hermes config/memory/skill PR.
2. The PR was merged quickly and the remote branch was deleted.
3. A follow-up cleanup request arrived while local root or an old worktree still held skill-library changes created during the cleanup itself.
4. The user-named scoped files (`.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, `.hermes/memories/USER.md`) were already identical to latest `origin/main`.
5. A different local skill-library diff still survived and deserved its own narrow PR.

## Decision rule

Treat the user's named scope as the first-class target, but do not ignore other meaningful local skill-library changes that the current session itself produced.

Order:

```bash
git fetch origin --prune
git status --short
for f in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
  cmp -s "$f" <(git show origin/main:"$f") && echo "scoped no-op $f" || echo "scoped differs $f"
done
```

- If the named scope differs, create/update the scoped PR first.
- If the named scope is a no-op but other tracked/untracked skill-library files remain, classify them separately and create a narrow PR for only those surviving changes.
- In the final report, say explicitly that the requested config/memory subset was already absorbed, then list the separate PR payload.

## Safe narrow-PR sequence

```bash
ROOT=/path/to/skills-jk
BR=docs/<class-level-topic>-<date>
WT="$ROOT/.worktrees/<flat-topic>"

git -C "$ROOT" fetch origin --prune
git -C "$ROOT" worktree add -b "$BR" "$WT" origin/main

# Copy only the surviving meaningful files, not the whole dirty root.
cp -p "$ROOT/.hermes/skills/.../SKILL.md" "$WT/.hermes/skills/.../SKILL.md"
cp -p "$ROOT/.hermes/skills/.../references/<note>.md" "$WT/.hermes/skills/.../references/<note>.md"

git -C "$WT" status --short
git -C "$WT" diff --name-status
git -C "$WT" add <surviving-files>
git -C "$WT" commit -F /tmp/commit-message.txt
git -C "$WT" push -u origin HEAD
```

Then create the PR with the repository's `create-pr.yml` workflow, verify the bot-authored PR object, and clean root back to `origin/main` after verifying the remote branch head.

## Reporting

Report these separately:

1. `main` is aligned to `origin/main` and root is clean.
2. Requested config/memory files either produced a PR or were already identical to latest main.
3. Any additional PR contains only the surviving non-scoped skill-library diff.
4. Temporary PR worktrees/local branches were removed while the remote PR branch remains available for review.
