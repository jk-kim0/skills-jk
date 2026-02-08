---
id: go-client-completeness
title: QueryPie Go Client 완성도 개선
status: active
repos:
  - https://github.com/chequer-io/querypie-go-client
  - https://github.com/chequer-io/querypie-mono (addons/go-client)
created: 2026-02-08
---

# QueryPie Go Client 완성도 개선

## 목표

QueryPie Client for Operation (`qpc`) CLI 도구의 기능 완성도를 높여, 실무 운영 자동화에 활용할 수 있는 수준으로 발전시킨다.

## 배경

### 현재 상태 (v0.1)

`qpc`는 Go로 작성된 QueryPie 운영용 CLI 클라이언트로, 현재 DAC Access Control의 Grant 기능을 중심으로 구현되어 있다.

**구현 완료된 기능:**
- User fetch/ls (API v2)
- DAC Connection fetch/ls (상세 및 요약)
- DAC Privilege fetch/ls
- DAC Access Control fetch/ls
- DAC Grant (user + privilege + cluster/connection)
- DAC Cluster ls
- DAC Policy CRUD (DATA_LEVEL, DATA_ACCESS, DATA_MASKING, NOTIFICATION)
- DAC Sensitive Data Rule fetch/ls
- Config (서버 연결 확인)

**미구현 기능 (COMMANDS.md 기준):**
- User CRUD (upsert, activate, deactivate, delete, reset-password, describe)
- DAC Connection 생성
- Table-level 접근 권한 부여
- Sensitive Data 설정 적용
- Ledger Policy 적용
- SAC (Server Access Control) 전체

### 기술 스택

| 구성 | 기술 |
|------|------|
| 언어 | Go 1.24 |
| CLI 프레임워크 | cobra + viper |
| HTTP 클라이언트 | go-resty/resty/v2 |
| 로컬 DB | SQLite3 (gorm) |
| 바이너리 이름 | `qpc` |

### 아키텍처

```
cmd/           CLI 명령 정의 (cobra commands)
entity/        도메인 모델 + DB/API 연동
  dac_access_control/   접근 권한 부여
  dac_connection/       DB Connection 관리 (v1, v2)
  dac_privilege/        Privilege 관리
  dac_policy/           정책 관리
  dac_sdr/              Sensitive Data Rule
  user/                 사용자 관리 (v1, v2)
model/         공통 데이터 구조
config/        YAML 설정 처리
utils/         HTTP 추상화, 유틸리티
t/             통합 테스트 (shell script)
```

## 범위

### Phase 1: User Management 완성

User 리소스에 대한 CRUD 기능을 완성한다.

| 명령어 | 설명 | API |
|--------|------|-----|
| `qpc user describe <user>` | 사용자 상세 정보 조회 | local DB 조회 |
| `qpc user upsert <loginid>` | 사용자 생성/수정 | API v2 POST/PUT |
| `qpc user activate <user>` | 사용자 활성화 | API v2 PUT |
| `qpc user deactivate <user>` | 사용자 비활성화 | API v2 PUT |
| `qpc user delete <user>` | 사용자 삭제 | API v2 DELETE |
| `qpc user reset-password <user>` | 비밀번호 초기화 | API v2 POST |

### Phase 2: DAC 기능 확장

DAC 관련 미구현 기능을 추가한다.

| 명령어 | 설명 |
|--------|------|
| DAC Connection 생성 | CLI에서 DB Connection 생성 |
| Table-level 접근 권한 부여 | 테이블 단위 ACL 설정 |
| Sensitive Data 설정 적용 | Connection/table에 민감 데이터 규칙 적용 |
| Ledger Policy 적용 | Ledger 정책 연동 |

### Phase 3: SAC (Server Access Control)

서버 접근 제어 기능을 신규 구현한다.

| 명령어 | 설명 |
|--------|------|
| `qpc sac fetch-all` | 서버 목록 내려받기 |
| `qpc sac fetch <name>` | 특정 서버 정보 조회 |
| `qpc sac upsert <name>` | 서버 생성/수정 |
| `qpc sac delete <name>` | 서버 삭제 |
| `qpc sac describe <name>` | 서버 상세 정보 |
| `qpc sac upsert-server-group` | 서버 그룹 관리 (태그 기반) |

### Phase 4: 품질 및 배포

| 항목 | 설명 |
|------|------|
| 테스트 체계 개선 | shell script → Go 테스트로 전환 |
| CI/CD | GitHub Actions 빌드/릴리즈 파이프라인 |
| 문서화 | 명령어별 상세 사용법, 예제 |
| 에러 처리 개선 | 일관된 에러 메시지, exit code |

## 현재 구현 현황

### 구현 완료 (COMMANDS.md 기준)

- [x] `qpc user fetch` - 서버에서 사용자 정보 내려받기
- [x] `qpc user ls` - 로컬 DB 사용자 목록 조회
- [x] `qpc dac connection fetch` - Connection 정보 내려받기
- [x] `qpc dac connection ls` - Connection 목록 조회
- [x] `qpc dac privilege fetch` - Privilege 정보 내려받기
- [x] `qpc dac privilege ls` - Privilege 목록 조회
- [x] `qpc dac access-control fetch` - Access Control 정보 내려받기
- [x] `qpc dac access-control ls` - Access Control 목록 조회
- [x] `qpc dac cluster ls` - Cluster 목록 조회
- [x] `qpc dac grant` - 접근 권한 부여
- [x] `qpc dac fetch-by-uuid` - UUID로 리소스 조회 (디버그)
- [x] `qpc dac find-by-uuid` - UUID로 로컬 DB 조회 (디버그)
- [x] `qpc config querypie` - 서버 연결 확인

### COMMANDS.md 외 추가 구현

- [x] `qpc dac policy fetch` - 정책 내려받기
- [x] `qpc dac policy ls` - 정책 목록 조회
- [x] `qpc dac policy upsert` - 정책 생성/수정
- [x] `qpc dac policy delete` - 정책 삭제
- [x] `qpc dac sensitive-data-rule fetch` - 민감 데이터 규칙 내려받기
- [x] `qpc dac sensitive-data-rule ls` - 민감 데이터 규칙 조회

### 미구현

- [ ] User CRUD (upsert, activate, deactivate, delete, reset-password, describe)
- [ ] DAC Connection 생성
- [ ] Table-level 접근 권한 부여
- [ ] Sensitive Data 설정 적용
- [ ] Ledger Policy 적용
- [ ] SAC 전체 (fetch, upsert, delete, describe, server-group)

## 마일스톤

### Phase 1: User Management (목표: 2026 Q1)
- [ ] user describe 구현
- [ ] user upsert 구현
- [ ] user activate/deactivate 구현
- [ ] user delete 구현
- [ ] user reset-password 구현
- [ ] 통합 테스트 작성

### Phase 2: DAC 확장 (목표: 2026 Q2)
- [ ] DAC Connection 생성 기능
- [ ] Table-level 접근 권한 부여
- [ ] Sensitive Data 설정 적용
- [ ] Ledger Policy 적용

### Phase 3: SAC (목표: 2026 Q2-Q3)
- [ ] SAC entity/model 설계
- [ ] SAC fetch/ls 구현
- [ ] SAC upsert/delete 구현
- [ ] Server Group 관리 기능

### Phase 4: 품질 (ongoing)
- [ ] Go 테스트 프레임워크 도입
- [ ] CI/CD 파이프라인 구축
- [ ] 명령어 문서 자동 생성

## 메모

- 공개 저장소: https://github.com/chequer-io/querypie-go-client
- 개발은 `querypie-mono/addons/go-client`에서 진행, 공개 저장소에 sync
- API v0.9 (legacy)와 v2 혼용 중 — 신규 기능은 v2 API 우선 사용
- 코드 내 TODO: `dac_access_control.go:58` — 상세 access control fetch 미완성
