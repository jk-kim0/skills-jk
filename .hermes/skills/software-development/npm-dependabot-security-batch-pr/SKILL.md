---
name: npm-dependabot-security-batch-pr
description: Resolve many GitHub Dependabot npm security alerts in one reviewable PR by combining GitHub alert inspection, package-lock-only updates, scoped overrides, and audit/lockfile validation across multiple npm manifests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [npm, Dependabot, security, GitHub, lockfile, PR]
    related_skills: [github-pr-workflow, github-auth, systematic-debugging]
---

# npm Dependabot Security Batch PR

## When to use

Use this when the user asks to resolve a repository's GitHub Dependabot security page, especially with wording like:
- "security/dependabot 해결하는 PR"
- "Dependabot alerts를 한 번에 해결"
- "npm audit/lockfile security update PR"

This skill is for npm/package-lock based repositories. It generalizes the pattern where GitHub reports many alerts but they collapse into a smaller set of direct dependency bumps, transitive lockfile refreshes, and carefully scoped overrides.

## Core principles

- Inspect GitHub Dependabot alerts directly; do not rely only on local `npm audit`.
- Start from latest `origin/main` in a fresh worktree and verify merge-base before editing.
- Include every npm manifest/lockfile that appears in the alert list, not just the repo root.
- Prefer normal semver-compatible package updates and lockfile refreshes before adding overrides.
- If overrides are necessary, scope them narrowly and verify they do not create invalid dependency trees.
- Report that the PR is expected to close alerts after merge/default-branch reprocessing; pre-merge security-page counts usually still reflect `main`.

## Workflow

1. Verify repository and authentication.

   ```bash
   pwd
   git rev-parse --show-toplevel
   git remote -v
   gh auth status
   gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef,url
   ```

2. Fetch latest main and create a fresh worktree.

   ```bash
   git fetch origin --prune
   git switch main
   git pull --ff-only origin main
   git worktree add .worktrees/fix-dependabot-security -b fix/dependabot-security origin/main
   git -C .worktrees/fix-dependabot-security merge-base HEAD origin/main
   git -C .worktrees/fix-dependabot-security rev-parse origin/main
   ```

3. Query open Dependabot alerts from GitHub.

   ```bash
   gh api -H 'Accept: application/vnd.github+json' \
     /repos/OWNER/REPO/dependabot/alerts --paginate \
     --jq '.[] | select(.state=="open") | {number,package:.dependency.package.name,ecosystem:.dependency.package.ecosystem,manifest:.dependency.manifest_path,severity:.security_advisory.severity,summary:.security_advisory.summary,vulnerable:.security_vulnerability.vulnerable_version_range,patched:.security_vulnerability.first_patched_version.identifier}'
   ```

   Group by `manifest`, `package`, and highest patched version. Watch for secondary manifests such as `scripts/deploy/package-lock.json`.

4. Inspect current package versions in each affected lockfile.

   ```bash
   node - <<'NODE'
   const fs = require('fs')
   for (const file of ['package-lock.json', 'scripts/deploy/package-lock.json']) {
     if (!fs.existsSync(file)) continue
     const lock = JSON.parse(fs.readFileSync(file, 'utf8'))
     console.log('\n' + file)
     for (const name of ['next', 'axios', 'vm2', 'protobufjs', 'mermaid', 'uuid', 'postcss', 'vite', 'dompurify', 'yaml', 'undici', 'hono', '@hono/node-server', 'fast-uri', 'express-rate-limit', 'path-to-regexp', 'ip-address']) {
       const rows = Object.entries(lock.packages || {}).filter(([k]) => k === `node_modules/${name}` || k.endsWith(`/node_modules/${name}`))
       for (const [k, v] of rows) console.log(`${name}\t${v.version}\t${k}`)
     }
   }
   NODE
   ```

5. Update direct dependencies and regenerate lockfiles without running install scripts.

   Prefer `--package-lock-only --ignore-scripts` to avoid expensive or side-effectful installs in worktrees.

   ```bash
   npm install --package-lock-only --ignore-scripts <direct-package>@<patched-version> ...
   npm install --package-lock-only --ignore-scripts
   npm --prefix scripts/deploy install --package-lock-only --ignore-scripts <direct-package>@latest ...
   ```

6. Run audit for each manifest.

   ```bash
   npm audit --json >/tmp/root-audit.json
   npm --prefix scripts/deploy audit --json >/tmp/deploy-audit.json
   node - <<'NODE'
   const fs = require('fs')
   for (const file of ['/tmp/root-audit.json', '/tmp/deploy-audit.json']) {
     if (!fs.existsSync(file)) continue
     const data = JSON.parse(fs.readFileSync(file, 'utf8'))
     console.log(file, data.metadata.vulnerabilities)
   }
   NODE
   ```

7. If vulnerabilities remain, identify whether they are direct, transitive, or stale lockfile entries.

   - Try `npm audit fix --package-lock-only --ignore-scripts`.
   - If `next` remains vulnerable only through a bundled/fixed dependency such as `postcss`, consider a targeted override only after updating `next` to the patched release.
   - If a transitive advisory has a patched compatible version, a narrowly scoped override may be appropriate.

8. Validate overrides and lockfile consistency.

   Always run `npm ls` for overridden packages. `npm audit` can report zero vulnerabilities even when an override produced an invalid tree.

   ```bash
   npm ls <package> <parent-package> --package-lock-only
   npm --prefix scripts/deploy ls <package> <parent-package> --package-lock-only
   ```

   If `npm ls` reports `invalid`, do not commit. Remove or narrow the override and regenerate from a clean lockfile if needed.

9. If lockfile state looks contaminated by prior failed override attempts, regenerate cleanly.

   ```bash
   rm -rf node_modules package-lock.json
   npm install --package-lock-only --ignore-scripts
   npm audit --json
   npm ls <suspicious-package> <parent-package> --package-lock-only
   ```

   This avoids committing stale or invalid transitive resolutions.

10. Commit, push, create PR, and verify checks attach to the pushed head SHA.

   ```bash
   git fetch origin --prune
   test "$(git merge-base HEAD origin/main)" = "$(git rev-parse origin/main)"
   git add package.json package-lock.json scripts/deploy/package.json scripts/deploy/package-lock.json
   git commit -m "fix: resolve dependabot security alerts"
   git push -u origin HEAD
   gh pr create --title "fix: Dependabot 보안 알림 해결" --body-file /tmp/pr-body.md --base main --head fix/dependabot-security
   git rev-parse HEAD
   git ls-remote origin refs/heads/fix/dependabot-security
   gh pr checks <PR_NUMBER> || true
   ```

## Override guidance

Good override patterns:
- `overrides.postcss = "^8.5.10"` when Next pins a vulnerable older `postcss` and audit remains red after a patched Next bump.
- `overrides.@vercel/blob.undici = "^6.24.0"` or `overrides.cheerio.undici = "^7.24.0"` when the vulnerable package is clearly under that parent.

Pitfall: broad overrides can silently break unrelated dependency majors. For example, `overrides.brace-expansion = "^1.1.13"` can force `brace-expansion@1.x` under `minimatch@10`, even though `minimatch@10` requires `brace-expansion@^5.0.2`. `npm audit` may still show zero, but `npm ls brace-expansion minimatch --package-lock-only` reveals `invalid`. Do not commit that state.

## Verification standard

A good PR should include:
- direct GitHub alert inventory from `gh api`
- audit result for each npm manifest: zero vulnerabilities when possible
- `npm ls` validation for any overridden or suspicious dependency family
- commit based on latest `origin/main`
- PR checks attached to the exact pushed head SHA

Respect user preference if they do not want local build/test runs for dependency PRs. In that case, commit/push after audit/lockfile checks and rely on CI for build/test verification.

### Hermes tool-guard pitfall for `npm ls`

In Hermes CLI sessions, a single long `npm ls <many packages> --package-lock-only` command can be falsely rejected as a long-lived watch/server process. Do not treat that as dependency-tree failure.

Safer verification patterns:
- split `npm ls` by dependency family, e.g. XML packages, sanitizer packages, dev-tool packages, deploy packages
- run independent short `npm ls` checks in parallel when available
- use `npm audit --json > /tmp/<name>.json` first, then summarize the JSON separately; audit redirects often produce no stdout on success, which is expected
- if one `npm ls` family still triggers the guard, retry as individual packages or inspect `package-lock.json` with a small Node script

## References

- `references/corp-web-app-2026-05-dependabot.md` — session notes from a corp-web-app batch PR that required direct GitHub alert inventory, root plus `scripts/deploy` audits, targeted postcss/undici overrides, and cleanup after an over-broad brace-expansion override created invalid lockfile entries.
- `references/querypie-docs-2026-05-dependabot.md` — session notes from a querypie-docs batch PR covering root + `scripts/deploy` + `scripts/website-analysis`, Next 16.2.6, Mermaid 11.15.0 via override, Puppeteer engine-warning avoidance, and split `npm ls` verification to avoid Hermes tool-guard false positives.
- `references/querypie-docs-2026-05-dependabot.md` — querypie-docs batch PR notes covering root plus `scripts/deploy` plus `scripts/website-analysis`, targeted overrides, and the `npm ls` tool-guard workaround.
