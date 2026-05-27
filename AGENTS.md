# AGENTS.md

## Purpose
This repository uses local Skills.  
When the current working directory is `skills-jk`, always run Skill discovery before doing task work.

## Always-Run Skill Discovery
At the start of every user turn:

1. Check whether `cwd` is inside this repository.
2. Discover available skills from these sources (in order):
   - Session-provided skill list (if present)
   - `skills/` directory in this repository (each skill is `skills/<name>/SKILL.md`)
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

## Repo-Specific Skill Packs
Some repository-specific skills are stored outside active skill discovery to keep the default prompt small.

- Active entrypoints live under `.hermes/skills/software-development/<repo>-pack/SKILL.md`.
- Detailed pack contents live under `.hermes/skill-packs/<repo>/`.
- When a task matches `corp-web-japan`, `corp-web-app`, `corp-web-v2`, or `querypie-docs`, read the corresponding active `<repo>-pack` skill, then read `.hermes/skill-packs/<repo>/INDEX.md`.
- Load only the detailed `SKILL.md` files selected by that pack index; do not bulk-load an entire pack for narrow work.

## Fallback Rules
- If a named skill is missing or blocked, say so briefly and continue with best-effort fallback.
- If instructions are ambiguous, follow the safest minimal implementation and report assumptions.

## Output Contract
Before substantial work, state one short line:
- which skill(s) are being used
- why they were selected
- in what order (if multiple)

## Completion Workflow
- After finishing work, do not stop at local changes only.
- If there is no existing PR for the work branch, commit, push, and create a PR by default.
- If there is already an existing PR for the work branch, commit and push by default.
