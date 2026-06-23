# Evidence Collection

Prefer direct links and narrow search first.

Use `references/source-adapters.md` before calling external service APIs directly.

Record:

- source type
- source link or query
- access status
- retrieval time
- relevant summary
- evidence id

Do not paste long sensitive source text into planning documents. Use summaries and links.

Runtime artifacts under `.agents/runs/` are temporary. If worker findings matter for the approved
case, summarize them into `evidence.md` instead of making later stages depend on the runtime path.

## Source Types

- human input
- Jira ticket
- Slack thread
- GitHub issue
- repository file
- existing spec or documentation
- previous SDLC case
- command output

## Jira

Jira ticket 조회는 기본적으로 Jira CLI adapter를 사용한다.

```bash
.agents/skills/sdlc-plan/scripts/collect-jira.sh <issue-key> --run-id <run-id>
```

이 script는 `jira issue view <issue-key> --raw`와
`jira issue view <issue-key> --plain --comments <n>` 결과를 run artifact에 저장한다.
승인 case의 `evidence.md`에는 긴 원문 대신 요약과 근거 공백만 승격한다.

## Collection Rules

Separate human opinion from external source content.

Mark unverified assumptions explicitly.

Record failed lookups and permission gaps. Missing evidence is part of the planning context.

Use broad external searches only after the user agrees to the scope.
