User prefers using Hermes via Telegram first, with Slack connected optionally as a secondary channel.
§
User prefers the default working directory for future tasks to be ~/workspace.
§
User prefers the assistant to choose the method it can handle best for the task, rather than avoiding specific tools for their own sake.
§
User prefers polite Korean and may use Korean chat shorthand like ㅇㅇ, ㅇㅋ, ㄱㄱ.
§
User prefers verification via Draft PR and CI pipeline instead of spending time on running local development servers.
§
User wants PR status checked before commit/push on repo work to avoid continuing on a merged PR branch.
§
User prefers brief progress updates while work is in progress.
§
User prioritizes actual website appearance over technical implementation details when evaluating stakeholder-facing UI changes.
§
User says there is no policy that the Japanese site's default font must be Pretendard JP; do not treat that as a constraint.
§
User prefers low-context communication: respond explicitly to each instruction/question, treat questions as questions, suggestions as suggestions, and instructions as instructions; do not reinterpret a question as a command.
§
User prefers polite speech and does not want banmal.
§
User expects Git tasks to be completed through commit and push, and considers them complete only when reviewable via PR or web URL.
§
User expects long-running external commands to be actively monitored; if a command takes longer than expected, stop waiting, interrupt or switch strategy promptly instead of passively waiting.
§
User wants major work stages to be reflected in GitHub wiki documents during ongoing analysis/planning so they can track progress and review incrementally.
§
For confluence-mdx reverse-sync work, the user prefers two separate PRs in sequence: first update docs to reflect the current implementation state, then open a separate Draft PR for a new replacement plan document and refine that plan through review.
§
For querypie-docs reverse-sync discussions, the user values checking whether design concepts are actually reflected in current implementation and whether terminology is used consistently across code and docs.
§
User prefers not to discuss speculative designs for unimplemented features; focus on current implementation unless they explicitly ask for future design.
§
사용자는 새 작업을 시작할 때 항상 latest main branch 기준으로 새 worktree 또는 새 branch를 만들어 진행하길 원한다.
§
User prefers shorter, simpler file naming when a verbose component filename can be reduced without ambiguity.
§
User currently wants corp-web-v2 use-case demo detail routes to use plural /demo/use-cases/:id/:slug rather than singular /demo/use-case/:id/:slug.
§
In corp-web-v2, the user prefers PR titles, descriptions, and review comments to be written in Korean.
§
User prefers PR titles, descriptions, and repo-work comments to be written in Korean for this repo.
§
User currently wants corp-web-v2 use-case demo detail routes to use plural /demo/use-cases/:id/:slug.
§
User expects example path fragments to be treated as illustrative, not literal. When aligning asset paths, mirror the actual src/app URI structure rather than copying placeholder segments like '/path/' into real public paths.
§
User prefers deployment/infrastructure fixes that are logically separate from feature work, such as CMS/public tracing fixes, to be split into separate PRs instead of bundled into the feature PR.
§
User wants corp-web-v2 demo MDX content directories to mirror actual src/app/public URI naming across categories, e.g. use plural `src/content/mdx/demo/use-cases/**` to match `/demo/use-cases/**` and plural `src/content/mdx/demo/webinars/**` to align with `/webinars/**`.
§
In corp-web-v2 asset migration work, the user prefers non-image assets like animation JSON files to be colocated under route-aligned public paths with the related page assets (e.g. under public/solutions/<route>/) rather than left in generic shared roots like public/assets when they are page-specific.
§
User does not want local or CI reruns to be left waiting for long periods; avoid long passive waits when checking verification after repo changes.
§
For repo work, the user expects changes to be committed, pushed, and reflected in the PR without being asked again.
§
In corp-web-v2, the user wants repeated local npm install in fresh worktrees avoided when possible because it causes significant delay.
§
User wants an upfront time estimate before work starts, and if the estimate is exceeded, the assistant should stop promptly and report status/next steps instead of staying silent.
§
For repo work, user does not want time spent on local build/test verification; prefer commit/push first and monitor CI instead unless the user explicitly asks for local verification.
§
In corp-web-v2, the user does not want node_modules kept inside worktrees.
§
User wants very fast acknowledgements during repo work; do not stay silent while tools run, and report immediate status if a command is taking longer than expected.
§
User prioritizes very fast execution and fast replies; for slow tasks, prefer parallel execution and do not leave the user waiting without a response.
§
User expects an immediate verbal response first: briefly state what is being checked/changed before tool work, and if work runs longer than estimated, stop and switch to a faster alternative instead of continuing silently.
§
User wants root-cause investigations for Hermes latency to be thorough and evidence-based, not speculative.