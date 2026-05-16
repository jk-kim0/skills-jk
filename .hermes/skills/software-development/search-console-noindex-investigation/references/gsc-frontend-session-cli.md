# GSC frontend-session CLI pattern

Session learning from skills-jk GSC CLI work:

- Repeatedly controlling Chrome to click `START NEW VALIDATION` is inconvenient for unattended CLI runs. Prefer a two-phase workflow when maintaining a repo-local GSC CLI:
  1. one-time `frontend-session export` from an already logged-in, debuggable Chrome Search Console tab
  2. later direct CLI runs that reuse the saved cookies/WIZ tokens and call Search Console frontend endpoints with HTTP requests
- Keep the browser/CDP implementation as an explicit fallback command, but do not make it the default all-site path when the user wants automation without repeated browser approval/clicking.
- Treat the saved session as sensitive credential material. Store it outside the repo, defaulting to a user config path such as `~/.config/gsc/frontend-session.json`, write it with `0600` permissions, and never print cookie values or commit the file.
- Export enough state for frontend calls:
  - Google cookies for `search.google.com` / related Google domains
  - GSC WIZ globals such as `SNlM0e`, `FdrFJe`, and `cfb2h` when present
  - source URL/title metadata only for diagnostics
- Normal direct runs should fail fast with a clear message when the session file is missing, expired, or redirects to Google sign-in. Tell the user to rerun `frontend-session export` instead of silently falling back to browser control.
- Preserve dry-run semantics: list discovered/candidate issue rows without `--submit`; require explicit `--submit` before attempting direct validation-start calls.
- Because GSC frontend RPCs are undocumented, code should report when the direct `START NEW VALIDATION` RPC template cannot be found instead of pretending the click succeeded. The explicit browser fallback can remain available for manual recovery.

Suggested command shape:

```bash
gsc frontend-session export

gsc validate-index-issues-all \
  --site https://docs.querypie.com/ \
  --limit-sites 1 \
  --issue-limit 1

gsc validate-index-issues-all --submit
```

Verification pattern:

```bash
python3 -m py_compile bin/gsc
node --check bin/gsc-frontend-indexing
./bin/gsc frontend-session export --help
./bin/gsc validate-index-issues-all --help
./bin/gsc validate-index-issues-all --site https://docs.querypie.com/ --limit-sites 1 --issue-limit 1 --site-delay-ms 0
```

If Chrome remote debugging is unavailable in the agent environment, still verify the missing-session path and command help locally, and state that live export/submit requires a logged-in debuggable Chrome tab.