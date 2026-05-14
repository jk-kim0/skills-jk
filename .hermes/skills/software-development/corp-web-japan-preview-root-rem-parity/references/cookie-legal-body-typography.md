# Cookie/legal body typography measurement

Session context: user asked to compare body typography between:
- `https://stage.querypie.ai/t/cookie-preference`
- `https://www.querypie.com/ja/cookie-preference`

Measured in Chrome DevTools computed styles.

## Root sizes

Both pages reported:
- `html` root font size: `16px`
- `body` font size: `16px`

However the stage implementation used many values that match 15px-root computed output copied into a 16px-root site.

## Key measured values

| Element | Stage computed | Live computed | 15px-root token reconstruction |
|---|---:|---:|---:|
| H1 | `56.25px / 67.5px` | `60px / 72px` | `3.75rem / 4.5rem` => `60px / 72px` at 16px root |
| category label | `18.75px / 26.25px` | `20px / 28px` | `1.25rem / 1.75rem` => `20px / 28px` at 16px root |
| category body | `15px / 24.375px` | `16px / 26px` | `1rem / 1.625rem` => `16px / 26px` at 16px root |
| live intro/lead | stage `15px / 24.375px` | live `18px / 28px` | treat as lead, not default body |

## Legal default recommendation chosen by user

For legal pages' default body paragraphs:
- `16px / 26px`
- `text-slate-600`

Implementation scope used in corp-web-japan:
- update `src/components/sections/legal/document.tsx`
- change the shared `legalDocumentBodyClassName` base body text
- change `p` paragraph rules
- change `blockquote p` rules
- leave headings, lists, tables, and route-specific cookie components unchanged unless requested

## Pitfall

Do not interpret `15px` on the preview page as the desired legal body size when the values clearly match 15px-root computed output. Reconstruct the 16px-root token intent first, then apply only the user's chosen scope.
