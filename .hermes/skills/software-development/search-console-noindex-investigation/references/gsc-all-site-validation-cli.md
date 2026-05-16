# GSC all-site Page indexing validation CLI pattern

Session learning from skills-jk GSC CLI work:

- For a user who manages multiple Search Console properties, do not require a manually maintained site list when the account can discover properties itself.
- Use Search Console `sites().list()` / existing `gsc sites` data as the source of truth, then iterate selected `siteUrl` values.
- For Page indexing issue validation, reuse the browser-session helper that operates on the GSC UI because public APIs do not expose generic URL Request Indexing or issue-level validation restart.
- Default to URL-prefix properties and skip `sc-domain:*` properties unless explicitly requested. Domain properties overlap URL-prefix properties and can cause duplicate work or different UI paths.
- Keep the first implementation safe by making it dry-run by default; require an explicit `--submit` flag before clicking `START NEW VALIDATION`.
- Useful controls for the all-site wrapper:
  - `--site <siteUrl>` repeatable for scoped runs
  - `--limit-sites N` for smoke tests
  - `--issue-limit N` for per-site dry-runs
  - `--only-status Failed` default, with `all` or status override when needed
  - `--include-started` only when the user asks to re-evaluate already-started rows
  - `--include-domain-properties` opt-in for `sc-domain:*`
  - `--site-delay-ms` and per-issue `--delay-ms` to avoid racing the GSC SPA
  - `--port` to pass a Chrome remote debugging port to the browser helper
- Flush parent-process output before launching child browser-helper commands; otherwise child JSON can appear before the per-site header in terminal logs.
- When `--site` is supplied, do not count all unselected properties as skipped. Reserve skipped reporting for properties that were selected/discovered but intentionally excluded, such as `sc-domain:*` by default.

Verification pattern:

```bash
python3 -m py_compile bin/gsc
./bin/gsc validate-index-issues-all-browser --help
./bin/gsc validate-index-issues-all-browser \
  --site https://docs.querypie.com/ \
  --limit-sites 1 \
  --issue-limit 1 \
  --site-delay-ms 0
```

PR packaging pattern for skills-jk:

- Work from a fresh `.worktrees/<topic>` worktree based on `origin/main` so dirty root Hermes runtime/skill edits stay untouched.
- Use the repository's `.github/workflows/create-pr.yml` workflow for PR creation, not direct `gh pr create`.
