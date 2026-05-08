---
name: ga4-explore-fqdn-report
description: Build a GA4 Explore report grouped by FQDN/Hostname in the Google Analytics UI, including the UI-specific Hostname dimension quirks found in Explore.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# GA4 Explore FQDN Report

Use this when the user wants a Google Analytics 4 Explore report grouped by FQDN / host name from the browser UI.

## When to use
- User gives a GA4 Explore or property URL and asks for FQDN-based aggregation
- Need to create or edit a browser-side Explore report instead of using an API/export pipeline
- Need a reusable hostname table such as Active users / Event count by hostname

## Key finding
In GA4 Explore, searching for `host`, `host name`, or even `hostname` from the dimension picker can be misleading:
- `host name` may return no results
- there can be two `Hostname` entries
- one can be a disabled Custom dimension entry
- the usable one is under `Page / screen -> Hostname`

Do not assume the first visible `Hostname` result is the correct selectable dimension.

## Proven workflow
1. Open the target GA4 Explore/property URL in a signed-in browser session.
2. Start a new `Free form` exploration unless the user wants an existing one edited.
3. In `Dimensions`, add `Hostname`.
   - If search is flaky, search `page location` or `hostname`.
   - Confirm the selectable result under `Page / screen`.
   - Ignore or avoid the disabled `Custom -> Hostname` entry.
4. In `Rows`, keep only `Hostname`.
   - Remove starter dimensions like `City` if they were auto-added.
5. In `Columns`, remove starter dimensions like `Device category` so the result is a pure FQDN aggregate table.
6. In `Values`, keep or add the metrics the user likely wants:
   - `Active users`
   - optionally `Event count`
   - add others only if requested
7. Rename the exploration and tab clearly, e.g.:
   - Exploration: `FQDN Aggregate Report`
   - Tab: `FQDN Active Users`
8. Wait for the table to reload and verify that rows look like real FQDNs, e.g. `foo.example.com`.
9. Report back with:
   - the saved Explore URL
   - date range used
   - dimensions/metrics configured
   - top sample rows and totals

## Verification checklist
- Table row header is `Hostname`
- No unwanted row dimension such as `City` remains
- No unwanted column split such as `Device category` remains
- Table entries are actual hostnames/FQDNs
- Metrics are visible and totals populated
- Final URL is the saved `/edit/...` exploration link

## Pitfalls
- The UI can reopen picker dialogs or menus unexpectedly after confirm; if so, explicitly close/cancel them and continue.
- Accessibility snapshots may show duplicate `Hostname` items; check whether the chosen one came from `Page / screen`.
- If selecting by normal click fails, DOM/script-assisted clicking may be needed for the checkbox in the picker.
- Searching `host name` can fail even though `Hostname` exists.

## Default interpretation
If the user only says `FQDN 기준 집계`, default to:
- recent 28 days
- Free form table
- row = Hostname
- metrics = Active users + Event count
- no column breakdown

## Good final response shape
- `완료했습니다.`
- exploration name / tab name
- saved GA URL
- date range
- configured dimensions and metrics
- top 5 to 10 hostnames with metric samples
- totals
