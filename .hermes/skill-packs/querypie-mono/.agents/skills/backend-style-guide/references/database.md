# Database

## Flyway 규칙

### 파일 네이밍

```
V{major}.{minor}__{release_version}_{description}.sql
```

- **major**: release 버전에 매핑 (아래 표 참조)
- **minor**: 해당 major 내 순차 번호 (0부터 시작)
- **release_version**: `11.6.1.2` 형식의 릴리스 버전
- **description**: snake_case로 변경 내용 요약

#### 스키마별 독립 버전 관리

3개 스키마가 각각 **독립적인 major 버전 체계**를 사용한다. `flyway_schema_history`도 스키마별로 별도 관리된다.

| 스키마 | 파일 경로 | 현재 major 범위 |
|--------|---------|----------------|
| App DB (`querypie`) | `db/app/migration/` | V99~V106 |
| Log DB (`querypie_log`) | `db/log/migration/` | V2~V32 |
| Snapshot DB (`querypie_snapshot`) | `db/snapshot/migration/` | V1~V5 |

#### major 버전 ↔ release 매핑 (App DB)

| Release | Major 버전 | 예시 |
|---------|-----------|------|
| 11.2.x  | 99        | `V99.0__11.2.0.0_xxx.sql` |
| 11.3.x  | 100       | `V100.0__11.3.0.0_xxx.sql` |
| 11.4.x  | 101~102   | `V101.0__11.4.0.0_xxx.sql` |
| 11.5.0  | 103       | `V103.0__11.5.1.0_xxx.sql` |
| 11.5.2  | 104       | `V104.0__11.5.2.0_xxx.sql` |
| 11.5.4  | 104       | `V104.3__11.5.4.0_xxx.sql` |
| 11.6.0  | 105       | `V105.0__11.6.0.0_xxx.sql` |
| 11.6.1  | 106       | `V106.0__11.6.1.0_xxx.sql` |

새 major 버전 배정이 필요하면 **해당 스키마의** 기존 파일 목록을 확인하여 다음 번호를 사용한다.

#### major 버전 배정 기준

- cherry-pick 대상이 확실하면 처음부터 release 버전 범위의 major를 사용
- develop에만 들어갈 것이면 다음 릴리스의 major 사용
- 버전이 불확실하면 PR 리뷰에서 확인받은 후 머지

#### minor 버전 배정

동일 major 내에서 순차적으로 배정한다. 다른 브랜치에서 동일 minor를 사용 중일 수 있으므로, develop 브랜치의 최신 상태도 확인한다.

```bash
ls apps/api/app/src/main/resources/db/app/migration/V106* | sort -V
```

### DDL과 DML 분리 (권장)

```
V1.0__10.0.0_create_user_table.sql      -- DDL (CREATE, ALTER, DROP)
V1.1__10.0.0_insert_default_users.sql   -- DML (INSERT, UPDATE, DELETE)
```

| 이유 | 설명 |
|------|------|
| **롤백 용이** | DDL은 보통 auto-commit, DML은 트랜잭션 가능 |
| **순서 관리** | 테이블 먼저 만들고 → 데이터 넣기 명확 |
| **리뷰 편의성** | 구조 변경과 데이터 변경 분리해서 보기 쉬움 |
| **실패 시 디버깅** | 어디서 실패했는지 파악 쉬움 |

**실행 구조, 환경별 설정, 트러블슈팅:** `backend-ops` 스킬 참조

---

## Log DB 마이그레이션 가이드 (11.3.0+) ⭐⭐⭐

> **이 규칙은 Log DB (`querypie_log`)에만 적용됩니다.**
> - App DB (`querypie`): 해당 없음
> - Snapshot DB (`querypie_snapshot`): 별도 권장 규칙 없음

### 배경

11.3.0부터 **무중단/순단 배포**를 공식 지원합니다.

| 기존 문제 | 해결 방법 |
|----------|----------|
| 배포 시간이 오래 걸림 | Log DB 백업이 주요 원인 |
| 롤백 대비 Log DB 백업 필요 | 스키마가 상하위 호환되면 백업 불필요 |

**핵심**: Log DB 스키마를 **상하위 호환** 가능하게 설계 → 롤백해도 **Log DB 스키마는 롤백하지 않음** → 백업 불필요 → 배포 시간 단축

### 마이그레이션 스크립트 작성 규칙

| 구분 | 작업 | 비고 |
|------|------|------|
| ✅ **허용** | 테이블 추가 | |
| ✅ **허용** | nullable 컬럼 추가 | AFTER 절 사용 비권장 |
| ✅ **허용** | enum 컬럼에 값 추가 | |
| ✅ **허용** | 색인 삭제 | 로직 변경으로 불필요해진 경우 주의 |
| ⚠️ **데이터 적은 테이블만** | 색인 추가 | |
| ⚠️ **데이터 적은 테이블만** | 컬럼값 길이 증가 | |
| ❌ **불가** | 데이터 값 변경 | |
| ❌ **불가** | not null 컬럼 추가 | default 값 있어도 불가 |
| ❌ **불가** | 컬럼 이름 변경 | |

### 데이터 많은 테이블에서 "⚠️ 작업" 해야 할 때

1. 기존 테이블 이름 변경
2. 변경된 스키마로 신규 테이블 생성
3. 백그라운드에서 기존 테이블 데이터를 신규 테이블로 복사

### 왜 이런 규칙인가? (MySQL Online DDL)

[MySQL 8.0 공식 문서](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html) 기준:

| 작업 | MySQL 8.0.29+ | MySQL 8.0.12~8.0.28 | MySQL 5.7 |
|------|---------------|---------------------|-----------|
| **ADD COLUMN (맨 뒤)** | 즉시 (INSTANT) | 즉시 (INSTANT) | Rebuild |
| **ADD COLUMN (AFTER)** | 즉시 (INSTANT) | Rebuild | Rebuild |
| **DROP COLUMN** | 즉시 (INSTANT) | Rebuild | Rebuild |
| **VARCHAR 확장** | Rebuild 없음 | Rebuild 없음 | Rebuild 없음 |

> **VARCHAR 확장 주의**: 255바이트 → 256바이트 이상으로 늘릴 때는 COPY 알고리즘 필요 (Rebuild 발생)

**Table Rebuild 발생 시**:
- 테이블 전체 복사 → 디스크 I/O 폭증
- 복사 중 메타데이터 락 → DML 지연 → 서비스 장애

> **고객 환경이 다양**하므로 (MySQL 5.7 ~ 8.x, MariaDB 등) **최악의 케이스(5.7) 기준**으로 가이드 작성

---

## 롤백 스크립트 작성 (Log DB) ⭐⭐⭐

### 왜 필요한가?

1. 새 버전에서 enum에 값 추가 (예: `NEW_TYPE`)
2. 해당 값으로 로그 쌓임
3. 서비스 롤백
4. 구버전 코드가 `NEW_TYPE`을 모름 → **로그 조회 오류!**

### 해결: 새 enum 값이 들어간 데이터만 보정

| 규칙 | 내용 |
|------|------|
| 파일 경로 | `db/log/rollback/{version}.sql` |
| 파일 단위 | 릴리즈 단위로 하나의 파일 |
| 처리 대상 | **새 enum 값이 들어간 레코드만** (하루치) |
| 처리 방법 | `DELETE` 또는 기존 값으로 `UPDATE` |

> ⚠️ **주의**: 스키마(컬럼)는 건드리지 않음!
> - ❌ `DROP COLUMN` 금지 (대용량 테이블에서 Table Rebuild → 서비스 장애)
> - ✅ 데이터만 보정

### 가이드 위반 사례

`db/log/rollback/11.5.0.sql` - **이렇게 하면 안 됨**:
- `l_connection_user_role_logs`, `l_query_running_logs` 등에 `DROP COLUMN`
- `l_workflow_logs`에 `MODIFY COLUMN` (enum 값 삭제)
- 이 테이블들은 데이터가 많아 스키마 변경 시 Table Rebuild → 서비스 장애

**롤백 스크립트는 데이터 보정(`DELETE`/`UPDATE`)만 해야 함**

---

## Collation 필수 ⭐⭐⭐

```sql
CREATE TABLE some_table (
    ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

### 왜 Collation을 명시해야 하는가?

| 문제 | 설명 |
|------|------|
| **Collation 충돌** | 테이블마다 다른 collation → JOIN 시 에러 또는 인덱스 미사용 |
| **암묵적 변환** | DB 기본값에 의존하면 환경마다 다를 수 있음 |
| **성능 저하** | collation 불일치 시 implicit conversion → 인덱스 못 탐 |

---

## 테이블/컬럼 COMMENT 필수 ⭐⭐⭐

```sql
CREATE TABLE `ai_chat_conversations` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '고유 식별자',
    `provider` VARCHAR(50) NOT NULL COMMENT 'AI Provider: querypie, litellm, claude',
    `status` ENUM('active', 'archived') NOT NULL DEFAULT 'active' COMMENT '대화 상태',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
  COMMENT='AI Chat 대화 테이블';
```

### 왜 COMMENT가 필요한가?

| 이유 | 설명 |
|------|------|
| **DBA 튜닝 지원** | 카카오 DBA님이 튜닝 시 스키마 파악에 필요 |
| **스키마 문서화** | 코드 없이 DB만 봐도 컬럼 용도 파악 가능 |
| **enum/코드값 명시** | 허용되는 값 목록을 DB 레벨에서 확인 가능 |
| **유지보수 용이** | 시간이 지나도 컬럼 의미 파악 가능 |

---

## 인덱스 네이밍

```sql
-- 컨벤션: idx_{컬럼1}_{컬럼2}_...
-- 컬럼명 내 언더스코어는 제거, 컬럼 간에는 언더스코어로 구분

CREATE INDEX idx_useruuid ON some_table (user_uuid);
CREATE INDEX idx_createdat ON some_table (created_at);
CREATE INDEX idx_useruuid_createdat ON some_table (user_uuid, created_at);
```

---

## FK (Foreign Key) 안 씀 ⭐⭐⭐

### 왜 FK를 안 쓰는가?

| 이유 | 설명 |
|------|------|
| **DDD Aggregate Root** | Aggregate 간에는 UUID 참조만, 직접 FK 연결 안 함 |
| **마이그레이션 유연성** | FK 있으면 테이블 변경/삭제 순서가 복잡해짐 |
| **성능** | FK constraint check는 write 성능에 영향 |
| **애플리케이션 레벨 무결성** | 비즈니스 로직에서 참조 무결성 관리 |

```kotlin
// ❌ FK 대신
// ✅ UUID로 참조
@Entity
class WebAppAccessControl {
    @Column(name = "user_uuid")
    var userUuid: UUID  // FK 없이 UUID만 저장

    @Column(name = "role_uuid")
    var roleUuid: UUID
}
```

---

## Aggregate Root 패턴

```
Aggregate 내부 → @OneToMany + Cascade (FK 허용)
Aggregate 간 → UUID 참조만 (FK 없음)
```

```kotlin
@Entity
class WebApp {
    // 내부 Entity는 Cascade (FK OK)
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    var tags: MutableList<WebAppTag> = mutableListOf()

    // 다른 Aggregate는 UUID만 참조 (FK 없음)
    @Column(name = "owner_uuid")
    var ownerUuid: UUID?
}
```

---

## N+1 쿼리 주의 ⭐⭐⭐⭐⭐

### 문제

JPA에서 연관 관계(OneToMany, ManyToOne)를 조회할 때 N+1 쿼리 발생

```
1. findAll() → 1 쿼리
2. 각 Entity의 연관 객체 접근 시 → N개 추가 쿼리
= 총 N+1 쿼리 💀
```

### 해결 방법

#### 1. Fetch Join (QueryDSL)

```kotlin
override fun findAllByOsTypeWithTags(osType: ServerOsType): List<Server> =
    jpaQueryFactory
        .selectFrom(server)
        .leftJoin(server.tags, serverTag)
        .fetchJoin()  // 👈 핵심!
        .where(server.osType.eq(osType))
        .fetch()
```

#### 2. LAZY 로딩 기본 설정

```kotlin
@ManyToOne(fetch = FetchType.LAZY)  // 기본으로 LAZY!
@JoinColumn(name = "cluster_uuid")
var cluster: KubeCluster
```

#### 3. @EntityGraph (JPA Repository)

```kotlin
@EntityGraph(attributePaths = ["tags", "accounts"])
fun findByUuid(uuid: UUID): Server?
```

#### 4. Batch Size 설정

```properties
spring.jpa.properties.hibernate.default_batch_fetch_size=100
```

### 규칙

1. **기본은 LAZY** - 필요할 때만 EAGER 또는 fetchJoin
2. **목록 조회 시** - QueryDSL fetchJoin 사용
3. **N+1 발생 시** - 로그에서 쿼리 개수 확인 필수
