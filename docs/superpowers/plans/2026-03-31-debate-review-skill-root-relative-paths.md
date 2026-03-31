# Debate Review Skill-Root-Relative Paths Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `cc-codex-debate-review` resolve bundled assets relative to the skill directory instead of hard-coded workspace checkout paths.

**Architecture:** Keep target repository discovery unchanged, but move bundled skill assets such as the default config to a skill-root-relative lookup. Update the skill document to describe asset references relative to the `cc-codex-debate-review/` directory so the docs match runtime behavior.

**Tech Stack:** Python, pytest, Markdown

---

### Task 1: Lock the expected runtime path behavior with tests

**Files:**
- Modify: `skills/cc-codex-debate-review/tests/test_state.py`

- [ ] **Step 1: Write the failing test**

Add a test that imports the config module and asserts the default config path resolves to `skills/cc-codex-debate-review/config.yml`, not a top-level workspace config path.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest skills/cc-codex-debate-review/tests/test_state.py -q`
Expected: FAIL because the default config path still points at a top-level workspace config path instead of the bundled `config.yml`.

- [ ] **Step 3: Write minimal implementation**

Update the config loader to derive the default path from the package file location.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest skills/cc-codex-debate-review/tests/test_state.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/cc-codex-debate-review/lib/debate_review/config.py skills/cc-codex-debate-review/tests/test_state.py
git commit -m "refactor: resolve debate-review config from skill root"
```

### Task 2: Align skill docs with the runtime contract

**Files:**
- Modify: `skills/cc-codex-debate-review/SKILL.md`
- Modify: `docs/superpowers/plans/2026-03-30-debate-review-cli-impl.md`

- [ ] **Step 1: Write the failing expectation**

Identify the remaining hard-coded skill asset paths in the skill doc and implementation plan excerpt that still reference top-level workspace paths.

- [ ] **Step 2: Update docs**

Describe bundled assets with `./...` or `cc-codex-debate-review/...` semantics and state explicitly that these are resolved relative to the skill root.

- [ ] **Step 3: Verify docs**

Run: `rg -n "~/workspace/skills-jk|\\$HOME/workspace/skills-jk" skills/cc-codex-debate-review docs/superpowers/plans/2026-03-30-debate-review-cli-impl.md`
Expected: no matches for debate-review skill asset references that should now be skill-root-relative.

- [ ] **Step 4: Commit**

```bash
git add skills/cc-codex-debate-review/SKILL.md docs/superpowers/plans/2026-03-30-debate-review-cli-impl.md
git commit -m "docs: describe debate-review assets relative to skill root"
```

### Task 3: Full verification and PR handoff

**Files:**
- Verify: `skills/cc-codex-debate-review/tests/`

- [ ] **Step 1: Run focused verification**

Run: `pytest skills/cc-codex-debate-review/tests -q`
Expected: PASS

- [ ] **Step 2: Inspect diff**

Run: `git status --short` and `git diff --stat`
Expected: only the intended files for this refactor are changed.

- [ ] **Step 3: Create branch, push, and open PR**

Use non-interactive git commands and `env -u GITHUB_TOKEN gh ...` commands.
