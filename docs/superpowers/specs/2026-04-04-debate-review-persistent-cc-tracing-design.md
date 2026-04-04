# Debate Review Persistent CC Tracing Design

## Goal

Persist round and step timing history for `cc-codex-debate-review` and capture enough persistent-mode CC correlation metadata to connect debate-review state with `~/.claude/projects/.../subagents/*.jsonl` execution logs. Add a report generator that summarizes full-session timing and agent activity breakdown across all debate-review sessions.

## Scope

- Persist step timing per round instead of only keeping `journal.step_timings` for the current round.
- Capture persistent-mode dispatch metadata for CC and Codex steps.
- Capture command spans around orchestrator dispatches so report generation can distinguish orchestration overhead from agent active time.
- Add a CLI/report path that scans debate-state plus CC/Codex session logs and emits a machine-readable plus markdown report.
- Keep legacy mode out of scope.

## Data Model

- Add `journal.current_step_trace` for in-flight step bookkeeping.
- Add per-round `step_timings` and `step_traces`.
- Add step trace fields for:
  - `agent`
  - `started_at`, `completed_at`
  - `prompt_file`
  - `message_file`
  - `command_spans`
  - `persistent_session`
  - `dispatch`
  - `runtime_artifacts`
- `persistent_session` stores session handle used at dispatch time.
- `dispatch` stores `tool_use_id`, `task_id`, `output_file`, `subagent_log_path`, and raw response snippets when available.

## Matching Strategy

- Persistent CC matching is driven by `task_id` and `output_file`.
- If `output_file` is a symlink, resolve it and persist the real `subagent_log_path`.
- Later report generation reads the subagent JSONL and classifies tool time into:
  - local file I/O
  - local git
  - GitHub/API
  - reasoning/other

## Report Outputs

- New CLI command to build a full-session report from `~/.claude/debate-state`.
- Output includes session totals, per-round totals, per-step totals, and persistent-agent breakdown when traceable.
- Output format:
  - JSON payload for programmatic use
  - Markdown document for `docs/`

## Risks

- Existing state files vary by schema version, so migration helpers must be tolerant.
- CC session output formats may differ slightly; parser should degrade gracefully and mark missing fields as `unknown`.
- Per-tool active time will be approximate because CC logs provide event timestamps, not explicit CPU/wait attribution.
