# AIP self-hosted hero video replacement pattern

Use this when a corp-web-japan preview/static page currently embeds a YouTube hero video and the goal is to serve the media as QueryPie-owned website media instead of a YouTube iframe.

Observed baseline on `https://stage.querypie.ai/t/platforms/aip`:
- current implementation: `src/components/sections/aip/page.tsx` `AipHeroVideo()`
- current embed: `https://www.youtube.com/embed/nJGSCd6itUE`
- measured stage geometry: wrapper `1024x576`, iframe `1024x576`
- current wrapper classes: `mx-auto w-full max-w-[1024px] overflow-hidden rounded-[12px] shadow-[0_24px_80px_-55px_rgba(15,23,42,0.45)]`
- current inner container: `relative aspect-video w-full bg-black`

Implementation guidance:
1. Keep the existing measured hero wrapper geometry and styling stable unless the user explicitly asks for a layout change.
2. Replace only the inner media implementation (`iframe` -> self-hosted player), not the surrounding hero rhythm.
3. Do not commit large `.mp4` assets into the repo or serve them from generic Vercel-traced `public/` paths when the goal is production/stage hosting.
4. Keep only lightweight poster imagery in the repo, under the route-aligned asset root, e.g. `public/services/aip/hero-video-poster.jpg`.
5. Host the actual video on a QueryPie-owned storage/CDN origin, e.g. `media.querypie.ai/services/aip/...`, then reference it from the page.
6. Prefer HLS (`.m3u8`) with `hls.js` plus MP4 fallback for long-term operation; for a fast first pass, MP4-only is acceptable.
7. Use click-to-play poster-first UX by default:
   - initial poster image
   - centered play button
   - mount/play the video only after interaction
   - `preload="metadata"`, `playsInline`, and normal controls
   - avoid forced sound autoplay unless the user explicitly wants it
8. If captions exist, expose them with a `track` element.

Why this pattern:
- removes YouTube branding, related links, and third-party embed dependence
- avoids putting large binary video assets into git and Vercel deploy artifacts
- preserves the already-approved hero layout while swapping only the media delivery mechanism
- generalizes to ACP/FDE and other preview pages that may later need the same treatment
