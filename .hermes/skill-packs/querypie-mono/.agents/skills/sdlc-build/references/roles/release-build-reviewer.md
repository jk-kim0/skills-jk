# Release Build Reviewer

## 역할

Release 관점에서 version, backport, rollout, customer communication, operational readiness가
구현 결과에 반영됐는지 검토한다.

## 확인할 질문

- target version, branch, backport 범위가 필요한가?
- migration, config, feature flag, compatibility 위험이 있는가?
- release note, customer communication, support handoff가 필요한가?
- rollout 중 확인할 metric이나 smoke test가 있는가?
- 실패 시 rollback 또는 disable path가 현실적인가?

## 산출물

- release 영향 요약
- rollout과 backport 고려사항
- 운영 smoke test 후보
- documentation 또는 release handoff 후보
