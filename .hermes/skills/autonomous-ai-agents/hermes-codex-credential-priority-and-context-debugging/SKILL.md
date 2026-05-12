---
name: hermes-codex-credential-priority-and-context-debugging
description: Adjust which OpenAI Codex OAuth credential Hermes uses first, and debug why Codex sessions compress much earlier than a configured 1M context override.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Codex credential priority and context debugging

Use when a user says any of these:
- `hermes auth 에 보이는 credential 중 특정 것을 기본으로 쓰고 싶다`
- `gpt4 credential을 기본으로 쓰고 싶다`
- `context window가 1M인데 너무 일찍 compress 된다`
- `Preflight compression ... 272,000 threshold`

## What this skill covers

1. Choosing which `openai-codex` OAuth credential/account Hermes uses first
2. Explaining why Codex sessions can compress far earlier than `model.context_length` suggests
3. Distinguishing provider/model selection from credential/account selection

## Key concepts

### A. Model/provider selection vs credential selection are different

- `model.provider` and `model.default` choose the provider + model slug
- `credential_pool_strategies.<provider>` plus auth-pool ordering choose which credential/account is used first inside that provider

Example:
- Provider: `openai-codex`
- Model: `gpt-5.4`
- Credential used first: whichever `openai-codex` pool entry has the highest priority (lowest numeric `priority`) when strategy is `fill_first`

### B. How to make one Codex credential the default

For `openai-codex`, the practical setup is:
- strategy: `fill_first`
- preferred credential entry first / `priority: 0`

Useful config:
```yaml
credential_pool_strategies:
  openai-codex: fill_first
```

If `hermes auth` shows multiple entries like:
- gpt3
- gpt8
- gpt11
- gpt4

and the user wants `gpt4` first, reorder the `openai-codex` credential pool so `gpt4` is `priority: 0`.

## Safe procedure for credential-priority changes

1. Confirm current provider strategy in config
2. Confirm current `openai-codex` pool order and labels
3. Set or keep strategy as `fill_first`
4. Move the desired label to the first slot / `priority: 0`
5. Verify the pool order afterward

Important clarification for users:
- This changes **which login/account is used first**
- It does **not** change the chosen model slug from `model.default`

## Early-compression root cause on Codex OAuth

If the user has a config like:
```yaml
model:
  provider: openai-codex
  default: gpt-5.4
  context_length: 1050000
compression:
  threshold: 0.85
```
but sees logs like:
```text
Preflight compression: ~315,234 tokens >= 272,000 threshold
```
do not assume Hermes is ignoring config at random.

### Actual root cause

`openai-codex` uses provider-specific context resolution from the ChatGPT Codex OAuth `/models` endpoint.
That endpoint can report a much smaller real `context_window` than the direct OpenAI API for the same slug.

Observed practical case:
- `gpt-5.4` on Codex OAuth returned `context_window = 272000`
- `gpt-5.5` on Codex OAuth returned `context_window = 272000`

Hermes then runs a compression feasibility check at startup.
If the auxiliary compression model context is smaller than the current compression threshold, Hermes auto-lowers the live threshold so compression can still succeed.

That is why a session can end up using a threshold like `272000` even when the config claims `1050000`.

## Practical debugging checklist

When debugging early compression on Codex:

1. Verify the active config path and values
2. Verify the active provider is really `openai-codex`
3. Verify the provider's live `/models` response for the current slug's `context_window`
4. Compare:
   - configured `model.context_length`
   - actual provider `context_window`
   - compression threshold
   - auxiliary compression model context
5. Check whether Hermes auto-lowered the session threshold in the compression feasibility step

## Interpretation rules

### If Codex OAuth context is much smaller than config override

Then the config override is not a reliable reflection of real provider capacity.
A large configured `model.context_length` does not guarantee late compression.

### If the user wants to avoid compression around 300k

On Codex OAuth, simply raising `model.context_length` is not enough if the provider only allows ~272k.

## Recommended fixes

### Option 1 — Stay on Codex, make config realistic

Use when the user wants predictable behavior on Codex.

- Remove the unrealistic `model.context_length` override
- Or set it to the provider's real effective limit

This makes compression behavior honest and consistent.

### Option 2 — Disable compression entirely

Use only if the user explicitly accepts more request failures.

```yaml
compression:
  enabled: false
```

Important warning:
- This disables summarization/compression
- It does **not** increase the provider's real context limit
- Long sessions may fail instead of compressing

### Option 3 — Move to a real large-context provider

Use when the user truly wants >300k raw context before compression.

Requirements:
- main model provider must actually support that larger context
- auxiliary compression model/provider must also be able to summarize at that scale

Without both, Hermes may still lower thresholds for feasibility.

## Good final explanation to the user

Use wording like:
- `현재 1M 설정값보다 Codex OAuth provider의 실제 context_window가 더 작아서, Hermes가 startup feasibility check에서 threshold를 낮추고 있습니다.`
- `이 문제는 단순한 threshold 버그라기보다 provider real limit와 config override가 충돌한 상태입니다.`
- `credential 우선순위 변경은 account selection 문제이고, early compression은 provider context limit 문제입니다.`
