---
name: backend-ops
description: 백엔드 운영 지식 가이드. 마이그레이션 실행 구조, 환경별 설정 차이, 트러블슈팅 절차, 사고 사례 등.
---

# Backend Operations Guide

## 마이그레이션 실행 구조

마이그레이션은 API 서버가 아니라 **tools 컴포넌트**(`apps/tools`)가 담당한다.

- 마이그레이션 스크립트 위치: `apps/api/app/src/main/resources/db/`
- 실행 스크립트: `apps/tools/script/migrate.sh`
- 로컬 실행: `cd tools/bambi && make migrate-db`

### outOfOrder 설정

`migrate.sh`는 `-o` 플래그로 `outOfOrder` 모드를 선택할 수 있다.

| 환경 | 스크립트 | outOfOrder |
|------|---------|------------|
| 운영 배포 (`deploy/operation/setup.v2.sh`, `upgrade.sh`) | `migrate.sh runall` | **false** |
| 로컬 개발 (`deploy/local/up.sh`, `tools/bambi`) | `migrate.sh runall -o` | **true** |

- `outOfOrder=false`: 이미 적용된 버전보다 낮은 버전의 마이그레이션은 실행되지 않음 (단, tools의 `validateOnMigrate=false` 설정으로 검증 에러는 발생하지 않고 조용히 스킵됨)
- `outOfOrder=true`: 낮은 버전도 실행 시도됨

---

## 적용된 마이그레이션 변경 시 주의

Flyway는 `flyway_schema_history` 테이블에서 **버전 + checksum**으로 이력을 관리한다. 적용된 마이그레이션의 파일명/내용/존재 여부를 변경하면 히스토리와 불일치가 발생한다.

| 변경 유형 | 결과 |
|----------|------|
| 파일명(버전) 변경 | 히스토리 불일치 + out-of-order 실행 시도 → 실패 레코드(success=0)로 이후 마이그레이션 전체 블로킹 |
| SQL 내용 변경 | checksum 불일치 → 서버 시작 실패 |
| 파일 삭제 | 히스토리 검증 실패 |

### 변경이 필요한 경우의 대응 절차

잘못된 버전으로 머지되었거나, release 체리픽을 위해 버전을 변경해야 하는 경우가 있을 수 있다. 이때 **파일만 변경하고 히스토리를 방치하면 장애가 발생**한다.

1. **어떤 환경에 적용되었는지 확인**
   ```sql
   SELECT version, description, installed_on, success
   FROM flyway_schema_history WHERE version = '106.2';
   ```

2. **파일명 변경 (코드)**

3. **적용된 환경의 히스토리 정리 (필수)**
   ```sql
   -- 기존 버전 레코드 삭제
   DELETE FROM flyway_schema_history WHERE version = '106.2';
   -- 실패 레코드가 있다면 함께 삭제
   DELETE FROM flyway_schema_history WHERE version = '104.3' AND success = 0;
   ```

4. **tools 컴포넌트로 마이그레이션 재실행**하여 새 버전이 정상 적용되도록 한다

5. **적용 대상 환경 목록 (확인 필요)**
   - develop (`develop.ec2.querypie.io`)
   - nightly (`nightly.ec2.querypie.io`)
   - staging (해당 시)

---

## 사고 사례

### 2026-03-09: 버전 rename으로 인한 nightly 마이그레이션 전면 중단

**경과:**
1. PR #15145 (3/5): KAC GCP 마이그레이션이 `V106.2`, `V106.3`으로 develop에 머지 → DB에 적용됨
2. PR #15480 (3/5): forward proxy 인증 마이그레이션이 `V106.4`로 develop에 머지
3. PR #15491 (3/6): release 체리픽을 위해 `V106.2→V104.3`, `V106.3→V104.4`, `V106.4→V104.5`로 rename
4. PR #15565 (3/9): forward proxy 마이그레이션 버전을 `V106.4→V106.2`로 재배정
5. V104.3이 out-of-order로 실행 시도 → 실패(success=0) 기록
6. 실패 레코드로 인해 이후 마이그레이션 전부 블로킹 → API 500 에러

**근본 원인:** 파일명을 변경하면서 환경의 `flyway_schema_history` 레코드를 정리하지 않은 것

**교훈:** 마이그레이션 파일 변경 시 반드시 적용된 환경의 히스토리도 함께 정리해야 한다
