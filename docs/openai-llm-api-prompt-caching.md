# OpenAI LLM API 예제 4: 여러 차례 대화와 프롬프트 캐시

이 문서는 여러 차례 질의와 응답을 주고받을 때 프롬프트 캐시를 재사용하는 규칙과 구체적인 요청 예제를 설명한다.
공식 문서 확인 기준일은 2026-10-01이다.
주 예제는 Responses API, `gpt-5.6-terra`, 클라이언트의 전체 이력 관리 방식이다.
GPT-5.6 이후의 캐시 경계·보존 시간·요금 규칙은 이전 모델과 다르다.

## 캐시가 재사용하는 대상

Prompt caching은 모델이 이미 처리한 입력의 공통 prefix에 대한 계산 상태를 재사용한다.
Prefix는 렌더링된 모델 입력의 맨 앞부터 연속해서 같은 부분이다.
같은 내용이 요청 뒤쪽에 있어도 그 앞의 prefix가 바뀌면 해당 구간을 그대로 재사용할 수 없다.
JSON 최상위 key 순서 자체보다 모델에 렌더링되는 메시지·content·도구·설정이 중요한 기준이다.

캐시는 이전 답변 문자열을 그대로 돌려주는 응답 캐시가 아니다.
매 요청의 출력은 새로 생성된다.
캐시 토큰도 context window와 rate limit에 반영되며, 저장된 Response나 대화 객체와 별개의 기능이다.

```text
요청 1: [고정 도구/지침/참고자료 P][질문 U1]
요청 2: [고정 도구/지침/참고자료 P][질문 U1][답변 A1][질문 U2]
요청 3: [고정 도구/지침/참고자료 P][질문 U1][답변 A1][질문 U2][답변 A2][질문 U3]

P는 그대로 유지한다.
이전 질문과 답변도 보존하고 새 item을 마지막에 추가한다.
모델의 유효한 캐시 경계와 길이 조건을 만족하면 이전 요청의 prefix까지 재사용할 수 있다.
```

## 모델 세대별 규칙

다음 내용은 공식 Prompt caching 문서의 확인 기준일 동작이다.
모델이나 API가 바뀌면 지원 여부를 다시 확인한다.

| 항목 | GPT-5.6 이후 | GPT-5.5 및 그 이전 |
| --- | --- | --- |
| 최소 캐시 길이 | 숨겨진 OpenAI 지침을 제외한 visible input 1,024 토큰 | 모델과 tools·schema·reasoning 등 설정에 따라 달라짐 |
| 자동 경계 | 최근 eligible message의 끝 | 모델별 간격에 따른 implicit 경계 |
| 명시적 경계 | 지원 | 지원하지 않음 |
| 캐시 토큰 보고 | 매칭된 실제 eligible 경계 기준 | 숨겨진 토큰을 제외하고 128의 배수로 내림 |
| 보존 설정 | `prompt_cache_options.ttl: "30m"` | 지원 모델의 `prompt_cache_retention` |
| `prompt_cache_key` | 고객·사용자별 cache accounting 분리에 선택적으로 사용 | 안정적인 key로 라우팅 최적화 |
| 캐시 쓰기 비용 | 일반 입력 단가의 1.25배 | 별도의 cache-write 할증 없음 |
| 캐시 읽기 비용 | 보통 일반 입력의 0.1배이며 GPT-6.1 Sol은 0.05배 | 모델별 cached-input 요금 |

GPT-5.6 이후 `30m`은 마지막 쓰기·재사용 이후의 최소 캐시 수명 설정이다.
라우팅, 해당 경계의 존재, prefix 일치 여부 등도 필요하므로 TTL 설정만으로 hit가 보장되지는 않는다.
현재 공식 문서에서 이 세대의 지원 TTL 값은 `30m`이다.
이전 모델의 `24h`·`in_memory` 설정을 그대로 적용하지 않는다.

## 여러 차례 대화에서 지킬 규칙

| 규칙 | 이유와 적용 |
| --- | --- |
| 고정 지침과 공통 참고자료를 앞에 둔다 | 매 요청이 동일한 긴 prefix로 시작하게 한다 |
| 시각·요청 ID·현재 질문은 뒤에 둔다 | prefix 시작 부분을 매번 바꾸지 않는다 |
| 기존 메시지를 수정하지 않고 새 item을 추가한다 | 이전 요청의 content와 message ending을 보존한다 |
| 모델 output item을 재전달 가능한 형태로 보존한다 | tool·reasoning item과 assistant phase를 유지한다 |
| 모델과 주요 설정을 유지한다 | model, reasoning effort, verbosity, output schema 등의 변경은 렌더링된 prefix를 바꿀 수 있다 |
| tools의 이름·설명·schema·순서를 유지한다 | 도구 정의도 모델 입력 prefix에 영향을 준다 |
| 호출하지 않을 도구는 tool_choice로 제한한다 | tools 배열을 삭제하거나 재작성하는 일을 줄인다 |
| 캐시 경계를 처음부터 설계한다 | 공유된 prefix라도 저장·조회 가능한 경계가 없으면 재사용되지 않을 수 있다 |
| 필요할 때 compaction을 적용하고 전체 비용을 측정한다 | 요약이 prefix를 바꾸더라도 입력 감소가 더 유리할 수 있다 |
| 실제 usage와 latency를 측정한다 | 같은 key·대화 ID·긴 입력만으로 hit를 판단하지 않는다 |

이미 보낸 user 메시지 끝에 새 텍스트를 덧붙이는 대신 새 메시지로 추가한다.
메시지를 확장하면 이전 implicit 경계가 메시지 중간으로 옮겨져 재사용되지 않을 수 있다.
과거 item의 공백·문장·순서를 반복적으로 정규화하거나 바꾸지 않는다.
Client trace ID는 HTTP 헤더로 관리하고 고정 developer 지침의 첫 줄에 매번 넣지 않는다.

## 캐시 Mode와 경계 설정

### Implicit mode와 explicit breakpoint 함께 사용

GPT-5.6 이후 기본 `implicit` mode는 최근 eligible message 끝에 자동 경계를 둔다.
Eligible message는 user, 연속 tool result 중 마지막 결과, 처음 연속된 developer message 묶음의 마지막 메시지 등이다.
멀티턴에서는 이 mode가 이전 user·tool 경계를 조회해 커지는 대화 prefix를 재사용하는 데 유용하다.

고정 참고자료의 끝에도 explicit breakpoint를 두면 다른 질문이나 대화 분기에서도 공통 참고자료 prefix를 조회하기 쉽다.
Breakpoint는 지원되는 content block의 `prompt_cache_breakpoint`에 지정한다.
최상위 `instructions`에는 이 경계를 직접 넣을 수 없으므로 고정 지침을 developer message의 `input_text`로 보낸다.

한 요청은 최대 4개의 cache write 경계를 선택할 수 있다.
Implicit 경계가 하나를 사용하면 추가 explicit write 경계는 최대 3개이다.
반복 이력에 과거 explicit 경계가 더 많이 남아 있어도 모든 경계를 매 요청 새로 쓰는 것은 아니다.

### Explicit-only mode

`prompt_cache_options.mode: "explicit"`은 개발자가 표시한 경계만 사용한다.
Explicit breakpoint가 하나도 없으면 이 mode에서는 캐시를 사용하거나 쓰지 않는다.
고정 참고자료 끝에만 경계를 두면 그 뒤의 자주 바뀌는 suffix에 대한 cache-write 비용을 피할 수 있다.
다만 자라는 대화 이력까지 캐시하고 싶다면 재사용할 과거 경계도 보존하고 적절한 추가 경계를 선택해야 한다.

첫 요청을 implicit으로 쓰고 두 번째 요청을 explicit-only로 바꿀 때도 주의한다.
두 번째 요청에 첫 요청의 저장된 endpoint와 맞는 explicit 경계가 없으면 그 prefix를 조회하지 못할 수 있다.

## 구체적인 API Call: 정책을 참고하는 두 차례 대화

다음 payload의 상점 정책은 캐시 설명을 위해 만든 가상 참고자료이다.
실제 회사 정책이나 주문 데이터가 아니다.
긴 정책 내용을 고정 developer prefix로 두고, 첫 질문과 실제 API가 반환한 output을 다음 요청에서 보존한다.
모델의 최소 토큰 길이는 해당 모델·설정의 실제 사용량과 tokenizer로 확인해야 한다.
아래 응답 ID와 토큰 수는 설명용이며 실제 cache hit 또는 측정 결과가 아니다.

### 호출 1: 고정 Prefix와 첫 질문

다음 JSON을 `cache-request-01.json`으로 저장하고 호출한다.

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @cache-request-01.json
```

요청 payload:

```json
{
  "model": "gpt-5.6-terra",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "prompt_cache_key": "sample-store:policy-v1:customer-demo",
  "prompt_cache_options": { "mode": "implicit", "ttl": "30m" },
  "input": [
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "이 대화는 가상 온라인 상점의 상담 예제이다. 한국어로 답하고 아래 고정 정책을 일관되게 적용한다. 고객이 설명한 조건과 정책에서 확인할 수 있는 내용을 구분한다. 실제 주문 조회, 반품 접수, 결제 취소를 수행했다고 말하지 않는다. 질문이 단순한 정책 확인이면 관련 조건과 결론을 간단히 설명한다. 필요한 조건이 빠지면 무엇을 확인해야 하는지 알려준다. 이전 대화에서 확인한 조건을 이어서 사용하되 고객이 새 조건을 제시하면 최신 조건을 적용한다. 정책에 없는 예외나 혜택을 만들어내지 않는다. 상담 답변과 실제 업무 처리 완료를 구분하고, 예상 처리 시간을 확정된 처리 완료 시간으로 표현하지 않는다."
        },
        {
          "type": "input_text",
          "text": "반품 기한 정책: 단순 변심에 의한 반품은 배송 완료일을 기준으로 7일 이내에 신청할 수 있다. 이 예제의 일수는 영업일이 아닌 달력 날짜의 차이로 계산한다. 배송 당일은 경과 0일이고 다음 날은 경과 1일이다. 경과 7일까지 신청 가능하고 경과 8일부터 일반적인 단순 변심 반품 기한이 지난 것으로 판단한다. 미개봉 상품이라도 기한 조건을 별도로 확인한다. 기한이 지났다는 이유만으로 불량 상품의 권리까지 동일하게 처리하지 않으며 불량은 별도 확인 절차를 안내한다. 날짜가 불명확하면 실제 배송 완료일과 신청일을 확인한다. 고객이 경과 일수를 명시한 경우 그 수치를 사용하고 오늘 날짜를 새로 가정하지 않는다."
        },
        {
          "type": "input_text",
          "text": "상품 상태 정책: 단순 변심 반품은 상품을 사용하지 않았고 판매 가능한 상태로 유지한 경우를 기본 조건으로 한다. 미개봉 여부, 구성품 누락 여부, 고객 사용으로 인한 훼손 여부를 각각 확인한다. 포장을 열었다는 설명만으로 모든 상품의 반품을 일괄 거절하지 않으며 상품 종류와 실제 사용 여부가 필요하다고 안내한다. 위생상 재판매가 어려운 품목, 고객 요청으로 제작한 상품, 사용 흔적이 있는 상품은 추가 확인이 필요하다. 고객이 상품 종류를 알려주지 않으면 이러한 예외를 해당 고객에게 확정해서 적용하지 않는다. 구성품과 사은품이 있는 상품은 함께 반환하는 것이 원칙이며 누락 시 처리 조건 확인이 필요하다."
        },
        {
          "type": "input_text",
          "text": "배송비 정책: 단순 변심에 의한 반품의 반송 배송비는 고객이 부담한다. 상품 불량 또는 상점의 오배송으로 확인된 반품의 반송 배송비는 상점이 부담한다. 구체적인 원 단위 배송비는 주문과 택배 조건을 확인해야 하므로 정책에 없는 금액을 만들어내지 않는다. 처음 주문의 무료 배송 조건이 사라지는 부분 반품에는 최초 배송비의 재계산이 필요할 수 있으며 상세 주문 내역을 확인한다. 고객이 단순 변심이라고 명확히 말한 경우 불량 반품 규칙을 섞어서 설명하지 않는다. 고객이 기한과 상품 상태를 충족해도 배송비 부담 규칙은 별도로 적용한다. 담당자가 정한 별도 협의가 있다는 주장은 실제 확인 후 반영한다."
        },
        {
          "type": "input_text",
          "text": "환불 절차 정책: 반품 신청이 확인되면 회수 방법을 안내하고 상품이 상점에 도착한 뒤 상태를 검수한다. 검수가 완료된 후 원래 결제 수단으로 환불을 요청한다. 카드 승인 취소와 계좌 환불은 결제사나 금융기관의 처리 시간이 다를 수 있다. 고객에게 반품을 신청했다는 이유만으로 환불이 완료되었다고 안내하지 않는다. 환불 금액에는 실제 주문 할인, 쿠폰, 부분 반품, 배송비 조정 등의 조건을 확인해야 한다. 상담에서 결제 취소 버튼을 눌렀다거나 금융 거래가 끝났다고 주장하지 않는다. 고객이 환불 예정일을 물으면 회수, 검수, 결제사 반영 단계가 있다는 것을 설명하고 확인되지 않은 날짜를 확정하지 않는다."
        },
        {
          "type": "input_text",
          "text": "교환 정책: 교환은 반품 가능 기한과 상품 상태를 확인한 뒤 희망 상품의 재고를 확인한다. 사이즈나 색상 변경도 재고가 있어야 진행할 수 있다. 재고가 없을 경우 고객이 원하는 선택지를 확인하고 환불 또는 다른 상품 선택을 안내한다. 교환 상품과 원상품의 가격 차이는 별도 정산이 필요할 수 있으므로 같은 가격이라고 임의로 가정하지 않는다. 단순 변심 교환의 배송비는 고객 부담을 기본으로 안내한다. 상품 불량이나 오배송으로 확인된 교환은 상점 부담 규칙을 적용한다. 고객이 정책만 묻는 경우 교환을 이미 접수하거나 재고를 예약했다고 표현하지 않는다. 실제 신청에 필요한 주문 식별 정보는 별도 업무 절차에서 확인한다."
        },
        {
          "type": "input_text",
          "text": "대화 적용 예시: 배송 후 3일이 지났고 미사용 미개봉 상품을 단순 변심으로 반품하려는 고객에게는 일반 기한 조건을 충족한다고 안내하고 반송 배송비는 고객 부담이라고 설명한다. 배송 후 8일이 지났고 미개봉이라는 이유만으로 반품을 요청하면 미개봉 여부와 별개로 일반 단순 변심 기한이 지났다고 안내한다. 불량이라고 주장하는 고객에게는 사진이나 증상 등 확인 절차를 안내하고 불량이 확정되었다고 먼저 말하지 않는다. 답변은 고객이 묻는 핵심 조건부터 설명하고 불필요한 정책 전체를 반복하지 않는다. 이 고정 참고자료의 버전은 policy-v1이며 대화 중 원문을 재작성하거나 현재 시각을 삽입하지 않는다.",
          "prompt_cache_breakpoint": { "mode": "explicit" }
        }
      ]
    },
    { "role": "user", "content": "배송받은 지 8일 된 미개봉 상품인데, 단순 변심 반품이 가능해?" }
  ]
}
```

Explicit 경계는 일곱 번째 고정 content block의 끝이다.
이 경계까지의 공통 참고자료는 다른 질문에서도 재사용 대상으로 남는다.
일곱 content block의 `text`를 줄바꿈으로 연결해 `o200k_base`로 로컬 계산한 참고값은 1,277토큰이다.
이 값은 메시지 framing을 포함하지 않는 텍스트 계산값이며, 해당 모델의 실제 tokenizer나 API의 `usage` 값과 다를 수 있다.
`implicit` mode는 첫 user 메시지 끝에도 자동 경계를 선택할 수 있다.
그 경계는 다음 요청이 첫 질문까지 보존할 때 재사용 후보가 된다.

### 호출 1의 응답 Payload

다음 수치는 캐시를 처음 쓰는 상황을 설명하기 위한 가상 사용량이다.
이미 동일 prefix가 캐시에 있다면 첫 호출에서도 읽기가 발생할 수 있다.

```json
{
  "id": "resp_cache_01",
  "object": "response",
  "created_at": 1790812800,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_cache_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "미개봉이어도 배송 후 8일이 지났다면 일반적인 단순 변심 반품 기한인 7일을 초과합니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 1664,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 1600 },
    "output_tokens": 40,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 1704
  }
}
```

이 예제의 `cached_tokens: 0`은 읽은 캐시가 없다는 뜻이다.
`cache_write_tokens: 1600`은 설명용으로 이번 요청에서 캐시 쓰기에 분류한 입력 토큰 수이다.
JSON의 문자열 길이와 토큰 수를 동일하게 취급하지 않는다.

### 호출 2: 고정 Prefix와 이전 대화 보존

다음 JSON을 `cache-request-02.json`으로 저장한다.
실제 호출에서는 아래의 가상 assistant item을 호출 1에서 받은 실제 output으로 교체한다.

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @cache-request-02.json
```

요청 payload:

```json
{
  "model": "gpt-5.6-terra",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "prompt_cache_key": "sample-store:policy-v1:customer-demo",
  "prompt_cache_options": { "mode": "implicit", "ttl": "30m" },
  "input": [
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "이 대화는 가상 온라인 상점의 상담 예제이다. 한국어로 답하고 아래 고정 정책을 일관되게 적용한다. 고객이 설명한 조건과 정책에서 확인할 수 있는 내용을 구분한다. 실제 주문 조회, 반품 접수, 결제 취소를 수행했다고 말하지 않는다. 질문이 단순한 정책 확인이면 관련 조건과 결론을 간단히 설명한다. 필요한 조건이 빠지면 무엇을 확인해야 하는지 알려준다. 이전 대화에서 확인한 조건을 이어서 사용하되 고객이 새 조건을 제시하면 최신 조건을 적용한다. 정책에 없는 예외나 혜택을 만들어내지 않는다. 상담 답변과 실제 업무 처리 완료를 구분하고, 예상 처리 시간을 확정된 처리 완료 시간으로 표현하지 않는다."
        },
        {
          "type": "input_text",
          "text": "반품 기한 정책: 단순 변심에 의한 반품은 배송 완료일을 기준으로 7일 이내에 신청할 수 있다. 이 예제의 일수는 영업일이 아닌 달력 날짜의 차이로 계산한다. 배송 당일은 경과 0일이고 다음 날은 경과 1일이다. 경과 7일까지 신청 가능하고 경과 8일부터 일반적인 단순 변심 반품 기한이 지난 것으로 판단한다. 미개봉 상품이라도 기한 조건을 별도로 확인한다. 기한이 지났다는 이유만으로 불량 상품의 권리까지 동일하게 처리하지 않으며 불량은 별도 확인 절차를 안내한다. 날짜가 불명확하면 실제 배송 완료일과 신청일을 확인한다. 고객이 경과 일수를 명시한 경우 그 수치를 사용하고 오늘 날짜를 새로 가정하지 않는다."
        },
        {
          "type": "input_text",
          "text": "상품 상태 정책: 단순 변심 반품은 상품을 사용하지 않았고 판매 가능한 상태로 유지한 경우를 기본 조건으로 한다. 미개봉 여부, 구성품 누락 여부, 고객 사용으로 인한 훼손 여부를 각각 확인한다. 포장을 열었다는 설명만으로 모든 상품의 반품을 일괄 거절하지 않으며 상품 종류와 실제 사용 여부가 필요하다고 안내한다. 위생상 재판매가 어려운 품목, 고객 요청으로 제작한 상품, 사용 흔적이 있는 상품은 추가 확인이 필요하다. 고객이 상품 종류를 알려주지 않으면 이러한 예외를 해당 고객에게 확정해서 적용하지 않는다. 구성품과 사은품이 있는 상품은 함께 반환하는 것이 원칙이며 누락 시 처리 조건 확인이 필요하다."
        },
        {
          "type": "input_text",
          "text": "배송비 정책: 단순 변심에 의한 반품의 반송 배송비는 고객이 부담한다. 상품 불량 또는 상점의 오배송으로 확인된 반품의 반송 배송비는 상점이 부담한다. 구체적인 원 단위 배송비는 주문과 택배 조건을 확인해야 하므로 정책에 없는 금액을 만들어내지 않는다. 처음 주문의 무료 배송 조건이 사라지는 부분 반품에는 최초 배송비의 재계산이 필요할 수 있으며 상세 주문 내역을 확인한다. 고객이 단순 변심이라고 명확히 말한 경우 불량 반품 규칙을 섞어서 설명하지 않는다. 고객이 기한과 상품 상태를 충족해도 배송비 부담 규칙은 별도로 적용한다. 담당자가 정한 별도 협의가 있다는 주장은 실제 확인 후 반영한다."
        },
        {
          "type": "input_text",
          "text": "환불 절차 정책: 반품 신청이 확인되면 회수 방법을 안내하고 상품이 상점에 도착한 뒤 상태를 검수한다. 검수가 완료된 후 원래 결제 수단으로 환불을 요청한다. 카드 승인 취소와 계좌 환불은 결제사나 금융기관의 처리 시간이 다를 수 있다. 고객에게 반품을 신청했다는 이유만으로 환불이 완료되었다고 안내하지 않는다. 환불 금액에는 실제 주문 할인, 쿠폰, 부분 반품, 배송비 조정 등의 조건을 확인해야 한다. 상담에서 결제 취소 버튼을 눌렀다거나 금융 거래가 끝났다고 주장하지 않는다. 고객이 환불 예정일을 물으면 회수, 검수, 결제사 반영 단계가 있다는 것을 설명하고 확인되지 않은 날짜를 확정하지 않는다."
        },
        {
          "type": "input_text",
          "text": "교환 정책: 교환은 반품 가능 기한과 상품 상태를 확인한 뒤 희망 상품의 재고를 확인한다. 사이즈나 색상 변경도 재고가 있어야 진행할 수 있다. 재고가 없을 경우 고객이 원하는 선택지를 확인하고 환불 또는 다른 상품 선택을 안내한다. 교환 상품과 원상품의 가격 차이는 별도 정산이 필요할 수 있으므로 같은 가격이라고 임의로 가정하지 않는다. 단순 변심 교환의 배송비는 고객 부담을 기본으로 안내한다. 상품 불량이나 오배송으로 확인된 교환은 상점 부담 규칙을 적용한다. 고객이 정책만 묻는 경우 교환을 이미 접수하거나 재고를 예약했다고 표현하지 않는다. 실제 신청에 필요한 주문 식별 정보는 별도 업무 절차에서 확인한다."
        },
        {
          "type": "input_text",
          "text": "대화 적용 예시: 배송 후 3일이 지났고 미사용 미개봉 상품을 단순 변심으로 반품하려는 고객에게는 일반 기한 조건을 충족한다고 안내하고 반송 배송비는 고객 부담이라고 설명한다. 배송 후 8일이 지났고 미개봉이라는 이유만으로 반품을 요청하면 미개봉 여부와 별개로 일반 단순 변심 기한이 지났다고 안내한다. 불량이라고 주장하는 고객에게는 사진이나 증상 등 확인 절차를 안내하고 불량이 확정되었다고 먼저 말하지 않는다. 답변은 고객이 묻는 핵심 조건부터 설명하고 불필요한 정책 전체를 반복하지 않는다. 이 고정 참고자료의 버전은 policy-v1이며 대화 중 원문을 재작성하거나 현재 시각을 삽입하지 않는다.",
          "prompt_cache_breakpoint": { "mode": "explicit" }
        }
      ]
    },
    { "role": "user", "content": "배송받은 지 8일 된 미개봉 상품인데, 단순 변심 반품이 가능해?" },
    {
      "id": "msg_cache_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "미개봉이어도 배송 후 8일이 지났다면 일반적인 단순 변심 반품 기한인 7일을 초과합니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "다른 상품은 배송받은 지 3일이고 미사용 미개봉이야. 단순 변심 반품의 반송 배송비는 누가 부담해?" }
  ]
}
```

첫 요청의 developer message와 첫 질문은 그대로 유지했다.
첫 응답과 새 질문만 뒤에 추가했으므로 기존 prefix가 유지된다.
두 번째 질문은 다른 상품의 새 조건을 명시하므로 첫 질문의 8일 조건과 혼동하지 않는다.

### 호출 2의 응답 Payload

다음은 이전 prefix 일부를 읽고 새 구간을 쓰는 경우의 가상 응답이다.

```json
{
  "id": "resp_cache_02",
  "object": "response",
  "created_at": 1790812810,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_cache_02",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "배송 후 3일인 미사용 미개봉 상품은 일반 반품 조건을 충족하며, 단순 변심 반품의 반송 배송비는 고객이 부담합니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 1824,
    "input_tokens_details": { "cached_tokens": 1600, "cache_write_tokens": 160 },
    "output_tokens": 48,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 1872
  }
}
```

`input_tokens`에는 캐시 읽기·쓰기·일반 입력 토큰이 모두 포함된다.
`cached_tokens`를 입력 토큰에 다시 더하지 않는다.
이 가상 응답의 일반 입력은 `1824 - 1600 - 160 = 64`토큰이다.
세 번째 질문도 같은 설정과 prefix를 유지하고 두 번째 output 뒤에 새 user item을 추가한다.
5회 전체 이력 관리 방식은 [5회 대화 문서](openai-llm-api-five-turn-qa.md)에 나와 있다.

## 같은 Payload를 Explicit-only로 바꾸는 예

위 요청의 다른 내용과 developer breakpoint는 유지하고 다음 최상위 설정으로 교체한다.
아래 JSON은 완전한 생성 요청이 아닌 교체할 설정 부분이다.

```json
{
  "prompt_cache_options": { "mode": "explicit", "ttl": "30m" }
}
```

이 구성은 고정 developer 참고자료 끝에 있는 경계만 사용한다.
이전 질문·답변은 context에 포함되지만, 그 부분까지 쓰는 자동 경계는 없다.
대화 이력의 재사용이 많으면 implicit과 explicit 경계의 조합을 검토한다.
각 요청의 뒤쪽 내용이 서로 독립적이면 explicit-only로 고정 prefix만 쓰는 구성이 불필요한 쓰기를 줄일 수 있다.

## Tool 결과까지 재사용하는 예

Supported model의 function_call_output은 문자열 대신 content 배열로 보낼 수 있다.
다음은 이전 function_call의 결과 item에 explicit 경계를 붙이는 형태이다.
완전한 요청을 만들 때에는 해당 function_call과 원래 이력도 함께 보존한다.

```json
{
  "type": "function_call_output",
  "call_id": "call_policy_01",
  "output": [
    {
      "type": "input_text",
      "text": "정책 조회 결과: 단순 변심 반품 기한은 배송 후 7일이며 반송 배송비는 고객 부담입니다.",
      "prompt_cache_breakpoint": { "mode": "explicit" }
    }
  ]
}
```

도구 결과가 긴 공통 prefix의 끝에 있으면 이 경계를 대화 분기에서도 보존할 수 있다.
짧은 결과 한 문장 자체가 1,024 토큰을 넘을 필요는 없으며 경계 앞 전체 prefix의 길이가 기준이다.
캐시를 위해 결과 내용을 변형하지 않고 실제 실행 결과를 보존한다.

## Cache hit를 떨어뜨리는 변경

| 변경 | 영향 | 개선 |
| --- | --- | --- |
| 고정 developer 지침 첫 줄의 현재 시각을 매번 변경 | 앞부분부터 prefix가 달라짐 | 필요한 시각을 새 메시지의 뒤쪽에 전달 |
| 이전 assistant 답변을 매번 요약해서 덮어씀 | 요약 시작 구간 이후 일치하지 않을 수 있음 | 필요할 때만 compaction하고 새 prefix를 이후 요청에 재사용 |
| 도구 정의의 순서·설명을 매번 재생성 | 렌더링된 도구 prefix 변경 | 안정적인 정의와 순서 유지 |
| 필요 없는 tools를 삭제 | 공통 도구 prefix 변경 가능 | `tool_choice: "none"` 또는 allowed_tools로 호출 제한 |
| 긴 reference는 같지만 저장된 경계보다 앞에서 질문 변경 | 공통 부분 끝에 경계가 없으면 hit가 안 날 수 있음 | reference 끝에 explicit 경계 설정 |
| Explicit-only인데 breakpoint 없음 | 캐시 읽기·쓰기 없음 | 지원 content block에 경계 지정 |
| 같은 user 메시지 뒤에 질문을 덧붙임 | 이전 implicit 메시지 끝 경계가 사라짐 | 새 user 메시지를 추가 |
| 같은 key만 지정하고 내용은 매번 변경 | key는 prefix 일치를 대신하지 못함 | 같은 렌더링 prefix 유지 |

고정 참고자료를 바꿔야 하는 정책 변경은 정확성을 우선한다.
새 버전의 prefix로 전환하고 캐시가 다시 만들어지는 비용을 측정한다.
캐시 비율을 높이기 위해 불필요한 텍스트를 무조건 늘리지 않고 유용한 자료·토큰 수·실제 비용을 함께 평가한다.

## 사용량과 비용 측정

Responses에서 다음 값을 기록한다.

- `usage.input_tokens`
- `usage.input_tokens_details.cached_tokens`
- `usage.input_tokens_details.cache_write_tokens`
- `usage.output_tokens`
- 첫 토큰까지의 시간과 전체 응답 시간
- 모델, 정책 버전, 캐시 key, 요청 오류·재시도 여부

Token cache-hit rate는 여러 요청의 `cached_tokens` 합을 `input_tokens` 합으로 나눈다.
요청별 비율을 단순 평균하면 서로 다른 길이의 요청을 제대로 비교하지 못한다.
Chat Completions의 대응 경로는 `usage.prompt_tokens`와 `usage.prompt_tokens_details`이다.

```text
I = input_tokens
R = cached_tokens
W = cache_write_tokens
U = I - R - W

일반 입력 단가가 P이고 cache-read 배율이 r, cache-write 배율이 w이면:
입력 비용 = (U + r × R + w × W) × P / 1,000,000
```

위 가상 수치에 `gpt-5.6-terra`의 읽기 0.1배, 쓰기 1.25배를 적용하면 다음과 같다.

| 호출 | 전체 입력 I | 읽기 R | 쓰기 W | 일반 입력 U | 일반 입력 단가로 환산한 토큰 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1,664 | 0 | 1,600 | 64 | 2,064 |
| 2 | 1,824 | 1,600 | 160 | 64 | 424 |
| 합계 | 3,488 | 1,600 | 1,760 | 128 | 2,488 |

이 예제의 token cache-hit rate는 `1600 / 3488 ≈ 45.9%`이다.
입력 비용은 cache가 전혀 없을 때의 3,488 토큰 대비 2,488 토큰에 해당하는 일반 입력 비용이다.
출력 비용과 다른 도구 요금은 별도로 더한다.
Cache-write 비용은 일반 입력 요금에 덧붙이는 추가 fee가 아니라 해당 쓰기 토큰에 적용되는 단가이다.
실제 가격과 지원 정책은 [API pricing](https://developers.openai.com/api/docs/pricing)에서 다시 확인한다.

## 실측할 때의 확인 순서

1. 같은 모델·설정으로 고정 prefix 길이를 확인하고 1,024 visible token 조건을 만족하는지 확인한다.
2. 재사용하려는 content 끝에 유효한 breakpoint가 있는지 확인한다.
3. 첫 요청 후 실제 output item을 보존해 후속 요청에 추가한다.
4. 같은 key를 사용하는 관련 요청과 캐시 TTL을 확인한다.
5. 후속 응답의 cached_tokens와 cache_write_tokens, 전체 입력 비용을 함께 비교한다.
6. 캐시가 0이면 prefix 변경·경계·모델·TTL·라우팅을 조사하고 짧은 간격으로 무한 재시도하지 않는다.

이 문서의 예제 payload가 캐시 hit를 보장하지는 않는다.
문서 작성 과정에서 유료 OpenAI API를 호출하거나 실제 cache hit를 측정하지 않았다.
`store: false`에서도 prompt caching을 사용할 수 있으며 해당 값은 캐시 사용 여부를 판단하는 지표가 아니다.

## 공식 참고 문서

- [Prompt caching: 전체 규칙과 모델별 차이](https://developers.openai.com/api/docs/guides/prompt-caching)
- [GPT-5.6 이후의 caching](https://developers.openai.com/api/docs/guides/prompt-caching#how-caching-works-gpt-5-6-and-later)
- [이력 보존](https://developers.openai.com/api/docs/guides/prompt-caching#preserve-conversation-history)
- [Cache 경계와 implicit·explicit mode](https://developers.openai.com/api/docs/guides/prompt-caching#choose-a-caching-mode)
- [사용량과 비용 측정](https://developers.openai.com/api/docs/guides/prompt-caching#monitor-cache-performance)
- [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)
- [GPT-5.6 Terra의 지원 기능과 요금](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [공통 프로토콜 문서](openai-llm-api-protocol.md)
