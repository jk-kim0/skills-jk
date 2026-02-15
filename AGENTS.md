# AGENTS.md

## Purpose
This repository uses local Skills.  
When the current working directory is `skills-jk`, always run Skill discovery before doing task work.

## Always-Run Skill Discovery
At the start of every user turn:

1. Check whether `cwd` is inside this repository.
2. Discover available skills from these sources (in order):
   - Session-provided skill list (if present)
   - `skills/` directory in this repository
   - `$CODEX_HOME/skills/.system/` for built-in system skills
3. Build a short in-memory registry for this turn:
   - `name`
   - `description`
   - `path to SKILL.md`
4. Match user intent against the registry.

## Trigger Rules (Mandatory)
- If user mentions a skill name explicitly (`$skill-name` or plain text), use that skill.
- If user intent clearly matches a skill description, use that skill even without explicit name.
- If multiple skills match, use the minimal set and state execution order in one line.
- Do not carry skill activation across turns unless re-triggered.

## Skill Loading Policy
- Open `SKILL.md` first, and read only enough to execute correctly.
- Resolve relative paths from the skill directory first.
- Load only the specific referenced files needed (`references/`, `scripts/`, `assets/`).
- Prefer skill-provided scripts/templates over rewriting from scratch.

## Fallback Rules
- If a named skill is missing or blocked, say so briefly and continue with best-effort fallback.
- If instructions are ambiguous, follow the safest minimal implementation and report assumptions.

## Output Contract
Before substantial work, state one short line:
- which skill(s) are being used
- why they were selected
- in what order (if multiple)

