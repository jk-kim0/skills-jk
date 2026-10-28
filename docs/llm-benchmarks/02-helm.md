# HELM: Holistic Evaluation of Language Models

HELM은 단일 데이터셋보다 넓은 의미의 평가 프레임워크이자 Benchmark 모음입니다.
Stanford CRFM(Center for Research on Foundation Models)이 표준화된 조건에서 모델의 능력과 위험을 함께 측정하도록 만들었습니다.

## 기본 정보

| 항목 | 내용 |
| --- | --- |
| 정식 명칭 | Holistic Evaluation of Language Models |
| 운영 주체 | Stanford CRFM |
| 대표 논문 | Liang et al., TMLR 2023 |
| 원 연구 구성 | 16개 핵심 시나리오, 26개 표적 시나리오, 총 42개 시나리오 |
| 핵심 지표 | 정확도, calibration, robustness, fairness, bias, toxicity, efficiency |
| 자료 | [논문](https://arxiv.org/abs/2211.09110), [공식 프레임워크](https://github.com/stanford-crfm/helm), [리더보드](https://crfm.stanford.edu/helm/) |

## 1. 소개

모델 품질을 정확도 하나로 평가하면 공정성, 유해성, 견고성, 비용 같은 운영 위험이 가려집니다.
HELM은 같은 모델에 여러 시나리오와 여러 지표를 적용해 성능의 trade-off를 한 번에 드러내는 것을 목표로 합니다.

원 연구는 30개 모델을 42개 시나리오에서 평가했고, 핵심 시나리오의 7개 지표를 가능한 경우 함께 측정했습니다.
모델·프롬프트·응답·지표를 공개해 다른 연구자가 같은 조건을 재실행하거나 원시 결과를 재분석할 수 있도록 했습니다.

HELM의 중요한 관점은 “모든 모델을 하나의 종합 점수로 정렬하지 않는다”는 것입니다.
정확도와 독성, 효율성과 공정성은 서로 다른 축이므로, 시나리오별 원시 지표와 적용 범위를 함께 확인해야 합니다.

공식 GitHub README는 2026년 6월 1일부터 프레임워크가 maintenance mode에 들어갔다고 안내합니다.
따라서 HELM은 여전히 공신력 있는 방법론과 재현 도구이지만, 최신 모델 지원 범위와 리더보드 갱신 여부를 실행 전에 확인해야 합니다.

## 2. 평가 내용

HELM의 평가 단위는 `시나리오(scenario) × 모델(model) × 지표(metric)`입니다.
시나리오는 질문응답, 요약, 분류, 대화, 편향·독성 테스트처럼 사용 사례를 뜻합니다.
지표는 정답률뿐 아니라 확률 보정, 입력 변화에 대한 견고성, 인구집단별 격차, 독성, 비용과 지연시간 등을 포함합니다.

대표적인 핵심 지표는 다음과 같습니다.

- 정확도: 정답, 문자열 일치, F1, ROUGE 등 시나리오에 맞는 성능
- Calibration: 모델의 확률과 실제 정답 빈도의 일치 정도
- Robustness: 입력 표현이나 작은 교란이 바뀌어도 성능이 유지되는지
- Fairness와 bias: 집단별 성능과 편향의 차이
- Toxicity: 유해하거나 공격적인 출력의 빈도와 강도
- Efficiency: 입력·출력 토큰, 비용, 지연시간, 처리량

현재 HELM 생태계에는 HELM Capabilities, HELM Safety, VHELM 등 목적별 리더보드가 있고, MMLU-Pro·GPQA·IFEval 같은 개별 Benchmark도 같은 프레임워크에서 실행할 수 있습니다.
이때 “HELM 점수”라는 표현은 어떤 suite와 어떤 지표를 사용했는지 없이는 의미가 부족합니다.

## 3. 평가 수행 방법

### 3.1 실행 구성

HELM은 모델 호출 어댑터, 시나리오 정의, 프롬프트 템플릿, 데이터셋, 지표 계산기를 모듈로 분리합니다.
실행자는 `run-entries`에 모델과 시나리오를 지정하고, 결과를 suite 단위로 저장한 뒤 `helm-summarize`로 요약합니다.

공식 README의 최소 실행 예시는 다음과 같은 구조입니다.

```bash
pip install crfm-helm
helm-run \
  --run-entries mmlu:subject=philosophy,model=openai/gpt2 \
  --suite my-suite \
  --max-eval-instances 10
helm-summarize --suite my-suite
```

실제 평가에서는 API 키, 모델 이름, 요청 제한, 프롬프트 버전, 최대 인스턴스 수를 고정해야 합니다.
동일 시나리오라도 모델 제공자가 바뀌거나 시스템 프롬프트가 추가되면 결과가 달라집니다.

### 3.2 권장 절차

1. 목적에 맞는 suite와 시나리오를 선택하고 사용한 HELM 버전을 기록합니다.
2. 모델 어댑터와 모델 식별자를 고정합니다.
3. few-shot 예시, temperature, 최대 출력 길이, stop 조건을 명시합니다.
4. 각 요청의 프롬프트와 응답, 오류, 지연시간, 토큰 사용량을 보존합니다.
5. 시나리오별 지표를 계산하고 누락·실패 요청을 별도로 보고합니다.
6. 평균만 합치지 말고 지표 간 trade-off와 신뢰구간을 확인합니다.
7. `helm-server` 또는 공식 리더보드에서 원시 응답과 집계값이 일치하는지 확인합니다.

### 3.3 비교 방법

HELM에서는 먼저 평가 행렬을 만듭니다.

```text
모델 A × 시나리오 1 × 정확도
모델 A × 시나리오 1 × 독성
모델 A × 시나리오 1 × 효율성
...
```

모델을 하나의 순위로 압축해야 한다면, 어떤 시나리오와 지표를 어떤 가중치로 선택했는지 공개해야 합니다.
가중치를 숨긴 종합 점수는 HELM의 다중 지표 취지와 맞지 않습니다.

## 4. 결과 해석과 한계

HELM은 가장 포괄적인 도구 중 하나지만, 모든 영역을 대표하는 완전한 표본은 아닙니다.
원 논문도 비영어권 방언, 신뢰성 지표 등 일부 영역이 과소대표된다고 명시했습니다.
시나리오가 많아질수록 API 비용과 실행 시간이 커지고, 외부 모델 API의 버전 변경이 재현성을 떨어뜨릴 수 있습니다.

효율성 비교는 같은 하드웨어·배치 크기·네트워크 조건에서 수행하지 않으면 해석이 어렵습니다.
공정성과 독성 지표는 데이터셋의 라벨 정의와 문화적 맥락의 영향을 받으므로 “절대적인 안전 점수”로 읽지 않습니다.
모델 답변을 다른 모델이 채점하는 시나리오에서는 judge 모델의 편향과 평가자 일치도도 함께 기록합니다.

HELM을 출시 전 검토에 사용한다면 다음 순서를 권장합니다.

1. 핵심 제품 시나리오를 먼저 선택합니다.
2. 정확도·품질과 안전·공정성 지표를 동시에 실행합니다.
3. 실패 응답을 원문으로 샘플링해 정성 검토합니다.
4. 비용·지연시간·rate limit을 제품 SLO와 비교합니다.
5. 모델 변경 전후의 동일 suite 결과와 실제 사용자 지표를 함께 검토합니다.

## 5. 참고 자료

- [HELM 원 논문](https://arxiv.org/abs/2211.09110)
- [Stanford CRFM HELM 저장소](https://github.com/stanford-crfm/helm)
- [HELM 공식 사이트](https://crfm.stanford.edu/helm/)
- [HELM Capabilities 리더보드](https://crfm.stanford.edu/helm/capabilities/latest/)
- [HELM Safety 리더보드](https://crfm.stanford.edu/helm/safety/latest/)
