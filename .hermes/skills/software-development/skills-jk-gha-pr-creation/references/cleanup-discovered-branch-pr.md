# Cleanup-discovered remote branch with no obvious open PR

Use this when `skills-jk` cleanup discovers a branch/worktree that is not stale because it has a meaningful diff versus latest `origin/main`, but there is not yet an obvious open PR in the current status output.

## Recommended flow

1. Verify the branch is pushed:
   ```bash
   local_sha=$(git rev-parse <branch>)
   remote_sha=$(git ls-remote origin refs/heads/<branch> | awk '{print $1}')
   test "$local_sha" = "$remote_sha"
   ```
2. Check for any existing PR before dispatching:
   ```bash
   env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,url,title,author
   ```
3. If no open PR exists and the branch is a real payload, dispatch `.github/workflows/create-pr.yml` rather than deleting the branch as cleanup residue.
4. After dispatch, verify by branch head rather than relying only on the workflow run list:
   ```bash
   env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,url,headRefOid,author,title
   ```
5. Keep the open-PR worktree. The cleanup target state is root `main` clean plus open PR worktrees only.

## Pitfall

A workflow run can complete and create the PR between two checks, or a previous dispatch can already have created it. If `gh pr list --head <branch> --state open` returns an open PR, do not dispatch again; verify and report the existing PR.
