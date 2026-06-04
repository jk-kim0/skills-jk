---
name: querypie-runner-ops
description: Use when operating QueryPie self-hosted runners or querypie-mono runner cleanup workflows; contains migrated repo-specific memory and user preferences.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-context, migrated-memory]
    related_skills: []
---
# Querypie Runner Ops

## Overview

This skill is a compact trigger/index for QueryPie self-hosted runner operations, runner inventory context, and sensitive infrastructure safety expectations.

## When to Use

- The current task is in or about `querypie-runner-ops`.
- The user asks about prior conventions, repo-specific constraints, route/content policy, migration status, or operational quirks for this area.
- You are about to edit code, documentation, GitHub wiki pages, CI, deployment, or infrastructure connected to this area.

## Required Context

Known runner inventory context: Mac Studio LLM1 is reachable as `qp-test@10.11.1.11` (`Mac-Studio-LLM1.local`). QueryPie runners live at `/Users/qp-test/Workspace/github-runners-for-querypie-org`: 6 Linux ARM64 Compose runners, group `mac-studio-llm1-linux-arm64`, purpose ci/build. Verify the live host state before relying on this inventory.

For sensitive infrastructure setup such as GitHub self-hosted runners, use step-by-step guided execution and do not proceed ahead of explicit user guidance.

## Common Pitfalls

1. Do not copy repo-specific facts back into global memory unless they are broadly reusable across repositories.
2. Do not treat stored inventory notes as a substitute for live host/GitHub verification when runner counts, paths, groups, or labels may have changed.
3. Keep new findings in this skill or a more specific existing skill for the repo/workflow.

## Verification Checklist

- [ ] Skill loaded because the task matches `querypie-runner-ops`.
- [ ] Live runner host/GitHub state checked before acting on potentially stale inventory notes.
- [ ] Live repo/source checked before acting on potentially stale implementation details.
