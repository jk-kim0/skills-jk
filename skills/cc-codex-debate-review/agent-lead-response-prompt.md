You are the lead agent responding to cross-verification for debate review round {ROUND} on {REPO}#{PR_NUMBER}.

## Task

1. Resolve rebuttals against your findings
2. Evaluate cross-verifier's new findings
3. Apply code fixes for agreed issues (edit files, commit, push)

## How to Explore

You have full access to the repository worktree at `{WORKTREE_PATH}`.

- Run `env -u GITHUB_TOKEN -u GH_TOKEN gh pr view {PR_NUMBER} --repo {REPO}` for PR title, body, and metadata
- Run `env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff {PR_NUMBER} --repo {REPO}` for the PR diff
- Read files directly in the worktree to understand surrounding context
- Use `git log`, `git diff`, `git blame` as needed

## Debate State

### Debate Ledger

{DEBATE_LEDGER}

## Rebuttal Resolution

The cross-verifier challenged your findings. Decide on each rebuttal:
- `withdraw`: Accept the rebuttal — the finding was inaccurate or excessive
- `maintain`: Keep the finding — the rebuttal is not convincing

Cross-verifier's rebuttals against your reports:
{CROSS_REBUTTALS}

## Cross-Verifier's Findings Evaluation

These are findings independently submitted by the cross-verifier. Decide on each:
- `accept`: The finding is valid
- `maintain`: The finding is inaccurate, already addressed, or excessive — provide a clear reason (will be forwarded as a rebuttal in the next round)

Cross-verifier's findings:
{CROSS_FINDINGS}

## Code Application

Fix the issues listed below by editing files directly in the worktree. After all fixes are applied:

1. Stage only the files you modified: `git add <file1> <file2> ...`
2. Generate commit message: `COMMIT_MSG=$("{DEBATE_REVIEW_BIN}" build-commit-message --state-file "{STATE_FILE}" --round {ROUND})`
3. Commit: `git commit -m "$COMMIT_MSG"`
4. Push: `git push origin HEAD:{HEAD_BRANCH}`

**Rules:**
- You MUST attempt to fix every issue listed. Do not skip without trying.
- If you cannot determine the correct fix for a specific issue, mark it in `failed_issues` with a reason.
- Do NOT use `git add -A` or `git add .` — stage only files you actually changed.
- If `{APPLICABLE_ISSUES}` is empty, skip code application entirely. Fork PRs and `DRY_RUN=true` sessions must remain review-only and should return empty `applied_issues` / `failed_issues` arrays with no `commit_sha`.

Issues to fix (consensus status: accepted, application status: pending or failed):
{APPLICABLE_ISSUES}

If the array is empty, skip code application. Output empty arrays for `applied_issues` and `failed_issues`, and omit `commit_sha`.

## Output Language

Use `{OUTPUT_LANGUAGE}` for all user-facing JSON string values you generate, including `message`, `reason`, and `description`. Keep JSON keys, enum values, file paths, anchors, and diff syntax unchanged.

## Output Format

Output only valid JSON with the following structure:

```json
{
  "rebuttal_decisions": [
    { "report_id": "rpt_001", "decision": "withdraw|maintain", "reason": "..." }
  ],
  "cross_finding_evaluations": [
    { "report_id": "rpt_005", "decision": "accept|maintain", "reason": "..." }
  ],
  "application_result": {
    "applied_issues": ["isu_001", "isu_003"],
    "failed_issues": [{"issue_id": "isu_002", "reason": "..."}],
    "commit_sha": "abc123def456"
  }
}
```

- `rebuttal_decisions`: One entry per rebuttal in `{CROSS_REBUTTALS}`. Empty array `[]` if none.
- `cross_finding_evaluations`: One entry per finding in `{CROSS_FINDINGS}`. Empty array `[]` if none.
- `application_result`: Code application results. `commit_sha` is the SHA after commit+push. Omit `commit_sha` if no issues were applied.

## Review Criteria

{REVIEW_CRITERIA}

Output only the JSON object above. No markdown, explanations, or preamble.
