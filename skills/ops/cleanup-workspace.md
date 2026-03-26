---
name: cleanup-workspace
description: 최근 PR 상태 확인, local stale branch 정리, stale worktree 제거, base branch 이동 - 작업 시작/종료 시 workspace 정리
tags: [git, branch, worktree, pr, cleanup, workspace]
---

# Cleanup Workspace

## 목적

작업 시작 또는 종료 시 workspace를 정리한다:
1. 현재 repo의 최근 PR 상태 확인
2. Workspace 전체의 stale local branch 삭제
3. Stale git worktree 제거
4. 현재 repo의 base branch(main / develop)로 이동

## When to Use

- "PR 상태 확인하고 브랜치 정리해줘"
- "local stale branch, stale worktree 정리해줘"
- "workspace 정리해줘"
- 작업 종료 후 환경 초기화 시

---

## Step 1: 현재 repo의 최근 PR 상태 확인

```bash
gh pr list --state all --limit 15 \
  --json number,title,state,createdAt,mergedAt \
  --jq '.[] | "[\(.state)] #\(.number) \(.title) (\(.createdAt[:10]))"'
```

OPEN PR은 요약하여 사용자에게 보고한다.

---

## Step 2: Base Branch 감지

현재 repo에서 base branch 이름을 감지한다.

```bash
# Method 1: remote HEAD에서 감지 (가장 신뢰할 수 있음)
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'
```

위 명령이 결과를 반환하지 않으면 순차적으로 확인한다:

```bash
# Method 2: main → develop 순서로 존재 여부 확인
git show-ref --verify --quiet refs/remotes/origin/main && echo "main" \
  || git show-ref --verify --quiet refs/remotes/origin/develop && echo "develop" \
  || echo "main"
```

> 감지된 base branch 이름을 `BASE_BRANCH` 변수로 기억한다.

---

## Step 3: Workspace 전체 Stale Branch 정리

`~/workspace/skills-jk/bin/git-cleanup-branches` 스크립트를 사용한다.

### 3-1. Dry-run으로 확인

```bash
git-cleanup-branches
```

stale로 감지된 브랜치 목록을 사용자에게 보고한다.

### 3-2. 삭제 실행

```bash
git-cleanup-branches --delete
```

> 스크립트가 삭제 전 현재 브랜치가 stale이면 자동으로 base branch로 이동한다.

---

## Step 4: Stale Worktree 정리

### 4-1. 전체 worktree 목록 확인

```bash
git worktree list
```

### 4-2. Metadata pruning (누락된 경로 자동 정리)

```bash
git worktree prune
```

### 4-3. Prunable worktree 식별 및 제거

`git worktree list --porcelain` 출력에서 `prunable` 항목을 찾는다.

```bash
git worktree list --porcelain | grep -B5 "prunable"
```

각 prunable worktree의 경로를 확인하고 제거한다:

```bash
git worktree remove --force <path>
```

### 4-4. Detached HEAD worktree (PR review용) 정리

`/tmp/` 또는 `.worktrees/` 아래의 detached HEAD worktree 중:
- 디렉토리 이름 패턴: `*-pr-NNN*`, `*pr-NNN*`, `*-review*`
- 해당 PR 번호를 추출하여 PR 상태를 확인

```bash
# PR 번호 추출 예시: /tmp/querypie-pr939-review → PR #939
gh pr view <pr-number> --json state --jq '.state'
```

**제거 기준:**
- PR state가 `MERGED` 또는 `CLOSED` → 제거
- `OPEN` → 사용자에게 보고 후 확인

```bash
git worktree remove --force <path>
```

### 4-5. `.worktrees/` 디렉토리 하위 worktree 정리

repo 내 `.worktrees/` 디렉토리가 있는 경우, 각 worktree의 branch 상태를 확인:

```bash
git worktree list | grep ".worktrees/"
```

해당 브랜치의 PR이 MERGED/CLOSED인 경우:

```bash
git worktree remove --force <path>
rmdir <path>  # 빈 디렉토리 정리 (실패해도 무시)
```

---

## Step 5: Base Branch로 이동

Step 2에서 감지한 `BASE_BRANCH`로 이동하고 최신 상태로 업데이트한다.

```bash
git checkout <BASE_BRANCH>
git pull origin <BASE_BRANCH>
```

---

## 출력 형식

완료 후 다음 형식으로 요약 보고한다:

```
## Workspace 정리 완료

### PR 상태 (현재 repo)
- OPEN: N건 → #NNN 제목, #NNN 제목, ...
- 최근 MERGED: N건

### Branch 정리
- 삭제된 stale branch: N건 (repo-name: branch-name, ...)
- 삭제 없음 / 해당 없음

### Worktree 정리
- 제거된 worktree: N건 (경로, ...)
- 제거 없음 / 해당 없음

### 현재 브랜치
- [repo-name] main (최신 상태)
```

---

## 주의사항

- `OPEN` 상태의 worktree는 **절대 자동 제거하지 않는다** — 사용자 확인 후 진행
- `git worktree remove` 실패 시 `--force` 옵션으로 재시도
- `git-cleanup-branches`가 PATH에 없으면 `~/workspace/skills-jk/bin/git-cleanup-branches`를 직접 실행
