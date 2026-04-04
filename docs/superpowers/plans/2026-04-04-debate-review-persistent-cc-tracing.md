# Debate Review Persistent CC Tracing Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist persistent-mode tracing metadata and full round/step timing history, then generate a full-session timing report.

**Architecture:** Extend debate-review state with round-level trace structures, record dispatch metadata inside the orchestrator/CLI boundary, and add a report module that correlates debate-state with CC/Codex session logs. Keep report generation read-only over historic logs and tolerant of partial data.

**Tech Stack:** Python, pytest, debate-review CLI/state/orchestrator modules

---

## Chunk 1: State And Timing Persistence

### Task 1: Add failing tests for round-level step trace persistence

**Files:**
- Modify: `skills/cc-codex-debate-review/tests/test_timing.py`
- Modify: `skills/cc-codex-debate-review/tests/test_round_ops.py`

- [ ] Step 1: Write failing tests for per-round `step_timings` and `step_traces`
- [ ] Step 2: Run targeted pytest and observe failures
- [ ] Step 3: Implement minimal state/timing helpers
- [ ] Step 4: Re-run targeted pytest until green

## Chunk 2: Persistent Dispatch Correlation

### Task 2: Add failing tests for persistent dispatch metadata capture

**Files:**
- Modify: `skills/cc-codex-debate-review/tests/test_orchestrator.py`
- Modify: `skills/cc-codex-debate-review/tests/test_cli.py`

- [ ] Step 1: Write failing tests for persistent `task_id` / `output_file` / `subagent_log_path`
- [ ] Step 2: Run targeted pytest and observe failures
- [ ] Step 3: Implement orchestrator + CLI persistence
- [ ] Step 4: Re-run targeted pytest until green

## Chunk 3: Session Report Generator

### Task 3: Add failing tests for full-session report generation

**Files:**
- Create: `skills/cc-codex-debate-review/lib/debate_review/reporting.py`
- Create: `skills/cc-codex-debate-review/tests/test_reporting.py`
- Modify: `skills/cc-codex-debate-review/lib/debate_review/cli.py`

- [ ] Step 1: Write failing tests for markdown/json report output and classification
- [ ] Step 2: Run targeted pytest and observe failures
- [ ] Step 3: Implement report generator and CLI command
- [ ] Step 4: Re-run targeted pytest until green

## Chunk 4: Verification And Delivery

### Task 4: Verify, commit, and prepare PRs

**Files:**
- Modify: implementation files from earlier tasks
- Create: report document on docs branch only

- [ ] Step 1: Run focused pytest for debate-review package
- [ ] Step 2: Run full relevant pytest suite
- [ ] Step 3: Commit/push code branch and open code PR
- [ ] Step 4: Generate full-session markdown report
- [ ] Step 5: Commit/push docs branch and open docs PR
