# vLLM Inference Architecture Reference Implementation Plan

> **For agentic workers:** This plan is executed in the current documentation worktree. Steps use checkbox syntax for tracking.

**Goal:** vLLM `main` 소스를 기준으로 요청 생명주기, 모듈 카탈로그, 실행 시나리오를 각각 설명하는 Mermaid 기반 reference 문서 세 편을 작성한다.

**Architecture:** 세 문서는 같은 source baseline과 공통 용어를 공유하지만 서로 다른 독자 질문에 답한다. 요청 생명주기 문서는 시간 순서, 모듈 카탈로그 문서는 책임·경계, 실행 시나리오 문서는 조건별 분기를 중심으로 구성한다.

**Tech Stack:** Markdown, Mermaid, vLLM Python source inspection, shell-based link/path validation.

---

### Task 1: Source baseline and shared terminology

**Files:**

- Reference: `/Users/jk/workspace/vllm-main-source/vllm/entrypoints/launchers/api_server/entry.py`
- Reference: `/Users/jk/workspace/vllm-main-source/vllm/v1/engine/async_llm.py`
- Reference: `/Users/jk/workspace/vllm-main-source/vllm/v1/engine/core.py`
- Reference: `/Users/jk/workspace/vllm-main-source/vllm/v1/core/sched/scheduler.py`
- Reference: `/Users/jk/workspace/vllm-main-source/vllm/v1/worker/gpu_model_runner.py`

- [x] 조사 commit과 공통 source map을 설계 문서에 기록한다.
- [x] 논리 컴포넌트와 OS 프로세스 경계를 구분한다.
- [x] V1 기본 흐름과 선택적 V0/legacy 경로를 문서 범위에서 구분한다.

### Task 2: Request lifecycle reference

**Files:**

- Create: `docs/vllm-request-lifecycle-reference.md`

- [ ] HTTP router와 serving handler 경계를 설명한다.
- [ ] OnlineRenderer와 InputProcessor의 입력 변환을 설명한다.
- [ ] AsyncLLM의 request queue, EngineCoreClient, output handler 경로를 설명한다.
- [ ] Scheduler, KV cache, Executor, Worker, ModelRunner 경계를 sequence diagram으로 그린다.
- [ ] RequestOutput, IncrementalDetokenizer, OpenAI JSON/SSE 출력 경로를 설명한다.

### Task 3: Module catalog reference

**Files:**

- Create: `docs/vllm-module-catalog-reference.md`

- [ ] 패키지 계층을 flowchart로 그린다.
- [ ] 주요 모듈·클래스·함수·입력·출력·실행 위치를 표로 정리한다.
- [ ] 초기화 경로와 hot path를 구분한다.
- [ ] 분산 executor와 worker 구현 선택지를 catalog에 포함한다.

### Task 4: Execution scenarios reference

**Files:**

- Create: `docs/vllm-execution-scenarios-reference.md`

- [ ] non-streaming과 streaming 요청을 각각 설명한다.
- [ ] continuous batching과 chunked prefill 분기를 설명한다.
- [ ] prefix cache, block allocation, preemption, KV connector를 설명한다.
- [ ] distributed execution과 speculative decoding을 설명한다.
- [ ] Responses API의 built-in tool loop를 선택적 후속 시나리오로 설명한다.

### Task 5: Verification

**Files:**

- Verify: `docs/vllm-request-lifecycle-reference.md`
- Verify: `docs/vllm-module-catalog-reference.md`
- Verify: `docs/vllm-execution-scenarios-reference.md`

- [ ] Markdown heading·fence·relative link를 검사한다.
- [ ] 모든 로컬 vLLM source path가 조사 commit에 존재하는지 검사한다.
- [ ] Mermaid node와 edge가 문서의 설명과 일치하는지 수동 확인한다.
- [ ] git diff와 status를 확인한다.
