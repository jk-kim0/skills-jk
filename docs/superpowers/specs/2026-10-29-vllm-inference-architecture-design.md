# vLLM Inference Architecture Reference Design

## 목적

vLLM upstream `main`의 현재 소스를 조사하여 외부 API 요청이 LLM inference를 거쳐 응답으로 출력되는 구조를 reference 문서 세 편으로 설명한다.

문서는 사용자가 동일한 시스템을 서로 다른 관점에서 읽을 수 있도록 요청 생명주기, 모듈 카탈로그, 실행 시나리오를 각각 독립적인 진입점으로 제공한다.

## 조사 기준

- Repository: `https://github.com/vllm-project/vllm`
- Branch: `main`
- 조사 commit: `fa3b9d1377219247060d3c8b49eae199c9e7e154`
- 조사일: 2026-10-29
- 기본 실행 경로: V1 engine과 OpenAI 호환 generate API
- 범위 밖: 모든 모델별 특수 구현, 모든 provider endpoint, 성능 수치의 실측, 특정 배포판의 전체 PID 목록

문서에는 소스 경로와 조사 commit 링크를 함께 넣어 버전 드리프트를 추적할 수 있게 한다.

## 산출물

### 1. 요청 생명주기 중심

파일: `docs/vllm-request-lifecycle-reference.md`

외부 HTTP 요청 한 건을 기준으로 입력 검증·chat template 렌더링·토큰화·sampling 파라미터 구성·엔진 admission·EngineCore 전달·스케줄링·KV cache 할당·GPU forward·sampling·출력 처리·디토크나이징·JSON 또는 SSE 응답까지의 순서를 설명한다.

포함할 도식:

- 전체 계층 flowchart
- 단일 요청과 streaming 응답의 sequence diagram
- 각 경계에서 전달되는 데이터와 상태 표

### 2. 모듈 카탈로그 중심

파일: `docs/vllm-module-catalog-reference.md`

`entrypoints`, `renderers`, `v1/engine`, `v1/core`, `v1/executor`, `v1/worker`, `model_executor`, `distributed`의 책임과 주요 클래스·함수를 표로 정리한다.

포함할 도식:

- 패키지 계층 및 의존 방향 flowchart
- request-side, scheduler-side, worker-side, response-side 컴포넌트 관계도

각 항목에는 역할, 주요 입력·출력, 실행 위치, 대표 소스 경로를 기록한다.

### 3. 실행 시나리오 중심

파일: `docs/vllm-execution-scenarios-reference.md`

동일한 핵심 엔진이 설정과 요청 조건에 따라 어떻게 달라지는지 시나리오별로 설명한다.

필수 시나리오:

- 단일 non-streaming 요청
- token streaming 요청
- 여러 요청의 continuous batching
- prefix cache와 PagedAttention 계열 block 관리
- tensor/pipeline/data parallel 실행
- speculative decoding
- optional tool-call 후속 요청

각 시나리오는 Mermaid flowchart 또는 sequence diagram, 핵심 상태 변화, 적용되는 소스 경로, 주의사항으로 구성한다.

## 공통 문서 원칙

- 설명은 소스에서 확인한 사실과 개념적 요약을 구분한다.
- `vllm.entrypoints.openai.api_server`가 deprecated wrapper라는 점과 현재 `vllm server` launcher 경로를 명시한다.
- API server 프로세스와 EngineCore·worker 프로세스의 분리는 설정에 따라 달라질 수 있으므로 논리 컴포넌트와 OS 프로세스를 구분한다.
- scheduler는 별도의 고정된 prefill/decode 단계보다 `num_computed_tokens`와 `num_tokens_with_spec` 차이를 따라 토큰을 배정한다는 현재 V1 구현을 기준으로 설명한다.
- streaming 응답은 엔진 내부의 `RequestOutput` 스트림과 외부 HTTP SSE framing을 구분한다.
- KV cache는 논리 block 할당·prefix hit·connector transfer와 GPU physical storage를 구분한다.
- `n > 1`, LoRA, multimodal, structured outputs, tool parser는 핵심 경로에 영향을 주는 선택적 분기로 표시한다.

## 검증 계획

1. 각 문서가 H1 하나와 순차적인 heading 계층을 갖는지 확인한다.
2. Mermaid fenced block의 닫힘과 node reference 일관성을 확인한다.
3. 문서에 적은 vLLM 소스 경로가 조사 commit에 실제로 존재하는지 검사한다.
4. 세 문서 사이의 상대 링크와 조사 기준 commit 링크가 유효한지 확인한다.
5. 생성·수정한 파일만 git diff에 포함되는지 확인한다.
