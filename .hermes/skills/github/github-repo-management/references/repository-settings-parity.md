# Repository settings parity workflow

Use this when the user asks to make one GitHub repository's settings match a reference repository and to document the change.

## Workflow

1. Read target and reference settings before writing:

```bash
for repo in querypie/reference-repo querypie/target-repo; do
  gh repo view "$repo" --json \
    nameWithOwner,visibility,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled,hasProjectsEnabled,hasDiscussionsEnabled,deleteBranchOnMerge,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,repositoryTopics
  gh api "repos/$repo" --jq '{allow_auto_merge,allow_merge_commit,allow_rebase_merge,allow_squash_merge,delete_branch_on_merge,squash_merge_commit_title,squash_merge_commit_message,has_projects,has_wiki,has_issues,security_and_analysis}'
  gh api "repos/$repo/rulesets" --jq '.[] | {id,name,target,enforcement}'
done
```

2. Fetch full ruleset details from the reference repo; list endpoints often omit rule bodies:

```bash
gh api repos/querypie/reference-repo/rulesets/<id> --jq '{id,name,target,enforcement,conditions,bypass_actors,rules}'
```

3. Patch ordinary repository settings separately from `security_and_analysis`. This prevents a security-setting failure from blocking safe settings such as auto-merge, delete-branch-on-merge, or Projects disabled.

4. If secret scanning parity fails with `Secret scanning can only be enabled on repos where Advanced Security is enabled`, leave the target's security settings unchanged and document the prerequisite. Do not retry the same combined payload.

5. For required status checks, copy the reference ruleset shape but choose the target repository's actual check context. If the reference uses an aggregate check such as `CI result` that does not exist in the target, use an existing target check and document the deliberate difference.

6. Create or update a docs file in the target repository, commonly `docs/github-repository-settings.md`, with:
   - reference repo and target repo
   - changed repository settings table
   - branch/ruleset protection details
   - required status check context and any reference-target differences
   - unapplied settings and exact reason
   - commands for re-checking settings later

7. Open a documentation PR from a fresh latest-main worktree. If the new ruleset makes the PR blocked, verify whether the required check has actually attached. If the branch is behind current `origin/main`, rebase first, then let/trigger the target workflow on the new head SHA.

## Notes

- Repository rulesets can be created before the documentation PR, but doing so immediately enforces required checks on that PR too.
- `workflow_dispatch` runs may not always satisfy a PR-required check if the check context/name differs from the pull_request check run. Prefer the natural `pull_request` run when it appears; use manual dispatch only as a temporary nudge and verify the PR `statusCheckRollup` afterward.
