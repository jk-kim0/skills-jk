# Corp-web-app certifications page parity audit

Session: 2026-05-17

## URLs compared
- Production: https://www.querypie.com/ko/company/certifications
- Stage:      https://stage.querypie.com/ko/company/certifications

## Results

### 1. Page title prefix missing (BUG)
- **Visually**: Browser tab showed "Certifications" instead of "QueryPie AI Certifications"
- **Root cause**: During route-local migration, `export const metadata = { title: 'Certifications' }`
  lost the site prefix that was previously prepended automatically by the dynamic page framework.
- **Files fixed**:
  - `src/app/[locale]/company/certifications/page.ko.tsx`
  - `src/app/[locale]/company/certifications/page.en.tsx`
  - `src/app/[locale]/company/certifications/page.ja.tsx`
- **Fix**: `title: 'QueryPie AI Certifications'` (EN/KO), `title: 'QueryPie AI 認証'` (JA)
- **Verification**: Screenshot reload confirmed tab title matches production.

### 2. ISMS-P description duplicated from ISO 22301 (BUG)
- **Visually**: ISMS-P certification card showed "Business Continuity / Management" (wrong)
- **Root cause**: Copy-paste error during content migration — ISO 22301's description was reused
  for ISMS-P instead of its own description.
- **File fixed**: `src/app/[locale]/company/certifications/certification-items.ts`
- **Fix**: `description: ['Information Security Management', 'System for Privacy']`
- **Verification**: Screenshot reload confirmed text matches production.

### 3. Header shadow, card grid, footer (NO ISSUE)
- Layout, spacing, visual styling matched production.
- No CSS or component changes needed.

## Key source files for this route
```
src/app/[locale]/company/certifications/
├── page.tsx                       → locale wrapper, params only
├── page.en.tsx                    → metadata + hero (EN)
├── page.ko.tsx                    → metadata + hero (KO)
├── page.ja.tsx                    → metadata + hero (JA)
└── certification-items.ts         → card data array (3 certifications)

src/components/widget/certifications/
├── certifications.component.tsx   → section layout
└── certifications.module.css      → card grid styling
```

## Lesson: common migration regression
When migrating from dynamic/blob-driven pages to static `page.tsx` files with explicit
`export const metadata`, the site-wide title prefix is easy to miss because the previous
dynamic framework may have concatenated it automatically.

## PR opened
- #716 `fix/certifications-title`
- 4 files changed: 3 locale metadata titles + 1 data description fix.
