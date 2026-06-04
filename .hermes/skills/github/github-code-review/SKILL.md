---
name: github-code-review
description: "Review PRs: diffs, inline comments via gh or REST."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Code-Review, Pull-Requests, Git, Quality]
    related_skills: [github-auth, github-pr-workflow]
---

# GitHub Code Review

Perform code reviews on local changes before pushing, or review open PRs on GitHub. Most of this skill uses plain `git` — the `gh`/`curl` split only matters for PR-level interactions.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository

### Setup (for PR interactions)

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Reviewing Local Changes (Pre-Push)

This is pure `git` — works everywhere, no API needed.

### Get the Diff

```bash
# Staged changes (what would be committed)
git diff --staged

# All changes vs main (what a PR would contain)
git diff main...HEAD

# File names only
git diff main...HEAD --name-only

# Stat summary (insertions/deletions per file)
git diff main...HEAD --stat
```

### Review Strategy

1. **Get the big picture first:**

```bash
git diff main...HEAD --stat
git log main..HEAD --oneline
```

2. **Review file by file** — use `read_file` on changed files for full context, and the diff to see what changed:

```bash
git diff main...HEAD -- src/auth/login.py
```

3. **Check for common issues:**

```bash
# Debug statements, TODOs, console.logs left behind
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|HACK\|XXX\|debugger"

# Large files accidentally staged
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10

# Secrets or credential patterns
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"

# Merge conflict markers
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```

4. **Present structured feedback** to the user.

### Review Output Format

When reviewing local changes, present findings in this structure:

```
## Code Review Summary

### Critical
- **src/auth.py:45** — SQL injection: user input passed directly to query.
  Suggestion: Use parameterized queries.

### Warnings
- **src/models/user.py:23** — Password stored in plaintext. Use bcrypt or argon2.
- **src/api/routes.py:112** — No rate limiting on login endpoint.

### Suggestions
- **src/utils/helpers.py:8** — Duplicates logic in `src/core/utils.py:34`. Consolidate.
- **tests/test_auth.py** — Missing edge case: expired token test.

### Looks Good
- Clean separation of concerns in the middleware layer
- Good test coverage for the happy path
```

---

## 2. Reviewing a Pull Request on GitHub

### View PR Details

**With gh:**

```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
```

**With git + curl:**

```bash
PR_NUMBER=123

# Get PR details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "
import sys, json
pr = json.load(sys.stdin)
print(f\"Title: {pr['title']}\")
print(f\"Author: {pr['user']['login']}\")
print(f\"Branch: {pr['head']['ref']} -> {pr['base']['ref']}\")
print(f\"State: {pr['state']}\")
print(f\"Body:\n{pr['body']}\")"

# List changed files
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

### Check Out PR Locally for Full Review

This works with plain `git` — no `gh` needed:

```bash
# Fetch the PR branch and check it out
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Now you can use read_file, search_files, run tests, etc.

# View diff against the base branch
git diff main...pr-123
```

**With gh (shortcut):**

```bash
gh pr checkout 123
```

### Leave Comments on a PR

**General PR comment — with gh:**

```bash
gh pr comment 123 --body "Overall looks good, a few suggestions below."
```

**General PR comment — with curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments \
  -d '{"body": "Overall looks good, a few suggestions below."}'
```

### Leave Inline Review Comments

**Single inline comment — with gh (via API):**

```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')

gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="This could be simplified with a list comprehension." \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

**Single inline comment — with curl:**

```bash
# Get the head commit SHA
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -d "{
    \"body\": \"This could be simplified with a list comprehension.\",
    \"path\": \"src/auth/login.py\",
    \"commit_id\": \"$HEAD_SHA\",
    \"line\": 45,
    \"side\": \"RIGHT\"
  }"
```

### Submit a Formal Review (Approve / Request Changes)

**With gh:**

```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
gh pr review 123 --comment --body "Some suggestions, nothing blocking."
```

**With curl — multi-comment review submitted atomically:**

```bash
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"COMMENT\",
    \"body\": \"Code review from Hermes Agent\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"Use parameterized queries to prevent SQL injection.\"},
      {\"path\": \"src/models/user.py\", \"line\": 23, \"body\": \"Hash passwords with bcrypt before storing.\"},
      {\"path\": \"tests/test_auth.py\", \"line\": 1, \"body\": \"Add test for expired token edge case.\"}
    ]
  }"
```

Event values: `"APPROVE"`, `"REQUEST_CHANGES"`, `"COMMENT"`

The `line` field refers to the line number in the *new* version of the file. For deleted lines, use `"side": "LEFT"`.

---

## 3. Review Checklist

When performing a code review (local or PR), systematically check:

### Correctness
- Does the code do what it claims?
- Edge cases handled (empty inputs, nulls, large data, concurrent access)?
- Error paths handled gracefully?
- When a PR adds automatic fallback/default generation for an optional user input, verify the fallback only applies to the intended implicit/default path. Explicit user-provided identifiers (slugs, names, keys, addresses) should usually keep their validation/error semantics instead of being silently rewritten to a random or adjusted value unless the spec explicitly says so.

### Security
- No hardcoded secrets, credentials, or API keys
- Input validation on user-facing inputs
- No SQL injection, XSS, or path traversal
- Auth/authz checks where needed

### Code Quality
- Clear naming (variables, functions, classes)
- No unnecessary complexity or premature abstraction
- DRY — no duplicated logic that should be extracted
- Functions are focused (single responsibility)
- For layout/refactor PRs, trace container-width ownership end-to-end instead of reviewing only the renamed/extracted wrapper. If a route previously wrapped both title and list/content inside one `max-w-*` container, an extracted intro/title wrapper must not leave the sibling list/content area unconstrained unless the wider layout is explicitly intended.
- For Next.js App Router layout PRs, distinguish styling opt-in from layout-shell replacement. A child route `layout.tsx` can add wrappers but cannot remove or replace an already-applied parent/root layout. If a PR changes `src/app/layout.tsx` or middleware to enable one endpoint, call out that the implementation touches global request/render paths even if the visible behavior is route-gated; the structurally isolated alternative is route groups with multiple root layouts, which usually has a much larger routing-tree diff.
- For Tailwind/App Router route-group foundation PRs, frame the review around architecture intent, not just file count. Multiple root layouts via route groups are appropriate when Tailwind routes must avoid inheriting legacy Header/Main/Footer chrome; they are overkill for utility-only adoption. Verify: route groups are URL-transparent, existing public URLs stay stable, middleware is not given avoidable styling/layout exceptions, route inventory/typegen understand grouped paths, smoke routes are noindex if internal, and the PR documents which new routes belong in `(legacy)` versus `(tailwind)`.

### Testing
- New code paths tested?
- Happy path and error cases covered?
- Tests readable and maintainable?
- For source-level contract tests that build regexes dynamically in JavaScript/TypeScript, verify the regex string actually preserves backslashes. Prefer regex literals for static patterns and `new RegExp(String.raw`...`)` or double-escaped strings for dynamic model/path names; plain template literals like ``new RegExp(`\\s`)`` can silently become `s`/backspace-style patterns and fail only in CI.

### Performance
- No N+1 queries or unnecessary loops
- Appropriate caching where beneficial
- No blocking operations in async code paths

### Documentation
- Public APIs documented
- Non-obvious logic has comments explaining "why"
- README updated if behavior changed

---

## 4. Pre-Push Review Workflow

When the user asks you to "review the code" or "check before pushing":

1. `git diff main...HEAD --stat` — see scope of changes
2. `git diff main...HEAD` — read the full diff
3. For each changed file, use `read_file` if you need more context
4. Apply the checklist above
5. Present findings in the structured format (Critical / Warnings / Suggestions / Looks Good)
6. If critical issues found, offer to fix them before the user pushes

---

## 5. PR Review Workflow (End-to-End)

When the user asks you to "review PR #N", "look at this PR", or gives you a PR URL, follow this recipe:

### Step 1: Set up environment

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# Or run the inline setup block from the top of this skill
```

### Step 2: Gather PR context

Get the PR metadata, description, and list of changed files to understand scope before diving into code.

**With gh:**
```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checks 123
```

**With curl:**
```bash
PR_NUMBER=123

# PR details (title, author, description, branch)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER

# Changed files with line counts
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/files
```

### Step 3: Check out the PR locally

This gives you full access to `read_file`, `search_files`, and the ability to run tests.

```bash
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER
```

### Step 4: Read the diff and understand changes

```bash
# Full diff against the base branch
git diff main...HEAD

# Or file-by-file for large PRs
git diff main...HEAD --name-only
# Then for each file:
git diff main...HEAD -- path/to/file.py
```

For each changed file, use `read_file` to see full context around the changes — diffs alone can miss issues visible only with surrounding code.

### Step 5: Run automated checks locally (if applicable)

```bash
# Run tests if there's a test suite
python -m pytest 2>&1 | tail -20
# or: npm test, cargo test, go test ./..., etc.

# Run linter if configured
ruff check . 2>&1 | head -30
# or: eslint, clippy, etc.
```

### Step 6: Apply the review checklist (Section 3)

Go through each category: Correctness, Security, Code Quality, Testing, Performance, Documentation.

### Step 7: Post the review to GitHub

Collect your findings and submit them as a formal review with inline comments.

**With gh:**
```bash
# If no issues — approve
gh pr review $PR_NUMBER --approve --body "Reviewed by Hermes Agent. Code looks clean — good test coverage, no security concerns."

# If issues found — request changes with inline comments
gh pr review $PR_NUMBER --request-changes --body "Found a few issues — see inline comments."
```

**With curl — atomic review with multiple inline comments:**
```bash
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

# Build the review JSON — event is APPROVE, REQUEST_CHANGES, or COMMENT
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"REQUEST_CHANGES\",
    \"body\": \"## Hermes Agent Review\n\nFound 2 issues, 1 suggestion. See inline comments.\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"🔴 **Critical:** User input passed directly to SQL query — use parameterized queries.\"},
      {\"path\": \"src/models.py\", \"line\": 23, \"body\": \"⚠️ **Warning:** Password stored without hashing.\"},
      {\"path\": \"src/utils.py\", \"line\": 8, \"body\": \"💡 **Suggestion:** This duplicates logic in core/utils.py:34.\"}
    ]
  }"
```

### Step 8: Also post a summary comment

In addition to inline comments, leave a top-level summary so the PR author gets the full picture at a glance. Use the review output format from `references/review-output-template.md`.

**With gh:**
```bash
gh pr comment $PR_NUMBER --body "$(cat <<'EOF'
## Code Review Summary

**Verdict: Changes Requested** (2 issues, 1 suggestion)

### 🔴 Critical
- **src/auth.py:45** — SQL injection vulnerability

### ⚠️ Warnings
- **src/models.py:23** — Plaintext password storage

### 💡 Suggestions
- **src/utils.py:8** — Duplicated logic, consider consolidating

### ✅ Looks Good
- Clean API design
- Good error handling in the middleware layer

---
*Reviewed by Hermes Agent*
EOF
)"
```

### Ready-for-Review UI Screenshot Comment Sweep

When an open PR is not a draft (`isDraft == false`, i.e. Ready for Review), inspect the PR body before ordinary review work. If the body contains a dedicated `UI 변경` section, run the UI screenshot evidence workflow and post a PR comment with screenshots or a blocker note.

Use this for manual PR review and for scheduled sweeps. Do not run it for draft PRs, closed PRs, merged PRs, or PRs whose `UI 변경` section is absent or explicitly says there is no UI change.

Required behavior:

1. List open PRs and filter to Ready for Review only:

```bash
gh pr list --state open --json number,title,isDraft,body,headRefName,headRefOid,url
```

2. For each filtered PR, parse the body for a Markdown heading whose text is exactly or clearly `UI 변경`.
   - Accept common heading forms such as `## UI 변경`, `### UI 변경`, or a repository-specific section title that begins with `UI 변경`.
   - Only use paths and instructions inside that section; do not infer unrelated routes unless the user explicitly requested that.
   - If the section says `없음`, `N/A`, `No UI changes`, or equivalent, skip the PR.
3. Avoid duplicate work by keying comments to the exact PR head commit.
   - Before any screenshot capture, inspect existing PR comments with `gh pr view <number> --json comments` or `gh api repos/$OWNER/$REPO/issues/<number>/comments`.
   - Treat a prior comment as automation-owned only when it contains the stable marker `Hermes UI Screenshot Evidence` and a machine-readable `Head: <sha>` line.
   - If an automation-owned comment already has `Head: <current headRefOid>`, skip the PR entirely: do not recapture screenshots, do not upload attachments, and do not post another comment.
   - If automation-owned comments exist but all of them reference older head SHAs, the PR has changed since the last screenshot pass. Re-run capture for the current head and post a new comment. Do not edit or delete the old comment; the new comment supersedes it by naming the current head SHA.
   - If the PR body `UI 변경` section changed but the head SHA did not change, skip by default because GitHub PR body edits do not create a new renderable deployment. Only rerun in that case when the user explicitly asks for a recapture or when the previous automation-owned comment was a blocker caused by missing/ambiguous body instructions that are now fixed.
   - Include both `Head: <headRefOid>` and `Evidence-Key: ui-screenshot:<PR number>:<headRefOid>` in every posted comment so future runs can make an idempotent decision.
4. Capture screenshot evidence for every listed path that is reasonably reviewable.
   - Resolve `Before:` to the stable/base deployment and `After:` to the PR preview deployment.
   - Include full clickable URLs with scheme, host, and path for every `Before:` and `After:` entry.
   - Use the same viewport, authentication/session state, and wait strategy for before/after screenshots.
   - For auth-protected or stateful pages, either authenticate with the repo-approved demo account or post a blocker note describing exactly what prevented capture.
5. Upload/attach screenshots through the repository-approved GitHub attachment path, then post a top-level PR comment.
6. If capture fails, still post a short blocker/evidence comment instead of silently skipping a PR whose Ready-for-Review body requested UI evidence.
7. Never merge, close, mark ready, approve, or request changes as part of this screenshot sweep. The sweep only posts screenshot evidence comments or blocker comments.

Suggested comment shape:

```md
## Hermes UI Screenshot Evidence

Head: <headRefOid>
Evidence-Key: ui-screenshot:<PR number>:<headRefOid>
Source: Ready-for-Review PR body `UI 변경` section

### `<path>`
Before: https://stable.example.com/<path>
After: https://preview.example.com/<path>

![Before](...)
![After](...)

Notes:
- <visible result, blocker, auth redirect, server error, or DOM/style verification>
```

#### 30-minute Hermes cron registration

Use Hermes cron for an autonomous sweep. Prefer a Hermes profile that has cron configuration plus the browser/screenshot-capable toolsets needed by the evidence workflow. On this user's `skills-jk` setup, start from `hermes -p cron-config`; if screenshots require browser automation, ensure the created cron job also has browser-capable toolsets/profile configuration rather than relying on the default lean CLI profile.

Create the job from the target repository root, using the repository path as `--workdir` and this skill as an explicit preload:

```bash
REPO_DIR="/absolute/path/to/repo"

prompt=$(cat <<'EOF'
Open PR UI screenshot sweep:

1. Work in the configured repository.
2. List all open pull requests.
3. Process only PRs that are Ready for Review (`isDraft == false`). Skip draft, closed, and merged PRs.
4. For each Ready for Review PR, inspect the body for a dedicated `UI 변경` section.
5. If the section is absent or explicitly says no UI changes, skip and do not comment.
6. Before any screenshot capture, inspect existing comments for `Hermes UI Screenshot Evidence` and `Evidence-Key: ui-screenshot:<PR number>:<current head SHA>`.
7. If that exact evidence key already exists, skip the PR without recapturing, uploading, or commenting.
8. If older `Hermes UI Screenshot Evidence` comments exist for older head SHAs, treat the PR as changed: capture fresh Before/After evidence for the current head and post a new superseding comment. Do not edit or delete older evidence comments.
9. If the section exists and lists UI paths/states, capture Before/After screenshot evidence for the listed paths using the repository's stable/base deployment and the PR preview deployment.
10. Post a top-level PR comment with marker `Hermes UI Screenshot Evidence`, `Head: <current head SHA>`, `Evidence-Key: ui-screenshot:<PR number>:<current head SHA>`, full Before/After URLs, uploaded screenshot links, and any blocker notes.
11. Do not approve, request changes, merge, close, mark ready, edit PR bodies, or modify repository files.
EOF
)

hermes -p cron-config cron create \
  --name "ready-pr-ui-screenshot-sweep" \
  --deliver local \
  --skill github-code-review \
  --workdir "$REPO_DIR" \
  "30m" \
  "$prompt"
```

After creation, verify the scheduler record:

```bash
hermes -p cron-config cron list --all
hermes -p cron-config cron status
```

If the CLI-created job does not expose or persist required toolsets for screenshot capture, edit the job through the cron UI/tooling and verify these fields before relying on it:

- `enabled: true`
- `schedule: 30m`
- `skills` includes `github-code-review`
- `workdir` is the target repo root
- `deliver` is the intended destination (`local` unless a messaging channel is required)
- browser/screenshot-capable toolsets are enabled for the cron execution context
- GitHub auth and any attachment/upload helper required by the repository are available in that execution context

### Step 9: Clean up

```bash
git checkout main
git branch -D pr-$PR_NUMBER
```

### Decision: Approve vs Request Changes vs Comment

- **Approve** — no critical or warning-level issues, only minor suggestions or all clear
- **Request Changes** — any critical or warning-level issue that should be fixed before merge
- **Comment** — observations and suggestions, but nothing blocking (use when you're unsure or the PR is a draft)
