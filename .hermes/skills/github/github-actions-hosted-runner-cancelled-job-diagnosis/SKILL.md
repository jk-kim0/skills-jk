---
name: github-actions-hosted-runner-cancelled-job-diagnosis
description: Diagnose GitHub Actions runs that appear as failures but whose jobs were actually cancelled before any step started because a GitHub-hosted runner was never acquired.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, actions, ci, debugging, runner, hosted-runner]
---

# GitHub Actions hosted-runner cancelled-job diagnosis

Use this when a user gives you a GitHub Actions run/job URL and asks why it failed, especially when the UI says `failure` but the job page shows little or no log output.

## Core pattern

A workflow run can end with overall `conclusion: failure` even though the actual job never executed repository code.

Typical signature:
- job `conclusion` is `cancelled`
- job `steps` is empty
- `gh run view --job ... --log` returns `log not found`
- raw job metadata shows `runner_id: 0`
- `gh run view --verbose` shows an annotation like:
  - `The job was not acquired by Runner of type hosted even after multiple attempts`

When these all line up, the root cause is GitHub-hosted runner acquisition failure, not a failing build/test/deploy command.

## Investigation flow

Always use `gh` through the governed form:

```bash
env -u GITHUB_TOKEN gh run view <RUN_ID> --json name,displayTitle,event,status,conclusion,headBranch,headSha,url,jobs
env -u GITHUB_TOKEN gh run view <RUN_ID> --verbose
```

Then inspect the raw job object:

```bash
env -u GITHUB_TOKEN gh api repos/<owner>/<repo>/actions/runs/<RUN_ID>/jobs
```

If you need the specific job/check-run details:

```bash
env -u GITHUB_TOKEN gh api repos/<owner>/<repo>/check-runs/<JOB_ID>
```

## How to interpret the evidence

### Case A: real script failure
You likely have repository or workflow logic problems when:
- steps are present
- logs exist
- runner is assigned
- a specific command/step failed

Then debug the failing step itself.

### Case B: hosted runner acquisition failure
You likely have GitHub infrastructure/scheduling failure when:
- steps are absent
- logs are missing
- runner is not assigned (`runner_id: 0`)
- job is `cancelled`
- verbose annotation explicitly mentions hosted runner acquisition failure

Then do **not** blame checkout/build/deploy scripts.

## Extra checks

These help rule out adjacent causes:

1. Check workflow file for concurrency cancellation:
```bash
# inspect .github/workflows/<file>.yml
```
Look for:
- `concurrency:`
- `cancel-in-progress: true`

2. Check environment protection rules if the job targets an environment.

3. Check whether steps started at all.
- If no steps started, environment approval waits or script crashes are much less likely than runner acquisition failure.

## Recommended user-facing conclusion

Summarize clearly:
- the run looked like a failure at the workflow level
- but the job itself was cancelled before any step started
- the hosted runner was never acquired
- therefore the immediate cause is GitHub Actions runner availability/acquisition, not repo code

## Recommended next action

First response:
- rerun the workflow

If it repeats:
- check GitHub Actions status/incidents
- watch for organization-wide hosted-runner capacity issues
- consider self-hosted runners for critical deploy workflows
- consider adding retry/operational runbook guidance around production deploy jobs

## Evidence pattern from the saved case

Observed production deploy case:
- workflow run `conclusion: failure`
- job `Deploy` `conclusion: cancelled`
- `steps: []`
- `runner_id: 0`
- `gh run view --verbose` annotation: `The job was not acquired by Runner of type hosted even after multiple attempts`

This is the canonical pattern for this skill.
