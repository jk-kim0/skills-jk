---
name: search-console-noindex-main-vs-live
description: Investigate Google Search Console "Excluded by noindex tag" reports by comparing the exact live HTML served in production against the latest origin/main code, then separate code bugs from deployment drift.
---

# Search Console noindex: main vs live investigation

## When to use
- Search Console reports `Excluded by 'noindex' tag`
- The user wants the cause investigated against the current main branch, not a stale local checkout
- The site is deployed on Vercel / Next.js or a similar SSR/static stack
- You need to distinguish:
  1. current code still emits noindex
  2. main is already fixed but production still serves old HTML
  3. Google is just behind on recrawl

## Why this skill exists
A common failure mode is to read a stale local branch, conclude the code is wrong, and miss that `origin/main` already fixed the issue. Another common failure mode is to see Search Console still complaining and assume the fix failed, even though the real problem is that production is still serving an older deployment.

This workflow forces three-way verification:
- Search Console evidence
- latest `origin/main` source of truth
- actual live HTML response

## Required investigation order

### 1. Verify the exact Search Console issue page
If the user provides a Search Console drilldown URL, inspect that exact page first.
Capture:
- issue label (`Excluded by ‘noindex’ tag` vs other exclusions)
- affected page count
- example URLs
- last update / validation state if visible

Browser-based extraction is preferred when the user already has Search Console open.

### 2. Check live production HTML directly
For several affected example URLs, fetch the real production page and inspect:
- HTTP status
- `X-Robots-Tag` header
- HTML `<meta name="robots" ...>`
- canonical URL
- whether the URL is included in `sitemap.xml`

Do not stop at one sample if the issue lists many URLs. Confirm the pattern across multiple examples.

Useful shell pattern:
```bash
python3 - <<'PY'
import requests, re
url='https://example.com/path'
r=requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=20)
html=r.text
m=re.search(r'<meta[^>]+name="robots"[^>]+content="([^"]+)"', html, re.I)
print('status=', r.status_code)
print('xrobots=', r.headers.get('X-Robots-Tag'))
print('robots=', m.group(1) if m else None)
PY
```

### 3. Check robots.txt and sitemap.xml
Confirm whether:
- `robots.txt` is unrelated
- the affected URLs are still being submitted in `sitemap.xml`

This matters because a common contradictory state is:
- sitemap says the URL is indexable/discoverable
- page HTML says `noindex`

That contradiction often explains Search Console noise.

### 4. Inspect latest `origin/main`, not stale local `main`
Mandatory steps:
```bash
git -C /path/to/repo fetch origin main --quiet
git -C /path/to/repo rev-parse origin/main
git -C /path/to/repo log --oneline -n 12 origin/main
```

Then inspect the exact route files from `origin/main`, not from the dirty/behind local checkout:
```bash
git -C /path/to/repo show origin/main:src/app/blog/[id]/[slug]/page.tsx | sed -n '1,140p'
git -C /path/to/repo show origin/main:src/app/whitepapers/[id]/[slug]/page.tsx | sed -n '1,160p'
git -C /path/to/repo show origin/main:src/app/sitemap.ts | sed -n '1,260p'
```

Look specifically for:
- `robots: { index: false, follow: false }`
- any route-specific noindex branches
- sitemap inclusion of the same URL families

### 5. Compare code truth vs live truth
Classify the outcome into one of these buckets:

#### Case A: main still emits noindex
Diagnosis:
- this is a current code bug
- Search Console is accurately reflecting current production behavior

#### Case B: main is fixed, but live HTML still emits noindex
Diagnosis:
- deployment drift / production not serving the latest main fix
- Search Console is still correct about the current live site
- this is not a current main-branch code bug anymore

This was the key learning from the conversation that created this skill.

#### Case C: live HTML is already index/follow, but Search Console still shows noindex
Diagnosis:
- likely Google recrawl / validation lag
- production may already be fixed

### 6. If main is fixed, identify the fixing commit
Search for the commit that changed robots behavior and record:
- commit SHA
- commit title
- commit time

Example:
```bash
git -C /path/to/repo log --oneline --decorate --grep='allow indexing' -n 5 origin/main
git -C /path/to/repo show -s --format='%H%n%ci%n%s' <sha>
```

This lets you say confidently:
- latest main already contains the fix
- production appears not to be serving it yet

### 7. Check deployment/production-branch state if needed
If `origin/main` is fixed but live is stale, investigate deployment state next.
Typical questions:
- Is production actually tracking `main`?
- Did the fix commit deploy successfully?
- Is production serving an older branch or older deployment?

On Vercel, prefer project/deployment inspection. But note these practical pitfalls:
- CLI/API auth may fail even when env vars exist
- invalid/mismatched `VERCEL_TOKEN` or inaccessible `VERCEL_TEAM_ID` blocks verification
- if Vercel auth fails, report that production-branch confirmation remains unverified rather than guessing

## Recommended report structure
1. Search Console issue observed
2. Live production evidence
3. Latest `origin/main` evidence
4. Classification: code bug vs deploy drift vs Google lag
5. Next action to verify/fix

## Strong user-facing wording for Case B
Use wording like:
- `Latest origin/main is already fixed.`
- `However, live production still serves HTML with meta robots=noindex,nofollow.`
- `So the current issue is no longer a main-branch code bug; it is a production/deployment mismatch until proven otherwise.`

## Practical lessons
- Do not diagnose from a behind local `main`
- Do not assume Search Console lag if live HTML still says `noindex`
- If live HTML still says `noindex`, Google is not the root problem yet
- `x-vercel-cache: MISS` plus live `noindex` is a useful signal that the issue is not merely a stale CDN edge cache sample
- If CLI/API deployment inspection is blocked by auth, still deliver the grounded conclusion from source-vs-live comparison and explicitly mark deployment provenance as the remaining unknown
