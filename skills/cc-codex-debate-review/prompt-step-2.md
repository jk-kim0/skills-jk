## Round {ROUND} — Cross-Verification

You are the CROSS-VERIFIER this round.

### Lead's Findings

{LEAD_FINDINGS_JSON}

For each: `accept` or `rebut` with reason.
Use the provided `report_id` for each verification decision. Do not substitute `issue_id` when a `report_id` is available.

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

Each `cross_verifications` entry must use `report_id` and `decision`:

```json
{
  "cross_verifications": [
    {"report_id": "rpt_001", "decision": "accept", "reason": "..."},
    {"report_id": "rpt_002", "decision": "rebut", "reason": "..."}
  ],
  "withdrawals": [
    {"issue_id": "isu_001", "reason": "..."}
  ],
  "findings": [
    {"severity": "...", "criterion": 0, "file": "...", "line": 0, "anchor": "...", "message": "..."}
  ]
}
