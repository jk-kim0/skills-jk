---
name: github-pr-activity-report
description: Build a date-bounded GitHub pull-request activity report for a user using gh CLI, with GraphQL fallback/pagination when gh search JSON fields are insufficient.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Pull Requests, Reporting, GraphQL, gh-cli, Weekly Report]
    related_skills: [github-auth, github-pr-workflow]
---

# GitHub PR Activity Report

Use this when the user asks for:
- weekly/monthly PR history
- all PRs opened in a date range
- repo-by-repo PR summaries
- a work-report based on GitHub PR activity

## Goal
Produce a grounded report from live GitHub data, not memory.

## Recommended flow

1. Confirm live environment and current date/time.
   - Use `pwd` and `date` first.
   - If the user gives a relative period like "지난주 월요일부터", compute the exact start date in the target timezone.

2. Load GitHub auth/reporting context.
   - Use `github-auth` and, if needed, `github-pr-workflow`.
   - Verify `gh auth status` and get the GitHub login with `gh api user --jq '.login'`.

3. Try lightweight search first, but expect schema limits.
   - `gh search prs` is fine for quick checks, but its `--json` fields are limited.
   - Important finding: `gh search prs --json` may not support fields like `mergedAt`, even though they are needed for reporting.

4. If `gh search prs` lacks required fields, switch to GraphQL immediately.
   - Use `gh api graphql` with a query over `search(query:$q, type:ISSUE, first:100, after:$after)`.
   - Search string pattern:
     - `is:pr author:<login> created:>=YYYY-MM-DD sort:created-desc`
   - Request fields such as:
     - `number, title, url, state, isDraft`
     - `createdAt, updatedAt, closedAt, mergedAt`
     - `additions, deletions, changedFiles`
     - `baseRefName, headRefName, reviewDecision`
     - `repository { nameWithOwner }`
     - `labels(first:20) { nodes { name } }`

5. Always implement pagination.
   - Even if the expected volume seems small, fetch until `hasNextPage` is false.
   - Save raw results to a temp JSON file before summarizing.

6. Build summary layers from the raw JSON.
   - Overall totals: PR count, merged/open/closed counts
   - By repo: counts and change volume
   - By day: created-at distribution
   - Open PR list
   - Title inventory per repo for manual theme grouping

7. Write the user-facing report by topic, not just by repo.
   - After collecting titles, group related PRs into workstreams such as:
     - content migration
     - contact/gating flows
     - static-page refactors
     - docs/skills/conventions
     - QA/E2E/performance/ops
   - Keep the final narrative grounded in actual PR titles and states.

## Example GraphQL pagination script

Use `execute_code` or shell+python. A Python snippet is often easiest:

```python
import json, subprocess, textwrap
query = textwrap.dedent('''
query($q:String!, $after:String) {
  search(query:$q, type:ISSUE, first:100, after:$after) {
    issueCount
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number title url state isDraft createdAt updatedAt closedAt mergedAt
        additions deletions changedFiles baseRefName headRefName reviewDecision
        repository { nameWithOwner }
        labels(first:20) { nodes { name } }
      }
    }
  }
}
''')
q = 'is:pr author:jk-kim0 created:>=2026-04-27 sort:created-desc'
all_nodes = []
after = None
while True:
    cmd = ['gh','api','graphql','-f',f'query={query}','-F',f'q={q}']
    if after:
        cmd += ['-F', f'after={after}']
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    s = data['data']['search']
    all_nodes.extend(s['nodes'])
    if not s['pageInfo']['hasNextPage']:
        break
    after = s['pageInfo']['endCursor']
print(json.dumps(all_nodes, ensure_ascii=False, indent=2))
```

## Practical guidance

- For relative Korean date requests like "지난주 월요일부터 지금까지", compute the date explicitly in KST instead of assuming UTC.
- Use `createdAt` as the inclusion criterion unless the user explicitly asks for merged/closed-in-range activity instead.
- Mention the basis in the report: author, time window, and whether the count is by creation date.
- If the user asks for "all PR history", include open PRs as well as merged ones unless they specify otherwise.
- If the raw output is too large, save it to `/tmp/...json` and summarize from that file.

## Pitfalls learned

1. `gh search prs --json` field support is narrower than expected.
   - Do not rely on it for `mergedAt`.
   - Switch to GraphQL instead of fighting the CLI.

2. Search volume can exceed 100 items.
   - Always paginate GraphQL search results.

3. Title-only summaries are not enough for a good work report.
   - Add repo counts, day counts, state counts, and change-volume totals.

4. Work reports read better by theme than by raw chronology.
   - Use the title inventory to cluster PRs into meaningful initiatives.

## Deliverable checklist

Before finishing, confirm the report includes:
- exact date range
- GitHub account used
- total PR count
- merged/open/closed counts
- repo-by-repo totals
- currently open PRs
- topic-based narrative summary
- optional report-ready prose block for copy/paste
