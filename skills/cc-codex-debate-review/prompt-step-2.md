## Round {ROUND} — Cross-Verification

You are the CROSS-VERIFIER this round.

### Lead's Findings

{LEAD_FINDINGS_JSON}

For each: `accept` or `rebut` with reason.
Use the provided `report_id` for each cross-verification decision. Do not substitute `issue_id` when a `report_id` is available.

**Important:** Only include `report_id` values from the Lead's Findings above. Do NOT create or fabricate new `report_id` values.

### Task

Report your own additional findings not raised by the lead.

Re-raise rule: To re-raise an issue recorded as `withdrawn` in the Debate Ledger,
you must provide new evidence different from the original withdrawal reason.

Before reporting a finding, check the Debate Ledger:
- Do NOT report code added as a fix for a previously accepted issue
- Do NOT report something that is working correctly
- If unsure, err on the side of not reporting

**Duplicate detection:** If you notice an open issue you previously opened that describes the same root cause as another issue, add a `withdrawals` entry for your redundant issue.

### Debate Ledger

{DEBATE_LEDGER_TEXT}

### Output

```json
{"cross_verifications": [...], "withdrawals": [...], "findings": [...]}
```
