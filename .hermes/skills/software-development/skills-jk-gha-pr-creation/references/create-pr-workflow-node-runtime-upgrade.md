# create-pr.yml Node runtime upgrade nuance

When upgrading `skills-jk` workflow action majors for GitHub's JavaScript runtime deprecation warnings, `create-pr.yml` is special because it is also the repository-standard mechanism used to open the PR.

Observed pattern:
- A branch can correctly update `.github/workflows/create-pr.yml` from `actions/checkout@v4` to `actions/checkout@v6.0.2`.
- The PR-creation run dispatched to open that very PR still uses the default branch version of `create-pr.yml`, because workflow_dispatch resolves the workflow file from the default branch for that dispatch.
- Therefore the PR-creation run itself may still emit the old Node.js runtime deprecation warning one last time.
- This is not evidence that the branch failed to upgrade the runtime; after merge, subsequent `create-pr.yml` dispatches use the upgraded action.

Recommended verification:
1. Confirm the candidate action tag uses Node 24:
   ```bash
   tmp=$(mktemp -d)
   git clone --depth 1 --branch v6.0.2 https://github.com/actions/checkout.git "$tmp/checkout"
   grep -n "using:" "$tmp/checkout/action.yml"
   rm -rf "$tmp"
   ```
2. Ensure no deprecated first-party action refs remain:
   ```bash
   grep -R "actions/checkout@v4\|actions/setup-node@v4\|actions/upload-artifact@v4" .github/workflows || true
   ```
3. Run static validation:
   ```bash
   git diff --check
   actionlint .github/workflows/*.yml
   ```
4. After push, verify the remote branch head directly:
   ```bash
   git rev-parse HEAD
   git ls-remote origin refs/heads/<branch>
   ```
5. In the final report, explicitly distinguish:
   - the PR-creation run used the old default-branch workflow one last time
   - the PR payload updates future workflow runs after merge

Actionlint note:
- If `actionlint` surfaces a small pre-existing shellcheck issue in the same workflow file, it is acceptable to include a narrow behavior-preserving fix, such as replacing string-concatenated CLI arguments with a quoted bash array.
- Do not use this as permission to bundle unrelated workflow behavior changes.
