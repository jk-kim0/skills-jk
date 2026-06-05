# Next.js on Vercel: ESM package scope vs CJS launcher regression forensics

Use this reference when a Vercel deployment is `READY` and GitHub/Vercel checks are green, but every app route returns 500 with `ERR_REQUIRE_ESM`.

## Signature

Runtime log examples:

```text
Failed to handle / Error: require() of ES Module /var/task/front/.next/server/app/page.js from /var/task/front/___next_launcher.cjs not supported.
page.js is treated as an ES module file as it is a .js file whose nearest parent package.json contains "type": "module".
```

The same shape can appear for any App Router entry:

```text
/var/task/front/.next/server/app/login/page.js
/var/task/front/.next/server/app/[teamSlug]/home/page.js
/var/task/front/.next/server/app/api/auth/google/start/route.js
```

Typical metadata:

- `source`: `serverless`
- `responseStatusCode`: `500`
- deployment state: `READY`
- Vercel deployment metadata may include `bundler: "turbopack"`

## Investigation pattern

1. Confirm live behavior with `curl -D -` on the exact alias.
2. Inspect the deployment to get the deployment id and commit metadata.
3. Query deployment logs with `--level error`; `--status-code 500` may miss rows in some cases.
4. Check whether production/main has the same error before blaming the current PR.
5. Use `vercel list <project> --format json --status READY` to collect recent deployment metadata.
6. For each recent deployment URL, run a small `curl` status probe for representative routes such as `/`, `/login`, and a known team route.
7. Find the first transition from normal status (`200`/`307`) to `500` in chronological order.
8. Map that deployment's `githubPrId`, `githubCommitSha`, `githubCommitRef`, and commit message back to the PR.
9. Distinguish:
   - latent compatibility condition, such as an existing `package.json` `"type": "module"`
   - triggering PR, where the first Vercel deployment actually starts returning 500

## Interpretation guidance

Do not stop at the file named in the error (`app/page.js`, `login/page.js`, etc.). In this failure mode, the route file is often only the entry that the Vercel launcher tried to load. The triggering PR may have changed a shared runtime import, auth module, credential loader, or other server-side dependency that changes how the serverless bundle is emitted/loaded.

If a later PR preview is failing, check current production/main too. A later preview can be a victim of an already-broken main deployment, not the root cause.

## Reporting shape

Report two layers separately:

- `latent condition PR`: the PR that introduced the package/runtime condition if identifiable
- `first failing Vercel deployment / triggering PR`: the first deployment where status probes changed to 500

Also state whether CI/Vercel checks were green despite runtime 500, and recommend a post-deploy HTTP smoke check if deploy checks only validate build success.
