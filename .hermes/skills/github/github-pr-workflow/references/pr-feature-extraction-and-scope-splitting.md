# PR feature extraction and scope splitting

Use this reference when a feature or schema/model change was accidentally bundled into an active PR and the user asks to split it into a separate PR.

## Pattern

1. Inspect the active PR and confirm the mixed scope before editing.
2. Create a fresh worktree/branch from the latest `origin/main` for the extracted feature.
3. Reapply only the extracted feature onto that main-based branch.
4. If the feature changes a canonical content/schema field, remove superseded duplicate fields in the extracted PR rather than keeping both representations.
5. Add focused tests that prove the extracted feature behavior on the main-based branch.
6. Push and open the separate PR.
7. Return to the original PR branch and remove the extracted feature completely, leaving only the original PR scope.
8. Verify the original PR diff has no residue from the extracted feature.
9. Push the original PR branch and report both PR URLs and current check status.

## Residue checks

- Use source-tree checks for symbols that should disappear from the original PR, for example `git grep -n "FeatureType|featureHelper" -- ':!node_modules'`.
- Use PR diff checks for review scope, for example `gh pr diff <pr> | grep -n "FeatureType|featureHelper"`.
- When checking that a field was removed from the extracted PR, distinguish added lines from removed lines. `grep "sourceLabel"` can match `-sourceLabel` deletion lines and cause a false alarm; use `grep '^+sourceLabel:'` to detect fields that are still being added.
- Also check the original PR body for stale mentions of the extracted feature when the body previously described the mixed scope.

## Verification

Run the lightest focused checks for both branches:

- extracted PR: tests/lint for the feature implementation and schema/content migration
- original PR: tests/lint for the remaining original scope plus grep/diff residue checks for the extracted symbols

Avoid passive waiting after push unless the user explicitly asks to watch checks; report pending checks with their current state.