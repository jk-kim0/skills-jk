---
name: check-deployment
description: www.querypie.com (corp-web-app) 배포 버전 확인 방법
---

# 배포 버전 확인

## 엔드포인트

```
https://www.querypie.com/build-info.json
```

## 응답 형식

```json
{
  "commitSha": "ce1bd8fb4bb1dd1aee53c99598c9922230c083bf",
  "commitTitle": "fix(wiki): Confluence 리다이렉트 URL 경로 오류 수정 및 301 전환 (#581)",
  "commitAuthor": "JK",
  "commitDate": "2026-02-07 13:50:08 +0900",
  "branch": "master",
  "buildTime": "2026-02-07T04:58:36.257Z",
  "version": "1.0.0",
  "environment": "production"
}
```

## 필드 설명

| 필드 | 설명 |
|------|------|
| `commitSha` | 배포된 git commit SHA (full) |
| `commitTitle` | 커밋 메시지 제목 |
| `commitAuthor` | 커밋 작성자 |
| `commitDate` | 커밋 일시 |
| `branch` | 빌드 시 브랜치 (production은 `master`) |
| `buildTime` | 빌드 실행 시각 (UTC) |
| `environment` | `production` / `development` |

## 확인 명령어

```bash
curl -s https://www.querypie.com/build-info.json | python3 -m json.tool
```

## 구현 위치

- 생성 스크립트: `corp-web-app/scripts/generate-build-info.js`
- 출력 파일: `corp-web-app/public/build-info.json`
- `npm run build` 시 자동 생성됨
