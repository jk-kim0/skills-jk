# corp-web-japan live render parity references

Use these reference notes for concrete page-family pitfalls that are too detailed for the main SKILL.md.

Maintenance note: the main `SKILL.md` for this umbrella is currently near/over the `skill_manage` size limit, so prefer adding concrete page-family lessons here under `references/` and keeping the main body compact when it is next edited.

- `acp-child-faq-live-css-chain.md` — ACP child-page FAQ parity: `corp-web-contents` only declares `WithFAQBottomLayout`; inspect `corp-web-app` `FAQBottom` / `QnA` components and CSS modules for the real UI contract. Use this before editing FAQ UI on `/platforms/acp/*` child pages.
- `sibling-page-parity.md` — comparing one local/stage sibling page against another local/stage sibling page.
- `source-backed-widget-parity.md` — when the live page is driven by an upstream widget/component contract rather than plain static content.
- `plans-widget-source-contract-parity.md` — source-backed pricing/plans widget parity pitfalls.
