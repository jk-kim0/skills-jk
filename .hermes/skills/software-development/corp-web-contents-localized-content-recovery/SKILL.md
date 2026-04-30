---
name: corp-web-contents-localized-content-recovery
description: Recover missing localized content in corp-web-contents by using commit history to distinguish true deletions from missing translations, then restore canonical-path files instead of piling on redirects when possible.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-contents, localization, git-history, content-recovery, redirects]
---

# corp-web-contents localized content recovery

Use this when the user says a localized page is missing, showing the wrong language, or asks to restore deleted/deprecated language content in `corp-web-contents`.

## Why this skill exists

In `corp-web-contents`, a missing localized page can mean very different things:
- the current canonical path exists but the `ko` file contains English copy
- the canonical path has `en/ja` but no `ko` file at all
- an old path was deleted during route migration and only redirects remain (or should remain)
- the task actually belongs to a different repo, but the user expects work only in `corp-web-contents`

Do not guess. Use commit history first.

## Preferred method learned from experience

If the user asks for restoration, prefer restoring or creating files at the current canonical URI path.
Do **not** default to adding more redirect rules when the canonical path can hold the content directly.
Only use redirects when the real issue is legacy-route recovery and the user is okay with that approach.

## Workflow

1. Confirm repo scope first
- Stay inside `corp-web-contents` unless the user explicitly asks for another repo.
- Do not broaden into `corp-web-app` or `querypie-docs` just because `/docs` or public routing seems related.

2. Check the current canonical path
- Inspect whether the target route already has:
  - `.../ko/content.mdx`
  - `.../ko/meta.json` if applicable
- Compare sibling locales (`en`, `ja`) under the same canonical directory.

3. Use commit log before making conclusions
- For a specific file:
  - `git log --follow --oneline -- path/to/file`
  - `git log -S 'distinctive text' --oneline -- path/to/file`
  - `git show <commit>^:path/to/file`
- For migrations/deletions in a subtree:
  - `git log --all --diff-filter=D --name-status --format='COMMIT %H %ad %s' --date=short -- pages/...`
- Goal: classify each case as one of:
  - `wrong-language overwrite`
  - `deleted during migration`
  - `never had ko content`
  - `legacy route removed but canonical replacement exists`

4. Decide recovery mode

### A. Canonical file exists but content is wrong-language
Restore the pre-overwrite Korean copy from the parent of the bad commit.
Then optionally translate any remaining English UI labels if the page would otherwise feel mixed-language.

Typical example:
- `pages/company/about-us/ko/content.mdx`
- `pages/company/contact-us/ko/content.mdx`
were overwritten with English copy in a later commit; restore Korean baseline from `git show <bad_commit>^:...`.

### B. Canonical path has en/ja but no ko file, and git history shows no prior ko file
This is **not** a restoration. It is a new translation/content-creation task.
Tell the user clearly that there is nothing to restore from history for that slug.
List the missing canonical `ko/content.mdx` paths.

### C. Old route deleted during migration, canonical replacement exists
If the user wants the content visible at the current route, restore/create content at the current canonical path, not at the deleted route.
Only add or adjust redirects if the user specifically wants legacy URLs preserved.

5. Verify before finishing
- Recheck affected files with `read_file`.
- Re-run `git diff` on the exact files changed.
- If editing YAML redirects, parse-check with Python `yaml.safe_load`.
- If asked for git-complete work, commit/push and open a PR.

## Practical checks for `/ko/features/demo`

When the user says content under `/ko/features/demo` is not Korean:
- First inspect `pages/features/demo/ko/content.mdx` itself; it may exist but contain English copy.
- Then enumerate canonical subroutes under `pages/features/demo` where `en`/`ja` exist but `ko` is missing.
- Use commit log to distinguish:
  - migrated old tutorial/webinar/customer-success entries that truly had old `ko` pages
  - newer `use-cases`, `aip-features`, or webinar slugs that never had `ko` files and require new authoring

## Pitfalls

- Do not confuse “missing Korean on the site” with “deleted Korean file in git history”. Many canonical paths simply never had `ko` content.
- For older blog content, do not check only the current canonical path. Legacy localized blog files may exist under `pages/resources/discover/blog/**/<locale>/content.mdx` even when the current canonical path `pages/features/documentation/blog/**/<locale>/content.mdx` has no history. Search both path families before concluding that a localized document never existed.
- Important audit distinction learned from blog recovery work:
  - `git log --all --name-only --format= -- . | grep '/<id>/'` proves that files related to that posting ID existed somewhere in history.
  - It does **not** prove that a localized body file like `ja/content.mdx` or `ko/content.mdx` existed.
  - Meta-only results (`ja/meta.json`, `ko/meta.json`) are common and must not be mistaken for localized MDX body content.
- When the user believes a localized MDX body probably existed, do not stop at `git log --name-only`. Use `git rev-list --all --objects` to inspect every reachable historical path object and verify whether any `/<id>/.../<locale>/*.mdx` path ever existed at all.
  - Recommended verification pattern:
    ```bash
    git rev-list --all --objects | grep '/<id>/' | grep '/ja/' | grep '\.mdx$'
    git rev-list --all --objects | grep '/<id>/' | grep '/ko/' | grep '\.mdx$'
    ```
  - This is stronger than commit-path grep because it answers whether the file path ever existed in any reachable tree, not just whether nearby files changed in a commit.
- Interpretation rule:
  - If you find EN `content.mdx` plus JA/KO `meta.json`, but `rev-list --all --objects` finds no JA/KO `.mdx` paths, conclude that localized metadata existed but localized MDX body files did not.
- Important blog-locale completion lesson:
  - When the user wants all missing locale bodies filled on the current canonical blog paths, do not assume English is always the only valid source-of-truth.
  - First inspect the current canonical sibling locale files under `pages/features/documentation/blog/<id>/<slug>/`.
  - If only one canonical locale body currently exists (for example JA-only press/news content), use that existing canonical body as the translation source for the missing locales.
  - If multiple canonical locale bodies exist but diverge structurally or editorially, pick one primary canonical source-of-truth for structure and content order (usually the current EN file unless the user says otherwise), and use the other locale only as tone/reference.
  - Do not try to merge mismatched locale variants into a synthetic hybrid article.
- Important `meta.json` reliability lesson:
  - Historical locale `meta.json` files in old `pages/resources/discover/blog/**` trees can be absent, stale, or clearly mismatched to the current canonical article.
  - Use them only as weak supporting evidence for title/description/keywords, never as authoritative proof of a localized body.
  - If current canonical frontmatter and historical locale `meta.json` disagree, prefer the current canonical article body/frontmatter for translation tasks unless the user explicitly asks for legacy parity.
- Do not assume redirect repair is the best restoration method; the user may explicitly dislike redirect complexity.

  - some JA/KO `meta.json` files may simply duplicate EN text, or may even contain stale metadata copied from a different blog post.
  - therefore, when creating missing canonical localized MDX files on `pages/features/documentation/blog/**`, treat current EN `content.mdx` as the primary source of truth.
  - use historical locale `meta.json` only as supplementary hints for title/description/keywords/images, and only reuse those values when they actually match the current article.
  - if legacy `meta.json` conflicts with the current EN canonical MDX topic, prefer the canonical EN MDX and translate from it directly.
- Do not assume redirect repair is the best restoration method; the user may explicitly dislike redirect complexity.
- Do not inspect or change a different repo unless the user asks. Public routing can tempt you into `corp-web-app`, but content recovery may still belong only to `corp-web-contents`.
- `git log --follow` only accepts one pathspec; inspect files individually when needed.

## Good final output structure

1. What was found in commit history
2. Which files are true restores vs which are missing new translations
3. Exact files changed
4. PR URL if created
