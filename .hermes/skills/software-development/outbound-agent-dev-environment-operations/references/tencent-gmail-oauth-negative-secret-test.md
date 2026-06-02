# Tencent Gmail OAuth negative-secret test

Use this reference when the user explicitly asks to validate Gmail OAuth failure behavior by deploying an intentionally wrong `GMAIL_OAUTH_CLIENT_SECRET` to Tencent dev VMs.

## Intent

This is an intentional negative test, not a credential-repair task. Do not try to correct the secret or redirect the task into normal OAuth smoke success. The success condition is that the runtime is updated/restarted with the bad secret and remains publicly reachable so the product OAuth flow can be tested for the expected `invalid_client`/token-exchange failure.

## Safe operational pattern

1. Keep secret values out of chat and logs.
   - It is acceptable to report repo secret key names and `updatedAt` timestamps.
   - Do not print the wrong secret value after setting it.
2. Update the repo-level GitHub Actions secret consumed by the Tencent container-image workflow:
   - `GMAIL_OAUTH_CLIENT_SECRET` is common for Seoul/Tokyo when both use the shared OAuth client.
   - Leave `GMAIL_OAUTH_CLIENT_ID`, token encryption secrets, and state secrets unchanged unless the user explicitly requests otherwise.
3. Deploy/restart the currently intended image with Gmail config sync enabled:
   - `target=all` when both Seoul and Tokyo are requested.
   - `image=<current known-good outbound-front image>`.
   - `dry_run=false`.
   - `confirm_apply=APPLY`.
   - `update_gmail_oauth_config=true`.
4. Verify at job/step level, not only top-level run status:
   - `Validate deployment input` succeeded.
   - Each target job ran.
   - `Upload Gmail OAuth config update` succeeded for each target.
   - `Run deployment` succeeded for each target.
5. Verify public availability after restart:
   - `https://outbound-tokyo.dev.querypie.io/login` returns HTTP 200.
   - `https://outbound-seoul.dev.querypie.io/login` returns HTTP 200.

## Reporting

Report:

- GitHub Actions run URL.
- Target and image used.
- That `update_gmail_oauth_config=true` and `dry_run=false` were used.
- Per-target success for both config upload and deployment/restart.
- Public `/login` status for each target.
- That secret values were not exposed.

If the user later asks to restore the valid secret, use the same workflow shape after replacing `GMAIL_OAUTH_CLIENT_SECRET` with the valid value from the approved secret source.