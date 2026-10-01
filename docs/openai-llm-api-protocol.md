# OpenAI LLM API: Protocol과 Payload 구조

이 문서는 OpenAI LLM API를 HTTP로 호출할 때의 전송 방식과 요청·응답 JSON 구조를 설명한다.
공식 문서 확인 기준일은 2026-10-01이다.
OpenAI는 새 프로젝트에 Responses API를 권장하며, Chat Completions API도 지원한다.

## 문서 구성과 범위

| 문서 | 내용 |
| --- | --- |
| [간단한 질의와 응답](openai-llm-api-simple-qa.md) | 한 번의 HTTP 요청, 요청 본문, 응답 본문과 필드 해석 |
| [5회 질의와 응답](openai-llm-api-five-turn-qa.md) | 다섯 번의 호출에 전달되는 전체 대화 이력과 응답 |
| [Tool call을 포함하는 응답](openai-llm-api-tool-call.md) | 함수 정의, 호출 요청, 애플리케이션 실행, 결과 전달, 최종 응답 |
| [여러 차례 대화와 프롬프트 캐시](openai-llm-api-prompt-caching.md) | Prefix 유지 규칙, 캐시 경계, 요청 예제와 사용량 해석 |

상세 예제는 `POST /v1/responses`와 `gpt-5.6-terra`를 사용한다.
이 모델은 Responses, Chat Completions, function calling, prompt caching을 지원한다.
필드 지원 여부와 허용값은 사용하는 모델과 API에 따라 확인해야 한다.
예제 응답은 구조를 설명하기 위한 가상 데이터이며 실제 API 실행 결과가 아니다.
응답의 일부 선택 필드는 생략했고, ID·토큰 수·생성 문구는 실제 호출마다 달라진다.

이 문서에서 protocol은 HTTPS, 인증, HTTP 메서드, 응답 형식과 스트리밍 규약을 뜻한다.
Payload는 그 위에 전달되는 요청·응답 본문을 뜻한다.
Realtime, 파일 업로드, 음성 전용 API의 전체 스키마는 각각의 공식 문서를 참조한다.

## 공통 HTTP Protocol

### Endpoint와 인증

| 항목 | 값 또는 규칙 |
| --- | --- |
| Base URL | `https://api.openai.com/v1` |
| Responses 생성 | `POST /responses` |
| Chat Completions 생성 | `POST /chat/completions` |
| 전송 | HTTPS |
| 요청 본문 | UTF-8 JSON |
| 인증 | `Authorization: Bearer <API_KEY_OR_ACCESS_TOKEN>` |
| 요청 Content-Type | `application/json` |
| 일반 응답 Content-Type | `application/json` |
| HTTP 스트리밍 응답 Content-Type | `text/event-stream` |

`OpenAI-Organization`과 `OpenAI-Project`는 여러 조직에 속해 있거나 legacy user API key로 특정 프로젝트에 접근할 때 사용할 수 있다.
API key는 서버 환경변수나 키 관리 시스템에서 읽는다.
문서의 `OPENAI_API_KEY`는 환경변수 이름이며 실제 키 값을 의미하지 않는다.

HTTP/1.1 표기 예시는 다음과 같다.
실제 전송은 HTTP/2 등 다른 HTTP 버전을 사용할 수 있다.

```http
POST /v1/responses HTTP/1.1
Host: api.openai.com
Authorization: Bearer <OPENAI_API_KEY>
Content-Type: application/json
Accept: application/json
X-Client-Request-Id: 123e4567-e89b-12d3-a456-426614174000

{"model":"gpt-5.6-terra","input":"안녕하세요.","reasoning":{"effort":"none"},"store":false}
```

### 추적과 응답 헤더

| 헤더 | 의미 |
| --- | --- |
| `x-request-id` | 서버가 발급한 HTTP 요청 식별자 |
| `X-Client-Request-Id` | 클라이언트가 선택적으로 보내는 자체 요청 식별자 |
| `openai-processing-ms` | 서버 처리 시간 |
| `x-ratelimit-limit-requests` / `x-ratelimit-remaining-requests` | 요청 수 제한과 잔여량 |
| `x-ratelimit-limit-tokens` / `x-ratelimit-remaining-tokens` | 토큰 제한과 잔여량 |
| `x-ratelimit-reset-requests` / `x-ratelimit-reset-tokens` | 제한이 초기화되는 데 필요한 시간 |

`X-Client-Request-Id`는 요청마다 고유한 ASCII 문자열로 지정하며 최대 512자이다.
추적 ID는 재시도 시 중복 실행을 방지하는 idempotency key로 해석하지 않는다.
응답 JSON의 `id`는 모델 Response 객체의 ID이고, HTTP 헤더의 `x-request-id`와 별개이다.
응답 헤더는 상황에 따라 일부만 제공될 수 있다.

## Responses API Payload

### 요청 구조

아래 표는 일반적인 직접 모델 호출에 쓰는 필드를 정리한다.
전체 union 타입과 추가 필드는 [Responses create reference](https://developers.openai.com/api/reference/resources/responses/methods/create)에서 확인한다.

| 필드 | 일반적인 타입 | 의미 |
| --- | --- | --- |
| `model` | string | 호출할 모델 ID |
| `input` | string 또는 item 배열 | 현재 질문, 대화 이력, 함수 실행 결과 등 |
| `instructions` | string | 현재 요청의 developer/system 지침 |
| `max_output_tokens` | integer | 생성 토큰 상한이며 reasoning 토큰도 포함 |
| `reasoning` | object | `effort` 등 모델별 reasoning 설정 |
| `text` | object | 출력 형식과 상세도 설정 |
| `tools` | 배열 | 함수와 지원되는 내장 도구 정의 |
| `tool_choice` | string 또는 object | 도구 호출 허용·필수·특정 함수 지정 |
| `parallel_tool_calls` | boolean | 여러 함수 호출 허용 여부 |
| `previous_response_id` | string 또는 null | 이전 Response를 이용한 대화 연결 |
| `conversation` | string 또는 object | Conversations API의 지속적인 대화 객체 |
| `store` | boolean | Response 저장 여부 |
| `stream` | boolean | HTTP SSE 스트리밍 여부 |
| `background` | boolean | 지원되는 모델에서 백그라운드 처리 |
| `prompt_cache_options` | object | 지원 모델의 캐시 mode·TTL 등 |
| `prompt_cache_key` | string | 모델 세대에 따른 캐시 라우팅 또는 회계 분리 |
| `metadata` | object | 애플리케이션에서 사용하는 부가 식별 정보 |

`input` 배열은 메시지만 담는 배열이 아니다.
메시지, 도구 호출, 도구 실행 결과 등 서로 다른 item을 `type`으로 구분한다.

| Item / content type | 대표 필드 | 의미 |
| --- | --- | --- |
| `message` | `role`, `content` | user·assistant·developer·system 메시지 |
| `input_text` | `text` | 입력 메시지의 텍스트 content part |
| `input_image` | `image_url` 또는 `file_id`, `detail` | 이미지 입력 |
| `input_file` | `file_id` 또는 `file_url` 또는 `file_data` | 파일 입력 |
| `function_call` | `name`, `arguments`, `call_id` | 모델이 요청한 함수 호출 |
| `function_call_output` | `call_id`, `output` | 애플리케이션이 전달하는 함수 실행 결과 |
| `reasoning` | 모델별 reasoning 관련 필드 | 이전 모델 출력에 포함될 수 있는 reasoning item |

Item과 메시지 내부 content part는 서로 다른 계층이다.
예를 들어 이미지 입력은 `input[]`의 user 메시지 안에 있는 `content[]`에 들어간다.

```json
{
  "model": "gpt-5.6-terra",
  "reasoning": { "effort": "none" },
  "store": false,
  "input": [
    {
      "role": "user",
      "content": [
        { "type": "input_text", "text": "이 이미지의 내용을 설명해줘." },
        {
          "type": "input_image",
          "image_url": "https://example.com/sample.png",
          "detail": "auto"
        }
      ]
    }
  ]
}
```

`example.com`의 이미지 URL은 교체가 필요한 예시 URL이다.
이미지는 지원되는 외부 URL, base64 data URL 또는 업로드된 `file_id`로 제공할 수 있다.
파일 업로드는 별도의 Files API를 사용하며 업로드 자체의 본문은 multipart 형식이다.

### 응답 구조

| 필드 | 의미 |
| --- | --- |
| `id` | Response 객체 ID |
| `object` | `response` |
| `created_at` | 생성 시각의 Unix timestamp, 초 단위 |
| `model` | 실제 사용된 모델 |
| `status` | `completed`, `incomplete`, `failed`, `in_progress`, `queued`, `cancelled` 등 |
| `output` | 타입이 지정된 출력 item 배열 |
| `error` | Response 생성 실패의 상세 오류 또는 null |
| `incomplete_details` | 생성이 끝까지 완료되지 못한 이유 또는 null |
| `usage.input_tokens` | 전체 입력 토큰 수 |
| `usage.input_tokens_details.cached_tokens` | 입력 중 캐시에서 읽은 토큰 수 |
| `usage.input_tokens_details.cache_write_tokens` | 지원 모델에서 캐시에 쓴 입력 토큰 수 |
| `usage.output_tokens` | 출력 토큰 수이며 reasoning 토큰을 포함 |
| `usage.output_tokens_details.reasoning_tokens` | 출력 토큰 중 reasoning에 사용된 수 |
| `usage.total_tokens` | 입력 토큰과 출력 토큰의 합 |

`output[]`에는 `message`, `function_call`, `reasoning`, 내장 도구 관련 item 등이 함께 올 수 있다.
텍스트 메시지는 `type: "message"`인 item의 `content[]`에서 `type: "output_text"`인 부분을 읽는다.
`output[0]`이 항상 최종 텍스트라고 가정하면 안 된다.
거절 응답은 `refusal` content part 등으로 표현되므로 별도로 처리한다.

일부 공식 SDK의 `response.output_text`는 텍스트를 모아 주는 편의 속성이다.
Raw HTTP JSON의 최상위에 항상 `output_text`가 온다고 가정하지 않는다.
또한 사용자에게 보여줄 텍스트만 보관하면 다음 호출에 필요한 tool·reasoning item이나 assistant `phase`가 사라질 수 있다.

### 대화 상태와 저장

Responses에서 여러 차례 대화를 이어가는 방식은 세 가지이다.

1. 클라이언트가 이전 입력과 모든 필요한 output item을 다음 `input`에 포함한다.
2. `previous_response_id`로 이전 Response를 참조한다.
3. Conversations API의 `conversation`을 사용한다.

`conversation`과 `previous_response_id`는 한 요청에서 함께 사용하지 않는다.
`previous_response_id`를 사용해도 이전 요청의 최상위 `instructions`는 다음 요청에 자동으로 이어지지 않으므로 필요한 지침을 다시 보낸다.
대화 연결은 입력 토큰의 과금이나 context window 제한을 없애지 않는다.

상세 예제의 기본 방식은 `store: false`와 클라이언트의 전체 이력 관리이다.
`store: false`는 Response 저장 설정이며 prompt cache를 끄는 설정이 아니다.
HTTP에서 저장하지 않은 Response ID만으로 다음 요청의 전체 대화 상태가 복원된다고 가정하지 않는다.
WebSocket에는 연결 안의 메모리 상태를 재사용하는 별도 동작이 있다.

## Chat Completions API와의 차이

| 개념 | Responses | Chat Completions |
| --- | --- | --- |
| Endpoint | `/v1/responses` | `/v1/chat/completions` |
| 입력 | `input` string 또는 item 배열 | `messages` 배열 |
| 지침 | `instructions` 또는 developer/system message | developer/system message |
| 텍스트 입력 content type | `input_text` | `text` |
| 이미지 content type | `input_image` | `image_url` |
| 응답 | `output` item 배열 | `choices` 배열 |
| 텍스트 위치 | `output[].content[].text` | `choices[].message.content` |
| 함수 정의 | `tools[].name`, `parameters` | `tools[].function.name`, `parameters` |
| 함수 호출 | `function_call` item | assistant의 `tool_calls[]` |
| 함수 결과 | `function_call_output`와 `call_id` | `role: "tool"`과 `tool_call_id` |
| 출력 토큰 상한 | `max_output_tokens` | `max_completion_tokens` |
| Structured Outputs | `text.format` | `response_format` |
| Reasoning effort | `reasoning.effort` | `reasoning_effort` |
| 대화 연결 | 수동 이력, 이전 Response, Conversation | 클라이언트가 매번 messages 이력 전송 |
| HTTP 스트리밍 | 타입별 `response.*` event | `chat.completion.chunk`와 `choices[].delta` |

Chat Completions의 `max_tokens`, `functions`, `function_call`은 이전 형식이며 각각 최신 대응 필드를 확인한다.
동일한 모델 이름이 두 API에 있어도 도구 호출과 reasoning 설정의 지원 범위가 같다고 가정하지 않는다.

Structured Outputs에서 JSON Schema를 지정해도 HTTP 응답의 외부 envelope는 그대로이다.
모델이 생성한 JSON은 텍스트 필드 안에 들어가며 애플리케이션은 그 문자열을 JSON으로 한 번 더 파싱한다.
Schema 준수와 함께 거절·미완료 상태도 처리해야 한다.

## 스트리밍 Protocol

### HTTP SSE

`stream: true`를 설정하면 서버는 한 개의 큰 JSON 대신 SSE event를 순서대로 보낸다.
각 event는 빈 줄로 구분되며 `data:` 뒤에 JSON이 들어간다.
TCP/HTTP chunk 경계와 SSE event 경계는 같지 않다.
UTF-8 디코딩, 여러 `data:` 줄과 event framing을 처리하는 SSE parser가 필요하다.

Responses의 주요 event는 다음과 같다.

| Event | 의미 |
| --- | --- |
| `response.created` / `response.in_progress` | Response 생성과 처리 시작 |
| `response.output_item.added` / `.done` | 출력 item 추가와 완료 |
| `response.output_text.delta` / `.done` | 텍스트 조각과 해당 텍스트의 완료 |
| `response.function_call_arguments.delta` / `.done` | 함수 arguments 문자열 조각과 완료 |
| `response.completed` | Response의 정상 완료 |
| `response.incomplete` / `response.failed` | 미완료 또는 실패 |
| `error` | 스트림의 오류 |

아래는 중간 event와 일부 필드를 생략한 전송 예시이다.

```text
event: response.output_text.delta
data: {"type":"response.output_text.delta","sequence_number":4,"item_id":"msg_example","output_index":0,"content_index":0,"delta":"안녕"}

event: response.output_text.delta
data: {"type":"response.output_text.delta","sequence_number":5,"item_id":"msg_example","output_index":0,"content_index":0,"delta":"하세요."}

event: response.completed
data: {"type":"response.completed","sequence_number":9,"response":{"id":"resp_example","status":"completed"}}
```

텍스트는 item·content index별로 누적하고, 함수 arguments도 해당 호출별로 누적한다.
Arguments는 스트림 종료 전에 유효한 JSON이 아닐 수 있으므로 완료된 뒤 파싱·검증한다.
`response.output_text.done`은 특정 텍스트 part의 완료이며 전체 Response의 성공을 의미하지 않는다.
HTTP 200 이후에도 스트림 내부에서 실패할 수 있으므로 최종 상태를 확인한다.

Chat Completions 스트림은 `choices[].message` 대신 `choices[].delta`를 사용하고 `data: [DONE]`으로 끝난다.
`stream_options.include_usage: true`이면 `[DONE]` 전에 `choices: []`와 전체 `usage`를 담은 chunk가 추가될 수 있다.
연결이 중단되면 최종 usage를 받지 못할 수 있다.
Responses의 완료 판단에 Chat Completions의 `[DONE]` 규칙을 그대로 적용하지 않는다.

### Responses WebSocket와 Realtime

Responses는 `wss://api.openai.com/v1/responses`로 연결하는 WebSocket 모드도 지원한다.
클라이언트는 JSON `response.create` event를 보내며 본문은 HTTP Responses 요청과 비슷하다.
WebSocket에서는 `stream`, `background` 같은 HTTP 전용 설정을 사용하지 않는다.
`stream_id`와 연결 안의 이전 Response 상태 재사용은 WebSocket 고유 기능이다.

Realtime API는 저지연 음성·오디오 세션에 쓰는 별도의 API이다.
WebRTC, WebSocket, SIP 전송을 지원하며 Responses와 세션·event 스키마가 다르다.
두 API의 WebSocket event를 서로 교환 가능한 형식으로 취급하지 않는다.

## 오류와 재시도

일반적인 HTTP 오류 envelope의 구조는 다음과 같다.

```json
{
  "error": {
    "message": "Invalid value for a request parameter.",
    "type": "invalid_request_error",
    "param": "model",
    "code": null
  }
}
```

| HTTP 상태 | 주요 확인 사항 |
| --- | --- |
| 400 | JSON, 필수 필드, 모델별 파라미터, schema 확인 |
| 401 | 인증·키·프로젝트 설정 확인 |
| 403 | 접근 권한과 지역 제한 확인 |
| 404 | Endpoint와 리소스·모델 접근 가능 여부 확인 |
| 429 | 일시적 rate limit인지 크레딧·지출·usage 제한인지 구분 |
| 500 / 503 | 일시적 서버 오류·과부하에 대한 제한된 재시도 |

일시적 rate limit이나 과부하는 `Retry-After`가 있으면 그 값을 따르고, 없으면 jitter를 포함한 exponential backoff를 사용한다.
크레딧·지출 제한 오류는 반복 재시도로 해결되지 않으므로 `error.code`를 읽는다.
함수 실행에 부수 효과가 있으면 모델 요청 재시도와 함수 실행 중복 방지를 별도로 설계한다.

## 공식 참고 문서

- [API overview: 인증, 헤더, request ID, 호환성](https://developers.openai.com/api/reference/overview)
- [Responses API create](https://developers.openai.com/api/reference/resources/responses/methods/create)
- [Chat Completions API create](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
- [Responses로의 전환과 API 비교](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)
- [Streaming API responses](https://developers.openai.com/api/docs/guides/streaming-responses)
- [Responses WebSocket mode](https://developers.openai.com/api/docs/guides/websocket-mode)
- [Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
- [Error codes](https://developers.openai.com/api/docs/guides/error-codes)
- [GPT-5.6 Terra의 지원 기능](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
