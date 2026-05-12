---
name: github-pr-workflow
description: Full pull request lifecycle — create branches, commit changes, open PRs, monitor CI status, auto-fix failures, and merge. Works with gh CLI or falls back to git + GitHub REST API via curl.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge]
    related_skills: [github-auth, github-code-review]
---

# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle. Each section shows the `gh` way first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

This part is pure `git` — identical either way:

```bash
# Make sure you're up to date against the REMOTE default branch
# Prefer branching from origin/main, not from whatever local branch is checked out.
git fetch origin --prune
git checkout main && git pull origin main

# Create and switch to a new branch from the latest remote main tip
git checkout -b feat/add-user-authentication origin/main
```

Important safety rule:
- Do NOT create a new PR branch from a previously used feature/fix branch, even if that branch's PR was already merged.
- If the previous PR was squash-merged or otherwise rewritten on GitHub, the old local commit SHA may not exist on `main`, so GitHub can show that old commit again in the new PR even though the content was already merged.
- Always branch from `origin/main` (or the PR base branch) for new independent work.

Recommended verification before committing:

```bash
# Confirm the new branch is based on the current remote main
BASE=$(git merge-base HEAD origin/main)
echo "$BASE"
git rev-parse origin/main

# These should match for a fresh branch with no new commits yet
```

If they do not match, stop and inspect the branch ancestry before proceeding.

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

## 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

## 3. Pushing and Creating a PR

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body-file /tmp/pr-body.md
```

Prepare `/tmp/pr-body.md` first (recommended whenever the PR body contains backticks, shell metacharacters, or multiple paragraphs):

```bash
cat >/tmp/pr-body.md <<'EOF'
## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42
EOF
```

Small one-line bodies can still use `--body "..."`, but `--body-file` is safer and avoids command substitution / shell quoting issues when the text includes Markdown code spans like `` `src/file.ts` ``.

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

### Recovering a PR That Accidentally Includes Old Merged Commits

Symptom:
- A new PR unexpectedly shows commits from an older already-merged branch.
- This often happens when the new branch was created from a stale local branch instead of `origin/main`.

Fast diagnosis:

```bash
git fetch origin --prune
git log --oneline --decorate --graph --max-count=10
git merge-base origin/main HEAD
git rev-list --oneline origin/main..HEAD
```

If `origin/main..HEAD` includes an old unrelated commit, rewrite the branch so only the intended commit(s) remain.

Single-extra-parent case (common):

```bash
# Example: branch contains OLD_COMMIT -> YOUR_COMMIT, and OLD_COMMIT should not be in the PR
git rebase --onto origin/main OLD_COMMIT <your-branch>

# Resolve conflicts if needed, then continue without opening an editor
GIT_EDITOR=true git rebase --continue

# Update the existing PR branch safely
git push --force-with-lease origin HEAD:<your-branch>
```

After force-pushing, verify that the PR now contains only the intended commits:

```bash
git rev-list --oneline origin/main..HEAD
gh pr view <pr-number> --json commits,files,headRefName,url
```

This is especially important when the accidentally included old branch was merged via squash/rebase on GitHub, because the old local SHA may not be an ancestor of `origin/main` even when its content is already present there.

## 4. Monitoring CI Status

### Check CI Status

User-specific execution rule for fast repo work:
- Do not sit waiting on CI unless the user explicitly asks you to wait for completion.
- Preferred behavior is: trigger/push the updated branch, verify that fresh workflow runs attached to the new head SHA, report the current in-progress status, and return control immediately.
- Use watch/poll loops only when the user explicitly asks to keep watching until completion.
- For multiple PRs at once, use the bundled script `scripts/watch-multiple-pr-checks.py` instead of serial manual polling.

Important zero-check diagnostic:
- If `gh pr checks` says `no checks reported on the '<branch>' branch` and `gh run list --branch <branch>` is also empty, do not immediately assume GitHub is lagging or broken.
- First inspect whether the repository actually has any `pull_request`, `pull_request_target`, `push`, or branch-specific workflows that should run for that PR branch.
- Practical checks:
  - inspect `.github/workflows/*.yml`
  - run `env -u GITHUB_TOKEN gh workflow list`
  - read the relevant workflow triggers (`on:` blocks)
- Some repositories only have `workflow_dispatch`, comment-driven, or repository-dispatch automations. In those repos, a rebased/pushed PR can legitimately have zero attached checks.
- In that case, report explicitly that the PR is rebased/updated successfully but the repo has no automatic PR CI for that branch/event, so there is no failing check to fix.

**With gh:**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s) -- only if the user asked you to wait
gh pr checks --watch
```

**With git + curl:**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### Poll Until Complete (git + curl)

Only use this completion-wait loop when the user explicitly wants you to wait for green/red. Otherwise, do a one-shot status check, report the active run IDs/states, and return control.

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

### Poll multiple PRs to terminal state with `gh`

When a stacked PR chain or rollout requires watching several PRs together, `gh pr checks --watch` is awkward because it watches only one PR at a time. Use JSON polling so you can stop on the first failure or when all PRs are done.

Bundled helper:

```bash
python3 ~/.hermes/skills/github/github-pr-workflow/scripts/watch-multiple-pr-checks.py querypie/corp-web-japan 420 421 423 403
```

Important path caveat:
- do not assume `~/.hermes/skills/...` exists on this machine
- the actual skill install path can differ in git-installed or repo-local Hermes setups
- before invoking the helper by filesystem path, verify where the skill lives, or open the linked script from `skill_view(name='github-pr-workflow', file_path='scripts/watch-multiple-pr-checks.py')`
- if the script path is unavailable or uncertain, fall back to `env -u GITHUB_TOKEN gh pr checks <pr-number> --watch` for a single PR, or poll multiple PRs with repeated `gh pr checks`/`gh pr view` instead of blocking on a broken hard-coded path

What it does:
- polls each PR every 15 seconds
- prints `check-name=STATE` snapshots per PR
- exits `0` when all checks are terminal-success
- exits `1` on the first failed terminal state
- exits `2` on timeout or when check metadata cannot be fetched yet

Why `env -u GITHUB_TOKEN gh ...` appears in the helper:
- in some Hermes shells, an inherited `GITHUB_TOKEN` can override the user's normal `gh auth` context
- if `gh auth status` is already correct but `gh` API calls behave inconsistently, retry with `env -u GITHUB_TOKEN gh ...` before assuming GitHub itself is failing

## 5. Auto-Fixing CI Failures

When CI fails, diagnose and fix. This loop works with either auth method.

### Step 1: Get Failure Details

**With gh:**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### Step 3: Verify

Re-check CI status using the commands from Section 4 above.

### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

## 6. Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. Complete Workflow Example

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see Section 4)

# 8. Merge when green (see Section 6)
```

## Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` |
| Add comment | `gh pr comment N --body-file /tmp/comment.md` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |

## Practical CLI pitfalls

1. In Hermes terminal environments, split `git` workflow steps into smaller commands when the runner misclassifies a long chained command as a watch/server process.
   - A combined command such as `git fetch && git rebase && git add && git commit ...` can be rejected before execution with a false long-lived-process warning.
   - Safer pattern:
     ```bash
     git fetch origin main --quiet
     git status --short
     git add <files>
     ```
   - Then run the commit separately.

2. In the same environments, `git commit` may need either a PTY or a commit-message file.
   - Reliable patterns:
     ```bash
     cat >/tmp/commit-message.txt <<'EOF'
     fix: short subject
     EOF
     git commit -F /tmp/commit-message.txt
     ```
   - If the tool supports it, run the commit with PTY enabled.
   - This avoids false tool-guard failures and editor-prompt issues.

3. Prefer `--body-file` for `gh pr comment` as well as `gh pr create`.
   - If the comment body contains backticks like `` `src/app/api/...` ``, shell command substitution can break the command or produce confusing errors.
   - Safe pattern:
     ```bash
     cat >/tmp/pr-comment.md <<'EOF'
     This PR depends on `src/app/api/downloads/file/route.ts` changes in #123.
     EOF
     gh pr comment 123 --body-file /tmp/pr-comment.md
     ```

4. In stacked PR chains, verify remote branch refs directly after rebases or force-pushes.
   - `gh pr view` can lag, and GitHub can briefly show stale commit lists or an outdated branch/base relationship.
   - Check the actual remote head first:
     ```bash
     git rev-parse HEAD
     git ls-remote origin refs/heads/<stacked-branch>
     ```
   - If the remote ref is missing or wrong, push with an explicit refspec instead of relying on inferred branch destinations:
     ```bash
     git push --force origin HEAD:refs/heads/<stacked-branch>
     ```
   - After repairing the remote branch, re-check the PR base branch. If GitHub shows the wrong stacked base, reset it explicitly:
     ```bash
     gh pr edit <pr-number> --base <intended-base-branch>
     ```
   - This is especially useful when updating multiple stacked branches quickly and one branch appears to vanish or lose its expected base.
  - If you flatten a formerly stacked PR directly onto `main`, immediately rewrite the PR title/body so they no longer claim an old parent branch or parent PR. A common stale-state bug is: the code/base are already `main`-based, but the PR body still says `base branch: <old-parent-branch>` or `parent PR: #...`, which misleads reviewers.

5. When a parent PR in a stacked chain gets a hotfix, propagate that fix through child PRs by rebasing each child onto the updated parent branch, then force-pushing.
   - Common symptom: several open child PRs fail the same CI step even though the root cause lives in an earlier parent PR.
   - After pushing the fixes, if the user wants you to keep watching, monitor the whole chain together rather than checking each PR manually one by one. Prefer `scripts/watch-multiple-pr-checks.py` for that final verification pass.
   - Safe repair pattern:
     ```bash
     # fix and push the parent branch first
     git -C .worktrees/<parent> add <files>
     git -C .worktrees/<parent> commit -m "fix: ..."
     git -C .worktrees/<parent> push

     # then rebase each child onto the updated parent remote ref
     git -C .worktrees/<child-1> fetch origin --prune
     git -C .worktrees/<child-1> rebase origin/<parent-branch>
     git -C .worktrees/<child-1> push --force-with-lease

     git -C .worktrees/<child-2> fetch origin --prune
     git -C .worktrees/<child-2> rebase origin/<child-1-branch>
     git -C .worktrees/<child-2> push --force-with-lease
     ```
   - After each force-push, check that new workflow runs attached to the rewritten head branch:
     ```bash
     gh run list --branch <branch> --limit 3
     gh pr view <pr-number> --json statusCheckRollup,mergeStateStatus,url
     ```
   - If the same CI error disappears on the parent but persists on children, suspect that the children were not rebased onto the updated parent yet.

5. `gh pr diff` can fail on very large PRs.
   - GitHub may return HTTP 406 / `PullRequest.diff too_large` when the PR changes hundreds of files.
   - In that case, inspect files with:
     ```bash
     gh pr view <PR_NUMBER> --json files --jq '.files[].path'
     ```
   - Then filter locally, e.g.:
     ```bash
     gh pr view <PR_NUMBER> --json files --jq '.files[].path' | grep '^src/app/api/' || true
     ```
   - Use this to verify whether a scoped set of files is still present after history cleanup or PR splitting.
