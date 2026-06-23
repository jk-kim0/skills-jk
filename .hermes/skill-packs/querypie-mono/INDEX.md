# querypie-mono skill pack

Use when working in `chequer-io/querypie-mono`, especially backend/API work, local server execution, Jira debugging, RDP architecture/support analysis, or the AI Native SDLC workflow stored under `.agents`.

This pack is intentionally stored outside active `.hermes/skills/` so detailed QueryPie monorepo guidance is not injected into every default Hermes request. Load this index only when the current task belongs to `querypie-mono`, then read the smallest relevant skill set.

## Summary

- skills: 10
- skill root: `.hermes/skill-packs/querypie-mono/.agents/skills/`
- support root: `.hermes/skill-packs/querypie-mono/.agents/sdlc/core/`
- adapter roots: `.hermes/skill-packs/querypie-mono/.codex/agents/`, `.hermes/skill-packs/querypie-mono/.claude/`
- active entrypoint: `.hermes/skills/software-development/querypie-mono-pack/SKILL.md`

## How To Use

1. Read this `INDEX.md` first.
2. Pick the smallest relevant skill set from the trigger map below.
3. Read the selected `.hermes/skill-packs/querypie-mono/.agents/skills/**/SKILL.md` files directly with file tools.
4. If an SDLC skill references `.agents/sdlc/core/**`, resolve that path from this pack root unless the target checkout has a newer repo-local `.agents/sdlc/core`.
5. Do not copy the whole pack into the prompt unless the task truly requires broad monorepo context.

## Trigger Map

### Backend implementation and review

- `backend-style-guide` — `.hermes/skill-packs/querypie-mono/.agents/skills/backend-style-guide/SKILL.md`
  - Use for `apps/api` Kotlin/Spring backend implementation, PR review, architecture boundaries, authorization, events, database rules, and security review.
- `backend-ops` — `.hermes/skill-packs/querypie-mono/.agents/skills/backend-ops/SKILL.md`
  - Use for backend operations knowledge such as migrations, environment differences, troubleshooting, and deployment incident patterns.

### Local execution

- `server-runner` — `.hermes/skill-packs/querypie-mono/.agents/skills/server-runner/SKILL.md`
  - Use when running QueryPie local servers, deciding bambi versus local CLI/IDE execution, checking ports, migrations, and early-fail conditions.

### Jira debugging

- `jira-debug` family — `.hermes/skill-packs/querypie-mono/.agents/skills/jira-debug/README.md`
  - Use for Jira issue fetch, attachment organization, detail analysis, component identification, code search, report generation, setup, and Slack handoff.
  - Load only the sub-skill needed for the current step.

### RDP architecture and support

- `rdp-doc` — `.hermes/skill-packs/querypie-mono/.agents/skills/rdp-doc/SKILL.md`
  - Use for RDP/Windows Server access-control architecture, Server Agent structure, network flow, and glossary questions.
- `rdp-cs` — `.hermes/skill-packs/querypie-mono/.agents/skills/rdp-cs/SKILL.md`
  - Use for RDP customer support symptom classification, diagnostic collection, case analysis, response drafting, and closeout guidance.

### AI Native SDLC workflow

- `sdlc-plan` — `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-plan/SKILL.md`
  - Use when turning an idea, ticket, Slack thread, GitHub issue, or repo evidence into an approved SDLC plan.
- `sdlc-design` — `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-design/SKILL.md`
  - Use when converting an approved SDLC plan into design decisions, task model, build tasks, and handoff.
- `sdlc-build` — `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-build/SKILL.md`
  - Use when implementing an approved SDLC design and producing build evidence and test-stage handoff.
- `sdlc-backtrack` — `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-backtrack/SKILL.md`
  - Use when a later SDLC stage finds evidence that an earlier stage decision or artifact may need to change.

## Full Skill List

| skill | path | description |
| --- | --- | --- |
| `backend-ops` | `.hermes/skill-packs/querypie-mono/.agents/skills/backend-ops/SKILL.md` | Backend operations guide for migrations, environment differences, troubleshooting, and incidents. |
| `backend-style-guide` | `.hermes/skill-packs/querypie-mono/.agents/skills/backend-style-guide/SKILL.md` | QueryPie `apps/api` backend coding and review guide. |
| `jira-debug-*` | `.hermes/skill-packs/querypie-mono/.agents/skills/jira-debug/**/SKILL.md` | Jira issue fetch, analysis, component identification, code search, report generation, setup, and Slack handoff. |
| `rdp-cs` | `.hermes/skill-packs/querypie-mono/.agents/skills/rdp-cs/SKILL.md` | RDP customer support diagnosis and response guidance. |
| `rdp-doc` | `.hermes/skill-packs/querypie-mono/.agents/skills/rdp-doc/SKILL.md` | RDP architecture, Server Agent, network flow, and glossary documents. |
| `sdlc-backtrack` | `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-backtrack/SKILL.md` | SDLC stage backtrack coordination. |
| `sdlc-build` | `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-build/SKILL.md` | Approved SDLC design implementation workflow. |
| `sdlc-design` | `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-design/SKILL.md` | Approved SDLC plan design workflow. |
| `sdlc-plan` | `.hermes/skill-packs/querypie-mono/.agents/skills/sdlc-plan/SKILL.md` | Evidence-driven SDLC planning workflow. |
| `server-runner` | `.hermes/skill-packs/querypie-mono/.agents/skills/server-runner/SKILL.md` | QueryPie local server execution orchestration. |

## Validation

From this pack root:

```bash
bash -n .agents/skills/jira-debug/scripts/download_and_organize.sh
bash -n .agents/skills/server-runner/scripts/start-frontend.sh
bash -n .agents/skills/server-runner/scripts/wait-api-health.sh
.agents/skills/sdlc-plan/scripts/validate-sdlc-plan.sh
.agents/skills/sdlc-design/scripts/validate-sdlc-design.sh
.agents/skills/sdlc-build/scripts/validate-sdlc-build.sh
.agents/skills/sdlc-backtrack/scripts/validate-sdlc-backtrack.sh
```

## Notes

- These files came from `querypie-mono/.agents/skills`.
- The SDLC skills depend on `.agents/sdlc/core`; this pack includes the matching core support files under `.hermes/skill-packs/querypie-mono/.agents/sdlc/core`.
- The SDLC skills also validate Codex and Claude adapters; this pack includes the matching `.codex/agents/sdlc-*`, `.claude/agents/sdlc-*`, `.claude/commands/sdlc-plan.md`, and `.claude/skills/sdlc-plan/SKILL.md` support files.
- Keep active `.hermes/skills/` compact; add only thin entrypoints there.
