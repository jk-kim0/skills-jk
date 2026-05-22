# Vercel CLI token visibility from Hermes on macOS

Session finding: the user's normal local shell can have `VERCEL_TOKEN`, while Hermes `terminal()` may not see it in the default non-interactive environment.

Verified pattern:
- default Hermes tool env: `VERCEL_TOKEN` unset
- `zsh -lc`: `VERCEL_TOKEN` unset
- `zsh -ic`: `VERCEL_TOKEN` set

When a Vercel task says the local shell has `VERCEL_TOKEN`, do not stop after checking the default tool env or `zsh -lc`. Check interactive zsh too:

```bash
zsh -ic 'python3 - <<"PY"
import os
v = os.environ.get("VERCEL_TOKEN")
print("VERCEL_TOKEN present:", bool(v))
print("length:", len(v or ""))
PY'
```

Run Vercel CLI through interactive zsh when needed:

```bash
zsh -ic 'vercel whoami --token "$VERCEL_TOKEN"'
zsh -ic 'vercel logs <deployment-or-url> --token "$VERCEL_TOKEN" --json'
```

Pitfall: saying "local shell has no Vercel token" after only checking Hermes' non-interactive env is wrong. Say "the current Hermes tool env does not expose the token" and verify `zsh -ic` before concluding credentials are unavailable.
