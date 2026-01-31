# Projects

장기 목표 또는 작업 그룹을 관리합니다.

## Private Projects

비공개 프로젝트는 **[skills-jk-private](https://github.com/jk-kim0/skills-jk-private)** 저장소에서 관리합니다.

| 저장소 | 용도 |
|--------|------|
| `skills-jk` (여기) | 공개 프로젝트 |
| `skills-jk-private` | 비공개 프로젝트, Task (Slack 기반, Private repo 작업, 고객사 정보 등) |

> 비공개 기준 상세: [docs/repository-visibility.md](../docs/repository-visibility.md)

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
