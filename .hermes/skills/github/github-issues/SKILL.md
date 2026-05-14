---
name: github-issues
description: "Create, triage, label, assign GitHub issues via gh or REST."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Issues, Project-Management, Bug-Tracking, Triage]
    related_skills: [github-auth, github-pr-workflow]
---

# GitHub Issues Management

Create, search, triage, and manage GitHub issues. Each section shows `gh` first, then the `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repo with a GitHub remote, or specify the repo explicitly

### Setup

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

## 1. Viewing Issues

**With gh:**

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**With curl:**

```bash
# List open issues
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:  # GitHub API returns PRs in /issues too
        labels = ', '.join(l['name'] for l in i['labels'])
        print(f\"#{i['number']:5}  {i['state']:6}  {labels:30}  {i['title']}\")"

# Filter by label
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&labels=bug&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"

# View a specific issue
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  | python3 -c "
import sys, json
i = json.load(sys.stdin)
labels = ', '.join(l['name'] for l in i['labels'])
assignees = ', '.join(a['login'] for a in i['assignees'])
print(f\"#{i['number']}: {i['title']}\")
print(f\"State: {i['state']}  Labels: {labels}  Assignees: {assignees}\")
print(f\"Author: {i['user']['login']}  Created: {i['created_at']}\")
print(f\"\n{i['body']}\")"

# Search issues
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/search/issues?q=authentication+error+repo:$OWNER/$REPO" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin)['items']:
    print(f\"#{i['number']}  {i['state']:6}  {i['title']}\")"
```

## 2. Creating Issues

**With gh:**

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description
After logging in, users always land on /dashboard.

## Steps to Reproduce
1. Navigate to /settings while logged out
2. Get redirected to /login?next=/settings
3. Log in
4. Actual: redirected to /dashboard (should go to /settings)

## Expected Behavior
Respect the ?next= query parameter." \
  --label "bug,backend" \
  --assignee "username"
```

### Practical drafting patterns

- Prefer `--body-file <path>` over long inline shell strings when the issue body is more than a few lines, includes markdown tables, or contains bilingual text.
- When updating an existing issue that functions as a living audit / tracking document, re-check the latest `main` / `origin/main` state first, rerun the relevant verification commands, and replace stale findings instead of appending new notes on top of resolved ones.
- If local `main` cannot be fast-forwarded to `origin/main` because the current checkout has uncommitted or conflicting work, do not treat that stale checkout as the audit baseline. Create a detached worktree at `origin/main`, rerun the validation there, and rewrite the issue from that clean latest-main snapshot.
- For audit/tracking issue rewrites, explicitly refresh counts, open-PR references, and failure/success command results from the current repo state. Do not carry forward numbers or failure claims from an older session without revalidation.
- For migration tracking issues that compare an upstream product/site/repo against the current implementation, include one concise table that maps: upstream endpoint/source file, current local preview or implementation endpoint/file, current public endpoint behavior, completion status/percentage, and remaining work. Ground the table in static source scans plus lightweight live endpoint checks when available, and separate “preview implemented” from “public replacement complete” so a preview-only route is not overstated as done.
- For such migration tracking issues, add an explicit “done criteria” section covering public route rendering, preview-route removal/retention policy, canonical metadata, sitemap, and test updates. This makes the issue maintainable as a long-lived tracking document rather than a one-off audit dump.
- Practical `gh issue edit --body-file` pitfall: when editing from a detached worktree or alternate cwd, ensure the body file path is resolvable from that cwd. Prefer an absolute path or write the draft inside the active worktree before calling `gh issue edit`.
- If the user wants the issue to be easily rewritten again in a future session, prepend a short maintainer section that states the issue goal, the minimum revalidation steps, and which sections must be refreshed on rewrite.
- When creating a child issue from a parent analysis issue, explicitly link it near the top with plain text like `Parent issue: #397`.
- Practical GitHub CLI note: on some repos / installations, `gh issue` flows may not expose a reliable parent-child linking action for regular issues. Do not block on finding a dedicated `parent` flag.
- Fallback contract for those cases:
  1. create the child issue with a top-of-body `Parent issue: #397` link
  2. comment on the parent with the new child issue number and a one-line summary
  3. if the repo uses Projects/sub-issues features and a dedicated parent-linking path is later available, that can be added separately; the plain-text parent link plus parent comment is the minimum robust path
- After creating the child issue, comment on the parent with the new child issue number and a one-line summary so the parent thread stays navigable.
- Shell-quoting pitfall for `gh issue comment --body ...`: if the body contains backticks, bracket expressions, or shell-like tokens such as ``max-w-[920px]``, do **not** wrap the whole body in double quotes. The shell can treat backticks as command substitution before `gh` runs. Prefer a `--body-file` or wrap the whole body in single quotes when no nested single-quote content is needed.
- When the repository or user prefers bilingual issue bodies, structure the body as:
  1. English section first
  2. separator such as `---`
  3. translated Japanese/Korean section below
- If the user explicitly asks for a single-language issue body instead, follow that request even if your default habit is bilingual.
- Do not over-apply adjacent repo language norms from PRs/docs/comments to issues. If the user asks for an issue body in Korean (or another single language), write the issue in that language directly even if PR titles/descriptions or repo-internal docs are usually English.
- If the user explicitly says not to switch the issue into English/Japanese or not to make it bilingual, treat that as a hard formatting constraint and rewrite the actual issue body accordingly.
- If the user asks to "write issue #N in Korean" (or another language) and the issue already exists, default to editing the real existing issue into that requested language rather than drafting new text only.
- Unless the user explicitly limits the request to the body only, localize the issue title too so the visible issue state is consistently in the requested language.
- After editing, immediately verify with `gh issue view N --json title,body,url` and return the URL.
- CLI verification pitfall: do not pipe `gh issue view --json ...` into `python3 - <<'PY' ...` because the here-doc consumes stdin and the JSON pipe will be lost. Prefer writing JSON to a temp file first (`gh issue view ... > /tmp/issue.json && python3 -c 'import json; ...'`) or use `python3 -c` directly on the pipe.
- When the issue is meant to establish a future refactor taxonomy or naming scheme, encode the exact naming constraints in the issue body itself instead of leaving them implicit. Example pattern: explicitly state whether temporary route prefixes such as `t-` are allowed only in app routes and forbidden in component/test family names.
- If a semantic family has already been identified during analysis (for example CTA purpose such as free trial vs trust vs contact), write the follow-up issue around the implementation decision for that family, not just the inventory. This produces clearer implementation-scoped child issues.
- For analysis or commonization work, classify findings by semantic intent first (for example CTA purpose such as free trial vs trust vs contact) before grouping by component implementation. This produces better follow-up issue boundaries.
- When rewriting an existing issue into a current-state reference document, first re-audit the latest `main`/`origin/main` state, remove stale future-tense plan text that is no longer true, and rewrite the body around current facts plus narrowly scoped follow-up candidates.
- When rewriting an existing issue into a current-state reference document, first re-audit the latest `main`/`origin/main` state, remove stale future-tense plan text that is no longer true, and rewrite the body around current facts plus narrowly scoped follow-up candidates.
- When the user repeats a request such as "update issue #N" for a living audit/tracking issue that was already updated recently, do not assume no-op. Re-fetch `origin/main`, re-check the issue body, re-check related PRs/open follow-ups and the relevant file inventory, then edit the real issue again with the latest verification timestamp or explicit "no related open PRs / no required follow-up" status so the GitHub issue reflects that a fresh revalidation happened.
- For refactor/taxonomy tracking issues, explicitly compare the existing body against commits merged after the body's recorded baseline. Reclassify items that have since merged as completed, list only current root/main survivors as remaining, and separately call out related open PRs with their current mergeability/conflict status before recommending follow-up order.
- When a user questions whether a listed remaining task is already done, immediately verify the live repo state (for example with `find`, `git ls-tree`, or targeted file searches) before answering. If the file/route/code no longer exists or the cleanup is already reflected on `origin/main`, remove the stale TODO from the issue, add a short "already resolved" note if useful, and do not leave duplicate/canonical cleanup language in the remaining-work section.
- For living audit/tracking issue refreshes in repos where the user prefers avoiding long local verification, it is acceptable to ground the issue update in the latest `origin/main` GitHub Actions run plus static inventory scans instead of rerunning local build/test commands. In that case, say so explicitly in the issue body (for example: "not locally rerun; based on successful CI for this head SHA + static inventory recalculation") and link the CI run/jobs used as evidence.
- If the user wants the issue itself to remain maintainable, add a top-of-body section that explains how future edits to that issue should be performed (for example: re-check latest `main`, keep the body in Korean only, distinguish generic primitives from concrete presets, and remove stale historical candidates). This is especially useful for long-lived audit/reference issues.
  1. Fetch latest `origin/main` and capture the new SHA.
  2. Diff `baseline..origin/main` scoped to the relevant directories before rewriting (for example `git diff --name-status <baseline>..origin/main -- src/app/t src/components/sections src/lib`).
  3. Inspect the first-parent merge log in that range so merged PR numbers and intent are explicit.
  4. Re-check related child issues by number (`gh issue view <n> --json state,title,url,updatedAt`) and reflect closed/open status in the parent body instead of leaving stale follow-up language.
  5. Re-enumerate the current file inventory/survivors from `origin/main` or a fast-forwarded main checkout, then rewrite the issue around current remaining concerns plus items intentionally removed from concern.
- If the user wants the issue itself to remain maintainable, add a top-of-body section that explains how future edits to that issue should be performed (for example: re-check latest `main`, keep the body in Korean only, distinguish generic primitives from concrete presets, and remove stale historical candidates). This is especially useful for long-lived audit/reference issues.
- For repo audit issues driven by user-supplied migration/parity rules, do not preserve already-invalidated "decision" bullets as if they were still open. If the user corrected the analysis (for example, shared CTA width is correct by policy, or uniform cards are acceptable by policy), rewrite those items out of the open-questions list and explicitly mark them as non-issues / out of scope instead.
- Practical audit-issue rewrite rule: separate the final body into `actual remaining issues` vs `items intentionally removed from concern`, so future readers do not reopen already-resolved policy questions.

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{
    "title": "Login redirect ignores ?next= parameter",
    "body": "## Description\nAfter logging in, users always land on /dashboard.\n\n## Steps to Reproduce\n1. Navigate to /settings while logged out\n2. Get redirected to /login?next=/settings\n3. Log in\n4. Actual: redirected to /dashboard\n\n## Expected Behavior\nRespect the ?next= query parameter.",
    "labels": ["bug", "backend"],
    "assignees": ["username"]
  }'
```

### Bug Report Template

```
## Bug Description
<What's happening>

## Steps to Reproduce
1. <step>
2. <step>

## Expected Behavior
<What should happen>

## Actual Behavior
<What actually happens>

## Environment
- OS: <os>
- Version: <version>
```

### Feature Request Template

```
## Feature Description
<What you want>

## Motivation
<Why this would be useful>

## Proposed Solution
<How it could work>

## Alternatives Considered
<Other approaches>
```

## Important execution rule for issue-writing requests

When the user asks for something like:
- "write this as a GitHub issue"
- "create an issue"
- "open a GitHub issue"
- "github issue 로 작성해줘"

interpret that as a request to create or update the actual GitHub issue unless the user explicitly asks for a draft only.

Do **not** stop at writing a local markdown draft or issue-body proposal when the repository and GitHub CLI are available.

Preferred sequence:
1. Check `gh auth status`
2. Check for obvious duplicates if useful
3. Create or edit the real issue with `gh issue create` or `gh issue edit`
4. Return the issue URL

If you need a local body file for safety or easier editing, that file is only an intermediate artifact. Finish by publishing the real issue in the same session.

Important style rule:
- If the user explicitly requests the issue language or format, follow that request directly.
- Do not substitute a different language or downgrade the task into a draft-only response unless the user asked for that.

## 3. Managing Issues

Before drafting an issue, check for repo-local guidance and user preferences about language, translation order, and how to quote on-page copy.

Common pitfalls:
- Do not assume all GitHub issues should be written in English. Some repos or users want Korean or another language for issue bodies.
- If the task involves webpage copy in Japanese, preserve the exact Japanese source text and pair it with a Korean translation when the user requests that format.
- Treat issue-writing requests as formatting-sensitive work: if the user specifies a language or bilingual structure, follow it literally instead of falling back to a generic template.

Practical rule:
1. Determine the repo/user language preference for the issue body.
2. If the user specifies a bilingual structure, keep that structure consistently throughout the body.
3. When quoting UI or website text, use the exact source wording from the page and add the requested translation immediately adjacent to it.

## 3. Managing Issues

### Add/Remove Labels

**With gh:**

```bash
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --remove-label "needs-triage"
```

**With curl:**

```bash
# Add labels
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels \
  -d '{"labels": ["priority:high", "bug"]}'

# Remove a label
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels/needs-triage

# List available labels in the repo
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/labels \
  | python3 -c "
import sys, json
for l in json.load(sys.stdin):
    print(f\"  {l['name']:30}  {l.get('description', '')}\")"
```

### Assignment

**With gh:**

```bash
gh issue edit 42 --add-assignee username
gh issue edit 42 --add-assignee @me
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/assignees \
  -d '{"assignees": ["username"]}'
```

### Commenting

**With gh:**

```bash
gh issue comment 42 --body "Investigated — root cause is in auth middleware. Working on a fix."
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/comments \
  -d '{"body": "Investigated — root cause is in auth middleware. Working on a fix."}'
```

### Closing and Reopening

**With gh:**

```bash
gh issue close 42
gh issue close 42 --reason "not planned"
gh issue reopen 42
```

**With curl:**

```bash
# Close
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "closed", "state_reason": "completed"}'

# Reopen
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "open"}'
```

### Linking Issues to PRs

Issues are automatically closed when a PR merges with the right keywords in the body:

```
Closes #42
Fixes #42
Resolves #42
```

To create a branch from an issue:

**With gh:**

```bash
gh issue develop 42 --checkout
```

**With git (manual equivalent):**

```bash
git checkout main && git pull origin main
git checkout -b fix/issue-42-login-redirect
```

## 4. Issue Triage Workflow

When asked to triage issues:

1. **List untriaged issues:**

```bash
# With gh
gh issue list --label "needs-triage" --state open

# With curl
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?labels=needs-triage&state=open" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"
```

2. **Read and categorize** each issue (view details, understand the bug/feature)

3. **Apply labels and priority** (see Managing Issues above)

4. **Assign** if the owner is clear

5. **Comment with triage notes** if needed

## 5. Bulk Operations

For batch operations, combine API calls with shell scripting:

**With gh:**

```bash
# Close all issues with a specific label
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

**With curl:**

```bash
# List issue numbers with a label, then close each
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?labels=wontfix&state=open" \
  | python3 -c "import sys,json; [print(i['number']) for i in json.load(sys.stdin)]" \
  | while read num; do
    curl -s -X PATCH \
      -H "Authorization: token $GITHUB_TOKEN" \
      https://api.github.com/repos/$OWNER/$REPO/issues/$num \
      -d '{"state": "closed", "state_reason": "not_planned"}'
    echo "Closed #$num"
  done
```

## Quick Reference Table

| Action | gh | curl endpoint |
|--------|-----|--------------|
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| View issue | `gh issue view N` | `GET /repos/{o}/{r}/issues/N` |
| Create issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| Add labels | `gh issue edit N --add-label ...` | `POST /repos/{o}/{r}/issues/N/labels` |
| Assign | `gh issue edit N --add-assignee ...` | `POST /repos/{o}/{r}/issues/N/assignees` |
| Comment | `gh issue comment N --body ...` | `POST /repos/{o}/{r}/issues/N/comments` |
| Close | `gh issue close N` | `PATCH /repos/{o}/{r}/issues/N` |
| Search | `gh issue list --search "..."` | `GET /search/issues?q=...` |
