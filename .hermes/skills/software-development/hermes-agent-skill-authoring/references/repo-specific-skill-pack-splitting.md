# Repo-specific skill pack splitting

Use this pattern when a Hermes setup has many repo-specific skills in active `.hermes/skills/` and the user wants to reduce the default skills index while still keeping the detailed procedures available.

## Goal

Move detailed repo-specific skills outside active skill discovery, keep a thin active entrypoint per repo, and make agents load only the pack index plus the small set of detailed `SKILL.md` files needed for the current task.

## Recommended layout

```text
.hermes/skills/software-development/<repo>-pack/SKILL.md
.hermes/skill-packs/README.md
.hermes/skill-packs/INVENTORY.md
.hermes/skill-packs/MEASUREMENT.md
.hermes/skill-packs/<repo>/INDEX.md
.hermes/skill-packs/<repo>/skills/<category>/<skill-name>/SKILL.md
```

Important: moving skills to a different category under `.hermes/skills/` does not reduce prompt size if Hermes still indexes the whole active skill root. To reduce the default skills index, move detailed repo-specific skills outside active `.hermes/skills/` or into a separate profile/home.

## Procedure

1. Work from a fresh non-main worktree based on latest `origin/main`.
2. Inventory all active skills before moving them:
   - count total `.hermes/skills/**/SKILL.md`
   - classify each skill as `active-common` or a repo pack such as `corp-web-japan`, `corp-web-app`, `corp-web-v2`, `querypie-docs`
   - write the classification to `.hermes/skill-packs/INVENTORY.md`
3. Move only the target repo-prefix skills out of active discovery:
   - source: `.hermes/skills/<category>/<repo>*`
   - destination: `.hermes/skill-packs/<repo>/skills/<category>/<repo>*`
   - preserve references/templates/scripts/assets by moving the whole skill directory
4. Add one thin active entrypoint skill per repo:
   - `.hermes/skills/software-development/<repo>-pack/SKILL.md`
   - frontmatter description should include the repo trigger and say it points to an inactive skill pack index
   - body should instruct agents to read `.hermes/skill-packs/<repo>/INDEX.md`, then only the detailed `SKILL.md` files selected by the index
5. Generate each `.hermes/skill-packs/<repo>/INDEX.md`:
   - summary count
   - pack root path
   - active entrypoint path
   - how-to-use steps
   - trigger map grouped by task class
   - full skill table with skill name, path, and description
6. Update repository agent guidance such as `AGENTS.md` so future agents know the pack protocol:
   - active entrypoints live in `.hermes/skills/.../<repo>-pack/SKILL.md`
   - detailed contents live in `.hermes/skill-packs/<repo>/`
   - when a task matches a pack, read the entrypoint and `INDEX.md`, then load only relevant detailed files
7. Measure the result and write `.hermes/skill-packs/MEASUREMENT.md`:
   - baseline active skill count
   - moved detailed skill count per repo
   - active skill count after split
   - inactive pack skill count
   - rough index token estimate before/after

## Verification

Run lightweight checks before committing:

```bash
# Active and inactive counts
find .hermes/skills -name SKILL.md | wc -l
find .hermes/skill-packs -name SKILL.md | wc -l

# Confirm only pack wrappers remain active for moved repos
python3 - <<'PY'
from pathlib import Path
for pref in ['corp-web-japan','corp-web-app','corp-web-v2','querypie-docs']:
    active=[p for p in Path('.hermes/skills/software-development').glob(pref+'*') if p.is_dir() and (p/'SKILL.md').exists()]
    print(pref, [p.name for p in active])
PY

# Validate SKILL.md frontmatter in both roots
python3 - <<'PY'
from pathlib import Path
import re
errors=[]
for root in [Path('.hermes/skills'), Path('.hermes/skill-packs')]:
    for p in root.rglob('SKILL.md'):
        text=p.read_text(errors='replace')
        if not text.startswith('---'):
            errors.append(f'{p}: missing frontmatter')
            continue
        end=text.find('\n---',3)
        if end == -1:
            errors.append(f'{p}: unclosed frontmatter')
            continue
        fm=text[3:end]
        if not re.search(r'^name:\s*\S+', fm, re.M): errors.append(f'{p}: missing name')
        m=re.search(r'^description:\s*(.+)$', fm, re.M)
        if not m: errors.append(f'{p}: missing description')
        elif len(m.group(1).strip()) > 1024: errors.append(f'{p}: long description')
print('\n'.join(errors))
raise SystemExit(1 if errors else 0)
PY

git diff --check
```

If `hermes skills list` is used as a live check, set `HERMES_HOME` to the worktree `.hermes` and ignore table/header lines. It should list active `.hermes/skills` entries, not inactive `.hermes/skill-packs` entries.

## Token estimate approach

A stable rough estimate is enough for before/after comparison:

```python
from pathlib import Path
import re

def fm_value(text, key):
    m = re.search(rf'^{key}:\s*(.+)$', text, re.M)
    return m.group(1).strip().strip('"\'') if m else ''

lines=[]
for p in sorted(Path('.hermes/skills').rglob('SKILL.md')):
    text=p.read_text(errors='replace')
    lines.append(f"- {fm_value(text,'name') or p.parent.name}: {fm_value(text,'description')}")
index='\n'.join(lines)
try:
    import tiktoken
    tokens=len(tiktoken.get_encoding('cl100k_base').encode(index))
except Exception:
    tokens=round(len(index)/4)
print(tokens)
```

Use the same estimator for baseline and after-split numbers; treat the result as relative, not provider-exact.

## Pitfalls

1. Category-only moves do not reduce prompt overhead when the active skill root is still fully indexed.
2. Do not delete repo-specific skills outright; move whole directories so references/templates/scripts/assets survive.
3. Do not leave both detailed repo skills and `<repo>-pack` wrappers active, or the index reduction disappears.
4. Do not assume `skill_view` can load inactive pack skills. Inactive pack files are read directly with file tools unless a profile symlinks/copies them into active `.hermes/skills/`.
5. If a repo uses workflow-based PR creation, follow that repo convention after committing the split.
