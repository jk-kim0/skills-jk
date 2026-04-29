---
name: corp-web-japan-blog-mdx-migration
description: Migrate Japanese blog MDX posts from corp-web-contents into corp-web-japan's current local blog publication pipeline, including frontmatter normalization, asset relocation, and CI-safe MDX cleanup.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-japan blog MDX migration

Use this when the task is to add or bulk-migrate Japanese blog MDX posts into `corp-web-japan`.

## Critical workflow gate

For this user and this repo, do **not** plan from memory.
Before editing:

1. Update local `main` to latest `origin/main`
2. Read recent relevant commit log on latest `main`
3. Inspect the current blog implementation files on latest `main`
4. Only then create a fresh worktree/branch

Minimum commands:

```bash
git fetch origin main --quiet
git checkout main
git pull --ff-only origin main
git log --oneline --decorate -n 20 origin/main -- src/app/blog src/content/blog src/lib/publications tests
git show origin/main:src/app/blog/page.tsx | sed -n '1,220p'
git show origin/main:src/app/blog/[id]/[slug]/page.tsx | sed -n '1,260p'
git show origin/main:src/lib/publications/blog-publication-records.ts | sed -n '1,260p'
git show origin/main:src/lib/publications/get-publication-post.ts | sed -n '1,260p'
```

## Source and target

Primary source:
- `../corp-web-contents/pages/features/documentation/blog/<id>/<slug>/ja/content.mdx`
- `../corp-web-contents/public/blog/*`
- `../corp-web-contents/public/news/*`

Reference source:
- `../corp-web-v2/src/content/mdx/blog/<id>/ja.mdx`
- `../corp-web-v2/public/blog/<id>/*`

Target repo:
- `corp-web-japan`

## Preflight locale audit before editing

Before creating or translating a supposedly missing local blog post, first confirm two separate facts on latest `main`:

1. whether the post ID already exists in local `src/content/blog/*.mdx`
2. which upstream locales actually exist under `../corp-web-contents/pages/features/documentation/blog/<id>/<slug>/{en,ja,ko}/content.mdx`

Why this matters:
- a user may refer to an upstream blog ID that is not yet present in the local `corp-web-japan` blog set
- some upstream posts do not have all three locales; do not assume `en/ja/ko` always exist
- if you skip this audit, you can start translation work for a post that is not part of the current local blog inventory or misreport a locale as "missing" when the real issue is that the post itself is not locally migrated yet

Recommended audit steps:

```bash
# confirm main HEAD
git fetch origin main --quiet
git rev-parse origin/main
git rev-parse main

# list local blog IDs on main
find src/content/blog -maxdepth 1 -name '*.mdx' | sort

# inspect the specific upstream post directory and available locales
find ../corp-web-contents/pages/features/documentation/blog/<id> -maxdepth 3 -type f | sort
```

If you need an exact 1..N completeness audit, use a small script that:
- reads local `src/content/blog/<id>.mdx` files from `main`
- extracts the local `slug`
- checks upstream `en/ja/ko` existence for that ID
- reports both:
  - IDs absent from the local repo
  - IDs present locally but missing one or more upstream locales

Practical lesson captured from real use:
- when auditing IDs `1..24` on `corp-web-japan` main HEAD, the useful result was not just "which locales are missing" but also "which IDs are not present locally at all"
- treat those as different categories in your report

## Current target format on latest main

Local blog pipeline expects one file per post under:
- `src/content/blog/<id>.mdx`

Required frontmatter shape:

```yaml
---
id: "21"
slug: "why-we-need-ai-red-teaming"
title: "..."
description: "..."
date: "2025年6月9日"
heroImageSrc: "/blog/21/thumbnail.png"
author: "kenny"   # optional
relatedIds:
  - "20"
  - "17"
  - "16"
---
```

Important:
- Use `id`, not directory name, as the lookup key
- Use `slug` for canonical detail routing
- Use Japanese date strings like `2025年6月9日`
- `relatedIds` should include only local blog post IDs, not legacy URLs

## Where assets should live

Preferred path learned from review follow-up:
- `public/blog/<id>/thumbnail.png`
- `public/blog/<id>/<inline-image>.png`

Do **not** keep migrated blog assets under `public/assets/image/blog/<id>/...` for this workflow.
If you initially copied them there, move them to `public/blog/<id>/...` and update MDX/frontmatter references.

MDX body references should use:
- `filepath="public/blog/<id>/..."`

Frontmatter hero image should use:
- `heroImageSrc: "/blog/<id>/thumbnail.png"`

## Migration procedure

### 1. Create a fresh worktree from latest main

Use a flat worktree directory name, not one derived mechanically from a branch name with slashes.

Example:

```bash
git worktree add .worktrees/blog-mdx-ja-all -b feat/blog-mdx-ja-all main
```

Then verify it is a real linked worktree:

```bash
git worktree list --porcelain
git -C .worktrees/blog-mdx-ja-all branch --show-current
git -C .worktrees/blog-mdx-ja-all rev-parse --show-toplevel
ls -la .worktrees/blog-mdx-ja-all | sed -n '1,20p'
```

If the directory exists but is not listed by `git worktree list`, remove it and recreate it properly.

### 2. Count the source vs target set

Typical audit:

```bash
find ../corp-web-contents/pages/features/documentation/blog -path '*/ja/content.mdx' | wc -l
find src/content/blog -maxdepth 1 -name '*.mdx' | wc -l
```

In one real case:
- source JA posts: 23
- target local posts on latest main before migration: 6

Important follow-up lesson:
- a JA-only count can undercount the full source universe if some posts exist only in `ko` or `en`
- before concluding migration is complete, inventory the post set by `id/slug` across all locales, then decide the source fallback per post
- practical fallback used successfully here:
  - prefer `ja`
  - if `ja` is missing, use `ko`
  - if both `ja` and `ko` are missing, use `en`
- in one real audit, the blog universe was:
  - 23 posts with `ja`
  - plus 6 additional posts without `ja`
  - total migrated local blog set after fallback migration: 29 posts

A good inventory script should emit, per `id/slug`:
- available locales
- chosen source locale
- source path
- title/description/author for parity fixture generation

### 3. Normalize frontmatter

From source frontmatter, map:
- `title` -> `title`
- `description` -> `description`
- `date` -> convert `YYYY-MM-DD` to `YYYY年M月D日` if needed
- `author` -> preserve if present
- `relatedPosts` -> convert to `relatedIds`
- source path slug -> `slug`
- thumbnail/news image -> `heroImageSrc: "/blog/<id>/thumbnail.png"`

Ignore source-only keys that latest main does not use, such as:
- `layout`
- `category`
- `ogImage`
- `keywords`

unless the target implementation is later expanded to use them.

Important follow-up lesson for fallback migrations:
- when the local target is intended as a temporary staging copy before later Japanese translation, it is acceptable to migrate a `ko` or `en` body into the local Japanese site pipeline
- keep the local route/id/slug stable, but treat `title` and `description` as later-translatable content rather than immutable source-of-truth metadata
- if you add a parity fixture for fallback migrations, do not require `title/description` equality for posts whose chosen source locale is not `ja`; otherwise later local translation work will be blocked by the test
- a practical test contract that worked well:
  - require full `id/slug/author` coverage for every post
  - require `title/description` parity only for posts whose fixture `sourceLocale` is `ja`
  - allow fallback-sourced posts (`ko`/`en`) to diverge locally after translation

### 4. Normalize blog and whitepaper links inside the body

Blog links that resolve to local migrated content should become:
- `/blog/<id>/<slug>`

Examples to rewrite:
- `https://www.querypie.ai/ja/features/documentation/blog/<id>/<slug>`
- `https://www.querypie.com/ja/features/documentation/blog/<id>/<slug>`
- `/ja/features/documentation/blog/<id>/<slug>`
- `/features/documentation/blog/<id>/<slug>`
- `/ja/blog/<id>/<slug>`

Whitepaper links:
- if the whitepaper already exists locally in `src/content/whitepapers/<id>.mdx`, rewrite to `/whitepapers/<id>/<slug>`
- otherwise keep an external `https://www.querypie.com/ja/...` URL

Important legacy-path recovery lesson:
- when trying to discover whether old localized MDX existed, do not inspect only the current canonical path under `pages/features/documentation/blog/**`
- use the posting ID and search all historical path families that may have contained the blog body, for example:
  - `pages/resources/discover/blog/<id>/<locale>/content.mdx`
  - `pages/resources/discover/blog/<id>/<slug>/<locale>/content.mdx`
  - `pages/resources/learn/documentation/blog/<id>/<slug>/<locale>/content.mdx`
  - `page-archives/discover/blog/<id>/<slug>/<locale>/content.mdx`
- practical command:

```bash
git log --all --name-only --format= -- . | grep -i 'blog' | grep '/<id>/' | sed '/^$/d' | sort -u
```

Why this matters:
- a current canonical path may have no `ja/content.mdx` or `ko/content.mdx` history, while an older path family still proves that localized body content existed
- the legacy path scan can reveal whether only `meta.json` existed for a locale, or whether a full localized `content.mdx` body was actually present

### 5. Copy and rename assets

Typical source asset patterns:
- `public/blog/b-thumb-<id>.png`
- `public/blog/blog<id>-image-<n>.png`
- `public/news/news-20.png`
- `public/news/news-21.png`

Copy into:
- `public/blog/<id>/thumbnail.png`
- `public/blog/<id>/<original-inline-name>.png`

For press-release-style posts using `news-20.png` or `news-21.png` as hero images, still store them as:
- `public/blog/<id>/thumbnail.png`

### 6. Remove unsupported MDX components

Latest main renderer supports these custom components:
- `Table`
- `Box`
- `ButtonLink`
- `ArticleFileImage`
- `InfoNote`
- `GatingCut`
- `ArticleGatingForm`

Real migration failures came from unsupported source components such as:
- `Youtube`
- `SplitView`
- `Link`
- `InlineLink`

Fixes used successfully:
- Replace `<Youtube ... />` with a raw `<iframe ...></iframe>` block
- Replace `SplitView` layouts with sequential `Box` + `ArticleFileImage` blocks
- Replace `Link` / `InlineLink` JSX with normal markdown links

Before pushing, scan for unsupported capitalized tags:

```bash
python3 - <<'PY'
from pathlib import Path
import re
allowed={'Table','Box','ButtonLink','ArticleFileImage','InfoNote','GatingCut','ArticleGatingForm'}
base=Path('src/content/blog')
found={}
for p in sorted(base.glob('*.mdx')):
    text=p.read_text()
    tags=set(re.findall(r'<([A-Z][A-Za-z0-9]*)\b', text))
    bad=sorted(t for t in tags if t not in allowed)
    if bad:
        found[p.name]=bad
print(found)
PY
```

Expected clean result:
- `{}`

### 7. Verify no stale asset paths remain

Search for old path patterns:

```bash
rg -n 'public/assets/image/blog|/assets/image/blog/' src/content/blog || true
```

Verify all asset refs exist:

```bash
python3 - <<'PY'
from pathlib import Path
import re
base=Path('src/content/blog')
missing=[]
for p in sorted(base.glob('*.mdx')):
    text=p.read_text()
    hero=re.search(r'^heroImageSrc:\s*"([^"]+)"', text, re.M)
    if hero and not Path('public'+hero.group(1)).exists():
        missing.append((p.name, hero.group(1)))
    for ref in re.findall(r'public/blog/[^\s)\"\']+', text):
        if not Path(ref).exists():
            missing.append((p.name, ref))
print(missing)
PY
```

Expected clean result:
- `[]`

### 8. Add a lightweight parity regression test

Do not stop at a raw file-count check when the task is "did we migrate everything?".
A better regression test is:
- compare the local migrated set against a checked-in parity fixture that was generated from `../corp-web-contents`
- assert parity for at least `id`, `slug`, `title`, `description`, and `author`

Recommended files:
- `tests/blog-migrated-ja-source-parity.test.mjs`
- `tests/fixtures/blog-migrated-ja-source-parity.json`

Important CI lesson:
- GitHub Actions / CI will not have `../corp-web-contents` checked out by default
- therefore, the committed regression test must NOT depend on reading `../corp-web-contents` at test runtime
- instead:
  1. run a one-time local audit against `../corp-web-contents`
  2. generate a checked-in JSON fixture snapshot from that source set
  3. make CI compare local `src/content/blog/*.mdx` against the checked-in fixture only

This keeps the PR self-contained while still locking in migration completeness.

Suggested fixture generation pattern:
- read every `../corp-web-contents/pages/features/documentation/blog/*/*/ja/content.mdx`
- parse frontmatter with the same YAML parser family used by the repo (`yaml`), not a brittle line-by-line parser
- normalize empty authors to `null`
- sort by numeric `id`
- write `tests/fixtures/blog-migrated-ja-source-parity.json`

Suggested parity test behavior:
- parse local `src/content/blog/<id>.mdx`
- compare the local normalized array to the checked-in fixture
- assert count equality and full object equality for `id/slug/title/description/author`

Why this matters:
- a count-only test can miss wrong slug/title mappings
- CI-inaccessible external repos will break naive source-dependent tests
- simple handwritten frontmatter parsing can mis-handle quotes, blanks, and arrays; use YAML parsing instead

### 8a. When JA is missing, support `ja -> ko -> en` fallback migration

A later follow-up established an additional reusable migration mode:
- if a blog post has `ja`, migrate `ja`
- if `ja` is missing but `ko` exists, migrate `ko`
- if both `ja` and `ko` are missing, migrate `en`

This is useful when the user wants canonical local blog coverage now and plans to translate the remaining posts into Japanese later.

Recommended audit flow for this mode:
1. enumerate all blog post id/slug directories under `../corp-web-contents/pages/features/documentation/blog`
2. record available locales per post
3. choose source locale with priority `ja -> ko -> en`
4. update the checked-in parity fixture to include all current blog posts plus a `sourceLocale` field for auditability

Example fixture fields:
- `id`
- `slug`
- `title`
- `description`
- `author`
- `sourceLocale`

Then make the parity test compare local content against that fixture while ignoring `sourceLocale` in the equality assertion unless you explicitly want the test to lock in the source-locale contract as well.

### 8b. Keep the count test aligned with fallback coverage

If the repo still has a simpler file-count regression such as `tests/blog-migrated-ja-content-count.test.mjs`, update it whenever fallback posts are added.

Real failure encountered:
- parity fixture/test was updated from 23 JA-only posts to 29 posts using `ja -> ko -> en` fallback
- CI still failed because the older count test continued asserting 23 files

Therefore, after adding fallback posts:
- update the count test description so it no longer says "Japanese blog MDX posts" only
- update the expected total file count
- update the explicit filename list to include the newly migrated ids

### 8c. Common fallback-migration content fixes

When migrating non-JA source posts into the local blog pipeline:
- normalize frontmatter into the local shape (`id`, `slug`, `title`, `description`, `date`, `heroImageSrc`, optional `author`, `relatedIds`)
- convert `YYYY-MM-DD` dates to the current local display format like `YYYY年M月D日`
- copy hero and inline assets into `public/blog/<id>/...` and rewrite MDX `filepath=` references accordingly
- convert unsupported JSX link components such as `<Link ...>...</Link>` into standard markdown links if the current local MDX renderer does not support them
- rewrite legacy internal blog hrefs like `/features/documentation/blog/<id>/<slug>` to local `/blog/<id>/<slug>` URLs where applicable

### 9. Rebase before push

Do not skip this.

```bash
git fetch origin main --quiet
git rebase origin/main
```

If there are working tree changes, commit first, then rebase.
Do not claim compliance with the latest-main rule unless this final rebase check was actually done.

### 10. Push and monitor CI

Push to the existing PR branch if this is PR follow-up work.
Then check:

```bash
env -u GITHUB_TOKEN gh pr checks <pr-number>
env -u GITHUB_TOKEN gh run list --branch <branch> --limit 10
```

If Preview/CI fails, inspect logs immediately.

## Known failure mode and fix

Real Vercel build failure encountered:
- prerender failed on `/blog/21/why-we-need-ai-red-teaming`
- error: `Expected component 'Youtube' to be defined`

Root cause:
- source MDX used unsupported `Youtube` component

Fix:
- replace the `Youtube` JSX node with a raw iframe block and push again
- then rescan all migrated MDX for any other unsupported custom components

## Success criteria

- local `main` updated before starting
- latest `main` blog implementation reviewed before planning
- fresh valid worktree created from latest `main`
- all Japanese source blog MDX posts migrated
- target files use current frontmatter shape
- blog asset paths use `public/blog/<id>/...`
- no unsupported MDX custom components remain
- no stale asset paths remain
- final branch rebased onto latest `origin/main`
- PR updated and CI/Preview pass
