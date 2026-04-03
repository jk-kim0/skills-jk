## Round {ROUND} — Cross-Verification

You are the CROSS-VERIFIER this round.

### Lead's Findings

{LEAD_FINDINGS_JSON}

For each: `accept` or `rebut` with reason.

### Task

Report your own additional findings not raised by the lead.

Re-raise rule: To re-raise an issue recorded as `withdrawn` in the Debate Ledger,
you must provide new evidence different from the original withdrawal reason.

Before reporting a finding, check the Debate Ledger:
- Do NOT report code added as a fix for a previously accepted issue
- Do NOT report something that is working correctly
- If unsure, err on the side of not reporting

### Debate Ledger

{DEBATE_LEDGER_TEXT}

### Output

```json
{"cross_verifications": [...], "findings": [...]}
```
