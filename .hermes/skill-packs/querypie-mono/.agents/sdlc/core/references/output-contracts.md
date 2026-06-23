# Output Contracts

## Language

All user-facing output and generated planning artifacts must be written in Korean (`한국어`).

Keep code, file paths, commands, ticket IDs, API names, product names, and role ids in their
original form.

## Document Quality

All approved case documents, stage documents, reports, and semantic review files must follow
`references/document-quality.md`.

The common quality gate is `scripts/validate-document-quality.sh`.

The optional formatter is `scripts/format-document-quality.sh`.

This quality contract is shared by `sdlc-plan` and future SDLC skills.

## Worker 결과

Each worker agent must return:

- `역할`
- `범위`
- `사용한 근거`
- `발견 사항`
- `선택지`
- `위험`
- `필요한 결정`
- `신뢰도`

## Approved Case

Approved case documents must follow `references/case-structure.md`.

Each stage output must fit the workflow in `references/stage-workflow.md`.

Root documents must include:

- `README.md`
- `metadata.yaml`
- `evidence.md`

Root `metadata.yaml` must follow `schemas/case-metadata.schema.json`. Use that schema as the
source of truth for required keys, allowed status values, and stage output paths.

Lifecycle status must exist only in root `metadata.yaml`. Do not duplicate current stage or status
fields in `README.md`, stage `result.md`, or stage `handoff.md`.

Each stage result must include:

- `단계 정보`
- `요약`
- `확정된 결정`
- `남은 결정`
- `주요 내용`
- `위험과 공백`
- `다음 단계로 넘길 내용`
- `체크포인트`

Plan result must additionally separate:

- `계획상 확정된 결정`
- `영향 가능성이 있는 영역`
- `설계 검토 후보`
- `Design 단계 질문`

Plan result must not present technical choices, implementation structure, or build work units as
final decisions. Those belong to design.

Affected areas in plan result are candidates. Design must re-check whether each area is an actual
change target.

Each stage handoff must include:

- `다음 단계`
- `반드시 읽을 문서`
- `확정된 결정`
- `열린 결정`
- `금지 사항`
- `완료 조건`
- `참고 근거`

Plan handoff must make design questions explicit. Treat plan handoff as input to design, not as
completed design.

Plan handoff must not require `.agents/runs/` artifacts. Summarize useful runtime findings into
`evidence.md`, then reference the approved case document.

`build/tasks.md` must include:

- `작업 단위`
- `의존성`
- `제외 범위`

The human review path should stay short:

- `README.md`
- current stage `result.md`
- `evidence.md` only when evidence must be checked

Stage completion reports are written under `.agents/runs/sdlc-stage/`. They are runtime evidence,
not approved case documents. If a `complete-stage.sh` report is `blocked`, tell the user which
current-stage items remain unfinished. If it is `needs-semantic-review`, write a semantic review
file. A stage is complete only after `finalize-stage.sh` accepts that semantic review.

## Case Split Proposal

Case split proposals must include:

- `원래 아이디어`
- `분리 근거`
- `연결된 Case 후보`
- `의존성`
- `추천 순서`
- `미뤄진 영향`
- `필요한 결정`

## Report

Discovery, validation, brief, and triage reports must include:

- `확인한 출처`
- `근거 요약`
- `근거 공백`
- `추천`
- `필요한 결정`
- `추천 다음 단계`
- `인수인계`
