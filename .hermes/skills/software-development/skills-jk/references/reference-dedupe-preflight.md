# Reference dedupe preflight for skills-jk

Use this checklist before adding or preserving any new `.hermes/skills/**/references/*.md` file in this repository.

## Why this exists

PR #466 removed repeated incident notes that accumulated when Hermes preserved one reference per cleanup or operations session. Most of those files were not exact byte duplicates, but they repeated the same durable routing rules that already belonged to canonical owner skills.

The goal is not to block useful new knowledge. The goal is to add the lesson to the right owner once, instead of creating another session-named note that future agents must route around.

## Preflight before creating a reference

1. Identify the durable topic, not the session story.
   - Good topic: `dirty-root preservation during workspace cleanup`.
   - Bad topic: `today's post-reset branch cleanup after PR N`.
2. Check the canonical owner map below.
3. Search the candidate owner before writing a new file:

```bash
find .hermes/skills .hermes/skill-packs skills -path '*/references/*' -type f | sort
rg -n "<topic keyword>|<error phrase>|<workflow name>" .hermes/skills .hermes/skill-packs skills
```

4. Prefer patching an existing `SKILL.md` section or reference when the rule is a clarification, pitfall, or repeated edge case.
5. Create a new `references/<topic>.md` only when all are true:
   - no existing reference owns the same durable rule;
   - the content is reusable beyond the current session transcript;
   - the filename names the class of problem, not the incident date, PR number, branch name, or temporary symptom;
   - the owning `SKILL.md` gains a short pointer to the new reference.
6. If the new lesson belongs to another repository, keep it in that repository's `.hermes/skills` instead of duplicating it here.

## Canonical owner map

| Durable topic | Update here |
| --- | --- |
| Local workspace cleanup, dirty-root preservation, stale branches/worktrees, repeated `workspace 정리` loops | `.hermes/skills/software-development/git-worktree-safety-pack/` and its references |
| General GitHub PR lifecycle, branch creation, CI interpretation, PR body safety, existing/open PR follow-up | `.hermes/skills/github/github-pr-workflow/` and `.hermes/skill-packs/github-pr-workflow/` |
| `skills-jk` bot-authored PR creation through `.github/workflows/create-pr.yml` | `.hermes/skills/software-development/skills-jk-gha-pr-creation/` |
| Repo-local Hermes profile/config-as-code conventions | `.hermes/skills/software-development/skills-jk/` or a more specific repo-local Hermes setup skill |
| Skill authoring structure, frontmatter, references/templates/scripts conventions | `.hermes/skills/software-development/hermes-agent-skill-authoring/` |
| Outbound-agent operational procedures | the outbound-agent repository's own `.hermes/skills` when available; only keep cross-repo reusable workflow here |

## Review checklist for PRs that add references

- [ ] The PR body names the canonical owner considered.
- [ ] The diff does not add a one-session incident note when an existing reference could be patched.
- [ ] The new filename is topic-level and does not include a PR number, branch name, date, or temporary failure wording.
- [ ] `SKILL.md` links to the reference if the file should be discoverable by future agents.
- [ ] Exact duplicate scan is clean when the PR adds or moves multiple reference files.

Suggested exact duplicate scan:

```bash
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
import hashlib
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
groups = defaultdict(list)
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.is_file() and '/references/' in path.as_posix() and path.suffix in {'.md', '.txt'}:
            groups[hashlib.sha256(path.read_bytes().strip()).hexdigest()].append(path.as_posix())
for files in groups.values():
    if len(files) > 1:
        print('
'.join(files), end='

')
PY
```
