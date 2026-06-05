# Japanese news company-name and press-contact copy

Use this reference when editing `corp-web-app` Japanese news MDX, especially `newsType: press-release` records and `docs/news.md`.

## Durable rules learned

- In Japanese news articles, when `QueryPie` refers to the company, write `QueryPie AI`.
  - This includes frontmatter `title` and `description` when the title/description refers to the company.
  - Keep product/platform names unchanged, such as `QueryPie AIP` and `QueryPie AI Platform`.
- For Japanese press releases, homepage / URL lines for QueryPie should use exactly:
  - `[https://querypie.ai](https://querypie.ai)`
- Apply the Japanese homepage rule to both:
  - current standardized `## メディアお問い合わせ` sections
  - older Japanese `### **【本件に関するお問い合わせ先】**` sections
- Historical Japanese press releases may also have a `会社情報` QueryPie URL line such as `www.querypie.ai/ja`; normalize QueryPie-owned URL lines there to `https://querypie.ai` as well.
- Do not change unrelated third-party URLs in the same article, such as partner company URLs.
- When updating `docs/news.md`, change only the Japanese press-release example unless the task explicitly asks for other locales. Keep English/Korean examples unchanged.

## Recommended verification

1. Search all Japanese news MDX:
   - `src/content/news/*.ja.mdx`
2. Identify all Japanese media-contact headings:
   - `メディアお問い合わせ`
   - `本件に関するお問い合わせ先`
3. Verify each section has a QueryPie Website line using exactly `[https://querypie.ai](https://querypie.ai)`.
4. Verify `docs/news.md` Japanese example uses `https://querypie.ai`, while English/Korean examples remain at their intended URLs unless explicitly in scope.
5. For company-name cleanup, verify no standalone company-reference `QueryPie` remains outside approved product names (`QueryPie AIP`, `QueryPie AI Platform`).
