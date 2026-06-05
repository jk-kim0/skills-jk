# News detail body-to-footer gap measurement

Use this reference when comparing publication/news detail pages where the user asks for the spacing between the article body and the footer.

## Measurement contract

Measure more than one landmark so the reported gap is unambiguous:

- `bodyBottomToFooterTop`: actual article/body content wrapper bottom -> footer top. This is the visible "본문 끝 -> footer 시작" gap most users mean.
- `bodyPaddingWrapperBottomToFooterTop`: parent padding wrapper bottom -> footer top. This excludes the body wrapper's bottom padding.
- `contentColumnBottomToFooterTop`: main content column bottom -> footer top.
- `layoutRowBottomToFooterTop`: two-column article row bottom -> footer top.
- `newsPostBottomToFooterTop`: whole article section bottom -> footer top. This may be `0px` even when the visible body-to-footer gap is large, because the section's bottom padding is inside the section.
- `newsPostBottomMinusBodyBottom`: total vertical space inside the article section after the body wrapper.

Report the exact measurement basis before giving numbers. If the user simply says "본문과 footer 사이", prefer `bodyBottomToFooterTop`, and include the section/footer boundary value if it explains the layout.

## DOM selection pattern

For corp-web-app news detail pages, use:

- body: `[data-news-body]`
- section: `[data-news-post]`
- footer: `footer, [role="contentinfo"]`

For corp-web-japan/querypie.ai publication detail pages, there may be no `data-news-body`; identify the publication body by the shared `publicationBodyClassName` wrapper and matching article text.

## Example result from live news detail pages

At viewport `1440x1200`, comparing:

- `https://querypie.ai/news/14/mitoco-buddy-official-launch`
- `https://www.querypie.com/ja/news/23/mitoco-buddy-official-launch`

Both rendered:

- actual body bottom -> footer top: `257px`
- body padding wrapper bottom -> footer top: `160px`
- content column bottom -> footer top: `160px`
- whole news/post section bottom -> footer top: `0px`

Interpretation: the visible body-to-footer gap was equal, while the article section itself touched the footer directly. The visible gap came from the body wrapper/column bottom padding plus section bottom padding, not from an external margin between the section and footer.
