# Self-Hosted Runners 설정 가이드

2개의 PC(사무실, 집)를 GitHub Actions self-hosted runner로 설정하는 방법

## 개요

```
GitHub Actions (트리거)
        │
        ├── office runner (사무실 PC)
        │
        └── home runner (집 PC)
```

## Runner 설치

각 PC에서 다음 단계를 수행합니다.

### 1. GitHub에서 Runner 추가

1. Repository → Settings → Actions → Runners
2. "New self-hosted runner" 클릭
3. OS 선택 후 안내에 따라 설치

### 2. Runner에 Label 추가

설치 시 또는 설치 후 label을 추가합니다:

```bash
# 사무실 PC
./config.sh --labels office

# 집 PC
./config.sh --labels home
```

### 3. Runner를 서비스로 등록 (선택)

PC 재시작 시 자동 실행되도록 설정:

```bash
# macOS
./svc.sh install
./svc.sh start

# Linux
sudo ./svc.sh install
sudo ./svc.sh start
```

## 사용 방법

### 특정 Runner에서 실행

workflow_dispatch로 수동 실행 시 runner 선택 가능:
- `any`: 사용 가능한 아무 runner
- `office`: 사무실 PC에서만 실행
- `home`: 집 PC에서만 실행

### 자동 실행

스케줄 트리거 시 사용 가능한 runner에서 실행됩니다.
두 PC 모두 online이면 먼저 available한 runner가 작업을 가져갑니다.

## 주의사항

- 두 PC 모두 offline이면 작업이 대기 상태로 남음
- 민감한 정보는 GitHub Secrets에 저장
- Runner가 실행되는 동안 PC가 sleep 모드에 들어가지 않도록 설정
