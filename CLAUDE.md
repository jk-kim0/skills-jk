# Skills-JK Project Guidelines

## Session Startup Rule

**skills-jk repo에서 새 작업 시작 시 반드시:**

1. `git checkout main && git pull origin main`
2. `git checkout -b <prefix>/<descriptive-name>`

자세한 절차: `skills/session-startup/SKILL.md`

## Branch Naming

| Prefix | Use |
|--------|-----|
| feat/ | 새 기능, 스킬 추가 |
| fix/ | 버그 수정 |
| docs/ | 문서 변경 |
| refactor/ | 리팩토링 |

## Testing Command Scripts

- `bin/` 아래 실행명령과 shell script에 대한 테스트는 해당 명령 옆의 `bin/t/` 아래에 둔다.
- 실행명령 테스트는 기본적으로 Bats를 사용한다.
- 예: `bin/hermes-sync-env`의 테스트는 `bin/t/hermes-sync-env.bats`에 둔다.

## Related Skills

- [session-startup](skills/session-startup/SKILL.md): 세션 시작 시 브랜치 관리
- [branch-workflow](skills/branch-workflow/SKILL.md): 브랜치 관리 전체 워크플로우
- [commit](skills/commit/SKILL.md): 커밋 메시지 규칙
- [update-project-doc](skills/update-project-doc/SKILL.md): PR/마일스톤 후 프로젝트 문서 갱신
