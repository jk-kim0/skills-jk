## Round {ROUND} — Lead Review

You are the LEAD reviewer this round.

### Pending Rebuttals (Step 1a)

{PENDING_REBUTTALS_JSON}

If empty, skip rebuttal resolution.
For each: decide `withdraw` (accept rebuttal) or `maintain` (keep finding).

### Task (Step 1b)

Review the PR diff. Report new findings by severity: critical, warning, suggestion.

Rules:
- Do NOT re-report withdrawn issues unless you have new evidence
- Do NOT report code added as a fix for a previously accepted issue
- If unsure, err on the side of not reporting

### Current Open Issues

{OPEN_ISSUES_JSON}

### Debate Ledger

{DEBATE_LEDGER_TEXT}

### Verdict

- 0 new findings + open issues is empty → `no_findings_mergeable`
- Otherwise → `has_findings`

### Output

```json
{"rebuttal_responses": [...], "findings": [...], "verdict": "..."}
```
