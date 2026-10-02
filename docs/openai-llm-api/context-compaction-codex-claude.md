# 긴 Context의 Compaction: Codex와 Claude의 동작·효과·주의사항

Compaction은 길어진 대화 이력을 요약이나 압축된 상태로 바꾸어 다음 작업에 필요한 context 공간을 확보하는 기능이다.
모델의 실제 context window를 늘리지는 않으며, 과거 대화의 모든 세부 사항을 원문 그대로 보존하는 기능도 아니다.

공식 문서 확인 기준일은 **2026-10-02**이다.
이 문서에서 Codex는 Codex CLI와 app-server를, Claude는 Claude Code를 중심으로 설명한다.
공개 OpenAI Responses API와 Claude Messages API의 compaction은 별도 절에서 다룬다.
CLI 버전, 모델, 인증 방식, provider와 gateway에 따라 지원 기능과 기본 임계값이 달라질 수 있다.
Payload와 숫자 예제는 설명용이며 실제 API 호출이나 비용·성능 측정 결과가 아니다.

## 1. 무엇이 바뀌는가

모델이 한 번의 추론에 사용하는 context에는 system/developer 지침, 도구 정의, 대화, 읽은 파일, 도구 결과 등이 들어간다.
응답과 reasoning/thinking을 생성할 여유도 필요하므로 입력을 허용 한계까지 채우는 운영은 피한다.
여러 차례 대화에서 과거 정보를 이어 주는 주체는 CLI의 실행 계층이나 API를 호출하는 애플리케이션이다.

```mermaid
flowchart LR
    A["고정 지침·도구 + 긴 대화·파일·도구 결과"] --> B["수동 요청 또는 자동 임계값 도달"]
    B --> C["요약·압축된 상태 생성"]
    C --> D["고정 지침 + 압축된 이력 + 필요한 최근 정보"]
    D --> E["새 질문·도구 호출·작업 계속"]
```

이 그림은 공통 개념을 보여 주며, 각 제품이 동일한 알고리즘이나 메시지 보존 규칙을 사용한다는 뜻은 아니다.

| 개념 | 역할 | Compaction과의 관계 |
| --- | --- | --- |
| Active context | 다음 모델 요청에 실제로 전달되는 정보 | Compaction이 줄이는 대상 |
| 세션 transcript | 화면이나 로그에 남은 전체 대화 기록 | 기록이 남아 있어도 모델이 매번 원문 전체를 보는 것은 아님 |
| 파일·Git·외부 작업 상태 | 실제 저장소와 실행 중이거나 완료된 작업 | Compaction이 파일을 되돌리거나 작업을 취소하지 않음 |
| Prompt cache | 같은 입력 prefix의 계산 상태 재사용 | 캐시된 토큰도 context 공간을 차지함 |
| 지속 지침·외부 메모 | `AGENTS.md`, `CLAUDE.md`, 상태 문서 등 | 요약에서 빠진 규칙과 사실을 다시 확인할 근거 |

화면에 과거 메시지가 보이거나 세션을 resume할 수 있다는 사실만으로, compaction 이후 모델이 그 메시지의 원문을 모두 읽었다고 판단하지 않는다.
Context와 캐시는 [기존 프롬프트 캐시 문서](prompt-caching.md), [Claude context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)를 함께 참고한다.

## 2. Codex와 Claude Code 비교

| 항목 | Codex CLI / app-server | Claude Code |
| --- | --- | --- |
| 수동 실행 | CLI `/compact`, app-server `thread/compact/start` | `/compact`, `/compact <보존할 내용>` |
| 자동 실행 | 모델 기본값 또는 `model_auto_compact_token_limit` 설정 | 모델·환경별 기본값 또는 auto-compact window 설정 |
| 문서화된 처리 | 이전 turn을 중요한 내용을 유지하는 간결한 요약으로 교체 | 오래된 tool output 정리 후 필요하면 별도 요청으로 대화 요약 |
| 보존 지침 | 프로젝트의 `AGENTS.md`와 별도 상태 문서를 근거로 확인 | `CLAUDE.md`의 `Compact Instructions`와 수동 focus 사용 가능 |
| 확인 수단 | `/status`, app-server compaction item의 완료 event | `/context`, `/usage`, compaction 후 작업 상태 재확인 |
| 공개 API와의 관계 | 모든 버전이 항상 `/responses/compact`를 호출한다고 단정할 수 없음 | `/compact`를 Messages API의 특정 beta payload와 동일시하지 않음 |

### 2.1 Codex: 수동·자동 compaction

Codex CLI의 `/compact`는 보이는 대화를 요약해 토큰 공간을 확보한다.
공식 명령 문서는 이전 turn을 핵심 정보를 유지하는 간결한 요약으로 교체한다고 설명한다.

```text
/status
/compact
/status
```

`/status`에서 현재 모델, context·토큰 사용 정보를 확인한다.
`/new`는 같은 CLI 안에서 새 대화를 시작하며 context를 초기화하므로, 기존 작업을 요약해서 이어 가는 `/compact`와 목적이 다르다.
Codex 공식 문서에 설명된 명령은 `/compact`이며, Claude Code의 `/compact <focus>` 문법을 Codex에도 그대로 적용하지 않는다.

자동 compaction의 주요 설정은 다음과 같다.

| 설정 | 의미와 주의점 |
| --- | --- |
| `model_context_window` | 활성 모델의 context window를 Codex에 알리는 설정이며 provider의 실제 한계를 늘리지 않음 |
| `model_auto_compact_token_limit` | 자동으로 이력을 compact할 토큰 임계값이며, 미설정 시 모델 기본값 사용 |
| `model_auto_compact_token_limit_scope` | 기본 `total`은 전체 active context, `body_after_prefix`는 이어받은 compaction-window prefix 이후의 증가분을 기준으로 계산 |
| `compact_prompt` | Inline compaction prompt 재정의 |
| `experimental_compact_prompt_file` | Compaction prompt 파일 재정의이며 experimental 설정 |

다음 TOML은 임계값 설정의 형식 예시이며 모든 모델에 권장하는 수치가 아니다.
사용 중인 모델의 실제 한계와 출력 여유를 확인한 뒤 적용한다.

```toml
model_auto_compact_token_limit = 180000
model_auto_compact_token_limit_scope = "total"
```

공식 CLI·설정 문서만으로는 모든 버전과 provider의 remote/local 선택, fallback 순서, 정확히 남기는 메시지 수를 확정할 수 없다.
Custom compaction prompt 설정이 모든 경로에 같은 방식으로 적용된다고 가정하지 않는다.
운영에서는 설치된 버전과 provider의 지원을 확인하고, 요약 후 목표·제약·현재 작업이 유지됐는지 점검한다.

근거: [Codex developer commands](https://developers.openai.com/codex/developer-commands), [Configuration reference](https://developers.openai.com/codex/config-file/config-reference).

### 2.2 Codex app-server: 시작 응답과 완료 event

App-server는 다음 JSON-RPC 요청으로 수동 compaction을 시작한다.

```json
{
  "method": "thread/compact/start",
  "id": 25,
  "params": { "threadId": "thr_b" }
}
```

즉시 돌아오는 응답은 다음과 같다.

```json
{
  "id": 25,
  "result": {}
}
```

이 응답은 요청을 받아 시작했다는 뜻이며 compaction 완료를 뜻하지 않는다.
동일 thread의 `turn/*`, `item/*` 알림에서 진행 상태를 확인한다.
`contextCompaction` item의 `item/started`와 `item/completed`가 문서화된 관찰 지점이다.
클라이언트는 시작 acknowledgement만으로 새 압축 상태가 준비됐다고 처리하지 않는다.

근거: [Codex app-server](https://developers.openai.com/codex/app-server).

### 2.3 Claude Code: 요약과 context 재구성

Claude Code는 context가 커지면 오래된 도구 결과를 먼저 정리하고, 필요하면 대화를 요약한다.
요약에는 사용자 요청, 중요한 기술적 결정, 코드·파일, 오류와 해결 내용, 진행 중인 작업 등을 남긴다.
초기의 상세 지시나 중간 도구 출력이 원문 그대로 모두 유지되는 것은 아니다.

요약 생성 시 같은 system prompt, tools, 대화 이력에 요약 지시를 마지막 user 메시지로 추가한 **별도의 모델 요청**을 보낸다.
그 결과를 사용해 후속 요청의 긴 대화 이력을 짧은 요약으로 바꾼다.
요약 요청은 세션의 thinking 설정도 따르며, 요약에 필요한 입력·출력 비용이 발생한다.

```text
/context
/compact 목표, 확정한 설계, 수정 파일, 검증 결과, 남은 작업을 중심으로 보존해줘
/context
/usage
```

반복해서 필요한 보존 규칙은 프로젝트 `CLAUDE.md`에 적을 수 있다.

```markdown
## Compact Instructions

- 사용자 목표와 최신 수정 요청을 보존한다.
- 확정한 결정과 미확정 가설을 구분한다.
- 수정 파일, 작업 디렉토리, 브랜치, 남은 작업을 보존한다.
- 실제 수행한 검증과 아직 수행하지 않은 검증을 구분한다.
- 승인 조건과 진행 중인 도구·백그라운드 작업을 보존한다.
```

확인 기준일의 공식 문서는 compaction 후 다음과 같은 복원 동작을 설명한다.

| 대상 | Compaction 이후 |
| --- | --- |
| System prompt와 output style | 계속 적용 |
| 프로젝트 루트 `CLAUDE.md`, 경로 제한 없는 rules, auto memory, plan | 디스크에서 다시 주입 |
| Git status | 현재 저장소에서 새로 읽음 |
| 경로별 rules와 하위 디렉토리 `CLAUDE.md` | 해당 파일을 읽을 때 다시 로드 |
| 세션에서 읽거나 수정한 파일 | 최근 수정 순으로 최대 5개 재확인하며, 5,000토큰 초과 파일은 내용 대신 경로 참조 |
| 사용한 skill 본문 | Skill당 최대 5,000토큰, 총 25,000토큰 한도로 재주입하며 오래된 skill부터 제외 |
| 실행 중인 백그라운드 작업 | 계속 실행되며 진행 중인 작업 정보를 다시 알림 |

파일 수와 토큰 한도는 현재 문서에 기술된 구현 동작이며 영구적인 계약으로 취급하지 않는다.
중요한 파일이 자동으로 다시 읽혔다고 가정하지 말고 필요한 부분을 직접 확인한다.
루트·사용자 `CLAUDE.md`의 세션 중 변경은 `/compact`, `/clear` 또는 재시작 때 다시 로드되므로, 그 변경이 후속 동작과 cache hit에 영향을 줄 수 있다.

자동 compaction은 모델과 환경별로 다르며 모든 Claude Code 세션이 동일한 비율에서 compact하지 않는다.
현재 문서에서는 `/autocompact 200k`, 실행 시 `--autocompact 200k`, 환경변수 `CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000`으로 window를 설정할 수 있다.
환경변수는 정수 토큰 수만 받으며 명령·flag·설정보다 우선하고, window는 모델 한계 이하로 제한된다.
예를 들어 gateway의 실제 한계가 200K라면 1M 모델을 사용하더라도 그 gateway 한계에 맞게 설정해야 한다.

아주 큰 파일이나 tool output 때문에 요약 직후 context가 다시 차면 반복 compaction이 발생한다.
Claude Code는 몇 차례 시도 뒤 thrashing 오류로 중단할 수 있으므로 출력 범위를 줄이거나 필요한 부분만 다시 읽는다.

근거: [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works), [What survives compaction](https://code.claude.com/docs/en/context-window#what-survives-compaction), [Auto-compaction 설정](https://code.claude.com/docs/en/model-config#context-window-and-auto-compaction), [Prompt caching](https://code.claude.com/docs/en/prompt-caching#compacting-the-conversation).

## 3. 공개 API에서의 Compaction

API를 직접 사용하는 애플리케이션은 compaction 활성화, 성공 확인, 후속 이력 구성과 사용량 집계를 구현해야 한다.
다음 예제의 짧은 대화는 payload를 설명하기 위한 것이며, 자동 임계값 방식에서는 이 길이로 compaction이 발생하지 않는다.
모델 이름은 각 공식 compaction 예제의 모델을 따르며, 실제 계정·provider의 지원 여부는 별도로 확인한다.
공통 인증 값은 실제 secret이 아닌 환경변수나 교체용 placeholder이다.

### 3.1 OpenAI: Responses 요청 안에서 자동 compaction

Endpoint와 헤더:

```http
POST /v1/responses HTTP/1.1
Host: api.openai.com
Authorization: Bearer <OPENAI_API_KEY>
Content-Type: application/json
```

요청 payload:

```json
{
  "model": "gpt-5.3-codex",
  "store": false,
  "input": [
    { "role": "user", "content": "긴 코딩 작업을 시작하자." }
  ],
  "context_management": [
    { "type": "compaction", "compact_threshold": 200000 }
  ]
}
```

렌더링된 context가 설정한 임계값을 넘으면 서버가 compaction을 수행하고, 암호화된 compaction item을 출력한 뒤 줄어든 context로 추론을 계속한다.
이 방식에는 별도 `/responses/compact` 호출이 필요하지 않다.
Item은 이전 상태와 reasoning을 적은 토큰으로 이어 주는 불투명한 데이터이며 사람이 읽는 요약이 아니다.

후속 요청 구성은 대화 연결 방식에 따라 다르다.

| 연결 방식 | 후속 요청 규칙 |
| --- | --- |
| Stateless `input` 배열 | 이전 이력에 전체 output을 추가하며 compaction item도 보존 |
| Stateless 배열의 크기 최적화 | Output을 추가한 뒤 가장 최근 compaction item 앞의 item을 제거할 수 있음 |
| `previous_response_id` | 새 user 입력과 이전 Response ID를 전달하며 이력을 직접 잘라내지 않음 |

이 문서의 `store: false` 예제는 stateless 배열 방식이다.
저장하지 않은 Response ID만으로 HTTP 후속 대화가 복원된다고 가정하지 않는다.
Compaction, Response 저장, prompt caching은 각각 다른 기능이다.

### 3.2 OpenAI: 명시적인 `/responses/compact`

다음 호출은 애플리케이션이 compaction 시점을 직접 정하는 stateless 방식이다.
실제로 보낼 때는 그동안 모은 메시지와 필요한 assistant·tool·reasoning item 전체를 `input`으로 전달한다.

```bash
curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/responses/compact \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-6-astra",
    "input": [
      {"role": "user", "content": "교토 여행 일정을 계획해줘."},
      {"role": "assistant", "content": "사흘 동안 방문할 장소를 정했습니다."}
    ]
  }'
```

응답의 `output`은 다음 요청에 사용할 **전체 compacted window**이다.
암호화된 compaction item 외에 이전 window에서 유지한 item도 포함될 수 있다.
이 endpoint의 `output`은 자르거나 compaction item 하나만 골라 사용하지 않고 전체를 그대로 전달한다.
앞 절의 서버측 자동 compaction에서 허용한 prefix 제거 규칙을 이 반환값에 적용하지 않는다.

SDK에서 후속 입력을 구성하는 예제:

```javascript
import OpenAI from "openai";

const client = new OpenAI();
const compacted = await client.responses.compact({
  model: "gpt-6-astra",
  input: [
    { role: "user", content: "교토 여행 일정을 계획해줘." },
    { role: "assistant", content: "사흘 동안 방문할 장소를 정했습니다." }
  ]
});

const response = await client.responses.create({
  model: "gpt-6-astra",
  store: false,
  input: [
    ...compacted.output,
    { role: "user", content: "일정을 이틀 더 늘려줘." }
  ]
});

console.log(response.output_text);
```

Compaction에 보내는 기존 window 자체가 모델 한계 안에 들어가야 한다.
한계를 넘은 뒤 복구 수단으로 호출하기보다 출력·도구 결과의 증가 여유를 남기고 미리 수행한다.
Encrypted content를 직접 만들거나 편집하지 않는다.

근거: [OpenAI Compaction guide](https://developers.openai.com/api/docs/guides/compaction), [Responses compact reference](https://developers.openai.com/api/reference/resources/responses/methods/compact).

### 3.3 Claude API: On-demand compaction

확인 기준일의 Claude API에는 애플리케이션이 별도 요약 요청을 보내는 on-demand 방식이 있다.
`POST /v1/messages`에 `compaction`을 지정하고 `compact-2026-09-04` beta 헤더를 보낸다.

```bash
curl --fail-with-body --silent --show-error \
  https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: compact-2026-09-04" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 4096,
    "system": "한국어로 답하고 확정한 결정과 남은 작업을 구분한다.",
    "messages": [
      {"role": "user", "content": "여행 일정은 사흘로 정하자."},
      {"role": "assistant", "content": "사흘 일정으로 정했습니다."}
    ],
    "compaction": {"type": "summarize"}
  }'
```

성공하면 일반 답변 대신 `stop_reason: "compaction"`과 하나의 `compaction` block이 반환된다.
Block에는 읽을 수 있는 요약 `content`와 `signature`가 있다.
다음은 구조를 설명하는 가상 응답의 일부이며 signature는 실제 호출에 사용할 수 없다.

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "compaction",
      "content": "사용자와 여행 기간을 사흘로 확정했다.",
      "signature": "<ACTUAL_SIGNATURE_FROM_API>"
    }
  ],
  "stop_reason": "compaction"
}
```

후속 호출에서는 다음 규칙을 따른다.

1. 요약 대상 메시지를 반환된 assistant block으로 **교체**한다.
2. `messages` 맨 앞에 최신 compaction block 하나를 두고 그 뒤에 새로운 turn을 추가한다.
3. Block의 `content`와 `signature`를 반환된 그대로 보존한다.
4. 이후 block을 보내는 모든 요청에도 `compact-2026-09-04` 헤더를 포함한다.
5. 요약 요청에는 기존 대화와 동일한 `system`, `tools`를 전달한다.

이력을 맨 앞의 block으로 교체한 후의 구조 예제는 다음과 같다.
Signature placeholder는 실제 반환값으로 바꾸어야 한다.

```json
{
  "model": "claude-opus-5-5",
  "max_tokens": 2048,
  "system": "한국어로 답하고 확정한 결정과 남은 작업을 구분한다.",
  "messages": [
    {
      "role": "assistant",
      "content": [
        {
          "type": "compaction",
          "content": "사용자와 여행 기간을 사흘로 확정했다.",
          "signature": "<ACTUAL_SIGNATURE_FROM_API>"
        }
      ]
    },
    { "role": "user", "content": "이 일정에 맞춰 숙소 위치를 추천해줘." }
  ]
}
```

요약 대상 메시지가 block 앞에 남으면 400 오류이며, 뒤에 남으면 오류 없이 중복 전달될 수 있다.
다음 요청에서 block을 빼면 요약 정보도 전달되지 않는다.
Signed block이 있는 요청에서 threshold compaction을 함께 사용하지 않는다.

HTTP 200만으로 요약 성공을 판정하지 않는다.
`max_tokens`, 거절 등으로 요약에 실패하면 `content`가 빈 배열일 수 있으므로 `stop_reason`과 block을 확인한 뒤에만 기존 이력을 교체한다.
실패 시 원래 이력을 보존한다.
`max_tokens`는 요약 이전 thinking도 포함하므로 너무 작게 잡지 않는다.

미완료 `tool_use`가 있는 마지막 assistant turn은 tool result를 먼저 전달한 뒤 compact한다.
입력은 아직 context window 안에 들어가야 하며, 요약 범위의 이미지·문서·URL 원문이 후속 context에도 남는다고 가정하지 않는다.
현재 on-demand 지원은 provider별로 다르며, 공식 문서상 Amazon Bedrock에서는 사용할 수 없다.

근거: [Compaction on demand](https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand).

### 3.4 Claude API: 토큰 임계값 compaction

일반 Messages 요청 안에서 자동으로 요약하는 방식은 다른 beta와 필드를 사용한다.

```http
POST /v1/messages HTTP/1.1
Host: api.anthropic.com
x-api-key: <ANTHROPIC_API_KEY>
anthropic-version: 2023-06-01
anthropic-beta: compact-2026-01-12
Content-Type: application/json
```

```json
{
  "model": "claude-opus-5-5",
  "max_tokens": 4096,
  "messages": [
    { "role": "user", "content": "긴 코딩 작업을 이어가자." }
  ],
  "context_management": {
    "edits": [
      {
        "type": "compact_20260112",
        "trigger": { "type": "input_tokens", "value": 150000 },
        "pause_after_compaction": false
      }
    ]
  }
}
```

입력 토큰이 임계값에 도달하면 요약을 생성하고 compaction block을 반환한 뒤 후속 응답을 계속한다.
현재 문서의 기본 trigger는 150,000토큰이고 최소값은 50,000토큰이다.
이 수치는 Claude Code `/compact`의 기본 임계값을 뜻하지 않는다.

후속 요청에는 compaction block을 포함한 **전체 응답 content**를 assistant 메시지로 추가한다.
이 방식에서는 block이 요약한 메시지 뒤에 있고, API가 최신 block 이전 content를 자동으로 제외한다.
On-demand 방식의 “block을 맨 앞으로 옮기고 이전 메시지를 직접 교체” 규칙과 섞지 않는다.
`pause_after_compaction: true`이면 `stop_reason: "compaction"`으로 일시 정지한 뒤 이어갈 수 있다.

Custom `instructions`는 기본 요약 지시를 완전히 대체하므로 목표·결정·제약·미완료 작업 등 보존 대상을 빠뜨리지 않는다.
현재 문서상 Claude 5.1 이후 threshold 방식의 custom instructions는 이전 thinking을 포함하지 않는 visible conversation을 요약한다.
On-demand 방식과 thinking 처리까지 같다고 가정하지 않는다.

근거: [Compaction at a token threshold](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold).

## 4. 효과와 비용·캐시의 관계

### 4.1 공간과 응답 품질

| 기대 효과 | 적용 범위와 한계 |
| --- | --- |
| 후속 작업 공간 확보 | 새 질문, tool output, 답변에 사용할 active context가 늘어남 |
| 반복 입력 감소 | 요약 이전 이력을 매번 원문으로 처리하는 양을 줄일 수 있음 |
| 불필요한 정보 감소 | 오래된 시행착오와 중복 출력이 줄어 중요한 상태에 집중하기 쉬워짐 |
| 긴 작업의 연속성 | 사용자 목표, 확정한 결정, 남은 작업이 요약에 남아 있으면 계속 진행 가능 |
| 지연·비용 감소 가능성 | 후속 turn의 절감과 요약·cache rebuild 비용을 함께 계산해야 함 |

예를 들어 고정 지침·도구 10K와 대화·도구 결과 170K가 합쳐 180K인 입력을 생각해 보자.
대화 부분을 12K 상태로 바꾸면 후속 입력은 22K 수준이 될 수 있다.
이는 설명용 가정이며 제품의 보장된 압축률이 아니다.
이미 소비한 180K 입력이나 기존 출력의 비용이 취소되는 것도 아니다.

요약이 잘못된 결정을 남기거나 필요한 수치·코드·예외를 빠뜨리면 응답 품질이 떨어질 수 있다.
반복 compaction은 이전 요약을 다시 요약하면서 정보 누락이나 의미 변화를 누적시킬 수 있다.
정확한 원문이 필요한 내용은 파일·DB·문서 등 외부 근거를 보존하고 필요한 때 다시 읽는다.

### 4.2 Prompt cache와의 상호작용

Compaction은 기존 대화 prefix를 바꾸므로 **대화 이력 부분의 캐시를 새로 만들 수 있다**.
고정 system prompt나 tools까지 항상 모두 무효화된다는 뜻은 아니다.
그 앞부분이 동일하고 provider의 유효한 cache boundary가 있으면 공통 prefix를 계속 재사용할 수 있다.

Claude Code에서는 다음 동작이 문서화되어 있다.

- 캐시가 warm한 동안 요약 요청은 기존 prefix를 읽어 재사용할 수 있다.
- TTL이 지난 오래된 세션에서는 요약 요청이 긴 전체 이력을 uncached 입력으로 처리할 수 있다.
- 요약 뒤 turn은 짧아진 conversation layer의 캐시를 다시 만든다.
- System layer는 보통 유지하며, 디스크에서 다시 로드한 `CLAUDE.md`·memory가 바뀌면 project context의 cache hit도 달라진다.

API에서는 고정 지침·도구를 안정적으로 유지하고 적절한 cache boundary를 둔다.
Claude API는 system 끝과 compaction block에 `cache_control`을 둘 수 있으며, 서명된 block의 요약 내용과 signature는 수정하지 않는다.
OpenAI의 구체적인 경계·TTL 설정은 모델 세대에 따라 달라지므로 [프롬프트 캐시 문서](prompt-caching.md)의 해당 모델 규칙을 따른다.

Cache hit율만 높이기 위해 쓸모없는 이력을 계속 들고 다니거나 매 turn마다 compact하는 것은 권장하지 않는다.
자연스러운 작업 경계에서 compact하고, 후속 요청 수·캐시 수명·요약 품질을 함께 고려한다.
캐시된 180K 입력도 180K의 context를 차지하므로 prompt cache만으로 context 초과를 해결할 수 없다.

### 4.3 무엇을 측정해야 하는가

전체 비용은 일반 turn뿐 아니라 요약 요청의 입력·출력, cache read·write, 요약 후 재읽기까지 포함해 집계한다.
다음 항목을 compaction 전후로 비교한다.

- Active input 크기와 새 출력·도구 결과에 남은 여유.
- 요약 생성 지연, 다음 turn 지연, 전체 작업 완료 시간.
- 입력·출력 토큰, 캐시 읽기·쓰기 토큰과 요약 비용.
- 목표·제약 보존 여부, 파일 재읽기, 작업 중복 실행과 잘못된 판단 여부.

Claude API compaction beta는 요약 사용량을 `usage.iterations`의 `type: "compaction"`으로 보고한다.
On-demand 요약 요청의 최상위 `input_tokens`·`output_tokens`는 0이며, threshold 방식도 최상위 값에 compaction iteration을 포함하지 않는다.
전체 사용량은 iteration별 값을 합산하고, 캐시를 사용하면 cache read·creation 토큰도 비용 및 context 계산에 반영한다.
이미 받은 block의 재전달은 새로운 compaction 생성 비용을 뜻하지 않지만, 후속 요청의 일반 입력·캐시 비용까지 무료라는 뜻은 아니다.

근거: [Claude Code prompt caching](https://code.claude.com/docs/en/prompt-caching), [Claude Code costs](https://code.claude.com/docs/en/costs), [On-demand usage](https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand#count-compaction-usage), [Threshold usage](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold).

## 5. 주의사항과 운영 절차

### 5.1 요약에 남겨야 할 작업 상태

Compaction은 장기 작업을 계속하는 시점이므로 다음 정보를 명시적으로 남긴다.

| 정보 | 보존할 내용 |
| --- | --- |
| 목표와 범위 | 최신 사용자 요청, 완료 기준, 제외 범위 |
| 결정과 제약 | 선택한 설계와 이유, 고정해야 할 수치·식별자·규칙 |
| 위치와 변경 | 실제 worktree 경로, 브랜치, 수정 파일, commit·PR |
| 사실과 가설 | 확인한 결과와 아직 검증하지 않은 추측의 구분 |
| 검증 | 실행 명령과 결과, 마지막 검증 이후의 변경, 미실행 항목 |
| 진행 중 작업 | Tool call ID, 작업·job ID, 실행 상태, 재확인 방법 |
| 권한과 승인 | 사용자가 허용한 작업과 명시적으로 추가 승인이 필요한 작업 |
| 다음 단계 | 바로 수행할 행동, blocker, 다시 읽어야 할 근거 |

인계 내용 예제는 다음과 같다.
경로와 작업은 모두 가상 예제이다.

```text
목표: sample-repo의 로그인 오류를 수정하고 PR을 준비한다.
작업 위치: /workspace/sample-repo/.worktrees/fix-login
브랜치: fix/login-session
범위: 만료된 세션의 재인증 처리.
결정: 401 응답이면 세션을 지우고 로그인 화면으로 이동한다.
변경 파일: src/auth/session.ts, tests/auth/session.test.ts
검증 완료: 단위 테스트 통과. 이후 session.ts를 추가 수정했으므로 재실행 필요.
미검증: 통합 테스트와 브라우저 확인.
진행 중: 통합 테스트 job test-42가 실행 중. 결과를 확인하고 중복 실행하지 않는다.
권한: 로컬 수정과 PR 생성 허용. 운영 배포는 별도 승인 필요.
다음 단계: 현재 diff와 test-42 결과 확인, 단위 테스트 재실행, PR 검증 기록 갱신.
근거: 목표와 승인 조건은 사용자 요청, 파일 상태는 현재 Git diff를 다시 확인한다.
```

요약에 “테스트 통과”가 적혀 있어도 이후 코드가 바뀌었거나 다른 브랜치의 결과이면 현재 상태의 증거로 사용하지 않는다.
사용자 승인을 요약이 새로 만들어 내거나 범위를 넓힐 수는 없다.
중요한 승인 조건은 원래 지시와 프로젝트 규칙에서 다시 확인한다.

### 5.2 Compaction 전

1. 같은 작업을 계속할지, 새 작업을 시작할지 결정한다.
2. 현재 목표·결정·미완료 작업을 짧게 정리하고 중요한 원문은 파일에 남긴다.
3. API의 tool call/result 짝을 완결하고, 실행 중인 외부 작업 상태를 기록한다.
4. 전체 입력이 아직 허용 window 안에 있고 요약·출력에 필요한 여유가 있는지 확인한다.
5. 새 압축 상태의 성공을 확인하기 전까지 원래 이력을 복구 가능한 형태로 보관한다.

무관한 새 작업이면 긴 이력을 요약해서 들고 가기보다 새 대화를 시작할 수 있다.
Codex의 `/new`, Claude Code의 `/clear`는 새 context를 시작하는 선택지이다.
Claude Code의 `/recap`은 화면에 보여 주는 요약을 추가하며 기존 이력을 교체하지 않으므로 context 확보 목적의 `/compact`와 다르다.

### 5.3 Compaction 후

1. RPC 시작 응답, HTTP 상태, 실제 compaction 완료를 구분해서 확인한다.
2. 새 요청에서 요구하는 canonical window 또는 compaction block을 올바른 위치에 전달한다.
3. 최신 사용자 목표, 금지·승인 조건, 작업 디렉토리와 브랜치를 재확인한다.
4. 핵심 파일·diff·job 상태를 다시 읽고 요약의 추측을 실제 증거로 교정한다.
5. 남은 작업부터 계속하고, 이미 완료한 tool 작업이나 외부 쓰기를 반복하지 않는다.
6. Context·캐시·비용을 확인하고, 바로 다시 차면 대형 출력이나 지나치게 낮은 임계값을 조정한다.

세션 transcript 보존, API 데이터 보관, prompt cache 수명은 각각 별도 정책이다.
Compaction을 원문 삭제나 민감 정보 삭제 수단으로 사용하지 않는다.
요약에도 민감한 내용이 들어갈 수 있으므로 필요한 데이터 보관 정책을 별도로 적용한다.

## 6. 공식 참고 자료

| 구분 | 자료 | 확인할 내용 |
| --- | --- | --- |
| Codex | [Developer commands](https://developers.openai.com/codex/developer-commands) | `/compact`, `/status`, `/new` |
| Codex | [Configuration reference](https://developers.openai.com/codex/config-file/config-reference) | Context·auto-compaction·prompt 설정 |
| Codex | [App-server](https://developers.openai.com/codex/app-server) | `thread/compact/start`와 완료 알림 |
| Codex | [Glossary](https://developers.openai.com/codex/glossary) | Compaction·context·`AGENTS.md` 개념 |
| OpenAI API | [Compaction guide](https://developers.openai.com/api/docs/guides/compaction) | 자동·standalone 방식과 이력 전달 |
| OpenAI API | [Responses compact](https://developers.openai.com/api/reference/resources/responses/methods/compact) | 요청·응답 스키마 |
| Claude Code | [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) | Tool output 정리·요약·세션과 파일 상태 |
| Claude Code | [Context window](https://code.claude.com/docs/en/context-window) | Compaction 이후 보존·재주입 |
| Claude Code | [Model configuration](https://code.claude.com/docs/en/model-config) | Auto-compact window와 gateway 한계 |
| Claude Code | [Prompt caching](https://code.claude.com/docs/en/prompt-caching) | 요약 요청의 cache hit와 layer 재구성 |
| Claude Code | [Costs](https://code.claude.com/docs/en/costs) | 사용량·토큰 절감·요약 비용 |
| Claude API | [Compaction overview](https://platform.claude.com/docs/en/build-with-claude/compaction) | 지원 방식·모델·provider |
| Claude API | [Compaction on demand](https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand) | Signed block, 교체 규칙, 실패·usage 처리 |
| Claude API | [Compaction at a token threshold](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold) | 자동 trigger, 후속 이력, cache·usage |
| Claude API | [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) | Context 한계와 cached tokens |
