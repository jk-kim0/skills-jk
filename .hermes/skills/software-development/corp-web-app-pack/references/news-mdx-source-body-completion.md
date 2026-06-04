# News MDX source-body completion

Use this when asked to enrich `src/content/news/*.mdx` from linked media coverage, especially follow-up work after a PR migrated live news-list snippets into MDX.

## Workflow

1. Identify the exact MDX files in scope.
   - For a PR follow-up, prefer GitHub file metadata over guessing from the working tree:
     - `gh api repos/querypie/corp-web-app/pulls/<pr>/files --paginate --jq '.[] | select(.status=="added" and (.filename|endswith(".mdx"))) | .filename'`
   - If the PR is already merged and its branch is gone, create a fresh follow-up branch/worktree from latest `origin/main` instead of editing the merged branch.
2. Read each MDX file and extract the quoted `원문 기사` URL.
3. Visit/parses each source article and compare the parsed title/body against the MDX title/description.
   - Korean legacy news sites may use EUC-KR; detect `<meta charset>` and decode accordingly.
   - For Boannews articles, `div[itemprop="articleBody"]` is usually a good body selector, and article IDs near the target date can be probed when an existing link appears mismatched.
   - For WordPress-based Byline Network, a normal curl/Python user agent may receive 403; retry with a browser-like User-Agent plus `Accept-Language` and `Referer`.
4. If a linked source URL is wrong, correct it as part of the content fix and mention it in the PR body.
5. Enrich the MDX body as a faithful rewritten article summary, not as a verbatim long-form copy of the external article.
   - Preserve factual coverage: program names, dates, selectors/participants, product names, customer/investor names when relevant, quotes as paraphrased attribution, and concrete outcomes.
   - Avoid copying long stretches of journalist-authored prose. Keep the original source link visible.
6. Verify minimally:
   - frontmatter/body delimiter structure is intact,
   - each target still has `> 원문 기사:`,
   - body length/paragraph count increased enough to show meaningful enrichment.

## Pitfalls

- Do not fulfill “copy the full article body” literally for external media coverage. Treat it as a request for comprehensive source-based enrichment, and write a detailed original paraphrase instead.
- Do not trust migrated live-list links blindly; list snippets can contain duplicated URLs. In one observed case, a Kangwon National University training item pointed at the ISEC article and needed correction from Boannews `idx=133355` to the actual article `idx=132142`.
- Do not start local dev servers for this content-only work unless explicitly requested. A source/structure check is normally sufficient before commit/push.
