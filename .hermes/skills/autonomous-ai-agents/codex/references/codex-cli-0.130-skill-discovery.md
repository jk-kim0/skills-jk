# Codex CLI 0.130 skill discovery paths

Use this when a user asks how to make Codex CLI see skills from another local repository or from Hermes.

## Verified discovery roots

For Codex CLI 0.130.0, skill roots are not configured by adding arbitrary path lists to `~/.codex/config.toml`. Codex discovers skills from these roots:

1. `$CODEX_HOME/skills` (defaults to `~/.codex/skills`; deprecated but still scanned for backward compatibility)
2. `$HOME/.agents/skills` (current user-installed skills location)
3. repo-local `.agents/skills` directories between the project root and current working directory
4. system/admin/plugin roots such as `$CODEX_HOME/skills/.system`, `/etc/codex/skills`, and plugin-provided skill roots

Codex follows symlinked directories for user/admin/repo skill roots, so symlinks under `~/.agents/skills` are the preferred way to expose external local skill trees globally.

## Preferred setup for skills-jk + Hermes skills

```bash
mkdir -p ~/.agents/skills

ln -sfn "$HOME/workspace/skills-jk/skills" \
  "$HOME/.agents/skills/skills-jk"

ln -sfn "$HOME/workspace/skills-jk/.hermes/skills" \
  "$HOME/.agents/skills/skills-jk-hermes"
```

Restart Codex after changing skill symlinks because discovery happens at session startup.

## Verification

```bash
ls -la ~/.agents/skills

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
    'skills-jk',
    'skills-jk-hermes',
    '/Users/jk/workspace/skills-jk/skills',
    '/Users/jk/workspace/skills-jk/.hermes/skills',
]:
    print(needle, '=>', needle in text)

for line in text.splitlines():
    if 'skills-jk' in line or '/Users/jk/workspace/skills-jk' in line:
        print(line)
PY
```

## Config notes

`~/.codex/config.toml` `[skills]` is for skill enablement/inclusion controls, not arbitrary root registration. The schema accepts settings such as:

```toml
[skills]
include_instructions = true

[[skills.config]]
path = "/absolute/path/to/SKILL.md"
enabled = false
```

Use path/name entries to disable or re-enable specific discovered skills, especially when duplicate names exist.

## Pitfalls

- Do not invent unsupported config keys like `skills.paths`; Codex may reject unknown fields.
- Large skill collections can exceed the skills context budget, causing descriptions to be truncated. This does not necessarily mean the skills are undiscovered.
- If a skill does not appear, check the symlink, confirm each skill has a `SKILL.md`, and restart Codex.
