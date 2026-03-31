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

- Config file: `~/workspace/skills-jk/config/pr-auto-review.yml` (machine-specific path, fixed to this machine's checkout location)
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

The calling prompt must declare the agent identity explicitly. Do not infer runtime from filesystem state.

| Runtime | How invoked | Agent ID | State file | Review engine |
|---------|-------------|----------|------------|---------------|
| Claude Code | `/ralph-loop` prompt includes `agent=claude` | `claude` | `~/.claude/pr-review-state.json` | Claude-native review |
| Codex | `codex exec` prompt includes `agent=codex` | `codex` | `~/.codex/pr-review-state.json` | Codex-native review |

Example invocation prompts:

```
# Claude Code (/ralph-loop)
Review pending PRs (agent=claude): load ~/workspace/skills-jk/skills/pr-auto-review/SKILL.md and execute it

# Codex (cron)
Review pending PRs (agent=codex): load $HOME/workspace/skills-jk/skills/pr-auto-review/SKILL.md and execute it
```

## Review Contract

### Target PR sources

Collect open PRs from both:

1. `review-requested=@me`
2. Every repo listed in `~/workspace/skills-jk/config/pr-auto-review.yml`

Normalize each PR into:

- `repo` (e.g. `chequer-io/deck`)
- `number`
- `url`
- `created_at`
- `head_sha`
- `is_draft`

**Important:** The two `gh` sources return different JSON structures:

- `gh search prs` returns `repository.nameWithOwner` for the repo field and does **not** include `headRefOid`
- `gh pr list --repo <repo>` returns results scoped to that repo (repo name from the command argument) and **does** include `headRefOid`

Normalize `repo` as follows:
- From `gh search prs`: use `repository.nameWithOwner`
- From `gh pr list`: use the `--repo` argument value

If `head_sha` is missing (always the case for `gh search prs` results), fetch it with:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> --json headRefOid --jq .headRefOid
```

### Ordering and limit

- De-duplicate by `repo + number`
- Remove draft PRs (`isDraft=true`) — already available from collection, no extra API call needed
- Sort by `created_at` ascending
- Apply `max_prs_per_run` cap **after** deduplication, draft removal, and sort, **before** fetching missing `head_sha` values

The cap limits the **candidate pool** (post-draft-filter), not the number of reviews actually posted. State- and comment-based skips still occur per-PR after head_sha is resolved.

### Skip rules

Skip a PR when any of the following is true:

- PR is draft (handled in Step 3 pre-filter; retained as defensive check)
- State file already has any record for this agent + `head_sha` (regardless of outcome: `commented` or `no_findings`)
- Same agent comment tag already exists on the PR

Do not skip because the other agent already commented.

Note: closed PRs are filtered by `--state open` at collection time. If a PR closes between collection and review, the `gh pr diff` or `gh pr comment` call will fail and Failure Handling applies — no state update, retried next run (at which point the PR will no longer appear in collection).

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

Example (claude):

```text
[auto-review:claude][sha:abc1234]

## Warning
- src/api.ts:42 - Retries are unbounded and can loop forever on repeated 5xx failures.

## Suggestion
- src/api.ts:75 - Extract the duplicated error mapping into a helper to keep future changes consistent.
```

### Empty review policy

If there are no actionable findings, skip comment publication and record the SHA with `outcome=no_findings`. Do not post filler comments.

## Procedure

### 1. Load config

Read `~/workspace/skills-jk/config/pr-auto-review.yml` and resolve:

- `repos`
- `max_prs_per_run`

Fail fast if the config file is missing or malformed.

### 2. Resolve runtime

Extract `agent_id` from the calling prompt (look for `agent=claude` or `agent=codex`).

Set based on `agent_id`:

| `agent_id` | `state_file` | `comment_prefix` |
|------------|--------------|------------------|
| `claude` | `~/.claude/pr-review-state.json` | `[auto-review:claude]` |
| `codex` | `~/.codex/pr-review-state.json` | `[auto-review:codex]` |

Abort if `agent_id` cannot be determined.

### 3. Collect candidate PRs

Run:

```bash
# Source 1: review-requested PRs (headRefOid not available here)
env -u GITHUB_TOKEN -u GH_TOKEN gh search prs \
  --review-requested=@me --state open --limit 100 \
  --json number,repository,createdAt,url,isDraft

# Source 2: per configured repo (headRefOid available)
env -u GITHUB_TOKEN -u GH_TOKEN gh pr list \
  --repo <owner/repo> --state open --limit 100 \
  --json number,createdAt,headRefOid,isDraft,url
```

Then:
1. Extract `repo`: use `repository.nameWithOwner` from source 1; use the `--repo` argument value from source 2
2. Merge both lists
3. De-duplicate by `repo + number`
4. Remove entries where `isDraft=true`
5. Sort by `createdAt` ascending
6. Cap to `max_prs_per_run`

### 4. Load state

Read the runtime-specific state file.

Expected record shape:

```json
{
  "owner/repo#123": {
    "head_sha": "abc1234",
    "reviewed_at": "2026-03-26T20:00:00+09:00",
    "outcome": "commented",
    "comment_tag": "[auto-review:claude][sha:abc1234]"
  }
}
```

If the file is missing, start from an empty state.
If the file is corrupted, back it up to `<state_file>.bak.<unix_timestamp>` and continue with an empty state.

### 5. For each candidate PR

For each PR in order:

1. If `head_sha` is missing, fetch: `env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> --json headRefOid --jq .headRefOid`
2. Build `comment_tag`: `[auto-review:<agent_id>][sha:<head_sha>]`
3. Check state: if same `agent_id` + same `head_sha` already recorded → skip
4. Check existing PR comments for exact `comment_tag`: `env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> --json comments --jq '.comments[].body'` → if found, update state and skip
5. Otherwise proceed to review

### 6. Run review

#### Claude Code path

- Retrieve PR diff: `env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff <number> --repo <repo>`
- Optionally use `/code-review <PR URL>` as analysis aid
- Do **not** rely on `/code-review` to satisfy the final publication contract — it does not produce the required `[auto-review:claude][sha:...]` header
- Synthesize findings and build the final normalized comment body yourself
- Publish with `gh pr comment` (step 7)

#### Codex path

- Retrieve PR diff: `env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff <number> --repo <repo>`
- `codex review` can review local repo changes via `--base` or `--commit`, but it does **not** accept a PR URL as input — do not use it in this URL/diff-driven flow
- Use Codex-native reasoning on the retrieved diff to generate review findings
- Build the final normalized comment body and publish with `gh pr comment` (step 7)

### 7. Publish comment

Publish only after the final comment body is normalized to the required header and section format:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr comment <number> --repo <owner/repo> --body "$COMMENT_BODY"
```

### 8. Verify publication

Re-read comments and confirm the exact `comment_tag` exists on the PR:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> \
  --json comments --jq '.comments[].body' | grep -F "$COMMENT_TAG"
```

Only after verification:

- update state for `repo#number`
- set `head_sha`, `reviewed_at`, `outcome=commented`, `comment_tag`

If there are no actionable findings:

- do not publish a comment
- update state for `repo#number`
- set `head_sha`, `reviewed_at`, `outcome=no_findings`
- omit `comment_tag`

## Failure Handling

- Review generation fails: do not update state
- Comment publish fails: do not update state
- Comment verification fails: do not update state
- GitHub auth/network failure: stop this run without mutating state

The same SHA will be retried on the next scheduled run unless either:

- the matching comment tag is already present on the PR
- the state file already records `outcome=no_findings` for that SHA

## Common Mistakes

- Treating Claude and Codex as mutually exclusive reviewers
- Recording state before verifying the published comment
- Using generic comments without the required agent/SHA header
- Using `/code-review` or `codex review` as the final publication step
- Skipping a PR because the other agent already reviewed it
- Using a relative path for the config file

## Quick Reference

| Task | Rule |
|------|------|
| Review frequency | Once per agent per PR SHA |
| Shared suppression | Not allowed |
| Config path | `~/workspace/skills-jk/config/pr-auto-review.yml` (machine-specific) |
| Final comment publisher | This skill (not `/code-review` or `codex review`) |
| Comment identity | `[auto-review:<agent>][sha:<head_sha>]` |
| Success condition | Verified comment exists, or `outcome=no_findings` state recorded |
