# Codex CLI 0.130 Hermes Memory Mirror

Use when the user wants Codex CLI to reference Hermes Agent durable memory.

## Key findings

- Codex native memory read root is effectively `$CODEX_HOME/memories` (default `~/.codex/memories`).
- Codex does not currently expose a supported `memories.root`, `memories.paths`, or arbitrary read-root setting in `config.toml`.
- Codex memory read-path injects `~/.codex/memories/memory_summary.md` into developer instructions and lets the model search/read deeper memory files such as `MEMORY.md` via memory tools.
- `memory_summary.md` is truncated around 5,000 tokens in the prompt; keep it concise and point to searchable detail in `MEMORY.md`.
- Codex memory local backend rejects symlinks (`must not be a symlink`) for list/read/search path resolution, so do not symlink `~/.codex/memories` or files inside it to Hermes memory.
- Hermes built-in markdown memory in this setup lives at `~/workspace/skills-jk/.hermes/memories/{USER.md,MEMORY.md}`.

## Recommended no-Codex-patch implementation

Use a generated mirror, not symlinks:

```text
Hermes memory
  ~/workspace/skills-jk/.hermes/memories/{USER.md,MEMORY.md}
        ↓ refresh script
Codex memory mirror
  ~/.codex/memories/{memory_summary.md,MEMORY.md}
        ↓ Codex native memory extension
Codex sessions
```

`~/.codex/config.toml`:

```toml
[features]
memories = true

[memories]
use_memories = true
generate_memories = false
```

Rationale:
- `use_memories=true` lets Codex use the memory read prompt/tools.
- `generate_memories=false` prevents Codex's own memory generation/consolidation pipeline from rewriting the mirrored Hermes memory store.

Generate:
- `~/.codex/memories/memory_summary.md`: short, task-routing summary explaining this is a read-only Hermes memory mirror and that details are in `MEMORY.md`.
- `~/.codex/memories/MEMORY.md`: combined generated file containing Hermes `USER.md` and `MEMORY.md`, with a header saying not to edit directly.
- `~/.codex/memories/refresh-hermes-memory.sh`: re-runnable script that regenerates those two files from Hermes memory.

## Wrapper for automatic refresh

Prefer a wrapper over relying only on hooks:

```bash
#!/usr/bin/env bash
set -euo pipefail
"$HOME/.codex/memories/refresh-hermes-memory.sh" >/dev/null 2>&1 || true
exec /opt/homebrew/bin/codex "$@"
```

Place as `~/.local/bin/codex-hermes`, or alias `codex` to this wrapper. The wrapper must call the real binary path to avoid recursion.

## Optional SessionStart hook

Codex supports `SessionStart` hooks that can output additional context. A refresh hook can be added as a secondary safety net, but do not rely on it as the primary mechanism unless verified against the installed Codex version's prompt-construction order.

Example config shape:

```toml
[[hooks.SessionStart]]
matcher = "startup|resume|clear"

[[hooks.SessionStart.hooks]]
type = "command"
command = "$HOME/.codex/memories/refresh-hermes-memory.sh"
timeout = 10
statusMessage = "Refreshing Hermes memory mirror"
```

Hook trust/approval behavior may require user acceptance.

## Verification

```bash
codex features list | grep -i '^memories'
```

Expected: `memories ... true`.

```bash
codex debug prompt-input 'noop' > /tmp/codex-prompt.json
python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path('/tmp/codex-prompt.json').read_text())
text = '\n'.join(
    c.get('text', '')
    for item in data
    for c in item.get('content', [])
    if c.get('type') == 'input_text'
)
for needle in ['## Memory', 'Hermes Agent', 'MEMORY.md', 'corp-web-japan']:
    print(needle, '=>', needle in text)
PY
```

## Longer-term upstream-quality Codex patch

A cleaner Codex implementation would add a read-only external memory root:

```toml
[memories]
use_memories = true
generate_memories = false
read_root = "/Users/jk/workspace/skills-jk/.hermes/memories"
```

Expected code areas:
- `codex-rs/config/src/types.rs`: add `MemoriesToml.read_root` and `MemoriesConfig.read_root`.
- `codex-rs/memories/read/src/lib.rs` / `prompts.rs`: calculate memory read root from config instead of only `codex_home.join("memories")`.
- `codex-rs/ext/memories/src/extension.rs`: pass the read root into `LocalMemoriesBackend::from_memory_root`.
- Keep the write/consolidation root separate so Codex does not mutate external Hermes memory.

This patch is more invasive and should be proposed upstream only if the mirror approach becomes insufficient.