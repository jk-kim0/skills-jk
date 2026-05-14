# `/t/plans` source-backed widget parity failure

Session context:
- User compared `https://stage.querypie.ai/t/plans` / PR 504 preview against `../corp-web-app` plans implementation and reported many remaining detailed UI differences.
- The upstream source existed in `../corp-web-app/src/app/ja/plans/page.tsx` plus widget components/CSS under:
  - `../corp-web-app/src/components/widget/pricing/{pricing,product,plan-card}.*`
  - `../corp-web-app/src/components/widget/compare-table/*`
- PR 504 improved broad shape but was still unsatisfactory because it rebuilt the widget with local Tailwind primitives instead of preserving the upstream widget contract.

Root cause pattern:
- `/ja/plans` is a widget / application-contract page, not a normal static marketing page.
- Text parity and route-local JSX are insufficient for widget pages.
- A manually translated Tailwind implementation can pass structure tests while losing button chrome, icon rendering, type scale, tab underline behavior, table overflow/padding, row heights, and root-rem/final-pixel details.

Concrete evidence after PR 504:
- PR preview root: `16px`; live root: `15px`.
- Preview plan title: `26px / 34px`; live computed title: about `24.375px / 31.875px` because upstream uses a 15px root.
- Preview button used text plus `↗`; upstream uses the real `ButtonLink` component and icon wrapper.
- Preview table wrapper started around left `80px`; live table started around left `40px` inside its own overflow wrapper.
- Preview first table row was about `64px`; live first row was about `60px`.

Required workflow for future source-backed widget migrations:
1. Classify the page before coding: static marketing vs widget/application-contract.
2. If widget and upstream source exists, inspect the full upstream component chain and CSS modules before creating local primitives.
3. Prefer a direct-port or compatibility-layer strategy over a Tailwind approximation.
4. If direct port is rejected, explicitly choose a measured-rebuild strategy and collect browser geometry/computed-style anchors before declaring parity.
5. Add tests that defend widget UI contracts, not only route-local copy ownership.
6. Report remaining deltas honestly; do not call the page aligned from source-only checks.

Issue created from this session:
- `querypie/corp-web-japan` issue 505: `Investigate source-backed plans widget parity gap`
