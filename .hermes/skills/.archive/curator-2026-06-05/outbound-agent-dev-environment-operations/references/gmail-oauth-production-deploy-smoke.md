# Gmail OAuth production deployment smoke pattern

Use this reference when verifying Outbound Agent Gmail OAuth after a PR merge or environment-variable update on `outbound-dev`.

## What to verify before full Gmail consent

When the Google account with `querypie-saas-dev` access is not available yet, still collect useful deployment/OAuth evidence without completing consent:

1. Confirm the merged PR's own deploy run, not only the current alias.
   - `gh run view <run-id> --json status,conclusion,headSha,createdAt,updatedAt,url,jobs`
   - Extract the Vercel deployment id from the run log with `grep -Eo 'dpl_[A-Za-z0-9]+'`.
   - `vercel inspect <deployment-id> --scope querypie` and record `target=production`, `status=Ready`, aliases, and region.
2. If main advanced after the PR merge, state both facts:
   - the PR merge SHA deployed successfully, and
   - the live alias may now point at a newer main deployment.
3. Trigger a fresh manual Production deployment when the task asks for a new post-merge deployment:
   - `gh workflow run deploy-outbound-dev-production.yml -f BRANCH=main`
   - Watch the run or poll it; then inspect the new `dpl_...` deployment.
4. Verify Vercel env key presence without values:
   - `vercel env ls --scope querypie` and confirm the Gmail keys exist for Production/Preview.
   - Never print secret values.
5. Run runtime smoke against the alias:
   - `E2E_BASE_URL=https://outbound-dev.vercel.app npm run test:e2e:runtime-smoke` from `front/` when dependencies are present.
6. Run OAuth-start smoke up to the Google sign-in page:
   - log in to `/login`, navigate to `/<teamSlug>/settings/email-senders`, click `Connect Gmail`.
   - Confirm the resulting Google URL includes:
     - `client_id=<Outbound OAuth client id>`
     - `redirect_uri=https%3A%2F%2Foutbound-dev.vercel.app%2Fapi%2Fgmail%2Foauth%2Fcallback`
     - `scope=openid+email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.send`
   - Confirm the page is a Google sign-in/consent page, not `redirect_uri_mismatch` / `Error 400`.

## Google Console access check

Before claiming Authorized redirect URI registration was live-verified, check the active Google account and project access:

```bash
gcloud auth list --format='table(account,status)'
gcloud config get-value account
gcloud config get-value project
gcloud projects describe querypie-saas-dev --format='json(projectId,projectNumber,name)'
```

If the active account lacks access to `querypie-saas-dev`, report that Google Console live verification is blocked until the user authenticates an account with that project access. Do not substitute `querypie-deck-dev` or a personal Deck development account as evidence for the Outbound OAuth client.

## Evidence to capture after full consent

Once a suitable Google account can complete consent, continue with:

- successful callback back to `/<teamSlug>/settings/email-senders?gmail=connected...`
- Team Email Senders table row showing provider `Gmail sender`, connected account, sender address, and `active` health
- Sales Person sender selection saved to that Gmail sender
- Gmail test send result
- 1-recipient actual send result
- provider evidence such as Gmail message id/thread id, if exposed by the UI/database/logs

## Pitfalls

- A successful Vercel alias smoke is not enough to prove the exact PR SHA deployed; use the GitHub run and Vercel deployment id for exact-version evidence.
- OAuth start reaching Google sign-in proves redirect URI/client/scope compatibility but not refresh-token persistence or actual send. Label it as pre-consent smoke, not full Gmail connect smoke.
- Do not claim Google Console Authorized redirect URI registration was checked from live Console/API when `gcloud` is authenticated as an account without `querypie-saas-dev` permission.
