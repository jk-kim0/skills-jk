# Completion Review

단계 완료 검증은 두 층으로 나눈다.

## Hard Gate

`complete-stage.sh <case-id> <stage>`가 담당한다.

이 검증은 재현 가능해야 하므로 script가 판단한다.

- 필수 파일이 있는가
- 문서가 비어 있지 않은가
- placeholder가 남아 있는가
- `TODO`, `TBD`, `[미완료]`, `[blocker]` 같은 명시 신호가 있는가

Hard gate가 `blocked`이면 단계를 완료할 수 없다. Agent는 미완료 파일과 줄을
사용자에게 알려야 한다.

## Semantic Review

Hard gate가 통과하면 Agent가 LLM semantic review를 수행한다.

이 검토는 문맥상 빠진 내용을 찾기 위한 것이다. 단순히 단어를 찾는 검증이
아니다.

검토 질문:

- 현재 단계의 책임을 실제로 수행했는가?
- 결론과 근거가 연결되는가?
- 다음 단계가 대화 기록 없이 이어갈 수 있는가?
- `handoff.md`가 다음 단계의 읽을 문서, 열린 결정, 금지 사항, 완료 조건을 담는가?
- 문장은 있지만 내용이 빈약한 section은 없는가?
- 현재 단계에서 닫아야 할 결정과 다음 단계로 넘길 결정이 구분됐는가?
- `references/document-quality.md`의 읽기 쉬운 문서 기준을 지켰는가?

## Decision Values

Semantic review file은 `completion_decision`을 반드시 가진다.

- `pass`: 의미상 완료 가능하다.
- `proceed-with-concerns`: 우려는 있지만 사용자 승인으로 다음 단계에 넘길 수 있다.
- `blocked`: 현재 단계에서 보완해야 한다.

`proceed-with-concerns`는 `user_approved_concerns: true`일 때만 finalize할 수 있다.

## Required Flow

1. 사용자가 단계 완료 의사를 표현한다.
2. Agent가 `complete-stage.sh <case-id> <stage>`를 실행한다.
3. Hard blocker가 있으면 사용자에게 보고하고 멈춘다.
4. Hard blocker가 없으면 semantic review file을 작성한다.
5. Semantic blocker가 있으면 사용자에게 보고하고 멈춘다.
6. 통과했거나 사용자가 concern 진행을 승인하면 `finalize-stage.sh`를 실행한다.

Agent는 semantic review 없이 단계 완료를 선언하면 안 된다.

Semantic review file도 finalize 전에 `validate-document-quality.sh`를 통과해야 한다.
