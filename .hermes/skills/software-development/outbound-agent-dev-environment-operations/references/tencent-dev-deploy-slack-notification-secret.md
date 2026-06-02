# Tencent dev deploy Slack notification secret triage

Use this when `#alerts-outbound-dev` does not show messages after a main push / PR merge deploy, even though the deploy workflow ran.

## Symptom

`PR Cache-Only Build Validation / Main Deploy outbound-front image` has a `Notify Slack - main deploy started` job, but no Slack message appears in `#alerts-outbound-dev`.

Typical failed job log:

```text
SlackError: Missing input! A token must be provided to use the method decided.
```

This means the Slack GitHub Action did not receive a token at all. Investigate repository secret availability before assuming channel ID, Slack scopes, or payload JSON issues.

## Evidence checklist

1. Inspect the deploy workflow run jobs.
   - `gh run view <run-id> --json status,conclusion,headSha,jobs`
   - Check `Notify Slack - main deploy started` and `Notify Slack - main deploy result` separately.

2. Read the failed Slack notify job log.
   - `gh run view <run-id> --job <job-id> --log`
   - If the log says token is missing, the failure is at GitHub secret wiring, not Slack channel posting.

3. Verify the repository Actions secret exists.
   - `gh secret list --repo querypie/outbound-agent --app actions`
   - `SLACK_BOT_TOKEN` must be present.

4. If the secret is missing, retrieve the approved Slack bot token from the credential store without printing it.
   - For outbound-agent dev deploy alerts, the approved source is 1Password Dev vault item `Slack App OAuth Token (Ironman)`.
   - Validate only shape/presence in logs (`xoxb-...`, length, field label), never the token value.
   - Confirm with Slack API read calls if needed:
     - `auth.test` should return `ok=true`.
     - `conversations.info?channel=C0B7SA4N620` should identify `alerts-outbound-dev`.

5. Register the secret.
   - `printf '%s' "$token" | gh secret set SLACK_BOT_TOKEN --repo querypie/outbound-agent --app actions`
   - Re-run `gh secret list` and verify `SLACK_BOT_TOKEN` appears with an updated timestamp.

6. Verify posting capability.
   - Prefer a short diagnostic `chat.postMessage` to `C0B7SA4N620` after secret registration.
   - Report only `ok`, channel ID, timestamp presence, and safe error text.

## Important workflow behavior

If `notify-start` already failed before the secret was registered, the same run may not send a final update because `notify-result` can depend on `needs.notify-start.result == 'success'` and on the missing start message timestamp. Do not expect the already-running deployment to recover its Slack thread automatically. The next main push / PR merge deploy should post normally after `SLACK_BOT_TOKEN` is configured.

## Pitfalls

- Do not diagnose `#alerts-outbound-dev` channel membership first when the Slack Action log says token is missing. The Slack API call never reached channel authorization.
- Do not print bot tokens in chat, logs, PR bodies, or docs.
- Do not treat public deploy success as notification success; Slack notify jobs are independent workflow jobs and need their own evidence.
