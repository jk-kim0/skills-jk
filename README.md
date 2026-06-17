# skills-jk

AI Agent를 위한 스킬, 태스크, 프로젝트 관리 시스템입니다.
GitHub Actions와 self-hosted runner를 통해 자동화된 워크플로우를 실행합니다.
재사용 가능한 스킬을 정의하고, 구체적인 태스크를 관리하며, 장기 프로젝트를 추적합니다.

## Runner status CLI

`bin/gh-runners`는 지원하는 GitHub organization의 self-hosted runner 목록과 상태를 조회합니다.
첫 번째 인자로 organization 이름(`querypie` 또는 `chequer-io`)을 받으며, 생략하면 `querypie`를 사용합니다.

예시:
- `python3 bin/gh-runners --summarized`
- `python3 bin/gh-runners chequer-io --summarized`
- `python3 bin/gh-runners --extended --show-labels`
- `python3 bin/gh-runners --json --no-busy-jobs`
- `python3 bin/gh-runners --busy-repo querypie/querypie-mono --busy-repo querypie/querypie-docs`
- `python3 bin/gh-runners --scan-all-repos`

기본 busy job 조회는 빠른 응답을 위해 최근 self-hosted runner job 표본 상위 5개 repo만 스캔합니다.
현재 기본 후보: `corp-web-app`, `corp-web-japan`, `outbound-agent`, `corp-web-contents`, `payroll`.
`chequer-io`는 기본 busy job 후보가 없으므로, busy job 매칭이 필요하면 `--busy-repo` 또는 `--scan-all-repos`를 지정합니다.
전체 organization repo를 스캔해야 할 때만 `--scan-all-repos`를 사용합니다.
