# Stage Skill Authoring

이 문서는 `sdlc-design`, `sdlc-build`처럼 새 SDLC 단계 skill을 만들 때 따른다.

새 skill의 목적은 한 단계의 판단과 산출물을 안정적으로 만들게 하는 것이다.
공통 case 구조, 상태 관리, 문서 품질, 완료 절차는 core를 재사용한다.

## 기본 구조

새 단계 skill은 다음 구조를 권장한다.

```text
.agents/skills/sdlc-<stage>/
  SKILL.md
  agents/openai.yaml
  assets/prompts/stage-content-review.md
  assets/templates/<stage>-result.md
  assets/templates/<stage>-handoff.md
  references/workflow.md
  references/agent-routing.md
  references/roles/*.md
  scripts/validate-sdlc-<stage>.sh
```

단계별로 필요하지 않은 `agent-routing.md`나 `roles`는 만들지 않아도 된다.

`agents/openai.yaml`은 OpenAI/Codex UI adapter가 skill 목록, chip, 기본 prompt를
표시하기 위한 metadata다. stage workflow script가 실행 판단이나 산출물 검증을 위해
읽는 파일은 아니다.

이 파일을 만들 때는 `SKILL.md`의 목적과 호출 시점을 사람이 훑어볼 수 있는 짧은
문구로 요약한다. 현재 consumer가 없는 환경이라도 stage skill 구조를 일관되게
유지하려면 둘 수 있지만, 실행 필수 설정처럼 설명하면 안 된다.

## 만들지 말아야 할 것

새 단계 skill은 다음 공통 파일을 복사해서 가지면 안 된다.

- case 구조 문서
- stage workflow와 stage contract
- document quality 문서
- metadata schema
- `prepare`, `checkpoint`, `finish`, `finalize`, `validate` 공통 script
- `case-readme`, `case-metadata`, `case-evidence` 공통 template

이 항목은 `.agents/sdlc/core`의 source of truth를 그대로 사용한다.

## SKILL.md 작성 규칙

`SKILL.md`에는 단계의 핵심 사용 절차만 둔다.

다음 항목은 반드시 명시한다.

- 어떤 요청에서 이 skill을 사용할지
- 시작할 때 읽을 stage 전용 reference
- 시작할 때 읽을 core reference
- `prepare-stage.sh` 실행 규칙
- 작성할 stage 산출물
- `finish-stage.sh`와 `validate-case.sh` 실행 규칙
- backtrack이 필요한 경우 core `stage-backtrack.md`를 따른다는 규칙
- 사용자 응답과 산출물을 한국어로 작성한다는 규칙

## Core 연결 규칙

case 생성이 필요하면 core scaffold script를 사용한다.

```bash
.agents/sdlc/core/scripts/scaffold-case.sh <case-id> \
  --stage-template-root .agents/skills/sdlc-<stage>/assets/templates
```

단계를 시작할 때는 core prepare script를 사용한다.

```bash
.agents/sdlc/core/scripts/prepare-stage.sh <case-id> <stage>
```

단계를 마무리할 때는 core finish script를 사용한다.

```bash
.agents/sdlc/core/scripts/finish-stage.sh <case-id> <stage>
```

case를 검증할 때는 core validate script를 사용한다.

```bash
.agents/sdlc/core/scripts/validate-case.sh <case-id> <stage>
```

앞 단계로 되돌릴 때는 core backtrack script를 사용한다.

```bash
.agents/sdlc/core/scripts/backtrack-stage.sh <case-id> <target-stage> \
  --reason "<reason>" \
  --question "<question>"
```

## Template 규칙

단계별 template은 해당 단계가 직접 작성하는 문서만 포함한다.

예를 들어 `sdlc-design`은 `design-result.md`, `design-handoff.md`,
필요하면 `build-tasks.md` override만 가진다.

공통 root 문서와 모든 단계에 공통인 문서는 core template을 사용한다.

## 검증 규칙

각 단계 skill은 자기 검증 script를 가진다.

검증 script는 다음을 확인한다.

- 단계 skill의 필수 파일이 존재하는가
- core reference와 core script 경로가 올바른가
- backtrack reference와 script 경로가 올바른가
- 단계 전용 template이 존재하는가
- 사용자-facing 문서가 내부 검사 용어를 노출하지 않는가
- sample case를 만들고 core 검증을 통과하는가

검증 script는 `.agents/runs/` 아래에 임시 case를 만들고, git에 올리지 않는다.

## 작성 품질

모든 설명과 산출물은 한국어로 작성한다.

코드, 명령어, file path, ticket id, role id는 원문을 유지한다.

문서 한 줄은 80자에서 100자 사이를 목표로 한다. 길이를 맞추려고 어색하게 끊지
말고, 문장을 짧게 나누어 읽기 쉽게 만든다.
