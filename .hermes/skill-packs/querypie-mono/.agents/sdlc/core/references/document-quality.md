# Document Quality

이 문서는 모든 SDLC 산출물이 따라야 하는 공통 문서 품질 계약이다. `sdlc-plan`뿐 아니라 앞으로 추가될
SDLC skill도 이 문서를 먼저 읽어야 한다.

목표는 사람이 긴 산출물을 억지로 해석하지 않아도 결정, 근거, 다음 행동을 바로 찾을 수 있게 만드는
것이다.

## 기본 원칙

- 사용자 응답과 SDLC 산출물은 기본적으로 한국어로 작성한다.
- 코드, 경로, 명령어, ticket ID, API 이름, 제품명, role id는 원문을 유지한다.
- 문서는 먼저 결론을 말하고, 그 뒤에 근거와 선택지를 둔다.
- 한 문단은 되도록 세 문장 이하로 쓴다.
- 한 bullet은 하나의 생각만 담는다.
- 비어 있는 section은 빈 bullet로 두지 말고 `없음` 또는 실제 내용을 쓴다.
- 사람이 결정해야 하는 항목과 Agent가 보완할 항목을 구분한다.

## 줄 길이

문서의 prose line은 `printWidth` 80-100 범위에 맞춘다.

- 권장 폭은 80-100자이다.
- hard limit은 기본 100자이다.
- fenced code block 안의 code line은 예외로 둔다.
- URL은 원문 보존이 필요하므로 길이 검증에서 예외로 둔다.
- 긴 표보다 짧은 bullet 목록을 우선한다.

## 명확성

좋은 문장은 다음 질문에 답한다.

- 무엇을 결정해야 하는가?
- 왜 그렇게 판단했는가?
- 어떤 근거를 확인했는가?
- 다음 단계는 무엇을 읽고 무엇을 하지 말아야 하는가?
- 아직 모르는 것은 무엇이고 언제 다시 확인해야 하는가?

다음 표현은 그대로 두지 않는다. 쓰려면 조건, 담당자, 기한, 판단 기준을 붙인다.

- `추후`
- `필요시`
- `적절히`
- `대략`
- `검토 필요`
- `논의 필요`

## 산출물 구조

Root `README.md`는 사람이 빠르게 읽는 index 역할을 한다.

- 추천 방향과 남은 결정은 `README.md`에서 바로 보여야 한다.
- 자세한 내용은 현재 단계의 `result.md`에 둔다.
- 다음 단계가 이어받을 내용은 현재 단계의 `handoff.md`에 둔다.
- 근거 원문과 요약은 `evidence.md`에 둔다.
- 같은 내용을 여러 문서에 길게 반복하지 않는다.

Root `metadata.yaml`은 `schemas/case-metadata.schema.json`을 따른다. 사람이 쓰는
설명 문서가 아니라 다음 Agent와 script가 읽는 상태 카드이므로 key와 값의 형태를
임의로 바꾸지 않는다.

단계 lifecycle status는 `metadata.yaml`에만 둔다. `README.md`, `result.md`,
`handoff.md`에는 `현재 단계`, `상태`, `Status` 같은 현재 상태 field를 만들지 않는다.

## 검증 방식

문서 품질은 세 단계로 확인한다.

1. Prettier가 `printWidth: 100`, `proseWrap: preserve` 기준으로 포맷을 확인한다.
2. markdownlint가 Markdown 구조, 줄 길이, list 형식을 확인한다.
3. `validate-document-quality.sh`가 빈 placeholder와 SDLC 전용 field를 확인한다.

단계 완료 전에는 현재 단계의 `README.md`, `<stage>/result.md`, `<stage>/handoff.md`가 이 검증을
통과해야 한다.

Semantic review file도 finalize 전에 같은 문서 품질 검증을 통과해야 한다.

자동 포맷은 `format-document-quality.sh`로만 실행한다. 단계 완료와 finalize는 문서를 자동
수정하지 않고 실패 사유만 보고한다.

Prettier는 prose 줄바꿈을 강제로 바꾸지 않는다. markdownlint와 custom check는 줄 길이를
보고만 하며, 문서를 자동 수정하지 않는다.

markdownlint는 공통 `mise` 도구에 등록하지 않는다. 로컬에 설치된 `markdownlint-cli2`가
없으면 validator가 pinned `npx --yes markdownlint-cli2@0.22.1`로 실행한다.

## 작성자 체크리스트

- 첫 화면에서 추천 방향, 상태, 다음 행동을 찾을 수 있는가?
- `남은 결정`이 현재 단계 blocker인지 다음 단계 인수인계인지 구분되는가?
- 빈 bullet, 빈 field, `TODO`, `TBD`, `[미완료]`가 남아 있지 않은가?
- 빈 table cell이나 미시작 단계의 빈 placeholder row가 남아 있지 않은가?
- `metadata.yaml`이 schema를 통과하고 실제 검증 단계와 일치하는가?
- Markdown 문서에 lifecycle status가 복제되어 있지 않은가?
- 한 줄이 너무 길어 읽는 흐름을 끊지 않는가?
- compact 후 새 세션이 문서만 읽고 이어갈 수 있는가?
