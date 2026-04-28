---
name: corp-web-japan-publication-author-image-paths
description: Diagnose and fix broken author profile images in corp-web-japan publication detail pages by reconciling author registry paths with actual public asset locations.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, publications, authors, images, nextjs, debugging]
    related_skills: [corp-web-japan-origin-main-worktree-safety, github-pr-workflow, systematic-debugging, test-driven-development]
---

# corp-web-japan publication author image path debugging

Use this when blog/whitepaper publication author boxes render but the profile image is broken on stage/prod.

## Symptom pattern

Typical report:
- author box is visible on `/blog/:id/:slug` or `/whitepapers/:id/:slug`
- image area is broken or blank
- the rest of the author metadata (name/role/bio/link) renders normally

Example investigation target:
- `https://stage.querypie.ai/whitepapers/22/your-architect-vs-ai-agents`

## Root cause found in this repo

Publication author data flows through:
- `src/content/authors/ja.yaml`
- `src/lib/authors/resolve-authors.ts`
- `src/lib/publications/get-publication-post.ts`
- `src/components/AuthorBox.tsx`

Important repo-specific mismatch:
- author registry entries commonly use `profileImage: crew/<file>`
- publication resolver previously normalized that to `/crew/<file>`
- actual static files live under `public/crew/authors/<file>`
- result: stage/prod requests like `/crew/kenny.png` return 404, while `/crew/authors/kenny.png` returns 200

## Investigation workflow

1. Confirm latest base and work in a fresh worktree from `origin/main`.
2. Inspect these files first:
   - `src/components/AuthorBox.tsx`
   - `src/lib/authors/resolve-authors.ts`
   - `src/lib/publications/get-publication-post.ts`
   - `src/content/authors/ja.yaml`
3. Check actual asset locations under:
   - `public/crew/authors/`
4. Verify the live failing path directly.

Useful checks:

```bash
# Find author-related code/search hits
# use search_files on: AuthorBox, profileImage, profileImageSrc, avatarSrc

# Verify live asset behavior
python3 - <<'PY'
import requests
for url in [
  'https://stage.querypie.ai/crew/kenny.png',
  'https://stage.querypie.ai/crew/authors/kenny.png',
]:
    r = requests.get(url, timeout=20)
    print(url, r.status_code, r.headers.get('content-type'))
PY
```

Browser-side confirmation:
- inspect the rendered `img` or Next image URL
- if it contains `url=%2Fcrew%2F<file>` while the real asset is under `/crew/authors/<file>`, the root cause is confirmed

## Fix pattern

Prefer a central fix in `src/lib/authors/resolve-authors.ts` instead of editing many YAML rows.

### Variant A: assets still live under `public/crew/authors/`

Recommended normalization logic:
- strip leading `public/` and `/`
- if path already starts with `crew/authors/`, keep it as-is
- if path starts with `crew/`, rewrite it to `/crew/authors/<rest>`
- otherwise keep generic `/<normalized>` behavior

Reference implementation shape:

```ts
function normalizeProfileImageSrc(profileImage?: string): string | undefined {
  if (!profileImage) return undefined;

  const normalized = profileImage.replace(/^public\//, "").replace(/^\/+/, "");
  if (!normalized) return undefined;
  if (normalized.startsWith("crew/authors/")) return `/${normalized}`;
  if (normalized.startsWith("crew/")) {
    return `/crew/authors/${normalized.slice("crew/".length)}`;
  }

  return `/${normalized}`;
}
```

Why this is preferred:
- fixes blog and whitepaper publication author boxes together
- preserves existing YAML content shape
- avoids noisy content-wide edits
- remains compatible with non-crew assets such as `public/querypie-company/...`

### Variant B: author assets are later flattened into `public/crew/`

If the repo is refactored so former author assets move out of `public/crew/authors/` into `public/crew/`, update the shared resolver instead of mass-editing YAML.

Recommended normalization logic after flattening:
- if path starts with `crew/authors/`, rewrite to `/crew/<rest>`
- if path starts with `crew/`, keep it as `/crew/<rest>`
- otherwise keep generic `/<normalized>` behavior

Reference implementation shape:

```ts
function normalizeProfileImageSrc(profileImage?: string): string | undefined {
  if (!profileImage) return undefined;

  const normalized = profileImage.replace(/^public\//, "").replace(/^\/+/, "");
  if (!normalized) return undefined;
  if (normalized.startsWith("crew/authors/")) {
    return `/crew/${normalized.slice("crew/authors/".length)}`;
  }
  if (normalized.startsWith("crew/")) {
    return `/${normalized}`;
  }

  return `/${normalized}`;
}
```

Also update any fallback avatar in `src/lib/publications/get-publication-post.ts`, for example:
- `/crew/authors/brant.png` -> `/crew/brant.png`

### Collision handling when flattening `public/crew/authors/` into `public/crew/`

Before moving files, check for filename collisions between existing `public/crew/*` files and `public/crew/authors/*` files.

Use a quick inventory like:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path('public/crew')
auth = root / 'authors'
root_files = {p.name for p in root.iterdir() if p.is_file()}
auth_files = {p.name for p in auth.iterdir() if p.is_file()}
for name in sorted(root_files & auth_files):
    print(name)
PY
```

If collisions exist:
1. verify whether the files are byte-identical (`shasum -a 256`)
2. if identical, keep one copy and remove the duplicate
3. if different, search actual repo usage before overwriting anything
4. only replace the root file when evidence shows the author-path meaning should win

Practical repo finding:
- `noah.png` existed in both locations and the files differed
- there was no direct repo usage of the existing root `public/crew/noah.png`
- the author registry did use `profileImage: crew/noah.png`
- therefore the safe flattening choice was to let the author image version become the canonical `public/crew/noah.png`

### Existing PR follow-up rule

If the user asks to include this work in an already-open PR, do not create a new branch/PR.
Use a fresh worktree from the existing PR branch and push back to that same head branch.
This is especially important for asset-path cleanup follow-ups that the user wants folded into the original author-image PR.

## Regression test approach

Add a focused Node test under `tests/`.

Recommended assertions:
1. `resolve-authors.ts` contains the `crew/` -> `/crew/authors/` normalization branch
2. every `profileImage: crew/...` entry in `src/content/authors/ja.yaml` has a matching file in `public/crew/authors/...`

Practical note:
- keep the test dependency-light; simple regex parsing of YAML text is enough
- this avoids failures in fresh worktrees if package resolution is incomplete

## Minimal verification

Run at least:

```bash
node --test tests/author-profile-image-paths.test.mjs
```

If the user wants CI-first verification, push the branch and monitor PR checks instead of spending time on a full local build.

## Pitfalls

- assuming `/public/...` maps directly without checking the final public URL
- editing all YAML entries instead of fixing the shared resolver
- checking only one content family; the same resolver serves both blog and whitepaper publications
- writing a test that imports extra project deps when a simple file-content test is sufficient

## Done criteria

- broken author image path reproduced and traced to resolver output
- central resolver fix implemented
- regression test added and passing
- branch pushed and Draft PR opened when requested
