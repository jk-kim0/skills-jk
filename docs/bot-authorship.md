# Bot으로 PR 작성하기

PR 작성자를 사람이 아닌 Bot/AI Agent 이름으로 표시하는 방법을 정리합니다.

## 현재 적용된 방식: github-actions[bot]

이 Repository의 모든 자동화된 PR은 `github-actions[bot]`으로 생성됩니다.

### 구현 방법

**1. Workflow에 permissions 설정:**
```yaml
permissions:
  contents: write
  pull-requests: write
```

**2. Git 사용자 설정:**
```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
```

**3. GITHUB_TOKEN으로 PR 생성:**
```bash
GH_TOKEN: ${{ github.token }}
gh pr create --title "..." --body "..."
```

### 공통 스크립트

`.github/scripts/create-pr.sh` 스크립트를 사용하여 PR을 생성합니다:

```bash
.github/scripts/create-pr.sh <branch_prefix> <pr_title> [pr_body]
```

### 결과

| 항목 | 표시 이름 |
|------|----------|
| 커밋 작성자 | `github-actions[bot]` |
| PR 작성자 | `github-actions[bot]` |
| Co-Author | AI Agent 이름 (아래 참조) |

## AI Agent Co-Author 목록

| Agent | Co-Author 형식 |
|-------|----------------|
| Atlas | `Atlas <atlas@jk.agent>` |
| Claude | `Claude <claude@jk.agent>` |

## 방법 비교

| 방법 | 작성자 표시 | 추가 설정 | 제한사항 |
|------|-------------|----------|----------|
| **GITHUB_TOKEN (현재)** | `github-actions[bot]` | 없음 | PR이 다른 workflow 트리거 안함 |
| GitHub App | `Atlas[bot]` (커스텀) | App 생성 필요 | 없음 |
| PAT | 사용자 본인 | Token 생성 | Bot으로 표시 안됨 |

## 제한사항

`GITHUB_TOKEN`으로 생성한 PR은 **다른 workflow를 트리거하지 않습니다.**

예: `on: pull_request` workflow가 자동 실행되지 않음

이 제한이 문제가 된다면 GitHub App 또는 PAT를 사용해야 합니다.

## 참고 자료

- [How to use the github-actions bot](https://github.com/orgs/community/discussions/25863)
- [peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request)
- [actions/create-github-app-token](https://github.com/actions/create-github-app-token)
