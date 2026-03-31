---
name: cc-codex-debate-review
description: Debate-driven PR review orchestration where CC and Codex alternate as lead agent until consensus is reached
---

# CC-Codex Debate Review

## Overview

A system where Claude Code (CC) and Codex repeatedly review, rebut, and fix an open PR until both agents reach the same conclusion on all issues.

CC is both the orchestrator and the even-round lead agent. Codex is a subprocess invoked via `codex exec` and the odd-round lead agent.

**State management is handled by the CLI.** CC calls `$DEBATE_REVIEW_BIN` subcommands to manipulate state and only performs the review itself (generating findings, making rebuttal decisions).

```
CC (orchestrator)
  ├─ $DEBATE_REVIEW_BIN <subcommand> → state management (CLI)
  ├─ codex exec ...                  → Codex invocation (odd lead, even cross)
  └─ CC self-review                  → even lead, odd cross
```

## When to Use

- When consensus-based review by two agents is needed for a PR
- Example invocation: `run debate-review (repo=owner/repo, pr=123)`

## Inputs

All paths below are relative to the `cc-codex-debate-review/` directory.

| Input | Path |
|-------|------|
| CLI | `./bin/debate-review` |
| Config file | `./config.yml` |
| Review criteria | `./review-criteria.md` |
| Codex prompts | `./codex-*.md` |

### Prerequisites

- Local clone of the target repo required
- `gh auth` authentication complete
- `codex` CLI available
- `$DEBATE_REVIEW_BIN` executable

## GitHub CLI Rules

All `gh` calls inside the CLI strip injected token variables and use keyring authentication. CC must follow the same rule when calling `gh` directly:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh <subcommand>
```

---

## Procedure

### 1. Initialization

#### Setup + Initialize Session

```bash
SKILL_ROOT="<path-to-cc-codex-debate-review>"
DEBATE_REVIEW_BIN="$SKILL_ROOT/bin/debate-review"
CONFIG_FILE="$SKILL_ROOT/config.yml"
```

`REPO` (e.g., `owner/repo`) and `PR_NUMBER` are required arguments. Abort immediately if either is missing.

```bash
RESULT=$("$DEBATE_REVIEW_BIN" init --repo "$REPO" --pr "$PR_NUMBER" \
  --config "$CONFIG_FILE")
STATE_FILE=$(echo "$RESULT" | jq -r '.state_file')
STATUS=$(echo "$RESULT" | jq -r '.status')           # "created" | "resumed"
CURRENT_ROUND=$(echo "$RESULT" | jq -r '.current_round')
IS_FORK=$(echo "$RESULT" | jq -r '.is_fork')
DRY_RUN=$(echo "$RESULT" | jq -r '.dry_run')
CODEX_SANDBOX=$(echo "$RESULT" | jq -r '.codex_sandbox')
LANGUAGE=$(echo "$RESULT" | jq -r '.language')
```

`LANGUAGE` is passed to LLM prompts via `{OUTPUT_LANGUAGE}` to control user-facing output language. CLI-generated templates, skill instructions, and Codex prompts are always in English.

If `STATUS` is `resumed`, the response also includes `next_step` and optionally `resume_context` — see **Restart Rules** below.

---

### 2. Round Loop

After initialization, start loop from `CURRENT_ROUND`. Each round:

1. Step 0: Sync PR HEAD
2. Determine lead agent + initialize round
3. Step 1: Lead agent review (1a: resolve pending rebuttals → 1b: new review + verdict)
4. Step 2: Cross-verifier cross-verification (skipped on clean pass)
5. Step 3: Lead agent response + code application (skipped on clean pass)
6. Step 4: Settlement

---

### Step 0: Sync PR HEAD

```bash
SYNC_RESULT=$("$DEBATE_REVIEW_BIN" sync-head --state-file "$STATE_FILE")
```

The CLI handles git fetch, worktree management, and supersede detection.

If `SYNC_RESULT` contains `external_change: true`, a supersede occurred. The CLI has already reset issue states and incremented `current_round`, so CC reads the latest state via `show --json`, updates `CURRENT_ROUND`, and proceeds with the new round.

```bash
if [ "$(echo "$SYNC_RESULT" | jq -r '.external_change')" = "true" ]; then
  STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json)
  CURRENT_ROUND=$(echo "$STATE_JSON" | jq -r '.current_round')
fi
```

---

### Round Initialization

The CLI auto-determines lead agent (odd=Codex, even=CC) and returns all environment variables:

```bash
SYNCED_SHA=$(echo "$SYNC_RESULT" | jq -r '.post_sync_sha')
ROUND_RESULT=$("$DEBATE_REVIEW_BIN" init-round \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --synced-head-sha "$SYNCED_SHA")
LEAD_AGENT=$(echo "$ROUND_RESULT" | jq -r '.lead_agent')
CROSS_VERIFIER=$(echo "$ROUND_RESULT" | jq -r '.cross_verifier')
WORKTREE_PATH=$(echo "$ROUND_RESULT" | jq -r '.worktree_path')
HEAD_BRANCH=$(echo "$ROUND_RESULT" | jq -r '.head_branch')
```

---

### Step 1: Lead Agent Review

#### Step 1a: Resolve Pending Rebuttals

If rebuttals from the previous round exist, the lead agent decides `withdraw` or `maintain` for each.

Previous round rebuttals are available via `build-context` output's `pending_rebuttals` field.

Once the lead agent (CC or Codex) makes decisions:

```bash
"$DEBATE_REVIEW_BIN" resolve-rebuttals \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --step "1a" \
  --decisions '[{"report_id": "rpt_003", "decision": "withdraw", "reason": "Rebuttal accepted"}]'
```

Findings decided as `maintain` must be re-reported in Step 1b.

The CLI response includes a `re_report_ids` array with report IDs decided as `maintain`. These issues must be included in Step 1b findings.

Skip if no previous round exists or no rebuttals are pending.

#### Step 1b: New Review

**When Codex is lead (odd rounds):**

> **Important:** `codex-lead-review-prompt.md` handles Step 1a (rebuttal resolution) and Step 1b (new review) in **a single invocation**. From the Codex response, route `rebuttal_responses` to `resolve-rebuttals --step "1a"`, `findings` to `upsert-issue`, and `verdict` to `record-verdict`.

1. Build review context (CC generates from state data)
2. Read prompt template: `./codex-lead-review-prompt.md` (`$SKILL_ROOT/codex-lead-review-prompt.md`)
3. Substitute placeholders: `{REPO}`, `{PR_NUMBER}`, `{PR_TITLE}`, `{PR_BODY}`, `{ROUND}`, `{REVIEW_CONTEXT}`, `{DEBATE_LEDGER}`, `{OPEN_ISSUES}`, `{PENDING_REBUTTALS}`, `{OUTPUT_LANGUAGE}`, `{REVIEW_CRITERIA}`, `{DIFF}`
4. Obtain PR diff:
   ```bash
   DIFF=$(env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff "$PR_NUMBER" --repo "$REPO")
   ```
5. Execute Codex:
   ```bash
   cd "$WORKTREE_PATH"
   # Save prompt to temp file and pass via stdin (avoid ARG_MAX overflow)
   PROMPT_FILE=$(mktemp /tmp/debate-prompt-XXXXXX.txt)
   printf '%s' "$FILLED_PROMPT" > "$PROMPT_FILE"
   codex exec -s "$CODEX_SANDBOX" - < "$PROMPT_FILE"
   rm -f "$PROMPT_FILE"
   ```
6. Parse JSON response (retry up to 3 times on failure)
7. Route response:
   - `rebuttal_responses` → `resolve-rebuttals --step "1a"` (if non-empty)
   - `findings` → record each via `upsert-issue`
   - `verdict` → `record-verdict`

**When CC is lead (even rounds):**

CC directly reads the diff, review context, and review criteria to perform the review. Output format is the same JSON structure as Codex. CC must use `state["language"]` for all user-facing output (findings messages, reasons, descriptions), matching the same language constraint applied to Codex via `{OUTPUT_LANGUAGE}`.

#### Record Findings

Call `upsert-issue` for each finding from the lead agent:

```bash
"$DEBATE_REVIEW_BIN" upsert-issue \
  --state-file "$STATE_FILE" \
  --agent "$LEAD_AGENT" \
  --round "$CURRENT_ROUND" \
  --severity "critical" \
  --criterion 1 \
  --file "src/foo.ts" \
  --line 42 \
  --anchor "validate_input" \
  --message "Missing input validation"
```

`anchor` should prefer symbol names, function names, or other identifiers less sensitive to line shifts. Use `line<N>` if none exists.

#### Record Verdict

```bash
"$DEBATE_REVIEW_BIN" record-verdict \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --verdict "has_findings"
```

**Clean pass determination:** If findings are 0 and all existing issues are resolved:
- `--verdict "no_findings_mergeable"`
- Skip Steps 2, 3 and proceed to Step 4

---

### Step 2: Cross-Verifier Cross-Verification

**Precondition:** Only execute when not a clean pass.

The cross-verifier performs two tasks:
1. `accept` or `rebut` each of the lead's reports
2. Report its own new findings

**When Codex is cross-verifier (even rounds):**

Prompt template: `./codex-cross-verify-prompt.md` (`$SKILL_ROOT/codex-cross-verify-prompt.md`)
Placeholders: `{LEAD_AGENT_ID}`, `{LEAD_REPORTS}` plus common ones.

**When CC is cross-verifier (odd rounds):**

CC directly evaluates the lead's reports and generates its own findings. CC must use `state["language"]` for all user-facing output, matching the same language constraint applied to Codex via `{OUTPUT_LANGUAGE}`.

#### Record Cross-Verification Results

```bash
"$DEBATE_REVIEW_BIN" record-cross-verification \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --verifications '[
    {"report_id": "rpt_001", "decision": "accept", "reason": "Valid finding"},
    {"report_id": "rpt_002", "decision": "rebut", "reason": "Intentional duplication"}
  ]'
```

#### Record Cross-Verifier's New Findings

Each new finding from the cross-verifier is also recorded via `upsert-issue`:

```bash
"$DEBATE_REVIEW_BIN" upsert-issue \
  --state-file "$STATE_FILE" \
  --agent "$CROSS_VERIFIER" \
  --round "$CURRENT_ROUND" \
  --severity "warning" \
  --criterion 7 \
  --file "src/config.ts" \
  --line 15 \
  --anchor "TIMEOUT" \
  --message "Hardcoded timeout value"
```

The CLI automatically routes step1/step2 tracking based on the agent role.

---

### Step 3: Lead Agent Response + Code Application

**Precondition:** Only execute when not a clean pass.

The lead agent handles three things:
1. Respond to cross-verifier's rebuttals (withdraw/maintain)
2. Evaluate cross-verifier's new findings (accept/maintain)
3. Apply code fixes for agreed issues (same-repo PRs only)

**When Codex is lead:**

Prompt template: `./codex-lead-response-prompt.md` (`$SKILL_ROOT/codex-lead-response-prompt.md`)
Placeholders: `{CROSS_REBUTTALS}`, `{CROSS_FINDINGS}`, `{APPLICABLE_ISSUES}` plus common ones.

**When CC is lead:**

CC directly handles rebuttal resolution, cross findings evaluation, and code modifications. CC must use `state["language"]` for all user-facing output, matching the same language constraint applied to Codex via `{OUTPUT_LANGUAGE}`.

#### Record Rebuttal Responses + Cross Findings Evaluation

The lead agent handles two tasks:
1. Respond to cross-verifier's rebuttals: `withdraw` (accept) or `maintain` (reject, forwarded as rebuttal in the next round)
2. Evaluate cross-verifier's new findings: `accept` (add to consensus) or `maintain` (reject, forwarded as rebuttal in the next round)

Record all decisions in a single `resolve-rebuttals --step "3"` call:

```bash
"$DEBATE_REVIEW_BIN" resolve-rebuttals \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --step "3" \
  --decisions '[
    {"report_id": "rpt_002", "decision": "withdraw", "reason": "Rebuttal accepted"},
    {"report_id": "rpt_005", "decision": "accept", "reason": "Valid point"},
    {"report_id": "rpt_006", "decision": "maintain", "reason": "Already addressed"}
  ]'
```

`--step "3"` decision values:
- `withdraw`: Lead withdraws own finding (rebuttal accepted)
- `maintain`: Rejected — forwarded as rebuttal to the opposing agent in the next round
- `accept`: Accept cross-verifier's finding (added to consensus)

#### Apply Codex code_fixes

If Codex is lead and the `code_fixes` array is non-empty, CC applies each diff to the worktree.

**Skip code_fixes application for fork PRs.** Push is not possible, so applying patches to the worktree is meaningless. Skip this entire section if `IS_FORK` is `true`.

**If `DRY_RUN=true`, also prohibit actual worktree changes.** This is a review-only simulation, so do not execute `git apply`, `git commit`, or `git push`. Only record the agent's proposed `code_fixes` and applicable issues, then proceed to the settlement step.

Save each `code_fixes` item's `diff` value to a file and apply with `git apply`:

```bash
STAGED_FILES=$(mktemp)

# Iterate over each code_fix item
PATCH_FILE=$(mktemp /tmp/debate-patch-XXXXXX.patch)
printf '%s\n' "$DIFF_CONTENT" > "$PATCH_FILE"
git -C "$WORKTREE_PATH" apply --check "$PATCH_FILE"  # Verify
git -C "$WORKTREE_PATH" apply "$PATCH_FILE"           # Apply
git -C "$WORKTREE_PATH" apply --numstat "$PATCH_FILE" | awk '{print $3}' >> "$STAGED_FILES"
rm -f "$PATCH_FILE"
```

- On `--check` failure, record the issue_id as `failed-issues` and continue to the next item
- After all applications, reflect in Phase 1's `--applied-issues` and `--failed-issues`
- Accumulate actual file paths modified by successful patches for dedup staging in Phase 2
- When CC is lead, CC modifies code directly (code_fixes not needed)

#### Code Application (Same-Repo PR, 3-Phase)

All issues with `consensus_status=accepted` and `application_status=pending|failed` are fixed by the lead agent.

If `DRY_RUN=true`, skip all 3 phases. In dry-run mode, only verify state without creating commits/pushes.

**Phase 1: Record Application Results**

```bash
"$DEBATE_REVIEW_BIN" record-application \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --applied-issues '["isu_001", "isu_003"]' \
  --failed-issues '["isu_002"]'
```

**Phase 2: Record Commit SHA**

After code changes, commit (staging only modified files). Skip commit if no successful patches:
```bash
sort -u "$STAGED_FILES" | while IFS= read -r path; do
  [ -n "$path" ] && git -C "$WORKTREE_PATH" add -- "$path"
done
rm -f "$STAGED_FILES"
if git -C "$WORKTREE_PATH" diff --cached --quiet; then
  # No actual changes staged → skip commit/push
  COMMIT_SHA=""
else
  git -C "$WORKTREE_PATH" commit -m "fix: apply debate review findings (round $CURRENT_ROUND)"
  COMMIT_SHA=$(git -C "$WORKTREE_PATH" rev-parse HEAD)
fi
```

Staging targets are the actual changed file paths extracted from each successful patch's diff (deduplicated) or files directly modified by CC. The `file` field in `code_fixes` is treated only as a hint; `git add -A` must not be used.

If `COMMIT_SHA` is empty (no applied-issues or all patches failed), skip `--commit-sha` and Phase 3.

```bash
[ -n "$COMMIT_SHA" ] && "$DEBATE_REVIEW_BIN" record-application \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --commit-sha "$COMMIT_SHA"
```

**Phase 3: Push Verification**

Skip this step if `DRY_RUN=true`. Skip push and verification if `COMMIT_SHA` is empty.

```bash
[ -n "$COMMIT_SHA" ] && git -C "$WORKTREE_PATH" push origin "HEAD:$HEAD_BRANCH"
```

```bash
[ -n "$COMMIT_SHA" ] && "$DEBATE_REVIEW_BIN" record-application \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --verify-push
```

The CLI queries the actual PR HEAD and verifies it matches the commit SHA.

**Skip all 3 phases for fork PRs.** (Push not possible, `application_status=recommended`)

---

### Step 4: Settlement

```bash
SETTLE_RESULT=$("$DEBATE_REVIEW_BIN" settle-round \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND")
```

Branch based on `SETTLE_RESULT.result`:

| Result | Meaning | Next Action |
|--------|---------|-------------|
| `continue` | No consensus | Repeat round loop with `next_round` |
| `consensus_reached` | Consensus reached | Terminal processing → post comment |
| `max_rounds_exceeded` | Max rounds exceeded | Terminal processing → post comment |

If `continue`:
```
CURRENT_ROUND=$(echo "$SETTLE_RESULT" | jq -r '.next_round')
# Return to round loop start (Step 0)
```

---

### Terminal Processing + Final Comment

When `consensus_reached` or `max_rounds_exceeded`:

```bash
"$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE"
```

The CLI generates a comment using the appropriate template based on state and posts it to the PR. Duplicate prevention is handled by the CLI.

To skip comment posting (dry-run mode or manual override):

```bash
"$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE" --no-comment
```

Comment body is output to stdout without actual posting.

#### PR Title / Description Update

If code fixes were applied, update the PR title and description to accurately reflect the final changes.

1. Check current PR title/body:
   ```bash
   env -u GITHUB_TOKEN -u GH_TOKEN gh pr view "$PR_NUMBER" --repo "$REPO" --json title,body
   ```
2. Re-analyze changes based on the final diff:
   ```bash
   env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff "$PR_NUMBER" --repo "$REPO"
   ```
3. Update PR title/body if they don't match the latest code (skip if `DRY_RUN=true`):
   ```bash
   env -u GITHUB_TOKEN -u GH_TOKEN gh pr edit "$PR_NUMBER" --repo "$REPO" \
     --title "$UPDATED_TITLE" \
     --body "$UPDATED_BODY"
   ```

**Update criteria:**
- Whether fixes applied during debate review are reflected
- Whether specific numbers (line counts, structure, config items) are accurate
- Whether code examples (commands, variable names) match actual code

Skip this step if no code changes were made (all rounds were clean passes).

#### Worktree Cleanup

After terminal state:

```bash
git -C "$REPO_ROOT" worktree remove "$WORKTREE_PATH" --force
```

---

## Review Context + Placeholder Construction

Use `build-context` to generate all state-derived placeholder data for agent prompts:

```bash
CTX=$("$DEBATE_REVIEW_BIN" build-context --state-file "$STATE_FILE" --round "$CURRENT_ROUND")
```

The output JSON includes:

| Field | Placeholder | Description |
|-------|------------|-------------|
| `review_context` | `{REVIEW_CONTEXT}` | Last 2 rounds summary (text) |
| `open_issues` | `{OPEN_ISSUES}` | Unresolved issues (JSON array) |
| `debate_ledger` | `{DEBATE_LEDGER}` | Cumulative conclusion record (text) |
| `pending_rebuttals` | `{PENDING_REBUTTALS}` | Previous round rebuttals (JSON array) |
| `lead_reports` | `{LEAD_REPORTS}` | Current round lead findings (JSON array) |
| `cross_rebuttals` | `{CROSS_REBUTTALS}` | Current round cross rebuttals (JSON array) |
| `cross_findings` | `{CROSS_FINDINGS}` | Current round cross new findings (JSON array) |
| `applicable_issues` | `{APPLICABLE_ISSUES}` | Issues ready for code application (JSON array) |

CC only needs to add external data not in state: `{PR_TITLE}`, `{PR_BODY}`, `{DIFF}`, `{REVIEW_CRITERIA}`, `{REPO}`, `{PR_NUMBER}`, `{ROUND}`, `{OUTPUT_LANGUAGE}`.

---

## Debate Ledger Management

After Step 4 (`settle-round`), if `settled_issues` is non-empty, the orchestrator writes a 1-line summary for each and appends via CLI:

```bash
"$DEBATE_REVIEW_BIN" append-ledger \
  --state-file "$STATE_FILE" \
  --entries "$LEDGER_JSON"
```

Each entry: `{"issue_id", "status" (accepted/withdrawn), "reason", "summary", "round"}`. The CLI deduplicates by `(issue_id, status, round)`. If a withdrawn issue is re-raised and settled again, a new entry is appended (history accumulates).

---

## Restart Rules

When `init` returns `status: "resumed"`, the `next_step` field indicates where to resume:

| `next_step` | Action |
|-------------|--------|
| `step0` | Start from Step 0 (sync-head) |
| `step1` | Start from Step 1 (lead review) |
| `step2` | Start from Step 2 (cross-verification) |
| `step3` | Start from Step 3 (rebuttal response + cross findings eval + code application) |
| `step3_phase1` | Resume Step 3 Phase 1 (record application) |
| `step3_phase2` | Resume Step 3 Phase 2 (commit) |
| `step3_push` | Resume Step 3 push + Phase 3 verification. `resume_context.commit_sha` has the commit to push. |
| `step4` | Start from Step 4 (settlement) |

The `resume_context` object provides additional details (e.g., `clean_pass`, `commit_sha`).

---

## Failure Handling

| Failure Type | Handling |
|-------------|----------|
| Sync failure | Abort immediately, retry from sync on next run |
| Review analysis failure | Retry the step |
| Codex JSON parse failure | Retry same step up to 3 times, error exit on exceed |
| Commit failure | Retry from state recorded through Phase 1 |
| Push failure | Retry push from state recorded through Phase 2 |
| CLI exit code 1 | Parse JSON error message, diagnose and act |

On error exit, mark the state file as terminal failed first to prevent stale sessions from being resumed. Since `debate-review init` resumes `status=in_progress` sessions as-is, this step is mandatory on fatal error paths:

```bash
"$DEBATE_REVIEW_BIN" mark-failed --state-file "$STATE_FILE" \
  --error-message "$ERROR_MESSAGE"
```

After marking failed, post the final comment (add `--no-comment` if `DRY_RUN=true`) and clean up the worktree.

---

## Codex Invocation Reference

| Step | Template | Purpose |
|------|----------|---------|
| Step 1 (Codex lead) | `codex-lead-review-prompt.md` | Review + rebuttal resolution |
| Step 2 (Codex cross) | `codex-cross-verify-prompt.md` | Cross-verification + own findings |
| Step 3 (Codex lead) | `codex-lead-response-prompt.md` | Response + code fixes |

Invocation pattern:
1. Read prompt template
2. Substitute placeholders (see derivation methods below)
3. Pass prompt file via stdin: `codex exec -s "$CODEX_SANDBOX" - < "$PROMPT_FILE"`
4. Parse JSON output (retry up to 3 times on failure)

#### Placeholder Derivation

See `REFERENCE.md` for placeholder sources. State-derivable placeholders are returned by `build-context --state-file --round N`.

---

## Quick Reference

| Item | Rule |
|------|------|
| Lead agent | Odd rounds = Codex, Even = CC |
| Consensus condition | 2 consecutive clean passes (from different lead agents) |
| State file | `~/.claude/debate-state/<owner>-<repo>-<pr>.json` |
| CLI | `$DEBATE_REVIEW_BIN <subcommand>` |
| Comment tag | `[debate-review][sha:<initial_sha>]` |
| Max rounds | 10 (config `max_rounds`) |
| Codex sandbox | `read-only` (explicit opt-in for `danger-full-access`) |
| Worktree | `<repo_root>/.worktrees/debate-pr-<N>` |
| GitHub CLI | `env -u GITHUB_TOKEN -u GH_TOKEN gh ...` |
| Output language | Config `language` (default: `en`) |

## Common Mistakes

- **Manipulating state without CLI**: Always use `$DEBATE_REVIEW_BIN` subcommands for state changes
- **Skipping Step 0**: Always run `sync-head` even on restart
- **Using `post_sync_head_sha` in comment tag**: Use `initial_sha` for stability after Step 3 commits
- **Filtering by `opened_by`**: Lead agent fixes all agreed issues regardless of who opened them
- **Using Codex output as-is in comments**: Orchestrator must normalize to standard format
- **Ignoring phase order**: Strictly follow Phase 1 → commit → Phase 2 → push → Phase 3
- **Attempting push on fork PR**: Fork PRs skip code application/commit/push entirely
