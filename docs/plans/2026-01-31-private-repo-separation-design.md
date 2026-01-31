# Private Repository 분리 설계

## 개요

공개 Repository(skills-jk)에서 Skills, 문서, 공개 Tasks/Projects를 유지하면서, 비공개 Tasks/Projects는 별도 Private Repository에서 관리하는 구조를 설계한다.

## 저장소 구조

### Public repo (`skills-jk`)

```
skills-jk/
├── skills/          # 공개 스킬
├── docs/            # 공개 문서
├── tasks/           # 공개 가능한 Task
├── projects/        # 공개 가능한 Project
└── agents/          # Agent 정의
```

### Private repo (`skills-jk-private`)

```
skills-jk-private/
├── tasks/           # 비공개 Task
├── projects/        # 비공개 Project
└── .hooks/          # Pre-commit hook 스크립트
```

### 로컬 작업 디렉토리 (분리)

```
~/workspace/
├── skills-jk/           # Public
└── skills-jk-private/   # Private
```

두 repo는 완전히 분리된 디렉토리에서 작업하여 실수로 파일이 섞이는 것을 방지한다.

## 비공개 판단 기준

Task/Project 생성 시 다음 조건 중 하나라도 해당되면 Private repo에서 관리한다.

| 조건 | 확인 방법 |
|------|----------|
| Slack 메시지 기반 작업 | 출처가 Slack인가? |
| Private git repo 작업 | `gh api repos/{owner}/{repo}` → visibility 확인 |
| 고객사 이름 명시 | PR 리뷰 시 수동 확인 |

### 체크리스트

```markdown
## 공개 여부 판단 체크리스트

Task/Project 생성 전 확인:
- [ ] 출처가 Slack 메시지인가? → Private
- [ ] 작업 대상 repo가 private인가? → Private
- [ ] 고객사 이름이 포함되는가? → Private
- [ ] 위 항목 모두 해당 없음 → Public 가능
```

## Pre-commit Hook 검증

Public repo(`skills-jk`)에 pre-commit hook을 설치하여 2차 검증한다.

### 검증 항목

| 검증 | 동작 |
|------|------|
| Slack 키워드 탐지 | `Slack`, `slack.com`, `#channel` 패턴 발견 시 경고 |
| Private repo 참조 | 새 Task 파일의 `repo:` 필드 → GitHub API로 visibility 확인 |

### Hook 동작 방식

```bash
# .git/hooks/pre-commit (Public repo)

1. 커밋 대상 파일 중 tasks/, projects/ 파일 확인
2. Slack 관련 키워드 패턴 검사
3. 새로 추가된 파일의 repo: 필드가 있으면
   → gh api로 visibility 확인 (최초 1회)
4. 위반 발견 시 커밋 차단 + 안내 메시지 출력
```

### 안내 메시지 예시

```
⚠️  민감 정보 감지됨
- tasks/active/task-001.md: "Slack" 키워드 발견
- 이 Task는 skills-jk-private repo에서 관리하세요.
커밋이 차단되었습니다.
```

## 워크플로우

```
새 Task/Project 생성 요청
        │
        ▼
체크리스트 확인
├─ Slack 기반? ─────────────┐
├─ Private repo 작업? ──────┤
└─ 고객사명 포함? ──────────┤
        │                   │
        ▼                   ▼
    모두 아니오           하나라도 예
        │                   │
        ▼                   ▼
  skills-jk (Public)   skills-jk-private
        │                   │
        ▼                   ▼
   Pre-commit Hook       (Hook 없음)
   2차 검증                 │
        │                   │
        ▼                   ▼
     커밋/푸시            커밋/푸시
        │                   │
        ▼                   ▼
     PR 생성              PR 생성
        │
        ▼
   JK PR 리뷰
   (고객사명 수동 확인)
```

Private repo는 이미 비공개이므로 별도 hook이 필요 없다.

## 구현 작업 목록

### 1단계: Private repo 생성

- GitHub에서 `skills-jk-private` 생성 (Private)
- `tasks/`, `projects/` 폴더 구조 초기화
- README에 용도 및 비공개 기준 명시

### 2단계: Public repo 업데이트

- `docs/repository-visibility.md` 업데이트 (공개/비공개 기준 명시)
- Pre-commit hook 스크립트 작성 및 설치
- Task/Project 생성 Skill에 체크리스트 추가

### 3단계: 문서화

- 비공개 판단 체크리스트 Skill 문서
- 두 repo 간 관계 및 운영 가이드

## 산출물

| 파일 | 위치 | 내용 |
|------|------|------|
| Pre-commit hook | `skills-jk/.git/hooks/pre-commit` | 민감 정보 검증 |
| 운영 가이드 | `skills-jk/docs/repository-visibility.md` | 공개/비공개 기준 |
| 체크리스트 Skill | `skills-jk/skills/ops/task-visibility.md` | 생성 시 판단 기준 |
| Private repo README | `skills-jk-private/README.md` | 용도 설명 |
