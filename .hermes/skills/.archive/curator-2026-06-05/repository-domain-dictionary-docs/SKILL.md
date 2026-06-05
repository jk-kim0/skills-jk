---
name: repository-domain-dictionary-docs
description: Create and maintain repository dictionary/glossary documents that capture general industry terminology separately from repo-specific product concepts or implementation terms.
version: 1.0.0
metadata:
  hermes:
    tags: [documentation, dictionary, glossary, domain-language, repository-docs]
---

# Repository Domain Dictionary Docs

Use this skill when the user asks to create or update a `dictionary`, `glossary`, `terms`, or common-language document under a repository's docs tree, especially when they distinguish general industry terms from repo-defined concepts.

## Goal

Produce a concise, reviewer-friendly reference that helps humans and AI agents use a shared vocabulary without accidentally turning implementation-specific names into general domain language.

## Core distinction

- **Industry dictionary / glossary**: general terms used across a market, domain, profession, or vendor category.
- **Project concept docs**: concepts this repository defines, such as product-specific entities, state machines, database fields, API event names, or implementation decisions.

If the user asks for general terms only, keep repository-specific entities and implementation terms out of the dictionary even if they are relevant to the product.

## Recommended workflow

1. Confirm repo and branch/worktree policy before editing.
2. Inspect existing `docs/` structure and adjacent guidance docs to match naming and tone.
3. Pick a clear English filename, commonly `docs/dictionary.md`, `docs/glossary.md`, or a domain-scoped variant such as `docs/sales-dictionary.md`.
4. Start the document with its purpose and scope.
5. Add a short “작성 지침” / contribution guide near the top so future AI agents can safely extend it.
6. Keep contribution guidelines compact; if the user requests a line limit, verify it explicitly.
7. Organize terms by stable domain categories rather than by implementation screens or database models.
8. For each term, include original term, localized expression if needed, and a short neutral explanation.
9. Avoid vendor-specific claims unless the section is explicitly about common vendor naming style.
10. Commit/push and create or update the PR when repo workflow expects it.

## Suggested document shape

```markdown
# Dictionary

## 문서 용도와 목적

이 문서는 <domain>에서 일반적으로 사용되는 업계 용어를 정리한다. 이 저장소에서 새로 정의한 제품 개념이나 구현 특화 용어를 설명하기 위한 문서가 아니라, 설계와 리뷰에서 공통 언어로 참고하기 위한 용어 사전이다.

## 작성 지침

1. 일반적인 업계 용어만 추가하고, 이 저장소의 구현 세부사항이나 내부 모델명은 넣지 않는다.
2. 용어는 영어 원어, 자연스러운 한국어 표현, 짧은 설명을 함께 적는다.
3. 설명은 특정 벤더나 제품에 종속되지 않도록 중립적으로 작성한다.
4. 같은 의미의 용어가 있으면 중복 항목을 만들기보다 기존 항목에 보조 표현으로 정리한다.
5. 약어는 처음 등장할 때 풀네임을 함께 적는다.

## 1. <Category>

| 영어 | 한국어 | 설명 |
| --- | --- | --- |
| Term | 번역 / 표현 | 짧은 설명. |
```

## Pitfalls

- Do not mix product-specific entity decisions into an industry dictionary. Put those in model/design docs instead.
- Do not turn user-provided rough notes into a long essay; normalize them into tables and short sections.
- Do not over-explain contribution guidelines. They should be actionable and short enough that future agents will actually follow them.
- Do not add speculative terms just because they sound adjacent. If the document is meant to be foundational, prefer common terms the target audience will recognize.
- Be careful with overloaded translations such as “전달됨”: distinguish email delivery from forwarding when both appear.
- For metrics, use “generally” phrasing when formulas differ by product, for example “일반적으로 Open / Delivered”.

## Verification checklist

- The document states its purpose and scope near the top.
- Contribution guidelines are within any requested length limit.
- Terms are general industry terms, not repo-only implementation names.
- Tables have consistent columns and neutral descriptions.
- Filename is English; body language matches repo convention.
- `git status` confirms changes are isolated to the intended worktree/branch.

## References
