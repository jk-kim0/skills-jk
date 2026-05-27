# /about-us parity pitfalls

## CTA interpretation pitfall

Do not treat every live-vs-preview CTA width delta as a preview defect.

Observed case:
- live `/ja/company/about-us`
  - outer CTA section width: 1280
  - inner content width: 841
  - heading width: 841
  - button width: 179
  - root font-size: 15px
- stage `/t/about-us`
  - outer CTA section width: 1280
  - inner content width: 1200
  - heading width: 1200
  - button width: 191
  - root font-size: 16px

Interpretation rule:
- This proves a numeric difference.
- It does NOT by itself prove the preview is wrong.
- First consider whether the live page is using an older/narrower one-off implementation while the preview is using the repo's shared CTA primitive and shared 16px-root system.
- Report this as `difference from live, but not clearly a defect` unless there is stronger evidence.

## Team-card measurement pitfall

Do not assume team cards are uniform on the live page.
Measure each person individually.

Observed live widths:
- Brant Hwang: 264
- Paul Hong: 242
- Sam Kim: 320
- Jake Im: 264
- Kris Park: 242
- Keizo Arinobu: 320

Observed stage widths:
- all six cards: 320

Interpretation rule:
- Report the mixed live widths as a factual rendering result.
- Then separately decide whether the task is:
  - strict live parity, or
  - preserving a cleaner uniform-grid design in preview/stage.
- Do not collapse those into one judgment.
