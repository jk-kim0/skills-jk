# Skills-JK Project Guidelines

## Session Startup Rule

**skills-jk repo에서 새 작업 시작 시 반드시:**

1. `git checkout main && git pull origin main`
2. `git checkout -b <prefix>/<descriptive-name>`

자세한 절차: `skills/ops/session-startup.md`

## Branch Naming

| Prefix | Use |
|--------|-----|
| feat/ | 새 기능, 스킬 추가 |
| fix/ | 버그 수정 |
| docs/ | 문서 변경 |
| refactor/ | 리팩토링 |

## Related Skills

- [session-startup](skills/ops/session-startup.md): 세션 시작 시 브랜치 관리
- [branch-workflow](skills/ops/branch-workflow.md): 브랜치 관리 전체 워크플로우
- [commit](skills/ops/commit.md): 커밋 메시지 규칙
- [update-project-doc](skills/ops/update-project-doc.md): PR/마일스톤 후 프로젝트 문서 갱신
