# corp-web-japan Vercel Runtime Log wiki report cron prompt

이 문서는 Hermes cron 작업으로 `corp-web-japan` Vercel production runtime log를 주기적으로 분석하고 `querypie/corp-web-japan` GitHub wiki에 운영 리포트를 작성/업데이트하기 위한 완전한 작업 지시서입니다.

이 파일은 새 Hermes cron 세션에서 현재 대화 맥락 없이도 동작하도록 작성되어 있습니다. 가능한 경우 cron job에 관련 skills를 함께 연결하고, skills가 로드되지 않는 환경에서도 아래 prompt 본문만으로 실행할 수 있도록 핵심 절차와 제약을 prompt 안에 중복 포함합니다.

권장 저장 위치: `.hermes/cron-prompts/corp-web-japan-vercel-runtime-log-wiki-report.md`

## 권장 cron 설정

권장 실행 시각:

```text
45 23 * * *
```

이 작업은 Vercel runtime log의 최근 24시간 접근 제약 때문에 KST 하루가 끝나기 직전 실행하는 것이 가장 안전합니다. 자정 이후에 전날 리포트를 만들면 전날 00:00 직후 로그가 이미 접근 가능 범위 밖으로 밀릴 수 있습니다.

권장 job 이름:

```text
corp-web-japan daily Vercel runtime log wiki report
```

권장 toolsets:

```text
terminal,file
```

권장 attached skills:

```text
vercel-runtime-log-audit
github-wiki-editing
```

선택적 보조 skill:

```text
hermes-agent
```

`hermes-agent`는 cron 기능 자체를 조정하거나 job을 생성/수정할 때만 필요합니다. 실제 예약 실행에서는 `vercel-runtime-log-audit`와 `github-wiki-editing`이 핵심입니다.

## 생성 방식

### Hermes 도구/API로 생성할 때

가능하면 cron job 생성 시 skills를 함께 지정합니다.

- schedule: `45 23 * * *`
- name: `corp-web-japan daily Vercel runtime log wiki report`
- prompt: 아래 `Cron job prompt` 전체
- skills:
  - `vercel-runtime-log-audit`
  - `github-wiki-editing`
- enabled_toolsets:
  - `terminal`
  - `file`

### CLI에서 생성할 때

CLI에서는 먼저 job을 만든 뒤 prompt를 붙여 넣거나 편집합니다.

```bash
hermes cron create '45 23 * * *'
hermes cron edit <job-id>
```

CLI에서 별도 skill attachment를 지원하지 않는 경우에도 아래 prompt는 자체 절차를 포함하므로 그대로 사용할 수 있습니다. 단, cron 세션에서 `terminal`과 `file` toolset이 사용 가능해야 합니다.

## Cron job prompt

아래 내용을 Hermes cron job의 prompt로 그대로 사용합니다.

```text
You are running an autonomous scheduled operational reporting task in a fresh Hermes cron session. Do not ask the user questions. Complete the task as far as the current environment allows, verify the result, and clearly report blockers if credentials or external services are unavailable.

Task: create or update a GitHub wiki report for querypie/corp-web-japan based on Vercel production runtime logs for the corp-web-japan project.

Skill loading requirement:
- If the Hermes skills tool is available, first load and follow these skills in this order:
  1. vercel-runtime-log-audit
  2. github-wiki-editing
- If a skill is unavailable, continue using the embedded instructions in this prompt. Do not stop only because a skill could not be loaded.
- Use the loaded skills for command pitfalls and verification details, but the concrete task scope in this prompt takes precedence.

Execution constraints:
- This job is autonomous. Do not ask clarifying questions.
- Do not fabricate log results, wiki commits, or push status.
- Use tools to inspect the live environment; do not rely on memory for current time, file state, git state, Vercel auth, or GitHub auth.
- Keep command output bounded. Use timeouts for broad log collection and change strategy if a Vercel query hangs or returns unsupported-option errors.
- Never print secret values. It is OK to print whether an environment variable is set.

Primary repositories and paths:
- Product repository: querypie/corp-web-japan
- Local product repository path, if present: /Users/jk/workspace/corp-web-japan
- Local wiki repository path, preferred if present: /Users/jk/workspace/corp-web-japan.wiki
- Wiki remote fallback: https://github.com/querypie/corp-web-japan.wiki.git
- Wiki target: querypie/corp-web-japan GitHub wiki
- Vercel project: corp-web-japan
- Vercel scope/team: querypie
- Vercel environment: production
- Reference report format: https://github.com/querypie/corp-web-japan/wiki/Vercel-Runtime-Log---May-20

Critical Vercel runtime-log constraint:
- Vercel runtime logs are only reliably accessible for the most recent 24 hours in this environment.
- Do not attempt to reconstruct older full-day reports outside the accessible 24-hour window.
- If the job is delayed or starts after the intended reporting day has partly fallen outside the recent-24h window, document the actual accessible window and do not claim full-day coverage.
- Because of this constraint, prefer reporting the current KST calendar day up to the audit time when the job runs before midnight KST.
- If a completed prior calendar-day report is required in the future, a separate log archival job must collect the data before it expires. This task does not do that.

Required report page naming:
- Use the existing wiki naming convention from the reference page.
- For a single KST date, create/update: `Vercel Runtime Log - Mon D`, e.g. `Vercel Runtime Log - May 20`.
- The wiki file name should follow the existing wiki file convention, e.g. `Vercel-Runtime-Log---May-20.md`.
- If the accessible window crosses two KST dates because the job was delayed, use a clear date range title such as `Vercel Runtime Log - May 20 through May 21`, and state the exact actual data range.

Required high-level workflow:
1. Confirm the current time in KST using the system clock.
   - Example: `TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S %Z'`
   - Japan and Korea are both UTC+09:00; label report times as KST.
2. Determine the intended reporting window:
   - If running before midnight KST as scheduled, report from the current KST date 00:00:00 through the audit time, or through 23:59:59 if a bounded `--until` is needed.
   - If current KST day start is more than 24 hours behind the runtime-log query point, use only the recent accessible 24-hour window and label it honestly.
   - Use ISO timestamps with explicit `+09:00` offset for Vercel queries when supported.
3. Verify prerequisites:
   - `command -v vercel`
   - `vercel whoami`
   - `printf 'VERCEL_TOKEN=%s\n' "${VERCEL_TOKEN:+set}"`
   - `printf 'VERCEL_TEAM_ID=%s\n' "${VERCEL_TEAM_ID:+set}"`
   - `command -v git`
   - `command -v gh`
   - `gh auth status`
4. Prepare the wiki repository:
   - Prefer the existing local clone at `/Users/jk/workspace/corp-web-japan.wiki` if it exists.
   - If it does not exist, clone `https://github.com/querypie/corp-web-japan.wiki.git` into a stable local path such as `/Users/jk/workspace/corp-web-japan.wiki` if possible, otherwise a temp path.
   - In the wiki repo, run `git status --short --branch` before editing.
   - If unrelated local wiki changes exist, do not overwrite them. Report the blocker unless they can be safely isolated.
   - Fetch and rebase/pull the wiki default branch before editing. Verify the actual branch name; do not assume it is `master` without checking.
   - Do not edit wiki files inside the product repository. GitHub wiki is a separate git repository.
5. Collect product repository context if available:
   - If `/Users/jk/workspace/corp-web-japan` exists, fetch `origin main`, read the current `origin/main` SHA and subject, and include them in the report as context.
   - Do not infer runtime-log findings from code inspection alone.
6. Collect Vercel logs for `corp-web-japan` production.
7. Write or update the wiki report markdown using the report template below.
8. Update `_Sidebar.md` in the wiki repository so the new dated page is discoverable. Preserve existing sidebar structure and add the new runtime-log page near adjacent Vercel Runtime Log reports.
9. Commit and push the wiki repository.
10. Verify the pushed wiki state.
11. Final response must include:
    - wiki page title and file path
    - committed wiki SHA
    - pushed branch name
    - exact reporting window and KST audit time
    - whether 5xx were found
    - any blockers or limitations

Vercel log collection requirements:
- First run `vercel logs --help` and verify the supported historical query syntax in the current CLI version.
- Start with a small existence check:
  `vercel logs --project corp-web-japan --environment production --since 24h --json --no-branch --scope querypie --limit 50`
- Ignore non-JSON progress lines such as `Fetching project ...` and parse only JSON lines.
- Deduplicate rows by `id`, `requestId`, or the most stable available identifier.
- Treat broad log samples as sampled top-sets, not authoritative full traffic totals.
- Vercel CLI/API can repeat rows or plateau around a limited number of unique rows; explicitly document this if observed.
- `--level error` can include non-5xx rows such as `responseStatusCode: 200`; always filter client-side for response/status code beginning with `5` before reporting 5xx counts.
- If a query reaches a hard cap such as 1000 rows, report `>=1000` or `capped at 1000`, not exactly 1000.

Required status-specific queries:
Run explicit status checks for:
- `307`
- `308`
- `404`
- `500`
- `502`
- `503`
- `504`

Preferred CLI pattern, adjusted for the chosen window:

```bash
vercel logs --project corp-web-japan --environment production \
  --since '<WINDOW_START_ISO_WITH_OFFSET>' \
  --until '<WINDOW_END_ISO_WITH_OFFSET>' \
  --status-code 404 \
  --json --no-branch --scope querypie --limit 1000
```

Also run:

```bash
vercel logs --project corp-web-japan --environment production \
  --since '<WINDOW_START_ISO_WITH_OFFSET>' \
  --until '<WINDOW_END_ISO_WITH_OFFSET>' \
  --level error \
  --json --no-branch --scope querypie --limit 1000
```

Then client-side filter that result to actual 5xx statuses only.

Fallback query strategy:
- If `--status-code` is unsupported or unreliable in the current CLI, try `--search 'status:404'` for 404-like samples and use explicit integer status checks where supported.
- Do not use `--status-code 5xx` unless `vercel logs --help` and a probe prove it is accepted. Some Vercel paths require comma-separated integers only.
- If only live tailing by URL/deployment ID is supported, fall back to the direct Vercel request-log API if credentials allow it.
- For direct request-log API, explicitly filter `environment=production`; unfiltered project queries can be polluted by preview traffic.
- If neither CLI nor API can access historical logs, do not write a fake wiki report. Return a blocker summary with the exact failing prerequisite/query.

Recommended local parsing approach:
- Use a short Python helper or shell pipeline to execute each query, combine stdout/stderr, keep lines beginning with `{`, parse JSON, dedupe, and summarize.
- Normalize status fields from `responseStatusCode`, `statusCode`, or equivalent.
- Normalize path fields from `requestPath`, `path`, `uri`, or structured JSON embedded in `message` when available.
- For messages like `[runtime-404] {...}` and `[runtime-missing-redirect] {...}`, parse the trailing JSON object when possible to extract `requestedPath`, `redirectTarget`, `host`, `referer`, and `userAgent`.

Classification guidance:
- Scanner/probe noise examples include WordPress paths, `/.env*`, `/.git/*`, `/.ssh/*`, `/appsettings.json`, `/actuator/env`, `/api/config`, `/api/env`, `/secrets.json`, `/.well-known/traffic-advice`, `/xmlrpc.php`, `/wp-*`, `/cgi-bin/*`, `/swagger.json`, `/openapi.json`, `/runtime-config.js`, and similar config/secret/exploit probes.
- Do not recommend redirects for scanner/probe noise by default.
- Repeated application/content paths, canonicalization failures, or stale public route families may be actionable.
- Runtime logs do not capture every user-visible 404. Edge/static 404s may be absent from runtime logs. State this limitation if 404 volume is low or absent.
- If manual live checks are performed after log collection, record the check time and keep those checks in a separate section so they do not pollute log-derived counts.
- If a path-specific 404 looks like a malformed content URL with extra title text appended, inspect current production HTML/sitemap/repo content only if needed and classify whether current in-site emission is reproduced. Do not default to redirects for one-off external/cached malformed hits.

Report language and style:
- Write the wiki report in Korean.
- Keep technical terms such as Vercel, Runtime Log, HTTP, 5xx, 404, `production`, command snippets, and route paths as-is.
- Avoid leftover English section labels except where the existing wiki convention intentionally uses English product/technical names.
- Use markdown links for wiki references.
- Keep multiline runtime messages collapsed to one line in tables/lists.
- Frame the report as an operational snapshot, not a source-of-truth metrics system.

Required report template:

```markdown
# Vercel Runtime Log - {Mon D or date range}

날짜: {YYYY-MM-DD or YYYY-MM-DD ~ YYYY-MM-DD}
감사 수행 시각: {YYYY-MM-DD HH:mm:ss} KST
저장소 위키: `querypie/corp-web-japan`
참고 페이지:
- [Vercel Runtime Log - May 20](Vercel-Runtime-Log---May-20)
이번 감사에 사용한 제품 저장소 `origin/main` 스냅샷: `{sha}` (`{subject}`)
Vercel 프로젝트: `corp-web-japan`

## 범위

- 확인한 프로젝트: `corp-web-japan`
- 환경: `production`
- 요청한 KST 기준 로그 창:
  - `{start}`부터 `{end}`까지
- 실제 데이터 범위:
  - `{actual latest/earliest observed rows, or limitation}`
- 확인 초점:
  - `(uri, http code)` 기준 non-`200` runtime-log 응답
  - production `5xx` 이슈가 runtime log에 보이는지 여부
  - 접근 가능한 top-set 안의 주요 `404`/`307`/`308` 패턴

데이터 무결성 참고:
- Vercel historical log output은 broad/high-volume status query에서 JSON row를 반복 출력하거나 제한된 unique ID 수에서 plateau가 생길 수 있습니다.
- 아래 count는 보이는 행을 dedupe한 top-set count이며, 권위 있는 full-day traffic total이 아닙니다.
- Vercel runtime logs는 edge/static layer에서 처리된 모든 사용자-visible 404를 포괄하지 않을 수 있습니다.
- Manual live recheck를 수행했다면 로그 수집 후 실행했는지, 그리고 count에 포함될 수 있는지 분리해서 적습니다.

## 수집 방법과 조회 동작

사용한 주요 명령과 query shape를 요약합니다.

- broad query raw JSON rows: `{n}`
- broad query unique rows: `{n}`
- direct `307` unique rows: `{n}`
- direct `308` unique rows: `{n}`
- direct `404` unique rows: `{n}`
- direct `500` unique rows: `{n}`
- direct `502` unique rows: `{n}`
- direct `503` unique rows: `{n}`
- direct `504` unique rows: `{n}`
- `--level error` client-side `5xx` filter unique rows: `{n}`

## 요약

1. `{5xx finding}`
2. `{broad production status mix}`
3. `{redirect/canonicalization finding}`
4. `{404/scanner/stale-path finding}`

## 상태별 확인

### A. Broad production top-set

- 출력된 raw JSON lines: `{n}`
- Unique log IDs: `{n}`
- unique broad sample의 status mix: `{status mix}`

| URI | HTTP code | 보이는 수 |
|---|---:|---:|
| `{path}` | `{status}` | `{count}` |

대표적인 최신 broad rows:

- `{KST timestamp}` — `{status}` `{path}` — source `{source}`, deployment `{deploymentId}`

### B. Direct `307`/`308` findings

| URI | HTTP code | 보이는 수 | 해석 |
|---|---:|---:|---|
| `{path}` | `{status}` | `{count}` | `{classification}` |

### C. Direct `404` findings

| URI | HTTP code | 보이는 수 | 분류 |
|---|---:|---:|---|
| `{path}` | `404` | `{count}` | `{scanner/probe/stale-route/actionable}` |

대표적인 최신 `404` rows:

- `{KST timestamp}` — `404` `{path}` — source `{source}`, deployment `{deploymentId}` — `{one-line message}`

### D. Direct `5xx` findings

- direct `500`: `{n}`
- direct `502`: `{n}`
- direct `503`: `{n}`
- direct `504`: `{n}`
- `--level error` 중 client-side `5xx` filter: `{n}`

If any 5xx exists, include this table:

| 시각(KST) | HTTP code | URI | source | deployment | message |
|---|---:|---|---|---|---|

## 운영적 해석

- `{interpretation of 5xx}`
- `{interpretation of 404/307/308}`
- `{whether any route-policy follow-up is recommended}`

## Manual live recheck

Only include this section if manual checks were performed.

| 확인 시각(KST) | 경로 | 결과 | 비고 |
|---|---|---|---|

## 다음 조치 제안

1. `{next action or no immediate action}`
2. `{monitoring/reporting note}`

---
*Report generated by Hermes Agent.*
```

Wiki update requirements:
- Before editing, read the existing target page if it exists.
- Preserve useful prior content only if updating the same day; otherwise create a new dated page.
- Update `_Sidebar.md` in the same commit when creating a new dated report.
- Commit message format:
  `docs: add Vercel runtime log report for {YYYY-MM-DD}`
  or
  `docs: update Vercel runtime log report for {YYYY-MM-DD}`
- Push the wiki repo default branch.
- Verify push with:
  - `git status --short --branch`
  - `git log -1 --oneline`
  - `git ls-remote origin refs/heads/<wiki-branch>`

Failure handling:
- If Vercel auth is unavailable or invalid, do not fabricate a report. Write a concise final response explaining the auth blocker and the prerequisite that failed.
- If GitHub auth is unavailable or invalid, do not fabricate a wiki update. Report the exact `gh auth status` or git push failure.
- If the wiki repo has unrelated local changes, do not overwrite them. Report the dirty files and stop unless you can isolate your changes safely.
- If GitHub wiki push fails because the remote advanced, fetch and rebase the wiki branch, resolve only your report/sidebar changes, then push again.
- If the report page can be written locally but cannot be pushed, report the local file path and exact push error.
- If Vercel logs return no rows, distinguish between `no logs in the accessible window` and `query/auth/tool failure` using the prerequisite and small existence-check evidence.
- If the task cannot complete, final response should be a blocker report, not a partial success claim.
```

## Notes for future maintainers

- The schedule is intentionally near the end of the KST day because the task cannot reliably access arbitrary historical runtime logs beyond the recent 24-hour window.
- If the desired report should represent a completed calendar day after midnight, the collection layer must be changed to store logs before they expire; otherwise the beginning of the prior day can be lost.
- If the Vercel CLI behavior changes, update the prompt after confirming the new `vercel logs --help` output and a small successful probe query.
- Keep the attached skill list and the embedded prompt in sync. The attached skills provide better current pitfalls, while the embedded prompt lets a fresh cron session continue even if skill loading fails.
