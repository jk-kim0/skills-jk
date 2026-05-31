# querypie-docs Dependabot batch notes (2026-05)

Use as a concrete reference for npm Dependabot cleanup in `querypie/querypie-docs`-style repos with several independent npm manifests.

## Alert shape

Open Dependabot alerts were spread across:

- root `package-lock.json`
  - `next` advisories requiring `16.2.6` or newer
  - `mermaid` requiring `11.15.0`
  - many transitive advisories: `fast-uri`, `fast-xml-builder`, `fast-xml-parser`, `@xmldom/xmldom`, `dompurify`, `uuid`, `vite`, `picomatch`, `brace-expansion`, `yaml`, `flatted`, `lodash-es`, `postcss`
- `scripts/deploy/package-lock.json`
  - `hono`, `@hono/node-server`, `fast-uri`, `ip-address`, `express-rate-limit`, `path-to-regexp`
- `scripts/website-analysis/package-lock.json`
  - `basic-ftp`, `ip-address`

## Successful update pattern

Root:

- updated direct Next packages:
  - `next@16.2.6`
  - `@next/third-parties@16.2.6`
  - `eslint-config-next@16.2.6`
- did not keep `mermaid` as a new direct dependency after the initial lockfile update; instead used a root override so `@theguild/remark-mermaid` resolves to patched `mermaid@11.15.0`.
- expanded targeted `overrides` for vulnerable transitive packages.
- important scoped overrides used nested forms for dependency families where major ranges differ:
  - `minimatch@3` -> `brace-expansion@^1.1.13`
  - `minimatch@5`/`minimatch@9` -> `brace-expansion@^2.0.3`
  - `minimatch@10` -> `brace-expansion@^5.0.5`
  - `micromatch` -> `picomatch@^2.3.2`
  - `tinyglobby`, `vite`, `vitest` -> `picomatch@^4.0.4`
  - `next`, `styled-components`, `vite` -> `postcss@^8.5.10`
  - `nextra`, `vite` -> `yaml@^2.8.3`
  - `oas-*`/`swagger2openapi` -> `yaml@^1.10.3`

`scripts/deploy`:

- updated `@vercel/sdk` to the latest available at the time (`1.21.5`) and `dotenv` to latest.
- added overrides for the vulnerable transitive set:
  - `hono@^4.12.18`
  - `@hono/node-server@^1.19.13`
  - `fast-uri@^3.1.2`
  - `ip-address@^10.1.1`
  - `express-rate-limit@^8.2.2`
  - `path-to-regexp@^8.4.0`

`scripts/website-analysis`:

- attempted newest `puppeteer`, but local Node `v22.10.0` produced engine warnings because `puppeteer@25` requires `>=22.12.0`.
- reverted direct `puppeteer` range to the existing `^24.37.5` family and used transitive overrides instead:
  - `basic-ftp@^5.3.1`
  - `ip-address@^10.1.1`

## Verification

Run audits for every affected manifest:

```bash
npm audit --json > /tmp/querypie-docs-root-audit.json
npm --prefix scripts/deploy audit --json > /tmp/querypie-docs-deploy-audit.json
npm --prefix scripts/website-analysis audit --json > /tmp/querypie-docs-analysis-audit.json
```

Expected result after the update was zero vulnerabilities in all three audit summaries.

Spot-check overridden trees with smaller `npm ls` groups rather than one huge command. In this Hermes environment, a long `npm ls pkg1 pkg2 ...` command can be misclassified by the tool guard as a long-lived server/watch process. Split checks, for example:

```bash
npm ls @xmldom/xmldom fast-xml-builder fast-xml-parser --package-lock-only
npm ls dompurify mermaid uuid --package-lock-only
npm ls brace-expansion --package-lock-only
npm ls picomatch --package-lock-only
npm ls postcss --package-lock-only
npm ls yaml --package-lock-only
npm --prefix scripts/deploy ls hono @hono/node-server fast-uri --package-lock-only
npm --prefix scripts/deploy ls ip-address express-rate-limit path-to-regexp --package-lock-only
npm --prefix scripts/website-analysis ls basic-ftp ip-address puppeteer --package-lock-only
```

## PR/cleanup notes

- Dependabot alert counts in GitHub remain default-branch-based until merge and reprocessing.
- If the PR merges quickly and the remote branch is deleted, a later repo-local workspace cleanup should verify `gh pr view <number>` and `git fetch --prune`, then remove the clean merged worktree and local branch residue.
