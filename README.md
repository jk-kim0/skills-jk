# skills-jk

AI Agent를 위한 스킬, 태스크, 프로젝트 관리 시스템입니다.
GitHub Actions와 self-hosted runner를 통해 자동화된 워크플로우를 실행합니다.
재사용 가능한 스킬을 정의하고, 구체적인 태스크를 관리하며, 장기 프로젝트를 추적합니다.

## Runner status CLI

`bin/gh-runners`는 QueryPie organization의 GitHub self-hosted runner 목록과 상태를 조회합니다.

예시:
- `python3 bin/gh-runners --summarized`
- `python3 bin/gh-runners --extended --show-labels`
- `python3 bin/gh-runners --json --no-busy-jobs`
- `python3 bin/gh-runners --busy-repo querypie/querypie-mono --busy-repo querypie/querypie-docs`
