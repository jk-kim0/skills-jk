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

## 실수 방지 Hook 설치

```bash
cp .github/hooks/commit-msg .git/hooks/ && chmod +x .git/hooks/commit-msg
```

Hook이 검사하는 항목:
- `Co-Authored-By: Claude ...` 형식 사용 시 커밋 차단

## 관련 문서

- [branch-workflow](./branch-workflow.md) - 전체 워크플로우
- [bot-authorship](../../docs/bot-authorship.md) - Bot 작성자 상세
