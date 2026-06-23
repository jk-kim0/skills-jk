# Agent Routing

The main session acts as `plan-agent`.

Use routing before the `계획 준비 요약` when the request is large enough to need multiple
viewpoints. The routing note explains which role perspectives will be covered by 기본 검토 and
which roles may benefit from 별도 역할 Agent 검토.

Always use these roles:

- `evidence-collector`
- `evidence-synthesizer`

Use these roles unless the request is trivial:

- `product-planner`
- `senior-engineer`

Use conditional roles only when their trigger applies:

| Role                 | Trigger                                                                  |
| -------------------- | ------------------------------------------------------------------------ |
| `case-split-advisor` | Idea may become several independent SDLC cases                           |
| `technical-manager`  | Multiple components, architecture tradeoff, or ownership coordination    |
| `ux-designer`        | User flow, screen, usability, copy, or interaction impact                |
| `qa-manager`         | Test strategy, regression risk, acceptance coverage, or automation scope |
| `release-manager`    | Rollout, migration, feature flag, rollback, or operational sequencing    |
| `planning-reviewer`  | Final planning document quality check                                    |
| `risk-reviewer`      | Security, permission, data, compliance, or production risk               |

Do not call every role by default. Select the smallest useful set.

When `sdlc-plan` requests a role perspective, include this plan-stage instruction in the request:

```text
이번 요청은 plan 단계입니다. 근거, 영향 가능성이 있는 영역, 선택지, 위험,
design 단계에서 확정할 질문을 정리하세요. 기술 선택, 구현 구조, build 작업 단위는
확정하지 마세요.
```

## Routing Output

Before invoking workers, write a short routing note:

- selected roles
- reason each role is needed
- skipped roles that may look relevant
- brief file path each role should read
- output destination for each role
