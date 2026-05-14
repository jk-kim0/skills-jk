# /certifications mobile gutter audit note

Session context: review of `https://stage.querypie.ai/certifications` after company page primitive commonization. The question was whether `CompanyPageSection` mobile `px-[30px]` is appropriate for a certification card/gallery page, especially around 300px-wide devices.

## Current measured contract

Source at the time:
- `CompanyPageSection`: `px-[30px]`
- `CertificationCard`: `px-8` (`32px` left/right card padding)

Measured on staging with Playwright at mobile viewports:

| Viewport | Outer gutter | Card outer width | Card content width after card padding | Total gutter share |
| --- | ---: | ---: | ---: | ---: |
| 300px | 30px each side | 240px | 176px | 20.0% |
| 320px | 30px each side | 260px | 196px | 18.75% |
| 360px | 30px each side | 300px | 236px | 16.7% |
| 390px | 30px each side | 330px | 266px | 15.4% |

## Aesthetic conclusion

- At 390px, the 30px gutter is acceptable and reads as calm/premium rather than cramped.
- At 360px, it is still mostly acceptable.
- At 300–320px, the 30px gutter becomes visually conservative for a card/gallery page. The card is not broken, but it feels slightly narrow/tall and less like a gallery tile.
- This is not a global company-page defect; text-heavy pages may still benefit from the 30px gutter.

## Concrete wrapping signal

On a 300px viewport:
- 30px gutter leaves the first card at 240px wide and content at 176px.
- Reducing only the outer gutter to 24px increases card width to 252px and content width to 188px.
- In this session, the PCI DSS line `Payment Card Industry Data` changed from wrapping into two lines at 30px to fitting in one line at 24px.

That means the issue is not purely subjective; a small gutter reduction can cross an actual line-wrapping threshold for some certification descriptions.

## Recommendation pattern

Do not change the global `CompanyPageSection` mobile gutter just because `/certifications` is card-heavy.

If implementing a fix:
1. keep the 30px default for general company/text pages;
2. add a narrow named gutter preset or a card-gallery wrapper for `/certifications`-like pages;
3. avoid broad `className`, `contentClassName`, or `contentWidthClassName` escape hatches;
4. consider `24px` as the safest compromise;
5. consider `20px` if the priority is strongest narrow-mobile card/gallery balance at 300px.

Decision guidance:
- `24px`: safest minimal change; keeps the premium company-page tone and improves some wrapping.
- `20px`: best visual balance for 300px card/gallery pages; still not edge-to-edge, but less conservative.
- `16px`: likely too app-like/aggressive for this B2B company-page tone unless explicitly requested.

## Issue/body wording pattern

Useful concise wording for GitHub issues:

> `/certifications`의 30px mobile gutter는 390px 전후의 일반 모바일 폭에서는 acceptable하지만, 300~320px narrow viewport에서는 card/gallery page로서 다소 보수적으로 보인다. 300px 기준 outer gutter 30px은 화면 폭의 20%를 차지하고, card 내부 padding 32px까지 포함하면 실제 card content width가 176px까지 줄어든다. 이 때문에 card가 약간 좁고 길게 보이며, 일부 영문 설명은 line wrapping이 늘어난다. 다만 이는 layout breakage는 아니며, `/about-us`, `/contact-us`, `/news`까지 포함한 `CompanyPageSection` 기본값을 전역으로 바꿀 사안은 아니다. 수정한다면 `/certifications` 같은 card/gallery page에 한정된 named gutter preset 또는 card-gallery wrapper를 도입하는 편이 적절하다. 값은 24px이 가장 안전한 절충안이고, 300px narrow mobile의 card balance만 보면 20px이 가장 자연스럽다.
