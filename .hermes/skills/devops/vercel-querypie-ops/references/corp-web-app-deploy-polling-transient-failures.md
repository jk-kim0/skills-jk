# corp-web-app deploy polling transient failures

Use this when `corp-web-app` GitHub Actions staging/production/preview deploy workflows fail even though the Vercel deployment later appears as `Ready`.

## Symptom signature

- GitHub Actions workflow such as `Deploy on Staging` fails in `Run Deploy Script`.
- Log shows deployment was created and repeated status polling, for example:
  - `Deployment created: ID dpl_..., status INITIALIZING`
  - `Deployment status: BUILDING`
  - `Error: Unable to make request: TypeError: fetch failed`
- `vercel inspect <deployment-id> --scope querypie` shows the deployment is actually `Ready` and aliases such as `stage.querypie.com` are attached.
- Route probes on the stage URL return 200 and expected metadata/content is present.

## Root cause pattern

This is usually not a Next.js build/runtime failure and not necessarily caused by the merged PR's app code. It can be a transient Vercel API/network failure while `scripts/deploy/index.js` polls deployment status via `vercel.deployments.getDeployment(...)`.

The deployment can finish successfully on Vercel while the GitHub workflow exits non-zero because the polling API request failed once and the script treated that as fatal.

## Investigation steps

1. Identify the failed workflow and head SHA:
   - `gh run list --branch main --limit 20 --json databaseId,workflowName,conclusion,status,headSha,displayTitle,url`
   - `gh run view <run-id> --log`
2. Extract the deployment ID from the log (`dpl_...`).
3. Inspect the deployment without creating a new deployment:
   - `vercel inspect <deployment-id> --scope querypie`
4. If the deployment is `Ready`, verify aliases and a small set of affected routes:
   - `curl -I https://stage.querypie.com/<path>`
   - for metadata changes, fetch the HTML and inspect relevant `<meta>` tags.
5. Compare the app/PR evidence against the deploy script evidence before changing code. If app checks pass and only polling failed, fix the deploy polling path rather than reverting the app PR.

## Durable fix pattern

In `scripts/deploy/index.js`, keep existing semantic failures intact:

- 404/cancelled deployment remains a cancellation/removal signal and can use the outer deployment retry flow.
- terminal deployment statuses such as `ERROR`, `CANCELED`, or timeout remain failures.

Add bounded retry around `vercel.deployments.getDeployment(...)` for transient request errors such as `TypeError: fetch failed`:

- retry a small fixed number of times, e.g. 3
- sleep briefly between retries, e.g. 5 seconds
- log the retry attempt and original error message
- after the retry budget is exhausted, rethrow the original error

Do not run a bare `vercel` command while investigating; use `vercel inspect`, `vercel ls`, or `vercel logs` explicitly.

## Verification

- Source checks:
  - `node --check scripts/deploy/index.js`
  - `npx --yes prettier --check scripts/deploy/index.js`
- Operational checks:
  - `vercel inspect <deployment-id> --scope querypie`
  - targeted `curl -I` or HTML metadata probes for the affected stage routes
- After the fix PR merges, check the next `Deploy on Staging` run rather than assuming the PR preview deploy proves the staging workflow path.