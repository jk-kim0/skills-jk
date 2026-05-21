# Vercel WAF rate-limit investigation reference

Use this when runtime logs show no app/runtime 403 or 429 rows but an external E2E/curl sweep sees 403/429 responses.

## Official Vercel behavior to remember

Source pages checked:
- https://vercel.com/docs/vercel-waf/rate-limiting
- https://vercel.com/docs/vercel-waf/
- https://vercel.com/docs/attack-mode/
- https://vercel.com/docs/limits

Key points:
- WAF Rate Limiting controls how many requests from the same source can hit an app within a time window.
- The request limit is the maximum number of requests allowed in the selected window from a common source.
- Rate-limit counters are tracked per region; traffic for the same key spread across regions can exceed the configured per-region limit.
- Actions can include default 429, Log, Deny, or Challenge.
- Fixed window is available on all plans; token bucket is Enterprise-only.
- Counting windows are typically minimum 10s and maximum 10min, with Enterprise supporting up to 1hr.
- Vercel WAF config changes are documented as taking effect globally within about 300ms.
- Attack Mode and custom WAF challenge traffic may block non-browser automation, even when browser traffic works.

## Inspect the active project WAF config

If Vercel CLI is authenticated, `vercel api` can query the firewall config without an exported `VERCEL_TOKEN`:

```bash
PROJECT_ID='<project id>'
TEAM_ID='<team id>'
vercel api "/v1/security/firewall/config?projectId=${PROJECT_ID}&teamId=${TEAM_ID}" \
  > /tmp/vercel-firewall.json

python3 - <<'PY'
import json
obj=json.load(open('/tmp/vercel-firewall.json'))
a=obj.get('active',{})
print('firewallEnabled', a.get('firewallEnabled'), 'version', a.get('version'), 'updatedAt', a.get('updatedAt'))
print('managedRules', json.dumps(a.get('managedRules'), ensure_ascii=False))
print('crs active', {k:v for k,v in (a.get('crs') or {}).items() if v.get('active')})
print('ip blocks', a.get('ips'))
print('rules count', len(a.get('rules') or []))
for r in a.get('rules') or []:
    print('\nRULE', r.get('name'), 'active=',r.get('active'), 'id=',r.get('id'))
    print('action', json.dumps(r.get('action'), ensure_ascii=False))
    print('conditions', json.dumps(r.get('conditionGroup'), ensure_ascii=False)[:2000])
PY
```

## Evidence pattern: E2E sweep is rate-limited, not app-broken

A reliable diagnosis requires all of these checks:
1. Actions log: identify the first non-200, request concurrency, retry behavior, and whether the first failure is 429 followed by broad 403.
2. Vercel runtime logs for the same environment/time window:
   - query broad preview/production logs
   - query explicit `--status-code 403` and `--status-code 429`
   - if runtime logs show zero 403/429 but do show 200s for the same route family, the app runtime did not emit the 403/429.
3. Direct single-request curl after the burst for representative failed URLs.
   - If those return 200, the route implementation is likely healthy.
4. Inspect WAF rules for rate-limit thresholds and challenge/deny actions.

## Example corp-web-app finding from 2026-05-21

Project:
- `corp-web-app`
- projectId `prj_1PANizagPBzs7OF4efV8QoMAhgzx`
- teamId `team_8DsCdrF1uCfwY30OS8F8lREn`

Active WAF findings:
- firewall enabled, version 20
- `Default-RateBaseRule-Challenge`:
  - limit 100
  - window 10 seconds
  - fixed window
  - keys: `ip`, `header:user-agent`
  - action: `challenge`
  - actionDuration: `1h`
  - excludes several corporate/proxy IP ranges
- `Default-RateBaseRule-Deny`:
  - limit 1000
  - window 10 seconds
  - fixed window
  - key: `ip`
  - action: `deny`

Observed run:
- GitHub Actions sitemap E2E swept 182 URLs with concurrency 8 and a fixed User-Agent.
- First attempt hit 429, then many 403s.
- Playwright retries repeated the full sweep and made later attempts broadly 403.
- Same-time Vercel preview runtime logs had zero runtime 403/429 rows and only the expected `/eula` 404.
- Representative 403 URLs returned 200 via single curl afterward.

Correct fix pattern:
- lower default concurrency well below the configured WAF threshold
- add an inter-request delay
- disable whole-suite retries for the sitemap sweep, because retries amplify WAF challenge state

A conservative default for a 100 requests / 10s rule is about 2 requests/s, e.g. concurrency 1 and 500ms delay, which yields roughly 20 requests / 10s.
