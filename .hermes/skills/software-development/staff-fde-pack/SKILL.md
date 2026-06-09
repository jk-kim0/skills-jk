---
name: staff-fde-pack
description: Use when working in the staff-fde repository, especially the staff-fde/partner-release-dashboard app; captures repo-specific workflow rules including direct gh PR creation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-context, staff-fde, partner-release-dashboard, github, pull-requests]
    related_skills: [github-pr-workflow, git-worktree-safety-pack]
---
# Staff FDE Pack

## Overview

Use this repo-context skill when working in the `staff-fde` repository, especially the `staff-fde/partner-release-dashboard/` app.

This skill captures repository-specific workflow constraints that override generic skills when they conflict.

## When to Use

- The current repository is `staff-fde`.
- The task touches or discusses `staff-fde/partner-release-dashboard/`.
- The task involves creating, updating, or documenting a PR for `staff-fde` work.

## PR Creation Rule

For work in `staff-fde/partner-release-dashboard/`, create pull requests with the direct GitHub CLI command:

```bash
gh pr create --base <base-branch> --head <feature-branch> --title "<title>" --body-file <body-file>
```

Do not use a GitHub Actions workflow-dispatch PR creation flow for this app.

If the repository has a workflow similar to `create-pr.yml`, do not treat it as the default for `staff-fde/partner-release-dashboard/`. Use `gh pr create` directly unless the user explicitly asks for a different method.

## Recommended PR Hygiene

1. Before committing or pushing, check whether the branch already has an open PR and whether that PR is still open.
2. Rebase or recreate the branch from latest `origin/main` when doing normal repo work, following the user's broader repo-work preference.
3. Write PR titles and bodies in Korean unless the user or repository guidance says otherwise.
4. Use `--body-file` for PR bodies that contain commands, Markdown tables, backticks, or shell-sensitive text.
5. Avoid auto-closing issue keywords in PR bodies unless the user explicitly instructs it.

## Common Pitfalls

1. Do not copy the `skills-jk` repository's workflow-dispatch PR creation habit into `staff-fde/partner-release-dashboard/` work.
2. Do not assume a repo-level PR creation workflow is the preferred method for this app just because such workflows exist in other repositories.
3. Do not leave a branch pushed without a PR after completing repo work; create the PR directly with `gh pr create`.

## Verification Checklist

- [ ] The task was confirmed to be in `staff-fde` or `staff-fde/partner-release-dashboard/`.
- [ ] PR creation used `gh pr create`, not a GitHub Actions workflow dispatch.
- [ ] The PR base/head, title, and body were verified after creation with `gh pr view`.
- [ ] No auto-closing issue keyword was added unless explicitly requested.
