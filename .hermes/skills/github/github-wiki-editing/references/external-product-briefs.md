# External product briefs for GitHub wiki pages

Use this reference when a wiki page should summarize an external product or website, especially for early product planning or competitive/reference research.

## Recommended investigation flow

1. Preserve the user's requested wiki page name exactly.
   - A request like `myuser.com` should become `myuser.com.md` unless the user asks for a different title.

2. Research the live product, not the local repository.
   - Start with the public landing page and linked pages.
   - Capture product positioning, target customer, core use cases, feature list, apparent workflow, pricing/plans, and UI structure.
   - If pages are dynamic, use a browser/rendering pass rather than relying only on raw HTML.

3. Separate observed facts from interpretation.
   - Use wording such as “관찰됨”, “추정”, “확인되지 않음” when a behavior is inferred from public pages.
   - Do not present hidden implementation details, data model, or internal workflow as fact unless the site exposes them.

4. Include a source note.
   - List visited URLs or a short “참고 URL” section.
   - Mention if a linked case study, docs page, or pricing page was unavailable/404 at the time of review.

5. Publish through the wiki git repository.
   - Prepare the markdown locally even if the wiki remote is not yet materialized.
   - If `hasWikiEnabled` is true but `.wiki.git` returns `Repository not found`, treat it as an uninitialized wiki state. Retry after the wiki repo is created, then fetch/rebase and push the prepared page.
   - For private wikis, verify by recloning or fetching the wiki git repo; web/curl checks can show 404 even after a successful push.

## Suggested document structure

```md
# <product/domain>

## 요약
- 제품 포지셔닝과 한 줄 설명
- 주요 대상 고객

## 핵심 기능
- 기능별 bullet list

## 작동 방식
1. 사용자가 시작하는 단계
2. 시스템이 처리하는 단계
3. 결과/출력/후속 액션

## UI 구성
- 랜딩 페이지/대시보드/설정/결과 화면 등 공개적으로 관찰 가능한 UI

## 가격/플랜
- 공개 가격 또는 플랜 구분
- 확인되지 않은 항목은 명시

## 관찰된 기술/트래킹 요소
- 공개 HTML/스크립트/렌더링에서 관찰된 요소만 기록

## 불명확한 부분
- 로그인 뒤 기능, 내부 workflow, API, 데이터 모델 등 확인 불가 항목

## 참고 URL
- <url>
```

## Quality checklist

- Requested wiki filename/page slug preserved
- Public-site claims are sourced or labeled as inference
- Product functions, operation model, and UI are all covered
- Unavailable pages or unverified assumptions are explicitly called out
- Wiki push is verified from the wiki git repository, not only by browser/curl
