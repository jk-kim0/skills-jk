---
name: github-issue-markdown-link-safety
description: Prevent accidental GitHub issue references when writing issue bodies that mention numbered content IDs like #24 or #30.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, issues, markdown, linking]
    related_skills: [github-issues, github-pr-body-file-safety]
---

# GitHub issue markdown link safety

Use this when writing or editing a GitHub issue body that mentions numbered documents, posts, whitepapers, PRs, or routes.

## Problem
GitHub auto-links bare tokens like `#24` and `#30` as repository issue references.

This is wrong when the text actually means:
- a whitepaper number
- a content ID
- a route segment
- any other non-issue numeric identifier

## Safe rules

1. Do not leave bare `#24` / `#30` in final issue copy unless you intentionally mean issue references.
2. Prefer plain text such as `Whitepaper 24` or `whitepaper ID 24`.
3. Best option: use explicit markdown links to the real target URL.
4. For PR references, also prefer explicit markdown links when clarity matters.

## Safe examples

Instead of:

```md
- Whitepaper #24
- Whitepaper #30
```

Use:

```md
- [Whitepaper 24](https://querypie.ai/whitepapers/24/ai-transformation-japan)
- [Whitepaper 30](https://querypie.ai/whitepapers/30/saas-end-or-evolution)
```

For local article paths:

```md
- Local article: [`/whitepapers/24/ai-transformation-japan`](https://querypie.ai/whitepapers/24/ai-transformation-japan)
```

For external targets:

```md
- External download CTA target: [querypie.com download page](https://www.querypie.com/ja/features/documentation/white-paper/24/ai-transformation-japan/download)
```

For PR references:

```md
- [PR #159](https://github.com/querypie/corp-web-japan/pull/159)
```

## Quick checklist
- scan the body for bare `#<number>` tokens
- decide whether each one is a real issue reference
- replace non-issue references with plain text or explicit markdown links
- verify the rendered issue body after editing

## When this matters most
- migration audits
- content inventory issues
- documentation issues that mention numbered assets/posts
- PR/issue bodies mixing GitHub references with content IDs
