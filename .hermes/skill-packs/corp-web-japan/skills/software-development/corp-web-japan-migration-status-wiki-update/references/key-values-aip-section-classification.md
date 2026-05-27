# Key values page classification

Session learning from corp-web-japan migration-status/replacement audits.

## Finding

`https://www.querypie.com/ja/key-values` looks like a standalone live URL, but its shipped content is the AIP value-card section:

- `成果にこだわるエンタープライズAI`
- `AI導入を、ワンストップで実現する３つの価値`
- `従量課金型のAIモデル`
- `統合型AIゲートウェイ`
- `AI専門家伴走サービス`

## Source evidence pattern

Use all three checks before classifying it as a migration blocker:

1. `corp-web-app`
   - `../corp-web-app/src/app/[locale]/key-values/page.tsx` allows only JA and renders `page.ja`.
   - `../corp-web-app/src/app/[locale]/key-values/page.ja.tsx` renders `IntroducingQueryPie` with AIP-related items and links to AIP subpages.
2. `corp-web-contents`
   - no dedicated `key-values` MDX/page content source was found.
   - This is an app-level section route, not an authored standalone content page.
3. `corp-web-japan` latest main
   - the same copy can be covered by the AIP page value section, e.g. `src/app/platforms/aip/page.tsx` around the `AipValueSection`.

## Classification rule

When the local AIP public page already includes the same value-card section, classify `/ja/key-values` as **covered by the AIP introduction page section**, not as a required standalone local public page.

Do not automatically add a new `/key-values` local page. Treat any decision to preserve or redirect the old exact URL as a separate route-policy/redirect question, not as a migration-completeness blocker.
