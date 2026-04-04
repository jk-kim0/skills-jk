# Debate Review Session Report

- Generated at: 2026-04-04T12:18:19.382789+00:00
- Sessions: 62
- Completed: 56
- In progress: 6

## Findings

- **Step-Level Coverage**: 306개 round 중 step 정보가 있는 round는 147개, agent breakdown이 있는 round는 140개입니다.
- **Slowest Median Step**: step2_cross_review의 median은 145.9초로, 집계된 step 중 가장 깁니다.
- **Lead Agent Comparison**: Lead round median은 CC 99.8초, Codex 310.3초이며 Codex 쪽이 더 느립니다.
- **Longest Session**: jk-kim0/skills-jk#153 세션이 257025.6초로 가장 길었습니다.

## Statistics

- Coverage (rounds with steps): 147 / 306
- Coverage (rounds with breakdown): 140 / 306

### Durations

| Metric | Count | Min | Max | Average | Median |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sessions | 62 | 13.9 | 257025.6 | 13987.0 | 1878.1 |
| Rounds | 53 | 9.8 | 66330.5 | 1599.2 | 156.6 |

### Step Durations

| Metric | Count | Min | Max | Average | Median |
| --- | ---: | ---: | ---: | ---: | ---: |
| step0_sync | 13 | 9.8 | 279.2 | 75.8 | 46.3 |
| step1_lead_review | 117 | 0.1 | 1365.4 | 136.8 | 121.1 |
| step2_cross_review | 32 | 0.9 | 9725.0 | 1615.6 | 145.9 |
| step3_lead_apply | 28 | 9.3 | 1580.9 | 186.6 | 109.0 |
| step4_settle | 11 | 0.0 | 0.0 | 0.0 | 0.0 |

### Lead Agent Round Durations

| Metric | Count | Min | Max | Average | Median |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cc | 22 | 35.2 | 412.1 | 137.2 | 99.8 |
| Codex | 31 | 9.8 | 66330.5 | 2636.7 | 310.3 |

## Appendix

### jk-kim0/skills-jk#177

- Status: in_progress
- Outcome: None
- Duration: 25.5s

#### Round 1

- Lead agent: codex
- Duration: 9.8s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 9.8 |  |  |  |  |  |


### jk-kim0/skills-jk#175

- Status: in_progress
- Outcome: None
- Duration: 1050.1s

#### Round 1

- Lead agent: codex
- Duration: 1035.3s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 279.2 |  |  |  |  |  |
| step1_lead_review | 756.1 | codex | 1.9 | 0.0 | 3.8 | 127.7 |


### jk-kim0/skills-jk#174

- Status: consensus_reached
- Outcome: consensus
- Duration: 284.6s

#### Round 1

- Lead agent: codex
- Duration: 168.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 61.0 | codex | 0.6 | 0.6 | 2.9 | 56.9 |

#### Round 2

- Lead agent: cc
- Duration: 91.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 87.7 |  |  |  |  |  |
| step1_lead_review | 3.8 | cc |  |  |  |  |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#172

- Status: consensus_reached
- Outcome: consensus
- Duration: 1264.5s

#### Round 1

- Lead agent: codex
- Duration: 521.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 120.1 | codex | 1.9 | 0.3 | 3.4 | 114.1 |
| step3_lead_apply | 112.8 | codex | 0.5 | 1.9 | 0.0 | 108.2 |

#### Round 2

- Lead agent: cc
- Duration: 68.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 56.3 | codex | 2.1 | 0.0 | 2.4 | 51.8 |

#### Round 3

- Lead agent: codex
- Duration: 248.8s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 76.7 | codex | 0.1 | 0.0 | 2.8 | 73.8 |
| step3_lead_apply | 75.9 | codex | 0.1 | 1.9 | 0.0 | 72.5 |

#### Round 4

- Lead agent: cc
- Duration: 178.2s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 29.4 | codex | 0.5 | 0.0 | 0.0 | 28.9 |

#### Round 5

- Lead agent: codex
- Duration: 44.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 21.8 | codex | 0.0 | 0.0 | 1.9 | 19.9 |
| step3_lead_apply | 103.0 | codex | 0.5 | 1.8 | 0.0 | 98.4 |

#### Round 6

- Lead agent: cc
- Duration: 104.4s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 100.5 |  |  |  |  |  |
| step1_lead_review | 3.8 | cc |  |  |  |  |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#173

- Status: consensus_reached
- Outcome: consensus
- Duration: 66342.3s

#### Round 1

- Lead agent: codex
- Duration: 66330.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 87.6 | codex | 0.3 | 1.6 | 5.9 | 79.7 |

#### Round 2

- Lead agent: cc
- Duration: 412.1s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 117.9 | codex | 2.0 | 0.5 | 7.0 | 108.5 |

#### Round 3

- Lead agent: codex
- Duration: 315.1s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 43.4 | codex | 1.8 | 0.0 | 3.7 | 37.9 |
| step3_lead_apply | 118.1 | codex | 0.7 | 3.4 | 2.2 | 111.6 |

#### Round 4

- Lead agent: cc
- Duration: 233.8s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 37.6 | codex | 1.9 | 0.0 | 3.9 | 31.8 |

#### Round 5

- Lead agent: codex
- Duration: 251.3s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 41.7 | codex | 2.1 | 0.1 | 3.0 | 36.5 |
| step3_lead_apply | 76.8 | codex | 0.2 | 3.2 | 2.0 | 71.4 |

#### Round 6

- Lead agent: cc
- Duration: 155.9s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 22.1 | codex | 0.1 | 0.1 | 0.0 | 21.9 |

#### Round 7

- Lead agent: codex
- Duration: 34.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 21.5 | codex | 1.0 | 0.9 | 3.0 | 16.6 |

#### Round 8

- Lead agent: cc
- Duration: 42.1s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 42.0 |  |  |  |  |  |
| step1_lead_review | 0.1 | cc |  |  |  |  |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#171

- Status: consensus_reached
- Outcome: consensus
- Duration: 785.6s

#### Round 1

- Lead agent: codex
- Duration: 552.4s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 148.1 | codex | 3.6 | 0.0 | 4.7 | 139.7 |
| step3_lead_apply | 127.7 | codex | 0.6 | 1.9 | 0.0 | 123.3 |

#### Round 2

- Lead agent: cc
- Duration: 156.6s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 46.4s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 46.3 |  |  |  |  |  |
| step1_lead_review | 0.1 | codex | 0.0 | 1.1 | 2.9 | 24.9 |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#170

- Status: consensus_reached
- Outcome: consensus
- Duration: 287.3s

#### Round 1

- Lead agent: codex
- Duration: 171.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: 48.9s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 29.4s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 29.3 |  |  |  |  |  |
| step1_lead_review | 0.1 | codex |  |  |  |  |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#170

- Status: in_progress
- Outcome: None
- Duration: 74475.4s


### querypie/querypie-docs#978

- Status: consensus_reached
- Outcome: consensus
- Duration: 1890.8s

#### Round 1

- Lead agent: codex
- Duration: 1010.8s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 143.2 | codex | 1.2 | 1.7 | 3.8 | 136.0 |
| step3_lead_apply | 472.2 | codex | 1.4 | 1.9 | 10.1 | 366.2 |

#### Round 2

- Lead agent: cc
- Duration: 271.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 40.8 | codex | 1.2 | 0.0 | 0.6 | 39.0 |

#### Round 3

- Lead agent: codex
- Duration: 310.3s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 11.4 | codex | 0.0 | 0.0 | 0.0 | 11.4 |
| step3_lead_apply | 211.2 | codex | 0.8 | 1.9 | 6.7 | 133.7 |

#### Round 4

- Lead agent: cc
- Duration: 48.9s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: 33.0s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 28.1 |  |  |  |  |  |
| step1_lead_review | 4.9 | codex | 0.0 | 0.0 | 0.0 | 10.1 |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#169

- Status: consensus_reached
- Outcome: consensus
- Duration: 644.4s

#### Round 1

- Lead agent: codex
- Duration: 411.3s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 97.4 | codex | 1.4 | 0.0 | 3.1 | 92.5 |
| step3_lead_apply | 68.2 | codex | 0.4 | 1.8 | 0.0 | 64.8 |

#### Round 2

- Lead agent: cc
- Duration: 76.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 43.4s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 39.5 |  |  |  |  |  |
| step1_lead_review | 3.9 | codex | 0.0 | 0.0 | 3.5 | 19.7 |
| step4_settle | 0.0 |  |  |  |  |  |


### chequer-io/deck#783

- Status: consensus_reached
- Outcome: consensus
- Duration: 2935.4s

#### Round 1

- Lead agent: codex
- Duration: 2917.1s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 197.6 | codex | 2.0 | 0.0 | 8.2 | 185.0 |
| step3_lead_apply | 453.3 | codex | 1.6 | 3.0 | 6.2 | 270.8 |

#### Round 2

- Lead agent: cc
- Duration: 195.1s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 457.6s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 128.9 | codex | 2.1 | 0.0 | 2.8 | 123.9 |
| step3_lead_apply | 239.0 | codex | 0.9 | 3.1 | 2.8 | 166.0 |

#### Round 4

- Lead agent: cc
- Duration: 35.2s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: 355.0s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 79.7 | codex | 0.9 | 0.0 | 2.8 | 76.0 |
| step3_lead_apply | 28.1 | codex | 0.2 | 0.0 | 0.0 | 27.9 |

#### Round 6

- Lead agent: cc
- Duration: 61.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: 48.8s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 43.9 |  |  |  |  |  |
| step1_lead_review | 4.9 | codex | 0.1 | 0.0 | 2.9 | 19.0 |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#167

- Status: in_progress
- Outcome: None
- Duration: 79010.6s


### chequer-io/deck#773

- Status: consensus_reached
- Outcome: consensus
- Duration: 2135.3s

#### Round 1

- Lead agent: codex
- Duration: 1886.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 129.6 | codex | 2.4 | 0.0 | 2.9 | 124.2 |
| step3_lead_apply | 150.0 | codex | 0.7 | 3.2 | 0.0 | 121.5 |

#### Round 2

- Lead agent: cc
- Duration: 95.3s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 72.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 68.6 |  |  |  |  |  |
| step1_lead_review | 4.1 | codex | 0.0 | 1.1 | 2.3 | 45.7 |
| step3_lead_apply | 85.6 | codex | 1.4 | 3.2 | 0.0 | 64.5 |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#168

- Status: consensus_reached
- Outcome: consensus
- Duration: 2431.4s

#### Round 1

- Lead agent: codex
- Duration: 1813.3s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 17.7 | codex | 0.3 | 0.0 | 0.0 | 17.4 |
| step3_lead_apply | 1580.9 | codex | 6.5 | 3.9 | 4.7 | 1557.6 |

#### Round 2

- Lead agent: cc
- Duration: 82.6s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 345.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: 39.9s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: 93.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 93.7 |  |  |  |  |  |
| step1_lead_review | 0.1 | codex |  |  |  |  |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#167

- Status: consensus_reached
- Outcome: consensus
- Duration: 2910.1s

#### Round 1

- Lead agent: codex
- Duration: 619.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 131.8 | codex | 1.9 | 0.0 | 3.9 | 125.8 |
| step3_lead_apply | 112.5 | codex | 0.5 | 6.3 | 2.1 | 103.3 |

#### Round 2

- Lead agent: cc
- Duration: 107.7s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: 1502.0s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 1365.4 | codex | 0.2 | 0.0 | 0.0 | 1365.1 |
| step3_lead_apply | 25.5 | codex | 0.1 | 0.0 | 0.0 | 25.3 |

#### Round 4

- Lead agent: cc
- Duration: 395.5s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 30.4 | codex | 0.1 | 0.0 | 0.0 | 30.0 |

#### Round 5

- Lead agent: codex
- Duration: 56.9s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 41.1 | codex | 0.2 | 0.0 | 0.5 | 39.2 |

#### Round 6

- Lead agent: cc
- Duration: 117.4s

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step0_sync | 117.4 |  |  |  |  |  |
| step1_lead_review | 0.1 | cc |  |  |  |  |
| step4_settle | 0.0 |  |  |  |  |  |


### jk-kim0/skills-jk#165

- Status: consensus_reached
- Outcome: consensus
- Duration: 760.7s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 140.5 | codex | 2.5 | 0.7 | 2.6 | 134.4 |
| step3_lead_apply | 147.8 | codex | 0.3 | 1.9 | 0.0 | 143.2 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 44.7 | codex | 0.2 | 0.6 | 2.3 | 41.5 |


### jk-kim0/skills-jk#164

- Status: consensus_reached
- Outcome: consensus
- Duration: 1135.1s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 13.5 | codex | 0.0 | 0.0 | 1.2 | 12.3 |
| step3_lead_apply | 105.5 | codex | 0.8 | 3.0 | 0.0 | 100.3 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 36.0 | codex | 0.4 | 0.0 | 3.7 | 31.9 |


### jk-kim0/skills-jk#166

- Status: consensus_reached
- Outcome: consensus
- Duration: 2094.8s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 120.7 | codex | 1.6 | 0.0 | 4.0 | 114.8 |
| step3_lead_apply | 163.6 | codex | 0.5 | 2.0 | 0.0 | 159.6 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 45.7 | codex | 1.6 | 0.0 | 2.6 | 41.5 |


### chequer-io/deck#772

- Status: consensus_reached
- Outcome: consensus
- Duration: 1267.8s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 135.0 | codex | 4.1 | 0.7 | 3.5 | 126.7 |
| step3_lead_apply | 197.4 | codex | 4.0 | 3.2 | 3.5 | 166.4 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 28.3 | codex | 0.0 | 0.3 | 0.0 | 28.0 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 8.1 | codex | 0.0 | 0.0 | 0.0 | 8.1 |
| step3_lead_apply | 15.1 | codex | 0.0 | 0.0 | 0.0 | 15.1 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 13.0 | codex | 0.0 | 0.0 | 2.3 | 10.6 |


### querypie/querypie-docs#975

- Status: consensus_reached
- Outcome: consensus
- Duration: 1385.0s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 138.0 | codex | 1.1 | 0.8 | 4.0 | 128.1 |
| step3_lead_apply | 366.1 | codex | 0.8 | 2.6 | 9.2 | 168.9 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 33.0 | codex | 0.0 | 0.3 | 0.0 | 32.7 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 11.7 | codex | 0.0 | 0.0 | 0.0 | 11.7 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#155

- Status: consensus_reached
- Outcome: consensus
- Duration: 1754.4s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 268.8 | codex | 2.2 | 0.4 | 4.4 | 260.9 |
| step3_lead_apply | 85.3 | codex | 0.2 | 1.7 | 0.0 | 82.4 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 40.0 | codex | 0.1 | 0.2 | 0.0 | 39.7 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 27.0 | codex | 0.0 | 0.0 | 0.0 | 27.0 |
| step3_lead_apply | 9.3 | codex | 0.0 | 0.0 | 0.0 | 9.3 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 30.5 | codex | 0.2 | 0.2 | 0.0 | 30.1 |
| step3_lead_apply | 68.0 | codex | 0.0 | 1.9 | 0.0 | 65.3 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 22.0 | codex | 0.0 | 0.3 | 0.0 | 21.7 |


### chequer-io/querypie-ai-docs#129

- Status: consensus_reached
- Outcome: consensus
- Duration: 1721.3s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 245.2 | codex | 3.9 | 0.9 | 5.1 | 231.8 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 94.1 | codex | 1.4 | 1.0 | 3.6 | 87.0 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 61.8 | codex | 0.9 | 0.0 | 0.5 | 59.2 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 0.9 | codex | 0.0 | 0.0 | 0.0 | 0.9 |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 121.1 | codex | 2.8 | 1.2 | 6.9 | 107.2 |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/querypie-ai-docs#128

- Status: consensus_reached
- Outcome: consensus
- Duration: 2390.4s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 172.7 | codex | 3.0 | 1.1 | 5.7 | 162.8 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 202.5 | codex | 1.3 | 1.7 | 5.8 | 191.5 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 133.5 | codex | 2.1 | 0.8 | 0.8 | 105.0 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 161.5 | codex | 1.9 | 0.2 | 1.2 | 142.0 |


### jk-kim0/skills-jk#153

- Status: consensus_reached
- Outcome: consensus
- Duration: 5915.9s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 28.7 | codex | 0.2 | 0.0 | 0.0 | 28.5 |
| step3_lead_apply | 15.2 | codex | 0.1 | 0.0 | 0.0 | 15.1 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 109.1 | codex | 1.0 | 0.1 | 3.0 | 101.8 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 29.8 | codex | 0.2 | 0.2 | 0.1 | 29.3 |
| step3_lead_apply | 11.3 | codex | 0.0 | 0.0 | 0.0 | 11.3 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 82.4 | codex | 1.4 | 1.3 | 4.7 | 74.3 |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 28.1 | codex | 0.2 | 0.1 | 0.7 | 27.0 |


### querypie/querypie-docs#971

- Status: consensus_reached
- Outcome: consensus
- Duration: 1250.3s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 124.9 | codex | 1.6 | 0.7 | 5.3 | 114.9 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 124.2 | codex | 1.1 | 0.0 | 3.9 | 116.4 |


### querypie/querypie-docs#969

- Status: consensus_reached
- Outcome: consensus
- Duration: 14523.2s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 16.3 | codex | 0.2 | 0.0 | 0.0 | 16.1 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 182.9 | codex | 2.0 | 0.6 | 0.6 | 179.2 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 193.1 | codex | 1.9 | 0.2 | 3.6 | 185.9 |
| step2_cross_review | 5753.1 | cc | 757.3 | 31.0 | 1910.4 | 2243.0 |


### owner/repo#456

- Status: in_progress
- Outcome: None
- Duration: 236863.7s


### querypie/querypie-docs#970

- Status: consensus_reached
- Outcome: consensus
- Duration: 2103.6s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 98.4 | codex | 1.4 | 0.8 | 2.9 | 91.6 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 90.6 | codex | 1.4 | 1.5 | 3.7 | 82.3 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 112.5 | codex | 1.9 | 1.1 | 2.6 | 105.6 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 274.3 | codex | 2.8 | 0.3 | 4.0 | 265.8 |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#154

- Status: consensus_reached
- Outcome: consensus
- Duration: 235.1s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 53.3 | codex | 1.4 | 0.3 | 3.9 | 46.9 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### querypie/querypie-docs#968

- Status: consensus_reached
- Outcome: consensus
- Duration: 3522.8s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 164.2 | codex | 2.8 | 1.3 | 4.0 | 154.6 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 215.5 | codex | 1.5 | 0.5 | 3.0 | 208.8 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 198.8 | codex | 1.7 | 1.2 | 3.5 | 192.1 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 122.9 | codex | 1.4 | 0.0 | 3.4 | 117.7 |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 195.0 | codex | 3.1 | 0.7 | 3.6 | 186.2 |


### jk-kim0/skills-jk#153

- Status: in_progress
- Outcome: None
- Duration: 257025.6s


### chequer-io/deck#760

- Status: consensus_reached
- Outcome: consensus
- Duration: 779.0s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 97.0 | codex | 2.3 | 2.3 | 9.5 | 75.8 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 193.7 | codex | 3.9 | 0.4 | 8.5 | 164.1 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 125.1 | codex | 0.7 | 3.0 | 6.5 | 111.5 |
| step2_cross_review | 9725.0 | cc | 71.6 | 25.5 | 4.2 | 9553.4 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#152

- Status: consensus_reached
- Outcome: consensus
- Duration: 256.8s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 110.2 | codex | 3.2 | 0.3 | 3.2 | 102.6 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### querypie/querypie-docs#967

- Status: consensus_reached
- Outcome: consensus
- Duration: 1641.3s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 205.5 | codex | 1.6 | 1.0 | 3.6 | 198.2 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 99.4 | codex | 1.5 | 0.0 | 2.3 | 94.1 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 310.8 | codex | 3.5 | 0.6 | 1.1 | 303.1 |


### jk-kim0/skills-jk#150

- Status: stalled
- Outcome: stalled
- Duration: 1087.9s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 217.8 | codex | 1.9 | 1.0 | 5.4 | 207.8 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 83.6 | codex | 3.4 | 0.5 | 3.6 | 75.5 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 107.7 | codex | 2.1 | 0.7 | 5.0 | 97.6 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/deck#757

- Status: consensus_reached
- Outcome: consensus
- Duration: 230.7s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 101.6 | codex | 0.5 | 0.8 | 5.2 | 89.6 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#149

- Status: consensus_reached
- Outcome: consensus
- Duration: 2572.1s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 174.5 | codex | 3.6 | 0.0 | 3.3 | 166.3 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 143.4 | codex | 3.4 | 0.2 | 3.2 | 135.5 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 128.2 | codex | 2.3 | 0.0 | 4.6 | 120.4 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 118.0 | codex | 3.8 | 0.1 | 4.9 | 108.0 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 200.5 | codex | 7.2 | 0.0 | 4.6 | 187.1 |


### chequer-io/deck#752

- Status: consensus_reached
- Outcome: consensus
- Duration: 2733.8s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 234.7 | codex | 3.5 | 0.7 | 0.0 | 210.4 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 230.8 | codex | 4.5 | 2.6 | 6.9 | 211.6 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 273.4 | codex | 2.2 | 1.5 | 4.1 | 264.1 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 266.7 | codex | 2.4 | 0.0 | 4.1 | 236.2 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 317.2 | codex | 1.9 | 3.4 | 5.0 | 306.9 |


### querypie/querypie-docs#966

- Status: consensus_reached
- Outcome: consensus
- Duration: 1949.2s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 283.6 | codex | 1.6 | 1.1 | 5.2 | 273.6 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 115.3 | codex | 1.9 | 1.3 | 5.2 | 105.9 |


### jk-kim0/skills-jk#147

- Status: consensus_reached
- Outcome: consensus
- Duration: 3684.7s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 158.5 | codex | 1.4 | 0.9 | 4.2 | 151.2 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 266.3 | codex | 0.9 | 0.0 | 3.7 | 261.2 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 140.5 | codex | 1.6 | 0.0 | 6.1 | 132.2 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 145.7 | codex | 3.7 | 0.8 | 4.6 | 135.9 |


### jk-kim0/skills-jk#145

- Status: failed
- Outcome: error
- Duration: 13.9s


### chequer-io/querypie-mono#15962

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Duration: 7649.3s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 182.9 | codex | 5.3 | 1.2 | 0.0 | 176.3 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 263.9 | codex | 5.0 | 2.3 | 3.6 | 249.7 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 309.4 | codex | 8.4 | 0.1 | 5.8 | 291.7 |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 242.4 | codex | 6.8 | 0.0 | 4.0 | 231.6 |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### querypie/querypie-docs#963

- Status: stalled
- Outcome: stalled
- Duration: 2151.6s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 115.8 | codex | 1.8 | 1.0 | 0.0 | 112.1 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 3737.1 | cc | 151.0 | 108.6 | 14.6 | 2518.3 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#143

- Status: consensus_reached
- Outcome: consensus
- Duration: 1861.0s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 114.1 | codex | 1.3 | 0.5 | 0.0 | 111.5 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 114.9 | codex | 1.3 | 0.0 | 0.0 | 113.2 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 87.0 | codex | 1.8 | 0.0 | 0.2 | 84.3 |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/deck#749

- Status: consensus_reached
- Outcome: consensus
- Duration: 694.9s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 230.0 | codex | 5.0 | 0.0 | 0.0 | 213.0 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 8261.6 | cc | 54.4 | 20.0 | 10.5 | 7850.8 |


### chequer-io/deck#748

- Status: consensus_reached
- Outcome: consensus
- Duration: 1016.5s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 106.4 | codex | 1.3 | 0.0 | 0.0 | 72.2 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#144

- Status: consensus_reached
- Outcome: consensus
- Duration: 515.8s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 155.5 | codex | 0.8 | 0.1 | 0.0 | 154.5 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#142

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Duration: 2138.7s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 4417.7 | cc | 9.6 | 15.2 | 13.9 | 3987.3 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/deck#745

- Status: consensus_reached
- Outcome: consensus
- Duration: 1954.4s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 277.7 | codex | 4.7 | 0.1 | 0.0 | 268.0 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 212.5 | codex | 3.9 | 0.0 | 0.0 | 208.6 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/deck#744

- Status: failed
- Outcome: error
- Duration: 757.4s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 169.1 | codex | 1.1 | 0.0 | 0.0 | 168.0 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 152.5 | codex | 2.2 | 0.0 | 0.0 | 150.3 |
| step2_cross_review | 4618.7 | cc | 6.4 | 28.4 | 10.2 | 3625.2 |


### jk-kim0/skills-jk#141

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Duration: 3544.3s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### querypie/querypie-docs#962

- Status: consensus_reached
- Outcome: consensus
- Duration: 2119.7s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 144.5 | codex | 1.6 | 0.8 | 0.0 | 141.3 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 126.6 | codex | 1.6 | 0.1 | 0.0 | 124.5 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 157.1 | codex | 1.5 | 0.3 | 0.0 | 154.5 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 100.5 | codex | 1.2 | 0.2 | 0.0 | 98.1 |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 132.7 | codex | 0.7 | 0.2 | 0.0 | 130.6 |


### querypie/querypie-docs#961

- Status: consensus_reached
- Outcome: consensus
- Duration: 1514.0s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 121.1 | codex | 4.6 | 0.0 | 0.0 | 116.4 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 177.4 | codex | 1.6 | 0.3 | 0.0 | 174.7 |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 126.7 | codex | 2.3 | 0.7 | 0.0 | 122.6 |


### jk-kim0/skills-jk#137

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Duration: 2795.6s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 4629.6 | cc | 1.8 | 20.0 | 10.7 | 3997.4 |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#135

- Status: consensus_reached
- Outcome: consensus
- Duration: 1865.4s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step1_lead_review | 222.9 | codex | 2.1 | 0.0 | 0.0 | 220.0 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 2810.9 | cc | 0.7 | 12.4 | 12.8 | 2510.0 |


### jk-kim0/skills-jk#134

- Status: consensus_reached
- Outcome: consensus
- Duration: 211.3s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 4172.0 | cc | 116.4 | 29.2 | 26.4 | 3776.5 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### querypie/querypie-docs#958

- Status: consensus_reached
- Outcome: consensus
- Duration: 5573.1s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/deck#734

- Status: consensus_reached
- Outcome: consensus
- Duration: 229.7s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/querypie-mono#15924

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Duration: 12112.1s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 171.1 | codex | 9.0 | 1.0 | 0.0 | 161.1 |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### querypie/querypie-docs#957

- Status: consensus_reached
- Outcome: consensus
- Duration: 1538.1s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 148.5 | codex | 2.1 | 0.2 | 0.0 | 144.8 |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### chequer-io/deck#735

- Status: consensus_reached
- Outcome: consensus
- Duration: 2029.0s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| step2_cross_review | 1493.1 | cc | 6.6 | 6.7 | 8.7 | 913.7 |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |


### jk-kim0/skills-jk#131

- Status: max_rounds_exceeded
- Outcome: no_consensus
- Duration: 29548.5s

#### Round 1

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 2

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 3

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 4

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 5

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 6

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 7

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 8

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 9

- Lead agent: codex
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |

#### Round 10

- Lead agent: cc
- Duration: Nones

| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| (no step-level data) |  |  |  |  |  |  |
