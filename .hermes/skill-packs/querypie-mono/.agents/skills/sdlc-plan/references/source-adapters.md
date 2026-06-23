# Source Adapters

Source adapter는 외부 서비스에서 근거를 가져오는 표준 진입점이다. Agent가 직접
API 호출 방식을 매번 새로 만들지 않도록, 먼저 adapter script를 사용한다.

## Common Rules

1. 외부 source 조회는 가능한 한 CLI adapter를 먼저 사용한다.
2. raw 결과는 run artifact에 저장하고, 승인 case에는 요약만 승격한다.
3. 조회 실패도 근거 공백으로 기록한다.
4. 긴 원문, 민감한 원문, 첨부 원문은 case 문서에 그대로 붙이지 않는다.
5. adapter로 해결되지 않는 작업만 API fallback을 검토한다.

## Jira CLI Adapter

Jira ticket 조회는 기본적으로 Jira API 직접 호출이 아니라 Jira CLI를 사용한다.

사용 script:

```bash
.agents/skills/sdlc-plan/scripts/collect-jira.sh <issue-key> --run-id <run-id>
```

기본 command:

```bash
jira issue view <issue-key> --raw
jira issue view <issue-key> --plain --comments <n>
```

저장 위치:

```text
.agents/runs/sdlc-plan/<run-id>/sources/jira/<issue-key>.raw.json
.agents/runs/sdlc-plan/<run-id>/sources/jira/<issue-key>.plain.txt
.agents/runs/sdlc-plan/<run-id>/sources/jira/<issue-key>.meta.md
```

`--raw` 결과는 Agent 분석과 구조화에 사용한다. `--plain` 결과는 사람이 원문을
확인할 때 사용한다. 승인 case의 `evidence.md`에는 ticket 요약, 관련 결정, 근거
공백만 적는다.

## Jira Fallbacks

Jira CLI가 없거나 인증되지 않았거나 권한이 없으면 다음을 기록한다.

- 사용한 command
- 실패 시각
- exit code
- stderr 요약
- 필요한 사용자 조치

첨부파일 다운로드, 특수 field, bulk pagination처럼 CLI로 충분하지 않은 경우에만
API fallback을 허용한다. 이 경우에도 API 응답 원문은 run artifact에 두고,
승인 case에는 요약만 남긴다.
