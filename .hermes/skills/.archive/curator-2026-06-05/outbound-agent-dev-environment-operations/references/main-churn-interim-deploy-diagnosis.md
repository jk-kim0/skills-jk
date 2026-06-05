# Main-churn interim deploy diagnosis

Use when checking outbound-agent dev deployment status while `origin/main` is moving and the user asks for Vercel plus Dev Seoul/Tokyo status.

## Observed pattern

- A latest `origin/main` SHA can be superseded while its deployment checks are still running.
- Vercel production deploy for the superseded SHA may complete and attach the `outbound-dev.vercel.app` alias, while a newer SHA immediately starts a new Vercel production deploy.
- Tencent main image deploy is sequential and concurrency-cancelled by newer pushes. When an older image publish job is `cancelled`, downstream Seoul/Tokyo deploy jobs may appear as `skipped`; classify that as superseded by a newer main push, not as a Seoul/Tokyo runtime failure.
- Seoul/Tokyo `/login` 200 during this window proves public health only. It does not prove the newest SHA is deployed.

## Recommended diagnosis sequence

1. Fetch `origin/main` and record the current SHA.
2. Inspect recent main runs for all three workflows:
   - `Deploy outbound-dev Production`
   - `CI`
   - `PR Cache-Only Build Validation / Main Deploy outbound-front image`
3. If a run is cancelled/skipped, re-fetch `origin/main` before diagnosing. If a newer main SHA exists and has fresh runs, treat the older run as superseded unless logs show an independent failure.
4. For Vercel, check both:
   - `vercel inspect https://outbound-dev.vercel.app --scope querypie --no-color` for the active alias.
   - `vercel ls outbound-dev --scope querypie --prod --meta githubCommitSha=<sha> --no-color` for exact commit deployment.
5. For Tencent, report job state separately:
   - image publish
   - Seoul deploy
   - Seoul cleanup/smoke
   - Tokyo deploy
   - Tokyo cleanup
6. If latest Vercel/Tencent runs are still in progress and the user did not ask to block until completion, give an interim diagnosis and start a short background watcher with `notify_on_complete` rather than waiting silently.

## Classification language

- `Vercel/outbound-dev: public health OK; SHA <old> deployed successfully, but latest SHA <new> is still Building/in progress.`
- `Dev Seoul: /login 200; latest Tencent deploy has not reached the Seoul deploy job yet, so this is healthy but not latest-proven.`
- `Dev Tokyo: /login 200; older run skipped due to main churn, newest Tokyo deploy pending/not started.`

## Pitfall

Do not collapse Vercel and Tencent into a single deployment status. Vercel can be Ready for one SHA while Tencent is cancelled/skipped for that SHA and a newer SHA is pending.