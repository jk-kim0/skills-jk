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

This part is pure `git`. In repositories that use worktrees, or whenever the current/root checkout is on `main`, prefer a fresh linked worktree from the latest remote main tip instead of branching in place:

```bash
# Make sure you're up to date against the REMOTE default branch.
# Prefer a fresh worktree from origin/main, not a branch created from whatever checkout is currently active.
git fetch origin --prune
git worktree add .worktrees/<flat-name> -b feat/<topic> origin/main

# Verify the new worktree really starts from the latest remote main tip
git -C .worktrees/<flat-name> rev-parse HEAD origin/main
git -C .worktrees/<flat-name> merge-base HEAD origin/main
```

If the repository does not use worktrees for that task, the in-place fallback is still:

```bash
git fetch origin --prune
git checkout -b feat/<topic> origin/main
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

Important interpretation rule for later review/debugging:
- distinguish `local main was updated` from `the current root checkout was switched back to main`
- a repository can have an up-to-date `main` ref while the root workspace is still checked out to some feature branch
- when validating whether a PR branch was correctly based/rebased onto latest main, compare the PR head against the base tip that existed at PR creation/update time, not against a newer `origin/main` that may already include that PR merge
- especially for merged PRs, `current origin/main` can be ahead by exactly the merge commit that absorbed the PR; that does **not** mean the PR branch failed to rebase onto latest main before merge
- practical checks:
  ```bash
  gh pr view <number> --json headRefName,headRefOid,baseRefName,mergeCommit
  git merge-base <pre-merge-base-tip> <pr-head-sha>
  git rev-list --left-right --count <pre-merge-base-tip>...<pr-head-sha>
  ```
- use this wording discipline in reports too: say `root checkout was not restored to main yet` rather than incorrectly saying `main was not updated`

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

Issue-linking and closing rule:
- Default to non-closing issue references in PR titles/bodies/comments.
- Do **not** use auto-closing keywords such as `Closes #<issue>`, `Fixes #<issue>`, or `Resolves #<issue>` unless the user explicitly asked for the PR merge to close that issue.
- Safe default PR body section:
  ```md
  ## Related issue
  - [#433](https://github.com/<owner>/<repo>/issues/433)
  ```
- This applies even more strongly in stacked or multi-PR work, where an early merge can close the issue before the full chain lands.
- If you already opened a PR with an auto-closing keyword by mistake, edit the PR body immediately to remove it before merge.
- When in doubt, leave issue closure to a separate explicit user decision or a later manual issue comment.

Important temp-file safety rule:
- Prefer a repo-external temp path such as `/tmp/pr-body.md` or another absolute temp location.
- Do **not** default to writing PR/issue body drafts inside the repository or worktree root (for example `.tmp-pr-body.md`) unless you intentionally want that file tracked.
- If you must place a draft file inside the checkout temporarily, exclude it from `git add` and run `git status --short` before commit so you do not accidentally commit the body file.
- Practical failure pattern: creating the PR body inside the worktree, staging broad paths, then needing an amend commit only to remove the stray temp file.
- The same separation rule applies to repository guidance changes discovered during implementation work: if you edit AGENTS.md, checked-in skills, or other repo-operational guidance as a follow-up to feature work, prefer a separate branch and separate PR instead of silently bundling those guidance changes into the feature PR.
- Exception: if an open PR already exists for the same guide/skill/docs source-of-truth, update that existing PR instead of opening a parallel PR. Parallel docs/skill PRs for the same workflow create competing canonical documents and should be avoided unless the user explicitly asks for a split.

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
- Also do not assume a docs-only or guidance-only PR will necessarily miss checks just because the repository has a known path-ignore caveat; verify the actual PR `statusCheckRollup` or `gh pr checks` result after creation, because some docs-only changes can still attach required checks and preview/deploy workflows.

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

After identifying the issue, use file tools (`patch`, `write_file`) to fix the code.

Smoke/typecheck pitfall:
- If the failed CI job is a smoke command that chains lint + typecheck + test grouping, reproduce that full smoke command locally after the narrow fix, not only the targeted regression test.
- TypeScript failures around formatting helpers often indicate a source/display contract mismatch, especially optional metadata (`string | undefined`) being passed into a formatter that expects `string`. Preserve `undefined` for missing optional fields rather than formatting an empty or missing value unless the product contract explicitly says otherwise.

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

## `gh pr view` branch-targeting compatibility note

When verifying a PR by branch name after creation or push, prefer passing the branch name as the positional argument:

```bash
gh pr view <branch-name> --json number,title,url,headRefName,baseRefName,state
```

Do not assume `gh pr view --head <branch>` is available. Some `gh` versions do not support a `--head` flag for `pr view` and will fail with:

```text
unknown flag: --head
```

Safe rule:
- for `gh pr view`, use one of:
  - PR number
  - PR URL
  - branch name as the positional argument
- reserve explicit `--head` usage for commands that actually document that flag in the installed `gh` version

Practical verification pattern after PR creation:

```bash
gh pr create ...
gh pr view <branch-name> --json number,title,url,headRefName,baseRefName,state
```


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

4. After rebases or force-pushes, verify remote branch refs directly before trusting PR metadata.
   - This applies both to stacked PR chains and to ordinary follow-up updates on an existing open PR.
   - `gh pr view` can lag, and GitHub can briefly show stale commit lists, an outdated `headRefOid`, or an outdated branch/base relationship even when the push already succeeded.
   - CLI compatibility pitfall: not all `gh` versions support `gh pr view --head <branch>`. A safer cross-version pattern is to pass the branch name as the positional PR selector:
     ```bash
     env -u GITHUB_TOKEN gh pr view <branch-name> --json number,title,url,headRefName,baseRefName,state
     ```
   - Check the actual remote head first:
     ```bash
     git rev-parse HEAD
     git ls-remote origin refs/heads/<branch>
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
   - When a stacked parent PR is squash-merged and its branch is deleted, the child PR may automatically retarget to `main` while its head still contains the parent's original, now-unmerged-by-SHA commit. Symptom: `gh pr view <child> --json baseRefName,commits` shows `baseRefName=main` and both the parent original commit plus the child commit. Fix by rebasing the child with `git rebase --onto origin/main <original-parent-commit-sha> <child-branch>`, then force-push and update the PR body to remove stacked-parent language. Verify with `git rev-list --oneline origin/main..HEAD` and `gh pr view <child> --json commits,files,baseRefName` before reporting success.
   - Important recovery pattern for existing open PRs: GitHub can still show an open PR with `headRefName` / prior `headRefOid` metadata even when the actual remote head branch ref is gone. Practical symptom set:
     ```bash
     gh pr view <pr-number> --json headRefName,headRefOid,url
     git ls-remote origin refs/heads/<head-branch>
     ```
     where `gh pr view` returns a branch name/SHA but `git ls-remote` returns nothing.
   - In that state, do not trust local `origin/<branch>` refs or GitHub mergeability badges. Recreate the missing remote branch explicitly from the intended local worktree/branch:
     ```bash
     git -C <worktree> rev-parse HEAD
     git -C <worktree> push --force origin HEAD:refs/heads/<head-branch>
     git ls-remote origin refs/heads/<head-branch>
     ```
   - GitHub may print a generic `Create a pull request for '<branch>'` message during this recovery push even though the PR already exists. That does not mean a new PR was created; verify the existing PR's `headRefOid` again after the push.
   - After a successful rebase/squash update, `mergeStateStatus` can remain `BEHIND`, `UNKNOWN`, or even stale `DIRTY` briefly. Before doing another rewrite, verify the real ancestry first:
     ```bash
     git fetch origin --prune
     git merge-base origin/<head-branch> origin/main
     git rev-parse origin/main
     git rev-list --count origin/main..origin/<head-branch>
     ```
     If the merge-base equals `origin/main` and the ahead count is the expected PR commit count, treat the branch as correctly rebased and wait for GitHub state to catch up rather than rewriting it again.

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
   - After each force-push, verify that fresh workflow runs attached to the rewritten head SHA, not merely that the branch has some recent runs:
     ```bash
     git rev-parse HEAD
     gh run list --branch <branch> --limit 3 --json headSha,status,conclusion,workflowName,url
     gh pr view <pr-number> --json headRefOid,statusCheckRollup,mergeStateStatus,url
     ```
   - Compare `git rev-parse HEAD`, PR `headRefOid`, and each run's `headSha`. Only treat the rerun as attached correctly when the new runs reference the current rewritten HEAD SHA.
   - Practical interpretation: `mergeable=MERGEABLE` plus `mergeStateStatus=BLOCKED` immediately after a rebase/force-push often means the conflict is already resolved and required checks are merely pending on the new head. Do not report it as an unresolved merge conflict unless GitHub actually reports a conflict/unmergeable state.
   - If the same CI error disappears on the parent but persists on children, suspect that the children were not rebased onto the updated parent yet.

5. Existing PR follow-up hygiene.
5. Existing PR follow-up hygiene.
   - When resolving rebase conflicts on an existing UI/content PR, treat removals from merged PRs as first-class intent, not as disposable conflict noise. Before accepting the open-PR side of a conflict, list deleted/removed JSX, imports, helper components, visible copy, and tests from the merged PR and verify they do not get resurrected. This is especially important for UI header controls, metadata lines, descriptions/leads under headings, selectors, and route-local layout details that the user explicitly asked to remove.
   - After conflict resolution, run a negative grep for exact removed strings/components and add or preserve tests that assert absence. Example checks: `grep -R "<RemovedComponent\|removed visible copy" <touched-files> || true`, plus source tests using `assert.doesNotMatch(...)`. Do this before amending/force-pushing so review feedback like “I already told you to delete this” is not repeated across pushes.
   - When reconciling UI placement conflicts, preserve both content presence and relative position. If a selector/button was intentionally moved next to an H1, tests should pin the structure/order, not merely assert the component still exists somewhere in the file.
   - When the user asks to "fix the PR" / "PR 고쳐줘" after several incremental follow-up commits, do not stop at fixing the immediate failing check.
   - For iterative link/content cleanup PRs where the user keeps providing more pages or links, keep updating the same open PR branch and refresh the PR body/test plan after each batch. When changing link constants or route targets, search for existing source-inspection tests that still assert the old target; CI failures can come from stale contract tests outside the latest touched files, such as route-family `cta-links.test.mjs` files. If the stale test is the failure, update it to the new local/canonical route, rerun the failed test plus directly affected route tests, rebase onto latest `origin/main`, push with `--force-with-lease` if the rebase rewrites commits, and verify fresh workflow runs attach to the rewritten head SHA.
   - When the user points to an existing PR and asks to rename a term/component family, update that same PR branch rather than creating a new PR. Keep the diff narrow, but rename all project-facing occurrences in the touched route/component/test family: imports, JSX tags, exported function names, default export names, related structure tests, and route-family module filenames that still carry the obsolete term. Before pushing, run a targeted grep for the old term/path and the narrow route-family test so tests do not keep asserting stale wording.
   - If the existing PR head branch is already checked out in another worktree, keep the fresh-worktree isolation by creating a temporary local follow-up branch from `origin/<pr-head>`, then push `HEAD` explicitly back to `refs/heads/<pr-head>` with `--force-with-lease`. Do not create a second PR and do not leave the temporary branch as the PR branch. See `existing-pr-followup-worktree/references/pr-branch-already-checked-out.md` for the detailed recipe.
  - Default to a full branch-hygiene pass unless the user narrows scope:
    - inspect review comments, CI failures, and `mergeStateStatus`
    - if checks are green but `mergeStateStatus=DIRTY`, diagnose it as a latest-main conflict/rebase task rather than a test-failure task
    - inspect the merged PR(s) or commits that advanced `origin/main` across the conflicted files, preserve their intent, and reapply only the open PR's intended delta
    - when a merged PR intentionally removed UI/copy/metadata, preserve the full removal, not only the obvious component deletion. Do not resurrect adjacent deleted lines while resolving conflicts just because they are part of the open PR side's preferred structure. Example: if latest main removed privacy-policy header controls and date metadata, keep both removed; reapply only the shared legal primitive/className changes.
    - after conflict resolution, grep for the removed symbols/text from the merged PR and update structure tests to assert absence when the removal is intentional. This catches accidental resurrection before push.
    - fix the actual issue
    - rebase onto latest `origin/main`
    - if the branch history is only iterative fixups, squash to one clean commit
    - force-push the cleaned branch
    - if the surviving commits/scope changed materially, refresh the PR title/body so Summary/Test Plan match the cleaned branch
  - For UI/CSS follow-up branches with several incremental spacing/layout tweaks, do not leave the PR body describing the intermediate history. Rewrite it around the final landed contract on the branch:
    - describe the final CSS values that remain after the latest push, not the earlier trial values
    - separate page-specific exceptions from shared primitive/layout rules
    - explicitly note removed semantic-only variants or overrides when the final result simplified back to one shared rule
    - keep the file list and test plan aligned with the surviving diff, not the earlier larger scope
  - When the user explicitly asks for a visible experiment or validation commit on an existing PR (for example removing section-specific spacing to see whether a shared spacing contract is sufficient), keep it on the same PR branch rather than opening a new PR. Make the commit message/body state that it is a validation commit, push it, and update the PR body so reviewers understand the branch’s current visual contract instead of the earlier safer baseline. Run the narrow structural/source tests that encode the contract, but do not over-verify locally if the user wants to inspect the Preview Deployment themselves.
  - Only preserve a multi-commit PR history when the user explicitly asks for it or the commits are meaningfully staged for review.


6. `gh pr diff` can fail on very large PRs.

   - In that case, inspect files with:
     ```bash
     gh pr view <PR_NUMBER> --json files --jq '.files[].path'
     ```
   - Then filter locally, e.g.:
     ```bash
     gh pr view <PR_NUMBER> --json files --jq '.files[].path' | grep '^src/app/api/' || true
     ```
   - Use this to verify whether a scoped set of files is still present after history cleanup or PR splitting.

7. When working with git worktrees, prefer absolute worktree paths in follow-up verification commands.

   - Tool runners do not always keep the same current working directory across calls.
   - A relative path like:
     ```bash
     cd .worktrees/<branch>
     ```
     can fail if the next command runs from a different directory than expected.
   - Safer patterns:
     ```bash
     WT=/absolute/path/to/repo/.worktrees/<branch>
     cd "$WT"
     git status --short
     ```
     or:
     ```bash
     git -C /absolute/path/to/repo/.worktrees/<branch> status --short
     ```
   - This matters most after PR creation/push, when you do one last remote-head verification pass and want to avoid a false failure caused only by cwd drift.

8. Never write file-tool line-number prefixes back into tracked files.

   - Some file-reading tools render content with display prefixes like:
     ```text
     1|first line
     2|second line
     ```
     or, after repeated misuse, even nested forms like:
     ```text
     1| 1| 1|real content
     ```
   - Those prefixes are presentation metadata, not file content.
   - Do **not** copy `read_file` output directly into `write_file`, `patch`, PR comments, or committed docs without stripping the prefixes first.
   - Safe rule:
     - use `read_file` for inspection only
     - use raw filesystem reads / editor buffers / scripts for full-file rewrites
     - after any file rewrite sourced from tool output, run a verification grep or regex check for accidental `^\s*\d+\|` line starts before committing
   - This matters especially in docs-only PR follow-up work, where a mistaken rewrite can silently replace the whole file with line-number-prefixed content.

9. Markdown links to GitHub paths containing `[` or `]` need extra escaping.

   - Paths like `src/app/blog/[id]/[slug]/page.tsx` are not safe to paste raw into ordinary Markdown links.
   - Two things must happen:
     - escape `[` and `]` in the visible link label
     - percent-encode bracket characters in the URL path (`[` -> `%5B`, `]` -> `%5D`)
   - Safe shape:
     ```md
     [src/app/blog/\[id\]/\[slug\]/page.tsx](https://github.com/<owner>/<repo>/blob/<commit>/src/app/blog/%5Bid%5D/%5Bslug%5D/page.tsx)
     ```
   - Prefer commit-pinned blob/tree URLs when the doc is meant to preserve a stable historical example.
   - After editing Markdown with bracketed route paths, inspect the rendered or raw final file once before commit to ensure the link label and URL were both encoded correctly.
