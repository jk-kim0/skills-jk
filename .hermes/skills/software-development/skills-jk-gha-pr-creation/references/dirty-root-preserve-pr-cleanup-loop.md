# skills-jk cleanup quirks for bot-authored preservation PRs

Use this note only after the generic cleanup procedure has been selected from `git-worktree-safety-pack`.
This file records `skills-jk`-specific quirks that are not owned by the generic cleanup references.

## Canonical owner map

| Topic keyword | Canonical owner |
| --- | --- |
| `dirty-root`, `behind-main`, `stale-deletion-hunks`, `workspace-sweep` | `git-worktree-safety-pack/references/dirty-root-behind-main-preservation.md` and `git-worktree-safety-pack/references/repeated-cleanup-merged-preservation-pr-stale-deletions.md` |
| `open-pr-followup`, `duplicate-payload`, `dirty-pr-less-worktree` | `git-worktree-safety-pack/references/open-pr-cleanup-repeat-and-preservation.md` and `git-worktree-safety-pack/references/cleanup-preserve-dirty-payload-into-open-pr.md` |
| `final-root-clean`, `merged-preservation-pr`, `regenerated-residue` | `git-worktree-safety-pack/references/final-sweep-after-preserve-pr.md` and `git-worktree-safety-pack/references/merged-preservation-pr-branch-refusal.md` |
| `workflow-dispatch`, `bot-pr`, `body-input` | `git-worktree-safety-pack/references/workflow-dispatch-pr-creation-verification.md` and this skill's `create-pr.yml` procedure |

Do not recreate one incident reference per cleanup session.
Add new generic rules to the owning `git-worktree-safety-pack` reference, and add only repo-specific `skills-jk` workflow quirks here.

## Repo-specific quirks

- `skills-jk` opens normal review PRs through `.github/workflows/create-pr.yml`; do not commit from root `main` and do not use direct `gh pr create` for normal review PRs.
- `create-pr.yml` runs can appear under `headBranch: main` because the workflow is dispatched from the default branch.
  Verify the remote branch head and `gh pr list --head <branch>` instead of relying on `gh run list --branch <feature-branch>`.
- For PR bodies, pass the Markdown body through the workflow's defined `body` input.
  Do not invent `body-file` unless the workflow defines that input.
- Fresh docs/skill PRs may show `mergeStateStatus: BLOCKED` with no attached checks.
  Treat this as unconfirmed policy/check state until a check rollup, `gh pr checks`, or workflow run proves a current-head failure.
- If the named scoped files, such as `.hermes/config.yaml` or `.hermes/memories/*.md`, are byte-identical to latest `origin/main`, do not create a fake scoped PR.
  Preserve only the surviving skill/reference residue, and say which scoped files collapsed to no-op.
- Generated `.hermes/skills/**` residue can be stale bundle churn.
  Exclude manifest churn, deleted support files, or old-bundle downgrades unless representative diffs prove the change is authored and current.

## Verification add-ons

After the generic cleanup checks pass, verify the repo-specific PR path:

```bash
branch=$(git branch --show-current)
git rev-parse HEAD
git ls-remote origin "refs/heads/$branch"
env -u GITHUB_TOKEN gh pr list --head "$branch" --state open --json number,url,title,author,headRefOid
git diff --name-only origin/main...HEAD | sort
```

Final reports for `skills-jk` cleanup should distinguish:

- root `main` alignment and clean status;
- the bot-authored PR URL, head SHA, and payload file list;
- scoped files that collapsed to no-op against latest `origin/main`;
- stale generated residue excluded from the PR;
- intentionally retained open-PR worktrees and deleted merged/stale worktrees.
