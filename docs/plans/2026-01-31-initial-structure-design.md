# Skills-JK 초기 구조 설계

## 개요

AI Agent를 위한 Skill, Task, Project 관리 시스템

## 요구사항

- Skills 관리 + Task/Project 추적
- 8개 이상의 유동적인 프로젝트 관리
- 자동화 업무: 코드 작업, 반복 운영, 정보 수집/분석
- 실행 방식: 체크리스트/스케줄/이벤트 기반 자동 + 수동 트리거
- 실행 환경: GitHub Actions (트리거) + 로컬 self-hosted runner (실행)
- 구조: Skills, Tasks, Projects 독립적이되 서로 참조 가능

## 개념 정의

- **Skill**: AI Agent가 특정 작업을 수행하는 방법/지침
- **Task**: 구체적인 할 일 단위
- **Project**: 장기 목표 또는 작업 그룹

## 디렉토리 구조

```
skills-jk/
├── skills/           # AI Agent 작업 지침
│   ├── coding/       # 코드 작업 관련
│   ├── ops/          # 운영/배포 관련
│   └── research/     # 조사/분석 관련
│
├── tasks/            # 구체적인 할 일
│   ├── active/       # 진행 중인 작업
│   ├── backlog/      # 대기 중인 작업
│   └── done/         # 완료된 작업 (아카이브)
│
├── projects/         # 장기 목표/작업 그룹
│   ├── active/       # 진행 중인 프로젝트
│   └── archive/      # 완료/중단된 프로젝트
│
├── .github/
│   └── workflows/    # GitHub Actions 워크플로우
│
└── docs/
    └── plans/        # 설계 문서
```

## 파일 포맷

### Skill

```markdown
---
name: skill-name
description: 스킬 설명
tags: [tag1, tag2]
---

# Skill Title

## 목적
...

## 수행 절차
...

## 출력 형식
...
```

### Task

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
- [ ] 조건 2

## 진행 로그
### YYYY-MM-DD
- 내용
```

### Project

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

## GitHub Actions 구조

### 스케줄 기반 실행

```yaml
name: Scheduled Tasks
on:
  schedule:
    - cron: '0 9 * * 1'
  workflow_dispatch:

jobs:
  run-tasks:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Run AI Agent
        run: claude "tasks/active 폴더의 due가 임박한 task를 처리해줘"
```

### 이벤트 기반 실행

```yaml
name: Event Triggered
on:
  repository_dispatch:
    types: [task-request]
  issue_comment:
    types: [created]

jobs:
  handle-event:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Process Event
        run: claude "이벤트를 분석하고 적절한 task를 실행해줘"
```

## 구현 순서

1. 디렉토리 생성
2. 첫 번째 Skill 작성
3. 첫 번째 Project 생성
4. 첫 번째 Task 생성
5. Self-hosted runner 설정
6. 자동화 워크플로우 추가
