---
name: github-issue-validity-check
description: >
  Validate whether a GitHub issue is still valid against the latest main branch
  by reading the issue via gh, comparing the codebase against origin/main, and
  confirming runtime behavior when needed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, issue-triage, validation, regression, main-branch, browser]
    related_skills: [requesting-code-review, systematic-debugging, github-code-review]
---

# GitHub Issue Validity Check

Use this skill when the user asks whether a GitHub issue is still valid on the
latest `main` branch, especially for UI/behavior bugs.

## Goal

Answer one of these with evidence:
- the issue is still valid on latest `main`
- the issue is already fixed on latest `main`
- the issue is partially valid / ambiguous and needs clarification

## Workflow

1. Read the issue details from GitHub.
   - Prefer `gh issue view <number> --repo <owner/repo> --json ...`.
   - If the browser page is 404, do not assume the issue is inaccessible; use `gh`.

2. Check the repo state.
   - Confirm branch and remote.
   - Compare the current code against `origin/main`.
   - If the user asked about "latest main", inspect `origin/main`, not the
     current worktree branch.

3. Inspect the code paths implicated by the issue.
   - Search for relevant components, styles, helpers, and routes.
   - Read the files that likely control the behavior.
   - Compare the relevant files to `origin/main` when needed.

4. Verify runtime behavior when the issue is visual or interactive.
   - Start or reuse the local app if necessary.
   - Use the browser to inspect the live page.
   - Check computed styles or DOM behavior when the issue is about cursor,
     hover, visibility, layout, interaction, or text rendering.

5. Decide validity.
   - If the code clearly matches the issue and the live page reproduces it,
     mark it valid.
   - If the current `main` branch already fixes it, mark it invalid on main.
   - If one symptom is fixed and another remains, call it partially valid.

## Evidence Checklist

For a valid/invalid verdict, gather at least one of:
- issue text from `gh issue view`
- code evidence from `read_file` / `search_files`
- diff evidence against `origin/main`
- live browser evidence (DOM snapshot or computed style)

## Pitfalls

- A GitHub issue URL may show a generic page or 404 in the browser.
  Always fall back to `gh issue view`.
- The current branch may differ from `main`; do not judge validity from the
  current branch unless the user explicitly asks about it.
- Visual issues often need live browser verification; source code alone may be
  insufficient.
- Text-cursor vs pointer behavior can be a browser default, not a code bug.
  Confirm the computed cursor on the element before concluding.

## Output Style

Keep the conclusion concise and explicit:
- "Valid on latest main"
- "Fixed on latest main"
- "Partially valid"

Then include short evidence bullets.
