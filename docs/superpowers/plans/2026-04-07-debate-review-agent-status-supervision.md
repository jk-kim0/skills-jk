# Debate Review Agent Status Supervision Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add live streaming supervision to persistent debate-review steps so the orchestrator can surface agent status, detect stalls, and persist heartbeat/recovery summaries.

**Architecture:** Keep the existing orchestrator shape, but replace blocking step dispatch with a streaming subprocess runner that feeds normalized vendor events into a shared supervisor. Persist only supervision summaries and artifact paths in state, while raw stdout/stderr lines go to per-step log files. Progress output becomes status-aware and updates on a 5-second tick or immediate state change.

**Tech Stack:** Python 3, `subprocess.Popen`, pytest, existing `debate_review` state/reporting modules

---

## Chunk 1: Runtime Primitives

### Task 1: Add failing tests for vendor event normalization

**Files:**
- Create: `skills/cc-codex-debate-review/tests/test_runtime_events.py`
- Create: `skills/cc-codex-debate-review/lib/debate_review/runtime_events.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_normalize_codex_turn_started():
    ...

def test_normalize_claude_partial_delta():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_runtime_events.py -v`
Expected: FAIL because `debate_review.runtime_events` does not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
def normalize_event(...):
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_runtime_events.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime_events.py lib/debate_review/runtime_events.py
git commit -m "feat: add runtime event normalization"
```

### Task 2: Add failing tests for heartbeat and stall transitions

**Files:**
- Create: `skills/cc-codex-debate-review/tests/test_runtime_supervision.py`
- Create: `skills/cc-codex-debate-review/lib/debate_review/runtime_supervision.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_supervisor_transitions_from_awaiting_to_thinking():
    ...

def test_supervisor_marks_codex_suspected_stall_after_90s():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_runtime_supervision.py -v`
Expected: FAIL because supervisor module does not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
class StepSupervisor:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_runtime_supervision.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime_supervision.py lib/debate_review/runtime_supervision.py
git commit -m "feat: add runtime stall supervision"
```

## Chunk 2: Progress And Trace Persistence

### Task 3: Add failing tests for status-aware progress output

**Files:**
- Modify: `skills/cc-codex-debate-review/tests/test_progress.py`
- Modify: `skills/cc-codex-debate-review/lib/debate_review/progress.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_step_status_change_prints_immediately():
    ...

def test_tick_line_includes_last_event_age():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_progress.py -v`
Expected: FAIL because reporter cannot track supervision status yet

- [ ] **Step 3: Write minimal implementation**

```python
class ProgressReporter:
    def step_status(...):
        ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_progress.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_progress.py lib/debate_review/progress.py
git commit -m "feat: add status-aware progress reporting"
```

### Task 4: Add failing tests for trace step IDs and supervision summaries

**Files:**
- Modify: `skills/cc-codex-debate-review/tests/test_timing.py`
- Modify: `skills/cc-codex-debate-review/lib/debate_review/timing.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_start_step_trace_assigns_step_id_and_dedupe_token():
    ...

def test_update_step_trace_merges_supervision_summary():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_timing.py -v`
Expected: FAIL because trace metadata does not include supervision fields yet

- [ ] **Step 3: Write minimal implementation**

```python
def start_step_trace(...):
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_timing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_timing.py lib/debate_review/timing.py
git commit -m "feat: persist supervision trace metadata"
```

## Chunk 3: Orchestrator Streaming Integration

### Task 5: Add failing orchestrator tests for streaming supervision

**Files:**
- Modify: `skills/cc-codex-debate-review/tests/test_orchestrator.py`
- Create: `skills/cc-codex-debate-review/lib/debate_review/runtime_stream.py`
- Modify: `skills/cc-codex-debate-review/lib/debate_review/orchestrator.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_dispatch_step_records_supervision_summary_from_stream():
    ...

def test_dispatch_step_uses_recovery_on_hard_stall():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrator.py -v`
Expected: FAIL because adapter dispatch is still blocking

- [ ] **Step 3: Write minimal implementation**

```python
class StreamingProcessRunner:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_orchestrator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_orchestrator.py lib/debate_review/runtime_stream.py lib/debate_review/orchestrator.py
git commit -m "feat: stream persistent agent runtime events"
```

### Task 6: Run regression suite

**Files:**
- Verify: `skills/cc-codex-debate-review/tests/`

- [ ] **Step 1: Run focused runtime tests**

Run: `python3 -m pytest tests/test_runtime_events.py tests/test_runtime_supervision.py tests/test_progress.py tests/test_timing.py tests/test_orchestrator.py -v`
Expected: PASS

- [ ] **Step 2: Run the full suite**

Run: `python3 -m pytest`
Expected: PASS

- [ ] **Step 3: Inspect diff**

Run: `git status --short`
Expected: only intended implementation files are modified
