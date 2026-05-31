# Tencent VM container-image CD: PR cache-only vs main deploy

Session-derived pattern for outbound-agent-style Tencent VM container CD.

## Problem

A PR head commit ID is not stable as the final deployed version:

- the PR branch can be rebased or amended;
- GitHub squash/rebase merge creates a new `main` commit ID;
- therefore a PR-built image tag must not be described as the final deployment artifact.

## Recommended workflow shape

Use one workflow for both validation and deployment, but make the mode explicit.

- `pull_request`
  - checkout the PR state;
  - compute the current commit metadata only for summary/validation;
  - run `docker buildx build ... --output=type=cacheonly`;
  - do not `docker login` / `docker push`;
  - skip all VM-mutating jobs.

- `push` to `main`
  - checkout the final `main` commit;
  - compute the immutable tag from that final commit;
  - build and push the image once;
  - pass the exact pushed image as a job output to sequential VM deploy jobs.

- `workflow_dispatch`
  - allow explicit `push_image` for manual promotion/rollback workflows if needed;
  - keep VM deploy gated by explicit inputs or separate deploy workflow.

## Naming / review visibility

Make cache-only behavior visible in places reviewers actually see:

- workflow `name` / `run-name`: include `PR Cache-Only Build Validation` and `Main Deploy`;
- job name: use wording like `Cache-only validation / publish outbound-front image`;
- step summary: print a `Mode` line:
  - `PR Cache-Only Build Validation` for PRs;
  - `Main Publish + Tencent Deploy` for main push;
- PR body: state that PR tags are temporary PR-head validation tags and are not reused for deploy;
- runbook/current-state docs: document that PR does no registry push and no Tencent VM deploy.

## Transient registry/rate-limit failures

If a PR cache-only validation fails while loading base image metadata from Docker Hub, and the log shows `429 Too Many Requests` / unauthenticated pull rate limit, classify it as transient registry exhaustion rather than a product-code failure.

Recommended response:

1. Inspect the failed job log and quote the registry/rate-limit line in the internal diagnosis.
2. Do not change app or docs just to satisfy the failed Docker check.
3. If the PR branch is behind `origin/main`, rebase the PR branch onto latest main and push with `--force-with-lease`; this both restores branch hygiene and triggers fresh checks on the current merge base.
4. If the branch accumulated iterative fixup commits during PR maintenance, squash them into one reviewer-facing commit before the force push when that improves reviewability.
5. Verify the fresh run is attached to the new head SHA. If it passes, report the previous failure as resolved transient infrastructure.

## Commit tag rule

For outbound-agent, the immutable image tag uses the 7-character commit id:

```bash
git rev-parse --short=7 HEAD
```

Example:

```text
ireg.querypie.io/ci/outbound-front:e4051c1
```

Do not change this to 12 characters during PR follow-up unless the user explicitly changes the convention.
