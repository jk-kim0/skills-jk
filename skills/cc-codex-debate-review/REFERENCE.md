# Debate Review Reference

## Placeholder Sources

**From orchestrator variables:** `{REPO}`, `{PR_NUMBER}`, `{ROUND}`

**From external commands:**
- `{PR_TITLE}`, `{PR_BODY}`: `gh pr view --json title,body`
- `{DIFF}`: `gh pr diff "$PR_NUMBER" --repo "$REPO"`
- `{REVIEW_CRITERIA}`: Contents of `$SKILL_ROOT/review-criteria.md`

**From `init` output:** `{OUTPUT_LANGUAGE}` (`language` field)

**From `init-round` output:** `{LEAD_AGENT_ID}` (`lead_agent` field)

**From `build-context` output:** `{REVIEW_CONTEXT}`, `{OPEN_ISSUES}`, `{DEBATE_LEDGER}`, `{PENDING_REBUTTALS}`, `{LEAD_REPORTS}`, `{CROSS_REBUTTALS}`, `{CROSS_FINDINGS}`, `{APPLICABLE_ISSUES}` — all returned as a single JSON object by `build-context --state-file --round N`.
