# OG preview image authoring rules for corp-web-japan

Use this reference when updating or auditing repo-local MDX authoring guidance for Open Graph/Twitter preview images in `querypie/corp-web-japan`.

## Durable rule

For public MDX publication/resource families, the effective OG preview image must be a route-aligned PNG under the family asset root and must not be SVG.

Current safe authoring default in `corp-web-japan`:

- `heroImageSrc` is the authored image field used by list/card/detail metadata surfaces.
- Prefer `heroImageSrc: "/<family>/<id>/thumbnail.png"`.
- Do not add `openGraphImageSrc` unless the target loader/frontmatter contract actually supports it.

Future/loader-supported shape:

- If a family explicitly supports `openGraphImageSrc`, treat the effective preview as `openGraphImageSrc ?? heroImageSrc`.
- `openGraphImageSrc` must reference a PNG preview asset.
- `heroImageSrc` may remain a separate page/card image only when `openGraphImageSrc` supplies the PNG preview.

Locale path rule, when supported by the loader and file exists under `public/**`:

- shared path: `/news/<id>/thumbnail.png`
- locale suffix: `/news/<id>/thumbnail.ko.png`
- locale-prefixed public path: `/ko/news/<id>/thumbnail.png`

## Where to encode the rule

For repo-local skill updates, patch the common skill first:

- `.agents/skills/mdx-publication-operations/SKILL.md`

Then add one-line family reminders to every relevant wrapper so agents see the rule after loading the narrow skill:

- `.agents/skills/blog-posting/SKILL.md`
- `.agents/skills/news-posting/SKILL.md`
- `.agents/skills/whitepaper-posting/SKILL.md`
- `.agents/skills/events-posting/SKILL.md`
- `.agents/skills/use-case-posting/SKILL.md`
- `.agents/skills/aip-demo-posting/SKILL.md`
- `.agents/skills/acp-demo-posting/SKILL.md`
- `.agents/skills/introduction-deck-posting/SKILL.md`
- `.agents/skills/glossary-posting/SKILL.md`
- `.agents/skills/manuals-posting/SKILL.md`

## Porting from corp-web-app PRs

When the user asks to apply an equivalent rule from `querypie/corp-web-app`:

1. Inspect the referenced PR diff for the rule, but adapt it to `corp-web-japan` current loader support.
2. Avoid documenting unsupported frontmatter as active authoring contract.
3. If `openGraphImageSrc` does not exist in the current repo, document it only as a future/loader-supported override.
4. Keep the change in repo-local `.agents/skills/**` when the request is about agent authoring rules, not production code.
5. Use a branch worktree from latest `origin/main`, commit, push, and open/update the PR if requested or expected by repo workflow.

## Verification

For skill/documentation-only changes:

```bash
git diff --check
```

Do not run local builds/tests for documentation-only repo-local skill changes unless the user explicitly asks or the edits touch executable code.