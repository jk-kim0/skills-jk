# Debate Review Reference

## Placeholder Sources

**From orchestrator variables:** `{REPO}`, `{PR_NUMBER}`, `{ROUND}`

**From `init-round` output:** `{WORKTREE_PATH}`, `{HEAD_BRANCH}`, `{LEAD_AGENT_ID}`

**From file:** `{REVIEW_CRITERIA}` — contents of `$SKILL_ROOT/review-criteria.md`

**From `init` output:** `{OUTPUT_LANGUAGE}` (`language` field)

**From `build-context` output:** `{OPEN_ISSUES}`, `{DEBATE_LEDGER}`, `{PENDING_REBUTTALS}`, `{LEAD_REPORTS}`, `{CROSS_REBUTTALS}`, `{CROSS_FINDINGS}`, `{APPLICABLE_ISSUES}` — all returned as a single JSON object by `build-context --state-file --round N`.

**Removed (agents obtain directly):** `{PR_TITLE}`, `{PR_BODY}`, `{DIFF}`, `{REVIEW_CONTEXT}` — agents run `gh pr view`, `gh pr diff`, and explore the worktree themselves.
