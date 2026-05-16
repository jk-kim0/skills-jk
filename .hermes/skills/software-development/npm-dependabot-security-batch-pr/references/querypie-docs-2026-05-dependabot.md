# querypie-docs Dependabot batch PR notes (2026-05)

Context: `querypie/querypie-docs` Dependabot security page had many npm alerts across three manifests:

- root `package-lock.json`
- `scripts/deploy/package-lock.json`
- `scripts/website-analysis/package-lock.json`

## Useful alert inventory command

```bash
gh api -H 'Accept: application/vnd.github+json' \
  /repos/querypie/querypie-docs/dependabot/alerts --paginate \
  --jq '.[] | select(.state=="open") | {number,package:.dependency.package.name,ecosystem:.dependency.package.ecosystem,manifest:.dependency.manifest_path,severity:.security_advisory.severity,summary:.security_advisory.summary,vulnerable:.security_vulnerability.vulnerable_version_range,patched:.security_vulnerability.first_patched_version.identifier}'
```

## Root manifest pattern

Direct updates:

- `next`, `@next/third-parties`, `eslint-config-next` -> `16.2.6`

Targeted overrides were needed for transitive advisories including:

- `@xmldom/xmldom`
- `dompurify`
- `fast-uri`
- `fast-xml-builder`
- `fast-xml-parser`
- `flatted`
- `mermaid`
- `uuid`
- `brace-expansion` under multiple `minimatch` majors
- `picomatch` under `micromatch`, `tinyglobby`, `vite`, `vitest`
- `postcss` under `next`, `styled-components`, `vite`
- `yaml` under `nextra`, `vite`, and old OpenAPI packages

Important: do not add `mermaid` as a new direct dependency just to satisfy a transitive alert if `@theguild/remark-mermaid` already owns it. Prefer an override so the app dependency surface stays narrow.

## scripts/deploy pattern

`@vercel/sdk` update alone may not clear advisories. Add targeted overrides for patched transitive packages if still vulnerable:

- `hono`
- `@hono/node-server`
- `fast-uri`
- `ip-address`
- `express-rate-limit`
- `path-to-regexp`

Verify with:

```bash
npm --prefix scripts/deploy audit --json
npm --prefix scripts/deploy ls hono @hono/node-server fast-uri --package-lock-only
npm --prefix scripts/deploy ls ip-address express-rate-limit path-to-regexp --package-lock-only
```

## scripts/website-analysis pattern

Avoid blindly bumping Puppeteer to the latest major if it introduces a stricter local Node engine than the repo/environment currently uses. In this case latest `puppeteer@25` warned for local Node `v22.10.0`; keeping the existing `^24.x` line and adding transitive overrides cleared audit without the engine warning:

- `basic-ftp`
- `ip-address`

Verify with:

```bash
npm --prefix scripts/website-analysis audit --json
npm --prefix scripts/website-analysis ls basic-ftp ip-address puppeteer --package-lock-only
```

## Hermes CLI pitfall

A combined command like:

```bash
npm ls @xmldom/xmldom brace-expansion dompurify fast-uri fast-xml-builder fast-xml-parser flatted mermaid picomatch postcss uuid vite yaml --package-lock-only
```

can be rejected by Hermes as a suspected long-lived watch/server process. Split it into shorter family checks or inspect the lockfile with Node instead.

## PR completion standard used

- Fresh branch from latest `origin/main`
- Commit package manifest/lockfile changes only
- Push branch and create PR
- Verify local HEAD equals remote branch HEAD with `git ls-remote`
- Verify `gh pr view` shows checks attached to the pushed head SHA
- Do not wait passively for CI unless the user asks
