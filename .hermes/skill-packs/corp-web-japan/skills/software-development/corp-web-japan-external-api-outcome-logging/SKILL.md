---
name: corp-web-japan-external-api-outcome-logging
description: Add structured skip/success/failure logging for shared external API calls in corp-web-japan, with endpoint-aware context and mirrored tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, logging, vercel, slack, salesforce, external-api, testing]
---

# corp-web-japan external API outcome logging

Use this when the user wants reliable runtime-log visibility for external API calls under `src/lib/forms/server/`, especially Slack and Salesforce, and wants to distinguish which local endpoint triggered the call.

## Goal

For every external API call:
- log success, skip, and failure explicitly
- use log level by outcome:
  - success -> `console.info`
  - skipped -> `console.warn`
  - failed -> `console.error`
- include endpoint identity such as:
  - `endpointName: "contact-us"`
  - `endpointName: "gating-form"`
- include request path when available, for example:
  - `/contact-us/submit`
  - `/api/gating-form/unlock`

This makes Vercel runtime logs operationally useful when the user wants to confirm whether Slack/Salesforce actually succeeded, skipped, or failed.

## Proven approach

### 1. Add one shared structured logging helper under `src/lib/forms/server/`

Create a small helper such as:
- `src/lib/forms/server/external-api-log.ts`

Recommended shape:
- `service`: `"slack" | "salesforce" | "license"`
- `endpointName`: local logical endpoint, e.g. `contact-us`, `gating-form`
- `requestPath`: local URI path, e.g. `/contact-us/submit`
- `outcome`: `success | skipped | failed`
- optional details:
  - `reason`
  - `remoteUrl`
  - `statusCode`
  - `recordUUID`

Recommended emit format:
- prefix with a stable token such as `[external-api]`
- then JSON stringify the payload

Example:
```ts
console.info(`[external-api] ${JSON.stringify(entry)}`)
```

Reason:
- structured logs are easier to query in Vercel runtime logs
- the prefix makes them visually searchable
- shared helper keeps level/outcome semantics consistent

### 2. Move outcome classification into the shared API helpers themselves

Do not leave logging responsibility only in callers.

For helpers such as:
- `src/lib/forms/server/salesforce-delivery.ts`
- `src/lib/forms/server/slack-notification.ts`

make the helper itself decide:
- skipped
- success
- failed

This ensures every caller gets consistent logs.

### 3. Prefer result objects over exception-only control flow for expected skip/fail states

For operationally expected states like:
- missing Slack credentials
- missing Salesforce endpoint
- Slack API non-OK response
- Salesforce response missing `recordUUID`

prefer returning a result object like:
- `{ ok: true }`
- `{ ok: false, reason: "missing_credentials" }`
- `{ ok: false, reason: "missing_endpoint" }`

instead of relying only on thrown exceptions.

This makes it easier to:
- log exact outcome once
- map caller HTTP status consistently
- test skip/success/failure behavior directly

### 4. Log-level mapping that worked well

#### Slack
- missing token/channel -> warn + `reason: "missing_credentials"`
- Slack API failure -> error + `reason: "api_<error-or-status>"`
- success -> info

#### Salesforce
- missing endpoint -> warn + `reason: "missing_endpoint"`
- HTTP failure -> error + `reason: "http_<status>"`
- missing success ID field -> error + `reason: "missing_recordUUID"` (or current configured field)
- request exception -> error + `reason: "request_error"`
- success -> info + include `recordUUID`

### 5. Make callers pass explicit endpoint context

Update higher-level callers such as:
- `src/lib/contact-us-submit.ts`
- `src/lib/gating-form-submit.ts`

to pass explicit context into shared helpers.

Recommended examples:

```ts
await deliverSalesforcePayload({
  endpoint: process.env.SALESFORCE_ENDPOINT,
  endpointName: "contact-us",
  requestPath: "/contact-us/submit",
  payload,
  successIdField: "recordUUID",
})
```

```ts
await postSlackNotification({
  endpointName: "gating-form",
  requestPath: "/api/gating-form/unlock",
  requestBody,
  token: slackToken,
  channel: slackChannel,
  title: "New Gated Document Unlock Received",
})
```

Important lesson:
- do not rely only on a string like `[contact-us]` in `logPrefix`
- use explicit fields so logs are machine-readable and consistent

### 6. Keep caller-facing HTTP behavior aligned with helper results

After converting helpers to structured result returns:
- caller should translate `missing_credentials` to the existing server/config error status if appropriate
- caller should translate other failed external API results to request-processing failure status

In the observed implementation:
- Slack `missing_credentials` maps to `500`
- other Slack failures map to `502`

### 7. Test this with a strict RED -> GREEN sequence

Add failing tests first for:
- helper log payload content
- helper log level by outcome
- caller passing endpointName/requestPath

Useful test files:
- `tests/src/lib/forms/server/slack-notification.test.mjs`
- `tests/src/lib/forms/server/salesforce-delivery.test.mjs`
- `tests/src/lib/contact-us-submit.test.mjs`
- `tests/src/lib/gating-form-submit.test.mjs`

What to verify directly:
- skip logs use `console.warn`
- success logs use `console.info`
- failure logs use `console.error`
- log JSON includes:
  - `service`
  - `endpointName`
  - `requestPath`
  - `outcome`
  - `reason` where applicable
- Salesforce success includes `recordUUID`
- callers contain explicit `endpointName` and `requestPath` wiring

### 8. Existing TS test harness pattern works well here

This repo already has a useful loader:
- `tests/helpers/ts-module-loader.mjs`

Use it to import `.ts` helper modules in `.mjs` tests.

Useful tactics:
- stub `global.fetch`
- temporarily replace `console.info`, `console.warn`, `console.error`
- capture emitted log strings and assert against JSON fragments

Pattern used successfully:
```js
const originalInfo = console.info
const infoLogs = []
console.info = (...args) => infoLogs.push(args.map(String).join(" "))
```

### 9. Runtime-log motivation

This pattern was driven by a real operational need:
- Vercel runtime logs previously showed Salesforce success clearly
- Slack success was not directly visible
- user wanted to know whether Slack was actually delivered after form submission

Structured outcome logging closes that observability gap.

## Important finding about license issuance

During this work, no current license-issuance external API caller was found in the `corp-web-japan` repository.

Practical implication:
- implement the shared logger with `service: "license"` support now
- but do not claim license logging is wired until an actual caller exists
- when a future license external API caller is added, use the same helper and endpoint-context pattern immediately

## Verification that worked

Fast targeted RED/GREEN:
```bash
node --test \
  tests/src/lib/forms/server/slack-notification.test.mjs \
  tests/src/lib/forms/server/salesforce-delivery.test.mjs \
  tests/src/lib/contact-us-submit.test.mjs \
  tests/src/lib/gating-form-submit.test.mjs
```

Then repo baseline:
```bash
npm run test
```

## Pitfalls

1. If Slack helper still throws on missing credentials, skip cases cannot be logged as warnings cleanly.
2. If callers keep only legacy `logPrefix` strings, runtime logs remain harder to query and compare.
3. If you forget to pass `endpointName` and `requestPath`, shared logs lose the local endpoint identity the user asked for.
4. If tests only assert returned result objects but not console level/payload, logging regressions can slip through.
5. Do not promise license logging is implemented unless the repo actually contains a license external API caller.

## Done criteria

- shared helper exists for structured external API log emission
- Slack helper logs skipped/success/failed with warn/info/error respectively
- Salesforce helper logs skipped/success/failed with warn/info/error respectively
- callers pass explicit `endpointName` and `requestPath`
- tests cover helper outcomes and caller wiring
- `npm run test` passes
