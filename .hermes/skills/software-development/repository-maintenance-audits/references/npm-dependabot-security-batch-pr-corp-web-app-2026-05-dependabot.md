# corp-web-app Dependabot batch PR notes (2026-05)

## Context

Repository: `querypie/corp-web-app`
Task: resolve all open GitHub Dependabot alerts under `security/dependabot` in one PR.

Useful PR result:
- Branch: `fix/dependabot-security`
- PR: `https://github.com/querypie/corp-web-app/pull/643`
- Commit: `1426136237589be9dbf9e4c978cc719f1e1a204e`

## Alert inventory pattern

The GitHub Dependabot API showed many alerts across two manifests:
- `package-lock.json`
- `scripts/deploy/package-lock.json`

Important package families included:
- root: `next`, `axios`, `vm2`, `protobufjs`, `@protobufjs/utf8`, `mermaid`, `uuid`, `postcss`, `vite`, `dompurify`, `yaml`, `undici`, `effect`, `flatted`, `defu`, `picomatch`, `follow-redirects`
- deploy: `hono`, `@hono/node-server`, `fast-uri`, `express-rate-limit`, `path-to-regexp`, `ip-address`

Command used:

```bash
gh api -H 'Accept: application/vnd.github+json' \
  /repos/querypie/corp-web-app/dependabot/alerts --paginate \
  --jq '.[] | select(.state=="open") | {number,package:.dependency.package.name,ecosystem:.dependency.package.ecosystem,manifest:.dependency.manifest_path,severity:.security_advisory.severity,summary:.security_advisory.summary,vulnerable:.security_vulnerability.vulnerable_version_range,patched:.security_vulnerability.first_patched_version.identifier}'
```

## Successful root updates

Direct/package.json updates:
- `next`, `@next/third-parties`, `eslint-config-next` -> `^15.5.18`
- `mermaid` -> `^11.15.0`
- `uuid` -> `^13.0.1`

Overrides that remained useful:
- `@vercel/blob.undici` -> `^6.24.0`
- `cheerio.undici` -> `^7.24.0`
- `postcss` -> `^8.5.10`

Reason for `postcss` override:
- Even after updating Next.js to the patched 15.5.x line, npm audit still mapped Next to vulnerable `postcss` because Next pins `postcss` internally.
- A targeted `overrides.postcss` regenerated the root lockfile with `postcss@8.5.14` and audit reached zero.

## Successful deploy updates

In `scripts/deploy`:
- `@vercel/sdk` -> `^1.21.5`
- `dotenv` -> `^17.4.2`

This refreshed transitive packages to patched versions:
- `hono@4.12.18`
- `@hono/node-server@1.19.14`
- `fast-uri@3.1.2`
- `express-rate-limit@8.5.2`
- `path-to-regexp@8.4.2`
- `ip-address@10.2.0`

## Important pitfall discovered

A broad override like:

```json
"overrides": {
  "brace-expansion": "^1.1.13"
}
```

made `npm audit` report zero vulnerabilities, but produced an invalid lockfile tree:
- `minimatch@10.2.4` requires `brace-expansion@^5.0.2`
- the broad override forced `brace-expansion@1.1.14` under those paths
- `npm ls brace-expansion minimatch --package-lock-only` reported `ELSPROBLEMS invalid`

Do not trust audit alone after overrides. Always run `npm ls` for the overridden package and relevant parents.

Cleanup that fixed the invalid state:

```bash
# after removing the bad brace-expansion override from package.json
rm -rf node_modules package-lock.json
npm install --package-lock-only --ignore-scripts
npm ls brace-expansion minimatch postcss --package-lock-only
npm audit --json
```

The clean regeneration kept:
- `brace-expansion@1.1.14` for old `minimatch@3` paths
- `brace-expansion@5.0.6` for `minimatch@10` paths
- `postcss@8.5.14` through the targeted postcss override

## Verification outputs worth reproducing

Root:

```text
npm audit --json -> { info: 0, low: 0, moderate: 0, high: 0, critical: 0, total: 0 }
npm ls brace-expansion minimatch postcss --package-lock-only -> no invalid dependencies
```

Deploy:

```text
npm --prefix scripts/deploy audit --json -> { info: 0, low: 0, moderate: 0, high: 0, critical: 0, total: 0 }
npm --prefix scripts/deploy ls hono @hono/node-server fast-uri express-rate-limit path-to-regexp ip-address --package-lock-only -> patched transitive versions present
```

## Communication note

After pushing the branch, GitHub still reported vulnerabilities on the default branch in the remote push message. That is expected before merge because Dependabot security alerts are evaluated from the default branch/dependency graph. The PR body should say audit is clean on the branch and alerts are expected to close after merge/default-branch reprocessing, not claim the security page is already closed.
