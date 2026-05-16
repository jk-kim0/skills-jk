# Codex CLI 0.130 goals feature and Hermes-porting notes

Use this reference when the user asks about Codex CLI `/goal`, goal persistence, or recreating Codex goals in Hermes.

## What `/goal` is in Codex 0.130

On this machine, `/goal` is not a separate installed plugin or repo-local skill. It is controlled by the Codex feature flag:

```bash
codex features list | rg '^goals'
```

Observed state:

```text
goals  experimental  true
```

The config knob is:

```toml
[features]
goals = true
```

## Upstream implementation shape

The relevant upstream Codex source paths are:

- `codex-rs/core/src/tools/handlers/goal_spec.rs`
- `codex-rs/core/src/tools/handlers/goal.rs`
- `codex-rs/core/src/tools/handlers/goal/create_goal.rs`
- `codex-rs/core/src/tools/handlers/goal/get_goal.rs`
- `codex-rs/core/src/tools/handlers/goal/update_goal.rs`
- `codex-rs/core/src/goals.rs`
- `codex-rs/core/templates/goals/continuation.md`
- `codex-rs/core/templates/goals/budget_limit.md`
- `codex-rs/core/templates/goals/objective_updated.md`

The feature exposes three model tools when enabled:

- `get_goal`: read current thread goal, status, token budget, elapsed-time usage, token usage, and remaining token budget.
- `create_goal`: create a new active objective only when explicitly requested; fails if a goal already exists.
- `update_goal`: intentionally narrow; only marks an existing goal `complete`. Pause/resume/budget-limited states are user/runtime-controlled.

Important contract from `goal_spec.rs`:

- Do not infer goals from ordinary tasks.
- Set `token_budget` only when explicitly requested.
- Do not mark a goal complete because the turn is ending or because the budget is nearly exhausted.
- Completion requires the objective to actually be achieved and no required work to remain.

## Continuation prompt behavior

The continuation prompt treats the objective as user-provided data, not higher-priority instructions. Core behaviors:

- Keep the full objective intact across turns.
- Do not redefine success around a smaller/easier subset.
- Work from authoritative current state, not stale conversation memory.
- Before completion, audit every explicit requirement, referenced artifact, command, test, gate, invariant, and deliverable against current evidence.
- Treat uncertain, indirect, or missing evidence as not complete.

## Hermes porting pattern used in skills-jk PR #335

Because Hermes does not currently have native per-thread goal runtime hooks, the practical port is:

1. Add a `goal` Hermes skill (`name: goal`) so Hermes' skill slash-command mechanism exposes `/goal ...`.
2. Add a transparent state-management script such as `bin/hermes-goal`.
3. Store goal JSON under `$HERMES_GOAL_HOME`, `$HERMES_HOME/goals`, or `~/.hermes/goals`.
4. Recreate the behavioral contract in the skill body:
   - explicit creation only
   - objective as user-provided task data
   - continuation from current evidence
   - completion only after requirement-by-requirement audit
5. Add tests for lifecycle, duplicate active-goal prevention, continuation prompt rendering, named slots, and clear behavior.

Verification commands used:

```bash
python3 -m pytest tests/test_hermes_goal.py -q
python3 - <<'PY'
from pathlib import Path
import re, yaml
path = Path('.hermes/skills/productivity/goal/SKILL.md')
content = path.read_text()
assert content.startswith('---')
match = re.search(r'\n---\s*\n', content[3:])
assert match
frontmatter = yaml.safe_load(content[3:match.start()+3])
assert frontmatter['name'] == 'goal'
assert frontmatter['description']
assert len(frontmatter['description']) <= 1024
assert content[match.end()+3:].strip()
PY
```

## Pitfalls

- Do not look for `codex plugin list`; Codex 0.130 has `codex plugin marketplace`, but `/goal` is a feature flag path, not a listed plugin.
- Do not treat Codex's feature as automatically portable to Hermes core. Without Hermes runtime hooks, implement it as skill + script + explicit agent discipline.
- Do not claim exact per-goal token accounting in Hermes unless a real runtime accounting hook exists; a script-level port can only record advisory/manual token counts.
- If the user asks to make the feature usable immediately in the active repo-local Hermes setup, remember that copying the script/skill into the active root checkout after PR creation can leave untracked root files until the PR merges or the root is updated.