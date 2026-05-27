# Final cleanup: merge races and regenerated Hermes residue

Use this during repeated `skills-jk` local sweep / workspace cleanup sessions when PRs are being created while the user or automation may merge them quickly.

## Signal pattern

- A scoped PR branch is pushed and a bot PR is created.
- During follow-up amendment/rebase/body-edit work, `gh pr view <n>` shows the PR is already `MERGED`.
- `git ls-remote origin refs/heads/<branch>` may be empty because GitHub deleted the head branch after merge.
- Rebase output may say a commit was skipped as already applied to `origin/main`.
- If the agent force-pushes the same branch name again, GitHub may recreate the remote branch, but the old PR object remains `MERGED` and still reports the stale pre-merge `headRefOid` / file list.

## Correct response

1. Before amending or force-pushing an existing cleanup PR branch, re-check the PR state:

```bash
env -u GITHUB_TOKEN gh pr view <pr> --json state,mergedAt,headRefName,headRefOid,url
```

2. If the PR is `MERGED`, stop updating that branch as a PR target.
3. Fetch latest `origin/main` and create a new latest-main branch/worktree for the remaining diff.
4. Copy only the still-unmerged residue into the new worktree.
5. Commit, push, and create a new bot PR via `create-pr.yml`.
6. Delete any accidentally recreated remote branch for the merged PR after the replacement PR exists:

```bash
git push origin --delete <old-merged-pr-branch>
```

7. Report the merged PR and the replacement PR as separate facts.

## Regenerated residue during verification

`skills-jk` verification itself can re-dirty root `main`:

- invoking skills/tooling can regenerate `.hermes/skills/**` bundled files;
- profile-aware Hermes runs can recreate `.hermes/profiles/**`;
- profile setup can reapply `.gitignore`, `.hermes/config.yaml`, or `AGENTS.md` changes that are already preserved in an open PR.

After every final verification pass, run one last root cleanup check:

```bash
git status --short --branch
```

If only generated/runtime residue remains and it is already preserved in a PR or explicitly excluded, restore tracked files first and remove only untracked profile runtime state:

```bash
git restore -- .hermes/skills .gitignore .hermes/config.yaml AGENTS.md .hermes/profiles 2>/dev/null || true
# Do NOT rm -rf .hermes/profiles after profile-as-code lands; durable profile files are tracked.
git clean -fd -- .hermes/profiles 2>/dev/null || true
```

Important transition rule: once `.hermes/profiles/README.md`, profile `config.yaml`, or profile `SOUL.md` files are tracked on `origin/main`, treating the whole directory as runtime residue will create tracked deletions. If cleanup accidentally deletes tracked profile files, immediately restore them from `origin/main` before reporting root clean.

Then re-run `git status --short --branch` and report root clean only if it is actually clean.

## Pitfall

Do not keep using `gh pr view` metadata as proof that a re-pushed branch updated a merged PR. For merge races, the remote ref and PR object can diverge: the branch exists again, but the PR is still merged and stale. The correct fix is a new PR for the remaining diff, not another force-push to the old branch.
