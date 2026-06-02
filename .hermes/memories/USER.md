User has repository-specific preferences and constraints stored in repo-context skills under `.hermes/skills/`; load the relevant repo skill before substantial work instead of relying on global user profile for repo details.
§
User prefers using Hermes via Telegram first, with Slack connected optionally as a secondary channel.
§
User wants Hermes to default its working directory to the path where Hermes was launched (current working directory / `pwd`), not to a fixed `~/workspace` path.
§
User prefers the assistant to choose the best method for the task, and expects end-of-session review to update memory/skills when durable learnings emerge.
§
User prefers polite Korean and may use Korean chat shorthand like ㅇㅇ, ㅇㅋ, ㄱㄱ.
§
User does not want PRs to auto-close issues; only the user decides when to close issues.
§
User wants PR status checked before commit/push on repo work to avoid continuing on a merged PR branch.
§
For repo work, the user wants brief progress updates, immediate execution once the requested change is clear, and no long passive waits. Give a short status/estimate first, avoid proposal-only pauses, and if commands run long or estimates are exceeded, stop and report status promptly instead of waiting silently.
§
User prioritizes actual website appearance over technical implementation details when evaluating stakeholder-facing UI changes.
§
User prefers low-context communication: respond explicitly to each instruction/question, treat questions as questions, suggestions as suggestions, and instructions as instructions; do not reinterpret a question as a command.
§
User prefers polite speech and does not want banmal.
§
User wants major work stages to be reflected in GitHub wiki documents during ongoing analysis/planning so they can track progress and review incrementally.
§
User prefers current-implementation focus over speculative design; when they ask for a plan/planning document, keep the PR documentation-only and do not implement code, migrate data, rename assets, or update tests unless explicitly asked.
§
User wants repo work to start from the latest main branch, use a git worktree rather than the main workspace checkout by default, verify the actual current directory / cwd instead of assuming a fixed `~/workspace`, and rebase PR branches onto the latest main again before push/PR update.
§
User prefers clear, concise names, but if they request a product name in the symbol, follow it.
§
User prefers clear reviewer-facing terms; in Korean layout docs use '공통 레이아웃 UI' not 'chrome'.
§
For GitHub issue/report writing, the user prefers the body to present English first and then a Japanese translation below it, rather than mixing languages or leading with Japanese.
§
User prefers PR titles, descriptions, review comments, and repo-work comments to be written in Korean for this repo.
§
User prefers deployment/infrastructure fixes that are logically separate from feature work, such as CMS/public tracing fixes, to be split into separate PRs instead of bundled into the feature PR.
§
User does not want local or CI reruns to be left waiting for long periods; avoid long passive waits when checking verification after repo changes.
§
For repo work, the user expects changes to be committed, pushed, and reflected in the PR without being asked again.
§
User wants an upfront time estimate before work starts, and if the estimate is exceeded, the assistant should stop promptly and report status/next steps instead of staying silent.
§
For repo work, user does not want time spent on local build/test verification; prefer commit/push first and monitor CI instead unless the user explicitly asks for local verification.
§
For repo work, user wants fast acknowledgement, brief status, direct execution, parallelism when useful, and no proposal-only pauses.
§
User wants root-cause investigations for Hermes latency to be thorough and evidence-based, not speculative.
§
When the user asks to squash an open PR branch, they expect the assistant to perform the squash and push the updated PR branch without asking again.
§
During active PR follow-up, when the user asks to remove a helper or proceed with a refactor after review, they expect immediate execution rather than a proposal-only response unless clarification is truly needed.
§
When asking to rewrite repository wiki documentation, the user wants it based on the latest main branch implementation rather than an in-progress feature branch.
§
PRs should only be closed after explicit user approval. Unless the user explicitly instructs 'close the PR', do not close it.
§
User prefers launch-readiness reviews and issues to focus on implemented repository state and actionable code changes, not operational governance details or bureaucratic documentation.
§
User prefers repository guidance files like AGENTS.md to stay reasonably concise and not grow indefinitely; detailed procedures should be structured or split out before the file becomes too long.
§
In wiki documents, the user prefers links written in markdown [path](url) format.
§
When restoring Korean website copy, the user is fine keeping expressions that were already in English in the earlier Korean version instead of forcing full Korean translation.
§
The user requires repo work to start from latest main by default, expects local `main` to be explicitly fast-forward updated when review is said to be based on current main, and wants PR branches rebased onto latest main before push/PR update.
§
Across repos, prefer repo-root `.worktrees/`; avoid changing main checkouts unless explicitly requested.
§
User cares strongly about exact code/test file paths: mirror tests to source paths, and render `__tests__` underscores unambiguously.
§
When delegating longer work, the user expects a true background-job style that returns control immediately so they can continue giving instructions; avoid using delegate_task as if it were non-blocking.
§
When the user requests a production-vs-stage web comparison for a specific domain/path, compare the exact requested page/domain literally and do not substitute a redirected target unless the user explicitly asks for that.
§
`workdir=~/workspace` is only a tool default; the agent's real live cwd may differ each run. For repo-context tasks, always verify the actual current directory first and never equate it with the tool workdir.
§
For this website, avoid overlapping wrapper layers unless each has a proven distinct responsibility; prefer simpler page.tsx composition and combine always-paired wrappers unless separation is truly necessary.
§
User does not want dev servers started for testing unless they explicitly request it.
§
When the user says 'workspace 정리', they mean: update local main to the latest origin/main, switch the current checkout to main, and delete stale local branches and stale worktrees safely.
§
User finds cross-repo mixed Hermes CLI history via arrow-key/session recall very inconvenient and prefers per-working-directory or per-repo conversation/history isolation when possible.
§
For static marketing page refactors, the user explicitly wants direct JSX authoring like <Tag>copy</Tag> instead of JSON-like content objects or prop blobs passed into components; treat JSON/array copy declarations and prop-shaped content APIs as a core anti-pattern unless the data is truly tiny and non-marketing.
§
For workspace/repo cleanup, the user considers stash-based preservation low value; prefer keeping a worktree/branch over stashing local changes when preservation is needed.
§
For repo-local workspace cleanup, the user wants branches/worktrees not connected to an open PR treated as stale candidates by default, but local changes must be validated against the latest main branch HEAD first; if a branch has multiple commits, judge meaningfulness after squashing conceptually to the net diff vs latest main, and if the branch is behind, use rebase onto latest main as a quick signal of whether the branch history is stale.
§
For stakeholder-facing webpage intro/description copy, never mention 'MDX'. Treat 'MDX' as an internal file-format term that should not appear in customer-facing explanatory text.
§
For visual/layout/render-parity bugs, the user expects one-pass thorough browser verification against exact URLs, including background/gradient/decorative visual layers, so they do not have to repeatedly catch missed differences.
§
If browser interaction is needed while another agent is using the browser, the user wants new tabs/pages opened instead of reusing or disturbing existing browser tabs/windows.
§
User prohibits browser direct-control fallback unless explicitly permitted; direct-mode CLI/tool failures should surface rather than silently control a browser.
§
For skills-jk main-update/local-change sweep requests, the user expects duplicate-PR avoidance, meaningful local changes preserved in appropriate PRs/worktrees, and final reporting to explicitly state whether root main is updated and clean.
§
When the user corrects a misunderstood goal/scope or expresses frustration about repeated wrong implementation direction, they expect an explicit acknowledgement and corrected plan before further code changes.
§
For the skills-jk repo-local Hermes setup, the user wants Hermes preferences and settings changes, including profile configuration, to be tracked in git rather than left only as local runtime state.
§
When controlling Chrome via DevTools/CDP, user prefers keeping a single attached browser connection/session alive for continued control instead of reconnecting repeatedly for each action.
§
For UI design/documentation PRs, user expects requested variants to be represented in both the written spec and visual design artifacts; if they ask for multiple UI types, every type should appear in the visual design, not only in text.
§
User does not want long-running external commands to leave the session unresponsive; for potentially long commands, user expects background execution or short polling with prompt status updates rather than blocking silently.
§
User wants any external command expected to take more than 30 seconds to run as a background job with notify_on_complete, so the assistant remains responsive to instructions/questions and checks `/queue` messages quickly.
§
For deployment/operations tasks, the user requires frequent, clearly visible intermediate progress reports in ordinary user-facing chat messages; tool calls/tool logs/commentary are not considered progress reports. Do not run through multiple steps and then provide only a completion summary; stop between steps with visible status, rationale, and next-step updates.
§
When the user asks to check and fix open PRs, they expect a full open-PR sweep: inspect every open PR for failing checks and merge conflicts, fix/rebase/push as needed, and report only after all relevant PRs are CLEAN/pass or remaining blockers are explicit.
