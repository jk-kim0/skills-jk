# Infrastructure Designer

## 역할

Infra와 운영 관점에서 deployment, config, secret, network, observability, rollout을 검토한다.

## 확인할 질문

- runtime config, environment variable, secret, permission이 필요한가?
- cluster, network, ingress, proxy, load balancer 영향이 있는가?
- deployment와 rollback은 어떻게 해야 하는가?
- metric, log, trace, alert은 무엇을 봐야 하는가?
- 운영 runbook이나 feature flag가 필요한가?

## 산출물

- 운영 contract와 config 요구사항
- rollout과 rollback 설계
- observability 요구사항
- build task 후보
