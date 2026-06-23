# Agent Invocation

## Principle

Worker roles are part of the planning workflow, but runtime subagents are not guaranteed.

A skill activation cannot force a Codex subagent to spawn. Native subagents are a runtime
capability, not a skill capability.

The plan-agent must use explicit user approval before requesting native worker agents. If that
approval is missing, unavailable, or rejected by the runtime, use same-session role review.

Role perspective review is required when the plan needs multiple viewpoints. Native subagents are
optional execution support, not the only way to collect role perspectives.

## Shared Invocation Contract

Each worker agent receives:

- run id
- starting context
- case id
- idea draft
- role spec path
- source index path
- evidence bundle path
- brief path
- output contract path
- output destination path

Each worker returns:

- role
- scope
- evidence used
- findings
- options
- risks
- decision needed
- confidence

Worker outputs are temporary run artifacts. Do not copy every worker file into an approved case.
Consolidate them into `evidence.md`, the current stage `result.md`, and `handoff.md`.

## Codex

Use `.codex/agents/sdlc-*.toml` for native custom agents when explicit user approval exists.

The plan-agent must not assume that reading this skill is enough to spawn selected subagents.

Before requesting Codex native workers, write the routing note and include this in the
`계획 준비 요약`:

```text
검토 방식

- 기본 검토: 제가 같은 세션에서 기술, QA, 위험 관점을 나누어 검토합니다.
- 별도 역할 Agent 검토: 승인하면 선택한 역할 Agent 세션을 요청합니다.

이 계획은 기술, QA, 위험 관점이 필요해 보입니다.
별도 역할 Agent 의견까지 모아서 진행할까요?
```

The following user requests count as approval:

- `관련 Agent 의견까지 모아줘`
- `역할 Agent들에게 물어보고 계획해줘`
- `subagent를 써서 검토해줘`
- `병렬 Agent로 확인해줘`

If Codex does not allow native subagents, stop retrying and run same-session role review.

Do not ask only `에이전트 사용할까요?`. Explain the review method and the fallback.

## Claude Code

Use `.claude/agents/sdlc-*.md` for native subagents after brief files exist and the user has
approved worker-agent collection.

The Claude command must explicitly invoke selected subagents. If Claude Code cannot invoke them,
run same-session role review.

## Same-Session Role Review

Same-session role review is the default fallback when native worker agents are unavailable.

Same-session role review also applies when the user does not approve separate native workers.

For each selected role:

1. Read `.agents/skills/sdlc-plan/references/roles/<role>.md`.
2. Read the routing note, brief, source index, and evidence bundle.
3. Review only from that role's responsibility and non-responsibility.
4. Write a concise worker result under `.agents/runs/sdlc-plan/<run-id>/workers/<role>.md`.
5. Mark the invocation method as `same-session role review`.

Do not pretend that same-session output came from a separate native subagent.

## Deferred Backends

Do not implement these backends in the first pass:

- `non-interactive-cli`
- `tmux`

If native subagents are unavailable, continue in the main session and record the fallback method.
