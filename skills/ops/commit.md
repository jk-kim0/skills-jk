---
name: commit
description: Commit Log 작성 Skill - PR 병합 여부 확인 및 커밋 규칙
tags: [git, commit, pr, workflow]
---

# Commit 규칙

## 핵심 규칙

### 1. 커밋 전 PR 병합 여부 확인 (필수)

기존 브랜치에 커밋할 때, 반드시 해당 브랜치의 PR이 이미 병합되었는지 확인합니다.

```bash
# PR 상태 확인
gh pr list --head <branch-name> --state all --json number,state,mergedAt

# 또는 PR 번호를 알고 있는 경우
gh pr view <pr-number> --json state,mergedAt
```

| PR 상태 | 조치 |
|---------|------|
| `OPEN` | 커밋 & 푸시 가능 |
| `MERGED` | 새 브랜치 생성 후 새 PR 작성 |
| `CLOSED` | 새 브랜치 생성 후 새 PR 작성 |

### 2. PR이 이미 병합된 경우

```bash
# 1. main 브랜치로 이동 및 업데이트
git checkout main
git pull origin main

# 2. 새 브랜치 생성
git checkout -b <new-branch-name>

# 3. 필요한 파일 복사 또는 cherry-pick
git cherry-pick <commit-hash>  # 또는 수동으로 파일 복사

# 4. 새 PR 생성
git push -u origin <new-branch-name>
gh workflow run create-pr.yml -f branch="<new-branch-name>" -f title="<type>: ..."
```

## 커밋 메시지 형식

```bash
git commit -m "$(cat <<'EOF'
<type>: <subject>

<body>

Co-Authored-By: Atlas <atlas@jk.agent>
EOF
)"
```

### Type 종류

| Type | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `refactor` | 리팩토링 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드/설정 변경 |

## 체크리스트

- [ ] PR 병합 여부 확인했는가?
- [ ] Co-Authored-By 트레일러가 올바른가? (`Atlas <atlas@jk.agent>`)
- [ ] 커밋 메시지가 변경 내용을 명확히 설명하는가?

## 관련 문서

- [create-pr](./create-pr.md) - PR 생성 규칙
- [branch-workflow](./branch-workflow.md) - 브랜치 워크플로우
