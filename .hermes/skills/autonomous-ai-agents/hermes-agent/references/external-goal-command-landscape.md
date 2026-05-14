# External `/goal` command landscape

Use this note when a user asks for a real `/goal`-style command/skill/plugin in the broader agent ecosystem (Hermes/OpenClaw/Codex-adjacent), especially when they want a recommendation rather than generic brainstorming.

## Evaluation checklist

1. Confirm the candidate exposes an actual `/goal` command, not just a prompt template or planning rubric.
2. Read the upstream README for the command surface and terminal states.
3. Check any plugin manifest/metadata file for activation mode, config schema, and install identity.
4. If available, cross-check a marketplace/audit page (for example ClawHub) for install string and audit status.
5. Explicitly classify whether it is:
   - execution loop / state machine
   - prompt shaper / prompt improver
   - vague concept draft / low-evidence project

## Current high-signal candidates reviewed

### 1) brasco05/goal-command
- Repo: https://github.com/brasco05/goal-command
- Marketplace: https://clawhub.ai/plugins/openclaw-goal-command
- Type: execution loop plugin
- Why it stands out:
  - real `/goal` command family documented in README
  - subcommands include `/goal`, `/goal status`, `/goal resume`, `/goal sync`
  - creates durable run files under `goals/runs/<timestamp-slug>/`
  - pushes runs toward explicit terminal states: `DONE`, `BLOCKED`, `FAILED`
  - plugin manifest confirms install identity `openclaw-goal-command`
  - ClawHub page showed audit `Pass` during review
- Recommended install string (from marketplace):
  - `openclaw plugins install clawhub:openclaw-goal-command`

### 2) Dallionking/agent-goal-skill
- Repo: https://github.com/Dallionking/agent-goal-skill
- Type: prompt shaper, not executor
- Important distinction:
  - helps turn a rough objective into a stronger `/goal` prompt
  - does **not** execute the goal itself
- Use when the user wants better goal specification, not a closed-loop runner.

## Recommendation pattern

If the user asks for “the best `/goal` skill/plugin” and wants something they can actually use today, prefer `goal-command` first and explain why it is an execution mechanism rather than only a planning aid.

If the user instead wants help writing better `/goal` prompts, mention `agent-goal-skill` as a complementary tool rather than the primary answer.

## Pitfalls

- Do not recommend a candidate as a `/goal` implementation just because the word `goal` appears in the repo name.
- Do not blur execution plugins and prompt-shaping skills together.
- Do not rely on search snippets alone; confirm in README/manifest.
- Google web search may present anti-bot interstitials, so be prepared to validate through raw GitHub files and secondary search/index pages.
