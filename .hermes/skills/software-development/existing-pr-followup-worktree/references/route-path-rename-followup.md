# Route/path rename follow-up on an existing PR

Use this when a user asks to adjust an already-open PR so a route, URI segment, or route directory name changes, without opening a new PR.

## Pattern

1. Verify the PR is open and identify `headRefName`, `baseRefName`, current head SHA, files, and merge state:
   ```bash
   env -u GITHUB_TOKEN gh pr view <PR> --repo <owner/repo> \
     --json number,state,title,headRefName,baseRefName,headRefOid,mergeStateStatus,url,files
   ```
2. If the PR branch is already checked out in another worktree, create a temporary follow-up branch from `origin/<headRefName>` in a fresh worktree. Push back explicitly to `refs/heads/<headRefName>` at the end.
3. Move route directories with `git mv`, preserving Next.js App Router structure. For localized wrappers, move every locale path together, for example:
   - `src/app/archived/<old>/...` -> `src/app/archived/<new>/...`
   - `src/app/{en,ko,ja}/archived/<old>/...` -> `src/app/{en,ko,ja}/archived/<new>/...`
4. Replace route-string references narrowly in affected source/docs/tests:
   - imports such as `src/app/.../<old>/page`
   - `generateMetadata` pathname defaults
   - canonical/alternate URLs
   - README/provenance docs inside the moved route family
   - structure/source tests asserting the old route
5. Verify no stale route string remains:
   ```bash
   rg 'archived/<old>|/<old-route-segment>' src docs tests
   ```
6. Run the narrowest route/source test that imports the moved page modules.
7. Rebase onto latest `origin/main` before pushing, then rerun the stale-string grep and narrow test.
8. Push the temporary branch back to the PR head branch explicitly:
   ```bash
   git push --force-with-lease origin HEAD:refs/heads/<headRefName>
   ```
9. Verify local and remote head SHA match with `git ls-remote` before trusting PR metadata.
10. Inspect and update the PR body if it still names the old route or file path. This is easy to miss after a mechanical rename.
11. Report current checks without waiting passively unless asked to watch them.

## Pitfalls

- A successful file rename can leave stale route strings in metadata, alternates, source tests, and the PR body.
- `gh pr checks` may exit non-zero while checks are merely pending; use the output to report current status, not as proof of failure.
- After force-push, `mergeStateStatus=BLOCKED` can simply mean required checks are pending. Verify ancestry/head SHA before treating it as a conflict.
