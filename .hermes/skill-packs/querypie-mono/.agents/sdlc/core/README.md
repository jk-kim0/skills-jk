# SDLC Core

`.agents/sdlc/core`는 모든 SDLC 단계가 함께 쓰는 공통 규칙과 도구를 담는다.

여기는 특정 단계의 업무 지식이 아니라 case 구조, 단계 계약, 문서 품질, 상태 관리,
마무리 절차처럼 모든 단계가 같은 방식으로 지켜야 하는 기준을 둔다.

## 책임

core는 다음 항목을 담당한다.

- `.sdlc/cases/<case-id>/` 아래의 공식 case 구조
- `metadata.yaml` schema와 단계 lifecycle status 관리
- `prepare`, `checkpoint`, `backtrack`, `finish`, `finalize`, `validate` 공통 script
- 모든 단계가 따르는 입력, 티키타카, 출력, 출력 보정 공정
- 모든 SDLC 산출물이 따라야 하는 Markdown 품질 기준
- 새 단계 skill이 재사용할 공통 template과 작성 규칙

core는 다음 항목을 담당하지 않는다.

- 특정 단계의 전문 판단
- 특정 단계의 worker role 구성
- 특정 단계의 전용 template과 prompt
- 특정 단계에서만 필요한 외부 service adapter

## 단계 Skill과의 관계

각 단계 skill은 자기 단계의 workflow, prompt, role, 전용 template만 가진다.

각 단계 skill은 case 생성, 상태 변경, 문서 품질 검증, 완료 처리를 직접 새로 만들지
않고 core script와 core reference를 호출한다.

새 단계 skill을 만들 때는 `.agents/sdlc/core/references/stage-skill-authoring.md`를
읽고, 공통 파일을 복사하지 않는다.

## 기본 사용 순서

단계를 시작할 때는 다음 script로 현재 case 문맥을 복구한다.

```bash
.agents/sdlc/core/scripts/prepare-stage.sh <case-id> <stage>
```

단계를 마무리할 때는 다음 script를 사용자-facing 진입점으로 사용한다.

```bash
.agents/sdlc/core/scripts/finish-stage.sh <case-id> <stage>
```

case 상태를 확인할 때는 다음 script를 사용한다.

```bash
.agents/sdlc/core/scripts/validate-case.sh <case-id> <stage>
```

뒤 단계에서 앞 단계 결정을 짧게 다시 열어야 하면 다음 script를 사용한다.

```bash
.agents/sdlc/core/scripts/backtrack-stage.sh <case-id> <target-stage> \
  --reason "<reason>" \
  --question "<question>"
```

## 설계 원칙

공식 상태는 chat history가 아니라 `.sdlc/cases/<case-id>/`와 `metadata.yaml`이다.

단계별 판단은 stage skill에 둔다. 공통 절차와 검증은 core에 둔다.

문서가 길어질수록 다음 단계가 읽기 어렵다. core는 짧고 일관된 산출물을 요구한다.
