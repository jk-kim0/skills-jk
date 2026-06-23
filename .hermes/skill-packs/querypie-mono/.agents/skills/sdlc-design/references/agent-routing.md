# Design Agent Routing

이 문서는 design 단계에서 어떤 역할 관점을 사용할지 고르는 기준이다.

Native worker agent는 사용자가 명시적으로 승인한 경우에만 요청한다. 지원되지 않거나
승인되지 않으면 같은 세션에서 역할별 검토를 수행하고 그 방식을 산출물에 기록한다.

## 기본 선택 규칙

plan handoff와 evidence에서 실제 영향 영역을 찾고 필요한 역할만 고른다.

- API, service, authorization, audit, data flow가 있으면 `backend-designer`
- UI flow, component, accessibility, design token이 있으면 `frontend-designer`
- shared module, policy engine, protocol, compatibility가 있으면 `core-architect`
- deployment, config, network, secret, observability가 있으면 `infrastructure-designer`
- trust boundary, privacy, abuse case, spoofing 위험이 있으면 `security-risk-reviewer`
- test matrix, acceptance, regression scope가 필요하면 `qa-design-reviewer`
- release train, backport, rollout, customer impact가 있으면 `release-design-reviewer`

## 역할별 출력 형식

역할 검토는 짧고 구조적으로 남긴다.

- `역할`
- `검토 범위`
- `사용한 근거`
- `설계 제안`
- `위험`
- `Build 작업 제안`
- `열린 결정`
- `신뢰도`

## 최소 검토

작은 design이라도 다음 세 관점은 기본으로 확인한다.

- 기술 구조: 구현 경계와 contract가 build 가능한가?
- 품질: test와 regression 기준이 충분한가?
- 위험: 보안, 운영, release 위험이 숨겨져 있지 않은가?

## 금지 사항

- 역할 의견을 사람의 최종 결정처럼 쓰지 않는다.
- prototype 초안을 확정 구현으로 취급하지 않는다.
- 모든 역할을 기계적으로 호출하지 않는다.
- `.agents/runs/` 파일을 다음 단계의 필수 근거로 만들지 않는다.
