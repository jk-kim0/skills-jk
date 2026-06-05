# Next.js ESM/CJS launcher runtime 500 on Vercel

Use this reference when a Vercel deployment is `READY` and GitHub/Vercel checks are green, but the live page returns `500`.

## Observed signature

Runtime log entries can look like:

```text
Failed to handle / Error: require() of ES Module /var/task/front/.next/server/app/page.js from /var/task/front/___next_launcher.cjs not supported.
page.js is treated as an ES module file as it is a .js file whose nearest parent package.json contains "type": "module" ...
code: 'ERR_REQUIRE_ESM'
```

Key fields:

- `source`: `serverless`
- `responseStatusCode`: `500`
- `message`: contains `___next_launcher.cjs`, `.next/server/app/page.js`, and `ERR_REQUIRE_ESM`

## Diagnosis pattern

1. Confirm the failing URL with `curl -D -` and note `x-matched-path: /500` and the deployment id embedded in the error HTML or from `vercel inspect`.
2. Run deployment-scoped logs with `--level error`; a status-code-only query can return no rows in some cases.
3. Inspect both the Preview alias and the stable production alias. If both show the same signature, do not attribute the issue to a feature PR diff by default.
4. Compare the PR diff against `origin/main` for `package.json`, `vercel.json`, `next.config.*`, and lockfile changes. If none changed, classify it as a runtime/deployment compatibility issue rather than the UI change itself.
5. Inspect Vercel project settings (`vercel project inspect <project>`) for root directory, Node.js version, framework preset, build command, and output directory.
6. Check whether GitHub/Vercel deploy checks only validate build/deploy completion. A `READY` deployment can still fail on first runtime request when no post-deploy HTTP smoke check exists.

## Likely remediation directions

- Review whether the app-level `package.json` must keep `"type": "module"`; if not required, test removing it or switching to CommonJS semantics while preserving explicit `.mjs` config files.
- Add a post-deploy smoke check for `/`, `/login`, or another guaranteed route so runtime 500s fail the deployment check instead of passing as green.
- Treat the fix as deploy/runtime infrastructure work when production and preview are both affected, even if the first report came from a PR Preview URL.
