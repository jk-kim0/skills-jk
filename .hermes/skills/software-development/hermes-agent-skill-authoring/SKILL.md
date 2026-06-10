---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [writing-plans, requesting-code-review]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/`:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range. If you're pushing past 20k, split into `references/*.md` and reference them from SKILL.md.

## Peer-Matched Structure

Every in-repo skill follows roughly:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

## Directory Placement

Default Hermes-agent repository shape:

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

Important repo-override rule:
- Some skill-library repositories intentionally do **not** use category directories. For example an internal `skills.sh` style repository may require `skills/<skill-name>/SKILL.md` and a `description` block containing `Trigger:` lines.
- When working outside the Hermes-agent source tree, read the repository guidance first (for example `AGENTS.md` and `docs/skill-management.md`) and inspect 2-3 peer `skills/*/SKILL.md` files before choosing a path or frontmatter shape.
- Treat the repository's checked-in guide and peer shape as authoritative over this skill's default category layout. If the guide says self-developed skills go directly under `skills/<name>/`, do not create `skills/devops/<name>/` just because the source skill came from a categorized Hermes library.

Personal-to-shared skill promotion pattern:
- When a user asks to move one or more personal/local skills into a shared skill repository, first preserve the original content long enough to identify reusable responsibilities, then refactor into class-level shared skills rather than mirroring a personal skill tree verbatim.
- Split generic enabling workflows from domain-specific operations. Example: a general access/protocol workflow such as `QueryPie Multi Agent Seamless SSH` should become its own skill, while a runner-specific skill should reference it and focus on GitHub runner diagnostics, inventory, redaction, and operations.
- Put environment- or organization-specific target lists, mappings, and snapshots in `references/*.md`; keep `SKILL.md` focused on durable procedure, trigger rules, safety rules, and links to the reference.
- If the first draft combines a generic workflow and a domain-specific operation, treat a review request to separate them as a boundary correction: add the generic skill, narrow the original skill, remove duplicated procedure text from references, then update the same open PR branch.

## Workflow

1. **Survey peers** in the target category:
   ```
   ls skills/<category>/
   ```
   Read 2-3 peer SKILL.md files to match tone and structure.
2. **Check validator constraints** in `tools/skill_manager_tool.py` if unsure.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md`.
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** on the active branch.
6. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

Validation/commit safety:
- When combining validation, `git diff --check`, commit, and push in one shell command, start the command with `set -e` or split validation into a separate tool call. A failed Python assertion or validation command must stop the commit path; otherwise the shell can continue to `git add` / `git commit` and leave a pushed change whose validation actually failed.
- If a validation assertion fails because it was too broad for the existing skill body, rerun a narrower validation that checks only the changed section before creating or updating the PR, and mention both the initial failure and corrected validation in the report.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Promoting Personal Skills into a Shared Skill Repository

When moving a user-local or personal skill into a shared/internal repository, do not blindly mirror the original skill tree.

Preferred workflow:

1. Read the target repository's own skill-management guide first; its directory shape may differ from Hermes' category layout. For example, a repo may require `skills/<name>/SKILL.md` with no category subdirectory.
2. Start from a latest-main branch/worktree before writing the shared skill.
3. Preserve the original skill's intent and proven commands, but rewrite the body for the target audience and remove private/session-only dependencies.
4. If the source skill contains concrete inventories, host mappings, incident findings, or other context that is useful but not the main procedure, move that material into `references/<topic>.md` and add a one-line pointer from `SKILL.md`.
5. Keep secrets out of both `SKILL.md` and references. Runner tokens, PATs, `.env` values, private keys, cookies, and credential-like environment values should be described only as redacted metadata.
6. Validate the resulting files for frontmatter, diff hygiene, accidental tool line-number prefixes, and conflict markers before committing.
7. For a review-first handoff, create the PR as Draft and expect follow-up edits on the same branch rather than opening a second PR.

Common pitfall: copying a personal skill's references verbatim can leave dangling links to private paths or session-specific files. Convert those links into shared repo-local `references/` files when the detail is still useful, or remove them when they are only historical noise.

## Canonical Docs + Thin Skill Wrapper Pattern

When a repository needs both human-readable guidance and an agent skill for the same workflow, avoid maintaining the same detailed checklist in two places.

Preferred shape:

- Put the complete, canonical procedure in `docs/<topic>.md`, `ops/<topic>.md`, or another repo documentation page when humans and agents both need to read it.
- Keep the repo-local `SKILL.md` as a very thin trigger/index that covers only:
  - when to load the skill
  - the exact path to the canonical docs page
  - optional pointers to related skills, without restating their procedures
- Put reusable output formats/templates in one `references/<template-or-format>.md` file when the format is used by more than one prompt/doc/skill.
- Do not duplicate scripts, taxonomy tables, viewport lists, reporting formats, verification checklists, done criteria, examples, or step-by-step execution rules in both the docs page and the skill.
- For product/technical/operational decisions that include rationale, alternatives, and future implementation impact, pick one canonical decision log document for the change (for example `openspec/changes/<change-id>/design.md`, `docs/adr/<topic>.md`, or a repo-standard ADR path). Feature design docs, implementation plans, handoff docs, issues, and repo-local skills should only link to that decision log or carry a very short current-conclusion summary; do not copy the same decision table into multiple places.
- If a prompt/runbook must remain self-contained enough for cron/autonomous execution, prefer embedding the execution procedure in the canonical runbook and making the skill point to it, rather than copying the same procedure into every required skill.
- If the reviewer says the skill and docs are still duplicative, remove more from the skill rather than arguing that the remaining duplicate is only a summary.
- If the skill needs session-specific or deeply technical supporting detail that is not appropriate for human-facing docs, place it under `references/` and add a one-line pointer from `SKILL.md`.
- For status inventory documents (for example `docs/feature-status.md`) where the user wants the document to stay focused on the actual list/table, move durable authoring rules, source-discovery order, evidence checks, status definitions, and review procedures into a repo-local class-level skill. Leave the inventory doc with only a short purpose/scope plus a pointer to that skill; do not leave extracted sections behind as “related docs”, “review process”, or long definitions.

Use this pattern especially after a reviewer notes duplication between a docs guide and a skill, or asks for non-inventory guidance to be split out of an inventory/status document. Make the source-of-truth split explicit, then remove the duplicated guidance from the other artifact rather than keeping a summary that still competes with the skill. For repo-local cron/runbook work, explicitly document the source-of-truth split in the canonical doc (for example: runbook owns schedule/procedure; `references/` owns report template; `SKILL.md` files are thin indexes).

## Repo-Local Skills Need Agent Guidance Entry Points

When a user asks to create or update a "repo-local skill", treat it as checked-in repository source, not as a user-local runtime skill.

1. Read the repository guidance first (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, etc.) to find the canonical skill root. Common patterns include `.agents/skills/<name>/SKILL.md` with `.hermes`/`.codex` symlinks pointing at `.agents`.
2. Obey the repository's branch/worktree policy. If guidance says changes must be made under repo-local `.worktrees/`, create a fresh latest-main worktree and write the skill there instead of modifying the root checkout.
3. Use file tools (`write_file` / `patch`) for the checked-in `SKILL.md`; do not use `skill_manage(action='create')`, because that creates a user-local skill outside the repo.
4. Validate frontmatter and size just like bundled skills, then commit the repository change. If the repo workflow expects PRs for source changes, push and open/update a PR rather than leaving only a local commit.
5. In the final report, include the exact skill path, branch/commit/PR URL if created, and note that the current session may not auto-discover the newly added repo-local skill until a fresh session or explicit path read.

When a repository contains checked-in skills under a non-Hermes runtime path such as `.agents/skills/<name>/SKILL.md`, do not assume the current agent runtime will auto-discover or `skill_view` them.

If the user reports that repo-local skills are not being referenced, or you discover `.agents/skills/` without an `AGENTS.md`/equivalent repository guidance file:

1. Inspect a sibling or source repository's `AGENTS.md` if the user names one.
2. Add or update the target repo's `AGENTS.md` to define:
   - `.agents/skills/` as the canonical repo-local skill root
   - `.agents/skills/README.md` or the repo's actual `.agents/README.md` as the local skill index
   - explicit trigger rules mapping task classes to skill files
   - a fallback instruction to read `.agents/skills/<name>/SKILL.md` directly when native skill loading cannot see repo-local skills
3. Keep the guidance concise and class-level; do not paste entire skill procedures into `AGENTS.md`.
4. If the repo has `.agents/README.md` but no `.agents/skills/README.md`, update `.agents/README.md` with a short skill index instead of inventing a second index file unless the repo guidance asks for one.
5. For a user request to create a rich repo-local skill plus reference material, use the source-of-truth split deliberately: a human-facing canonical doc when humans and agents both need the rule, a concise `SKILL.md` trigger/procedure, and `references/*.md` for detailed good/bad examples and session-specific nuance.
6. Put this guidance change in a separate branch/PR before continuing feature work when the user asks for it or when it is a prerequisite to correct agent behavior.
7. Check `.gitignore`: some repositories ignore `AGENTS.md`. If the repo intentionally needs tracked agent guidance, stage it with `git add -f AGENTS.md` and mention that in the PR summary.

Common pitfall: merely committing `.agents/skills/**` is not enough. Future agents need a tracked entry point that tells them to discover and read those repo-local skills. Another pitfall is creating a detailed skill but forgetting the repo's local skill index, so future agents see `AGENTS.md` yet still lack a quick trigger map.

## Active-PR Repo-Local Skill Follow-Up

When the user asks to save a repo-specific skill while you already have an open PR/worktree for the same operational change, update that same branch/PR if the skill documents the workflow introduced by that PR. Do not create a separate local-only skill or a separate PR unless the skill is unrelated to the active change.

Required follow-up pattern:

1. Add the skill under the repository's canonical skill root (for example `.agents/skills/<skill-name>/SKILL.md`) and match existing peer frontmatter/structure.
2. If the new skill governs generated documentation or content, encode the repository-specific renderer/content contract directly in the skill: supported Markdown subset, frontmatter rules, locale completeness, labeling rules for incomplete/Mock-Up sections, and the exact static validation checks to run. Do not leave those rules only in the PR body or current chat.
3. Validate the skill frontmatter and `git diff --check`.
4. Commit the skill on the active branch and update the existing PR body to mention the new repo-local skill.
5. Fetch/rebase onto latest `origin/main` before force-pushing, because main may have advanced while the PR was open and may already contain overlapping docs/script fixes.
6. If rebase conflicts occur, preserve the already-merged main intent and keep the skill commit as the active PR's unique addition.
7. Verify the remote head SHA, PR file list, and fresh check runs after push.

Pitfalls:
1. Adding a repo-local skill after the PR is already open can make `mergeStateStatus` turn `DIRTY` if another PR landed meanwhile. Treat this as normal PR hygiene: rebase/resolve before reporting the skill update as complete.
2. Writing a repo-local skill that only says "read OpenSpec" or "update docs" is too thin when the session discovered concrete content-production rules. Capture the class-level workflow and validation contract so future agents do not repeat ad hoc inspection and labeling decisions.
3. When the user corrects a newly-authored repo-local skill's trigger or scope, update the skill itself immediately on the same PR branch. If the correction broadens a narrow environment/task skill into a class-level skill, rename the directory and frontmatter `name` to the broader class instead of only appending trigger phrases to the old narrow skill. Also update the PR title/body so reviewers see the new class-level scope.
4. When editing PR bodies that contain backticks or shell-sensitive text, write the body to a temporary file and use `gh pr edit --body-file <file>` instead of embedding the body in a shell-quoted command. This avoids accidental command substitution and corrupted PR descriptions.
5. In a git worktree, `.git` may be a pointer file rather than a directory. Do not write PR body files or other temporary review artifacts to `<worktree>/.git/<name>` unless you first resolve the actual git dir. Prefer `mktemp` or `/tmp/<repo>-<purpose>.md` for `gh pr create --body-file` / `gh pr edit --body-file` inputs.

## Skill Library Maintenance Shape

When updating the skill library after a session, prefer class-level umbrella skills over one-session-one-skill entries.

### Reference dedupe / refactor workflow

When the user asks to review skill `references/` docs or remove duplication across the skill library:

1. Treat the work as class-level source curation, not as one more session-note capture pass.
2. Scan existing `references/*.md` files for exact repeated paragraphs and topic clusters before writing new support files.
3. Pick one canonical owner for each repeated decision/workflow, then convert sibling files into short adapters that link to the canonical reference and add only skill-specific application notes.
4. Keep `SKILL.md` bodies as triggers, routing rules, pitfalls, and short reminders; move long checklists, example formats, and session evidence into `references/`.
5. Remove session/PR-number-specific names from reusable references when the lesson is durable, e.g. rename `pr123-...` into a class-level pattern name.
6. Before committing, run a changed-reference duplicate scan and a stale session-name/PR-number scan, then include those verification results in the PR body.
7. If unrelated local dirty files exist, preserve them outside the commit scope while rebasing/PR-creating; do not accidentally stage runtime or memory residue just because it was present during the curation task.
8. If an existing helper/reference such as a repo-local dedupe preflight already covers part of the requested procedure, do not simply duplicate it verbatim in a new skill. Create a new class-level umbrella only when the requested class is broader (for example duplicate `SKILL.md` responsibilities plus duplicate `references/` docs), and cross-link or summarize the narrower owner instead of copying all of its text.
9. For `skills-jk` itself, a requested library-curation workflow skill should normally be an active repo-local skill under `.hermes/skills/software-development/<class-name>/SKILL.md`, not a root-level governed policy under `skills/`, unless the guidance is meant to constrain both Hermes and Codex globally.

Be active by default:
- Treat "review the conversation and update the skill library" as an instruction to find and encode at least one reusable lesson when the session had any non-trivial workflow, correction, or repeated pattern.
- Do not default to `Nothing to save.` just because the task ended successfully; first look for a small governing-skill patch, pitfall, or concise `references/` note.
- User workflow/style corrections belong in the governing `SKILL.md`, not only in memory, so future sessions start with the corrected workflow.
- If a skill was loaded or consulted during the session and the new lesson fits it, update that currently-loaded skill first instead of creating a narrow session-specific skill.
- If the user explicitly restricts the skill-library update pass to memory/skill-management tools, do not attempt repository reads, Git commands, PR creation, or file-tool edits. Use `skill_manage(action='patch'|'write_file')` on the loaded or existing umbrella skill that owns the lesson, then report the exact skill updated and any overlap noticed.

Default update order:
1. Patch a skill that was actually loaded or used in the session if it governs the same task class.
2. If no loaded skill fits, patch an existing umbrella skill after checking `skills_list` / `skill_view`.
3. Put session-specific measurements, error transcripts, reproduction recipes, or detailed page examples under `references/<topic>.md`, then add a one-line pointer from `SKILL.md`.
4. Create a new skill only when no existing class-level skill covers the workflow.

Naming rule:
- A good skill name describes a recurring class of work, e.g. `browser-render-parity-comparison` or `corp-web-japan-live-page-render-parity`.
- A bad skill name only makes sense for today's task, e.g. a PR number, issue number, URL slug, exact error string, feature codename, or `fix-<specific-bug>`.

Maintenance pitfall:
- Do not append every session's raw findings directly to a large umbrella `SKILL.md`. If the learning is mostly concrete measurements or task-specific evidence, move the detail into `references/` and keep the umbrella body to the general rule and a pointer.
- User style/workflow corrections are skill material, not only memory material: embed them in the governing skill as a pitfall or required step so the next session starts with the corrected workflow.

## Editing Existing In-Repo Skills

- **Small fix (typo, added pitfall, tightened trigger):** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` works fine on in-repo skills.
- **Major rewrite:** `write_file` the whole SKILL.md. `skill_manage(action='edit')` also works but requires supplying the full new content.
- **Adding supporting files:** `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`. `skill_manage(action='write_file')` also works and enforces the references/templates/scripts/assets subdir allowlist.
- **When the user cites a prior issue/PR/report as evidence that a skill output was hard to read, inspect that artifact first and patch the governing skill's reusable template/checklist, not just the one artifact. Encode the missing field as a required template column, evidence rule, pitfall, and verification checklist item when all four help prevent recurrence.
- **Always commit** the edit — in-repo skills are source, not runtime state.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leaving a reusable workflow trapped in one repo after the user asks to generalize it.** If a workflow was first authored as a repo-local `.agents/skills/<name>/SKILL.md` and the user says to add it to `skills-jk` or make it general-purpose, create a class-level shared skill under the appropriate `.hermes/skills/<category>/<name>/` directory, remove or rewrite repository-specific paths, product names, issue examples, and project-only assumptions, and keep only adaptable examples. Do not simply copy the repo-local skill verbatim into the shared library.

3. **Bulk-generating skill files without Hermes file writes.** When creating many `SKILL.md` and `references/*` files from a script, call `hermes_tools.write_file()` from `execute_code` (or the normal `write_file` tool) for every intended repository write, then verify with `read_file` / `search_files`. Do not rely on ad hoc direct filesystem writes in a helper script without an immediate tool-backed verification pass; if verification shows no files, rerun through `write_file` rather than continuing from assumed state.

4. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation.

3. **Description too generic.** Peer descriptions start with "Use when ..." and describe the *trigger class*, not the one task. "Use when debugging X" > "Debug X".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2-3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

## Verification Checklist

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Use when ..."
- [ ] Total file ≤ 100,000 chars (aim for 8-15k)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch
