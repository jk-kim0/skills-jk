---
id: querypie-docs-mdx-to-storage-xhtml-cli
title: QueryPie Docs MDX -> Confluence Storage XHTML CLI
status: active
repos:
  - https://github.com/querypie/querypie-docs
created: 2026-02-15
updated: 2026-02-16
---

# QueryPie Docs MDX -> Confluence Storage XHTML CLI

## 목표 (변경)

기존 목표(의미 동등성, 정규화 비교)를 폐기하고, 다음 목표로 전환한다.

- **원문 `page.xhtml`를 바이트 단위로 복원**한다.
- 사소한 노드/속성/공백 차이도 허용하지 않는다.
- `MDX -> XHTML` 결과가 원문 `page.xhtml`와 `byte-equal`이어야 한다.

즉, 이 프로젝트는 "유사 XHTML 생성기"가 아니라 **lossless roundtrip 복원기**다.

## 왜 기존 접근으로는 실패하는가

현재 구조(`line-based parser + emitter + verify normalize`)는 다음 한계를 갖는다.

1. Forward 단계에서 정보 손실 발생 (`#link-error`, `ac:emoticon`, `ac:adf-extension`, filename 정규화 등)
2. 역변환이 "추론 기반 재생성"이므로 원문 문자열을 1:1 복제할 수 없음
3. 일반 XML/HTML serializer가 공백/속성순서/self-closing 표기를 바꿈
4. verify가 정규화 중심이라 "정확 복원" 설계 압박을 약화시킴

결론: **복원에 필요한 원본 정보를 forward 단계에서 보존**하지 않으면 목표 달성 불가.

## 설계 원칙

1. Lossless by default: 원본 정보를 절대 버리지 않는다.
2. Source of truth 분리: 의미 표현(MDX)과 복원 메타(sidecar)를 함께 유지한다.
3. Deterministic rendering: serializer가 원문 토큰/표현을 보존한다.
4. Byte-equal gate: 최종 품질지표는 pass율이 아니라 byte-equal 비율이다.

## 새 아키텍처 (Lossless Roundtrip)

```
Confluence XHTML (source)
  ├─ A. Forward convert -> expected.mdx
  └─ B. Sidecar extract -> expected.roundtrip.json

expected.mdx + expected.roundtrip.json
  -> MDX to XHTML restore pipeline
     1) parse mdx -> blocks (+ stable block_id)
     2) compare with sidecar fingerprints
     3) unchanged block = raw xhtml splice
     4) changed block = deterministic re-render
     5) token-preserving document stitch

output.xhtml == page.xhtml (byte-equal)
```

### 핵심 컴포넌트

- `roundtrip_sidecar.py` (신규)
  - 원문 XHTML의 블록 경계, raw fragment, 링크/매크로 원본, 속성 순서/표기 보존
- `block_identity.py` (신규)
  - forward/reverse 양방향에서 안정적인 `block_id` 생성
- `rehydrator.py` (신규)
  - sidecar를 이용해 unchanged 블록 raw 복원, changed 블록만 렌더링
- `token_preserving_serializer.py` (신규)
  - `<br/>` vs `<br />`, attribute order, whitespace, CDATA 표기 보존
- `byte_verify_cli.py` (신규 또는 기존 확장)
  - `byte-equal` 검증을 기본 모드로 강제

## 데이터 계약 (Roundtrip Sidecar v1)

`expected.roundtrip.json` 예시 필드:

- `page_id`
- `source_sha256`
- `blocks[]`
  - `block_id`
  - `kind` (`paragraph`, `list`, `macro`, `table`, ...)
  - `raw_xhtml`
  - `raw_span` (offset begin/end)
  - `semantic_fingerprint`
  - `link_metadata[]` (`ri:content-title`, `ri:space-key`, `ac:anchor`, original href)
  - `macro_metadata` (`ac:adf-extension` payload 포함)
  - `attachment_metadata` (원본 filename/ids)
- `document_tokens`
  - 문서 단위 접합 시 필요한 토큰(개행/indent/prefix/suffix)

## 구현 단계

### Phase L1 — 계약/인프라 (필수)

#### Task L1.1: Roundtrip Sidecar 스키마 확정
- [ ] `expected.roundtrip.json` 스키마 정의
- [ ] 스키마 버전(`roundtrip_schema_version`) 도입
- [ ] fixture 3건에 샘플 sidecar 생성

#### Task L1.2: Forward sidecar 생성기 구현
- [ ] forward 변환 시 sidecar 동시 생성
- [ ] link/macro/attachment 원본 정보 저장
- [ ] 기존 CLI에 `--write-sidecar` 옵션 추가

#### Task L1.3: Stable block_id 설계
- [ ] 블록 경계 규칙 정의
- [ ] block_id 생성 알고리즘 구현
- [ ] forward/reverse 일치 테스트

### Phase L2 — 복원 파이프라인

#### Task L2.1: Rehydrator 구현
- [ ] unchanged 블록 raw splice
- [ ] changed 블록 fallback renderer
- [ ] hybrid 문서 조립

#### Task L2.2: Token-preserving serializer 구현
- [ ] self-closing 표기 보존
- [ ] attribute 순서 보존
- [ ] whitespace/line-break 보존
- [ ] CDATA 경계 보존

#### Task L2.3: 비가역 케이스 복원
- [ ] `#link-error`를 sidecar 기반으로 원복
- [ ] `ac:adf-extension` raw payload 원복
- [ ] `ac:emoticon`, `ri:filename` 원복

### Phase L3 — 검증 체계 전환

#### Task L3.1: Byte verify를 기본 게이트로 전환
- [ ] `verify` 기본 모드를 byte-equal로 변경
- [ ] 실패 시 semantic diff는 보조 출력만 제공

#### Task L3.2: 회귀 테스트 재정의
- [ ] testcase 21건 전체 byte-equal snapshot 추가
- [ ] CI 실패 기준을 byte-equal mismatch로 고정

#### Task L3.3: 성능/안정성 보강
- [ ] 대용량 문서 복원 시간 측정
- [ ] sidecar schema migration 전략 수립

## 완료 기준 (DoD)

1. `tests/testcases/*` 대상 `MDX + sidecar -> XHTML` 결과가 원문과 byte-equal
2. known exception 없음 (임시 예외 허용 금지)
3. sidecar 없는 입력에 대해선 명시적으로 "lossless 미보장" 경고 출력
4. CI에서 byte-equal gate 통과

## 테스트 전략

### 필수 테스트

- `test_roundtrip_sidecar_schema.py`
- `test_block_identity_stability.py`
- `test_rehydrator_raw_splice.py`
- `test_token_preserving_serializer.py`
- `test_lossless_roundtrip_e2e.py` (21 fixtures)

### 실패 분석 출력

byte mismatch 시 최소 정보 출력:

- 최초 mismatch byte offset
- 주변 200-byte context
- block_id 매핑 정보

## 리스크와 대응

1. Sidecar 크기 증가
- 대응: gzip 저장 옵션 + CI artifact 분리

2. Block 경계 변경 시 기존 sidecar 무효화
- 대응: schema version + migration tool

3. serializer 구현 난이도
- 대응: full rewrite 대신 토큰 스트림 기반 최소 구현부터 시작

4. 기존 파이프라인과의 충돌
- 대응: `--mode semantic`(기존), `--mode lossless`(신규) 병행 후 점진 전환

## 운영 정책 변경

- 기존 "pass/fail + reason 통계"는 보조 지표로 강등
- 핵심 KPI를 다음으로 교체:
  - `byte_equal_pass_count / total`
  - `unchanged_block_raw_splice_ratio`
  - `fallback_rendered_block_ratio`

## 다음 액션 (즉시)

- [ ] L1.1 sidecar 스키마 초안 작성
- [ ] L1.2 forward sidecar 생성 PoC 구현
- [ ] testcase 3건(`lists`, `panels`, `544211126`)에 대해 byte-equal 복원 실험
- [ ] 프로젝트 문서/PR 템플릿에 "lossless gate" 반영
