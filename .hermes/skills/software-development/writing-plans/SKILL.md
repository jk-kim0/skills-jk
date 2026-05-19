---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
version: 1.1.1
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Writing Implementation Plans

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

## When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## Plan Document Structure

### Header (Required)

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Scope Boundary

When the user asks for a plan, planning document, migration plan, audit plan, or checklist, treat the deliverable as the plan itself unless they explicitly ask for implementation.

- Do not create implementation files, helper modules, data migrations, asset renames, or production code just because the plan identifies them as future work.
- It is acceptable to inspect code, run read-only/browser verification, and update the planning document.
- If the user resolves an open decision during planning, rewrite the plan so the resolved choice appears as a concrete directive in the relevant step/checklist, rather than leaving a separate “decision needed” section.
- If implementation accidentally starts and the user corrects the scope, revert/remove the out-of-scope implementation artifacts and continue with documentation only.

### Planning framework adoption plus first usage

When planning a repository-wide foundation change and its first concrete usage (for example adding Tailwind CSS and then converting one page to Tailwind classes), split the plan into two PRs unless the user explicitly asks to bundle them:

1. **Foundation PR** — dependencies, build/config files, global imports/token bridges, tiny helper utilities, and minimal smoke verification only. Explicitly forbid production page rewrites in this PR.
2. **Usage PR** — the individual page/component migration that depends on the foundation. If the foundation PR is still open, document the stacked-base option and parent PR reference; if merged, branch the usage PR from latest main.

The plan document should spell out allowed files, forbidden scope, verification for each PR, and whether the usage PR is stacked or main-based. For CSS framework adoption specifically, include a preflight/global-style risk note and require checking whether the target repo already has the framework pipeline before proposing className-only rewrites.

When the existing app has legacy global resets or CSS Modules, explicitly plan the cascade-layer migration path. Do not treat global reset changes as part of a routine route migration: document whether the first usage PR must use route-scoped CSS Module / stable `data-*` selector corrections while leaving `globals.css` unchanged, then schedule a separate visual-risk PR for moving reset/base rules into the framework layer (for Tailwind v4, usually `@layer base`) and a cleanup follow-up to remove temporary route-scoped corrections. Acceptance criteria should require browser computed-style validation, because className presence and generated CSS rules can still lose to cascade. See `references/css-framework-global-reset-risk.md`.

### Preserve broad migration scope when the first usage is only a pilot

When a user asks for a plan that starts with one page, route, collection, or feature as the first implementation target, do not accidentally narrow the whole plan to that pilot. Explicitly separate:

- **Overall scope** — the full class of pages/routes/collections/surfaces the migration is meant to cover.
- **First milestone** — the initial page or family chosen because it is urgent, broken, easiest to validate, or provides the reference pattern.
- **Follow-up sequence** — the remaining families/surfaces in a reviewable order, usually one route family or page group per PR.
- **Common rules** — behavior that must remain stable across all follow-up PRs, such as route/canonical/sitemap boundaries, CMS-managed surface exclusions, loader/frontmatter preservation, and whether customer-facing copy may mention internal implementation terms.

If the user corrects “this is not only X; it starts with X,” update the plan title, goal, architecture, PR labels, follow-up sections, and acceptance criteria so every part reflects the broader scope. Avoid leaving a document whose title or task headings still imply X-only scope while a small paragraph says otherwise.

## Writing Process

### Step 1: Understand Requirements

Read and understand:
- Feature requirements
- Design documents or user description
- Acceptance criteria
- Constraints

### Step 2: Explore the Codebase

Use Hermes tools to understand the project:

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

### Step 3: Design Approach

Decide:
- Architecture pattern
- File organization
- Dependencies needed
- Testing strategy

### Step 4: Write Tasks

Create tasks in order:
1. Setup/infrastructure
2. Core functionality (TDD for each)
3. Edge cases
4. Integration
5. Cleanup/documentation

### Step 5: Add Complete Details

For each task, include:
- **Exact file paths** (not "the config file" but `src/config/settings.py`)
- **Complete code examples** (not "add validation" but the actual code)
- **Exact commands** with expected output
- **Verification steps** that prove the task works

### Step 6: Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

### Step 7: Save the Plan

```bash
mkdir -p docs/plans
# Save plan to docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:
```bash
git add [files]
git commit -m "type: description"
```

## Common Mistakes

### Vague Tasks

**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code

**Bad:** "Step 1: Add validation function"
**Good:** "Step 1: Add validation function" followed by the complete function code

### Missing Verification

**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths

**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Execution Handoff

After saving the plan, offer the execution approach:

**"Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"**

When executing, use the `subagent-driven-development` skill:
- Fresh `delegate_task` per task with full context
- Spec compliance review after each task
- Code quality review after spec passes
- Proceed only when both reviews approve

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious.**
