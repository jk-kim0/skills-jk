# Vercel Protection Bypass for Automation for corp-web-app stage E2E

Use this when GitHub Actions Playwright E2E against `https://stage.querypie.com` reaches `Vercel Security Checkpoint`, `Failed to verify your browser`, or HTTP 403 before the page renders.

## Why this is the durable fix

Vercel's official Protection Bypass for Automation lets automation send a project-scoped secret in either:

- HTTP header: `x-vercel-protection-bypass: <secret>`
- query parameter: `x-vercel-protection-bypass=<secret>`

For browser tests, also send:

- `x-vercel-set-bypass-cookie: true`

This sets a bypass cookie for follow-up in-browser requests. Vercel documents this path as bypassing Bot Protection challenges, while active DDoS/security mitigations can still block traffic.

## Hermes/local shell pitfall

In this user's setup, `VERCEL_TOKEN` may be present only in interactive zsh, not in Hermes's default non-interactive terminal environment and not necessarily in `zsh -lc`.

Check it with:

```bash
zsh -ic 'printf "VERCEL_TOKEN=%s len=%s\n" "${VERCEL_TOKEN:+set}" "${#VERCEL_TOKEN}"'
```

Run Vercel CLI/API probes through interactive zsh when needed:

```bash
zsh -ic 'vercel whoami --token "$VERCEL_TOKEN"'
```

Do not report that Vercel logs/API are unavailable until this interactive-zsh check has been tried.

## corp-web-app identifiers observed in this session

- Vercel team/account: `querypie-4030`
- projectName: `corp-web-app`
- projectId: `prj_1PANizagPBzs7OF4efV8QoMAhgzx`
- teamId/orgId: `team_8DsCdrF1uCfwY30OS8F8lREn`

Reconfirm these from `.vercel/project.json` or the Vercel API before making changes if significant time has passed.

## Create the bypass secret via REST API

Vercel CLI does not expose a high-level `vercel protection-bypass` command in CLI 48.2.9. Use the REST API:

```bash
zsh -ic '
set -euo pipefail
BYPASS_SECRET="$(openssl rand -hex 32)"

curl -sS -X PATCH \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.vercel.com/v1/projects/prj_1PANizagPBzs7OF4efV8QoMAhgzx/protection-bypass?teamId=team_8DsCdrF1uCfwY30OS8F8lREn" \
  -d "$(jq -n --arg secret "$BYPASS_SECRET" --arg note "GitHub Actions Contact Us E2E" \
    '\''{generate: {secret: $secret, note: $note}}'\'')" \
  >/tmp/vercel-bypass-create.json

printf "%s" "$BYPASS_SECRET" | gh secret set VERCEL_AUTOMATION_BYPASS_SECRET --repo querypie/corp-web-app
'
```

Security notes:

- Do not print the generated secret.
- Do not commit the secret.
- Store it in GitHub Actions as `VERCEL_AUTOMATION_BYPASS_SECRET`.
- The same generated value is the one Playwright should send in the `x-vercel-protection-bypass` header.

## Playwright config pattern

```ts
const vercelAutomationBypassSecret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;

export default defineConfig({
  use: {
    extraHTTPHeaders: vercelAutomationBypassSecret
      ? {
          'x-vercel-protection-bypass': vercelAutomationBypassSecret,
          'x-vercel-set-bypass-cookie': 'true',
        }
      : undefined,
  },
});
```

In the GitHub Actions workflow, fail fast if the secret is absent so the error is actionable instead of another ambiguous checkpoint failure.

## Verification

After setting the GitHub secret:

```bash
gh workflow run e2e-contact-us-stage.yml --repo querypie/corp-web-app --ref <pr-branch>
```

Then inspect the run. A missing secret should fail in the explicit preflight step. With the secret set, the test should proceed past Vercel checkpoint and fail only on real page/form assertions if any remain.
