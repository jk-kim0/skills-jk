# Living audit issue refresh from latest main

Use this reference when a user asks to update an existing tracking/audit issue after follow-up PRs have merged.

## Pattern

1. Fetch latest main and capture the SHA.
   - `git fetch origin main --prune`
   - `git rev-parse origin/main`
2. Read the current issue body before editing.
   - `gh issue view <n> --json title,state,body,comments,updatedAt,url > /tmp/issue.json`
3. Identify issue-scope paths from the body and repo context.
4. Re-enumerate changes after the issue's old baseline or triggering PR.
   - `git log --oneline --reverse <baseline>..origin/main -- <paths...>`
   - `git diff --name-status <baseline>..origin/main -- <paths...>`
5. Inspect recently merged PR bodies for what was actually claimed and verified.
   - `gh pr view <n> --json title,state,mergedAt,url,body,headRefOid`
6. Check whether related open PRs still affect the same scope.
   - `gh pr list --state open --search '<keywords>' --json number,title,url,headRefName,isDraft,updatedAt`
7. Check relevant CI/deploy evidence for the latest main SHA and/or final merged PR head SHA.
   - `gh run list --branch main --commit <sha> --json ...`
   - `gh run list --commit <pr_head_sha> --json ...`
8. Rewrite the issue body around current facts:
   - latest baseline SHA/time
   - verification basis
   - completed follow-up PRs
   - current source/test/doc inventory
   - remaining concrete work only
   - explicit out-of-scope boundaries
   - note if local build/test/browser verification was not rerun
9. Verify the edit.
   - `gh issue edit <n> --body-file <file>`
   - `gh issue view <n> --json title,body,url,updatedAt`

## Good final shape

- The issue should not preserve old broad recommendations if main already addressed them.
- Move resolved findings into a completed/current-state section.
- If no immediate code change remains, say the issue is now a reference/audit record rather than a broad implementation TODO.
- Do not close the issue unless the user explicitly asks.

## Example evidence language

`Local build/test was not rerun for this issue refresh. This update is based on latest origin/main static source inventory plus the relevant successful GitHub Actions runs linked below.`
