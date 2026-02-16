---
name: using-git-worktrees
description: Use when working on multiple branches or isolated tasks - create and manage git worktrees to avoid branch contamination
tags: [git, workflow, worktree]
---

# Using Git Worktrees

## 목적

브랜치 간 오염 없이 병렬 작업 환경을 만듭니다.

## 수행 절차

1. 기준 브랜치 최신화
2. worktree 생성
3. 각 worktree에서 독립 작업
4. 완료 후 worktree 정리

## 기본 명령

```bash
git checkout main
git pull origin main
git worktree add ../<repo>-<topic> -b <prefix>/<topic>
```
