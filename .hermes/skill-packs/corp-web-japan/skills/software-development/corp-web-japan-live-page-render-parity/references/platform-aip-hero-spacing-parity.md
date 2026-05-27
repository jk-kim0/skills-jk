# `/t/platforms/aip` hero spacing parity note

Session-specific detail from comparing:
- Stage preview: `https://stage.querypie.ai/t/platforms/aip`
- Live reference: `https://www.querypie.com/ja/solutions/aip`

## Key measurement outcome

The important distinction was absolute hero start offset vs internal hero rhythm.

Measured anchors:
- Stage header height: about `64px`
- Live header height: about `88px`
- Stage `header.bottom -> h1.top`: about `16px`
- Live `header.bottom -> h1.top`: about `80px`
- `h1.bottom -> first paragraph.top`: `20px` on both
- `first paragraph.bottom -> YouTube/media.top`: `80px` on both
- `media.bottom -> first value-card/major section.top`: `120px` on both

Conclusion:
- The stage page's internal hero/body/media rhythm already matched live.
- The mismatch was only the page-family top offset from GNB/header to the hero `h1`.
- Therefore the fix should not touch `AipHeroTitle`, `AipHeroLead`, or hero body/media gap components.

## Implementation lesson

For Platform-family pages, make the first-page/hero top offset a family-level primitive:

```tsx
export function PlatformContentSection(...) { ... }

export function PlatformPageSection({ children }: ChildrenProps) {
  return (
    <PlatformContentSection className="pb-[120px] pt-[120px] lg:pt-[144px]">
      {children}
    </PlatformContentSection>
  );
}

export function PlatformHeroSection({ children }: ChildrenProps) {
  return <PlatformPageSection>{children}</PlatformPageSection>;
}
```

Why this shape matters:
- `PlatformPageSection` mirrors `CompanyPageSection` as the owner of GNB/header-to-content start offset.
- `PlatformContentSection` remains available for later body sections so they do not inherit hero/page-start padding.
- `PlatformHeroSection` becomes a semantic alias/delegator rather than the only place that knows about the page top offset.

## Pitfall

Do not fix a header-to-H1 delta by changing internal hero rhythm if measured intra-hero gaps already match live. That would make the paragraph/media rhythm regress while hiding the real issue: the page starts too close to the GNB.
