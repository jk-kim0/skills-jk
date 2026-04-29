---
name: github-cli-env-diagnostics
description: Safely diagnose whether gh is using a shell GITHUB_TOKEN versus local keyring/SSH auth, without being misled by masked tool output.
tags: [github, gh, auth, env, debugging]
---

# GitHub CLI env diagnostics

Use this when:
- `gh` authentication behavior seems surprising
- you need to know whether `GITHUB_TOKEN` is actually present in the shell
- tool output may mask secret-like strings and make naive diagnostics misleading

## Problem

Do not rely on echoed labels like:

```bash
echo "GITHUB_TOKEN=$GITHUB_TOKEN"
```

In some tool/platform layers, output matching secret-like patterns may be masked. That can make a diagnostic label look like a real token value, or hide the difference between:
- unset
- set but empty
- set and non-empty

## Safe checks

Prefer explicit presence checks:

```bash
printenv GITHUB_TOKEN >/dev/null 2>&1 && echo present || echo absent
[ "${GITHUB_TOKEN+x}" = x ] && echo present || echo absent
[ -z "${GITHUB_TOKEN-}" ] && echo empty_or_absent || echo nonempty
```

Or in Python:

```bash
python3 - <<'PY'
import os
print('present' if 'GITHUB_TOKEN' in os.environ else 'absent')
print('nonempty' if os.environ.get('GITHUB_TOKEN') else 'empty_or_absent')
PY
```

## When using gh in this environment

If repository or global policy requires unsetting `GITHUB_TOKEN`, use:

```bash
env -u GITHUB_TOKEN gh auth status -h github.com
env -u GITHUB_TOKEN gh pr view <PR_NUMBER>
```

## Practical lesson

A masked output string is not proof that a token exists.
Verify presence with `printenv`, parameter-expansion checks, or Python before concluding that `gh` is authenticating via `GITHUB_TOKEN`.
