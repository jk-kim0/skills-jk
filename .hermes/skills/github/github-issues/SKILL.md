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
- For preview-to-public migration tracking issues, explicitly add a required verification/fix stage before public rollout. That stage should check each preview page against the source webpage for complete content coverage, visual/UI parity, copied media/assets, CTA/link parity, interaction behavior, placeholder removal, code-structure consistency, and tests that defend the parity contract. Do not let the issue jump directly from “preview route exists” to “public local rendering” without this validation work.
- For such migration tracking issues, add an explicit “done criteria” section covering public route rendering, preview-route removal/retention policy, canonical metadata, sitemap, test updates, and confirmation that preview pages have already passed source-content/UI/code-consistency parity checks. This makes the issue maintainable as a long-lived tracking document rather than a one-off audit dump.
- When a user broadens scope from a single route/page implementation issue into a site-wide sequential migration program, rewrite the existing issue into a program-level tracking document instead of creating a second narrowly overlapping issue by default. Update the title/body to reflect the expanded scope, add a repo-derived inventory table of all current in-scope surfaces, explicitly mark non-scope references (for example social links that mention the platform but are not playback dependencies), and structure the remaining work as ordered phases/slices. For media-migration programs, the useful issue shape is: overall goal, shared architecture recommendation, current inventory from code search, explicit non-scope, phase-by-phase rollout plan, shared frontend/media contracts, and both per-slice and program-level done criteria.
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
- Practical comment replacement pitfall: `gh issue view <n> --json comments --jq '.comments[].id'` returns GraphQL node IDs such as `IC_...`, not REST numeric comment IDs. Deleting those with `gh api -X DELETE /repos/<owner>/<repo>/issues/comments/<id>` returns HTTP 404. For node IDs, delete comments with GraphQL: `gh api graphql -f query='mutation($id:ID!){deleteIssueComment(input:{id:$id}){clientMutationId}}' -f id="$id"`. If a REST numeric database ID is available, then the REST delete endpoint is fine.
- For very large audit issues, keep the main body as baseline/scope/summary/domain counts and split the full inventory into issue comments via `--body-file`. After posting, verify both body length and comment count/lengths with `gh issue view <n> --json body,comments --jq '{body_len:(.body|length),comments:(.comments|length),comment_lens:[.comments[].body|length]}'` so truncation or missing comments are caught immediately.
- For source-link or external-link audit issue rewrites, define the scan boundary before counting and encode it in the issue body. If the user narrows scope to implemented source surfaces, exclude dependency/library sources (`node_modules`, package-manager lockfiles, npm registry/package links), repo/process documentation (`docs/**`, `.agents/**`, `.github/**`), tests/fixtures, generated output, and guidance files unless explicitly requested. Prefer scanning tracked files from latest `origin/main`, filtering to implementation/content roots such as `src/**`, and separating first-party/owned hosts from third-party hosts so cleanup counts are not inflated by owned service domains.
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
- When a tracking issue originally proposed a specific implementation API or naming scheme, but the merged code settled on a different simpler API, do not preserve the old recommendation as open work. Rewrite it as “initial proposal vs final implementation”, document the current contract from code, and list follow-up only if there is an actual remaining mismatch.
- For issue updates that merely refresh status, do not close the issue unless the user explicitly asks. It is often useful to leave the issue open as a living contract/reference document while marking “no immediate code work remains.”
- When the user repeats a request such as "update issue #N" for a living audit/tracking issue that was already updated recently, do not assume no-op. Re-fetch `origin/main`, re-check the issue body, re-check related PRs/open follow-ups and the relevant file inventory, then edit the real issue again with the latest verification timestamp or explicit "no related open PRs / no required follow-up" status so the GitHub issue reflects that a fresh revalidation happened.
- For refactor/taxonomy tracking issues, explicitly compare the existing body against commits merged after the body's recorded baseline. Reclassify items that have since merged as completed, list only current root/main survivors as remaining, and separately call out related open PRs with their current mergeability/conflict status before recommending follow-up order.
- When the user asks to update a tracking issue "based on main" after issue-authored PRs have just been merged, rewrite the issue from a latest-`origin/main` snapshot rather than preserving the old planned PR breakdown. Move merged PR scopes into a "completed / reflected on main" section, remove or downgrade stale planned PRs, and keep only current remaining candidates. If a related PR was closed because its proposed direction was rejected or superseded, state the final decision and do not leave that PR's original scope as remaining work.
- When a refactor/tracking issue was originally framed around applying one shared primitive broadly, but latest main has evolved into several valid family-specific primitives, rewrite the issue around a family taxonomy instead of forcing the old primitive plan. Include: latest main SHA, stale route/name assumptions removed, each family’s representative routes/files/tests, the current shared primitive for that family, proposed new family-level primitives only where duplication remains, explicit non-scope for families that should not be merged, and PR breakdown by family. Update the issue title too if the old title still implies the stale single-primitive goal.
- When a user questions whether a listed remaining task is already done, immediately verify the live repo state (for example with `find`, `git ls-tree`, or targeted file searches) before answering. If the file/route/code no longer exists or the cleanup is already reflected on `origin/main`, remove the stale TODO from the issue, add a short "already resolved" note if useful, and do not leave duplicate/canonical cleanup language in the remaining-work section.
- For living audit/tracking issue refreshes in repos where the user prefers avoiding long local verification, it is acceptable to ground the issue update in the latest `origin/main` GitHub Actions run plus static inventory scans instead of rerunning local build/test commands. In that case, say so explicitly in the issue body (for example: "not locally rerun; based on successful CI for this head SHA + static inventory recalculation") and link the CI run/jobs used as evidence.
- When refreshing a taxonomy/reference issue after many route or primitive refactor PRs have merged, rewrite it around the current `origin/main` state rather than preserving the old TODO framing. Capture: latest SHA and timestamp, related child issue states, open PR list, current route/file inventory, newly introduced primitives or family boundaries, items removed from concern, and only concrete remaining follow-up candidates. If all child scopes are closed and no direct open PR remains, say that the issue is now a reference/taxonomy record rather than a broad implementation TODO.
- If a related open PR exists but it is a narrow refinement inside an already-settled family, list it explicitly as a related open PR without reopening the broad taxonomy/reference issue. State its exact scope boundary (for example, “legal MDX body typography refinement”) and say that it does not overturn the parent issue's completed family/broad primitive conclusion unless the PR actually changes that taxonomy.
- For preview/static route taxonomy issues, directly re-enumerate routes and renames from `origin/main` before editing (for example `git ls-tree -r --name-only origin/main src/app/t | grep '/page\.tsx$'`, `git diff --name-status <old-sha>..origin/main -- src/app/t src/components/sections tests`, and first-parent merge logs). Explicitly distinguish promoted public routes, removed preview routes, renamed preview route families, and routes that intentionally remain in a separate family. Do not leave stale `/t/*` or old namespace assumptions in the current-state section.
- If the latest `origin/main` tip is docs-only or otherwise has no fresh full CI run, distinguish the latest code-affecting CI evidence from the latest tip/deploy evidence. Record both rather than overstating the docs-only head as fully CI-validated: e.g. "latest code-affecting main CI success: <sha/run>; latest docs-only tip deploy success: <sha/run>; local build/test not rerun." Also list open docs-only PRs separately when they do not affect the tracked migration/product status.
- When a merged PR has partially or fully resolved an audit/tracking issue, rewrite the body around the current remaining issue instead of preserving stale broad recommendations. Add a short "completed" section for the merged PR, remove resolved concerns from remaining work, and narrow the next action to the smallest still-unverified boundary. If visual/browser verification was not rerun, state that explicitly rather than implying the merged code is visually validated.
- For technical-debt inventory issues that list orphan/stale component or route candidates, re-check current imports, route trees, and tests from `origin/main` before preserving the item as remaining work. If the candidate has been moved into an explicit family (for example an internal-demo/reference family), imported by a current route, and guarded by tests that document the old path removal/new path retention, remove it from open work and record it as resolved/justified instead of leaving a duplicate cleanup TODO.
- When refreshing a migration/tracking issue after route-rename PRs have merged, re-enumerate route existence directly from `origin/main` (`git ls-tree`, `git cat-file -e origin/main:<path>`, and targeted `git grep`) before editing. Move merged route-renames/deletions into a completed section, remove stale "target route" language from remaining work, and keep remaining work focused on the next real boundary such as public local rendering, metadata/sitemap, redirect policy, or parity checks.
- If the relevant `origin/main` CI run is still in progress, do not overstate verification as green. Record job-level status at edit time (for example scope/smoke/tests passed, build still in progress) and link the run so the issue remains truthful without waiting passively for long CI completion.
- If the user wants the issue itself to remain maintainable, add a top-of-body section that explains how future edits to that issue should be performed (for example: re-check latest `main`, keep the body in Korean only, distinguish generic primitives from concrete presets, and remove stale historical candidates). This is especially useful for long-lived audit/reference issues.
  1. Fetch latest `origin/main` and capture the new SHA.
  2. Diff `baseline..origin/main` scoped to the relevant directories before rewriting (for example `git diff --name-status <baseline>..origin/main -- src/app/t src/components/sections src/lib`).
  3. Inspect the first-parent history in that range so merged PR numbers and intent are explicit. Do not rely only on `git log --first-parent --merges`: repositories that use squash-merge have no merge commits in the relevant range. Prefer `git log --oneline --reverse <baseline>..origin/main` (squash commit subjects often include `(#123)`) and use `git diff --name-status <baseline>..origin/main -- <paths>` to ground the changed scope.
  4. Re-check related child issues by number (`gh issue view <n> --json state,title,url,updatedAt`) and reflect closed/open status in the parent body instead of leaving stale follow-up language.
  5. Re-enumerate the current file inventory/survivors from `origin/main` or a fast-forwarded main checkout, then rewrite the issue around current remaining concerns plus items intentionally removed from concern.
- If the user wants the issue itself to remain maintainable, add a top-of-body section that explains how future edits to that issue should be performed (for example: re-check latest `main`, keep the body in Korean only, distinguish generic primitives from concrete presets, and remove stale historical candidates). This is especially useful for long-lived audit/reference issues.
- For repo audit issues driven by user-supplied migration/parity rules, do not preserve already-invalidated "decision" bullets as if they were still open. If the user corrected the analysis (for example, shared CTA width is correct by policy, uniform cards are acceptable by policy, or a component name encodes product intent rather than route placement), rewrite those items out of the open-questions list and explicitly mark them as non-issues / out of scope instead.
- Practical audit-issue rewrite rule: separate the final body into `actual remaining issues` vs `items intentionally removed from concern`, so future readers do not reopen already-resolved policy questions.
- When leaving a remaining-work item in a living issue, make it concrete enough that a future implementer can understand the intended change without reconstructing the whole conversation. Include: target files/symbols, why the current state is mismatched, what may change, what must not change, and the decision still needed. For naming/alias cleanup items, explicitly distinguish whether the name describes product intent/purpose (e.g. “try AIP free”) versus route/page placement (e.g. “used only on AIP pages”); do not claim cross-family usage is a mismatch unless the product-intent reading is actually wrong. Also say whether UI copy, hrefs, layout, behavior, or product policy are out of scope.
- When a user challenges an issue's remaining-work classification or asks what a remaining item means, re-evaluate the underlying design model before defending the old finding. For responsive UI audit issues, do not preserve a one-page follow-up just because a measured width looks smaller; first decide whether the component is intentionally fluid (for example an equal-grid card gallery that divides available width into 1/2/3 columns with fixed-height rhythm). For component naming issues, first decide whether the name is purpose/product-oriented or route/family-oriented before recommending a rename. If the observed delta is actually a shared policy difference across multiple pages (for example live gutter 24px vs local primitive gutter 30px), rewrite it as a policy/non-issue note rather than a page-specific defect.
- When rewriting an issue after user correction, be explicit about the correction: move stale recommendations out of remaining work, document why they are now non-issues, and avoid language that implies an implementation PR is still expected when the current conclusion is “no immediate code work.”
- When a user narrows a migration/tracking issue's scope (for example preview `/t/*` implementation only, excluding public local rendering), rewrite the issue around that scope boundary rather than keeping old rollout tasks as remaining work. Add explicit `In scope` / `Out of scope` sections, remove excluded tasks from completion criteria, and if useful keep a short “removed previous remaining work” section so future readers do not treat the excluded rollout work as required by that issue.
- When the user asks to add a clarification or "명시해줘" to an existing issue after identifying that a PR contradicts the intended contract, prefer adding a focused issue comment rather than rewriting a long tracking issue body, unless they explicitly ask to edit the body. The comment should state the durable implementation contract, identify the non-goal/regression pattern, avoid auto-close keywords, and then be verified with `gh issue view ... --json comments --jq '.comments[-1]'` before returning the comment URL.
- When the user then asks to update or re-review the full issue from `main`, refresh the body from actual `origin/main` rather than the disputed PR branch: fetch `origin/main`, capture the current SHA, inspect open PRs, inspect recently merged/closed related PRs, and verify whether the disputed contract actually landed by reading the relevant files from `origin/main` with `git show origin/main:<path>` or `git cat-file -e`. If the contradicting PR was closed without merge, say that explicitly in the issue body and remove/avoid language that treats its changes as pending or accepted. For long migration issues, update the status table, completed checklist, remaining-work checklist, and verification notes together so the body is internally consistent.
- When the user asks to convert an existing issue into a repository guide or durable documentation, do the real repo workflow rather than only rewriting the issue:
  1. fetch latest `origin/main` and create a fresh non-main worktree/branch
  2. use the issue body as background, but rewrite it into final-state guidance based on the current implementation, not as an issue transcript
  3. place the guide under the repo's existing docs structure and link it from adjacent canonical docs so future readers can find it
  4. avoid auto-closing keywords in the PR body unless the user explicitly wants the issue closed
  5. after opening the PR, comment on the issue with the PR URL and a short description so the issue remains navigable
  6. for docs-only changes, `git diff --check` plus static link/content inspection can be sufficient when the repo/user prefers avoiding local test/build; still verify that GitHub checks attach to the PR head SHA and report their current state.

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
