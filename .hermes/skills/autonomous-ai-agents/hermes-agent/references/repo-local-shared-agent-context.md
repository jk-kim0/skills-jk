# Repo-local shared agent context for Hermes + Codex

Use this when a repository should carry reviewable agent guidance and skills that both Hermes and Codex can discover without maintaining duplicate `.hermes` and `.codex` trees.

## Preferred layout

Use `.agents/` as the vendor-neutral source-controlled tree:

```text
.agents/
  README.md
  skills/
    <repo-skill>/
      SKILL.md
.codex -> .agents
.hermes -> .agents
AGENTS.md
```

Rationale:
- Codex discovers repo-local `.agents/skills` directories.
- Hermes can load the same skills when launched with `HERMES_HOME=$PWD/.hermes`; because `.hermes` is a symlink to `.agents`, both tools see one shared tree.
- `.agents` is a clearer class-level name for multi-agent context than making either `.codex` or `.hermes` the canonical source.

## Setup commands

From the repository root or worktree:

```bash
mkdir -p .agents/skills
ln -sfn .agents .codex
ln -sfn .agents .hermes
```

Add a repo-specific skill at:

```text
.agents/skills/<repo-name>-repo/SKILL.md
```

## Ignore discipline

Do not add broad rules such as `/.agents/*` and do not pre-ignore runtime paths that do not exist yet.

Default rule:
- Keep `.gitignore` limited to concrete paths that are currently necessary, such as `/.worktrees/` when the repo uses repo-local worktrees.
- If verification or agent startup generates new local files (for example `.agents/logs/`, `.agents/SOUL.md`, `.agents/skills/.hub/`, caches, SQLite files), report the exact generated paths to the user and ask before adding ignore rules.
- If the user has not approved new ignore rules, delete the local generated residue before committing.

## Verification

Check symlinks:

```bash
python3 - <<'PY'
import os
from pathlib import Path
for p in ['.codex', '.hermes']:
    path = Path(p)
    print(f'{p}: is_symlink={path.is_symlink()} target={os.readlink(path) if path.is_symlink() else None} resolves_to={path.resolve()}')
print('codex skill path works:', Path('.codex/skills/<repo-skill>/SKILL.md').exists())
print('hermes skill path works:', Path('.hermes/skills/<repo-skill>/SKILL.md').exists())
PY
```

Check Codex discovery from a new session context:

```bash
codex debug prompt-input 'noop' > /tmp/codex-prompt.json
python3 - <<'PY'
import json
from pathlib import Path
text = '\n'.join(
    c.get('text', '')
    for item in json.loads(Path('/tmp/codex-prompt.json').read_text())
    for c in item.get('content', [])
    if c.get('type') == 'input_text'
)
for needle in ['.agents/skills', '<repo-skill>']:
    print(needle, '=>', needle in text)
PY
```

Check Hermes discovery:

```bash
HERMES_HOME="$PWD/.hermes" hermes skills list
```

After verification, inspect `git status --short --branch`. If verification created untracked runtime files, report them and remove them unless the user approves adding narrow ignore rules.
