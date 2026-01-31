# Self-Hosted Runners 설정 가이드

GitHub Actions self-hosted runner 설정 및 관리 방법

## 현재 Runner 구성

### Home PC (MacBook ARM64)

| Runner | 라벨 | 디렉토리 | 상태 |
|--------|------|----------|------|
| home-A | `self-hosted`, `macOS`, `ARM64`, `home`, `A` | `~/actions-runner-a` | online |
| home-B | `self-hosted`, `macOS`, `ARM64`, `home`, `B` | `~/actions-runner-b` | online |
| home-C | `self-hosted`, `macOS`, `ARM64`, `home`, `C` | `~/actions-runner-c` | online |

### Office PC (예정)

| Runner | 라벨 | 디렉토리 | 상태 |
|--------|------|----------|------|
| office-A | `self-hosted`, `office`, `A` | TBD | 미설정 |
| office-B | `self-hosted`, `office`, `B` | TBD | 미설정 |
| office-C | `self-hosted`, `office`, `C` | TBD | 미설정 |

## 아키텍처

```
GitHub Actions (트리거)
        │
        ├── home runners (집 MacBook)
        │   ├── home-A
        │   ├── home-B
        │   └── home-C
        │
        └── office runners (사무실 PC) - 예정
            ├── office-A
            ├── office-B
            └── office-C
```

## Runner 설치 방법

### 1. Runner 디렉토리 생성 및 다운로드

```bash
# 디렉토리 생성
mkdir -p ~/actions-runner-a ~/actions-runner-b ~/actions-runner-c

# Runner 다운로드 (최신 버전 확인: https://github.com/actions/runner/releases)
curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.331.0/actions-runner-osx-arm64-2.331.0.tar.gz

# 각 디렉토리에 압축 해제
tar xzf actions-runner.tar.gz -C ~/actions-runner-a
tar xzf actions-runner.tar.gz -C ~/actions-runner-b
tar xzf actions-runner.tar.gz -C ~/actions-runner-c
```

### 2. 등록 토큰 발급

```bash
# gh CLI로 토큰 발급
gh api -X POST repos/jk-kim0/skills-jk/actions/runners/registration-token --jq '.token'
```

### 3. Runner 설정

```bash
# Runner A 설정
cd ~/actions-runner-a
./config.sh --url https://github.com/jk-kim0/skills-jk \
  --token <TOKEN> \
  --labels home,A \
  --name home-A \
  --unattended

# Runner B, C도 동일하게 (라벨과 이름만 변경)
```

### 4. 서비스 등록

```bash
# 각 runner 디렉토리에서 실행
./svc.sh install
./svc.sh start
```

## 서비스 관리 명령어

```bash
# 상태 확인
./svc.sh status

# 중지
./svc.sh stop

# 시작
./svc.sh start

# 서비스 제거
./svc.sh uninstall
```

## Runner 제거 방법

```bash
cd ~/actions-runner-a

# 서비스 중지 및 제거
./svc.sh stop
./svc.sh uninstall

# GitHub에서 runner 제거
./config.sh remove --token $(gh api -X POST repos/jk-kim0/skills-jk/actions/runners/registration-token --jq '.token')
```

## Workflow에서 사용

### 특정 Runner 지정

```yaml
jobs:
  build:
    runs-on: [self-hosted, home, A]  # home-A에서만 실행
```

### 위치 기반 선택

```yaml
jobs:
  build:
    runs-on: [self-hosted, home]  # home의 아무 runner에서 실행
```

### 병렬 실행 (3개 작업 동시)

```yaml
jobs:
  task-a:
    runs-on: [self-hosted, home, A]
  task-b:
    runs-on: [self-hosted, home, B]
  task-c:
    runs-on: [self-hosted, home, C]
```

## 주의사항

- Runner가 실행되는 동안 PC가 sleep 모드에 들어가지 않도록 설정
- 민감한 정보는 GitHub Secrets에 저장
- 모든 runner가 offline이면 작업이 대기 상태로 남음
- 로그 위치: `~/Library/Logs/actions.runner.jk-kim0-skills-jk.<runner-name>/`
