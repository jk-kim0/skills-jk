# News Thumbnail Background Matching

Use this reference when a corp-web-app news/publication thumbnail needs to match the background color of an existing live/reference image.

## Pattern

1. Identify the exact reference image URL or local asset named by the user.
2. Sample the reference image background from stable border/corner pixels, not from the visible foreground artwork.
3. Prefer the most common border color as the thumbnail background color.
   - In the 2026-06 news thumbnail case, the reference PNG border/corner color was RGB(248, 248, 248), i.e. `#F8F8F8`.
4. For SVG thumbnails where the user asks for a full-bleed background without rounded corners:
   - keep one full-canvas `<rect width="..." height="..." fill="#..."/>` as the first visible background layer;
   - remove decorative grid/background paths if they are no longer part of the requested visual;
   - remove card rectangles with `rx`/`ry`, white fills, and strokes that create rounded-rectangle framing.
5. Verify at file level before committing:
   - SVG parses as XML;
   - expected fill color exists;
   - old fill colors and `rx`/`ry` rounded-corner attributes are gone where requested;
   - white card/grid markers are not left behind.

## Lightweight verification snippet

```bash
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
for path in [Path('public/news/25/thumbnail.svg'), Path('public/news/24/thumbnail.svg')]:
    text = path.read_text()
    ET.fromstring(text)
    print(path, {
      'has_target_bg': 'fill="#F8F8F8"' in text,
      'has_rx': ' rx=' in text or 'rx=' in text,
      'has_white_card': 'fill="white"' in text,
    })
PY
```

## Pitfalls

- Do not visually guess the background from a URL when the image is accessible. Sample the pixels.
- If Pillow is unavailable, do not encode that as a durable tool limitation; use another image tool or a small PNG decoder/sampling script for the current task.
- Avoid broad local builds for asset-only SVG edits unless the user asks for them; XML parse plus targeted string checks are usually sufficient.
