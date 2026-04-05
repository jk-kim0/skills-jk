## Round {ROUND} — Lead Response + Code Application

### Rebuttals Against Your Findings

{CROSS_REBUTTALS_JSON}

For each: `withdraw` or `maintain`.
Use the provided `report_id` for each rebuttal decision. Do not substitute `issue_id` when a `report_id` is available.

### Cross-Verifier's New Findings

{CROSS_NEW_FINDINGS_JSON}

For each: `accept` or `maintain`.
Use the provided `report_id` for each cross-finding evaluation. Do not substitute `issue_id` when a `report_id` is available.

### Withdrawals

If you realize one of your own open issues is a duplicate of another open issue or is no longer valid, add a `withdrawals` entry. You may only withdraw issues you originally opened.

### Issues to Fix

{APPLICABLE_ISSUES_JSON}

### Potential Issues to Fix (if you accept cross-findings above)

{POTENTIAL_APPLICABLE_ISSUES_JSON}

These issues are from the cross-verifier's findings. If you `accept` them in Cross-Verifier's New Findings above, include them in your code application as well. Do NOT fix them if you chose `maintain` (reject).

If both "Issues to Fix" and accepted potential issues are empty, skip code application entirely — return empty `applied_issues`/`failed_issues` arrays and omit `commit_sha`.

### Code Application

1. Edit files in {WORKTREE_PATH}
2. `git add <files>` (only files you modified — do NOT use `git add -A` or `git add .`)
3. Prepare the issue result arrays, e.g.: `APPLIED_ISSUES_JSON='["isu_001"]'` and `FAILED_ISSUES_JSON='[]'`
4. `COMMIT_MSG=$("{DEBATE_REVIEW_BIN}" build-commit-message --state-file "{STATE_FILE}" --round {ROUND} --applied-issues "$APPLIED_ISSUES_JSON")`
5. `git commit -m "$COMMIT_MSG"`
6. `git push origin HEAD:{HEAD_BRANCH}`

### Output

```json
{"rebuttal_decisions": [...], "cross_finding_evaluations": [...], "withdrawals": [...], "application_result": {"applied_issues": [...], "failed_issues": [...], "commit_sha": "..."}}
```
