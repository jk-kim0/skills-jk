# oh-my-codex (OMX) setup alongside Codex CLI

Use this when installing or validating OMX, the oh-my-codex workflow layer for OpenAI Codex CLI.

## Key facts

- Official project/package: `oh-my-codex`.
- CLI binary installed by the package: `omx`.
- Do not install the unrelated npm package named `omx` for this purpose.
- OMX only needs a working authenticated `codex` command on `PATH`; Codex itself may be installed by Homebrew, npm, or another supported method.
- If Codex is Homebrew-owned, do not run a combined `npm install -g @openai/codex oh-my-codex`, because npm can fail or conflict when trying to create an already-owned `codex` binary.

## Setup flow

1. Inspect the environment before changing it:

```bash
pwd
printf 'node: '; node -v 2>/dev/null || true
printf 'npm: '; npm -v 2>/dev/null || true
printf 'codex: '; codex --version 2>/dev/null || true
printf 'codex path: '; command -v codex 2>/dev/null || true
printf 'omx path: '; command -v omx 2>/dev/null || true
npm prefix -g 2>/dev/null || true
npm root -g 2>/dev/null || true
npm view oh-my-codex version engines bin --json
```

2. Install only `oh-my-codex` when Codex is already present:

```bash
npm install -g oh-my-codex
```

3. Verify install and run doctor:

```bash
command -v omx
omx --version
omx doctor
```

4. If doctor reports missing first-time setup entries, prefer preserving existing user config:

```bash
omx setup --merge-agents
```

Use `omx setup --force` only when the warning explicitly recommends replacement or the user accepts that scope.

5. Re-run checks and auth status:

```bash
omx doctor
codex login status
```

6. Run an actual smoke test:

```bash
omx exec --skip-git-repo-check -C . "Reply with exactly OMX-EXEC-OK"
```

Expected final output includes `OMX-EXEC-OK`.

## Interpreting common warnings

- `Explore Harness: Rust harness sources are packaged, but no compatible packaged prebuilt or cargo was found`: only `omx explore` may be unavailable. Basic `omx`, `omx exec`, and Codex integration can still be usable.
- `Config: config.toml exists but no OMX entries yet`: expected before first setup; run `omx setup --merge-agents` when preserving existing Codex config is desired.
- `Prompts directory not found`, low skill count, missing Codex `AGENTS.md`, or missing `.omx/state`: expected before first setup; should resolve after `omx setup --merge-agents`.

## Example known-good macOS+nvm result

- Node: `v22.10.0`
- npm: `10.9.0`
- Codex CLI: `codex-cli 0.132.0`, Homebrew-owned at `/opt/homebrew/bin/codex`
- OMX: `oh-my-codex v0.18.5`, nvm global binary at `/Users/jk/.nvm/versions/node/v22.10.0/bin/omx`
- `codex login status`: `Logged in using ChatGPT`
- `omx doctor` after setup: `15 passed, 1 warnings, 0 failed`; only Explore Harness warning remained.
