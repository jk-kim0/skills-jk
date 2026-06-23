---
name: sdlc-backtrack
description: Use when evaluating and coordinating SDLC backtracks to earlier stages.
---

# SDLC Backtrack

Use this skill when a later SDLC stage finds evidence that an earlier stage decision or artifact
may need to change.

This skill is not a lifecycle stage. It coordinates a short feedback loop: validate the evidence,
decide whether backtrack is warranted, get user approval, then call the core backtrack script.

## Quick Start

1. Identify the case id, current stage, suspected target stage, and proposed question.
2. Read `references/workflow.md`, `references/decision-model.md`,
   `.agents/sdlc/core/references/stage-backtrack.md`,
   `.agents/sdlc/core/references/stage-contracts.md`, and
   `.agents/sdlc/core/references/document-quality.md`.
3. Read `references/user-guide.md` when the user asks how backtrack works.
4. Run `.agents/sdlc/core/scripts/prepare-stage.sh <case-id> <current-stage>`.
5. Read the documents listed under `반드시 읽을 문서`.
6. Read target stage documents, downstream stage documents, source, tests, or evidence only when
   needed to evaluate the backtrack claim.
7. Classify the issue using `references/decision-model.md`.
8. If backtrack is not warranted, explain the better path and do not run the script.
9. If backtrack may be warranted, draft a proposal using
   `assets/templates/backtrack-proposal.md`.
10. Discuss the proposal with the user. Keep the loop centered on one question.
11. If the user approves, run
    `.agents/sdlc/core/scripts/backtrack-stage.sh <case-id> <target-stage>`.
12. Write a short result using `assets/templates/backtrack-result.md` under
    `.agents/runs/sdlc-backtrack/<case-id>/`.
13. Run `.agents/sdlc/core/scripts/validate-case.sh <case-id> <target-stage>`.
14. Hand off to the target stage skill, such as `sdlc-design`, to close the approved question.

## Rules

- Do not run `backtrack-stage.sh` before user approval.
- Do not silently edit completed earlier-stage documents.
- Do not use backtrack for work that belongs to the current stage.
- Do not reopen broad scope. One backtrack loop should close one core question.
- If the proposed change is larger than one PR or changes the case goal, recommend case split or a
  new plan instead.
- Downstream artifacts are stale after backtrack. Keep them, but re-check them before continuing.

## Language Rules

Write user-facing responses and generated backtrack artifacts in Korean (`한국어`) by default.

Keep code, file paths, commands, ticket IDs, API names, product names, role ids, and technology
names in their original form.

## Storage Rules

Temporary backtrack proposals and results go under `.agents/runs/sdlc-backtrack/<case-id>/`.

Approved lifecycle state changes are stored only in `metadata.yaml` through the core script.

Official decision changes belong in the target stage documents after the backtrack is opened.
