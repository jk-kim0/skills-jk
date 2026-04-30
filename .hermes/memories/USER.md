User prefers using Hermes via Telegram first, with Slack connected optionally as a secondary channel.
§
User wants Hermes to default its working directory to the path where Hermes was launched (current working directory / `pwd`), not to a fixed `~/workspace` path.
§
User prefers the assistant to choose the method it can handle best for the task, rather than avoiding specific tools for their own sake.
§
User prefers polite Korean and may use Korean chat shorthand like ㅇㅇ, ㅇㅋ, ㄱㄱ.
§
For repo work, default to PR+CI; use Closes/Fixes only when the PR fully resolves the linked issue.
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
사용자는 모든 코드 작업을 항상 latest main branch 기준으로 시작하길 원한다. 작업 전 반드시 latest main을 업데이트/확인하고, 관련 commit log와 변경된 구현을 파악한 뒤에만 계획·수정해야 하며, 이 과정은 생략할 수 없다.
§
User prefers shorter, simpler file naming when a verbose component filename can be reduced without ambiguity.
§
User currently wants corp-web-v2 demo use-cases and webinars to use plural route-aligned naming consistently: detail routes should use `/demo/use-cases/:id/:slug`, and MDX content directories should mirror actual public URI naming such as `src/content/mdx/demo/use-cases/**` and `src/content/mdx/demo/webinars/**`.
§
For GitHub issue/report writing, the user prefers the body to present English first and then a Japanese translation below it, rather than mixing languages or leading with Japanese.
§
User prefers PR titles, descriptions, review comments, and repo-work comments to be written in Korean for this repo.
§
User expects example path fragments to be treated as illustrative, not literal. When aligning asset paths, mirror the actual src/app URI structure rather than copying placeholder segments like '/path/' into real public paths.
§
User prefers deployment/infrastructure fixes that are logically separate from feature work, such as CMS/public tracing fixes, to be split into separate PRs instead of bundled into the feature PR.
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
User wants very fast acknowledgements during repo work and dislikes proposal-only pauses: give a brief status message first, then proceed directly with the clear requested change; for slower tasks prefer parallel execution and do not leave the user waiting without a response.
§
User wants root-cause investigations for Hermes latency to be thorough and evidence-based, not speculative.
§
In corp-web-v2, the user does not want CMS/public managed route/data files such as src/app/[locale]/features/demo/page.tsx or src/content/documentation/** modified unless they explicitly authorize that exact file or subtree; route, canonical, link, or naming cleanup requests do not imply permission to edit CMS-managed files.
§
In corp-web-v2 stage/content verification, the user treats /features/** as legacy paths that should not count as implemented. If content is not exposed on a separate non-/features public URI, it should be considered not yet implemented.
§
For Solutions static-pages follow-up, the user wants remaining Solutions MDX documents fully reimplemented and replaced in the PR, not left as source artifacts.
§
In corp-web-v2 wiki and migration audits, the user wants `/features/**` treated as legacy across documents, and any content exposed only under `/features/**` should be considered not yet implemented until it has a separate non-legacy public URI.
§
In corp-web-v2 demo work, the user does not want src/features/demo/** touched for image-path consistency fixes unless explicitly requested.
§
In corp-web-v2 route-policy changes, the user wants the GitHub wiki naming-convention document and the corresponding code updates done together in the same batch, not separately.
§
When a requested cleanup would require touching a previously forbidden scope like `src/features/demo/**`, the user expects the assistant to stop and ask before making even a minimal supporting change; do not widen scope just to complete a cleanup.
§
In corp-web-v2 static-page work, the user prefers each page's content to stay colocated in one directory for easy comparison, does not want copy/data/helper split into separate directories, and wants static page.tsx files to remain very thin with minimal logic.
§
The user is open to challenging existing corp-web-v2 repository conventions and does not consider the current overall structure inherently authoritative when evaluating better file placement.
§
For static marketing pages, the user wants page.tsx to show the real marketing copy inline between semantic UX components. Avoid giant content-object props into section components; prefer slot-like APIs with copy passed directly in markup.
§
In corp-web-v2 follow-up work, the user does not want a new PR or reviewer requests created unless they explicitly ask for that PR/review action for the current scoped task; do not infer PR/reviewer permission from earlier broader requests.
§
When the user asks to squash an open PR branch, they expect the assistant to perform the squash and push the updated PR branch without asking again.
§
In corp-web-v2 static-page work, the user wants metadata/SEO data kept route-local with each page rather than centralized in a shared registry; avoid central metadata registries for static pages.
§
In corp-web-v2 static-page work, the user prefers removing even thin shared helpers like route-specific page helpers when they reduce route-local explicitness; favor fully self-contained page.tsx files.
§
During active PR follow-up, when the user asks to remove a helper or proceed with a refactor after review, they expect immediate execution rather than a proposal-only response unless clarification is truly needed.
§
When the user says not to touch a scope like src/features/demo/**, do not change even a single line there for cleanup or path fixes without explicit permission, even if it seems like the minimal way to avoid a broken reference.
§
In corp-web-v2, do not modify CMS-related code or legacy URL/redirect behavior unless the user explicitly instructs that exact scope; route/list-page requests alone do not authorize CMS or legacy URL changes.
§
In corp-web-v2 migration comparison wiki tables, the user wants memo/description cells kept concise and information-dense; do not include legacy-route explanatory prose when current canonical routes are the real subject.
§
사용자는 corp-web-v2에서 CMS 관련 코드/경로와 공개 MDX 경로 분석을 완전히 별개로 취급하길 원한다. MDX 목록/공개 경로 원인 분석에서는 /features/** 등 CMS legacy 경로와 CMS 관련 코드 전체를 아예 분석 대상에서 제외하고 언급도 하지 말 것.
§
User prefers sitemap-style documentation to emphasize URI paths first, with nested bullet lists for page titles and translations, because it makes website structure easier to scan.
§
User does not need local build testing or local dev servers for corp-web-japan changes and prefers relying on CI for verification; local dev servers consume too many resources in the user's environment and interfere with work unless explicitly requested.
§
When asking to rewrite repository wiki documentation, the user wants it based on the latest main branch implementation rather than an in-progress feature branch.
§
When documenting corp-web-japan issues or link audit tables, the user prefers all links written in markdown [path](url) format, wants a Korean translation column next to Japanese labels, and when showing Japanese text to the user expects a Korean translation in parentheses immediately after it.
§
PRs should only be closed after explicit user approval. Unless the user explicitly instructs 'close the PR', do not close it.
§
User prefers launch-readiness reviews and issues to focus on implemented repository state and actionable code changes, not operational governance details or bureaucratic documentation.
§
User prefers repository guidance files like AGENTS.md to stay reasonably concise and not grow indefinitely; detailed procedures should be structured or split out before the file becomes too long.
§
Whenever showing Japanese text to the user, include the Korean translation immediately after it in parentheses.
§
In wiki documents, the user prefers links written in markdown [path](url) format.
§
When restoring Korean website copy, the user is fine keeping expressions that were already in English in the earlier Korean version instead of forcing full Korean translation.
§
For corp-web-v2 documentation sidebar requests, preserve the exact ordered structure literally as specified by the user. Current required order: CMS label -> All -> Introduction -> Glossary -> Manuals -> White Papers -> Blogs -> separator -> MDX label -> White Papers -> Blogs. Do not omit CMS White Papers/Blogs, and do not reinterpret the request as either CMS-only or MDX-only.
§
The user requires all repo work to start from the latest main branch by default unless explicitly instructed otherwise, and requires PR branches to be rebased onto the latest main branch again before push/PR update.
§
Across all repos, unless explicitly told to use the main workspace checkout, do not modify code there; use a git worktree for code changes.
§
User cares strongly about code structure and file paths, including tests: place test files on paths mirroring the source file paths they cover.
§
For corp-web-japan contact-us rollout, the user's intended strategy is: keep /t/contact-us as a feature-flag path until implementation and testing are fully complete, make all implementation other than the /t path production-ready, and then switch the existing /contact-us redirect endpoint at the end with a minimal route change.
§
For corp-web-japan contact-us rollout, the user wants /t/contact-us kept as the feature-flag public form route until final validation/testing is complete; only at the very end should the existing /contact-us public entry be switched with a minimal route change.
§
For corp-web-japan contact-us rollout, the correct approved structure is: keep the form page at /t/contact-us until final validation/testing, use /contact-us/submit as the submit endpoint, keep app route code thin, and place backend implementation in reusable shared locations such as src/lib or src/components rather than route-local heavy logic.
§
When delegating longer work, the user expects a true background-job style that returns control immediately so they can continue giving instructions; avoid using delegate_task as if it were non-blocking.
§
When the user requests a production-vs-stage web comparison for a specific domain/path, compare the exact requested page/domain literally and do not substitute a redirected target unless the user explicitly asks for that.
§
User does not want Python code used for simple Vercel CLI/environment inspection tasks; prefer pure Vercel CLI and basic shell output instead.
§
`workdir=~/workspace` is only a tool default; the agent's real live cwd may differ each run. For repo-context tasks, always verify the actual current directory first and never equate it with the tool workdir.
§
User prefers shorter page-level component names in corp-web-japan; in page.tsx, component names should match UX element names directly (e.g. SolutionOverviewSection rather than TopPageSolutionOverviewSection).
§
User does not want dev servers started for testing unless they explicitly request it.
§
When cleaning stale corp-web-japan worktrees, a worktree whose only remaining dirt is .hermes/ local runtime state and whose remote branch/PR is already merged should be deleted rather than preserved.
§
For top-page refactors in corp-web-japan, the user's key requirement is not just moving copy into page.tsx, but authoring it as direct JSX like <Component>marketing text</Component> rather than large JSON-like props/objects in page.tsx.
§
When the user says 'workspace 정리', they mean: update local main to the latest origin/main, switch the current checkout to main, and delete stale local branches and stale worktrees safely.
