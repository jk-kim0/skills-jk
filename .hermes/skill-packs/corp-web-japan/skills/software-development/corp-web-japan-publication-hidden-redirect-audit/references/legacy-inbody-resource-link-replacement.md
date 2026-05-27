# Legacy in-body QueryPie resource link replacement

Use this reference when a corp-web-japan task asks to replace `https://www.querypie.com/ja/**` links inside MDX article/blog/whitepaper bodies with local canonical resource routes.

## Decision rule

For each legacy URL:

1. Search the exact URL in the touched MDX file(s).
2. Extract resource type, id, slug, and hash fragment.
3. Verify the local record exists in the current checkout, preferably by filename and frontmatter:
   - whitepapers: `src/content/whitepapers/<id>-*.mdx`
   - blogs: `src/content/blog/<id>-*.mdx`
   - news/events/use-cases/demo: corresponding `src/content/<family>/` roots
4. If the local record exists, replace with canonical local path and preserve the fragment.
5. If the local record does not exist, stop before inventing a local URL and classify the missing resource as local migration vs hidden shadow record vs redirect-only vs remain external.

## Session examples

Legacy whitepaper URLs in blog bodies mapped cleanly to local canonical whitepaper routes:

| Legacy URL | Local record | Replacement |
|---|---|---|
| `https://www.querypie.com/ja/resources/discover/white-paper/8/secure-login-token-management#脅威の種類` | `src/content/whitepapers/8-secure-login-token-management.mdx` | `/whitepapers/8/secure-login-token-management#脅威の種類` |
| `https://www.querypie.com/ja/features/documentation/white-paper/29/ai-agent-guardrails-governance-2026-implementation` | `src/content/whitepapers/29-ai-agent-guardrails-governance-2026-implementation.mdx` | `/whitepapers/29/ai-agent-guardrails-governance-2026-implementation` |
| `https://www.querypie.com/ja/resources/discover/white-paper/2-shell-native-command-control` | `src/content/whitepapers/2-shell-native-command-control-ssh-proxy-architecture.mdx` | `/whitepapers/2/shell-native-command-control-ssh-proxy-architecture` |
| `https://www.querypie.com/ja/resources/discover/white-paper/5-preventing-command-bypass` | `src/content/whitepapers/5-preventing-command-bypass.mdx` | `/whitepapers/5/preventing-command-bypass` |

## Verification pattern

Run a static residue check against the touched files, e.g. search for:

```text
https://www\.querypie\.com/ja/(resources/discover/white-paper|features/documentation/white-paper)
```

For content-only MDX link rewrites, a focused source-level test is usually enough. In corp-web-japan, `npm run test -- <specific tests>` may be routed through `scripts/ci/run-node-tests.mjs` and execute broader grouped suites than the argument list suggests; treat a broad pass as acceptable but do not assume it was narrowly scoped.
