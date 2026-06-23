# Backtrack Decision Model

이 문서는 발견된 문제가 backtrack 대상인지 판단하는 기준이다.

## 분류

### 현재 단계에서 처리

다음이면 backtrack하지 않는다.

- 현재 단계의 검증, 구현, 리뷰, 문서화 책임으로 해결 가능하다.
- 앞 단계 결정은 맞고 현재 단계 실행만 잘못됐다.
- 문서 누락이 현재 단계 handoff에만 영향을 준다.

### Downstream handoff

다음이면 backtrack하지 않고 다음 단계로 넘긴다.

- 현재 단계 완료는 가능하지만 다음 단계 검증이나 운영 확인이 필요하다.
- design이나 build decision은 바꾸지 않아도 된다.
- 위험을 숨기지 않고 handoff에 남기면 된다.

### Backtrack

다음이면 backtrack을 권장한다.

- 앞 단계의 확정 결정이 실제 근거와 충돌한다.
- 앞 단계가 닫았어야 할 질문이 열린 채 downstream으로 넘어왔다.
- 현재 단계에서 수정하면 scope, design contract, build task trace가 깨진다.
- downstream 산출물이 앞 단계의 잘못된 전제를 계속 신뢰하게 된다.

### Case split 또는 새 plan

다음이면 backtrack보다 case split 또는 새 plan을 권장한다.

- case goal 자체가 바뀐다.
- 하나의 trunk-based PR 경계를 넘는다.
- 여러 stage를 전면 재작성해야 한다.
- 제품 방향이나 고객 impact를 다시 기획해야 한다.

## 근거 검토

근거는 다음 질문으로 검토한다.

- 공식 case 문서와 충돌하는가?
- source, test, spec, 운영 기록 같은 확인 가능한 근거가 있는가?
- 현재 단계에서 처리하면 어떤 계약이 깨지는가?
- target stage에서 닫아야 하는 질문은 정확히 무엇인가?
- backtrack하지 않으면 downstream에서 어떤 잘못된 판단이 이어지는가?

## 선택지 작성

선택지는 보통 2-3개만 제시한다.

- 추천안: 가장 일관된 SDLC 경로
- 최소 변경안: downstream 재작업을 줄이는 경로
- 분리안: scope가 큰 경우 별도 case나 plan으로 분리하는 경로

각 선택지는 장점, 비용, 위험, 다시 검토할 산출물을 함께 적는다.
