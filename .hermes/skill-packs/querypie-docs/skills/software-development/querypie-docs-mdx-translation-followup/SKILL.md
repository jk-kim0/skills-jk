---
name: querypie-docs-mdx-translation-followup
description: Update English and Japanese translations for querypie-docs Confluence/MDX Korean source-sync PRs, using repo-local skills and targeted skeleton checks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [querypie-docs, mdx, translation, confluence, github, pr]
---

# QueryPie docs MDX translation follow-up

Use this when an open `querypie-docs` PR contains Korean Confluence/MDX source updates and the user asks to add the corresponding English/Japanese translation updates.

## Trigger

- The user references a `querypie-docs` PR that was created from Confluence source changes, usually after running:
  - `bin/fetch_cli.py --recent --attachments`
  - `bin/convert_all.py`
- The user asks to update or translate the corresponding English/Japanese docs.

## Required skills/docs to read

Before editing, check the repo-local skill library and docs. This repo may keep the relevant translation skills under `.claude/skills/`, not only in the global Hermes skill list.

Read at minimum:

1. `.claude/skills/translation.md`
2. `.claude/skills/sync-ko-to-en-ja.md`
3. `.claude/skills/mdx-skeleton-comparison.md`
4. `.claude/skills/confluence-pr-update.md`
5. `docs/translation.md`
6. `docs/api-naming-guide.md`

If these repo-local translation skills are missing, tell the user explicitly before proceeding.

## Workflow

1. Treat the request as an existing-PR follow-up.
   - Verify the PR is open.
   - Use a fresh worktree based on the PR head branch.
   - Push back to the original PR branch.
   - Do not open a new PR unless explicitly requested.

2. Inspect the PR delta from `origin/main...HEAD`.
   - Identify changed `src/content/ko/**` files.
   - Map each Korean path to the same relative path under `src/content/en/**` and `src/content/ja/**`.

3. Translate/update EN and JA files.
   - Preserve MDX structure, blank lines, tables, code blocks, links, image paths, escaped entities, and emphasis markers.
   - Do not translate code blocks or link targets.
   - Translate frontmatter title, body text, image alt text, and captions when present.
   - For renamed or expanded release-note pages, create the EN/JA files with the same filename and frontmatter shape as KO, then update each language `_meta.ts`.
   - Leave old release-note files alone unless the PR/user explicitly removes them.

4. Verify targeted quality before commit.
   - `git diff --check`
   - grep changed EN/JA files for remaining Korean Hangul.
   - Compare line counts for newly-created translated files where KO/EN/JA should be structurally parallel.
   - Run skeleton checks from `confluence-mdx` with `target/{en,ja}/...` paths, not `../src/content/...` paths.
   - Run `bin/skeleton/cli.py --compare` and filter to touched paths to catch missing EN/JA counterparts.

5. Interpret skeleton output carefully.
   - Skeleton may report pre-existing differences or language-expression differences in unchanged sections.
   - Do not over-edit unrelated old translation text just to silence skeleton output.
   - Report any such residual skeleton diffs explicitly in the PR body/final summary.

6. Commit and push.
   - Use an `mdx:` commit prefix for `src/content/**` changes.
   - Rebase/verify against latest `origin/main` as appropriate for the PR branch.
   - Push to the existing PR branch and verify local HEAD, remote branch HEAD, and PR `headRefOid` match.

7. Refresh the PR body.
   - Mention both the original Korean Confluence sync and the EN/JA translation follow-up.
   - List language families touched.
   - Include targeted verification and note any known/residual skeleton differences.

## Pitfalls

- Do not say “no translation skill exists” until checking `.claude/skills/` in the repository.
- Do not create a separate translation PR for an open Confluence sync PR unless the user asks.
- Do not run broad local builds by default when the user prefers CI; targeted document and skeleton checks are sufficient unless explicitly requested.
- Do not copy read-file line-number prefixes into MDX files.
