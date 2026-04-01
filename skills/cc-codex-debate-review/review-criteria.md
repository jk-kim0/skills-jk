# PR Review Criteria

## Severity Levels

| Level | Description |
|-------|-------------|
| `critical` | Correctness bug, security vulnerability, data loss risk. Must fix before merge |
| `warning` | Reliability, performance, or maintainability risk. Resolution recommended |
| `suggestion` | Code improvement opportunity. Not a blocker |

---

## Canonical-Kind Vocabulary

| # | canonical-kind | Description |
|---|---|---|
| 1 | `missing_validation` | Missing input validation |
| 2 | `missing_error_handling` | Missing error handling |
| 3 | `unbounded_loop` | Loop/retry without termination condition |
| 4 | `wrong_target_ref` | Incorrect reference target |
| 5 | `stale_state_transition` | Invalid state transition order |
| 6 | `unused_variable` | Declared but unused variable/field |
| 7 | `hardcoded_value` | Hardcoded value |
| 8 | `duplicate_logic` | Duplicate code/logic |
| 9 | `security_injection` | SQL/command/XSS injection vulnerability |
| 10 | `race_condition` | Concurrency issue |
| 11 | `resource_leak` | Unreleased file/connection resource |
| 12 | `wrong_scope` | Excessive or insufficient access scope |
| 13 | `incorrect_algorithm` | Logic/algorithm error |
| 14 | `missing_test` | Missing test coverage |
| 15 | `doc_mismatch` | Documentation does not match implementation |
| 16 | `ci_failure` | CI pipeline failure caused or not addressed by the PR |

**Fallback** (when none of the above apply):
`criterion:<N>|file:<path>|anchor:<anchor>|msg:<sha1(normalize(message))[:12]>`

Note: `issue_key` generation is handled by the orchestrator. Agents output only raw findings in the format below.

---

## Actionable Finding Requirements

- Must be specific and clear (file + line reference required)
- Must be fixable within the PR scope
- Must relate to code introduced or modified by the PR (exclude pre-existing issues)
- Must not be a style preference or subjective opinion

---

## Items to Skip

- Style nits (formatting, naming preferences) — unless they cause confusion
- Pre-existing issues not introduced by this PR
- Subjective architecture opinions without concrete impact
- Issues already raised in previous rounds (deduplication is handled by the orchestrator)

---

## Raw Report Output Format

This section is a **reference for the raw finding array schema**. The actual top-level output format follows the JSON object specification in each prompt.

Raw findings placed in the `findings` field follow this JSON array item schema:

```json
[
  {
    "severity": "critical|warning|suggestion",
    "criterion": 1,
    "file": "src/foo.ts",
    "line": 42,
    "anchor": "validate_input",
    "message": "Description of the issue and why it matters"
  }
]
```

- `criterion`: Review criteria number. Use standard kind index (1-15) if applicable, otherwise a fallback number.
- `file`: Repository-relative path
- `line`: Line number based on the current PR diff
- `anchor`: Symbol name, function name, or other identifier less sensitive to line shifts. Use `line<N>` format if none exists.
- `message`: Clear explanation of what is wrong and why it matters

---

## CI Pipeline Check

Before reviewing the diff, check the PR's CI pipeline status:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr checks {PR_NUMBER} --repo {REPO}
```

- **All passing**: Proceed to diff review.
- **No checks reported**: `gh pr checks` may print `no checks reported on the '<branch>' branch` and exit with status 1 when the PR has no check runs yet. Treat this as `no checks yet`, not as a CI failure. Confirm with:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh run list --repo {REPO} --branch "$(env -u GITHUB_TOKEN -u GH_TOKEN gh pr view {PR_NUMBER} --repo {REPO} --json headRefName -q .headRefName)" --limit 20
```

If the fallback shows no runs, note `no checks yet` and proceed to diff review.
- **Failures present**: Investigate failed checks using `gh run view <run-id> --log-failed`. Diagnose the root cause — determine whether the failure is caused by changes in this PR or is a pre-existing/flaky issue. Report PR-caused failures as findings with `criterion: 16` (`ci_failure`).
- **Pending/running**: Note the status and proceed to diff review. Do not wait.

---

## Review Scope

- Focus exclusively on the PR diff
- Read surrounding code for context, but only report issues in changed/added lines
- Infer intent from the PR title and description
