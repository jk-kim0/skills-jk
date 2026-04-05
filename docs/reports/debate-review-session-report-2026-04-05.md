# Debate Review Session Report

- Generated at: 2026-04-05T10:07:14.745754+00:00
- Sessions: 66
- Completed: 62
- In progress: 4

## Findings

- **Excluded Population**: session 통계에서는 dry-run 3개, in-progress 4개를 제외했습니다. round 통계에서는 completed_at 누락 254개를 제외했습니다.
- **Step-Level Coverage**: 통계 대상 completed round 69개 중 step 정보가 있는 round는 55개, agent breakdown이 있는 round는 45개입니다.
- **Slowest Median Step**: step2_cross_review의 median은 148.5초로, 집계된 step 중 가장 깁니다.
- **Cross-Reviewer Split**: step2_cross_review median은 CC 4294.9초, Codex 82.4초로 cross-review 분포가 agent별로 크게 갈립니다.
- **Lead Agent Comparison**: Lead round median은 CC 90.6초, Codex 213.9초이며 Codex 쪽이 더 느립니다.
- **Longest Session**: jk-kim0/skills-jk#173 세션이 66342.3초로 가장 길었습니다.

## Population

| Population | Total | Included | Excluded Dry Run | Excluded In Progress | Excluded Missing Completed At |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sessions | 66 | 62 | 3 | 4 | - |
| Rounds | 323 | 69 | 0 | 0 | 254 |
| Steps | 258 | 258 | 0 | 0 | 0 |

_Sessions do not use the Excluded Missing Completed At column; session inclusion is based on `finished_at`._

## Statistics

- Coverage (rounds with steps): 55 / 69
- Coverage (rounds with breakdown): 45 / 69

### Completed Session And Round Wall-Clock Durations

| Metric | Count | Min | 25% | Median | 75% | Max | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sessions | 62 | 13.9 | 765.3 | 1681.3 | 2330.7 | 66342.3 | 3582.8 |
| Rounds | 69 | 15.9 | 53.6 | 117.4 | 310.3 | 1886.7 | 273.8 |

### Completed Step Wall-Clock Durations

| Metric | Count | Min | 25% | Median | 75% | Max | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| step0_sync | 26 | 0.2 | 40.1 | 66.4 | 98.8 | 432.0 | 94.1 |
| step1_lead_review | 133 | 0.1 | 29.8 | 115.8 | 161.5 | 1365.4 | 121.3 |
| step2_cross_review | 37 | 0.9 | 40.8 | 148.5 | 1493.1 | 9725.0 | 1425.9 |
| step3_lead_apply | 36 | 5.4 | 24.1 | 88.5 | 148.4 | 1580.9 | 153.1 |
| step4_settle | 26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

### Completed Step Wall-Clock Durations By Agent

| Metric | Count | Min | 25% | Median | 75% | Max | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| step1_lead_review / cc | 10 | 0.1 | 3.7 | 4.2 | 52.5 | 116.5 | 29.0 |
| step1_lead_review / codex | 123 | 0.1 | 41.4 | 120.7 | 166.6 | 1365.4 | 128.8 |
| step2_cross_review / cc | 12 | 151.6 | 2481.4 | 4294.9 | 4910.5 | 9725.0 | 4196.7 |
| step2_cross_review / codex | 25 | 0.9 | 33.0 | 82.4 | 148.5 | 230.8 | 96.0 |
| step3_lead_apply / cc | 2 | 5.4 | 6.2 | 7.0 | 7.7 | 8.5 | 7.0 |
| step3_lead_apply / codex | 34 | 9.3 | 41.1 | 97.2 | 149.4 | 1580.9 | 161.7 |

### Completed Step Active Durations

| Metric | Count | Min | 25% | Median | 75% | Max | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| step1_lead_review | 121 | 8.1 | 49.1 | 121.1 | 172.7 | 1365.4 | 135.3 |
| step2_cross_review | 35 | 0.9 | 40.4 | 143.4 | 2152.0 | 9725.0 | 1485.6 |
| step3_lead_apply | 34 | 9.3 | 70.0 | 109.0 | 157.9 | 1580.9 | 181.2 |

### Completed Step Active Durations By Agent

| Metric | Count | Min | 25% | Median | 75% | Max | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| step1_lead_review / codex | 121 | 8.1 | 49.1 | 121.1 | 172.7 | 1365.4 | 135.3 |
| step2_cross_review / cc | 10 | 1493.1 | 3845.8 | 4518.2 | 5472.2 | 9725.0 | 4961.9 |
| step2_cross_review / codex | 25 | 0.9 | 33.0 | 82.4 | 148.5 | 230.8 | 95.1 |
| step3_lead_apply / codex | 34 | 9.3 | 70.0 | 109.0 | 157.9 | 1580.9 | 181.2 |

### Completed Lead Agent Round Wall-Clock Durations

| Metric | Count | Min | 25% | Median | 75% | Max | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cc | 30 | 15.9 | 48.9 | 90.6 | 156.4 | 412.1 | 123.1 |
| Codex | 39 | 29.4 | 64.4 | 213.9 | 487.8 | 1886.7 | 389.7 |

## Appendix

### jk-kim0/skills-jk#182

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 892.2s
- Active: 137.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | 141.1s | 0.1s | skip | skip | 0.0s | 141.2s |
| 2 | cc | 73.1s | 67.8s | 75.7s | 5.4s | 0.0s | 222.0s |
| 3 | codex | 308.8s | 0.1s | skip | skip | 0.0s | 308.9s |
| 4 | cc | 46.9s | 6.7s | skip | skip | 0.0s | 53.6s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 141.2s
- Active: 72.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 141.1 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | 72.2 | codex | 1.1 | 0.5 | 3.1 | 67.1 |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 222.0s
- Active: 53.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 73.1 | None |  |  |  |  |  |
| step1_lead_review | 67.8 | None | cc |  |  |  |  |
| step2_cross_review | 75.7 | 53.6 | codex | 0.8 | 0.0 | 0.0 | 52.8 |
| step3_lead_apply | 5.4 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 308.9s
- Active: 12.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 308.8 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | 12.0 | codex | 0.2 | 0.0 | 0.0 | 11.8 |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 53.6s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 46.9 | None |  |  |  |  |  |
| step1_lead_review | 6.7 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### querypie/querypie-docs#979

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1848.7s
- Active: 903.3s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | 432.0s | 143.9s | 590.3s | 18.5s | 0.0s | 1184.7s |
| 2 | cc | 163.9s | 82.7s | 22.9s | 8.5s | 0.0s | 255.0s |
| 3 | codex | 31.0s | 5.7s | skip | skip | 0.0s | 36.7s |
| 4 | cc | 26.3s | 3.7s | skip | skip | 0.0s | 30.0s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 1184.7s
- Active: 866.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 432.0 | None |  |  |  |  |  |
| step1_lead_review | 143.9 | 295.5 | codex | 4.2 | 0.1 | 5.6 | 280.9 |
| step2_cross_review | 590.3 | None | cc |  |  |  |  |
| step3_lead_apply | 18.5 | 571.2 | codex | 2.1 | 2.9 | 84.2 | 457.2 |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 255.0s
- Active: 22.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 163.9 | None |  |  |  |  |  |
| step1_lead_review | 82.7 | None | cc |  |  |  |  |
| step2_cross_review | 22.9 | 22.9 | codex | 0.0 | 0.2 | 0.0 | 22.3 |
| step3_lead_apply | 8.5 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 36.7s
- Active: 13.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 31.0 | None |  |  |  |  |  |
| step1_lead_review | 5.7 | 13.7 | codex | 0.0 | 0.1 | 0.0 | 12.6 |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 30.0s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 26.3 | None |  |  |  |  |  |
| step1_lead_review | 3.7 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### chequer-io/deck#783

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 303.3s
- Active: 613.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | 17.2s | 160.8s | skip | 453.3s | 0.0s | 178.3s |
| 2 | cc | 0.2s | 116.5s | skip | skip | 0.0s | 117.1s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 178.3s
- Active: 613.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 17.2 | None |  |  |  |  |  |
| step1_lead_review | 160.8 | 160.3 | codex | 2.8 | 1.4 | 0.3 | 154.7 |
| step3_lead_apply | 453.3 | 453.3 | codex | 1.6 | 3.0 | 6.2 | 270.8 |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 117.1s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 0.2 | None |  |  |  |  |  |
| step1_lead_review | 116.5 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#179

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 666.1s
- Active: 305.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | 208.9s | 75.8s | 151.6s | 17.6s | 0.0s | 453.9s |
| 2 | cc | 85.0s | 4.7s | skip | skip | 0.0s | 89.7s |
| 3 | codex | 64.3s | 5.8s | skip | skip | 0.0s | 70.1s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 453.9s
- Active: 260.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 208.9 | None |  |  |  |  |  |
| step1_lead_review | 75.8 | 133.9 | codex | 3.9 | 0.0 | 3.9 | 125.7 |
| step2_cross_review | 151.6 | None | cc |  |  |  |  |
| step3_lead_apply | 17.6 | 126.5 | codex | 1.0 | 4.2 | 2.1 | 118.1 |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 89.7s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 85.0 | None |  |  |  |  |  |
| step1_lead_review | 4.7 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 70.1s
- Active: 44.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 64.3 | None |  |  |  |  |  |
| step1_lead_review | 5.8 | 44.8 | codex | 0.2 | 0.0 | 2.9 | 41.7 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#175

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 901.3s
- Active: 666.7s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 230.0s | skip | 160.5s | skip | 716.7s |
| 2 | cc | skip | skip | 219.1s | skip | skip | 81.9s |
| 3 | codex | 52.8s | 0.1s | skip | 19.8s | 0.0s | 52.9s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 716.7s
- Active: 390.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 230.0 | 230.0 | codex | 1.3 | 0.4 | 4.8 | 215.4 |
| step3_lead_apply | 160.5 | 160.5 | codex | 0.7 | 2.1 | 1.9 | 153.8 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 81.9s
- Active: 219.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 219.1 | 219.1 | codex | 0.5 | 0.0 | 3.4 | 215.2 |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 52.9s
- Active: 57.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 52.8 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | 37.3 | codex | 0.0 | 0.2 | 0.8 | 36.3 |
| step3_lead_apply | 19.8 | 19.8 | codex | 0.0 | 0.0 | 0.0 | 19.8 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#178

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 663.7s
- Active: 225.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 162.2s | skip | 32.1s | skip | 526.0s |
| 2 | cc | skip | skip | skip | skip | skip | 40.7s |
| 3 | codex | 58.7s | 0.1s | skip | skip | 0.0s | 58.8s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 526.0s
- Active: 194.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 162.2 | 162.2 | codex | 4.5 | 0.0 | 4.0 | 153.7 |
| step3_lead_apply | 32.1 | 32.1 | codex | 0.2 | 0.0 | 0.0 | 31.9 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 40.7s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 58.8s
- Active: 30.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 58.7 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | 30.9 | codex | 0.3 | 0.0 | 0.0 | 30.3 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#177

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1054.2s
- Active: 538.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 116.5s | skip | 124.1s | skip | 399.6s |
| 2 | cc | skip | skip | skip | skip | skip | 33.6s |
| 3 | codex | skip | 49.3s | skip | 91.5s | skip | 213.9s |
| 4 | cc | skip | skip | skip | skip | skip | 25.5s |
| 5 | codex | skip | 31.4s | skip | 75.4s | skip | 160.7s |
| 6 | cc | skip | skip | skip | skip | skip | 15.9s |
| 7 | codex | 82.3s | 29.1s | skip | skip | 0.0s | 111.4s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 399.6s
- Active: 240.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 116.5 | 116.5 | codex | 1.1 | 0.0 | 3.5 | 111.5 |
| step3_lead_apply | 124.1 | 124.1 | codex | 0.7 | 2.0 | 3.4 | 115.4 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 33.6s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 213.9s
- Active: 140.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 49.3 | 49.3 | codex | 1.1 | 0.0 | 4.0 | 44.0 |
| step3_lead_apply | 91.5 | 91.5 | codex | 0.2 | 2.1 | 3.2 | 82.6 |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 25.5s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 160.7s
- Active: 106.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 31.4 | 31.4 | codex | 0.2 | 0.0 | 3.4 | 27.6 |
| step3_lead_apply | 75.4 | 75.4 | codex | 0.2 | 2.0 | 3.4 | 68.0 |

#### Round 6

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 15.9s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 111.4s
- Active: 50.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 82.3 | None |  |  |  |  |  |
| step1_lead_review | 29.1 | 50.0 | codex | 0.3 | 0.0 | 3.2 | 46.2 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#174

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 284.6s
- Active: 61.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 61.0s | skip | skip | skip | 168.7s |
| 2 | cc | 87.7s | 3.8s | skip | skip | 0.0s | 91.5s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 168.7s
- Active: 61.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 61.0 | 61.0 | codex | 0.6 | 0.6 | 2.9 | 56.9 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 91.5s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 87.7 | None |  |  |  |  |  |
| step1_lead_review | 3.8 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#172

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1264.5s
- Active: 596.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 120.1s | skip | 112.8s | skip | 521.7s |
| 2 | cc | skip | skip | 56.3s | skip | skip | 68.5s |
| 3 | codex | skip | 76.7s | skip | 75.9s | skip | 248.8s |
| 4 | cc | skip | skip | 29.4s | skip | skip | 178.2s |
| 5 | codex | skip | 21.8s | skip | 103.0s | skip | 44.7s |
| 6 | cc | 100.5s | 3.8s | skip | skip | 0.0s | 104.4s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 521.7s
- Active: 232.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 120.1 | 120.1 | codex | 1.9 | 0.3 | 3.4 | 114.1 |
| step3_lead_apply | 112.8 | 112.8 | codex | 0.5 | 1.9 | 0.0 | 108.2 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 68.5s
- Active: 56.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 56.3 | 56.3 | codex | 2.1 | 0.0 | 2.4 | 51.8 |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 248.8s
- Active: 152.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 76.7 | 76.7 | codex | 0.1 | 0.0 | 2.8 | 73.8 |
| step3_lead_apply | 75.9 | 75.9 | codex | 0.1 | 1.9 | 0.0 | 72.5 |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 178.2s
- Active: 29.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 29.4 | 29.4 | codex | 0.5 | 0.0 | 0.0 | 28.9 |

#### Round 5

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 44.7s
- Active: 124.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 21.8 | 21.8 | codex | 0.0 | 0.0 | 1.9 | 19.9 |
| step3_lead_apply | 103.0 | 103.0 | codex | 0.5 | 1.8 | 0.0 | 98.4 |

#### Round 6

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 104.4s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 100.5 | None |  |  |  |  |  |
| step1_lead_review | 3.8 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#173

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 66342.3s
- Active: 566.7s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 87.6s | skip | skip | skip | - |
| 2 | cc | skip | skip | 117.9s | skip | skip | 412.1s |
| 3 | codex | skip | 43.4s | skip | 118.1s | skip | 315.1s |
| 4 | cc | skip | skip | 37.6s | skip | skip | 233.8s |
| 5 | codex | skip | 41.7s | skip | 76.8s | skip | 251.3s |
| 6 | cc | skip | skip | 22.1s | skip | skip | 155.9s |
| 7 | codex | skip | 21.5s | skip | skip | skip | 34.5s |
| 8 | cc | 42.0s | 0.1s | skip | skip | 0.0s | 42.1s |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 87.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 87.6 | 87.6 | codex | 0.3 | 1.6 | 5.9 | 79.7 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 412.1s
- Active: 117.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 117.9 | 117.9 | codex | 2.0 | 0.5 | 7.0 | 108.5 |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 315.1s
- Active: 161.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 43.4 | 43.4 | codex | 1.8 | 0.0 | 3.7 | 37.9 |
| step3_lead_apply | 118.1 | 118.1 | codex | 0.7 | 3.4 | 2.2 | 111.6 |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 233.8s
- Active: 37.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 37.6 | 37.6 | codex | 1.9 | 0.0 | 3.9 | 31.8 |

#### Round 5

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 251.3s
- Active: 118.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 41.7 | 41.7 | codex | 2.1 | 0.1 | 3.0 | 36.5 |
| step3_lead_apply | 76.8 | 76.8 | codex | 0.2 | 3.2 | 2.0 | 71.4 |

#### Round 6

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 155.9s
- Active: 22.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 22.1 | 22.1 | codex | 0.1 | 0.1 | 0.0 | 21.9 |

#### Round 7

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 34.5s
- Active: 21.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 21.5 | 21.5 | codex | 1.0 | 0.9 | 3.0 | 16.6 |

#### Round 8

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 42.1s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 42.0 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#171

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 785.6s
- Active: 304.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 148.1s | skip | 127.7s | skip | 552.4s |
| 2 | cc | skip | skip | skip | skip | skip | 156.6s |
| 3 | codex | 46.3s | 0.1s | skip | skip | 0.0s | 46.4s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 552.4s
- Active: 275.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 148.1 | 148.1 | codex | 3.6 | 0.0 | 4.7 | 139.7 |
| step3_lead_apply | 127.7 | 127.7 | codex | 0.6 | 1.9 | 0.0 | 123.3 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 156.6s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 46.4s
- Active: 29.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 46.3 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | 29.0 | codex | 0.0 | 1.1 | 2.9 | 24.9 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#170

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 287.3s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | 171.7s |
| 2 | cc | skip | skip | skip | skip | skip | 48.9s |
| 3 | codex | 29.3s | 0.1s | skip | skip | 0.0s | 29.4s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 171.7s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 48.9s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 29.4s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 29.3 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | None | codex |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#170

- Status: in_progress
- Outcome: None
- Dry run: True
- Stats eligibility: no (excluded from stats: dry_run, in_progress)
- Wall clock: 153010.8s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| (no rounds) | | | | | | | |

### querypie/querypie-docs#978

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1890.8s
- Active: 888.9s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 143.2s | skip | 472.2s | skip | 1010.8s |
| 2 | cc | skip | skip | 40.8s | skip | skip | 271.7s |
| 3 | codex | skip | 11.4s | skip | 211.2s | skip | 310.3s |
| 4 | cc | skip | skip | skip | skip | skip | 48.9s |
| 5 | codex | 28.1s | 4.9s | skip | skip | 0.0s | 33.0s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 1010.8s
- Active: 615.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 143.2 | 143.2 | codex | 1.2 | 1.7 | 3.8 | 136.0 |
| step3_lead_apply | 472.2 | 472.2 | codex | 1.4 | 1.9 | 10.1 | 366.2 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 271.7s
- Active: 40.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 40.8 | 40.8 | codex | 1.2 | 0.0 | 0.6 | 39.0 |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 310.3s
- Active: 222.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 11.4 | 11.4 | codex | 0.0 | 0.0 | 0.0 | 11.4 |
| step3_lead_apply | 211.2 | 211.2 | codex | 0.8 | 1.9 | 6.7 | 133.7 |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 48.9s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 33.0s
- Active: 10.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 28.1 | None |  |  |  |  |  |
| step1_lead_review | 4.9 | 10.1 | codex | 0.0 | 0.0 | 0.0 | 10.1 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#169

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 644.4s
- Active: 188.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 97.4s | skip | 68.2s | skip | 411.3s |
| 2 | cc | skip | skip | skip | skip | skip | 76.5s |
| 3 | codex | 39.5s | 3.9s | skip | skip | 0.0s | 43.4s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 411.3s
- Active: 165.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 97.4 | 97.4 | codex | 1.4 | 0.0 | 3.1 | 92.5 |
| step3_lead_apply | 68.2 | 68.2 | codex | 0.4 | 1.8 | 0.0 | 64.8 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 76.5s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 43.4s
- Active: 23.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 39.5 | None |  |  |  |  |  |
| step1_lead_review | 3.9 | 23.2 | codex | 0.0 | 0.0 | 3.5 | 19.7 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#167

- Status: in_progress
- Outcome: None
- Dry run: True
- Stats eligibility: no (excluded from stats: dry_run, in_progress)
- Wall clock: 157546.0s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| (no rounds) | | | | | | | |

### chequer-io/deck#773

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2135.3s
- Active: 414.3s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 129.6s | skip | 150.0s | skip | 1886.7s |
| 2 | cc | skip | skip | skip | skip | skip | 95.3s |
| 3 | codex | 68.6s | 4.1s | skip | 85.6s | 0.0s | 72.7s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 1886.7s
- Active: 279.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 129.6 | 129.6 | codex | 2.4 | 0.0 | 2.9 | 124.2 |
| step3_lead_apply | 150.0 | 150.0 | codex | 0.7 | 3.2 | 0.0 | 121.5 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 95.3s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 72.7s
- Active: 134.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 68.6 | None |  |  |  |  |  |
| step1_lead_review | 4.1 | 49.1 | codex | 0.0 | 1.1 | 2.3 | 45.7 |
| step3_lead_apply | 85.6 | 85.6 | codex | 1.4 | 3.2 | 0.0 | 64.5 |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#168

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2431.4s
- Active: 1598.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 17.7s | skip | 1580.9s | skip | 1813.3s |
| 2 | cc | skip | skip | skip | skip | skip | 82.6s |
| 3 | codex | skip | skip | skip | skip | skip | 345.7s |
| 4 | cc | skip | skip | skip | skip | skip | 39.9s |
| 5 | codex | 93.7s | 0.1s | skip | skip | 0.0s | 93.7s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 1813.3s
- Active: 1598.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 17.7 | 17.7 | codex | 0.3 | 0.0 | 0.0 | 17.4 |
| step3_lead_apply | 1580.9 | 1580.9 | codex | 6.5 | 3.9 | 4.7 | 1557.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 82.6s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 345.7s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 39.9s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 93.7s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 93.7 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | None | codex |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#167

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2910.1s
- Active: 1706.7s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 131.8s | skip | 112.5s | skip | 619.5s |
| 2 | cc | skip | skip | skip | skip | skip | 107.7s |
| 3 | codex | skip | 1365.4s | skip | 25.5s | skip | 1502.0s |
| 4 | cc | skip | skip | 30.4s | skip | skip | 395.5s |
| 5 | codex | skip | 41.1s | skip | skip | skip | 56.9s |
| 6 | cc | 117.4s | 0.1s | skip | skip | 0.0s | 117.4s |
#### Round 1

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 619.5s
- Active: 244.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 131.8 | 131.8 | codex | 1.9 | 0.0 | 3.9 | 125.8 |
| step3_lead_apply | 112.5 | 112.5 | codex | 0.5 | 6.3 | 2.1 | 103.3 |

#### Round 2

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 107.7s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 1502.0s
- Active: 1390.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 1365.4 | 1365.4 | codex | 0.2 | 0.0 | 0.0 | 1365.1 |
| step3_lead_apply | 25.5 | 25.5 | codex | 0.1 | 0.0 | 0.0 | 25.3 |

#### Round 4

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 395.5s
- Active: 30.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 30.4 | 30.4 | codex | 0.1 | 0.0 | 0.0 | 30.0 |

#### Round 5

- Lead agent: codex
- Stats eligibility: yes
- Wall clock: 56.9s
- Active: 41.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 41.1 | 41.1 | codex | 0.2 | 0.0 | 0.5 | 39.2 |

#### Round 6

- Lead agent: cc
- Stats eligibility: yes
- Wall clock: 117.4s
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 117.4 | None |  |  |  |  |  |
| step1_lead_review | 0.1 | None | cc |  |  |  |  |
| step4_settle | 0.0 | None |  |  |  |  |  |


### jk-kim0/skills-jk#165

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 760.7s
- Active: 333.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 140.5s | skip | 147.8s | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 44.7s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 288.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 140.5 | 140.5 | codex | 2.5 | 0.7 | 2.6 | 134.4 |
| step3_lead_apply | 147.8 | 147.8 | codex | 0.3 | 1.9 | 0.0 | 143.2 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 44.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 44.7 | 44.7 | codex | 0.2 | 0.6 | 2.3 | 41.5 |


### jk-kim0/skills-jk#164

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1135.1s
- Active: 155.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 13.5s | skip | 105.5s | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 36.0s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 119.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 13.5 | 13.5 | codex | 0.0 | 0.0 | 1.2 | 12.3 |
| step3_lead_apply | 105.5 | 105.5 | codex | 0.8 | 3.0 | 0.0 | 100.3 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 36.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 36.0 | 36.0 | codex | 0.4 | 0.0 | 3.7 | 31.9 |


### jk-kim0/skills-jk#166

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2094.8s
- Active: 330.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 120.7s | skip | 163.6s | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 45.7s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 284.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 120.7 | 120.7 | codex | 1.6 | 0.0 | 4.0 | 114.8 |
| step3_lead_apply | 163.6 | 163.6 | codex | 0.5 | 2.0 | 0.0 | 159.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 45.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 45.7 | 45.7 | codex | 1.6 | 0.0 | 2.6 | 41.5 |


### chequer-io/deck#772

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1267.8s
- Active: 396.9s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 135.0s | skip | 197.4s | skip | - |
| 2 | cc | skip | skip | 28.3s | skip | skip | - |
| 3 | codex | skip | 8.1s | skip | 15.1s | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 13.0s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 332.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 135.0 | 135.0 | codex | 4.1 | 0.7 | 3.5 | 126.7 |
| step3_lead_apply | 197.4 | 197.4 | codex | 4.0 | 3.2 | 3.5 | 166.4 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 28.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 28.3 | 28.3 | codex | 0.0 | 0.3 | 0.0 | 28.0 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 23.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 8.1 | 8.1 | codex | 0.0 | 0.0 | 0.0 | 8.1 |
| step3_lead_apply | 15.1 | 15.1 | codex | 0.0 | 0.0 | 0.0 | 15.1 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 13.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 13.0 | 13.0 | codex | 0.0 | 0.0 | 2.3 | 10.6 |


### querypie/querypie-docs#975

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1385.0s
- Active: 548.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 138.0s | skip | 366.1s | skip | - |
| 2 | cc | skip | skip | 33.0s | skip | skip | - |
| 3 | codex | skip | 11.7s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 504.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 138.0 | 138.0 | codex | 1.1 | 0.8 | 4.0 | 128.1 |
| step3_lead_apply | 366.1 | 366.1 | codex | 0.8 | 2.6 | 9.2 | 168.9 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 33.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 33.0 | 33.0 | codex | 0.0 | 0.3 | 0.0 | 32.7 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 11.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 11.7 | 11.7 | codex | 0.0 | 0.0 | 0.0 | 11.7 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#155

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1754.4s
- Active: 550.9s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 268.8s | skip | 85.3s | skip | - |
| 2 | cc | skip | skip | 40.0s | skip | skip | - |
| 3 | codex | skip | 27.0s | skip | 9.3s | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 30.5s | skip | 68.0s | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 22.0s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 354.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 268.8 | 268.8 | codex | 2.2 | 0.4 | 4.4 | 260.9 |
| step3_lead_apply | 85.3 | 85.3 | codex | 0.2 | 1.7 | 0.0 | 82.4 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 40.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 40.0 | 40.0 | codex | 0.1 | 0.2 | 0.0 | 39.7 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 36.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 27.0 | 27.0 | codex | 0.0 | 0.0 | 0.0 | 27.0 |
| step3_lead_apply | 9.3 | 9.3 | codex | 0.0 | 0.0 | 0.0 | 9.3 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 98.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 30.5 | 30.5 | codex | 0.2 | 0.2 | 0.0 | 30.1 |
| step3_lead_apply | 68.0 | 68.0 | codex | 0.0 | 1.9 | 0.0 | 65.3 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 22.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 22.0 | 22.0 | codex | 0.0 | 0.3 | 0.0 | 21.7 |


### chequer-io/querypie-ai-docs#129

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1721.3s
- Active: 523.1s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 245.2s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 94.1s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 61.8s | skip | skip | skip | - |
| 6 | cc | skip | skip | 0.9s | skip | skip | - |
| 7 | codex | skip | 121.1s | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 245.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 245.2 | 245.2 | codex | 3.9 | 0.9 | 5.1 | 231.8 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 94.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 94.1 | 94.1 | codex | 1.4 | 1.0 | 3.6 | 87.0 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 61.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 61.8 | 61.8 | codex | 0.9 | 0.0 | 0.5 | 59.2 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 0.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 0.9 | 0.9 | codex | 0.0 | 0.0 | 0.0 | 0.9 |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 121.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 121.1 | 121.1 | codex | 2.8 | 1.2 | 6.9 | 107.2 |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/querypie-ai-docs#128

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2390.4s
- Active: 670.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 172.7s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 202.5s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 133.5s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 161.5s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 172.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 172.7 | 172.7 | codex | 3.0 | 1.1 | 5.7 | 162.8 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 202.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 202.5 | 202.5 | codex | 1.3 | 1.7 | 5.8 | 191.5 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 133.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 133.5 | 133.5 | codex | 2.1 | 0.8 | 0.8 | 105.0 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 161.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 161.5 | 161.5 | codex | 1.9 | 0.2 | 1.2 | 142.0 |


### jk-kim0/skills-jk#153

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 5915.9s
- Active: 304.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 28.7s | skip | 15.2s | skip | - |
| 2 | cc | skip | skip | 109.1s | skip | skip | - |
| 3 | codex | skip | 29.8s | skip | 11.3s | skip | - |
| 4 | cc | skip | skip | 82.4s | skip | skip | - |
| 5 | codex | skip | 28.1s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 43.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 28.7 | 28.7 | codex | 0.2 | 0.0 | 0.0 | 28.5 |
| step3_lead_apply | 15.2 | 15.2 | codex | 0.1 | 0.0 | 0.0 | 15.1 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 109.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 109.1 | 109.1 | codex | 1.0 | 0.1 | 3.0 | 101.8 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 41.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 29.8 | 29.8 | codex | 0.2 | 0.2 | 0.1 | 29.3 |
| step3_lead_apply | 11.3 | 11.3 | codex | 0.0 | 0.0 | 0.0 | 11.3 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 82.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 82.4 | 82.4 | codex | 1.4 | 1.3 | 4.7 | 74.3 |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 28.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 28.1 | 28.1 | codex | 0.2 | 0.1 | 0.7 | 27.0 |


### querypie/querypie-docs#971

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1250.3s
- Active: 249.1s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 124.9s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 124.2s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 124.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 124.9 | 124.9 | codex | 1.6 | 0.7 | 5.3 | 114.9 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 124.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 124.2 | 124.2 | codex | 1.1 | 0.0 | 3.9 | 116.4 |


### querypie/querypie-docs#969

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 14523.2s
- Active: 6145.4s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 16.3s | skip | skip | skip | - |
| 2 | cc | skip | skip | 182.9s | skip | skip | - |
| 3 | codex | skip | 193.1s | 5753.1s | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 16.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 16.3 | 16.3 | codex | 0.2 | 0.0 | 0.0 | 16.1 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 182.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 182.9 | 182.9 | codex | 2.0 | 0.6 | 0.6 | 179.2 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 5946.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 193.1 | 193.1 | codex | 1.9 | 0.2 | 3.6 | 185.9 |
| step2_cross_review | 5753.1 | 5753.1 | cc | 757.3 | 31.0 | 1910.4 | 2243.0 |


### owner/repo#456

- Status: in_progress
- Outcome: None
- Dry run: False
- Stats eligibility: no (excluded from stats: in_progress)
- Wall clock: 315399.1s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| (no rounds) | | | | | | | |

### querypie/querypie-docs#970

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2103.6s
- Active: 575.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 98.4s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 90.6s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 112.5s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 274.3s | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 98.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 98.4 | 98.4 | codex | 1.4 | 0.8 | 2.9 | 91.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 90.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 90.6 | 90.6 | codex | 1.4 | 1.5 | 3.7 | 82.3 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 112.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 112.5 | 112.5 | codex | 1.9 | 1.1 | 2.6 | 105.6 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 274.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 274.3 | 274.3 | codex | 2.8 | 0.3 | 4.0 | 265.8 |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#154

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 235.1s
- Active: 53.3s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 53.3s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 53.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 53.3 | 53.3 | codex | 1.4 | 0.3 | 3.9 | 46.9 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### querypie/querypie-docs#968

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 3522.8s
- Active: 896.4s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 164.2s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 215.5s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 198.8s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 122.9s | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | 195.0s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 164.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 164.2 | 164.2 | codex | 2.8 | 1.3 | 4.0 | 154.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 215.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 215.5 | 215.5 | codex | 1.5 | 0.5 | 3.0 | 208.8 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 198.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 198.8 | 198.8 | codex | 1.7 | 1.2 | 3.5 | 192.1 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 122.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 122.9 | 122.9 | codex | 1.4 | 0.0 | 3.4 | 117.7 |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 195.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 195.0 | 195.0 | codex | 3.1 | 0.7 | 3.6 | 186.2 |


### jk-kim0/skills-jk#153

- Status: in_progress
- Outcome: None
- Dry run: True
- Stats eligibility: no (excluded from stats: dry_run, in_progress)
- Wall clock: 335561.0s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| (no rounds) | | | | | | | |

### chequer-io/deck#760

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 779.0s
- Active: 10140.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 97.0s | skip | skip | skip | - |
| 2 | cc | skip | skip | 193.7s | skip | skip | - |
| 3 | codex | skip | 125.1s | 9725.0s | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 97.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 97.0 | 97.0 | codex | 2.3 | 2.3 | 9.5 | 75.8 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 193.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 193.7 | 193.7 | codex | 3.9 | 0.4 | 8.5 | 164.1 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 9850.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 125.1 | 125.1 | codex | 0.7 | 3.0 | 6.5 | 111.5 |
| step2_cross_review | 9725.0 | 9725.0 | cc | 71.6 | 25.5 | 4.2 | 9553.4 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#152

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 256.8s
- Active: 110.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 110.2s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 110.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 110.2 | 110.2 | codex | 3.2 | 0.3 | 3.2 | 102.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### querypie/querypie-docs#967

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1641.3s
- Active: 615.7s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 205.5s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 99.4s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 310.8s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 205.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 205.5 | 205.5 | codex | 1.6 | 1.0 | 3.6 | 198.2 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 99.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 99.4 | 99.4 | codex | 1.5 | 0.0 | 2.3 | 94.1 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 310.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 310.8 | 310.8 | codex | 3.5 | 0.6 | 1.1 | 303.1 |


### jk-kim0/skills-jk#150

- Status: stalled
- Outcome: stalled
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1087.9s
- Active: 409.1s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 217.8s | skip | skip | skip | - |
| 2 | cc | skip | skip | 83.6s | skip | skip | - |
| 3 | codex | skip | 107.7s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 217.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 217.8 | 217.8 | codex | 1.9 | 1.0 | 5.4 | 207.8 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 83.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 83.6 | 83.6 | codex | 3.4 | 0.5 | 3.6 | 75.5 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 107.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 107.7 | 107.7 | codex | 2.1 | 0.7 | 5.0 | 97.6 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/deck#757

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 230.7s
- Active: 101.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 101.6s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 101.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 101.6 | 101.6 | codex | 0.5 | 0.8 | 5.2 | 89.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#149

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2572.1s
- Active: 764.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 174.5s | skip | skip | skip | - |
| 2 | cc | skip | skip | 143.4s | skip | skip | - |
| 3 | codex | skip | 128.2s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 118.0s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 200.5s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 174.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 174.5 | 174.5 | codex | 3.6 | 0.0 | 3.3 | 166.3 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 143.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 143.4 | 143.4 | codex | 3.4 | 0.2 | 3.2 | 135.5 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 128.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 128.2 | 128.2 | codex | 2.3 | 0.0 | 4.6 | 120.4 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 118.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 118.0 | 118.0 | codex | 3.8 | 0.1 | 4.9 | 108.0 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 200.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 200.5 | 200.5 | codex | 7.2 | 0.0 | 4.6 | 187.1 |


### chequer-io/deck#752

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2733.8s
- Active: 1322.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 234.7s | skip | skip | skip | - |
| 2 | cc | skip | skip | 230.8s | skip | skip | - |
| 3 | codex | skip | 273.4s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 266.7s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 317.2s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 234.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 234.7 | 234.7 | codex | 3.5 | 0.7 | 0.0 | 210.4 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 230.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 230.8 | 230.8 | codex | 4.5 | 2.6 | 6.9 | 211.6 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 273.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 273.4 | 273.4 | codex | 2.2 | 1.5 | 4.1 | 264.1 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 266.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 266.7 | 266.7 | codex | 2.4 | 0.0 | 4.1 | 236.2 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 317.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 317.2 | 317.2 | codex | 1.9 | 3.4 | 5.0 | 306.9 |


### querypie/querypie-docs#966

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1949.2s
- Active: 398.9s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 283.6s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 115.3s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 283.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 283.6 | 283.6 | codex | 1.6 | 1.1 | 5.2 | 273.6 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 115.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 115.3 | 115.3 | codex | 1.9 | 1.3 | 5.2 | 105.9 |


### jk-kim0/skills-jk#147

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 3684.7s
- Active: 711.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 158.5s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 266.3s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 140.5s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 145.7s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 158.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 158.5 | 158.5 | codex | 1.4 | 0.9 | 4.2 | 151.2 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 266.3s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 266.3 | 266.3 | codex | 0.9 | 0.0 | 3.7 | 261.2 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 140.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 140.5 | 140.5 | codex | 1.6 | 0.0 | 6.1 | 132.2 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 145.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 145.7 | 145.7 | codex | 3.7 | 0.8 | 4.6 | 135.9 |


### jk-kim0/skills-jk#145

- Status: failed
- Outcome: error
- Dry run: False
- Stats eligibility: yes
- Wall clock: 13.9s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| (no rounds) | | | | | | | |

### chequer-io/querypie-mono#15962

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 7649.3s
- Active: 998.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 182.9s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 263.9s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 309.4s | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | 242.4s | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 182.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 182.9 | 182.9 | codex | 5.3 | 1.2 | 0.0 | 176.3 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 263.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 263.9 | 263.9 | codex | 5.0 | 2.3 | 3.6 | 249.7 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 309.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 309.4 | 309.4 | codex | 8.4 | 0.1 | 5.8 | 291.7 |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 242.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 242.4 | 242.4 | codex | 6.8 | 0.0 | 4.0 | 231.6 |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### querypie/querypie-docs#963

- Status: stalled
- Outcome: stalled
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2151.6s
- Active: 3852.9s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 115.8s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | 3737.1s | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 115.8s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 115.8 | 115.8 | codex | 1.8 | 1.0 | 0.0 | 112.1 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 3737.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 3737.1 | 3737.1 | cc | 151.0 | 108.6 | 14.6 | 2518.3 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#143

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1861.0s
- Active: 316.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 114.1s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 114.9s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | 87.0s | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 114.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 114.1 | 114.1 | codex | 1.3 | 0.5 | 0.0 | 111.5 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 114.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 114.9 | 114.9 | codex | 1.3 | 0.0 | 0.0 | 113.2 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 87.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 87.0 | 87.0 | codex | 1.8 | 0.0 | 0.2 | 84.3 |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/deck#749

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 694.9s
- Active: 8491.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 230.0s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | 8261.6s | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 230.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 230.0 | 230.0 | codex | 5.0 | 0.0 | 0.0 | 213.0 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 8261.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 8261.6 | 8261.6 | cc | 54.4 | 20.0 | 10.5 | 7850.8 |


### chequer-io/deck#748

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1016.5s
- Active: 106.4s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 106.4s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 106.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 106.4 | 106.4 | codex | 1.3 | 0.0 | 0.0 | 72.2 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#144

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 515.8s
- Active: 155.5s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 155.5s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 155.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 155.5 | 155.5 | codex | 0.8 | 0.1 | 0.0 | 154.5 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#142

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2138.7s
- Active: 4417.7s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | 4417.7s | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 4417.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 4417.7 | 4417.7 | cc | 9.6 | 15.2 | 13.9 | 3987.3 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/deck#745

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1954.4s
- Active: 490.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 277.7s | skip | skip | skip | - |
| 2 | cc | skip | skip | 212.5s | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 277.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 277.7 | 277.7 | codex | 4.7 | 0.1 | 0.0 | 268.0 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 212.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 212.5 | 212.5 | codex | 3.9 | 0.0 | 0.0 | 208.6 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/deck#744

- Status: failed
- Outcome: error
- Dry run: False
- Stats eligibility: yes
- Wall clock: 757.4s
- Active: 4940.3s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 169.1s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 152.5s | 4618.7s | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 169.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 169.1 | 169.1 | codex | 1.1 | 0.0 | 0.0 | 168.0 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 4771.2s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 152.5 | 152.5 | codex | 2.2 | 0.0 | 0.0 | 150.3 |
| step2_cross_review | 4618.7 | 4618.7 | cc | 6.4 | 28.4 | 10.2 | 3625.2 |


### jk-kim0/skills-jk#141

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 3544.3s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### querypie/querypie-docs#962

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2119.7s
- Active: 661.4s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 144.5s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 126.6s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 157.1s | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | 100.5s | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | 132.7s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 144.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 144.5 | 144.5 | codex | 1.6 | 0.8 | 0.0 | 141.3 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 126.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 126.6 | 126.6 | codex | 1.6 | 0.1 | 0.0 | 124.5 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 157.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 157.1 | 157.1 | codex | 1.5 | 0.3 | 0.0 | 154.5 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 100.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 100.5 | 100.5 | codex | 1.2 | 0.2 | 0.0 | 98.1 |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 132.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 132.7 | 132.7 | codex | 0.7 | 0.2 | 0.0 | 130.6 |


### querypie/querypie-docs#961

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1514.0s
- Active: 425.2s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 121.1s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | 177.4s | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | 126.7s | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 121.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 121.1 | 121.1 | codex | 4.6 | 0.0 | 0.0 | 116.4 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 177.4s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 177.4 | 177.4 | codex | 1.6 | 0.3 | 0.0 | 174.7 |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 126.7s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 126.7 | 126.7 | codex | 2.3 | 0.7 | 0.0 | 122.6 |


### jk-kim0/skills-jk#137

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2795.6s
- Active: 4629.6s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | 4629.6s | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 4629.6s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 4629.6 | 4629.6 | cc | 1.8 | 20.0 | 10.7 | 3997.4 |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#135

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1865.4s
- Active: 3033.8s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | 222.9s | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | 2810.9s | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 222.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 222.9 | 222.9 | codex | 2.1 | 0.0 | 0.0 | 220.0 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 2810.9s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 2810.9 | 2810.9 | cc | 0.7 | 12.4 | 12.8 | 2510.0 |


### jk-kim0/skills-jk#134

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 211.3s
- Active: 4172.0s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | 4172.0s | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 4172.0s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 4172.0 | 4172.0 | cc | 116.4 | 29.2 | 26.4 | 3776.5 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### querypie/querypie-docs#958

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 5573.1s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/deck#734

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 229.7s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/querypie-mono#15924

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 12112.1s
- Active: 171.1s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | 171.1s | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 171.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 171.1 | 171.1 | codex | 9.0 | 1.0 | 0.0 | 161.1 |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### querypie/querypie-docs#957

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 1538.1s
- Active: 148.5s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | 148.5s | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 148.5s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 148.5 | 148.5 | codex | 2.1 | 0.2 | 0.0 | 144.8 |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### chequer-io/deck#735

- Status: consensus_reached
- Outcome: consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 2029.0s
- Active: 1493.1s

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | 1493.1s | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: 1493.1s

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 1493.1 | 1493.1 | cc | 6.6 | 6.7 | 8.7 | 913.7 |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |


### jk-kim0/skills-jk#131

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Dry run: False
- Stats eligibility: yes
- Wall clock: 29548.5s
- Active: Nones

| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | codex | skip | skip | skip | skip | skip | - |
| 2 | cc | skip | skip | skip | skip | skip | - |
| 3 | codex | skip | skip | skip | skip | skip | - |
| 4 | cc | skip | skip | skip | skip | skip | - |
| 5 | codex | skip | skip | skip | skip | skip | - |
| 6 | cc | skip | skip | skip | skip | skip | - |
| 7 | codex | skip | skip | skip | skip | skip | - |
| 8 | cc | skip | skip | skip | skip | skip | - |
| 9 | codex | skip | skip | skip | skip | skip | - |
| 10 | cc | skip | skip | skip | skip | skip | - |
#### Round 1

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Stats eligibility: no (excluded from stats: missing_completed_at)
- Wall clock: Nones
- Active: Nones

| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |  |
