# OpenAI LLM API 예제 2: 5회 질의와 응답

이 문서는 질문과 답변을 다섯 번 주고받을 때의 API call과 전체 요청 payload를 설명한다.
공식 문서 확인 기준일은 2026-10-01이다.
Responses API를 다섯 번 호출하고, 애플리케이션이 대화 이력을 직접 관리한다.

## 전제와 대화 내용

모델은 `gpt-5.6-terra`이고 매 요청에 `store: false`, `stream: false`, `reasoning.effort: "none"`을 지정한다.
매번 같은 `instructions`를 보내고, `input`에는 이전 질문과 모델의 output item을 순서대로 유지한다.
예제 응답은 주요 필드를 발췌한 가상 데이터이며 실제 실행 결과가 아니다.
ID·시각·토큰 수와 실제 문구는 호출마다 달라진다.
실제 구현에서는 문서의 가상 답변 대신 직전 API 응답의 output을 사용한다.

| 회차 | 사용자 질의 | 예제 응답 | 해당 요청의 input item 수 |
| --- | --- | --- | ---: |
| 1 | 2 더하기 3은? | 2 더하기 3은 5입니다. | 1 |
| 2 | 그 결과에 4를 곱하면? | 5에 4를 곱하면 20입니다. | 3 |
| 3 | 거기서 6을 빼면? | 20에서 6을 빼면 14입니다. | 5 |
| 4 | 그 값을 2로 나누면? | 14를 2로 나누면 7입니다. | 7 |
| 5 | 처음부터 계산 과정을 한 문장으로 정리해줘. | 전체 계산 과정 요약 | 9 |

5회 대화는 API 요청 5개와 API 응답 5개이다.
한 번의 요청에 질문 5개를 미리 넣는 방식과 구분한다.
다섯 번째 응답을 이력에 반영하면 user·assistant item은 총 10개가 된다.

## 공통 API Call

모든 회차는 동일한 endpoint와 헤더를 사용한다.
아래 각 회차의 요청 JSON을 표시된 파일명으로 저장하고 해당 curl 명령을 실행한다.
응답은 JSON으로 받으며, 다음 요청을 만들기 전에 `status`와 output item을 확인한다.
명령 실행에는 유효한 서버 환경변수 `OPENAI_API_KEY`가 필요하다.

```http
POST /v1/responses HTTP/1.1
Host: api.openai.com
Authorization: Bearer <OPENAI_API_KEY>
Content-Type: application/json
Accept: application/json
```

각 호출에서 `input`이 실제 모델 context이다.
같은 API key로 호출하거나 같은 `metadata`를 보내는 것만으로 이전 대화가 자동 복원되지 않는다.

## 1회차: 첫 질문

### API Call과 요청 Payload

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @request-01.json
```

`request-01.json`:

```json
{
  "model": "gpt-5.6-terra",
  "instructions": "한국어로 한 문장으로 답하고, 이전 계산 결과를 이어서 사용하세요.",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "input": [
    { "role": "user", "content": "2 더하기 3은?" }
  ]
}
```

### 응답 Payload

```json
{
  "id": "resp_turn_01",
  "object": "response",
  "created_at": 1790812800,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_turn_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "2 더하기 3은 5입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 45,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "output_tokens": 12,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 57
  }
}
```

`resp_turn_01`은 Response 객체 ID이고 `msg_turn_01`은 output message ID이다.
다음 요청에는 첫 질문과 이 `output` message를 보존하고 새 질문을 추가한다.

## 2회차: 이전 결과에 4 곱하기

### API Call과 요청 Payload

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @request-02.json
```

`request-02.json`:

```json
{
  "model": "gpt-5.6-terra",
  "instructions": "한국어로 한 문장으로 답하고, 이전 계산 결과를 이어서 사용하세요.",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "input": [
    { "role": "user", "content": "2 더하기 3은?" },
    {
      "id": "msg_turn_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "2 더하기 3은 5입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "그 결과에 4를 곱하면?" }
  ]
}
```

### 응답 Payload

```json
{
  "id": "resp_turn_02",
  "object": "response",
  "created_at": 1790812810,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_turn_02",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "5에 4를 곱하면 20입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 79,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "output_tokens": 14,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 93
  }
}
```

모델은 두 번째 질문의 `그 결과`를 첫 번째 답변의 5와 연결한다.
두 번째 질문만 보내면 이 연결에 필요한 context가 빠진다.

## 3회차: 이전 결과에서 6 빼기

### API Call과 요청 Payload

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @request-03.json
```

`request-03.json`:

```json
{
  "model": "gpt-5.6-terra",
  "instructions": "한국어로 한 문장으로 답하고, 이전 계산 결과를 이어서 사용하세요.",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "input": [
    { "role": "user", "content": "2 더하기 3은?" },
    {
      "id": "msg_turn_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "2 더하기 3은 5입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "그 결과에 4를 곱하면?" },
    {
      "id": "msg_turn_02",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "5에 4를 곱하면 20입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "거기서 6을 빼면?" }
  ]
}
```

### 응답 Payload

```json
{
  "id": "resp_turn_03",
  "object": "response",
  "created_at": 1790812820,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_turn_03",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "20에서 6을 빼면 14입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 113,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "output_tokens": 14,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 127
  }
}
```

## 4회차: 이전 결과를 2로 나누기

### API Call과 요청 Payload

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @request-04.json
```

`request-04.json`:

```json
{
  "model": "gpt-5.6-terra",
  "instructions": "한국어로 한 문장으로 답하고, 이전 계산 결과를 이어서 사용하세요.",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "input": [
    { "role": "user", "content": "2 더하기 3은?" },
    {
      "id": "msg_turn_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "2 더하기 3은 5입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "그 결과에 4를 곱하면?" },
    {
      "id": "msg_turn_02",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "5에 4를 곱하면 20입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "거기서 6을 빼면?" },
    {
      "id": "msg_turn_03",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "20에서 6을 빼면 14입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "그 값을 2로 나누면?" }
  ]
}
```

### 응답 Payload

```json
{
  "id": "resp_turn_04",
  "object": "response",
  "created_at": 1790812830,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_turn_04",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "14를 2로 나누면 7입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 148,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "output_tokens": 14,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 162
  }
}
```

## 5회차: 전체 계산 과정 요약

### API Call과 요청 Payload

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @request-05.json
```

`request-05.json`:

```json
{
  "model": "gpt-5.6-terra",
  "instructions": "한국어로 한 문장으로 답하고, 이전 계산 결과를 이어서 사용하세요.",
  "reasoning": { "effort": "none" },
  "max_output_tokens": 256,
  "store": false,
  "stream": false,
  "input": [
    { "role": "user", "content": "2 더하기 3은?" },
    {
      "id": "msg_turn_01",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "2 더하기 3은 5입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "그 결과에 4를 곱하면?" },
    {
      "id": "msg_turn_02",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "5에 4를 곱하면 20입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "거기서 6을 빼면?" },
    {
      "id": "msg_turn_03",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "20에서 6을 빼면 14입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "그 값을 2로 나누면?" },
    {
      "id": "msg_turn_04",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "14를 2로 나누면 7입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    },
    { "role": "user", "content": "처음부터 계산 과정을 한 문장으로 정리해줘." }
  ]
}
```

### 응답 Payload

```json
{
  "id": "resp_turn_05",
  "object": "response",
  "created_at": 1790812840,
  "status": "completed",
  "model": "gpt-5.6-terra",
  "error": null,
  "incomplete_details": null,
  "output": [
    {
      "id": "msg_turn_05",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "2에 3을 더해 5를 얻고, 4를 곱해 20으로 만든 뒤, 6을 빼서 14를 얻고 2로 나누면 7입니다.",
          "annotations": [],
          "logprobs": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 191,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "output_tokens": 45,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 236
  }
}
```

## 이력을 구성하는 규칙

요청 N의 `input`은 요청 N-1의 `input`, 응답 N-1의 재전달 가능한 `output` item, 새 user item을 순서대로 연결한 것이다.
최상위 Response 객체 전체를 `input`에 넣지 않는다.
Response의 `usage`, `created_at` 등은 대화 item이 아니다.

```text
요청 1: [U1]
요청 2: [U1, A1, U2]
요청 3: [U1, A1, U2, A2, U3]
요청 4: [U1, A1, U2, A2, U3, A3, U4]
요청 5: [U1, A1, U2, A2, U3, A3, U4, A4, U5]
완료 이력: [U1, A1, U2, A2, U3, A3, U4, A4, U5, A5]
```

이 예제에서는 reasoning을 끄고 텍스트 message 하나만 반환된 것으로 가정한다.
다른 설정에서 `reasoning`이나 tool item이 반환되면 관련 output 전체를 보존한다.
Assistant `phase`가 반환되는 모델에서는 그 값도 유지한다.
공식 SDK는 output을 다음 input 형식으로 변환하는 기능을 제공할 수 있으므로 SDK별 방법을 따른다.

## 사용량과 캐시의 관계

매 요청은 전달된 전체 context를 기준으로 입력 토큰을 계산한다.
이전 질문과 답변을 다시 보낸다고 해서 해당 토큰이 자동으로 무료가 되는 것은 아니다.
예제의 가상 입력 토큰 합계는 `45 + 79 + 113 + 148 + 191 = 576`이다.
모든 캐시 수치를 0으로 둔 이유는 이 예제가 짧은 대화 구조를 보여 주기 때문이다.

이처럼 기존 이력을 바꾸지 않고 뒤에 새 item을 추가하면 공통 prefix를 유지하기 쉽다.
실제 캐시 읽기는 모델의 최소 길이, 유효한 캐시 경계, TTL, 라우팅 등의 조건을 만족해야 한다.
긴 대화에서는 context window와 전체 비용도 확인하고, 필요할 때 요약·compaction을 적용한다.
캐시 최적화의 구체적인 규칙은 [프롬프트 캐시 예제](openai-llm-api-prompt-caching.md)를 참조한다.

## 다른 대화 연결 방식

서버에서 상태를 관리하려면 저장된 Response의 `previous_response_id` 또는 Conversations API의 `conversation`을 사용할 수 있다.
이 경우에도 필요한 최상위 `instructions`와 현재 요청의 설정을 관리해야 한다.
단순히 요청 JSON이 작아졌다고 해서 모델에 사용되는 context나 입력 과금까지 줄어든다고 해석하지 않는다.
HTTP의 `store: false` 예제에 가상 Response ID만 붙여 서버 대화 연결 예제로 바꾸지 않는다.

## 공식 참고 문서

- [Responses API create](https://developers.openai.com/api/reference/resources/responses/methods/create)
- [Conversation state: 수동 이력과 서버 대화 연결](https://developers.openai.com/api/docs/guides/conversation-state)
- [Responses 전환: instructions와 output item 재사용](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
- [공통 프로토콜 문서](openai-llm-api-protocol.md)
