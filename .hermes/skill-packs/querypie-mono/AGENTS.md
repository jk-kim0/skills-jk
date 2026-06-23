# Codex Workspace Guide

이 저장소에서는 Claude 전용 자산을 그대로 유지하면서, Codex가 같은 워크플로우를
따라갈 수 있도록 브리지 문서를 사용합니다.

## 응답 규칙

- 기본 응답은 한글로 작성합니다.
- 코드, 경로, 명령어, 식별자는 원문 그대로 사용합니다.
- Claude 전용 slash command는 Codex에서 직접 실행되지 않습니다.
- 같은 이름의 의도가 감지되면 로컬 skill과 원본 `.claude` 문서를 읽어 수행합니다.

## 로컬 Codex Skills

- `sdlc-plan`: AI Native SDLC 계획 단계를 수행하는 공통 Agent Skill
  - 경로: `.agents/skills/sdlc-plan/SKILL.md`
- `sdlc-build`: 승인된 SDLC 설계를 구현하고 test 단계 인수인계를 작성하는 Agent Skill
  - 경로: `.agents/skills/sdlc-build/SKILL.md`
- `sdlc-backtrack`: 뒤 단계에서 발견한 근거를 검토해 앞 단계 feedback loop를 조율하는
  Agent Skill
  - 경로: `.agents/skills/sdlc-backtrack/SKILL.md`
- `claude-bridge`: 루트 `.claude/skills`, `.claude/commands` 자산을 Codex에서 사용하는 브리지
  - 경로: `.codex/skills/claude-bridge/SKILL.md`
- `frontend-doc`: `apps/front` 프론트엔드 지식 베이스 브리지
  - 경로: `apps/front/.codex/skills/frontend-doc/SKILL.md`
- `frontend-agent-bridge`: `apps/front/.claude/agents` 역할을 Codex 작업 규칙으로 변환한 브리지
  - 경로: `apps/front/.codex/skills/frontend-agent-bridge/SKILL.md`

## 사용 규칙

- `/sdlc-plan` 또는 SDLC 계획 의도가 감지되면
  `.agents/skills/sdlc-plan/SKILL.md`를 먼저 엽니다.
- `sdlc-build` 또는 SDLC 구현 단계 의도가 감지되면
  `.agents/skills/sdlc-build/SKILL.md`를 먼저 엽니다.
- `sdlc-backtrack` 또는 SDLC backtrack 의도가 감지되면
  `.agents/skills/sdlc-backtrack/SKILL.md`를 먼저 엽니다.
- 사용자가 Claude 자산 이름을 직접 언급하면 대응하는 로컬 skill을 먼저 엽니다.
- 루트 `.claude/commands/*.md`를 따라야 하는 요청은 `claude-bridge`를 사용합니다.
- `apps/front` 아래 작업은 `apps/front/AGENTS.md`를 추가로 읽고,
  기본적으로 `frontend-doc`를 먼저 사용합니다.
- 기존 `.claude` 문서는 source of truth입니다.
- Codex용 문서가 축약본일 경우, 실제 실행 전 원본 `.claude` 문서를 확인합니다.

## SDLC Plan

- 공통 SDLC core는 `.agents/sdlc/core`에 둡니다.
- 계획 단계 skill은 `.agents/skills/sdlc-plan`에 둡니다.
- Codex worker agent adapter는 `.codex/agents/sdlc-*.toml`에 둡니다.
- Claude Code adapter는 `.claude/skills/sdlc-plan`,
  `.claude/commands/sdlc-plan.md`, `.claude/agents/sdlc-*.md`에 둡니다.
- 진행 중 산출물은 `.agents/runs/sdlc-plan/<run-id>/`에 두며 git에 올리지 않습니다.
- 승인된 SDLC case는 `.sdlc/cases/<yyyy-mm-dd-name>/`에 저장합니다.
- 승인 case는 `계획 준비 요약`에 대한 사용자 승인 후에만 생성합니다.
- 모든 SDLC 산출물은 `.agents/sdlc/core/references/document-quality.md`를
  따르며, 완료 전 `validate-document-quality.sh` 검증을 통과해야 합니다.
- 모든 SDLC 단계는 `.agents/sdlc/core/references/stage-workflow.md`의
  입력, 티키타카, 출력, 출력 보정 공정을 따릅니다.
- worker Agent 의견 수집은 `.agents/skills/sdlc-plan/references/agent-invocation.md`를
  따릅니다. native subagent가 불가하면 동일 세션 역할 검토로 대체하고 그 방식을 기록합니다.
- 새 SDLC 단계 skill을 만들 때는
  `.agents/sdlc/core/references/stage-skill-authoring.md`를 먼저 확인합니다.
