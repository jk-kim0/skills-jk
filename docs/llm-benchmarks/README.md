# LLM Benchmark 평가 Reference

이 문서는 AI 모델과 대규모 언어 모델(LLM)을 평가할 때 자주 인용되는 Benchmark 10개를 공신력과 재현성 기준으로 정리한 참고 자료입니다.
조사 기준일은 2026-10-26입니다.
각 Benchmark의 원 논문, 공식 저장소, 공식 리더보드를 우선 확인했습니다.

## 이 목록을 읽는 방법

‘상위 10개’는 단일 기관이 발표한 공식 순위가 아닙니다.
Benchmark마다 측정 대상, 데이터 공개 수준, 평가 비용, 최신성, 오염 위험이 다르므로 하나의 점수로 서열화할 수 없습니다.
이 문서의 순서는 다음 네 가지 기준을 함께 적용한 편집 순서입니다.

| 기준 | 비중 | 판단 기준 |
| --- | ---: | --- |
| 공신력 | 30% | 학술대회·대학·연구기관·공개 연구 커뮤니티가 운영하거나 원 논문과 유지보수 주체가 명확한가 |
| 재현성 | 25% | 데이터, 평가 코드, 프롬프트, 채점 규칙, 버전 정보가 공개되어 동일한 실험을 반복할 수 있는가 |
| 영향력 | 25% | 연구 논문과 모델 카드, 공개 리더보드에서 반복적으로 사용되는가 |
| 범위와 실무 가치 | 20% | 일반 능력, 추론, 코드, 사실성, 인간 선호 등 실제 의사결정에 필요한 능력을 얼마나 잘 보완하는가 |

따라서 순위는 “모델 성능 순위”가 아니라 “평가 자산으로서의 신뢰와 활용 가치” 순위입니다.
모델을 하나의 숫자로 비교하려면 이 목록에서 목적에 맞는 여러 Benchmark를 골라 함께 보고해야 합니다.

## 공신력 기준 상위 10개 요약

| 순위 | Benchmark | 운영·발표 주체 | 주로 측정하는 것 | 대표 지표 | 상세 문서 |
| ---: | --- | --- | --- | --- | --- |
| 1 | MMLU | Hendrycks 연구팀, ICLR 2021 | 57개 학문·전문 분야의 지식과 문제 해결 | 4지선다 정확도 | [MMLU](01-mmlu.md) |
| 2 | HELM | Stanford CRFM | 시나리오별 능력, 안전성, 공정성, 효율성의 종합 평가 | 시나리오×다중 지표 | [HELM](02-helm.md) |
| 3 | BIG-bench | Google과 132개 기관의 공동 연구자 | 200개 이상 과제의 광범위한 능력 탐색 | 과제별 정확도·생성·사용자 정의 지표 | [BIG-bench](03-big-bench.md) |
| 4 | Chatbot Arena (LMArena) | LMSYS·Arena 운영팀 | 실제 사용자가 느끼는 모델 간 선호 | Bradley–Terry 기반 평점과 승률 | [Chatbot Arena](04-chatbot-arena.md) |
| 5 | HumanEval | OpenAI | Python 코드 생성의 기능적 정확성 | pass@k | [HumanEval](05-humaneval.md) |
| 6 | GSM8K | OpenAI 연구팀 | 초등학교 수준의 다단계 수학 문장제 | 최종 답 정확도 | [GSM8K](06-gsm8k.md) |
| 7 | MATH | Hendrycks 연구팀, NeurIPS 2021 | 경시대회 수준의 수학 문제 해결 | 정답 일치율 | [MATH](07-math.md) |
| 8 | GPQA | Rein et al., COLM 2024 | 생물·물리·화학의 대학원 수준 전문 추론 | 4지선다 정확도 | [GPQA](08-gpqa.md) |
| 9 | TruthfulQA | Lin, Hilton, Evans, ACL 2022 | 잘못된 통념을 반복하지 않는 사실성 | truthfulness·informativeness·MC1/MC2 | [TruthfulQA](09-truthfulqa.md) |
| 10 | HellaSwag | Zellers et al., ACL 2019 | 상식적 문장 완성과 사건의 자연스러운 다음 단계 | 4지선다 정확도 | [HellaSwag](10-hellaswag.md) |

## 목적별 선택 가이드

| 평가 목적 | 우선 선택 | 함께 보면 좋은 Benchmark | 이유 |
| --- | --- | --- | --- |
| 범용 지식과 학술 능력 | MMLU | HELM, BIG-bench | 과목별 편차와 다중 지표를 함께 볼 수 있습니다. |
| 모델의 실제 대화 선호 | Chatbot Arena | HELM | 사용자 선호와 통제된 정적 평가를 분리해 볼 수 있습니다. |
| 코드 생성 | HumanEval | HELM의 코드 시나리오 | 텍스트 유사도가 아니라 테스트 실행 결과를 봅니다. |
| 간단한 수학 추론 | GSM8K | MATH | 산술 중심 문제와 경시대회 수준 문제를 구분합니다. |
| 고난도 과학 지식 | GPQA | MMLU의 전문 과목 | 전문가 검증 문항과 일반 전문 과목 문항을 비교합니다. |
| 사실성·환각 위험 | TruthfulQA | HELM Safety | 진실성 점수와 유해성·편향 지표를 분리합니다. |
| 상식적 사건 이해 | HellaSwag | BIG-bench의 상식 과제 | 문맥상 자연스러운 다음 사건을 고르는 능력을 봅니다. |
| 종합적인 모델 출시 검토 | HELM | MMLU, HumanEval, GSM8K, TruthfulQA, Chatbot Arena | 능력·안전·효율·실사용 선호를 한 프레임에서 관리합니다. |

## 공통 평가 프로토콜

Benchmark 이름만 같아도 평가 설정이 달라지면 결과를 직접 비교할 수 없습니다.
최소한 다음 항목을 모델 결과와 함께 기록해야 합니다.

1. 데이터셋과 코드의 버전, 커밋 SHA 또는 릴리스 날짜를 고정합니다.
2. zero-shot, few-shot, chain-of-thought 여부와 예시 순서를 기록합니다.
3. temperature, top-p, 최대 출력 토큰, stop sequence, seed를 기록합니다.
4. 도구 사용, 검색, 계산기, 코드 실행, 외부 문서 접근을 명시합니다.
5. 채점 전처리와 정답 추출 규칙을 공개합니다.
6. 단일 평균뿐 아니라 과목·난이도·언어·카테고리별 점수를 함께 보고합니다.
7. 반복 샘플링을 사용하면 평균, 표준오차 또는 신뢰구간, 샘플 수를 보고합니다.
8. 평가 비용, 지연시간, 실패율, rate limit, 컨텍스트 길이도 운영 지표로 남깁니다.
9. 학습 데이터와 Benchmark 사이의 중복 가능성과 공개 테스트셋 오염 여부를 확인합니다.
10. 모델 버전, 시스템 프롬프트, 추론 서버 설정을 결과와 함께 보존합니다.

## 점수 해석 시 주의할 점

높은 점수가 일반적인 지능이나 실제 제품 품질을 보장하지는 않습니다.
정적 객관식 Benchmark는 프롬프트 형식과 데이터 오염에 민감합니다.
생성형 Benchmark는 채점기와 정답 추출기의 편향을 함께 가집니다.
인간 선호 Benchmark는 사용자 집단, 언어, 질문 분포, 모델 노출 방식의 영향을 받습니다.
작은 데이터셋은 점수 차이가 커 보여도 통계적으로 유의하지 않을 수 있습니다.
Benchmark가 포화되면 최신 모델 간 차이를 구분하지 못하므로 새 버전이나 보완 Benchmark를 병행해야 합니다.

## 상세 문서 목록

- [01. MMLU](01-mmlu.md)
- [02. HELM](02-helm.md)
- [03. BIG-bench](03-big-bench.md)
- [04. Chatbot Arena (LMArena)](04-chatbot-arena.md)
- [05. HumanEval](05-humaneval.md)
- [06. GSM8K](06-gsm8k.md)
- [07. MATH](07-math.md)
- [08. GPQA](08-gpqa.md)
- [09. TruthfulQA](09-truthfulqa.md)
- [10. HellaSwag](10-hellaswag.md)

## 기본 참고 자료

- [MMLU 논문](https://arxiv.org/abs/2009.03300)
- [HELM 논문](https://arxiv.org/abs/2211.09110)
- [BIG-bench 논문](https://arxiv.org/abs/2206.04615)
- [Chatbot Arena 논문](https://arxiv.org/abs/2403.04132)
- [HumanEval 논문](https://arxiv.org/abs/2107.03374)
- [GSM8K 논문](https://arxiv.org/abs/2110.14168)
- [MATH 논문](https://arxiv.org/abs/2103.03874)
- [GPQA 논문](https://arxiv.org/abs/2311.12022)
- [TruthfulQA 논문](https://arxiv.org/abs/2109.07958)
- [HellaSwag 논문](https://arxiv.org/abs/1905.07830)
