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

## CI watch after amend / force-push

When a PR branch is amended or force-pushed after checks have already started, any existing `gh pr checks --watch` or background watch may finish against the previous head SHA. After every amend, rebase, force-push, or branch replacement:

1. Verify the pushed branch tip: `git rev-parse HEAD origin/<branch>`.
2. Re-query the PR head SHA: `gh pr view <pr> --json headRefOid,statusCheckRollup`.
3. Treat old completed check output as evidence only for the old SHA.
4. Start a fresh watch for the new SHA, or explicitly report that the new checks are still pending.

Pitfall: do not say “CI passed” for the PR after a force-push just because a previous background watch completed successfully. Name whether the pass belongs to the old or current head SHA.

## Stacked PRs on top of an open PR

When the user asks to create a new PR "on top of" an existing open PR, treat it as a stacked PR workflow rather than branching from `main`.

1. Inspect the base PR first: `gh pr view <number> --json state,headRefName,baseRefName,url,title` and verify it is still open.
2. Fetch the base PR head or use its existing clean worktree/branch if one is already present.
3. Create the new branch from the base PR head and create the new PR with `--base <base-pr-head-branch>`, not `--base main`.
4. Before editing, verify the actual worktree with both `git status --short --branch` and `git rev-parse --show-toplevel`. Do not trust a newly created path until these commands show the intended branch and repository root.
5. If an attempted extra worktree under a repo-local `.worktrees/` path is missing, resolves to the root checkout, or otherwise does not show the intended branch, stop using that path. Prefer switching an existing clean base-PR worktree to the child branch, or create a sibling worktree and re-verify before writing files.
6. After pushing, confirm the new PR metadata shows `baseRefName` equal to the base PR's head branch and `headRefName` equal to the new branch.

Pitfall: a path existing under `.worktrees/` is not enough evidence that edits are happening in the desired git worktree. Always verify with `git rev-parse --show-toplevel` from inside the path before creating files.

## PR body safety for markdown with shell-sensitive characters

Before any `gh` command, read active repo/local guidance such as `AGENTS.md`, `.agents/`, `.hermes/`, or user-scope rules that may constrain GitHub CLI invocation. If the active guidance requires unsetting token environment variables, run every GitHub CLI command as `env -u GITHUB_TOKEN gh ...`, including read-only calls like `gh pr view`, `gh pr checks`, `gh run list`, and `gh api`. This avoids accidentally using a stale or lower-priority token from the environment and keeps final PR reports consistent with the user's GitHub Gate expectations.

When creating or editing a PR body that contains backticks, `$()`, shell variables, GitHub Actions expressions, or multiline markdown, prefer a temporary markdown file plus `gh pr create --body-file <file>` or `gh pr edit --body-file <file>` instead of passing the body through a double-quoted `--body "..."` argument. See `references/pr-body-shell-quoting-safety.md` for the full repair recipe and verification pattern.

## CI follow-up during open-PR sweeps

When an open-PR cleanup sweep finds a failed check, treat the latest PR head as the source of truth before and after fixing:

1. Capture `headRefOid`, `statusCheckRollup`, `gh pr checks`, and the newest `gh run list --branch <branch>` runs.
2. Inspect the failing job log and fix the smallest branch-local cause.
3. Amend or commit on the same PR branch, then push/force-push with lease as appropriate.
4. Re-query the remote branch head and GitHub checks after the push; stale failed checks from the previous SHA are not current failures.
5. If the new checks are still pending, report the PR as pending/in-progress rather than complete.

Concrete schema-edit pitfall: when a PR removes or renames a Prisma model field, scan the same model for `@@index`, `@@unique`, relation, and generated/client references to the old field. A leftover `@@index([removedField])` can pass code review visually but fail Prisma validation/build CI.

Detailed non-bundled PR follow-up/body/validity procedures have been consolidated into the inactive pack at `.hermes/skill-packs/github-pr-workflow/INDEX.md`. For narrow follow-up, stacked rebase, body-file safety, or PR validity audit work, read that index and then only the relevant detailed file. Repo-specific PR creation wrappers such as `skills-jk-gha-pr-creation` own only their repository-specific dispatch mechanism; keep generic PR lifecycle and CI guidance here rather than duplicating it in those wrappers.

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
# Important: also verify that the target path is actually a linked worktree.
# `git -C <path>` can climb to a parent repository if <path> is only a plain
# subdirectory, which can falsely make status/rev-parse checks look successful.
test -f .worktrees/<flat-name>/.git || { echo "missing linked-worktree .git file"; exit 1; }
git worktree list --porcelain | grep -F "worktree $(pwd)/.worktrees/<flat-name>"
git -C .worktrees/<flat-name> rev-parse --show-toplevel
git -C .worktrees/<flat-name> rev-parse HEAD origin/main
git -C .worktrees/<flat-name> merge-base HEAD origin/main
```

If the repository does not use worktrees for that task, the in-place fallback is still:

```bash
git fetch origin --prune
git checkout -b feat/<topic> origin/main
```

When fast-forwarding an existing local `main`, prefer the explicit fetched remote ref over ambiguous pull syntax:

```bash
git fetch origin --prune
git checkout main
git merge --ff-only origin/main
```

Avoid relying on `git pull --ff-only origin main` in unusual repo/worktree configurations; it can fail with messages such as `Cannot fast-forward to multiple branches`. The explicit `fetch` + `merge --ff-only origin/main` form is clearer and safer.

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

### Direct commits to `main` when explicitly requested

Default repo work should still use feature branches/worktrees and PRs, but if the user explicitly asks to commit and push directly to `main` (especially in a brand-new repository or for a simple initial docs/bootstrap change), do the direct path instead of forcing a PR workflow:

```bash
# Verify current branch, remote, and pending changes first
git status --short --branch
git remote -v
git branch --show-current

# Commit only the intended files
git add README.md
git commit -m "docs: add project README"

# Push main and set upstream if needed
git push -u origin main

# Verify clean sync
git status --short --branch
git log --oneline --decorate -1
```

Pitfalls:
- Do not reinterpret an explicit "main branch에 commit 생성하고 push" request as a PR request.
- Still verify the remote URL and branch before pushing, because direct-main pushes are side effects.
- Keep the final report short: commit SHA/message, push target, and clean/synced status.

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

### Preserve file-specific commit-log conventions

When the user explicitly asks to follow an existing commit-log convention, do not infer the message shape only from general Conventional Commits. Inspect the touched file's own history first:

```bash
git log --all --follow --date=short --pretty=format:'%h %ad %s' -- <path> | head -40
git log --all --date=short --pretty=format:'%h %ad %s' --grep='<file-or-feature-name>' | head -60
```

Then choose the most recent matching convention for that class of change. If a later review reveals a coupled version field or release marker was missed, amend the existing PR commit rather than adding a noisy follow-up commit, then force-push with an explicit lease and refresh the PR body.

For installer/script default-version bumps, also inspect nearby header/version metadata before committing. A repo may maintain both a product default version (for example `RECOMMENDED_VERSION`) and a script/self version (for example `SCRIPT_VERSION` with a `YY.MM.PATCH` contract); bump both when the file's history shows that script releases are manually versioned.

## 3. Pushing and Creating a PR

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### Create or Update Exactly One PR and Immediately Provide the URL to the User

When the user asks for “PR 1”, “PR 하나”, or otherwise requests a single PR, first check whether an open PR already exists for the same head branch or same scoped change before creating a new one. If a matching open PR exists, update that PR branch/body instead of opening a duplicate. Treat the user’s “one PR” constraint as both a split-scope instruction and a duplicate-avoidance requirement.

**Critical step: After creating or updating a PR, immediately show the user the exact GitHub PR URL, regardless of whether they explicitly asked for it or not. Do not wait for the user to request the URL.**

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
- When the user asks for a PR that addresses a specific issue, comment on that issue after the PR is created with the PR URL and a concise summary of the change. Use `gh issue comment --body-file` for shell-safe Markdown, then verify the last comment URL with `gh issue view <n> --json comments --jq '.comments[-1]'`.
- This applies even more strongly in stacked or multi-PR work, where an early merge can close the issue before the full chain lands.
- If you already opened a PR with an auto-closing keyword by mistake, edit the PR body immediately to remove it before merge.
- When in doubt, leave issue closure to a separate explicit user decision or a later manual issue comment.

Stacked split-PR rule for foundation + first usage:
- If the user asks for a reusable/foundation change and then a separate first application of that foundation, make two PRs instead of bundling them.
- PR 1 targets `main` and contains only the shared component, primitive, infrastructure, or other foundation change.
- PR 2 targets PR 1's branch and contains only the usage/application change.
- In PR 2's body, explicitly state `Base branch: <parent-branch>` and `Parent PR: #<number>` so reviewers understand the stacked base.
- Verify PR 2's scoped diff against the parent branch (`git diff --stat origin/<parent-branch>...HEAD`), not only against `origin/main`, so the parent foundation diff is not mistaken for part of the child PR.
- When a merged planning/documentation PR explicitly defines a foundation PR followed by a first usage PR, treat the merged PR as context from latest `main`, not as a branch to revive; create PR 1 from `origin/main`, then create PR 2 stacked on `origin/<pr-1-branch>` if PR 1 is still open.
- If that plan is a living document, update it on the active implementation branches so reviewers can see which planned PRs now exist and how the stacked child relates to the parent.
- See `references/stacked-plan-execution.md` for the detailed recipe, including lockfile-only dependency updates and worktree-local `node_modules` cleanup after verification.
- If an open child PR was stacked on a parent/foundation PR that has since landed on `main`, rebuild the same child PR branch on latest `origin/main` so the PR contains only the child patch, then update stale stacked-parent PR body text; use `references/stacked-pr-after-parent-merge.md`.
- Important distinction: if the user says to “rebase PR A on top of PR B” or “PR A를 PR B 위로 rebase,” do not automatically change PR A's GitHub target/base branch. Rebase the head branch history as requested, but keep the PR base branch unchanged unless the user explicitly asks to retarget the PR. Some review workflows want the branch ancestry stacked while the GitHub target remains `main`.
- Important: do not change an existing PR's GitHub target/base branch just because the user asks to “rebase it on top of” another PR. Unless the user explicitly says to retarget the PR, keep the PR target branch unchanged (often `main`), rebase only the head branch history, and mention the dependency in the PR body if helpful. Changing the target branch changes review/merge semantics and can be wrong even when the branch ancestry is stacked.

Important temp-file safety rule:
- Prefer a repo-external temp path such as `/tmp/pr-body.md` or another absolute temp location.
- Do **not** default to writing PR/issue body drafts inside the repository or worktree root (for example `.tmp-pr-body.md`) unless you intentionally want that file tracked.
- If you must place a draft file inside the checkout temporarily, exclude it from `git add` and run `git status --short` before commit so you do not accidentally commit the body file.
- Practical failure pattern: creating the PR body inside the worktree, staging broad paths, then needing an amend commit only to remove the stray temp file.
- The same separation rule applies to repository guidance changes discovered during implementation work: if you edit AGENTS.md, checked-in skills, or other repo-operational guidance as a follow-up to feature work, prefer a separate branch and separate PR instead of silently bundling those guidance changes into the feature PR.
- Exception: if an open PR already exists for the same guide/skill/docs source-of-truth, update that existing PR instead of opening a parallel PR. Parallel docs/skill PRs for the same workflow create competing canonical documents and should be avoided unless the user explicitly asks for a split.
- Mid-session merge pitfall: before pushing or editing an existing PR branch that was open earlier in the session, re-check `gh pr view <number> --json state,mergedAt,headRefName,headRefOid,files,url`. If it is now `MERGED`, stop updating that branch as the PR target. Start a fresh latest-`origin/main` branch/worktree for any remaining changes, open a new PR, then clean the obsolete worktree/local branch and delete the old remote head only if no open PR uses it. See `references/merged-pr-during-followup-recovery.md`.
- If a `git push --force-with-lease` follow-up to an existing PR branch is rejected as `stale info`, do not immediately retry with a broader force push. First fetch/prune and re-check `gh pr view <number> --json state,mergedAt,headRefName,headRefOid,url` plus `git ls-remote origin refs/heads/<head-branch>`. If the PR became `MERGED` and the remote head was deleted during the follow-up, treat the prepared local commit as a patch for a new follow-up PR: reset/switch the temporary worktree to latest `origin/main`, cherry-pick or reapply only the intended narrow commit, push a new branch, and explain in the PR body that the original PR merged before the follow-up landed. This preserves the user's requested change without resurrecting a deleted merged branch.
- If the local checkout is on a branch whose upstream was deleted because its PR already merged, but the working tree still has uncommitted content changes, do not revive the deleted branch. Save the local diff to a repo-external patch, create a backup branch at the old local tip, reset/switch to a fresh branch from `origin/main`, apply the patch with `git apply --3way`, resolve conflicts against latest main, then create/update a new PR. See `references/merged-pr-local-uncommitted-content-refresh.md`.
- For MDX content PRs that start from Korean Confluence Space synchronization, check sibling localized files under `src/content/en/...` and `src/content/ja/...` before finalizing the PR. If the Korean change is a product version/build tag/date or short product-support label, apply equivalent EN/JA updates in the same PR unless the user explicitly scopes it to Korean only.
- If the PR is already merged, the remote head branch has been deleted, and the stale local branch still has uncommitted edits, preserve the edits as a patch, create a backup branch at the old local HEAD, reset/switch to a fresh branch from `origin/main`, apply the patch with `git apply --3way`, resolve conflicts there, and open a new follow-up PR instead of resurrecting the deleted branch. See `references/merged-pr-deleted-head-with-local-edits.md`.

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
- If an open PR was `DIRTY`, then after rebase/force-push verify the real remote ancestry before interpreting GitHub's remaining state: `git ls-remote origin refs/heads/<branch>`, `git merge-base origin/main origin/<branch>`, `git rev-parse origin/main`, and `git rev-list --left-right --count origin/main...origin/<branch>`. When the merge-base equals `origin/main`, the branch is `0 1` ahead, `statusCheckRollup` is empty, and `reviewDecision=REVIEW_REQUIRED`, a remaining `mergeStateStatus=BLOCKED` is a review/policy gate, not an unresolved conflict or CI failure. Do not keep rewriting the branch; report that the conflict is resolved and review is required.
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
- Fresh Node/Next.js worktrees can fail targeted Vitest checks before test collection because CSS/PostCSS devDependencies are not resolvable from that worktree (for example `Cannot find module '@tailwindcss/postcss'` from `postcss.config.mjs`). When the user prefers avoiding repeated local installs, do not install dependencies just to unblock the local check; run lightweight hygiene checks such as `git diff --check`, push, verify CI runs attach to the current head SHA, and report the local test as blocked by dependency resolution rather than assertion failure. See `references/fresh-worktree-node-dependency-resolution.md`.
- If the root checkout already has a compatible `node_modules` and the worktree is missing dependencies, a short-lived worktree-local symlink can be a useful RED/GREEN verification shortcut for targeted Vitest/lint: `ln -s ../../../front/node_modules front/node_modules` (adjust relative path), run the narrow command, then remove the symlink before `git status`/commit. Treat this as an optional local convenience, not a committed repo change, and do not use it to hide real generated-client or Prisma/typegen prerequisites.
- If you are adding or adjusting a narrow source-level route/component test in such a fresh worktree, a better lightweight verification path can be to mock CSS-importing foundation/shared components in the test so Vitest does not need to transform their `.module.css` imports. This is appropriate when the assertion is about route composition, metadata, or source contracts rather than CSS rendering. Keep the mocks local to that test and still run `git diff --check` plus the repo’s test-group assertion before pushing.
- If the failed CI job is a smoke command that chains lint + typecheck + test grouping, reproduce that full smoke command locally after the narrow fix, not only the targeted regression test.
- When adding a new test file in repos that partition tests into CI groups, run the repo's test-group assertion script before pushing (for example `node scripts/ci/assert-test-groups.mjs`) and add the new test path to exactly one appropriate group such as `scripts/ci/test-groups.mjs`. A targeted `node --test <new-file>` pass is not enough if CI rejects unassigned tests.
- If a PR starts failing CI on a GitHub pull request merge ref after another PR has landed on `main`, do not assume the active PR's touched files caused the failure. First rebase the PR head onto latest `origin/main`, then rerun the failing test. If the failure is in a source-level inventory/content availability test and the newly merged main content legitimately changes fallback order, counts, or “missing content” status, update the stale test expectation to the current content contract rather than changing unrelated product code. Verify fresh runs attach to the rebased head SHA.
- Some CI workflows include a final aggregator job such as `Validate Test` / `Verify validation dependency results` that fails only because an upstream dependency failed. Do not debug the aggregator as a test failure. Inspect the upstream failed job logs first (for example `Validate Lint`), fix that root cause, and expect the aggregator to pass once dependencies pass.
- For Vercel preview/deploy workflows, distinguish product build/deploy status from wrapper-script transport failures. If the Vercel status context is already `SUCCESS` / "Deployment has completed" but the GitHub Actions deploy job failed at the end with a transient request error such as `TypeError: fetch failed`, do not rewrite product code. Rerun the failed deploy job/run, then verify the rerun is attached to the current PR head SHA and all check rollup entries are success/skipped.
- Similarly, if a deploy job creates a Vercel deployment successfully but then polls `INITIALIZING` until a fixed timeout (for example `Deployment polling timed out after 600s`), treat it first as a deploy polling/platform timing failure, not an application code failure. Check whether normal app CI/build checks passed, rerun the failed deploy job once, and report the Vercel target/status rather than making speculative product-code changes.
- For Docker/buildx cache-only image validation failures, inspect the actual failed log before changing product code. If the failure is an external image registry/rate-limit condition such as Docker Hub `429 Too Many Requests` while loading base image metadata, classify it as transient infrastructure/registry exhaustion. Rerun the failed job once when appropriate, but do not repeatedly push empty/no-op commits just to retrigger CI; report the external cause and wait for rate limit recovery or fix the workflow/authentication separately.
- For lint failures in newly added React/Next test files, check for imports that were previously needed for JSX but are unused under the repo's JSX transform (for example `import * as React from 'react';`). Run the repo smoke command, not only the targeted Vitest test, because targeted tests can pass while `next lint` fails.
- For routing/internal-index source tests, broad negative assertions can fail because new reviewer-facing copy accidentally reintroduces forbidden UI labels or selector words. If CI says a removed label such as `English`, `Japanese`, or `Korean` reappeared, inspect both the new code and the test's intended guard before weakening the test; prefer changing the new internal/admin copy to neutral abbreviations (`EN`/`KO`/`JA`) or more specific wording so the guard remains meaningful. See `references/internal-route-followup-ci.md`.
- TypeScript failures around formatting helpers often indicate a source/display contract mismatch, especially optional metadata (`string | undefined`) being passed into a formatter that expects `string`. Preserve `undefined` for missing optional fields rather than formatting an empty or missing value unless the product contract explicitly says otherwise.
- Next.js typed routes can reject dynamic `Link href` values or router navigation values built from runtime strings, including `router.push(fallbackHref)` in client components. If the target route pattern is intentional and already covered by the App Router tree, prefer importing `type { Route } from "next"`, assigning the computed/fallback href once (for example `const fallbackRoute = fallbackHref as Route`), and passing that typed value to `Link` or `router.push`; avoid scattering inline casts through JSX or event handlers.
- When a typed-route fix changes a string that a source-contract test asserts, treat a follow-up test failure as a stale source-contract assertion before changing product code again. Update the test to assert the durable contract: non-submit control, history/back behavior, typed fallback route, and fallback navigation target.
- React Hooks lint failures such as `react-hooks/set-state-in-effect` on a client component that initializes local state from `localStorage` usually mean browser preference state should be modeled as an external store. If multiple components read the same preference, use `useSyncExternalStore` with a shared `readStored...` and `subscribe...` helper, dispatch a custom same-tab event after writes, and also subscribe to the `storage` event for cross-tab changes.
- After rebasing an existing PR onto latest `origin/main`, treat previously untouched legacy/detail routes as likely typecheck failure sites when the PR changes a shared schema or model. CI may fail on a stale page that still references an old field even if the rebase conflict was elsewhere. Inspect the exact `tsc` error, update the UI to the current schema field contract, and run the same typecheck command locally with the repo's required Node version when possible before pushing.
- Next.js `next typegen` / `next build` can rewrite generated route-reference files such as `next-env.d.ts` differently between dev/build modes. If that file changes only as a side effect of local verification and the task is not to update generated type references, inspect the diff and revert the local generated-file change before committing so the PR stays focused.

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

   - When squashing an existing PR branch after a rebase, do not run `git reset --soft origin/main` while additional working-tree edits are still unstaged and then assume the next commit captured everything.
   - Practical symptom: `git status --short --branch` shows `MM` paths after the soft reset, and the new commit includes the old PR delta but not the newest refactor/fix.
   - Safe pattern: before the soft reset, either commit/stash the new edits or stage/amend them immediately afterward; after the commit, require `git status --short` to be clean and compare `git diff --stat origin/<head-branch>..HEAD` / `git diff --stat origin/main...HEAD` before pushing.
   - If `git push --force-with-lease` is rejected with stale info because a parallel `fetch` or GitHub-side update moved the remote tracking ref, fetch/inspect the remote head and retry only after confirming your local branch intentionally replaces the remote PR head.
   - After rebases or force-pushes, verify remote branch refs directly before trusting PR metadata.
   - This applies both to stacked PR chains and to ordinary follow-up updates on an existing open PR.
   - If an open PR branch is stale and its diff against latest `origin/main` is polluted by many unrelated files, prefer a clean-replacement workflow over committing on top of the stale branch: create a temporary worktree from `origin/main`, apply only the intended scoped changes, run targeted checks, commit once, record the old remote tip with `git ls-remote`, force-with-lease push `HEAD` back to the same PR branch, then verify `gh pr view <pr> --json files` contains only the expected files.
   - If a docs/planning PR appears to include feature documents or other files that have since landed on `main`, treat those files as base content rather than PR payload. A safe recovery pattern is: fetch and fast-forward local `main`, abort any conflicted rebase, reset the PR worktree hard to `origin/main`, reapply only the intended surviving diff (for example by extracting a single file from the old PR branch), commit once, and force-with-lease back to the same PR head. Then refresh the PR body so it no longer claims the absorbed files are part of the PR.
   - After any rebase/clean-replacement push, fetch again before final reporting. `origin/main` can advance during the operation; if `git rev-list --left-right --count origin/main...origin/<branch>` becomes `1 1` or otherwise shows the PR is behind, rebase the same PR branch again onto the new `origin/main`, force-with-lease, and re-run the merge-base/file-list verification.
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
   - If the user asks to create a stacked PR on top of a specific parent PR, but that parent PR merges while you are preparing the child and its head branch is deleted, do not try to recreate or target the deleted parent branch. Treat the merged parent as already part of the base, rebase or recreate the child on latest `origin/main`, open the PR against `main`, and explicitly state in the PR body that it is a follow-up to the parent PR because the parent has merged. Verify the resulting diff against `origin/main...HEAD` so only the child delta remains.
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
    - when asked to sweep open PRs for conflicts/CI failures, do not stop after repairing the first PR. After each push, re-run the open-PR scan for `mergeStateStatus=DIRTY` and failed check conclusions (`FAILURE`, `ERROR`, `ACTION_REQUIRED`) because another open PR may become visible as conflicted once GitHub state refreshes or after the first branch is updated. For the concise end-to-end recipe, including the `origin/main`-advanced-during-sweep race and stale `BLOCKED` vs real conflict distinction, see `references/open-pr-conflict-sweep.md`.
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
   - When adding a new ordinary CI workflow by copying/paralleling a sibling repo, inspect the target repo's real package/workspace shape before writing the workflow. For nested apps, set `defaults.run.working-directory` and `cache-dependency-path` to the nested workspace (for example `front/` + `front/package-lock.json`) rather than assuming a root `package.json`.
   - Keep the sibling repo as a shape reference, not a blind source copy: preserve trigger/concurrency/runner patterns, but map commands to the target repo's actual scripts (`prisma:validate`, `lint`, `typecheck`, `test`, `build`, etc.) and runtime docs.
   - When a repository may grow multiple CI jobs, prefer a stable aggregate job (commonly named `CI result`) as the only required status check instead of requiring every individual CI/deploy job in repository settings. Implement the aggregate with `needs: [...]`, `if: ${{ always() }}`, and a small shell step that accepts only `success|skipped` upstream results; when adding future CI jobs, update the aggregate job's `needs` list and result-check step rather than changing branch protection every time.
   - If repository rulesets already require an individual check such as a deploy preview job, update the `required_status_checks` rule to the aggregate context after the aggregate workflow job exists or is being introduced in the same PR. Preserve existing ruleset conditions, bypass actors, pull-request parameters, and other rules when PATCH/PUT-ing via `gh api`; only replace the required status check context. Verify with `gh api repos/<owner>/<repo>/rulesets/<id> --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks'`.
   - For workflow-only CI additions, use static validation first (`git diff --check`, YAML parse, `actionlint .github/workflows/<file>.yml`) rather than spending time on local build/test when the user prefers fast PR creation.
   - When a workflow file is reusable (`on: workflow_call`) rather than directly dispatched by a human, make that role obvious in both the filename and the Actions display name. Prefer names such as `reusable-<purpose>.yml`, set `name:` to include `Reusable Workflow`, and add a short top-of-file Korean comment explaining that people should not run it directly because it is called by an upper-level workflow. This prevents reviewers/operators from confusing a reusable sub-workflow with a manual deploy button.
   - After opening the PR, verify fresh checks/runs attached to the PR head SHA. `gh pr checks` can exit non-zero while checks are merely pending; read the table/status and confirm with `gh run list --branch <branch> --json headSha,status,conclusion,url` before treating it as a failure.

9a. Manual deployed-URL E2E workflow, Node runtime upgrades, and WAF-aware throttling.

   - When a workflow run emits a warning like `Node.js 20 actions are deprecated` for `actions/checkout@v4`, `actions/setup-node@v4`, or `actions/upload-artifact@v4`, diagnose it as the JavaScript action runtime version, not the app/test `node-version`. Prefer upgrading the referenced first-party action majors to releases whose `action.yml` declares `runs.using: node24` rather than hiding the warning with `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` or opting out later with `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true`.
   - Keep the distinction explicit in PRs and user reports:
     - **Action runtime upgrade**: changes action majors such as `actions/checkout@v4` -> `@v6`, while preserving `node-version: '22'` or whatever app/test runtime the repo already uses.
     - **Repo/app Node runtime upgrade**: changes `actions/setup-node` inputs like `node-version: '22'` -> `'24'`, and may also declare `package.json` `engines.node`, update lockfile root metadata, and add `.nvmrc` / `.node-version` for local tool selection.
   - When the user asks to upgrade the repo to a Node LTS version, treat it as an app/CI runtime change, not merely an action-major cleanup. Keep the PR narrow but align the obvious sources of truth: workflow `node-version`, `package.json` `engines.node`, package-lock root package `engines`, and local version files if the repo does not already have a different version-management convention. Use `24.x` in `engines.node` when the intent is “Node 24 LTS major” rather than a specific patch.
   - For Node runtime PRs where the user wants to run verification later, do not spend time on local build/test. Use lightweight verification such as `git diff --check`, `actionlint .github/workflows/*.yml`, JSON parse checks for `package.json` / `package-lock.json`, grep for stale `node-version: '22'`, then push and report queued CI instead of waiting.
   - Verification pattern for that warning:
     ```bash
     # Discover old first-party action majors in workflows
     grep -R "actions/checkout@v4\|actions/setup-node@v4\|actions/upload-artifact@v4" .github/workflows || true

     # Confirm candidate releases run on node24 before editing
     for repo_tag in actions/checkout@v6.0.2 actions/setup-node@v6.4.0 actions/upload-artifact@v7.0.1; do
       repo=${repo_tag%@*}; tag=${repo_tag#*@}; tmp=$(mktemp -d)
       git clone --depth 1 --branch "$tag" "https://github.com/$repo.git" "$tmp/repo" >/dev/null 2>&1
       grep -n "using:" "$tmp/repo/action.yml"
       rm -rf "$tmp"
     done
     ```
   - If the warning is reported from one manual workflow but the same deprecated action majors remain in other workflow files, consider a narrow repo-wide workflow action-major update across `.github/workflows/*.yml`; otherwise the PR's own Validate/Deploy workflows may continue emitting the same warning. Keep behavior unchanged: do not alter workflow triggers, permissions, cache settings, or app/test Node versions unless needed.
   - Validate workflow-only action upgrades with `actionlint .github/workflows/*.yml`, `git diff --check`, and a final grep showing no remaining deprecated action refs. If the affected workflow is manual `workflow_dispatch`, dispatch it on the PR branch after push and report the run URL/current state without passively waiting.
   - If the workflow being upgraded is also the mechanism used to create the PR (for example a repo-standard `create-pr.yml` workflow), expect the PR-creation run itself to still execute from the default branch's old workflow until the PR merges. Do not treat that one last Node deprecation warning as proof the branch failed; verify the branch diff, confirm the upgraded action tag's `action.yml` declares `runs.using: node24`, and explain that future runs after merge will use the new runtime.
   - `actionlint` may surface unrelated pre-existing shellcheck warnings while validating an action-runtime-only change. If the fix is narrow and behavior-preserving, include it; otherwise report it separately rather than broadening the workflow PR into unrelated cleanup.

   - When a user asks to add a GitHub Actions workflow to run an already-merged E2E spec from a prior PR, treat the prior PR as context only if it is merged: start from latest `origin/main`, create a fresh branch/worktree, and add a narrow workflow-only PR instead of reviving the deleted old PR branch.
   - Prefer `workflow_dispatch` only when the user asks for manual execution. Do not add automatic `pull_request` or `push` triggers unless explicitly requested.
   - For deployed-runtime smoke tests that must run the same Playwright code against arbitrary deployments, use a separate no-`webServer` Playwright config and wire a workflow input such as `base_url` into `E2E_BASE_URL` (optionally also supporting `PLAYWRIGHT_BASE_URL`). Do not reuse a local E2E config that starts `next dev` when the goal is to test an already deployed URL. On Linux/self-hosted runners, install Playwright with OS dependencies (`npx playwright install --with-deps chromium`) unless the image is already known to include them; otherwise Chromium can fail before reaching the app with missing `libnspr4`/`libnss3`/`libasound2`. See `references/manual-runtime-smoke-playwright-workflow.md` for the concrete pattern, including Vercel Deployment Protection bypass headers and nested `front/` workspace wiring.
   - When the user asks for an E2E workflow against named already-deployed dev servers, do **not** reinterpret those servers as local server slots and do **not** add deployment, local `next dev`, PostgreSQL service containers, DB secrets, SSH tunnels, migrations, or Prisma helper setup unless explicitly requested. Prefer seeding only prerequisite login accounts via the deployment seed path, then let Playwright create a fresh Team and exercise the UI against `E2E_BASE_URL`. If the scenario later requires Gmail/Test Sender authentication, stop at that UI boundary and keep the sender-authenticated continuation as `test.skip` / TODO instead of fabricating sender identities through DB access. See `references/deployed-dev-server-e2e-seeded-account.md`.
   - Name manual deployed-URL E2E workflows/specs after the shared behavior under test, not necessarily after the representative endpoint used as the fixture. Example: if a common `gating-form` module is verified through one introduction-deck MDX URL, use files and scripts such as `e2e-gating-form-stage.yml`, `gating-form-stage.spec.ts`, and `test:e2e:gating-form:stage`; keep `introduction-deck` only in the target URL, selectors, or comments that describe the representative document.
   - If the E2E suite lives in a nested workspace such as `tests/`, set `defaults.run.working-directory: tests`, use `cache-dependency-path: tests/package-lock.json`, and run `npm ci` plus the browser install command from that workspace before invoking the existing package script.
   - Expose only safe runtime knobs as manual inputs, for example concurrency or max request rate inputs mapped to existing test environment variables. Avoid adding route/deploy behavior or modifying the app under test unless requested.
   - Upload Playwright artifacts with `if: always()` and paths rooted from the repository checkout, such as `tests/playwright-report/` and `tests/test-results/`, so failed manual runs are inspectable.
   - For workflow-only PR verification, prefer YAML parse + `actionlint` + `git diff --check`. If the referenced E2E is known to fail against the current deployed baseline, do not spend time running it locally just to reproduce the known failure; state that the workflow was statically validated and the E2E is expected to fail until the baseline issues are fixed.
   - If a deployed runtime smoke fails on `page.waitForResponse` or another navigation response event but the Playwright failure snapshot already shows the target authenticated page rendered correctly, treat it as a likely smoke synchronization problem before changing app code. Keep user-visible navigation assertions, then explicitly re-request the target route under the same authenticated browser session to preserve non-5xx response coverage. See `references/playwright-runtime-smoke-navigation-response.md`.
   - If a manual E2E workflow sweeps many deployed URLs, distinguish app failures from rate limiting before changing product code: inspect the Actions log for the first non-200, retries, and request settings; query Vercel runtime logs for the same environment/time window and explicit `403`/`429` status codes; direct-curl representative failed URLs after the burst. If runtime logs show the app returned 200 and no runtime 403/429 rows, treat the failure as WAF/rate-limit behavior and fix the E2E by lowering default request rate and disabling whole-suite retries for that script.
   - When a deployed-URL E2E sweep is governed by a known Vercel WAF rate limit, set the default request rate to a deliberate safety fraction of the real WAF limit rather than an arbitrary slow delay. Practical pattern from corp-web-app: WAF challenge threshold was `100 requests / 10s` for same `ip + user-agent`; the workflow default targeted 70% (`70 requests / 10s`) and exposed a manual input such as `sitemap_max_requests_per_10s`.
   - Implement throttling at the actual HTTP request-start boundary, not only after each logical URL item, so redirects/retries also count toward the limit. If concurrency is useful for slow network responses, keep a separate concurrency knob but make the global rate limiter authoritative. Example: `SITEMAP_E2E_CONCURRENCY=8` controls parallel in-flight URL checks, while `SITEMAP_E2E_MAX_REQUESTS_PER_10S=70` computes `ceil(10000 / 70)` milliseconds between stage request starts.
   - Log the effective concurrency, max requests per window, and request interval in the E2E output so Actions evidence explains the actual request rate. Document the manual workflow entry near the E2E script docs so future users know the spec can be launched from GitHub Actions UI and understand the WAF-aware default rate.
   - For sitemap-style deployed URL E2E, do not treat `sitemap.xml` as the only URL source when users report externally reachable entrypoints or known public links that are absent from the sitemap. Add a small fixture such as `tests/e2e/fixtures/required-public-urls.txt` (comments allowed, one URL per line), name it around the class of contract (`required public URLs`, not the incident), merge it with archived/live sitemap locs, and log separate counts for archived/live/required-public URLs.

9b. Production deploy workflow branch-source changes.

   - When changing a manual production deploy workflow from a release-branch promotion model to direct branch deployment, remove branch-mutation steps entirely instead of keeping a hidden `git checkout/rebase/push` phase.
   - When the requested pattern is “like querypie-docs/corp-web-japan” or another sibling repo, match the sibling implementation shape closely instead of inventing extra deploy-script behavior.
   - If the sibling workflow exposes a `workflow_dispatch` input such as `BRANCH` with default `main`, use that input directly, for example `BRANCH: ${{ inputs.BRANCH }}`, rather than `github.ref_name`. This makes the manual dispatch UI the source of the deployed branch and preserves the default-main behavior.
   - If the deploy script already reads `process.env.BRANCH` / `process.env.TARGET_ENV` and passes them to Vercel SDK `gitSource.ref` / `target`, do not add new env validation, target normalization, or helper abstractions unless the user explicitly asks for script hardening. The safer follow-up for a sibling-parity request is usually to leave the script unchanged and only adjust the workflow.
   - After removing push/rebase behavior, lower workflow permissions from `contents: write` to `contents: read` unless another remaining step still needs writes.
   - Compare against known-good sibling workflows and scripts when the user says "like repo X", and keep repo-specific secrets/vars intact unless the request explicitly includes normalizing those too.
   - When adding Vercel SDK deploy scripts/workflows for an existing project, keep workflow names visibly environment-specific and project-specific, and prefer verb-first deploy names (for example `Deploy <project> Preview` vs `Deploy <project> Production`) so the Actions UI makes the action, project, and Preview vs Production target obvious. Use matching verb-first workflow file names such as `deploy-<project>-preview.yml`. See `references/vercel-sdk-project-deploy-workflows.md` for the reusable script/workflow pattern.
   - When a manual `workflow_dispatch` entrypoint delegates to a reusable `workflow_call` workflow, name the reusable file with an explicit `reusable-` prefix rather than a vague `target` suffix. Example: keep the user-facing entrypoint as `deploy-tencent-container-image.yml`, and name the called workflow `reusable-deploy-tencent-container-image.yml`. After renaming, update every `uses: ./.github/workflows/<file>.yml` reference and any source/contract tests that read workflow files by path; validate with `git diff --check` and `actionlint` for the touched workflow files.
   - When a repository uses Prisma/Vercel with Preview and Production sharing one development DB, keep PR Preview deploy workflows read-only with respect to DB schema. Put actual shared DB migration/backfill execution behind a dedicated `workflow_dispatch` workflow with a direct DB URL secret, fixed DB-level concurrency, and environment protection. Do not add a redundant typed confirmation input (for example `APPLY <ENV> DB MIGRATION`) when manual dispatch plus a protected GitHub Environment is the intended safety gate, unless the user explicitly asks for that extra friction. Treat `prisma migrate resolve --applied <baseline>` as a one-time baseline adoption step, not something to run on every deploy. See `references/manual-shared-db-migration-workflows.md`.
   - For Prisma 7 read-only schema drift checks, do not use removed `migrate diff --from-url` / `--to-schema-datamodel` flags. Use `--from-config-datasource` / `--to-schema`, and make wrapper scripts inject the selected live DB URL through the datasource env that `prisma.config.ts` actually reads. See `references/prisma7-migrate-diff-schema-check.md` for the concrete recipe and local `.env`/`DATABASE_DIRECT_URL` pitfall.
   - When a shared Vercel Neon DB migration workflow fails because `DATABASE_DIRECT_URL` is empty, fix the GitHub Actions secret from the Neon direct/non-pooling URL, then distinguish live DB drift from missing committed Prisma migration artifacts. See `references/shared-db-neon-direct-url-and-migration-artifact-recovery.md`.
   - If CI fails in a source-contract test that enumerates Prisma migration artifacts after an intentional migration was added, update the test allowlist with the exact new migration directory instead of debugging schema behavior. See `references/prisma-migration-artifact-allowlist-ci.md`.
   - When moving a shared Vercel development DB from Neon Marketplace to Supabase Marketplace for region support, create/connect the Supabase resource, promote `POSTGRES_PRISMA_URL` to encrypted runtime `DATABASE_URL`, set the GitHub environment `DATABASE_DIRECT_URL` secret from `POSTGRES_URL_NON_POOLING`, remove recurring one-time `migrate resolve` steps, update seed safety away from Neon-only host checks, delete the old Neon resource only after migration/schema/seed verification, and refresh stale PR text. See `references/shared-db-supabase-marketplace-migration.md`.
   - See `references/workflow-dispatch-production-branch.md` for a concise migration recipe and verification checklist.

   - For Tencent VM container CD in container-image based repos, prefer a single build-and-deploy workflow for `main` push: build/push the immutable image once, expose the registry image as a job output, then call reusable per-VM deploy jobs with that exact image. Do not create an independent deploy workflow that recomputes the image tag or can race the build.
   - If the user says every `main` commit should deploy “that version”, avoid `push.paths` filters on the CD workflow; path filters can skip docs/config commits and leave deployment-revision checks behind `main`. Keep PR validation path filters if useful, but make `main` CD match the stated revision policy.
   - For PR validation of the same image workflow, do **not** imply that the PR build artifact/tag will be reused after merge: PR heads can be rebased/squash-merged and their commit IDs can change. Make PR behavior explicitly cache-only build validation (`docker buildx --output=type=cacheonly`), with no registry push and no VM deploy. Put this wording in the workflow `name`/`run-name`, job name, step summary, PR body, and runbook so reviewers see `PR Cache-Only Build Validation` rather than mistaking the check for a deployable artifact.
   - For automatic CD, protect VM-mutating jobs with `if: github.event_name == 'push' && github.ref == 'refs/heads/main'` so PR builds and manual validation runs do not deploy by accident. Preserve a separate manual deploy workflow for dry-run, explicit APPLY, and rollback/promotion of a known immutable tag.
   - When a reusable SSH deploy workflow uploads registry credentials to a VM, generate the env file from GitHub secrets/vars only and shell-escape values with `printf %q`; never write literal credentials into tracked workflow files or logs.
   - See `references/tencent-container-pr-cache-only-validation.md` for the detailed PR-cache-only vs final-main-deploy naming and workflow pattern.

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
   - When a follow-up review says one topic belongs in a separate document, update the same open docs PR branch rather than opening a new PR: move the detailed section into a focused sibling doc, leave the original doc scoped to its stated purpose, and add a short cross-link between the two docs so reviewers can see the boundary.
- When the user clarifies the intended scope of a planning/design document, treat that as a document-boundary correction, not just a prose tweak. Preserve the corrected purpose throughout the doc: update the purpose paragraph, top-level decision/summary tables, detailed rationale sections, and “next implementation order” entries so they no longer reintroduce the out-of-scope topic. If the extracted topic still matters, create or update a sibling doc for it and link both ways where useful.
- For technology-choice planning docs specifically, keep them centered on selected technologies, alternatives, pros/cons, and rationale. Put repository/app directory layout, app placement, or workspace boundaries in a separate layout/architecture doc unless the user explicitly wants those concerns combined.
   - For audit docs, update all dependent count tables together: scanned files, occurrences, distinct URLs/hosts, host breakdowns, and code-vs-content counts. Do not update only the obvious changed row.
   - For infra/current-state docs, collect live provider and host evidence before writing prose: cloud resource identity via the provider CLI, DNS/public HTTP(S) smoke, Security Group/firewall rules, SSH host service status, runtime listener bindings, certificate expiry/timer state, and deployed revision files. Replace stale pre-provisioning language such as “DNS/TLS 후속 작업” with observed final state, and distinguish host-local listeners from actual public exposure through firewall/Security Group rules.
   - For route/status docs, verify current source paths and public route files exist on latest main before repeating old guidance. If a preview `/t/*` route has been promoted/removed, update active guidance to the canonical public route while preserving historical commit-pinned examples only when they are explicitly before/after evidence.
   - When docs/manual refresh work adds previously missing locale files or otherwise changes fallback coverage, inspect source tests that intentionally assert fallback behavior. If the product contract changed from `missing locale falls back to English` to `all active slugs have requested-locale content`, update the test fixture/expectation to assert requested-locale metadata rather than treating the now-present localized file as a regression.
   - For active seed/demo-scenario planning PRs, treat requests like “add this contact list to all demo teams” or “prepare these message examples for every team” as canonical scenario documentation updates when the PR is explicitly docs/planning-only. Update the scenario source-of-truth, fixture/file-layout examples, acceptance criteria, and PR body consistently; do not broaden into seed-code/schema changes unless the user explicitly asks for implementation. If the user renames a demo asset (for example from an old placeholder Contact List name to `contact-staff`), grep the entire canonical doc and JSON/YAML snippets for stale names/slugs so completion criteria, demo flow steps, and asset checklist do not keep the old term.
   - When a merged guideline changes fixture examples from JSON to YAML, do not mechanically convert a large `demo-scenario.local.json` example into one large `demo-scenario.local.yaml` file. For human-reviewable demo seed planning docs, prefer entity-type split fixture examples with a `demo-` prefix such as `demo-users.local.yaml`, `demo-teams.local.yaml`, `demo-products.local.yaml`, `demo-campaigns.local.yaml`, and other `demo-<entity>.local.yaml` files as needed. Update both directory-layout docs and canonical scenario docs, and refresh the PR body so reviewers see the final naming/splitting convention.
   - When the user asks to finalize a documented decision and open a PR, treat it as a source-of-truth update, not just prose. For OpenSpec-style repositories, first locate the existing active change and `design.md` decision log; update the decision status/value there, then update the affected contract/spec requirements and any scope/task checklist text so design/spec/tasks do not drift. Only create a new change if no existing active change owns the decision.
   - If the user explicitly asks to update UI design docs and OpenSpec first, then proceed with the implementation in one PR, do not split the OpenSpec/doc correction into a separate PR even if the repository's default OpenSpec maintenance workflow prefers separation. Treat the user's request as an explicit same-scope exception: update the UI design terms/overview/common-widget docs, update the relevant `openspec/specs/**/spec.md` requirement/scenario, then implement the narrow code/CSS/test change on the same existing PR branch when one already covers that scope. Refresh the PR body so reviewers see the final doc+spec+implementation contract, not just the implementation diff.
   - If the user refines the product policy mid-session while you are already updating OpenSpec/docs and implementation in the same PR, immediately fold that refinement into the canonical contract before continuing code changes. Preserve explicitly retained invariants rather than over-deleting adjacent behavior. Example shape: if the requested change removes a Team classification/type, but the user clarifies that account creation must still bootstrap a default Personal Team, the spec/docs/tests should say “Personal Team is the default Team created at account bootstrap, not a schema type” before the code removes the type field.
   - When updating an active docs/planning PR to reference a fixture, source file, or implementation artifact that is being prepared in a separate PR, keep the current PR documentation-only unless the user explicitly asks to implement it. Document the dependency explicitly: name the future path, state that it is produced by the other PR, describe whether the current PR should wait for that PR to merge or be stacked on top of it, and add Product Owner questions for fallback behavior if the file is absent. Do not silently add placeholder fixture files to make the docs self-contained.
   - When a user iteratively supplies concrete demo-seed content such as contact-list names, message examples, release-note bullets, or public landing-page URLs for an existing docs/planning PR, update the same canonical document and PR branch rather than opening a new PR. Verify referenced public pages when possible, extract only the user-facing source lines needed for the example, and keep each locale/team's message subject, body, and CTA aligned with the provided source. If the PR's source branch becomes dirty/behind while doing these follow-ups, rebase onto latest `origin/main`, preserve the canonical move/delete intent, force-push with lease, and refresh the PR body so reviewers see the latest accepted examples.
- When the user explicitly asks to add or reshape a small fixture in the same docs/planning PR, update both the fixture file and the canonical doc that describes its schema/rows in the same branch. Preserve canonical machine-readable fields separately from source annotations: for example store `mailto:` prefixes in a notes/source field rather than in a normalized `email` column, and add dedicated display/source columns when the user asks for separate English/Korean names. Validate the fixture with a tiny parser script plus `git diff --check`, then push the existing PR branch and verify the PR head SHA; do not broaden into local app tests unless requested.
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
