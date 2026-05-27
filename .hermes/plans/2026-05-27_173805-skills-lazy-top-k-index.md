# Hermes skills index lazy/top-k 구현 방안

## Goal

현재 `skills` toolset이 활성화되면 전체 skills catalog가 system prompt에 주입되어 default profile 기준 약 5.7k tokens를 차지한다. 목표는 skill 사용성은 유지하면서 기본 system prompt에는 전체 index를 넣지 않고, 필요할 때만 작은 후보 목록 또는 전체 목록을 도구로 조회하도록 바꾸는 것이다.

## Current context

현재 관련 코드 흐름:

- `run_agent.py`
  - `AIAgent._build_system_prompt()`에서 skill tools 존재 여부를 확인한다.
  - `has_skills_tools = any(name in self.valid_tool_names for name in ['skills_list', 'skill_view', 'skill_manage'])`
  - true이면 `build_skills_system_prompt(available_tools=..., available_toolsets=...)`를 호출하고 결과를 system prompt stable tier에 추가한다.

- `agent/prompt_builder.py`
  - `build_skills_system_prompt()`가 전체 skills index를 만든다.
  - local skills + external dirs를 스캔한다.
  - `.skills_prompt_snapshot.json`에 skill metadata snapshot을 저장한다.
  - 최종 prompt는 다음 구조다.
    - mandatory skill guidance
    - `<available_skills>`
    - category별 모든 skill name + description
    - `</available_skills>`

- `tools/skills_tool.py`
  - `skills_list(category=None)`는 현재 category 필터만 지원한다.
  - query/top-k 검색은 없다.
  - `skill_view(name, file_path=None)`가 실제 skill 본문을 로드한다.

현재 문제:

- 전체 skill index는 prompt cache 관점에서는 stable하지만, 매 요청 input token 비용에는 계속 포함된다.
- default profile 기준 skills block만 약 5.7k tokens다.
- 실제 한 턴에서 필요한 skill은 보통 0~5개다.

## Recommended implementation shape

권장 구현은 한 번에 완전한 semantic retrieval을 넣기보다, 안전한 2단계로 간다.

1. Phase 1: config-driven `compact` / `lazy` mode 도입
   - 전체 index를 제거하거나 top-k 후보만 system prompt에 넣는다.
   - lexical scoring 기반으로 시작한다.
   - 기존 full mode는 default/backward-compatible로 유지한다.

2. Phase 2: `skills_list(query=..., limit=...)` 확장
   - lazy mode에서 모델이 스스로 후보 검색을 할 수 있게 한다.
   - system prompt는 “필요하면 skills_list(query=...)를 먼저 호출하라”는 짧은 규칙만 제공한다.

3. Phase 3: optional semantic ranking
   - 필요하면 auxiliary model/embedding 없이도 충분한지 관찰한다.
   - 부족하면 lightweight local BM25/SQLite FTS 또는 auxiliary reranker를 추가한다.

## Config design

`hermes_cli/config.py`의 `DEFAULT_CONFIG['skills']`에 아래 설정을 추가한다.

```yaml
skills:
  index_mode: full        # full | compact | lazy | off
  index_top_k: 10         # compact/top-k 후보 수
  index_always_include:   # 어떤 모드에서도 항상 보여줄 핵심 skill
    - hermes-agent
  index_query_sources:
    - user_message
    - cwd
    - project_context_names
```

권장 기본값:

- upstream 기본값은 처음에는 `full`로 둔다.
  - 기존 동작을 깨지 않는다.
  - regression 위험이 작다.
- 사용자 repo/profile에서는 `lazy` 또는 `compact`를 opt-in한다.

나중에 안정화되면 기본값을 `compact`나 `lazy`로 바꿀 수 있다.

Mode 의미:

- `full`
  - 현재와 동일: 전체 category + skill 목록 주입.

- `compact`
  - mandatory guidance는 유지.
  - 전체 index 대신 top-k 후보만 `<available_skills>`에 넣는다.
  - top-k는 현재 user request, cwd, repo hints 기반 lexical score로 선택한다.
  - 이 모드는 “첫 턴부터 일부 후보가 보여야 한다”는 기존 UX와 lazy 사이의 절충안이다.

- `lazy`
  - system prompt에는 전체 index/후보 목록을 넣지 않는다.
  - 짧은 guidance만 넣는다.
  - 예: “Before substantial work, call skills_list(query=...) or skill_view(name=...) when a named skill is known.”
  - `hermes-agent`처럼 hard trigger가 있는 특수 skill은 별도 short guidance로 유지 가능하다.

- `off`
  - skills tool이 켜져 있어도 skills prompt를 아예 넣지 않는다.
  - 고급/디버깅용.

## Code changes

### 1. `agent/skill_utils.py`: metadata index helper 분리

현재 `prompt_builder.py`와 `tools/skills_tool.py`가 비슷한 metadata scan 로직을 각자 갖고 있다. lazy/top-k를 안정적으로 넣으려면 metadata 수집을 공통화하는 게 좋다.

추가 후보:

```python
def collect_skill_index_entries(
    *,
    available_tools: set[str] | None = None,
    available_toolsets: set[str] | None = None,
    include_disabled: bool = False,
) -> list[dict]:
    ...
```

entry shape:

```python
{
  "name": "hermes-agent",
  "skill_name": "hermes-agent",
  "category": "autonomous-ai-agents",
  "description": "Complete guide...",
  "path": "autonomous-ai-agents/hermes-agent/SKILL.md",
  "conditions": {...},
  "platforms": [...],
}
```

주의:

- 기존 snapshot `.skills_prompt_snapshot.json` 포맷을 바로 재사용해도 된다.
- 먼저 `prompt_builder.py` 내부 helper를 조금 정리하는 방식으로 시작하면 변경량을 줄일 수 있다.
- external dirs, disabled skills, platform matching, conditional activation은 기존과 동일하게 적용해야 한다.

### 2. `agent/prompt_builder.py`: mode-aware prompt builder로 확장

현재 함수:

```python
build_skills_system_prompt(available_tools=None, available_toolsets=None) -> str
```

변경안:

```python
def build_skills_system_prompt(
    available_tools: set[str] | None = None,
    available_toolsets: set[str] | None = None,
    *,
    user_message: str | None = None,
    cwd: str | None = None,
) -> str:
```

내부에서 config를 읽어 mode 결정:

```python
skills_cfg = load lightweight config or yaml_load(get_config_path())
mode = skills_cfg.get("index_mode", "full")
top_k = int(skills_cfg.get("index_top_k", 10) or 10)
always_include = set(skills_cfg.get("index_always_include") or [])
```

Mode별 renderer:

```python
if mode == "off":
    return ""
if mode == "lazy":
    return build_lazy_skills_guidance(always_include=...)
if mode == "compact":
    entries = rank_skill_entries(entries, query=user_message, cwd=cwd, top_k=top_k, always_include=...)
    return render_skills_prompt(entries, compact=True)
return render_skills_prompt(entries, compact=False)
```

중요: cache key에 mode/top_k/query/cwd/always_include를 포함해야 한다.

- `full`: 기존처럼 stable cache 가능.
- `lazy`: stable cache 가능.
- `compact`: user_message 기반이면 per-turn 변동이 생긴다. 이걸 stable system prompt에 넣으면 prompt caching 이점이 줄어든다.

따라서 `compact`는 두 가지 중 하나로 결정해야 한다.

A안: compact는 cwd/profile 기반 후보만 system prompt에 넣는다.
- stable하다.
- query 반영은 약하다.

B안: compact 후보는 volatile user-message context로 주입한다.
- query 반영이 좋다.
- system prompt cache를 덜 깨뜨린다.
- 구현은 더 복잡하다.

권장:
- Phase 1에서는 `lazy`를 우선 구현하고, `compact`는 cwd/profile 기반 또는 후순위로 둔다.
- query top-k는 `skills_list(query=...)` 도구에 맡긴다.

### 3. `run_agent.py`: user_message/cwd 전달 위치 결정

현재 `_build_system_prompt(system_message)`는 user message를 모른다. 그래서 진짜 query 기반 top-k를 system prompt에서 만들기 어렵다.

선택지:

#### 선택지 A: lazy mode만 system prompt에서 처리

- `_build_system_prompt()`는 user_message 없이 mode만 보고 lazy guidance를 반환한다.
- query 기반 후보 검색은 tool call `skills_list(query=...)`에서 수행한다.
- 구현이 가장 안전하다.

#### 선택지 B: `_build_system_prompt(system_message, user_message=None)`로 확장

- `run_conversation()`에서 system prompt를 만들 때 user_message를 넘긴다.
- compact mode에서 top-k 후보를 system prompt에 넣을 수 있다.
- 다만 system prompt가 사용자 입력마다 달라져 prompt caching 이점이 줄어든다.

권장:
- 처음에는 선택지 A.
- query 기반 후보는 tool에 맡긴다.
- 나중에 필요하면 volatile message injection 방식으로 B를 별도 설계한다.

### 4. `tools/skills_tool.py`: `skills_list`에 query/limit 추가

현재 schema:

```python
skills_list(category: str = None)
```

확장:

```python
def skills_list(
    category: str = None,
    query: str = None,
    limit: int = None,
    task_id: str = None,
) -> str:
```

schema도 확장:

```json
{
  "category": {"type": "string", "description": "Optional category filter"},
  "query": {"type": "string", "description": "Search query to rank skills by name, category, description, tags, and related skills"},
  "limit": {"type": "integer", "description": "Maximum number of skills to return"}
}
```

검색 대상:

- name
- category
- description
- metadata.hermes.tags
- metadata.hermes.related_skills
- possibly path segments

Scoring v1:

```python
score = 0
if exact name match: +100
if query token in name: +30
if query token in category: +20
if query token in tags: +20
if query token in related_skills: +15
if query token in description: +8
if token appears in cwd path segment: +10
```

한국어 query도 있을 수 있으므로:

- lower-case tokenization만으로도 1차는 충분하다.
- repo/path/skill names는 영어라 cwd와 category/name 매칭이 중요하다.
- query가 비어 있으면 기존 동작 유지.

반환 shape:

```json
{
  "success": true,
  "skills": [...],
  "categories": [...],
  "count": 10,
  "total_matches": 47,
  "query": "...",
  "hint": "Use skill_view(name) ..."
}
```

Backward compatibility:

- 기존 `skills_list(category=...)` 호출은 그대로 동작해야 한다.
- query/limit가 없으면 기존처럼 전체 목록 반환.

### 5. Lazy skills guidance 문구

`lazy` mode의 system prompt는 길이를 200~400 tokens 이내로 제한한다.

예시:

```text
## Skills (lazy)
You have access to skills via skills_list and skill_view. Do not assume the full skill catalog is shown in this prompt.
Before substantial or specialized work, search for relevant skills with skills_list(query=...) using the user's request, current repository/domain, and explicit skill names. If a skill is relevant, load it with skill_view(name) and follow it before acting.
If the user explicitly names a skill, call skill_view(name=...). If no skill appears relevant after a targeted search, proceed without one and state the assumption briefly.
For Hermes Agent setup/config/troubleshooting, load hermes-agent first.
After using a skill and finding it stale or wrong, update it with skill_manage when available.
```

특수 규칙:

- `hermes-agent` hard trigger는 유지한다.
- 기존 mandatory wording인 “Before replying, scan the skills below”는 lazy mode에서는 제거해야 한다. 아래에 목록이 없기 때문이다.
- “MUST load every partial match”도 완화해야 한다. 대신 “before substantial/specialized work, targeted search”가 맞다.

### 6. Optional `compact` mode renderer

compact mode를 넣는다면 다음 방식이 안전하다.

- full index 대신:
  - category summary만 표시하거나
  - `always_include + cwd/profile matched top_k`만 표시한다.

예시:

```text
## Skills (compact)
Use skills_list(query=...) to search the full catalog. A small preselected subset is shown below; it is not exhaustive.
<available_skills>
  autonomous-ai-agents:
    - hermes-agent: ...
  software-development:
    - skills-jk: ...
    - github-pr-workflow: ...
</available_skills>
```

선정 기준 v1:

- `index_always_include`
- cwd basename / git repo name과 skill name/description/category 매칭
- platform/profile name과 category/name 매칭
- recently used skill usage DB가 있다면 top recent를 추가 가능하지만 phase 1에서는 제외

## Proposed phases

### Phase 1: Lazy mode 최소 구현

Files likely to change:

- `hermes_cli/config.py`
- `agent/prompt_builder.py`
- `run_agent.py`는 가능하면 변경하지 않음
- `tests/`에 prompt_builder 관련 test 추가

Implementation:

1. `DEFAULT_CONFIG['skills']`에 `index_mode`, `index_top_k`, `index_always_include` 추가.
2. `prompt_builder.py`에 lightweight config reader 추가.
3. `build_skills_system_prompt()`에서 mode가 `lazy`면 full scan 없이 lazy guidance만 반환.
4. mode가 `off`면 빈 문자열 반환.
5. mode가 `full`이면 기존 로직 그대로.
6. cache key에 mode를 포함한다.

Validation:

- `skills.index_mode: full`에서 기존 prompt가 유지되는지 확인.
- `skills.index_mode: lazy`에서 `<available_skills>`가 사라지고 짧은 guidance만 들어가는지 확인.
- token probe로 skills block이 5.7k → 수백 tokens로 줄어드는지 확인.

Risk:

- lazy mode에서는 모델이 첫 턴에 skills_list를 호출하지 않고 넘어갈 수 있다.
- 이 위험은 guidance 문구와 tool-use enforcement로 어느 정도 줄인다.

### Phase 2: `skills_list(query, limit)` 구현

Files likely to change:

- `tools/skills_tool.py`
- possibly `agent/skill_utils.py` for shared metadata helper
- tests for `skills_list`

Implementation:

1. `_find_all_skills()`가 tags/related_skills/path를 포함하도록 확장하거나 별도 `_find_all_skill_entries()`를 추가한다.
2. query scoring helper 추가:

```python
def _rank_skills(skills, query, cwd=None): ...
```

3. `skills_list()`에 query/limit 인자 추가.
4. schema에 query/limit 추가.
5. query가 있으면 score > 0 우선 정렬, score tie는 category/name.
6. limit가 있으면 slice.

Validation:

- query exact name: `skills_list(query='hermes-agent', limit=5)`에 hermes-agent가 1위.
- repo keyword: `skills_list(query='skills-jk repo hermes profile', limit=5)`에 skills-jk/hermes-agent 계열이 상위.
- category filter + query 조합 동작.
- query 없는 기존 호출 결과 shape 유지.

### Phase 3: Compact top-k mode

Files likely to change:

- `agent/prompt_builder.py`
- maybe `agent/skill_utils.py`
- tests for compact rendering

Implementation:

1. `index_mode: compact`일 때 full scan은 하되 render는 top_k만 한다.
2. query는 사용하지 않고 cwd/profile/repo name 기반으로 stable ranking한다.
3. `index_always_include`는 score와 무관하게 포함한다.
4. prompt에 “not exhaustive; use skills_list(query=...)”를 명시한다.

Validation:

- compact mode prompt에 `<available_skills>`는 있으나 count가 top_k 이하.
- always_include가 항상 포함.
- full mode와 lazy mode가 서로 영향 없음.

### Phase 4: Docs and migration

Files likely to change:

- docs/configuration docs
- docs/skills docs 또는 website docs
- maybe `hermes-agent` skill reference update

Add examples:

```yaml
skills:
  index_mode: lazy
  index_top_k: 10
  index_always_include:
    - hermes-agent
```

Explain:

- full: maximum discoverability, highest prompt cost
- compact: moderate discoverability, lower prompt cost
- lazy: lowest prompt cost, relies on skills_list/skill_view calls
- off: advanced only

## Tests

Suggested tests:

1. `tests/test_prompt_builder_skills_index_modes.py`

Cases:

- default config or missing config → full mode behavior unchanged.
- `skills.index_mode: lazy` → prompt contains `Skills (lazy)` and does not contain `<available_skills>`.
- `skills.index_mode: off` → prompt is empty.
- invalid mode → falls back to `full` or `lazy` depending chosen policy. Recommend fallback to `full` for backward compatibility.

2. `tests/test_skills_list_query.py`

Cases:

- query returns ranked matching skill.
- limit truncates output.
- category filter still works.
- query absent preserves existing full listing behavior.
- disabled/platform-incompatible skills are excluded.

3. Optional integration token test

A lightweight estimator-based test can assert relative size, not exact tokens:

- Create temp HERMES_HOME with many fake skills.
- full mode prompt length > lazy mode prompt length by large margin.
- lazy mode does not scan/render all skill descriptions.

Avoid exact token counts in tests because tokenizer estimates may change.

## Rollout recommendation for this repo-local setup

After implementation lands, set only this repo/profile first:

```yaml
skills:
  index_mode: lazy
  index_top_k: 10
  index_always_include:
    - hermes-agent
    - skills-jk
```

Then verify:

```bash
hermes -p default chat --toolsets terminal,file,skills,memory,todo,code_execution -q "안녕"
```

And run the prompt-size probe:

- expected default total: current ~15.9k → likely ~10k or less
- expected skills block: current ~5.7k → ~300-600 tokens

## Main tradeoffs

### Discoverability vs token cost

Full mode maximizes passive discoverability. Lazy mode saves tokens but relies on the model following the instruction to call `skills_list`.

Mitigation:

- Keep hard trigger for `hermes-agent`.
- Use strong but short lazy guidance.
- Make `skills_list(query=...)` high-quality and cheap.

### Prompt caching

Query-specific top-k inside system prompt may hurt prompt caching because the system prompt changes every turn.

Recommendation:

- Do not put user-query top-k into stable system prompt in phase 1.
- Put query-based discovery behind the `skills_list(query=...)` tool.

### Backward compatibility

Existing users may expect skill index in prompt. Therefore:

- Default to `full` initially.
- Make lazy opt-in.
- Add docs and token-savings examples before changing default.

## Open questions

1. Should `lazy` eventually become default for new installs?
   - Recommendation: not immediately. Make opt-in, collect behavior.

2. Should `skills_list` default to full list or require query when lazy mode is on?
   - Recommendation: keep full list when query absent for backward compatibility.

3. Should top-k use semantic embeddings?
   - Recommendation: no for v1. Lexical + cwd/category scoring is simpler, deterministic, and avoids auxiliary model costs.

4. Should named skill hard triggers be configurable?
   - Recommendation: yes, via `index_always_include` plus explicit guidance for `hermes-agent`.

## Acceptance criteria

- With default `skills.index_mode: full`, existing behavior and tests continue passing.
- With `skills.index_mode: lazy`, no full `<available_skills>` block is present in system prompt.
- `skills_list(query=..., limit=...)` returns relevant candidates without requiring the full index in prompt.
- Token probe shows meaningful reduction in system prompt size for large skill libraries.
- Config changes are profile-aware through existing HERMES_HOME config loading.
- The implementation does not break `skill_view`, plugin skills, disabled skills, platform filters, or external skill directories.
