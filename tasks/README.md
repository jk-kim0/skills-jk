# Tasks

구체적인 할 일 단위를 관리합니다.

## 구조

- `active/` - 진행 중인 작업
- `backlog/` - 대기 중인 작업
- `done/` - 완료된 작업 (아카이브)

## 파일 포맷

```markdown
---
id: task-YYYY-MM-DD-NNN
title: 작업 제목
status: active|backlog|done
priority: high|medium|low
project: project-id
skills: [skill1, skill2]
repo: https://github.com/...
created: YYYY-MM-DD
due: YYYY-MM-DD
---

# Task Title

## 목표
...

## 상세 내용
...

## 완료 조건
- [ ] 조건 1

## 진행 로그
### YYYY-MM-DD
- 내용
```

## 상태 관리

Task의 상태가 변경되면 해당 폴더로 파일을 이동합니다:
- 새 작업 → `backlog/`
- 작업 시작 → `active/`
- 작업 완료 → `done/`
