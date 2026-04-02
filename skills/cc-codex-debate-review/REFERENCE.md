# Debate Review Reference

## Placeholder Sources

**From orchestrator variables:** `{REPO}`, `{PR_NUMBER}`, `{ROUND}`

**From `init-round` output:** `{WORKTREE_PATH}`, `{HEAD_BRANCH}`, `{LEAD_AGENT_ID}`

**From file:** `{REVIEW_CRITERIA}` — contents of `$SKILL_ROOT/review-criteria.md`

**From `init` output:** `{OUTPUT_LANGUAGE}` (`language` field)

**From `build-context` output:** `{OPEN_ISSUES}`, `{DEBATE_LEDGER}`, `{PENDING_REBUTTALS}`, `{LEAD_REPORTS}`, `{CROSS_REBUTTALS}`, `{CROSS_FINDINGS}`, `{APPLICABLE_ISSUES}` — all returned as a single JSON object by `build-context --state-file --round N`.

**Persistent mode (`show --json`)**: step message state data comes from `show --state-file "$STATE_FILE" --json`; use `issues` for open/applicable issue filtering, `debate_ledger` for ledger text, and `persistent_agents` for restart/recovery handle lookup. Step-specific findings and rebuttals still come from the previous agent JSON outputs, not `build-context`.

**Removed (agents obtain directly):** `{PR_TITLE}`, `{PR_BODY}`, `{DIFF}`, `{REVIEW_CONTEXT}` — agents run `gh pr view`, `gh pr diff`, and explore the worktree themselves.

## Persistent Agent Handles

Persistent mode stores live agent identifiers in the state file under `persistent_agents`:

- `persistent_agents.cc_agent_id`
- `persistent_agents.codex_session_id`

Write them immediately after agent creation with:

```bash
"$DEBATE_REVIEW_BIN" record-agent-sessions \
  --state-file "$STATE_FILE" \
  --cc-agent-id "$CC_AGENT_ID" \
  --codex-session-id "$CODEX_SESSION_ID"
```

On restart, load those fields from the state file (or `show --json`) before attempting the live-agent fast path.
