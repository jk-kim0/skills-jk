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
User says there is no policy that the Japanese site's default font must be Pretendard JP; do not treat that as a constraint.
§
User prefers low-context communication: respond explicitly to each instruction/question, treat questions as questions, suggestions as suggestions, and instructions as instructions; do not reinterpret a question as a command.
§
User prefers polite speech and does not want banmal.
§
Git tasks are complete only after commit/push and a PR/web URL; in corp-web-app route-local authoring, `/t` routes are interim safety checks, not the final deliverable.
§
User wants major work stages to be reflected in GitHub wiki documents during ongoing analysis/planning so they can track progress and review incrementally.
§
For confluence-mdx reverse-sync work, the user prefers two separate PRs in sequence: first update docs to reflect the current implementation state, then open a separate Draft PR for a new replacement plan document and refine that plan through review.
§
For querypie-docs reverse-sync discussions, the user values checking whether design concepts are actually reflected in current implementation and whether terminology is used consistently across code and docs.
§
User prefers current-implementation focus over speculative design; when they ask for a plan/planning document, keep the PR documentation-only and do not implement code, migrate data, rename assets, or update tests unless explicitly asked.
§
User wants repo work to start from the latest main branch, use a git worktree rather than the main workspace checkout by default, verify the actual current directory / cwd instead of assuming a fixed `~/workspace`, and rebase PR branches onto the latest main again before push/PR update.
§
User prefers clear, concise names, but if they request a product name in the symbol, follow it.
§
User prefers clear reviewer-facing terms; in Korean layout docs use '공통 레이아웃 UI' not 'chrome'.
§
User currently wants corp-web-v2 demo use-cases and webinars to use plural route-aligned naming consistently: detail routes should use `/demo/use-cases/:id/:slug`, and MDX content directories should mirror actual public URI naming such as `src/content/mdx/demo/use-cases/**` and `src/content/mdx/demo/webinars/**`.
§
For GitHub issue/report writing, the user prefers the body to present English first and then a Japanese translation below it, rather than mixing languages or leading with Japanese.
§
User prefers PR titles, descriptions, review comments, and repo-work comments to be written in Korean for this repo.
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
For repo work, user wants fast acknowledgement, brief status, direct execution, parallelism when useful, and no proposal-only pauses.
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
For corp-web-app/corp-web-japan route-local authoring, user wants visible JSX copy/links/composition, not JSON-like registries; corp-web-app GitHub wiki docs are Korean by default.
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
User prefers sitemap-style docs to emphasize URI paths first; for corp-web-app sitemap E2E, keep sitemap-absent required public URLs in a separate fixture merged into checks.
§
For corp-web-japan, user prefers CI over local builds/dev servers unless requested. For QueryPie micro-sites, user prefers monorepo and clear routing/assets over hidden middleware rewrites.
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
The user requires repo work to start from latest main by default, expects local `main` to be explicitly fast-forward updated when review is said to be based on current main, and wants PR branches rebased onto latest main before push/PR update.
§
Across repos, prefer repo-root `.worktrees/`; avoid changing main checkouts unless explicitly requested.
§
User cares strongly about exact code/test file paths: mirror tests to source paths, and render `__tests__` underscores unambiguously.
§
For corp-web-japan contact-us rollout, keep `/t/contact-us` as the feature-flag public form route until final validation/testing is complete; only at the very end should the existing `/contact-us` public entry be switched with a minimal route change. The approved structure is: use `/contact-us/submit` as the submit endpoint, keep app route code thin, and place backend implementation in reusable shared locations such as `src/lib` or `src/components` rather than route-local heavy logic.
§
When delegating longer work, the user expects a true background-job style that returns control immediately so they can continue giving instructions; avoid using delegate_task as if it were non-blocking.
§
When the user requests a production-vs-stage web comparison for a specific domain/path, compare the exact requested page/domain literally and do not substitute a redirected target unless the user explicitly asks for that.
§
User does not want Python code used for simple Vercel CLI/environment inspection tasks; prefer pure Vercel CLI and basic shell output instead.
§
`workdir=~/workspace` is only a tool default; the agent's real live cwd may differ each run. For repo-context tasks, always verify the actual current directory first and never equate it with the tool workdir.
§
For this website, avoid overlapping wrapper layers unless each has a proven distinct responsibility; prefer simpler page.tsx composition and combine always-paired wrappers unless separation is truly necessary.
§
User does not want dev servers started for testing unless they explicitly request it.
§
When cleaning stale corp-web-japan worktrees, a worktree whose only remaining dirt is .hermes/ local runtime state and whose remote branch/PR is already merged should be deleted rather than preserved.
§
For top-page refactors in corp-web-japan, the user's key requirement is not just moving copy into page.tsx, but authoring it as direct JSX like <Component>marketing text</Component> rather than large JSON-like props/objects in page.tsx.
§
When the user says 'workspace 정리', they mean: update local main to the latest origin/main, switch the current checkout to main, and delete stale local branches and stale worktrees safely.
§
When the user points to a specific Preview Deployment URL and reports a visual discrepancy, verify that exact deployed URL directly in the browser; local render alone is not sufficient because preview and local spacing/UX can differ.
§
User finds cross-repo mixed Hermes CLI history via arrow-key/session recall very inconvenient and prefers per-working-directory or per-repo conversation/history isolation when possible.
§
In corp-web-japan static-page route-local authoring refactors, even when the scope is reduced to one or a few sections, the user expects each targeted section to be fully refactored: section implementation should be extracted under src/components/sections, while page.tsx should retain the section copy/data/composition. Page-local helper section components inside page.tsx are not considered complete.
§
For static marketing page refactors, the user explicitly wants direct JSX authoring like <Tag>copy</Tag> instead of JSON-like content objects or prop blobs passed into components; treat JSON/array copy declarations and prop-shaped content APIs as a core anti-pattern unless the data is truly tiny and non-marketing.
§
In corp-web-japan static-page route-local authoring refactors, the user expects refactor-only PRs to preserve the existing UI exactly unless they explicitly request a design change. Preserve box/button wrapper classes, icons, spacing, and overall visual parity rather than re-styling while moving copy ownership.
§
In corp-web-japan static-page route-local authoring refactors, the user does not want section components to infer highlighted marketing copy by string matching; highlighted words/phrases should be authored explicitly in page.tsx JSX so copy emphasis ownership stays route-local.
§
In corp-web-japan route-local authoring, the user prefers section/card subtitles and similar small marketing copy to be authored as child elements in page.tsx rather than passed via prop fields like subtitle=.
§
For corp-web-japan static marketing copy, the user prefers semantic emphasis in route-local JSX via `<strong>...</strong>` rather than presentation-heavy inline `<span className=...>` markup; visual highlight styling should live in the wrapper/section component.
§
User expects clear implementation instructions to be executed, but for sensitive infrastructure setup such as GitHub self-hosted runners, they want step-by-step guided execution and no proceeding ahead of explicit guidance.
§
User does not use /rollback and prefers Hermes checkpoints disabled unless explicitly needed.
§
For workspace/repo cleanup, the user considers stash-based preservation low value; prefer keeping a worktree/branch over stashing local changes when preservation is needed.
§
In corp-web-japan resource-list refactors, the user wants page.tsx to keep route-authored hero (`ResourceListHeroSection`, `ResourceListHeroTitle`, `ResourceListHeroDescription`) and CTA sections visible, while only the repeated sidebar block may be extracted. For naming, prefer context-specific React terms and names over vague ones: keep `ResourceListSidebar*` primitives rather than renaming them to `Generic*`, and prefer a specific composed name like `ResourceCategorySidebar`/`ResourceListCategorySidebar` over broad names like `PublicResourceSidebar` when possible.
§
For repo-local workspace cleanup, the user wants branches/worktrees not connected to an open PR treated as stale candidates by default, but local changes must be validated against the latest main branch HEAD first; if a branch has multiple commits, judge meaningfulness after squashing conceptually to the net diff vs latest main, and if the branch is behind, use rebase onto latest main as a quick signal of whether the branch history is stale.
§
For stakeholder-facing webpage intro/description copy, never mention 'MDX'. Treat 'MDX' as an internal file-format term that should not appear in customer-facing explanatory text.
§
In corp-web-japan PR follow-up scope, removing demo /t entrypoints does not imply removing the general Preview Toggle UI or its API route. Keep that scope narrow unless the user explicitly asks to remove the global preview toggle.
§
When reviewing corp-web-japan publication/routing changes, the user expects priority on finding missing hidden-posting or redirect configuration/canonicalization gaps, not just whether a PR is stale or mergeable.
§
In corp-web-japan copy/content follow-up work, if the user asks to correct a mistaken title/label in an existing content item, prefer preserving the item and fixing the exact wording rather than deleting the page or replacing it with a broader structural change.
§
In corp-web-japan publication/routing audits, the user wants review focus on actual missing redirects and wrong redirect targets on the latest origin/main baseline, not on 'shrink/removal candidates.' Evidence should be prioritized from latest main code, route implementation, and stage/live behavior.
§
In corp-web-japan, when preview /t/* routes are promoted or replaced, the user does not want the /t/* endpoints kept at all and does not want redirect compatibility left behind, unless they explicitly ask for a specific /t/* path to remain. Default policy: remove /t/* route files entirely, not redirect them.
§
For visual/layout/render-parity bugs, the user expects one-pass thorough browser verification against exact URLs, including background/gradient/decorative visual layers, so they do not have to repeatedly catch missed differences.
§
For querypie.com/ja page migrations in corp-web-japan, the user wants the existing page copied as-is without invented preview explanation text, rewritten title/description copy, or new CTA sections unless explicitly requested.
§
If browser interaction is needed while another agent is using the browser, the user wants new tabs/pages opened instead of reusing or disturbing existing browser tabs/windows.
§
For corp-web-japan and similar repo work, any reusable migration/workflow skill should be provided as a repo-local skill under .agents/skills/, not only as a built-in/global skill.
§
For corp-web-app MDX migration reviews, user expects frontmatter relationship fields such as relatedIds, accepted identifier formats, and collection/family identifier contracts to be audited explicitly, not just content counts/routes/assets.
§
User prohibits browser direct-control fallback unless explicitly permitted; direct-mode CLI/tool failures should surface rather than silently control a browser.