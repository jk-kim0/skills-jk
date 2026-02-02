# Baseline SQL UUID 분석 보고서

## 프로젝트 정보

- **관련 프로젝트**: Flyway Squashed DDL (QPD-4430)
- **대상 레포지토리**: [chequer-io/querypie-mono](https://github.com/chequer-io/querypie-mono)
- **관련 PR**: [#14909 - feat(apps/api): baseline DDL/DML 추출 및 스키마 검증 모듈 구현](https://github.com/chequer-io/querypie-mono/pull/14909)
- **작업 브랜치**: `feature/baseline-module-refactoring`

## 개요

이 보고서는 `V102.15__baseline_11.5.0.sql` 파일의 INSERT 구문에서 UUID 값이 하드코딩된 부분을 원본 Migration SQL과 비교 분석한 결과입니다.

- **분석 일시**: 2026-02-02
- **Baseline 파일**: `querypie-mono/apps/api/app/src/main/resources/db/app/baseline/V102.15__baseline_11.5.0.sql`
- **원본 Migration 경로**: `querypie-mono/apps/tools/src/main/resources/db/migration/querypie/*.sql`

---

## 분석 결과 요약

| 테이블 | 원본 Migration | Baseline | 상태 | 비고 |
|--------|----------------|----------|------|------|
| admin_roles | 하드코딩 | 하드코딩 | ✅ 정상 | 빌트인 Owner Role |
| companies | 하드코딩 | 하드코딩 | ✅ 정상 | Default Company |
| proxies | 하드코딩 | 하드코딩 | ✅ 정상 | ARiSA 기본 Proxy |
| network_zones | 하드코딩 | 하드코딩 | ✅ 정상 | Default Zone |
| cluster_roles | 하드코딩 | 하드코딩 | ✅ 정상 | 기본 Cluster Roles |
| kerberos_configurations | 하드코딩 | 하드코딩 | ✅ 정상 | 기본 Kerberos Config |
| server_command_policies | 하드코딩 | 하드코딩 | ✅ 정상 | Default Policy |
| **k_proxy_setting** | **UUID()** | 하드코딩 | ❌ 수정필요 | 동적 생성 필요 |
| **oauth_apps** | **UUID()** | 하드코딩 | ❌ 수정필요 | uuid, client_secret 모두 |
| w_web_app_roles | 하드코딩 | 하드코딩 | ✅ 정상 | JIT Role |
| users | 하드코딩 | 하드코딩 | ✅ 정상 | 기본 사용자 |
| idp_settings | 하드코딩 | 하드코딩 | ✅ 정상 | 내부 IDP (db) |
| file_server_settings | UUID() | UUID() | ✅ 정상 | 후처리에서 변환됨 |

---

## 상세 분석

### 1. admin_roles ✅

**원본 Migration** (V77.12__9.18.0.12_admin_roles_built_in.sql):
```sql
insert into `admin_roles`(`uuid`, `name`, `description`, `built_in`, ...)
values ('03bc21fe-8241-11eb-a305-0a789f7c7580', 'Owner', 'QueryPie System Full Access', 1, NOW(), 1, NOW(), 1);
```

**Baseline**:
```sql
INSERT INTO `admin_roles` (`uuid`, `name`, `description`, `built_in`, ...)
VALUES ('03bc21fe-8241-11eb-a305-0a789f7c7580','Owner','QueryPie System Full Access',1,NOW(),1,NOW(),1);
```

**결론**: 빌트인 Owner Role로, 시스템 전반에서 참조되므로 하드코딩이 올바름.

---

### 2. companies ✅

**원본 Migration** (V67.11__9.10.0.11_workflow_rule_migration.sql):
```sql
INSERT INTO `companies` (`id`, `uuid`, `name`, `code`, `domain`, `path`, ...)
VALUES (1, 'c442f10a-5b8b-413f-bcbf-4abc52271e5f', 'Default', 'WLwXmAKzb', 'default', 'default', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: Default Company로, 다수의 테이블에서 FK로 참조되므로 하드코딩이 올바름.

---

### 3. proxies ✅

**원본 Migration** (V67.11):
```sql
INSERT INTO `proxies` (`id`, `uuid`, ..., `name`, ...)
VALUES (1, '04e4a8b5-5f97-11eb-9d76-0a789f7c7580', ..., 'ARiSA', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: ARiSA 기본 Proxy로, 하드코딩이 올바름.

---

### 4. network_zones ✅

**원본 Migration** (V67.11):
```sql
INSERT INTO `network_zones` (`id`, `uuid`, ..., `zone_name`, ...)
VALUES (1, 'b21abaaa-bbf2-11ed-9e22-0242ac110002', ..., 'Default', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: Default Zone으로, 하드코딩이 올바름.

---

### 5. cluster_roles ✅

**원본 Migration** (V67.11, V90.7):
```sql
-- V67.11
VALUES (1, 'ad5a17d1-bbf2-11ed-9e22-0242ac110002', ..., 'Read/Write', ...),
       (2, 'ad5a2e6a-bbf2-11ed-9e22-0242ac110002', ..., 'Read-Only', ...);

-- V90.7
values ('ee4060b7-e208-11ef-8fe7-0242ac120003', '-', 'acl only hidden cluster role', ...);
```

**Baseline**: 동일한 3개 UUID 사용

**결론**: 기본 Cluster Roles로, 하드코딩이 올바름.

---

### 6. kerberos_configurations ✅

**원본 Migration** (V67.11):
```sql
INSERT INTO `kerberos_configurations` (`id`, `uuid`, ...)
VALUES (1, 'b2c85cda-bbf2-11ed-9e22-0242ac110002', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: 기본 Kerberos Config로, 하드코딩이 올바름.

---

### 7. server_command_policies ✅

**원본 Migration** (V78.14__9.18.1.14_server_command_policy_default.sql):
```sql
insert into `server_command_policies` (`uuid`, `name`, `description`, ...)
values ('1b16baa5-e1aa-11ee-9ae5-0242ac120003', 'Default Policy', 'Default Policy', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: Default Policy로, system_settings에서 참조되므로 하드코딩이 올바름.

---

### 8. k_proxy_setting ❌ **수정 필요**

**원본 Migration** (V80.0__9.20.0.0_kac.sql):
```sql
INSERT INTO `k_proxy_setting` (`uuid`, `name`, `ca_cert`, `ca_key`, `host`, `port`, `created_at`)
VALUES (UUID(), 'default', '', '', 'customer.kac-proxy.domain', 6443, NOW());
```

**Baseline (현재 - 문제)**:
```sql
INSERT INTO `k_proxy_setting` (`uuid`, `name`, ...)
VALUES ('8ff1d8a5-ff8d-11f0-8917-a61018d9b039', 'default', ...);
```

**결론**: 원본에서 `UUID()` 함수를 사용하므로, Baseline도 `UUID()`로 변환해야 함.

---

### 9. oauth_apps ❌ **수정 필요 (보안 중요)**

**원본 Migration** (V100.9__11.3.0.9_create_oauth_apps_table.sql):
```sql
INSERT INTO `oauth_apps` (`uuid`, `name`, `client_id`, `client_secret`, ...)
    (SELECT UUID(),
            `oauth_client_id`,
            `oauth_client_id`,
            `oauth_client_secret`,
            ...
     FROM `system_settings`);
```

**Baseline (현재 - 문제)**:
```sql
INSERT INTO `oauth_apps` (`uuid`, ..., `client_secret`, ...)
VALUES ('97efb906-ff8d-11f0-8917-a61018d9b039', ..., '9722a240-ff8d-11f0-8917-a61018d9b039', ...);
```

**결론**:
- `uuid`: `UUID()` 함수로 변환 필요
- `client_secret`: **보안상 매우 중요** - `UUID()` 함수로 변환 필요. 하드코딩된 client_secret은 모든 설치 환경에서 동일하게 되어 보안 취약점 발생.

---

### 10. w_web_app_roles ✅

**원본 Migration** (V93.13__10.2.8.13_add_role_type_and_jit_role_data_to_web_app_roles.sql):
```sql
INSERT INTO `w_web_app_roles`(`uuid`, ...)
VALUES ('ffffffff-a170-4b9d-83e5-c7a92e000001', ..., 'Just In Time Role', 'JUST_IN_TIME', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: JIT Role로, 특수 UUID 패턴(`ffffffff-...`) 사용. 하드코딩이 올바름.

---

### 11. users ✅

**원본 Migration** (V67.11):
```sql
INSERT INTO `users` (`id`, `uuid`, ..., `login_id`, ...)
VALUES (1, 'd5e3a9e5-8080-11eb-a305-0a789f7c7580', ..., 'system', ...),
       (2, 'd8665fba-8080-11eb-a305-0a789f7c7580', ..., 'qp-admin', ...);
```

**Baseline**: 동일한 UUID 사용

**결론**: 기본 사용자(system, qp-admin)로, user_roles, user_password_history 등에서 참조되므로 하드코딩이 올바름.

---

### 12. idp_settings ✅

**원본 Migration** (V100.13__11.3.0.13_idp_settings.sql):
```sql
-- 기존 데이터 마이그레이션 시 UUID() 사용
SELECT UUID(), ... FROM `system_settings`;

-- 이후 내부 IDP는 고정 UUID로 UPDATE
UPDATE idp_settings SET uuid = 'e01c80db-879c-11f0-9e57-66773bd8c9b7' WHERE provider='db';

-- 또는 신규 설치 시 고정 UUID로 INSERT
INSERT INTO idp_settings(...)
SELECT 'e01c80db-879c-11f0-9e57-66773bd8c9b7', 'db', 'internal-idp', ...
```

**Baseline**: `'e01c80db-879c-11f0-9e57-66773bd8c9b7'` 사용

**결론**: 내부 IDP(db)는 명시적으로 고정 UUID가 지정되어 있으므로 하드코딩이 올바름.

---

### 13. file_server_settings ✅

**원본 Migration** (V81.20__10.0.0.20_rdp.sql):
```sql
insert into `file_server_settings` (`uuid`, `secret_key`, `created_at`)
value (UUID(), 'asdfqwerzxcvghjkvbnmtyuighjkdfghwertsdfgpoui', NOW());
```

**Baseline (before_postprocess)**: 하드코딩 UUID
**Baseline (after_postprocess)**: `UUID()` 함수 사용

**결론**: 후처리 스크립트에서 이미 올바르게 변환되고 있음.

---

## 필요한 조치 사항

### 후처리 스크립트 수정 필요

`querypie-mono/apps/api/app/script/baseline/postprocess.py`에 다음 테이블의 UUID 변환 로직 추가:

1. **k_proxy_setting**
   - `uuid` 컬럼 → `UUID()` 함수로 변환

2. **oauth_apps** (보안상 매우 중요)
   - `uuid` 컬럼 → `UUID()` 함수로 변환
   - `client_secret` 컬럼 → `UUID()` 함수로 변환

### 예상 수정 코드

```python
# postprocess.py에 추가할 테이블 목록
UUID_TABLES = [
    'file_server_settings',  # 기존
    'k_proxy_setting',       # 추가
    'oauth_apps',            # 추가 (uuid, client_secret 모두)
]
```

---

## 결론

총 13개 테이블 중 **2개 테이블에서 문제 발견**:

- `k_proxy_setting`: UUID 동적 생성 필요
- `oauth_apps`: UUID 및 client_secret 동적 생성 필요 (보안 취약점)

나머지 11개 테이블은 원본 Migration과 일치하여 정상적으로 하드코딩된 상태입니다.
