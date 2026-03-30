# PR 리뷰 기준

## 심각도 등급

| 등급 | 설명 |
|------|------|
| `critical` | 정확성 버그, 보안 취약점, 데이터 손실 위험. 병합 전 반드시 수정 |
| `warning` | 신뢰성, 성능, 유지보수성 위험. 해결 권장 |
| `suggestion` | 코드 개선 기회. 차단 사유 아님 |

---

## 표준 종류(Canonical-Kind) 어휘

| # | canonical-kind | 설명 |
|---|---|---|
| 1 | `missing_validation` | 입력값 검증 누락 |
| 2 | `missing_error_handling` | 에러 처리 누락 |
| 3 | `unbounded_loop` | 종료 조건 없는 루프/재시도 |
| 4 | `wrong_target_ref` | 잘못된 참조 대상 |
| 5 | `stale_state_transition` | 잘못된 상태 전이 순서 |
| 6 | `unused_variable` | 선언 후 미사용 변수/필드 |
| 7 | `hardcoded_value` | 하드코딩된 값 |
| 8 | `duplicate_logic` | 중복 코드/로직 |
| 9 | `security_injection` | SQL/command/XSS 등 인젝션 취약점 |
| 10 | `race_condition` | 동시성 문제 |
| 11 | `resource_leak` | 파일/연결 등 리소스 미해제 |
| 12 | `wrong_scope` | 과도하거나 부족한 접근 범위 |
| 13 | `incorrect_algorithm` | 로직/알고리즘 오류 |
| 14 | `missing_test` | 테스트 누락 |
| 15 | `doc_mismatch` | 문서와 구현 불일치 |

**폴백** (위 항목에 해당하지 않을 때):
`criterion:<N>|file:<path>|anchor:<anchor>|msg:<sha1(normalize(message))[:12]>`

참고: `issue_key` 생성은 오케스트레이터가 담당한다. Agent는 아래 형식의 원시 findings만 출력한다.

---

## 실행 가능한 Finding의 조건

- 구체적이고 명확해야 함 (파일 + 라인 참조 필수)
- PR 범위 내에서 수정 가능해야 함
- PR이 도입하거나 수정한 코드와 관련되어야 함 (기존 문제 제외)
- 스타일 선호나 주관적 의견이 아니어야 함

---

## 건너뛸 항목

- 스타일 지적 (포맷, 네이밍 선호) — 혼동을 유발하지 않는 한
- 이 PR이 도입하지 않은 기존 문제
- 구체적 영향 없는 주관적 아키텍처 의견
- 이전 라운드에서 이미 제기된 issue (중복 제거는 오케스트레이터가 처리)

---

## 원시 보고 출력 형식

Agent는 아래 스키마의 JSON 배열을 출력해야 한다:

```json
[
  {
    "severity": "critical|warning|suggestion",
    "criterion": 1,
    "file": "src/foo.ts",
    "line": 42,
    "anchor": "validate_input",
    "message": "이슈 설명과 중요한 이유"
  }
]
```

- `criterion`: 리뷰 기준 번호. 해당 시 표준 종류 인덱스(1-15) 사용, 아니면 폴백 번호.
- `file`: 저장소 상대 경로
- `line`: 현재 PR diff 기준 라인 번호
- `anchor`: 심볼명, 함수명 등 라인 이동에 덜 민감한 식별자. 없으면 `line<N>` 형식.
- `message`: 무엇이 잘못되었고 왜 문제인지 명확히 설명

---

## 리뷰 범위

- PR diff에만 집중
- 맥락 파악을 위해 주변 코드를 읽되, 변경/추가된 라인의 문제만 보고
- PR 제목과 설명에서 의도를 파악
