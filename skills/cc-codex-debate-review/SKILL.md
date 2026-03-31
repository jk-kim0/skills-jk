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

#### Load Config

```bash
SKILL_ROOT="<path-to-cc-codex-debate-review>"
DEBATE_REVIEW_BIN="$SKILL_ROOT/bin/debate-review"
CONFIG_FILE="$SKILL_ROOT/config.yml"
```

Read values from the config file:
```bash
MAX_ROUNDS=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['max_rounds'])")
CODEX_SANDBOX=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('codex_sandbox', 'read-only'))")
LANGUAGE=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('language', 'en'))")
```

The `LANGUAGE` value is passed to LLM prompts via `{OUTPUT_LANGUAGE}` to control the language of user-facing output (issue messages, reasons, descriptions). CLI-generated comment templates are always in English. Skill instructions and Codex prompts are also always in English.

#### Validate Arguments

`REPO` (e.g., `owner/repo`) and `PR_NUMBER` are required arguments. Abort immediately if either is missing.

#### Initialize Session

```bash
RESULT=$("$DEBATE_REVIEW_BIN" init --repo "$REPO" --pr "$PR_NUMBER" \
  --config "$CONFIG_FILE")
```

Extract from `RESULT` JSON:
```bash
STATE_FILE=$(echo "$RESULT" | jq -r '.state_file')
STATUS=$(echo "$RESULT" | jq -r '.status')           # "created" | "resumed"
CURRENT_ROUND=$(echo "$RESULT" | jq -r '.current_round')
IS_FORK=$(echo "$RESULT" | jq -r '.is_fork')
DRY_RUN=$(echo "$RESULT" | jq -r '.dry_run')
```

If `STATUS` is `resumed` → branch to **Restart Procedure** (see below).

#### Check State (if needed)

```bash
"$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json
```

Outputs the full state as JSON. Use `journal.step` to determine restart position.

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

### Lead Agent Determination + Round Initialization

| Round | Lead Agent | Cross-Verifier |
|-------|-----------|----------------|
| Odd (1, 3, 5, ...) | Codex | CC |
| Even (2, 4, 6, ...) | CC | Codex |

```bash
if [ $((CURRENT_ROUND % 2)) -eq 1 ]; then
  LEAD_AGENT="codex"
  CROSS_VERIFIER="cc"
else
  LEAD_AGENT="cc"
  CROSS_VERIFIER="codex"
fi

STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json)
REPO_ROOT=$(echo "$STATE_JSON" | jq -r '.repo_root')
WORKTREE_PATH="$REPO_ROOT/.worktrees/debate-pr-$PR_NUMBER"
HEAD_BRANCH=$(echo "$STATE_JSON" | jq -r '.head.pr_branch_name')
SYNCED_SHA=$(echo "$SYNC_RESULT" | jq -r '.post_sync_sha')

"$DEBATE_REVIEW_BIN" init-round \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --lead-agent "$LEAD_AGENT" \
  --synced-head-sha "$SYNCED_SHA"
```

---

### Step 1: Lead Agent Review

#### Step 1a: Resolve Pending Rebuttals

If rebuttals from the previous round exist, the lead agent decides `withdraw` or `maintain` for each.

Previous round rebuttals are found in the `show --json` output at `rounds[N-1].step3.rebuttals`.

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

## Review Context Construction

When requesting reviews in Step 1 and Step 2, pass the results of the last 2 rounds as context.

**Scope:** `max(1, current_round - 2)` to `current_round - 1` completed/superseded rounds. For Round 1, pass `(First round — no previous reviews)` in `{REVIEW_CONTEXT}`.

Since the last 2 rounds summary alone may miss older unresolved issues, the Codex lead Step 1 prompt also receives all current unresolved issues separately via `{OPEN_ISSUES}`.

**Components:**
1. Round metadata: number, lead agent, status, clean_pass
2. Step 1 results: findings summary (issue ID, severity, file, message)
3. Step 2 results: accept/rebut decisions + new findings
4. Step 3 results: rebuttal responses + code application results
5. Unresolved issue status

**Generation method:** CC constructs this from `rounds[]` and `issues` in the `show --json` output.

**Format:**

```text
## Review Context (rounds <N-2> to <N-1>)

### Round <N-2> [lead: <agent>, status: <status>, clean_pass: <bool>]

**Step 1 (<agent> review):**
- isu_001 (warning) src/foo.ts:42 — Infinite retry loop

**Step 2 (<agent> cross-verification):**
- rpt_001 (isu_001): accepted
- rpt_002 (isu_002): rebutted — "reason"

**Step 3 (<agent> response + application):**
- rpt_002 rebuttal: accepted → isu_002 withdrawn
- Applied: isu_001, isu_003

**Unresolved issues:** (none)
```

---

## Debate Ledger Management

Maintains a cumulative record of per-issue conclusions across all rounds so agents can reference prior decisions during longer debates (5+ rounds).

### When to Write Ledger Entries

After Step 4 (`settle-round`), the orchestrator (CC) checks the return value's `settled_issues`. For each settled issue, write a 1-line summary and append it to the state file's `debate_ledger` array.

### Ledger Entry Format

```json
{
  "issue_id": "isu_001",
  "status": "accepted",
  "reason": null,
  "summary": "Missing batch exit code — R1 Codex raised, R1 CC accept, R3 applied",
  "round": 3
}
```

- `status`: `accepted` or `withdrawn`
- `reason`: `consensus_reason` value. Withdrawal reason for withdrawn, `null` for accepted. Used to judge differentiation when re-raising
- `summary`: 1-line summary of issue content and raise/consensus/withdrawal history (orchestrator writes in natural language)
- `round`: Round number when the conclusion was finalized

### How to Record Ledger Entries

If `settle-round` returns `settled_issues`, the orchestrator reads the state file, appends entries to the `debate_ledger` array, and saves:

```bash
# After settle-round, if settled_issues exist:
STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json)
# CC writes a summary for each settled_issues entry
# Append to state file's debate_ledger and save
python3 - "$STATE_FILE" "$LEDGER_JSON" <<'PY'
import json, sys
path, ledger_json = sys.argv[1], sys.argv[2]
with open(path) as f:
    state = json.load(f)
entries = json.loads(ledger_json)
ledger = state.setdefault("debate_ledger", [])
existing = {(e["issue_id"], e["status"], e.get("round")) for e in ledger}
for entry in entries:
    key = (entry["issue_id"], entry["status"], entry.get("round"))
    if key not in existing:
        ledger.append(entry)
        existing.add(key)
import tempfile, os
dir_ = os.path.dirname(path)
with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as f:
    json.dump(state, f, indent=2)
    tmp = f.name
os.replace(tmp, path)
PY
```

### Re-appearance of Issues Already in the Ledger

If a withdrawn issue is re-raised and settled again, append a new entry (previous entries are preserved). History accumulates so agents can trace the full discussion flow for each issue.

### {DEBATE_LEDGER} Placeholder

When passing to prompts, convert the `debate_ledger` array to the following text format:

```text
## Debate Ledger (full-round conclusion summary)

- isu_001 [accepted] Missing batch exit code — R1 Codex raised, R1 CC accept, R3 applied
- isu_003 [withdrawn] (reason: Intentional design choice) KeyboardInterrupt handling — R1 Codex raised, R2 CC rebut, R5 Codex withdraw

To re-raise a previously withdrawn issue, you must present new evidence different from the reason above.
```

If the array is empty, pass `(First round — no previous conclusions)`.

---

## Restart Rules

Restart always begins with `init`:

```bash
RESULT=$("$DEBATE_REVIEW_BIN" init --repo "$REPO" --pr "$PR_NUMBER" \
  --config "$CONFIG_FILE")
# STATUS = "resumed"
```

Check `journal.step` via `show --json` to determine resume position:

| journal.step | Next Action |
|--------------|-------------|
| `init` | From Step 0 (sync-head) |
| `step0_sync` | From Step 1 (review) |
| `step1_lead_review` | If clean_pass=true → Step 4, otherwise Step 2 |
| `step2_cross_review` | Step 3 |
| `step3_lead_apply` | Check journal checkpoints, resume from incomplete phase |
| `step4_settle` | Next round Step 0 |

### Step 3 Restart Details

When `journal.step = step3_lead_apply`, check checkpoints:

1. `journal.push_verified = true` → Step 3 complete, proceed to Step 4
2. `journal.commit_sha` exists and matches PR HEAD → Treat as push success, re-run Phase 3 (`--verify-push`)
3. `journal.commit_sha` exists but doesn't match PR HEAD → Push incomplete, CC retries push then Phase 3
4. `journal.commit_sha = null` → From Phase 2 (regenerate commit)
5. `journal.applied_issue_ids` is empty → From Phase 1

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

On error exit, mark the state file as terminal failed first to prevent stale sessions from being resumed. Since `debate-review init` resumes `status=in_progress` sessions as-is, this step is mandatory on fatal error paths. As the CLI currently lacks a dedicated subcommand, this path exceptionally updates the state file directly, then posts the final comment (add `--no-comment` if `DRY_RUN=true`) and cleans up the worktree.

```bash
ERROR_MESSAGE=${ERROR_MESSAGE:-"Unknown error"}
python3 - "$STATE_FILE" "$ERROR_MESSAGE" <<'PY'
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

path, error_message = sys.argv[1], sys.argv[2]
with open(path) as f:
    state = json.load(f)

state["status"] = "failed"
state["final_outcome"] = "error"
state["finished_at"] = datetime.now(timezone.utc).isoformat()
state["error_message"] = error_message
state["head"]["terminal_sha"] = state["head"]["last_observed_pr_sha"]
state["journal"]["state_persisted"] = True

dir_ = os.path.dirname(path)
with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
    tmp_path = f.name
os.replace(tmp_path, path)
PY

if [ "$DRY_RUN" = "true" ]; then
  "$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE" --no-comment
else
  "$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE"
fi

if [ -z "${WORKTREE_PATH:-}" ]; then
  STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json 2>/dev/null || true)
  REPO_ROOT=$(printf '%s' "$STATE_JSON" | jq -r '.repo_root // empty')
  [ -n "$REPO_ROOT" ] && WORKTREE_PATH="$REPO_ROOT/.worktrees/debate-pr-$PR_NUMBER"
fi

if [ -n "${WORKTREE_PATH:-}" ] && [ -d "$WORKTREE_PATH" ]; then
  git -C "$REPO_ROOT" worktree remove "$WORKTREE_PATH" --force || true
fi
```

The CLI generates a comment using the error template and removes the stale worktree when cleanup is possible.

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

Common placeholders:
- `{REPO}`, `{PR_NUMBER}`, `{ROUND}`: Directly from orchestrator variables
- `{PR_TITLE}`, `{PR_BODY}`: Extracted from `gh pr view --json title,body`
- `{DIFF}`: `gh pr diff "$PR_NUMBER" --repo "$REPO"`
- `{REVIEW_CRITERIA}`: Contents of `./review-criteria.md` (`$SKILL_ROOT/review-criteria.md`)
- `{REVIEW_CONTEXT}`: Generated by CC in the format described in "Review Context Construction"
- `{DEBATE_LEDGER}`: Generated by CC from `state.debate_ledger` in the format described in the "Debate Ledger Management" section
- `{OUTPUT_LANGUAGE}`: `state["language"]` (initially sourced from `config.yml` at session creation; on resume, always use the value persisted in state). Used for user-facing JSON string values while keeping JSON keys and enums in English

Step-specific placeholders (derived from `show --json` output):

| Placeholder | Data Path | Description |
|---|---|---|
| `{OPEN_ISSUES}` | Currently unresolved items in `issues` | Full list of open issues at current round start. Includes older issues outside the last 2 rounds context. For same-repo: items with `consensus_status=open` or `consensus_status=accepted` and `application_status!=applied`. For fork: items with `consensus_status=open` or `consensus_status=accepted` and `application_status!=recommended`. Pass as JSON array combining `issue_id`, `consensus_status`, `application_status`, `severity`, `file`, `line`, `anchor`, `message` |
| `{PENDING_REBUTTALS}` | `rounds[N-1].step3.rebuttals` + `issues[*].reports[*]` | JSON array combining rebuttals from previous round step3 with the original finding's `issue_id`, `severity`, `file`, `line`, `anchor`, `message`. Enables the lead agent to see rebuttal reasons alongside original context |
| `{LEAD_AGENT_ID}` | `rounds[N].lead_agent` | Current round's lead agent ID |
| `{LEAD_REPORTS}` | `rounds[N].step1.report_ids` → `issues[*].reports[*]` | Combine `report_id`, `severity`, `file`, `line`, `anchor`, `message` from issues via report_id. Must include `report_id` in JSON array (cross-verifier needs it to return decisions by report_id) |
| `{CROSS_REBUTTALS}` | `rounds[N].step2.rebuttals` + `issues[*].reports[*]` | JSON array combining current round step2 rebuttals with the original finding's `report_id`, `issue_id`, `severity`, `file`, `line`, `anchor`, `message`. Enables the lead agent to identify which finding is being challenged |
| `{CROSS_FINDINGS}` | `rounds[N].step2.report_ids` → `issues[*].reports[*]` | Combine `report_id`, `severity`, `file`, `line`, `anchor`, `message` from issues via cross-verifier's report_ids. Include `report_id` in JSON array |
| `{APPLICABLE_ISSUES}` | Items in `issues` with `consensus_status=accepted` AND `application_status=pending\|failed` | List of issues to apply. JSON array including issue_id, file, line, message |

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
