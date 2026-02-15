---
name: create-pr
description: PR 생성 전 반드시 확인 - Bot 작성자 및 Co-Author 규칙, PR 승인/병합 금지
tags: [pr, git, github, workflow, bot]
---

# PR 생성 규칙

## 핵심 규칙

| 항목 | O | X |
|------|---|---|
| PR 작성자 | `github-actions[bot]` | 개인 계정 |
| Co-Author | `Atlas <atlas@jk.agent>` | `Claude ...` |
| PR 생성 | `gh workflow run create-pr.yml` | `gh pr create` |

## ⛔ 절대 금지 사항

> **모든 PR은 사람이 리뷰하고 병합해야 합니다. Claude가 절대로 수행해서는 안 됩니다.**

| 금지 행위 | 명령어 예시 | 이유 |
|-----------|-------------|------|
| PR 승인 | `gh pr review --approve` | 코드 리뷰는 사람이 수행 |
| PR 병합 | `gh pr merge` | 병합 결정은 사람이 수행 |
| PR 닫기 | `gh pr close` | 명시적 지시 없이 닫기 금지 |
| 리뷰 코멘트로 승인 | `gh pr review --comment "LGTM"` | 승인 의도의 코멘트 금지 |

### PR 닫기 규칙

- **명시적으로 Close를 지시하기 전에는 PR을 닫지 않습니다**
- PR에 문제가 있는 경우: 닫지 말고 수정 (rebase, force push 등)
- PR 재활용 우선: 새 PR 생성보다 기존 PR 수정 선호

**적용 범위**: querypie-mono를 포함한 **모든 저장소**의 PR

## 명령어

```bash
# 커밋
git commit -m "feat: ..." --trailer "Co-Authored-By: Atlas <atlas@jk.agent>"
git push -u origin <branch>

# PR 생성
gh workflow run create-pr.yml -f branch="<branch>" -f title="<type>: ..."
```

## PR Scope Gate (필수)

PR 생성 전에 아래 검증을 **반드시 통과**해야 합니다.  
목적: base 브랜치 대비 불필요한 커밋/파일 포함 방지.

### 1) 기준(base) 명시

- 기본값: `origin/main`
- Stacked PR인 경우: 직전 브랜치(`origin/<parent-branch>`)를 base로 명시

### 2) 커밋 범위 검증

```bash
git fetch origin --prune
git log --oneline <base>..HEAD
```

판정 기준:
- 의도한 커밋만 보여야 함
- 작업과 무관한 과거 커밋이 보이면 **PR 생성 중단**

### 3) 파일 범위 검증

```bash
git diff --name-status <base>...HEAD
```

판정 기준:
- 의도한 파일만 포함되어야 함
- 무관한 파일이 있으면 **PR 생성 중단**

### 4) 이상 시 복구 절차 (스크립트 금지, 수동 명령만)

```bash
# 새 정리 브랜치를 base에서 시작
git checkout -b <new-branch> <base>

# 필요한 커밋만 선택 반영
git cherry-pick <commit1> [<commit2> ...]

# 기존 PR 브랜치에 강제 반영
git push --force-with-lease origin <new-branch>:<old-pr-branch>
```

### 5) PR 생성 전 보고 형식 (필수)

PR 생성 실행 전에 아래 4개를 먼저 공유:
- base 브랜치
- `git log --oneline <base>..HEAD` 결과
- `git diff --name-status <base>...HEAD` 결과
- 이상 유무와 진행 여부(생성/중단)

## gh 실행 환경 규칙

로컬에서 `gh`를 실행할 때는 환경변수 토큰을 제거하고 keyring 인증을 사용합니다.

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh <subcommand>
```

이유:
- 셸에 주입된 `GITHUB_TOKEN`/`GH_TOKEN`이 권한 제한 토큰일 경우 `gh pr create`/`gh pr edit`/`gh pr view` 등이 실패할 수 있음
- 사용자 계정 keyring 토큰(`gh auth login`)을 우선 사용해야 일관된 권한으로 동작

## 스크립트 실행 규칙

`python3 script.py` 대신, 스크립트에 실행권한을 부여해 직접 실행합니다.

```bash
chmod +x ./script.py
./script.py
```

적용 범위:
- 로컬 자동화 스크립트 실행 전반
- PR 본문의 실행 예시 명령어 작성 시 동일 규칙 적용

## 커밋 수정 후 PR 업데이트

커밋을 amend/추가한 경우:

```bash
# 1. 푸시
git push --force-with-lease origin <branch>

# 2. PR 제목/설명 재검토 및 수정
gh pr edit <pr-number> --title "..." --body "..."
```

**체크리스트:**
- [ ] PR 제목이 최종 커밋 내용을 반영하는가?
- [ ] PR 설명이 모든 변경사항을 포함하는가?
- [ ] `<base>..HEAD` 커밋 범위가 의도와 일치하는가?
- [ ] `<base>...HEAD` 파일 범위가 의도와 일치하는가?

## 실수 방지 Hook 설치

```bash
cp .github/hooks/commit-msg .git/hooks/ && chmod +x .git/hooks/commit-msg
```

Hook이 검사하는 항목:
- `Co-Authored-By: Claude ...` 형식 사용 시 커밋 차단

## 관련 문서

- [branch-workflow](./branch-workflow.md) - 전체 워크플로우
- [bot-authorship](../../docs/bot-authorship.md) - Bot 작성자 상세
