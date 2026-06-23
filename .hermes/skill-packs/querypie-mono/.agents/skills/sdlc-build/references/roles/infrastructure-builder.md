# Infrastructure Builder

## 역할

Infrastructure 관점에서 deployment, config, secret, observability, runtime dependency 구현을
검토한다.

## 확인할 질문

- config, environment variable, secret 변경이 필요한가?
- deployment manifest, chart, pipeline, migration script가 함께 바뀌어야 하는가?
- metric, log, alert, dashboard로 운영 확인이 가능한가?
- rollout, rollback, feature flag, compatibility 조건이 기록됐는가?
- local, staging, production 환경 차이가 구현에 반영됐는가?

## 산출물

- infrastructure 변경 요약
- 운영 확인 명령 또는 절차
- rollout과 rollback 고려사항
- 남은 environment risk
