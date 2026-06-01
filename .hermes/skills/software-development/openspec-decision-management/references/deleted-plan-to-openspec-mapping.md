# Deleted plan to OpenSpec mapping issue pattern

Use when a docs-to-OpenSpec migration deletes or drastically shortens a long-lived sprint plan, implementation handoff, design doc, or checklist and reviewers need proof that content was not lost.

## Trigger

- A PR changes a detailed `docs/**` plan into a short bridge document pointing to `openspec/changes/**` or `openspec/specs/**`.
- The removed content includes requirements, decisions, file-level tasks, verification steps, or backlog notes.
- The user asks whether the deleted lines already exist in OpenSpec or asks for a mapping table.

## Workflow

1. Identify the pre-refactor source and current replacement.
   - Use the PR base or merge-base commit to read the old file.
   - Use current `HEAD` to read the moved/bridged file.
   - Capture the old line count and top-level headings.

2. Group deleted content by old line range and semantic section, not every individual line when the section is repetitive.
   - Common groups: goal/summary, architecture, tech stack, decision table, pre-alignment, each task, backlog.
   - For dense decision tables, map row-by-row.

3. For each group, locate the canonical replacement.
   - Proposal: scope, motivation, resolved decisions, acceptance.
   - `tasks.md`: implementation checklist.
   - `uc-*` spec: user-facing scenarios.
   - `contract-*` spec: schema/API/state/provider rules.
   - Other docs: backlog, feature status, model contracts, API boundary contracts.

4. Record coverage honestly.
   - `Covered in OpenSpec` when the same contract is now a Requirement/Scenario/task.
   - `Covered in docs/status/backlog` when the detail moved outside OpenSpec.
   - `Partial` when the exact old detail is only implied or generalized.
   - `Potential gap` when the detail is important but no canonical replacement is found.

5. Publish as a real GitHub issue if requested, not just a draft.
   - Title shape: `<Feature/Sprint> 계획 문서 OpenSpec 전환 삭제 내용 매핑`.
   - Body sections:
     - Purpose and baseline commits/paths.
     - Summary conclusion.
     - Main mapping table.
     - Decision-table mapping if relevant.
     - Task-breakdown mapping.
     - Backlog mapping.
     - Potential gaps.
     - Commands used.

## Useful table shape

```md
| Old lines | 삭제된 내용 | 대체 위치 | 대체 내용 / coverage |
| --- | --- | --- | --- |
| 13-28 | `/goal` 후보 전체 | `proposal.md`, `uc-*`, `contract-*`, `tasks.md` | 성공 조건은 proposal scope, UC scenario, contract requirement, task checklist로 분리되어 대체됨. |
```

For decision rows:

```md
| Old line | 결정 항목 | 대체 위치 | 대체 내용 / coverage |
| --- | --- | --- | --- |
| 35 | 원본 CSV 파일 장기 저장하지 않고 metadata만 남김 | `proposal.md`, `contract-*`, `docs/model/**`, status doc | 원본 파일 장기 저장 제외와 `importSourceRef`는 보존됨. `file name/size/hash` exact detail은 OpenSpec에는 없음. |
```

## Pitfalls

- Do not assume every deleted detail is in OpenSpec. Some valid replacements may live in `docs/backlog-requirements.md`, feature status docs, model docs, or a shared API-boundary spec.
- Do not hide partial coverage. If old wording such as `file name/size/hash` or `UI loading state is client state` was generalized to an async/job exclusion, mark it as partial and propose a spec addition if the detail matters.
- Do not map file-level task lists only to high-level tasks if current implementation evidence lives elsewhere. Link both the canonical OpenSpec task and the feature status/evidence file when needed.
- Avoid auto-closing issue keywords unless the user explicitly asks for merge-time closure.
