# News MDX localized boilerplate sync

Use this reference when updating multilingual `src/content/news/*.mdx` entries whose company boilerplate or media contact sections must match another news PR or article.

## Pattern

1. Work in a fresh repo-root `.worktrees/<task>` checkout from latest `origin/main` unless the user explicitly wants to continue an existing PR branch.
2. Load repo-local `.agents/skills/mdx-publication-operations` and `.agents/skills/news-posting` first.
3. Identify the source article/PR and target article files for all locales.
   - News files follow `src/content/news/<id>-<slug>.{en,ko,ja}.mdx`.
   - Assets should remain route-aligned under `public/news/<id>/...`.
4. For section sync tasks, replace the target tail section from the target heading onward with the source section from the matching locale.
   - Example headings: `## QueryPie 회사소개`, `## About QueryPie`, `## QueryPieについて`.
   - If the target has older headings like `## QueryPie 소개`, `## Contact`, or `## 문의`, replace from that older heading through EOF.
5. Verify that each target locale’s final synced section exactly matches the source locale’s section after trimming trailing whitespace.
   - A small Python assertion comparing `text[text.index(heading):].rstrip()` is sufficient.
6. Commit only the changed target MDX files. Do not include the source PR’s unrelated content or assets.
7. For PR follow-up, push the branch, open a separate PR, and report mergeability/check state without waiting passively for long-running CI.

## Pitfalls

- Do not manually paraphrase boilerplate when the user asks to make it identical to another PR/article; copy section text exactly per locale and verify equality.
- Do not bundle boilerplate sync into an unrelated feature/content PR when the user asks for a new PR.
- If the source article is on an open PR branch, use its worktree or fetched branch as the source of truth, but create the new target PR from latest `origin/main`.
