You are the lead agent responding to cross-verification for debate review round {ROUND} on {REPO}#{PR_NUMBER}.

## PR Information

**Title:** {PR_TITLE}

**Body:**
{PR_BODY}

## Review Context

{REVIEW_CONTEXT}

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

## Code Fixes

Provide unified diff patches for the issues below (consensus status: accepted, application status: pending or failed).

Notes:
- This prompt may not directly receive fork PR status.
- The orchestrator determines whether to apply `code_fixes` for fork PRs and may ignore them.
- If `{APPLICABLE_ISSUES}` is empty, output an empty array `[]`.

Issues to fix:
{APPLICABLE_ISSUES}

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
  "code_fixes": [
    { "issue_id": "isu_001", "file": "src/foo.ts", "description": "Fix description", "diff": "--- a/src/foo.ts\n+++ b/src/foo.ts\n@@ ... @@\n...\n+fixed code" }
  ]
}
```

- `rebuttal_decisions`: One entry per rebuttal in `{CROSS_REBUTTALS}`. Empty array `[]` if none.
- `cross_finding_evaluations`: One entry per finding in `{CROSS_FINDINGS}`. Empty array `[]` if none.
- `code_fixes`: Unified diff patches for issues to fix. Empty array `[]` if `{APPLICABLE_ISSUES}` is empty. The orchestrator may ignore this for fork PRs.

## Review Criteria

{REVIEW_CRITERIA}

## Diff

{DIFF}

Output only the JSON object above. No markdown, explanations, or preamble.
