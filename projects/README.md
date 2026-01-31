# Projects

장기 목표 또는 작업 그룹을 관리합니다.

## 구조

- `active/` - 진행 중인 프로젝트
- `archive/` - 완료/중단된 프로젝트

## 파일 포맷

```markdown
---
id: project-id
title: 프로젝트 제목
status: active|archived
repos:
  - https://github.com/...
created: YYYY-MM-DD
---

# Project Title

## 목표
...

## 범위
...

## 관련 Tasks
- [task-id](링크)

## 마일스톤
### Q1 2024
- [ ] 목표 1

## 메모
...
```
