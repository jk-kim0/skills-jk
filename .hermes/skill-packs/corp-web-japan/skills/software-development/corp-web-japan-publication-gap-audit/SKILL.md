---
name: corp-web-japan-publication-gap-audit
description: Audit missing publication IDs in corp-web-japan and decide whether each gap should become a hidden redirect record, a full local migration, a redirect-policy fix, or no action.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, publications, id-gaps, hidden-posting, redirect, corp-web-contents, vercel-logs]
---

# corp-web-japan publication ID gap audit

Use this when reviewing corp-web-japan publication/content routing and you notice missing numeric IDs in local content directories such as:
- `src/content/whitepapers/*.mdx`
- `src/content/events/*.mdx`
- `src/content/news/*.mdx`
- `src/content/blog/*.mdx`
- `src/content/demo/**`
- `src/content/use-cases/*.mdx`

## Why this skill exists

A missing ID does **not** automatically mean:
- a hidden posting should be added
- a redirect-only shadow record should be created
- local migration is missing

The correct answer depends on:
1. whether the source ever existed in `../corp-web-contents`
2. whether a Japanese (`ja`) source exists there now
3. whether production traffic still hits the missing legacy/current paths
4. whether the gap is already intentionally locked in by repo tests

In practice, the user expects this gap/source/traffic audit **before** a conclusion like “this PR is stale” or “just add hidden + redirect”.

## Core rule

Do not jump directly from “ID gap” to “create hidden posting”.

Always classify the gap first:
- `full-local-migration candidate`
- `hidden redirect record candidate`
- `legacy redirect-policy candidate`
- `separate anomaly / needs more source tracing`
- `intentional omission / no action`

## Recommended workflow

### 1. Inventory local ID gaps first

From the repo root, enumerate actual IDs and gaps per family.

Example:
```bash
python3 - <<'PY'
import os,re,glob
roots=[
 ('blog','src/content/blog'),
 ('whitepapers','src/content/whitepapers'),
 ('news','src/content/news'),
 ('events','src/content/events'),
 ('use-cases','src/content/use-cases'),
 ('demo-aip','src/content/demo/aip'),
 ('demo-acp','src/content/demo/acp'),
]
for name,root in roots:
    ids=sorted(int(os.path.splitext(os.path.basename(p))[0]) for p in glob.glob(root+'/*.mdx') if re.match(r'^\d+\.mdx$', os.path.basename(p)))
    gaps=[]
    if ids:
        gaps=sorted(set(range(min(ids), max(ids)+1))-set(ids))
    print(f'[{name}] count={len(ids)} gaps={gaps}')
PY
```

Also list actual filenames to avoid bad assumptions.

### 2. Check whether tests already encode the omission intentionally

Before deciding a gap is accidental, inspect corpus tests such as:
- `tests/whitepaper-imported-ja-corpus.test.mjs`
- `tests/events-imported-ja-corpus.test.mjs`
- family-specific imported-corpus tests

If the missing IDs are explicitly excluded from `expectedIds`, treat the omission as intentional **current behavior**, even if it may still deserve reconsideration.

Important interpretation:
- test omission means “currently expected state”
- it does **not** prove the omission is correct product policy

### 3. Investigate `../corp-web-contents` source existence

Stay grounded in the sibling repo the user named.

For each missing ID, inspect current/history paths.

Useful commands:
```bash
cd ../corp-web-contents

# broad path discovery by id
for id in 13 14; do
  git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep "/$id/" || true
done
```

Prefer narrowing by family patterns such as:
- `/white-paper/<id>/`
- `/webinars/<id>/`
- `/blog/<id>/`
- `/use-cases/<id>/`

### 4. Distinguish “source exists” from “JA migration candidate exists”

This is the critical fork.

#### A. Current canonical JA source exists in corp-web-contents
Example shape:
- `pages/features/documentation/white-paper/<id>/<slug>/ja/content.mdx`

Interpretation:
- the gap is likely a **full local migration candidate**
- do not default to a hidden redirect record first
- ask why the local corpus skipped migration of a still-existing JA source

#### B. Only EN/KO exists, but no JA canonical source exists
Example shape:
- `pages/features/demo/webinars/<id>/<slug>/en/content.mdx`
- `pages/features/demo/webinars/<id>/<slug>/ko/content.mdx`
- no `ja/content.mdx`

Interpretation:
- this is **not** a strong local Japanese migration candidate
- prefer classifying it as a **legacy redirect-policy candidate** rather than creating a local Japanese posting shell just to fill the number

### 5. Check production traffic before deciding priority

Use Vercel production logs for live evidence.

Fast existence check:
```bash
vercel logs --project corp-web-japan --environment production --since 24h --json --no-branch --limit 20
```

Then query specific suspected paths:
```bash
vercel logs --project corp-web-japan --environment production --since 30d --search '/features/documentation/white-paper/13' --json --no-branch --limit 20
vercel logs --project corp-web-japan --environment production --since 30d --search '/features/demo/webinars/7' --json --no-branch --limit 20
vercel logs --project corp-web-japan --environment production --since 30d --search '/events/6' --json --no-branch --limit 20
```

Important patterns:
- `runtime-missing-redirect` + `307` means legacy traffic still hits the path
- a direct `404` on a would-be current canonical path means the gap may already be user-visible

### 6. Classification rules

#### Class 1: full local migration candidate
Use this when:
- missing local ID exists in corp-web-contents current canonical source
- current canonical `ja/content.mdx` exists there
- legacy traffic may also exist

Typical example:
- whitepaper IDs missing locally even though `../corp-web-contents/pages/features/documentation/white-paper/<id>/.../ja/content.mdx` exists

Recommendation:
- prioritize re-evaluating why the local migration skipped this ID
- hidden redirect record is only a fallback, not the first assumption

#### Class 2: hidden redirect record candidate
Use this when:
- the gap corresponds to an old/local detail URL that should keep resolving
- local list visibility should stay off
- a stable target exists
- creating a full local migration is unnecessary or undesirable

Important note:
- choose this only after rejecting full migration as the more correct path

#### Class 3: legacy redirect-policy candidate
Use this when:
- historical source exists
- production legacy path traffic exists
- but there is no current Japanese canonical source to migrate

Typical example:
- old webinar IDs with EN/KO only, no JA source, but bots/users still hit `/features/demo/webinars/<id>/...`

Recommendation:
- review allowlist / redirect behavior first
- do not force-fit a local Japanese posting purely for numeric continuity

#### Class 4: separate anomaly
Use this when:
- production logs show a hit to a current-style path such as `/events/6/<slug>`
- but the slug does not match the obvious legacy source lineage
- and corp-web-contents history does not immediately explain it

Recommendation:
- trace the slug lineage separately before proposing hidden/redirect/migration

#### Class 5: intentional omission / no action for now
Use this when:
- repo tests intentionally exclude the ID
- no corp-web-contents source exists
- no production traffic exists

### 7. Report format

For each family, summarize like this:

```text
Family: whitepapers
Gap IDs: 13, 14

ID 13
- corp-web-contents canonical JA source: yes
- production traffic evidence: yes (`/features/documentation/white-paper/13/...` 307)
- classification: full local migration candidate
- note: do not jump straight to hidden redirect
```

## Practical findings that prompted this skill

### Whitepaper gap pattern
- local `src/content/whitepapers` can omit IDs that still exist in `../corp-web-contents/pages/features/documentation/white-paper/<id>/.../ja/content.mdx`
- if production logs also show requests to those legacy feature paths, the omission deserves migration review, not an automatic hidden shadow record

### Event/webinar gap pattern
- local `src/content/events` can intentionally omit webinar IDs that exist in corp-web-contents only as EN/KO source without `ja/content.mdx`
- if production logs show `runtime-missing-redirect` traffic to `/features/demo/webinars/<id>/...`, that usually points to redirect-policy work rather than local Japanese MDX migration

### Test-encoded omission pattern
- imported-corpus tests may explicitly freeze current omitted IDs in `expectedIds`
- this means the gap is deliberate in current repo state, but not necessarily the correct end state

## Pitfalls

- Assuming every gap should be filled with a local file
- Assuming every missing ID should be hidden + redirect
- Ignoring corpus tests that intentionally freeze omitted IDs
- Treating historical source existence as enough for local migration without checking JA source availability
- Treating legacy-path traffic as proof that a local canonical page is required; often it only proves redirect-policy relevance
- Reviewing a publication/routing PR only for stale/mergeable status and missing the more important hidden/redirect/gap question

## Done criteria

A gap audit is complete when you can answer, for each missing ID:
- did a source exist in corp-web-contents?
- does a canonical JA source exist there now?
- is there production traffic evidence?
- is the omission explicitly encoded in tests?
- should this become full migration, hidden redirect, redirect-only policy work, or no action?
