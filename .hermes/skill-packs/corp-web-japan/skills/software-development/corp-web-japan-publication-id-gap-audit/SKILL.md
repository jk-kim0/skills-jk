---
name: corp-web-japan-publication-id-gap-audit
description: Audit missing numeric publication IDs in corp-web-japan and decide whether each gap should be a full local migration, a hidden shadow record, a redirect-only legacy mapping, or left alone.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-japan publication ID gap audit

Use this when the user asks questions like:
- "there are gaps in posting IDs; what is missing?"
- "should this missing ID become a hidden posting?"
- "check corp-web-contents history and traffic before deciding"
- "review whether this PR missed hidden posting / redirect setup"

## Why this skill exists

A missing numeric ID in `src/content/**` is not enough evidence to add a hidden posting.
In this repo, the correct decision depends on three separate checks:
1. current local corpus state in `corp-web-japan`
2. canonical or historical source existence in `../corp-web-contents`
3. real traffic / legacy-path evidence from production logs

This skill exists because those checks often lead to different outcomes:
- full local migration candidate
- hidden shadow record candidate
- redirect-only legacy route handling
- separate orphan production route issue

## Core decision rule

Do **not** jump from `ID gap exists` to `create hidden posting`.

First classify the gap:
- `full local migration candidate`
- `redirect-only legacy candidate`
- `hidden shadow record candidate`
- `production-only orphan / separate investigation`

## Workflow

### 1. Inventory the current local ID gaps

From `corp-web-japan`, enumerate existing numeric MDX files and compute missing IDs for each family.

Typical families:
- `src/content/blog`
- `src/content/whitepapers`
- `src/content/news`
- `src/content/events`
- `src/content/use-cases`
- `src/content/demo/aip`
- `src/content/demo/acp`

Useful command pattern:

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
        gaps=sorted(set(range(min(ids), max(ids)+1)) - set(ids))
    print(name, ids[:3], '...', ids[-3:] if ids else [], 'gaps=', gaps)
PY
```

### 2. Check whether the repo intentionally encodes the gap in tests

Before treating a missing ID as an accident, inspect corpus tests such as:
- `tests/whitepaper-imported-ja-corpus.test.mjs`
- `tests/events-imported-ja-corpus.test.mjs`
- equivalent family tests

If `expectedIds` explicitly excludes the gap, that means the omission is at least currently intentional in the local repo snapshot.
That still does **not** prove the omission is correct.
It only tells you the repo has codified the current state.

### 3. Investigate `../corp-web-contents` source existence

For each missing ID, inspect whether canonical source currently exists in `../corp-web-contents` and whether it has the relevant locale body.

Key distinction:
- current canonical JA body exists
- only EN/KO exists, but no JA body
- only historical archived path exists
- nothing exists at all

Useful patterns:

```bash
cd ../corp-web-contents

# broad path history for a specific id
for id in 13 14; do
  git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep "/$id/" || true
done

# check current canonical locale files directly
[ -f pages/features/documentation/white-paper/13/seamless-ssh-connection/ja/content.mdx ] && echo yes
```

Interpretation:
- If current canonical JA source exists, the gap is a strong `full local migration candidate`.
- If only EN/KO webinar source exists and JA is absent, that is usually **not** a local Japanese migration candidate; it leans `redirect-only legacy candidate`.

### 4. Check production traffic before deciding scope

Use Vercel production logs for real evidence.

Fast setup check:

```bash
vercel whoami
vercel logs --project corp-web-japan --environment production --since 24h --json --no-branch --limit 20
```

Then query relevant legacy or canonical paths, for example:

```bash
vercel logs --project corp-web-japan --environment production \
  --since 30d \
  --search '/features/documentation/white-paper/13/seamless-ssh-connection' \
  --json --no-branch --limit 20
```

Things to look for:
- `[runtime-missing-redirect]` entries proving legacy-path traffic exists
- direct `404` entries on current local canonical-looking paths
- repeated bot/crawler hits versus broader user traffic

### 5. Confirm the upstream target actually resolves

For redirect-only or missing-redirect analysis, verify the corresponding `querypie.com` URL returns 200.

Example:

```bash
curl -I -L -sS -o /dev/null -w '%{http_code} %{url_effective}' \
  'https://www.querypie.com/features/documentation/white-paper/13/seamless-ssh-connection'
```

If the upstream target is 200 and production logs show hits to the legacy local path, you have strong justification for redirect handling at minimum.

### 6. Classify each gap

#### A. Full local migration candidate
Use this when all are true:
- local ID is missing in `corp-web-japan`
- current canonical source exists in `../corp-web-contents`
- correct JA body exists there
- production logs show legacy traffic or there is otherwise strong parity reason

Practical example from real work:
- whitepapers 13 and 14 were missing locally
- current canonical JA source existed upstream
- production legacy traffic still existed
- result: migrate them as full local MDX posts rather than hidden shadows

#### B. Redirect-only legacy candidate
Use this when:
- the local ID is missing
- upstream/history exists
- but there is no current JA local-migration-quality source for this site
- and production logs show legacy path hits that should still be sent upstream

Practical example pattern:
- webinar/event IDs where only EN/KO source exists upstream
- no suitable JA local article body exists
- legacy `/features/demo/webinars/<id>/...` traffic still occurs
- result: keep as redirect concern, not local corpus migration

#### C. Hidden shadow record candidate
Use this more narrowly.
Typical case:
- the local site already has a canonical replacement record
- another numeric ID needs to stay resolvable for continuity
- the content should stay out of the list
- detail access should redirect to the replacement record or external target

Do **not** use hidden shadow records as the first response to every gap.

Important practical variant learned from legacy webinar work:
- if a Korean-only legacy webinar ID still receives traffic, and a Japanese counterpart already exists locally under a different numeric ID, a hidden shadow event record can be the cleanest compatibility layer
- in that case, create a local `src/content/events/<old-id>.mdx` shadow file with:
  - `hidden: true`
  - the old legacy slug
  - `redirectUrl: "/events/<ja-id>/<ja-slug>"`
  - route-aligned thumbnail under `public/events/<old-id>/thumbnail.png`
- keep the shadow record in the event record set so `/events/<old-id>` and `/events/<old-id>/<old-slug>` still resolve and redirect correctly, while list pages continue to hide it via `visibleRecords = records.filter((record) => !record.hidden)`
- this is especially useful when the user explicitly wants local continuity rather than sending the request back to upstream `querypie.com`

Concrete mapping pattern observed in corp-web-japan:
- webinar 7 KO -> event 8 JA
- webinar 9 KO -> event 10 JA
- webinar 11 KO -> event 12 JA
- webinar 13 KO -> event 14 JA

#### D. Redirect-only legacy candidate
Use this when:
- the local ID is missing
- upstream/history exists
- but there is no current JA local-migration-quality source for this site
- and production logs show legacy path hits that should still be sent upstream

Practical example pattern:
- webinar/event IDs where only EN/KO source exists upstream
- no suitable JA local article body exists
- legacy `/features/demo/webinars/<id>/...` traffic still occurs
- result: keep as redirect concern, not local corpus migration

Additional routing rule learned from follow-up implementation:
- if the user wants this compatibility handled through local canonical records rather than generic missing-path fallback, prefer a dedicated static redirect route such as:
  - `src/app/features/demo/webinars/[id]/[[slug]]/route.ts`
- implementation shape:
  - look up the event record by `id`
  - if the record has `redirectUrl`, redirect there first
  - otherwise redirect to `getEventPublicationHref(id, record.slug)`
  - preserve the incoming query string
- this keeps legacy feature-webinar paths handled explicitly and consistently, without relying on the broad `[...missing]` catch-all helper
- when using shadow event records this way, also update the event canonical routes (`src/app/events/[id]/page.tsx` and `src/app/events/[id]/[slug]/page.tsx`) to honor `record.redirectUrl` before local canonicalization/rendering


#### D. Production-only orphan route issue
Use this when:
- production serves or receives traffic for a route that cannot be traced back to the current repo or `../corp-web-contents`
- examples include old `/posts/event/:id` or unexplained `/events/:id/:slug` 404s

Treat these as a separate lineage/debug task rather than forcing them into the local corpus immediately.

## Important experiential findings

### 1. A gap can be explicitly encoded in tests and still be wrong
A family test with `expectedIds` is evidence of the repo's current assumption, not proof that the omission is correct.
Use corp-web-contents source + production traffic to challenge that assumption.

### 2. Whitepaper gaps and webinar gaps often require different decisions
- Whitepaper gap + current JA source + legacy traffic -> usually local migration candidate
- Webinar gap + no JA source + legacy traffic -> usually redirect-only candidate

### 3. Production can have orphan event surfaces not traceable from the repo
During investigation, `/posts/event/6` was live in production and had canonical `/posts/event/6`, while `/events/6/...` 404ed and no matching source could be found in either current `corp-web-japan` or `../corp-web-contents` history.
Treat this as a separate production-orphan issue, not as proof that local `src/content/events/6.mdx` must be created.

## Recommended output format

For each gap family, report:
- missing IDs
- whether tests explicitly encode the omission
- whether current canonical upstream source exists
- whether JA body exists
- whether production traffic exists
- recommended classification
- recommended next action

Example:

```text
whitepapers 13, 14
- local IDs missing: yes
- encoded in local corpus test: yes
- current upstream JA source: yes
- legacy production traffic: yes
- classification: full local migration candidate
- next action: migrate into src/content/whitepapers/13.mdx and 14.mdx
```

## Follow-up implementation rule

If the user asks to proceed with a `full local migration candidate`:
- use a fresh worktree from latest `origin/main`
- if the family is whitepapers, load the whitepaper-posting skill
- migrate the content and route-aligned assets
- update corpus tests that list expected IDs
- run targeted family tests
- commit, push, and open the PR

## Pitfalls

- Treating every missing ID as a hidden posting requirement
- Ignoring `../corp-web-contents` current canonical source availability
- Ignoring locale suitability for the local Japanese site
- Looking only at code and not at production traffic
- Mistaking a production-only orphan route for a normal corpus migration candidate
