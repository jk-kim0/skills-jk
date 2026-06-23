# Build Agent Routing

이 문서는 build 단계에서 어떤 역할 관점을 사용할지 고르는 기준이다.

기본 방식은 같은 세션에서 역할별 검토를 수행하고 그 방식을 산출물에 기록하는 것이다.
Native worker agent는 대응되는 `.codex/agents` 또는 `.claude/agents` adapter가 있고,
사용자가 명시적으로 승인한 경우에만 요청한다.

## 기본 선택 규칙

`build/tasks.md`, 변경 파일, design handoff에서 실제 영향 영역을 찾고 필요한 역할만
고른다.

- 역할을 고르면 `references/roles/<role-id>.md`를 읽고 그 기준으로 검토한다.
- API, service, authorization, audit, data flow 구현이 있으면 `backend-builder`
- UI flow, component, state, accessibility 구현이 있으면 `frontend-builder`
- shared module, protocol, compatibility, policy engine 구현이 있으면 `core-builder`
- deployment, config, secret, observability 구현이 있으면 `infrastructure-builder`
- trust boundary, privacy, spoofing, permission 위험이 있으면 `security-risk-reviewer`
- test matrix, acceptance, regression scope가 필요하면 `qa-build-reviewer`
- backport, rollout, customer impact가 있으면 `release-build-reviewer`

## 역할별 출력 형식

역할 검토는 짧고 구조적으로 남긴다.

- `역할`
- `검토 범위`
- `사용한 근거`
- `구현 제안`
- `위험`
- `검증 제안`
- `열린 결정`
- `신뢰도`

## 최소 검토

작은 build라도 다음 세 관점은 기본으로 확인한다.

- 구현 구조: design contract와 task 범위를 지켰는가?
- 품질: 자동 또는 수동 검증 기준이 충분한가?
- 위험: 보안, 운영, release 위험이 숨겨져 있지 않은가?

## 금지 사항

- 역할 의견을 사람의 최종 결정처럼 쓰지 않는다.
- design 범위를 역할 검토만으로 확장하지 않는다.
- 모든 역할을 기계적으로 호출하지 않는다.
- `.agents/runs/` 파일을 다음 단계의 필수 근거로 만들지 않는다.
