---
name: pr-auto-review
description: Use when running scheduled automatic PR reviews across configured repositories with separate Claude Code and Codex review state
---

# PR Auto Review

## Overview

Automatically review open pull requests on a schedule and post one review comment per agent per HEAD SHA.

This skill supports a dual-agent setup:

- Claude Code reviews a PR once per SHA
- Codex reviews the same PR once per SHA

These are independent outcomes. One agent's review must not suppress the other.

## Inputs

- Config file: `config/pr-auto-review.yml`
- State file:
  - Claude Code: `~/.claude/pr-review-state.json`
  - Codex: `~/.codex/pr-review-state.json`
- GitHub CLI access via keychain auth

## Required GitHub Command Form

Always remove injected token variables before calling GitHub CLI:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh <subcommand>
```

## Runtime Contract

Determine the active runtime from the caller context, not from the mere existence of `~/.claude` or `~/.codex`.

| Runtime | Agent ID | State file | Review engine |
|---------|----------|------------|---------------|
| Claude Code | `claude` | `~/.claude/pr-review-state.json` | Claude-assisted review, optionally using `/code-review` as analysis aid |
| Codex | `codex` | `~/.codex/pr-review-state.json` | Codex-native review flow |

## Review Contract

### Target PR sources

Collect open PRs from both:

1. `review-requested=@me`
2. Every repo listed in `config/pr-auto-review.yml`

Normalize each PR into:

- `repo`
- `number`
- `url`
- `created_at`
- `head_sha`
- `is_draft`
- `state`

If `head_sha` is missing from list output, fetch it with `gh pr view`.

### Ordering and limit

- De-duplicate by `repo + pr_number`
- Sort by `created_at` ascending
- Process at most `max_prs_per_run`

### Skip rules

Skip a PR when any of the following is true:

- PR is closed
- PR is draft
- Same agent already recorded the same `head_sha`
- Same agent comment tag already exists on the PR

Do not skip because the other agent already commented.

## Comment Contract

### Required header

The final published comment must start with:

- Claude Code: `[auto-review:claude][sha:<head_sha>]`
- Codex: `[auto-review:codex][sha:<head_sha>]`

### Required body shape

Only publish actionable findings in these sections:

- `## Critical`
- `## Warning`
- `## Suggestion`

Each finding should include a file reference when possible.

Example:

```text
[auto-review:codex][sha:abc1234]

## Warning
- src/api.ts:42 - Retries are unbounded and can loop forever on repeated 5xx failures.

## Suggestion
- src/api.ts:75 - Extract the duplicated error mapping into a helper to keep future changes consistent.
```

### Empty review policy

If there are no actionable findings, prefer skipping comment publication. Do not post filler comments.

## Procedure

### 1. Load config

Read `config/pr-auto-review.yml` and resolve:

- `repos`
- `max_prs_per_run`

Fail fast if the config file is missing or malformed.

### 2. Resolve runtime

Set:

- `agent_id`
- `state_file`
- `comment_prefix`

### 3. Collect candidate PRs

Run:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh search prs --review-requested=@me --state open --json number,repository,createdAt,url,isDraft
env -u GITHUB_TOKEN -u GH_TOKEN gh pr list --repo <owner/repo> --state open --json number,createdAt,headRefOid,isDraft,url
```

Then normalize, de-duplicate, sort, and cap by `max_prs_per_run`.

### 4. Load state

Read the runtime-specific state file.

Expected record shape:

```json
{
  "owner/repo#123": {
    "head_sha": "abc1234",
    "reviewed_at": "2026-03-26T20:00:00+09:00",
    "comment_tag": "[auto-review:codex][sha:abc1234]"
  }
}
```

If the file is missing, start from an empty state.
If the file is corrupted, back it up and continue with an empty state.

### 5. For each candidate PR

For each PR:

1. Fetch current `head_sha` if needed
2. Build `comment_tag`
3. Check state for same-agent same-SHA completion
4. Check existing PR comments for the same `comment_tag`
5. Skip or review

### 6. Run review

#### Claude Code path

- Use Claude-native review capabilities
- `/code-review <PR URL>` may be used to generate analysis
- Do not rely on `/code-review` to satisfy the final publication contract
- If `/code-review` cannot guarantee the required comment header, generate the final normalized comment yourself and publish it with `gh pr comment`

#### Codex path

- Run a Codex-native review against the PR diff
- `codex review` may be used when operating locally on a checked-out branch
- When reviewing by PR URL without a prepared checkout, use Codex-native reasoning plus `gh`-retrieved diff/context and publish the final normalized comment with `gh pr comment`

### 7. Publish comment

Publish only after the final comment body is normalized to the required header and section format.

Example:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr comment <pr-number> --repo <owner/repo> --body "$COMMENT_BODY"
```

### 8. Verify publication

Re-read comments and confirm the exact `comment_tag` exists on the PR.

Only after verification:

- update state for `repo#pr`
- set `head_sha`
- set `reviewed_at`
- set `comment_tag`

## Failure Handling

- Review generation fails: do not update state
- Comment publish fails: do not update state
- Comment verification fails: do not update state
- GitHub auth/network failure: stop this run without mutating state

The same SHA may be retried on the next scheduled run unless the matching comment tag is already present.

## Common Mistakes

- Treating Claude and Codex as mutually exclusive reviewers
- Recording state before verifying the published comment
- Using generic comments without the required agent/SHA header
- Assuming `/code-review` is the final publication step
- Skipping a PR because the other agent already reviewed it

## Quick Reference

| Task | Rule |
|------|------|
| Review frequency | Once per agent per PR SHA |
| Shared suppression | Not allowed |
| Final comment publisher | This skill |
| Comment identity | `[auto-review:<agent>][sha:<head_sha>]` |
| Success condition | Verified comment exists, then state update |
