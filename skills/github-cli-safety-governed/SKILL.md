---
name: github-cli-safety-governed
description: Use when any task requires GitHub access, including issue, PR, run, or API lookup via GitHub CLI.
---

# GitHub CLI Safety Governed

## When to use

- GitHub 이슈, PR, Actions, API, 브랜치 메타데이터를 조회하거나 수정할 때
- `gh` 를 한 번이라도 실행해야 할 때
- GitHub 인증/권한 오류를 진단할 때

## Hard gate

`gh` 를 raw 형태로 실행하지 않는다.

허용 형식:

```bash
env -u GITHUB_TOKEN gh ...
```

금지 형식:

```bash
gh ...
GITHUB_TOKEN=... gh ...
```

## Required sequence

1. GitHub 접근이 필요하다고 판단하면 먼저 이 규칙을 적용한다고 명시한다.
2. 첫 `gh` 호출부터 항상 `env -u GITHUB_TOKEN gh ...` 를 사용한다.
3. 인증 또는 권한 오류가 나면 다른 추측 전에 아래 순서로 다시 확인한다.

```bash
env -u GITHUB_TOKEN gh auth status -h github.com
env -u GITHUB_TOKEN gh <same command>
```

4. 이후의 모든 `gh` 호출도 동일하게 `env -u GITHUB_TOKEN gh ...` 로 유지한다.

## Non-negotiable checks

- 이슈 조회도 예외가 아니다.
- 읽기 전용 명령도 예외가 아니다.
- `gh issue view`, `gh pr view`, `gh pr checks`, `gh run view`, `gh api` 전부 동일 규칙을 따른다.

## Required sequence for CI/run verification

PR, CI, manual dispatch 검증 시에는 아래 순서를 강제한다.

1. 먼저 최신 head SHA를 확인한다.

```bash
env -u GITHUB_TOKEN gh pr view <pr> --repo <owner>/<repo> --json headRefOid
```

2. 같은 head SHA 기준으로 `pull_request` 와 `workflow_dispatch` run을 각각 조회한다.

```bash
env -u GITHUB_TOKEN gh run list --repo <owner>/<repo> --branch <head-branch> --limit 30 --json databaseId,workflowName,event,headSha,status,conclusion,createdAt
```

3. 검증이 필요하다고 말한 경로는 해당 run의 핵심 job 로그까지 직접 확인한다.
   - 예: `detect`, `e2e-ready`, `e2e-*`, `ci-gate`

```bash
env -u GITHUB_TOKEN gh run view <run-id> --repo <owner>/<repo> --json jobs
env -u GITHUB_TOKEN gh run view <run-id> --repo <owner>/<repo> --job <job-id> --log
```

4. 조회 결과가 바로 안 보이면 `미확인` 으로 표현한다. exact SHA 기준 조회 전에는 `없다`고 단정하지 않는다.

## Failure pattern to avoid for CI checks

- `gh pr checks` 결과만 보고 manual `workflow_dispatch` 검증까지 끝났다고 간주하는 것
- 최신 head SHA를 확인하지 않고 오래된 run으로 결론 내리는 것
- `미확인` 을 `부재` 로 바꿔 말하는 것
- exact SHA 기준 run 조회 없이 “manual 실행 로그가 없다”고 단정하는 것

## Failure pattern to avoid

- 규칙을 알고 있다고 가정하고 raw `gh` 를 바로 실행하는 것
- 인증 오류 뒤에 토큰 범위를 추측하면서 `env -u GITHUB_TOKEN` 재실행을 빼먹는 것
- 웹 검색이나 curl 로 우회하기 전에 `env -u GITHUB_TOKEN gh ...` 를 먼저 시도하지 않는 것
