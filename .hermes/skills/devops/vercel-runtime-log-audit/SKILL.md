---
name: vercel-runtime-log-audit
description: Audit Vercel production runtime logs across projects, with reliable patterns for finding 404 and 5xx issues and publishing operational summaries.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vercel, logs, runtime, production, incident, operations]
---

# Vercel runtime log audit

Use this when the user asks to inspect Vercel runtime logs for abnormal production behavior such as 404s, 500s, or recurring runtime exceptions.

## When to use

- "Check production runtime logs"
- "Find 404 / 500 errors on Vercel"
- "Summarize abnormal logs across projects"
- "Write a wiki or incident snapshot from Vercel logs"

## Prerequisites

Confirm these first:

```bash
command -v vercel
printf 'VERCEL_TOKEN=%s\n' "${VERCEL_TOKEN:+set}"
printf 'VERCEL_TEAM_ID=%s\n' "${VERCEL_TEAM_ID:+set}"
vercel whoami
```

If you need all accessible projects, prefer the API because `vercel projects ls --json` may not emit usable JSON in automation:

```bash
python3 - <<'PY'
import json, os, urllib.request
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
url=f'https://api.vercel.com/v9/projects?teamId={team}&limit=100'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
for p in data.get('projects', []):
    print(p['name'])
PY
```

## Important findings

### 0.1 `--level error` is NOT always 5xx — filter client-side

A practical edge case: `--level error` can return rows whose `responseStatusCode` is `200`.
These are typically edge-middleware info logs mis-tagged by the platform, not real server errors.

Rule: always filter client-side for 5xx codes; do not report `--level error` counts as 5xx counts without this verification.

Example symptom from `corp-web-app`:
```json
{"responseStatusCode": 200, "level": "error", "message": "[features] /... status=200", "source": "edge-middleware"}
```

### 0. Start with a fast existence check before broad collection

Important current-environment caveat:
- newer Vercel CLI builds may or may not support the older project-scoped historical query shape (`vercel logs --project ... --since ... --until ...`)
- in some environments, `vercel logs --help` only exposes `vercel logs url|deploymentId`, i.e. live tailing for a ready deployment from now for a short period
- in other environments, newer CLI builds do support project-scoped historical queries again, including `--project`, `--environment`, `--since`, `--until`, `--status-code`, `--json`, and `--no-branch`
- before relying on older project/window examples from past notes, run `vercel logs --help` and verify which command shape is actually available
- if historical CLI queries are available, prefer them for day-window wiki snapshots because they can work through the CLI's logged-in context even when `VERCEL_TOKEN` is not exported to child script environments
- if only `url|deploymentId` tailing is supported, switch early to the direct `request-logs` API or document that exact historical recomputation is blocked from the current environment

For a single-project audit, first confirm that recent production logs actually exist and see the rough status mix with a small bounded query:

```bash
vercel logs --project <project> --environment production --since 24h --json --no-branch --limit 50
```

This should usually finish in a few seconds. Use it to answer:
- are logs present at all?
- what statuses are showing up recently?
- is the project mostly serving 200/304/307 and similar normal responses?

This is especially useful when a previous broad query returned zero results or timed out — distinguish:
- `no logs returned because the query/parse strategy was bad`
- from `logs exist, but there really are no 404/500 entries in the window`

### 1. Do not rely on `--status-code 500` for 5xx discovery across projects

In practice, `vercel logs --status-code 500 --json` or `--status-code 4xx/5xx` can return no JSON results even when `--level error` clearly returns production 500 entries.

For 5xx auditing, use:

```bash
vercel logs --project <project> --environment production --since 24h --level error --json --no-branch --limit 1000
```

Then filter client-side to `responseStatusCode` starting with `5`.

### 2. For 404s, `--search 'status:404'` works better than `--status-code 404`

Use:

```bash
vercel logs --project <project> --environment production --since 24h --search 'status:404' --json --no-branch --limit 1000
```

But treat the result carefully:
- output can contain duplicates
- counts are often better treated as sampled entries than authoritative totals
- dedupe by log `id`

### 3. `vercel logs` progress lines are not JSON

The CLI prints lines like:
- `Fetching project "..."`
- `Fetching logs...`

These may appear on stdout or stderr. Ignore non-JSON lines and parse only lines beginning with `{`.

### 3.5 Historical day-window queries can repeat rows and plateau at 50 unique entries

When querying a bounded historical window such as:

```bash
vercel logs --project <project> --environment production \
  --since '2026-04-25T00:00:00+09:00' \
  --until '2026-04-26T00:00:00+09:00' \
  --json --no-branch --limit 200
```

practical behavior may differ from the requested `--limit`:
- the CLI can emit many more JSON lines than the number of distinct log records
- after dedupe by `id`, you may end up with only about `50` unique rows even when `--limit 200` or higher was requested
- this can affect general queries and filtered `404` / `307` queries alike

Interpretation rule:
- do **not** report these as authoritative traffic totals
- report them as sampled runtime-log evidence for that day/window
- always dedupe by log `id` before counting paths or statuses

This matters especially for wiki or incident summaries covering exact calendar days: the safest framing is sampled status mix and repeated-path patterns, not exact volume.

### 3.6 Direct request-log API shape, environment filtering, and pagination can be misleading

When you call the backend directly at:

```text
https://vercel.com/api/logs/request-logs
```

note these field-level realities:
- the request requires `ownerId`, `projectId`, `startDate`, and `endDate`
- `startDate` / `endDate` must be epoch milliseconds, not ISO timestamps
- for production-only reporting, you should also pass `environment=production`
- without an explicit `environment` filter, project-level results can be heavily polluted by preview traffic and become misleading for production audits
- the response shape is top-level `rows` plus top-level `hasMoreRows`
- do **not** expect the older nested `pagination.data` structure
- row identifiers are usually under `requestId`, not the CLI-style top-level `id`
- status is typically `statusCode`, not `responseStatusCode`

If required fields are missing or typed wrong, typical API errors include:
- `Validation error: Required at "ownerId"`
- `Validation error: Expected number, received nan at "startDate"`

Important environment-scope finding:
- project-level request-log queries are **not reliably production-only by default**
- on `corp-web-japan`, an unfiltered current-day query returned a mix dominated by `preview` rows, with only a small minority of `production` rows
- for production wiki/audit work, explicitly pass `environment=production`
- similarly, use `environment=preview` when you actually want preview-only evidence
- do not assume `target=production` or `target=preview` filters the same way; verify with a small probe query and count the returned `environment` values

For historical day-window `404` / `307` audits, another practical failure mode can appear:
- page 0 returns 50 rows and `hasMoreRows = true`
- incrementing `page` can still return the exact same first-page `requestId` set instead of advancing
- this creates the illusion of more pages while preventing exact full-day aggregation
- on some projects or billing states, the API can fail even before pagination analysis with `HTTP 400 {"name":"ExceedsBillingLimitError"}` for very small historical windows (observed even for a 1-minute May 7 KST window on `corp-web-japan`)
- even on current-day windows where the API succeeds, broad `all` queries and some direct status filters such as `307` can still plateau at the first 50 unique rows while `hasMoreRows = true`
- in contrast, narrower direct filters such as `404` or `500` may return a complete set with `hasMoreRows = false`, so treat them separately instead of assuming all statuses have the same measurement quality

Interpretation rule:
- first verify the `environment` mix on a small sample; if preview traffic is present in a production audit, re-run with `environment=production`
- if page 1+ repeats page 0 `requestId` values, stop treating the API as paginating correctly
- if the API returns `ExceedsBillingLimitError` for small historical windows, treat exact historical recomputation as platform-blocked from the current environment and preserve/report only directly observed data
- report the page-0 result as a sampled top-set only when broader pagination stalls
- explicitly state that exact totals are blocked by backend pagination behavior
- still use direct `500` / `502` / `503` / `504` status queries, because zero-row checks are still useful and fast even when `404` / `307` pagination is broken
- when doing manual `curl` verification after collecting the clean sample, record a cutoff timestamp and distinguish the clean pre-verification counts from the later raw rows polluted by your own checks

### 4. Error queries can hit a hard practical cap

`vercel logs --level error --limit 1000` can hit the 1000-line cap quickly on noisy projects. If you get 1000 results, report it as:
- `>=1000` errors in the window
- not exactly 1000

### 5. Recent and longer-window checks are both useful

Recommended windows:
- primary snapshot: `24h`
- persistence cross-check: `30d`

This distinguishes active incidents from isolated noise.

## Recommended audit workflow

### A. Enumerate projects

Get projects through the API, then loop per project.

### B. Collect 5xx reliably

```bash
vercel logs --project <project> --environment production --since 24h --level error --json --no-branch --limit 1000
```

Parse JSON lines only, then keep records where:
- `responseStatusCode` is `500`, `502`, `503`, `504`, etc.

### C. Collect 404 samples

Default cross-project method:

```bash
vercel logs --project <project> --environment production --since 24h --search 'status:404' --json --no-branch --limit 1000
```

Dedupe by `id` before summarizing.

For a single project where you need a fast direct answer, also try the exact status-code filter:

```bash
vercel logs --project <project> --environment production --since 24h --status-code 404 --json --no-branch --limit 1000
```

In practice, this can return quickly and cleanly for one-project verification even though broader cross-project audits are often more reliable with `status:404` search.

### D. Direct single-project 5xx verification

When the user asks only about one project and wants a quick answer, prefer these bounded direct checks before attempting any expensive full export:

```bash
vercel logs --project <project> --environment production --since 24h --status-code 500 --json --no-branch --limit 1000
vercel logs --project <project> --environment production --since 24h --status-code 502 --json --no-branch --limit 1000
vercel logs --project <project> --environment production --since 24h --status-code 503 --json --no-branch --limit 1000
vercel logs --project <project> --environment production --since 24h --status-code 504 --json --no-branch --limit 1000
vercel logs --project <project> --environment production --since 24h --level error --json --no-branch --limit 1000
```

Interpretation pattern:
- first confirm logs exist with `--limit 50`
- then run direct `404`, explicit integer `5xx` status checks such as `500`/`502`/`503`/`504`, and the `--level error` query
- do not use `--status-code 5xx` unless the current CLI help and a probe confirm it works; some Vercel CLI/API paths reject it with `Validation error: statusCode must contain only comma-separated integers`
- if all explicit status checks return zero and the sample query clearly shows recent production logs, it is reasonable to conclude there were no recent runtime-visible 404/5xx entries in that window
- do not assume a broad general sample is sufficient to rule out same-day `500`s: the general `vercel logs --json` stream is recency-ordered, so a noisy later `404` period can push earlier same-day `500` rows out of a bounded sample
- if the broad sample and direct integer status query disagree, trust the direct status-specific result for existence, then inspect the returned rows directly

### E. Summarize by project

For each project report:
- count of sampled/distinct 404s
- count of confirmed 5xx errors
- top paths by `(status, requestPath)`
- representative latest entries with:
  - timestamp
  - status
  - path
  - first line of message
  - source
  - deploymentId

### E. Separate scanner noise from likely real app failures

Typical scanner/bot noise examples:
- `/wp-admin/...`
- `/wp-login.php`
- old `.php` probes
- config-discovery probes such as `/runtime-config.js`, `/env.json`, `/config.json`, `/swagger.json`, `/openapi.json`, `/.well-known/jwks.json`
- API/health probes such as `/api/health`, `/health`, `/api/account`, `/api/v1/config`, `/api/v2/settings`
- secret-file probes such as `/.env.local`, `/backend/.env`, `/api/.env`, `/admin/.env`, `/config.env`
- sensitive-path probes such as `/.git/config` and `/.ssh/id_rsa`

Likely real issues often show:
- repeated same application path
- same exception signature
- same deploymentId
- framework/runtime-specific message

Operational rule:
- do not treat the probe families above as redirect-review candidates by default
- for broken-link / changed-URL monitoring, maintain an actionable allowlist of content-like path families and exclude these probe families from the redirect-review queue
- summarize them as noise buckets instead: `config-probe`, `api-probe`, `secret-probe`, `exploit-probe`

**Additional scanner noise patterns observed in corp-web-app production logs:**
- `/.well-known/apple-app-site-association`, `/.well-known/assetlinks.json` — mobile app association probes
- `/.well-known/traffic-advice`, `/.well-known/ucp`, `/.well-known/security.txt`, `/.well-known/related-website-set.json`, `/.well-known/passkey-endpoints`, `/.well-known/gpc.json`, `/.well-known/webauthn` — web standard discovery probes
- `/llms.txt` — LLM discovery probe
- `/xmlrpc.php` — WordPress exploit probe
- `/sitemap` without `.xml` — search engine probe
- `/blog/content/images/...` directory paths (no filename) — legacy blog platform crawler noise

These should all be classified as scanner noise rather than actionable app 404s that need redirect rules.

### E.1 When the goal is to stop probe paths from appearing as runtime 404s

Important practical finding:
- Vercel does not provide a simple per-path "suppress 404 in Runtime Logs" setting
- if a request reaches a Vercel Function or Routing Middleware, a runtime-log row can still exist even if you stop calling `console.log`
- in a Next.js App Router setup with a runtime catch-all 404 handler (for example `src/app/[...missing]/page.tsx`), unmatched requests are intentionally made runtime-visible

Recommended approach:
- if the goal is specifically to prevent probe paths from showing up as runtime 404 noise, block or challenge them before they reach app runtime by using Vercel Firewall / WAF rules
- prefer exact-path rules for singletons like `/swagger.json` or `/api/health`
- prefer prefix rules for families like `/.git/*`, `/.ssh/*`, `/wp-admin/*`

Action guidance:
- exploit/secret probes -> usually `deny`
- config/API discovery probes -> `deny` or `challenge`, depending on your tolerance and plan features
- avoid redirects or rewrites for these probe paths; they convert scanner noise into misleading 3xx/200 behavior and can signal that the path is specially handled

Interpretation rule:
- Firewall/WAF is the right layer when you want these requests to stop becoming runtime-visible 404s
- post-processing filters are the right layer when you only need cleaner monitoring/reporting without changing request handling

### F. Runtime logs do NOT capture every user-visible 404

Important experiential finding: a user can genuinely hit a 404 on a Vercel-hosted site even when the project's production runtime-log queries show zero 404 entries.

This happens when the 404 is served by Vercel's edge/static layer rather than by application runtime execution.

What this means operationally:
- `vercel logs` runtime queries are not a complete source of truth for user-visible 404s
- `404 = 0` in runtime-log output does NOT prove users saw no 404 pages
- you must distinguish `runtime 404s` from `edge/static 404s`

### G. Fast synthetic verification for suspected missing 404s

When the user says they personally saw a 404 but runtime logs show none, do a bounded synthetic test:

```bash
curl -I -sS 'https://<domain>/__hermes-vercel-log-test-404' | sed -n '1,20p'
```

Then immediately run a recent bounded log query for the project:

```bash
vercel logs --project <project> --environment production --since 5m --json --no-branch --limit 200
```

If the HTTP response is `404` but the request path does not appear in recent runtime logs, treat that as evidence that the 404 is outside runtime-log visibility.

### H. Header signatures for edge/static 404s

These response headers are strong evidence that the 404 was handled by Vercel's edge/static layer rather than by app runtime:
- `x-matched-path: /404`
- `x-vercel-cache: HIT` or other cache-layer response
- `server: Vercel`

Interpretation:
- request was resolved to the platform 404 path
- response may be cached
- runtime logs may not contain the request even though the user definitely saw a 404 page

### I. When your own verification requests pollute the audit window

During path-specific incident work, your own `curl`, browser, or synthetic checks can immediately appear in the same runtime-log window and distort a tiny sample.

Use this pattern:

1. First collect the recent broad/path-specific sample.
2. Note the timestamp when you started manual verification.
3. Re-run the path query with an `--until '<timestamp>'` bound just before your own checks.
4. Report both if useful:
   - the raw recent sample including your probes
   - the cleaned sample excluding self-generated verification traffic

This is especially important when only a few requests exist in the window.

For dated wiki snapshots, be explicit about this in the data-integrity note:
- if the snapshot is for the current day and manual checks happened after collection, state that the checks are not included in the counts
- if you later recompute a completed full-day window, previous same-day manual checks may legitimately appear inside the status-specific log sample; do not say they are excluded unless you bounded the query with `--until` before those checks
- keep manual live checks in a separate section from log-derived counts

### J. Path-specific redirect audits: parse the structured JSON embedded in `message`

For custom runtime handlers that log structured payloads such as:
- `[runtime-missing-redirect] {...}`
- `[runtime-404] {...}`

Do not stop at top-level fields like `requestPath` and `responseStatusCode`.
Parse the trailing JSON object from `message` and extract fields such as:
- `requestedPath`
- `redirectTarget`
- `host`
- `referer`
- `userAgent`

This is often the only place where referrer and redirect-target evidence exists.

Practical implication:
- `referer: null` plus crawler user agents often means direct bot/unfurl fetches rather than normal in-site navigation
- repeated `redirectTarget` values let you verify whether an allowlisted redirect is sending traffic to the intended upstream URL

## Project-specific references

- `references/corp-web-japan-runtime-log-patterns.md` records observed corp-web-japan runtime-log patterns such as current-day 50-row plateaus, generic company/contact-path Python probing, and route-policy candidates from May 2026 snapshots.
- `references/corp-web-app-runtime-404-regression.md` records the corp-web-app pattern where repeated non-noise 404s were caused by middleware default-locale rewrites plus route handlers that still parsed the original unprefixed `request.url`, and gives the stage/prod probing, git-forensics, redirect-vs-rewrite fix, and regression-test recipe.
- `references/vercel-waf-rate-limit-investigation.md` records how to inspect active Vercel WAF rate-limit config with `vercel api`, interpret official WAF rate-limit behavior, and diagnose E2E 403/429 bursts as rate-limit/challenge behavior rather than app runtime failures.


## Useful one-off commands

### Show recent 5xx samples for one project

```bash
python3 - <<'PY'
import subprocess, json
cmd=['vercel','logs','--project','<project>','--environment','production','--since','24h','--level','error','--json','--no-branch','--limit','20']
p=subprocess.run(cmd, capture_output=True, text=True)
for raw in ((p.stdout or '')+'\n'+(p.stderr or '')).splitlines():
    raw=raw.strip()
    if raw.startswith('{'):
        x=json.loads(raw)
        if str(x.get('responseStatusCode','')).startswith('5'):
            print(json.dumps({k:x.get(k) for k in ['timestamp','responseStatusCode','requestPath','message','source','deploymentId']}, ensure_ascii=False))
PY
```

### Count confirmed 5xx entries fast

```bash
python3 - <<'PY'
import subprocess, json, collections
cmd=['vercel','logs','--project','<project>','--environment','production','--since','24h','--level','error','--json','--no-branch','--limit','1000']
p=subprocess.run(cmd, capture_output=True, text=True)
items=[]
for raw in ((p.stdout or '')+'\n'+(p.stderr or '')).splitlines():
    raw=raw.strip()
    if raw.startswith('{'):
        try:
            x=json.loads(raw)
            if str(x.get('responseStatusCode','')).startswith('5'):
                items.append(x)
        except:
            pass
print('count', len(items))
print('statuses', collections.Counter(x.get('responseStatusCode') for x in items))
PY
```

## Converting edge/static 404s into runtime-visible 404s

When the user wants nonexistent page URIs to appear in Vercel Runtime Logs, the practical fix for a Next.js App Router site is to force unmatched page paths through runtime.

### Root cause pattern

If the app has no matching runtime page/route for an unknown path, Vercel can serve the 404 at the edge/static layer.
In that case:
- the user still receives a real `404`
- Runtime Logs may show no matching request
- headers often indicate platform handling rather than app-runtime handling

### Reusable fix for App Router sites

Add a root catch-all page route:

```text
src/app/[...missing]/page.tsx
```

Recommended implementation pattern:

```tsx
import { headers } from "next/headers";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function MissingRoutePage({
  params,
}: {
  params: Promise<{ missing: string[] }>;
}) {
  const { missing } = await params;
  const requestHeaders = await headers();
  const requestedPath = `/${missing.join("/")}`;

  console.log(
    "[runtime-404]",
    JSON.stringify({
      requestedPath,
      host: requestHeaders.get("host"),
      referer: requestHeaders.get("referer"),
      userAgent: requestHeaders.get("user-agent"),
    }),
  );

  notFound();
}
```

Why this works:
- the catch-all route matches otherwise-unmatched page paths
- `dynamic = "force-dynamic"` ensures runtime execution rather than static optimization
- the `console.log` creates a Runtime Log entry
- `notFound()` preserves the correct `404` response for the user

### Verification pattern

1. Verify locally

```bash
npm test
npm run typecheck
npm run build
npm run start -- --port 3012
curl -I http://127.0.0.1:3012/__hermes-vercel-log-test-404
```

Then confirm the local server output includes a line like:

```text
[runtime-404] {"requestedPath":"/__hermes-vercel-log-test-404", ...}
```

2. Verify on Vercel preview

If the repo has `git.deploymentEnabled: false`, branch pushes may not create preview deployments automatically. In that case use:

```bash
vercel pull --yes --environment=preview
vercel build
vercel deploy --prebuilt --yes --no-wait
```

Wait for the preview deployment to become `READY`, then trigger a missing path on the preview URL.

3. Confirm Runtime Logs now capture the request

```bash
vercel logs --project <project> --environment preview --since 10m --status-code 404 --json --no-branch --limit 50
```

Expected result:
- a matching log entry for the missing path
- `source` usually `serverless`
- `message` contains `[runtime-404]`

### Important scope note

This solves visibility for unmatched page-like routes captured by the App Router catch-all route.
It does NOT guarantee identical runtime-log visibility for every possible missing asset or other platform-level miss.

## Reporting guidance

Be explicit about measurement quality:
- `5xx` counts from `--level error` are the most reliable quick signal
- `404` counts from `status:404` are best treated as sampled/distinct entries after dedupe unless you have confirmed the requests are runtime-visible
- if a query hit 1000 lines, report `>=1000`
- if you added a runtime catch-all fix, distinguish `runtime-visible 404s after fix` from prior `edge/static 404s outside runtime visibility`

For interactive operational audits, progress updates must be visible user-facing chat messages, not just tool-call labels or a final report. Before each Vercel inspect/log/smoke step, say what is being checked, why, and the expected wait; after the command, report the result before running the next query. Avoid a “final report only” flow when the user asked for diagnosis with ongoing visibility.

## When Vercel auth is unavailable or invalid

A practical failure mode: the local environment can have `VERCEL_TOKEN` / `VERCEL_TEAM_ID` set but the token is expired or invalid, and newer CLI flows may fail with errors such as:
- `The specified token is not valid`
- API `403` on project listing even though repo docs contain the expected team/project identifiers

Fallback workflow for still-useful investigation:

1. Do not keep retrying unauthenticated log commands.
2. Look for repo-managed operational metadata first, for example files like:
   - `ops/vercel-firewall/README.md`
   - deployment/runbook docs that record `teamId`, `projectId`, project name, and expected domains
3. Check whether the repo wiki or checked-in incident notes already contain prior runtime-log snapshots for the exact path.
4. Cross-check current live behavior directly with `curl -I` against production and stage.
5. Use git history to explain likely path provenance, especially for one-off 404s on renamed routes.

This fallback cannot prove the missing `referer` or exact runtime row contents, so report that limitation explicitly. But it is still often enough to answer:
- whether the path is currently live or 404
- whether the app still emits that path in current HTML
- whether the path came from an older route contract, rename, or legacy external link

### Route-rename stale-link heuristic

If you see a path-specific 404 such as `/section/.../download` and current HTML no longer links there:
- search git history for the exact path and for nearby route-family renames
- inspect the current rendered HTML for the canonical replacement path
- if history shows a rename (for example `/download` -> `/pdf`) and current HTML only emits the new path, classify the likely cause as stale external/bookmarked/cached traffic rather than a current in-site navigation bug, unless logs later prove otherwise

Good summary structure:
1. scope and windows checked
2. per-project status table
3. detailed findings for noisy projects
4. representative error signatures and deployment IDs
5. limitations and next actions

## Wiki / incident document note

When publishing a wiki snapshot from runtime logs:
- record the date of the audit
- record the repo wiki target separately from the log source
- if relevant, include the current product repo `origin/main` SHA as context, but do not pretend the findings came from code inspection alone
- describe the page as an operational snapshot, not a source-of-truth metrics system
- if an existing page was written as a current-day partial report, recompute it after the calendar day is complete and explicitly change the effective range from "current-day logs" to "completed calendar-day window"
- when adding a new dated report to a GitHub wiki, update `_Sidebar.md` in the same commit so the page is discoverable from the wiki navigation
- for status-specific day reports, run explicit integer checks for `307`, `404`, `500`, `502`, `503`, and `504`, plus `--level error` filtered client-side for 5xx; do not rely on the broad top-set to reveal isolated earlier-day 500s
- after collecting log-derived counts, run a small manual live recheck for representative 404/307 paths and document it in a separate section; this can reveal that an earlier-window 404 is no longer current live behavior after a later deployment
- keep multiline runtime messages one-line in markdown tables/lists where possible, so a stack frame or wrapped error does not break wiki list formatting

## Pitfalls

- On this macOS Hermes setup, `VERCEL_TOKEN` may be loaded only by interactive zsh. Before concluding Vercel CLI credentials are unavailable, check `zsh -ic` in addition to the default tool env and `zsh -lc`; see `references/interactive-zsh-vercel-token.md`.


- Assuming `--status-code 500` is sufficient in every context
- Treating 404 counts as exact totals without dedupe
- Forgetting that `Fetching ...` lines are not JSON
- Reporting `1000` as the exact count when the CLI likely capped the result
- Mixing up product repo context with Vercel operational evidence
- Starting with a broad `--limit 1000` full-log export for a single project when a `--limit 50` existence check plus direct 404/500/5xx queries would answer the question faster
- Letting Vercel log collection run too long without a timeout; use bounded subprocess timeouts and change strategy immediately if a broad query exceeds the expected quick-run budget
- Trusting `--level error` entries as purely 5xx without client-side `responseStatusCode` filtering; some error-level rows may report `200` or other non-5xx statuses, so always filter by `responseStatusCode` starting with `5` when counting 5xx entries
