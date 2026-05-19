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
- When the user asks to "follow up on PR <number>", first verify that PR's current state with `gh pr view <number> --json state,mergedAt,headRefName,headRefOid,baseRefName`. If the PR is `OPEN`, update its branch; if it is `MERGED` or `CLOSED`, treat the PR number as context only, fast-forward local `main`, create a fresh latest-main branch/worktree, and open a separate follow-up PR rather than resurrecting the old head branch.

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

### Create the PR and Immediately Provide the URL to the User

**Critical step: After creating a PR, immediately show the user the exact GitHub PR URL, regardless of whether they explicitly asked for it or not. Do not wait for the user to request the URL.**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body-file /tmp/pr-body.md
```

**Capture and surface the PR URL:**

```bash
# After successful creation, output the PR URL explicitly
gh pr view $(git branch --show-current) --json url --jq '.url'
```

Alternatively, if the `gh pr create` output includes the URL, capture it and present it to the user. If you fall back to curl, the response JSON contains `html_url` — extract and show it.

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# Create PR via API
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }")

# Extract and display the URL
PR_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['html_url'])")
echo "Pull Request created: $PR_URL"
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

Stacked split-PR rule for foundation + first usage:
- If the user asks for a reusable/foundation change and then a separate first application of that foundation, make two PRs instead of bundling them.
- PR 1 targets `main` and contains only the shared component, primitive, infrastructure, or other foundation change.
- PR 2 targets PR 1's branch and contains only the usage/application change.
- In PR 2's body, explicitly state `Base branch: <parent-branch>` and `Parent PR: #<number>` so reviewers understand the stacked base.
- Verify PR 2's scoped diff against the parent branch (`git diff --stat origin/<parent-branch>...HEAD`), not only against `origin/main`, so the parent foundation diff is not mistaken for part of the child PR.

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
- When adding a new test file in repos that partition tests into CI groups, run the repo's test-group assertion script before pushing (for example `node scripts/ci/assert-test-groups.mjs`) and add the new test path to exactly one appropriate group such as `scripts/ci/test-groups.mjs`. A targeted `node --test <new-file>` pass is not enough if CI rejects unassigned tests.
- Some CI workflows include a final aggregator job such as `Validate Test` / `Verify validation dependency results` that fails only because an upstream dependency failed. Do not debug the aggregator as a test failure. Inspect the upstream failed job logs first (for example `Validate Lint`), fix that root cause, and expect the aggregator to pass once dependencies pass.
- For lint failures in newly added React/Next test files, check for imports that were previously needed for JSX but are unused under the repo's JSX transform (for example `import * as React from 'react';`). Run the repo smoke command, not only the targeted Vitest test, because targeted tests can pass while `next lint` fails.
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
   - For portable touched-file scans, do not rely on GNU-only `xargs -a`; macOS/BSD `xargs` rejects `-a`. Use a shell loop over a file list instead, for example `while IFS= read -r f; do git grep ... -- "$f"; done < /tmp/files.txt`, and make sure a failed helper invocation does not get misreported as a successful scan.
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

   - After rebases or force-pushes, verify remote branch refs directly before trusting PR metadata.
   - This applies both to stacked PR chains and to ordinary follow-up updates on an existing open PR.
   - If an open PR branch is stale and its diff against latest `origin/main` is polluted by many unrelated files, prefer a clean-replacement workflow over committing on top of the stale branch: create a temporary worktree from `origin/main`, apply only the intended scoped changes, run targeted checks, commit once, record the old remote tip with `git ls-remote`, force-with-lease push `HEAD` back to the same PR branch, then verify `gh pr view <pr> --json files` contains only the expected files.
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
   - When flattening a chain of open stacked PRs that should be independent, do not blindly rebase every head branch with its full stacked history. First inspect each PR with `gh pr view <n> --json headRefName,baseRefName,commits,files` and identify the commit/files that belong only to that PR. If a PR's diff includes parent/sibling files, recreate that PR branch from current `origin/main` and cherry-pick only the intended commit(s), then force-push back to the same head branch and edit the PR base to `main`. Verify every flattened PR with `git merge-base origin/main origin/<branch>` equals `origin/main`, `git rev-list --left-right --count origin/main...origin/<branch>` reports `0 1` (or the expected independent commit count), and `gh pr view <n> --json files,commits,baseRefName,assignees` shows only that PR's scoped files. Add requested assignees during the same sweep, e.g. `gh pr edit <n> --base main --add-assignee <login>`.
   - During a multi-PR flatten/rebase sweep, `origin/main` can advance while you are working because an earlier PR in the set merges. After force-pushing the batch, fetch again and re-run the merge-base / left-right-count checks against the new `origin/main`; if counts show `1 1` instead of `0 1`, rebase the rewritten branches once more onto the updated main before reporting completion.
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
   - For path/route/asset rename follow-ups, do a repo-wide grep for the old path before and after the move. If moving a public asset out of a shared-looking location, grep all references first; update every remaining reference to the new location or stop and confirm scope if unrelated feature areas would be affected. After pushing, verify the PR file list and refresh the PR body so it does not describe stale paths.
   - For additive navigation/config arrays that multiple open PRs touch (for example preview-route mapping tables plus their source tests), treat conflicts as additive unless evidence says otherwise: keep latest `origin/main` entries, reapply the open PR's new entry, remove conflict markers, and update/keep tests for every surviving entry. Verify with the narrow source tests that cover the mapping and the PR-specific route/content behavior before force-pushing.
   - When the user points to an existing PR and asks to rename a term/component family, update that same PR branch rather than creating a new PR. Keep the diff narrow, but rename all project-facing occurrences in the touched route/component/test family: imports, JSX tags, exported function names, default export names, related structure tests, and route-family module filenames that still carry the obsolete term. Before pushing, run a targeted grep for the old term/path and the narrow route-family test so tests do not keep asserting stale wording.
   - If the existing PR head branch is already checked out in another worktree, keep the fresh-worktree isolation by creating a temporary local follow-up branch from `origin/<pr-head>`, then push `HEAD` explicitly back to `refs/heads/<pr-head>` with `--force-with-lease`. Do not create a second PR and do not leave the temporary branch as the PR branch. See `existing-pr-followup-worktree/references/pr-branch-already-checked-out.md` for the detailed recipe.
  - Default to a full branch-hygiene pass unless the user narrows scope:
    - inspect review comments, CI failures, and `mergeStateStatus`
    - when asked to sweep open PRs for conflicts/CI failures, do not stop after repairing the first PR. After each push, re-run the open-PR scan for `mergeStateStatus=DIRTY` and failed check conclusions (`FAILURE`, `ERROR`, `ACTION_REQUIRED`) because another open PR may become visible as conflicted once GitHub state refreshes or after the first branch is updated.
    - when the user gives a PR number as a lower bound such as "PR 750 and later open PRs", first classify that boundary PR's state. If the boundary PR is already `MERGED`, treat it as context/baseline only and sweep the subsequent open PRs rather than trying to revive its deleted branch.
    - before editing code for a failing open PR, compare every target branch's merge-base against current `origin/main`. A branch that is one or more commits behind latest main can fail deploy/build because it lacks a shared component or helper that already landed on main; the correct fix is often a clean rebase/force-with-lease push, not duplicating the missing file or changing product code.
    - after rebasing a multi-PR batch, verify `git ls-remote` head SHA, `gh pr view .headRefOid`, `git merge-base origin/main origin/<branch>`, `git rev-list --left-right --count origin/main...origin/<branch>`, required checks, and deploy/Vercel status for each PR. Also repair small PR metadata gaps discovered during the sweep, such as missing assignees, while staying on the existing PRs.
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
  - When an existing PR follow-up asks to make the work inspectable on a Preview Deployment, implement explicit review entrypoints on the same PR branch when needed (for example locale-prefixed `/t` routes), add or update narrow source-level tests for those paths, and refresh the PR body with the exact paths reviewers should open. Important pitfall: preview-review entrypoints should not change existing public route behavior unless the user explicitly asks for public release/route changes. Keep public routes, redirects, canonical routes, and existing entry files unchanged; if a preview path needs migrated copy/components, mount them only under the preview route (for example `/[locale]/t/...`) and add tests that assert the public route surface remains unchanged. Place route tests in the path that mirrors the source route (for example `src/app/[locale]/t/page.tsx` -> `src/__tests__/app/[locale]/t/page.test.tsx`), not a broad ad hoc filename like `home-route-local.test.tsx`. After pushing, verify the new CI/Preview runs are attached to the new head SHA and report pending deploy state without passively waiting unless asked.
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
   - Verification pitfall in skill-heavy repos: broad scans over all `.hermes/skills/**` can false-positive on legitimate examples or reference separators, such as code blocks intentionally showing `1|first line` or long `=======` section dividers. For PR safety scans, restrict checks to the touched files and use narrow conflict-marker regexes such as `^(<<<<<<<|>>>>>>>)( |$)` and `^=======$` instead of treating every line containing equals signs as a merge conflict.
   - This matters especially in docs-only PR follow-up work, where a mistaken rewrite can silently replace the whole file with line-number-prefixed content.

9. GitHub Actions runner migration wording pitfall.

   - When a user asks to move workflows to "hosted runners" or similar wording, do not assume they mean GitHub-hosted `ubuntu-latest` if they provide organization self-hosted runner labels or an output like `gh-runners --show-labels`.
   - Treat the provided label inventory as the source of truth for the requested runner pool.
   - If the user specifies the exact labels to use, apply only those labels. Example: `runs-on: [self-hosted, Linux]` means do not add extra narrowing labels like `X64`, `os:ubuntu`, or `arch:amd64` even if they appear available.
   - Verification pattern for workflow-only runner changes:
     ```bash
     git diff --check
     grep -R "runs-on:" .github/workflows
     grep -R "ubuntu-latest\|self-hosted, Linux," .github/workflows || true
     ```
   - In the PR body, state the final runner selector, not any intermediate broader/narrower selector considered during the session.

9a. Production deploy workflow branch-source changes.

   - When changing a manual production deploy workflow from a release-branch promotion model to direct branch deployment, remove branch-mutation steps entirely instead of keeping a hidden `git checkout/rebase/push` phase.
   - When the requested pattern is “like querypie-docs/corp-web-japan” or another sibling repo, match the sibling implementation shape closely instead of inventing extra deploy-script behavior.
   - If the sibling workflow exposes a `workflow_dispatch` input such as `BRANCH` with default `main`, use that input directly, for example `BRANCH: ${{ inputs.BRANCH }}`, rather than `github.ref_name`. This makes the manual dispatch UI the source of the deployed branch and preserves the default-main behavior.
   - If the deploy script already reads `process.env.BRANCH` / `process.env.TARGET_ENV` and passes them to Vercel SDK `gitSource.ref` / `target`, do not add new env validation, target normalization, or helper abstractions unless the user explicitly asks for script hardening. The safer follow-up for a sibling-parity request is usually to leave the script unchanged and only adjust the workflow.
   - After removing push/rebase behavior, lower workflow permissions from `contents: write` to `contents: read` unless another remaining step still needs writes.
   - Compare against known-good sibling workflows and scripts when the user says "like repo X", and keep repo-specific secrets/vars intact unless the request explicitly includes normalizing those too.
   - See `references/workflow-dispatch-production-branch.md` for a concise migration recipe and verification checklist.

10. Markdown links to GitHub paths containing `[` or `]` need extra escaping.

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

11. Docs-refresh PRs against latest main need source-of-truth validation, not only prose edits.

   - When the user asks to update repository docs against current `main`/`origin/main`, start from a fresh latest-main worktree, record the exact base SHA, and re-run any scan/count commands that the docs claim as their baseline.
   - For audit docs, update all dependent count tables together: scanned files, occurrences, distinct URLs/hosts, host breakdowns, and code-vs-content counts. Do not update only the obvious changed row.
   - For route/status docs, verify current source paths and public route files exist on latest main before repeating old guidance. If a preview `/t/*` route has been promoted/removed, update active guidance to the canonical public route while preserving historical commit-pinned examples only when they are explicitly before/after evidence.
   - Before committing docs with many links, run a lightweight Markdown validation pass:
     ```bash
     python3 - <<'PY'
     import pathlib, re, subprocess, urllib.parse
     errors = []
     for p in sorted(pathlib.Path('docs').rglob('*.md')):
         text = p.read_text()
         for label, url in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text):
             if url.startswith(('http://', 'https://', '#', 'mailto:')):
                 continue
             target = urllib.parse.unquote(url.split('#', 1)[0])
             if target and not (p.parent / target).resolve().exists():
                 errors.append(f'{p}: missing relative link {url}')
         for commit, path in re.findall(r'https://github\.com/<owner>/<repo>/(?:blob|tree)/([0-9a-f]{7,40})/([^\s)]+)', text):
             path = urllib.parse.unquote(path)
             if subprocess.call(['git', 'cat-file', '-e', f'{commit}:{path}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
                 errors.append(f'{p}: missing commit-pinned path {commit}:{path}')
     print('\n'.join(errors))
     raise SystemExit(1 if errors else 0)
     PY
     ```
     Replace `<owner>/<repo>` with the current GitHub repository before running.
   - If docs mention issues, preserve the user's no-auto-close preference: use neutral references like `#521` / `Related issues`, not `Closes #521`, unless the user explicitly asked to close the issue on merge.
