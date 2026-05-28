# Codex CLI local skill discovery via `~/.agents/skills` symlinks

Use this when the user wants local Codex to reference an external skill library such as `skills-jk/.hermes/skills` without copying files or inventing unsupported Codex config keys.

## Verified pattern

Codex CLI 0.133.0 discovers skill directories exposed through symlinks under:

```bash
$HOME/.agents/skills
```

For the `skills-jk` repository, the default recommended setup is:

```bash
mkdir -p ~/.agents/skills

ln -sfn "$HOME/workspace/skills-jk/.hermes/skills" \
  "$HOME/.agents/skills/skills-jk-hermes"

ln -sfn "$HOME/workspace/skills-jk/skills" \
  "$HOME/.agents/skills/skills-jk"
```

After creating or changing symlinks, restart Codex. Skill discovery happens when a Codex session starts; already-running sessions may not pick up the change.

## Verification

Use `codex debug prompt-input` and check that expected skill paths or names appear in the prompt input:

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

for needle in [
    '/Users/jk/workspace/skills-jk/.hermes/skills',
    '/Users/jk/workspace/skills-jk/skills',
    'hermes-agent',
    'corp-web-app-pack',
    'github-pr-workflow',
]:
    print(needle, '=>', needle in text)
PY
```

Expected result after setup: the two paths and representative skill names print `True`.

## Pitfalls

- Do not add unsupported keys such as `skills.paths` or `[skills] paths = [...]` to `~/.codex/config.toml`. The `[skills]` section is for controlling discovered skills, not registering arbitrary discovery roots.
- The symlink label itself (for example `skills-jk-hermes`) may not appear in the prompt input. Check for target paths or actual skill names instead.
- Exposing `.hermes/skill-packs` directly is optional. Prefer `.hermes/skills` as the default because it contains active entrypoint skills such as repo pack skills; add `.hermes/skill-packs` only when future Codex sessions need direct access to detailed pack internals.
- Tool invocations in `skills-jk` can generate local Hermes runtime residue such as `.hermes/kanban.db-wal` and `.hermes/kanban.db-shm`; keep those ignored locally rather than treating them as skill changes.
