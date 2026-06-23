# Case Structure

승인된 SDLC case는 사람이 리뷰하고 다음 단계 Agent가 다시 시작할 수 있는 공식
상태 저장소다. 대화 기록은 참고 자료일 뿐이며, compact 또는 새 세션 이후에는
공식 상태로 간주하지 않는다.

## Directory Layout

```text
.sdlc/cases/<yyyy-mm-dd-name>/
  README.md
  metadata.yaml
  evidence.md

  plan/
    result.md
    handoff.md

  design/
    result.md
    handoff.md

  build/
    tasks.md
    result.md
    handoff.md

  test/
    result.md
    handoff.md

  review/
    result.md
    handoff.md

  documentation/
    result.md
    handoff.md

  release/
    result.md
    handoff.md
```

## Root Documents

- `README.md`: 사람이 처음 읽는 1페이지 입구다. 요약, 남은 결정, 다음 행동, 주요
  문서 링크만 둔다.
- `metadata.yaml`: Agent와 script가 읽는 상태 카드다. case id, 현재 단계, 관련
  ticket, 승인 상태, 다음 단계, source 목록을 구조화해서 둔다.
  `schemas/case-metadata.schema.json`을 따라야 하며 임의 key를 추가하지 않는다.
- `evidence.md`: Jira, Slack, GitHub, repository, worker 의견에서 얻은 근거를 모은
  appendix다. 사람이 기본으로 읽는 문서가 아니라 의심이 생겼을 때 확인한다.

## Stage Documents

- `result.md`: 해당 단계에서 확정한 최종 결과다. 사람이 승인할 판단과 다음 단계가
  따라야 할 결론을 담는다.
- `handoff.md`: 다음 단계가 반드시 읽는 인수인계다. 읽을 문서, 열린 결정, 금지
  사항, 다음 단계 진입 조건을 짧게 담는다.
- `build/tasks.md`: design 단계가 만든 구현 작업 목록이다. build 단계는 이 파일을
  기준으로 세부 작업을 나눈다.

## Writing Rules

1. 모든 사용자-facing 문서와 공식 case 문서는 한국어로 작성한다.
2. code path, command, ticket ID, API name, role id는 원문을 유지한다.
3. run artifact를 그대로 복사하지 않는다. 승인 case에는 요약하고 통합해서 남긴다.
4. 중요한 사용자 결정은 즉시 `README.md`, `metadata.yaml`, 현재 단계 문서에
   checkpoint한다.
5. 단계 lifecycle status는 `metadata.yaml`에만 기록한다. `README.md`, `result.md`,
   `handoff.md`에는 현재 단계나 상태값을 복제하지 않는다.
6. `.agents/runs/` runtime artifact는 공식 handoff의 필수 근거로 두지 않는다.
   필요한 worker 의견과 조사 결과는 `evidence.md`에 요약해서 승격한다.
7. 다음 단계 Agent가 전체 대화 없이도 이어갈 수 없으면 handoff가 불완전한 것이다.

## Runtime Rules

각 단계 Agent는 작업 시작 전에 `prepare-stage.sh <case-id> <stage>`를 실행한다.
작업 중 중요한 결정이 생기면 `checkpoint-stage.sh`로 기록한다. 작업 종료 전에는
`complete-stage.sh <case-id> <stage>`로 미완료 사항을 점검한다. 그 다음
semantic review를 작성하고, 통과 시 `finalize-stage.sh`로 완료를 확정한다.
마지막으로 `validate-case.sh <case-id> <stage>`를 실행한다.

`validate-case.sh`는 현재 단계 문서만 보지 않는다. 승인 case 전체의 Markdown 품질,
빈 placeholder, `metadata.yaml` schema, lifecycle status 복제 여부를 함께 검사한다.

미시작 단계 문서에는 빈 bullet이나 빈 table row를 두지 않는다. 아직 작성할 내용이
없으면 `없음` 또는 “아직 시작하지 않음”처럼 명시적인 문장을 쓴다.
