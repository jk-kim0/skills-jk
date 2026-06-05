# Vercel / Next.js ESM runtime incident forensics

Use this reference when an Outbound Agent Vercel deployment is `Ready` but returns HTTP 500 at runtime, especially with `ERR_REQUIRE_ESM` or `___next_launcher.cjs` in logs.

## Key lesson

When the user asks for the PR that broke a previously working deployment, identify the first deployment where live HTTP behavior changed from healthy to failing.
Do not answer only with the commit that introduced a latent precondition.

Report these as separate layers:

1. Incident culprit / trigger PR: first PR whose Vercel deployment changed healthy routes into runtime 500s.
2. Latent precondition PR: earlier PR that introduced a setting or code path that only became harmful later.
3. Fix PR: later remediation PR, if one exists.

## Evidence pattern

1. Find adjacent merged PRs around the incident window with `gh pr view` and `git log --first-parent`.
2. Pull GitHub deployment records for `main` and identify the deployment attached to each merge SHA.
3. For adjacent candidate deployments, read deployment statuses to get immutable Vercel URLs.
4. Smoke immutable URLs directly, preserving redirects:

```bash
curl -sS -o /tmp/body -D /tmp/headers -w '%{http_code} %{redirect_url}\n' 'https://<deployment>.vercel.app/'
curl -sS -o /tmp/body -D /tmp/headers -w '%{http_code} %{redirect_url}\n' 'https://<deployment>.vercel.app/login'
curl -sS -o /tmp/body -D /tmp/headers -w '%{http_code} %{redirect_url}\n' 'https://<deployment>.vercel.app/api/auth/google/start'
```

5. Query runtime logs and match the failing deployment ID/signature.
6. Only then name the culprit PR.

## Outbound Agent observed signature

A broken deployment can be `Ready` in Vercel while runtime routes all fail:

```text
Failed to handle / Error: require() of ES Module /var/task/front/.next/server/app/page.js
from /var/task/front/___next_launcher.cjs not supported.
page.js is treated as an ES module file as it is a .js file whose nearest parent package.json
contains "type": "module" which declares all .js files in that package scope as ES modules.
code: 'ERR_REQUIRE_ESM'
```

The same pattern can appear for `/login` and API routes such as `/api/auth/google/start`.

## Interpretation rule for `type: module`

For this Next.js/Vercel app, package-wide `"type": "module"` in `front/package.json` can force generated `.next/server/app/**/*.js` files to be interpreted as ESM while Vercel's CommonJS launcher loads them with `require()`.

Do not automatically blame the PR that first introduced `"type": "module"` if later deployments remained healthy.
Call it a latent precondition unless it is also the first bad deployment.

A correct incident report should say, for example:

```text
Incident culprit: PR that first produced runtime 500s.
Latent precondition: earlier PR that introduced front/package.json "type": "module".
```

## Remediation pattern

Prefer removing package-wide `"type": "module"` from the Next app package and using `.mjs` / `.cjs` for individual files that require explicit module semantics.
Add deployment smoke checks after Vercel deploy so build/deploy `Ready` cannot mask runtime entry loading failures.

Recommended smoke contract for Outbound Agent:

```text
/      -> 307
/login -> 200
```

If `/api/auth/google/start` is checked, missing config should redirect to login with a controlled failure reason, not return 500.
