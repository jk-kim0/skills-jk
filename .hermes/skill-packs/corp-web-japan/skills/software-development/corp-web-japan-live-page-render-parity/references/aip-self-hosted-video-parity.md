# AIP self-hosted video parity notes

Use these notes when replacing or demoing the AIP hero YouTube iframe with a self-hosted/native video player in corp-web-japan.

## Stage reference measured in browser

Reference page: `https://stage.querypie.ai/t/platforms/aip`

The AIP hero video surface is intentionally plain, not card-like:

- outer wrapper: `relative mx-auto w-full max-w-[1024px]`
- frame: `relative aspect-video w-full`
- rendered desktop geometry observed at 1631px viewport: `1024 x 576`
- corner radius: `0px`
- box shadow: `none`
- thumbnail: `/services/aip/aip-video-thumb-jp.png`
- behavior: poster-first overlay with centered play icon, then playback

Do not preserve rounded demo chrome such as `rounded-[28px]` or heavy shadows when the user asks to match the AIP hero.

## Downloading the YouTube source

Video id used by the AIP hero at the time of the session: `nJGSCd6itUE`.

Default `yt-dlp` can fail with HTTP 403 because YouTube may force SABR/PO-token behavior for some clients. If the first command fails, retry with Android + web client extraction:

```bash
python3 -m pip install --user --quiet yt-dlp
python3 -m yt_dlp \
  --extractor-args 'youtube:player_client=android,web' \
  -f 'bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4][height<=1080]/best[height<=1080]' \
  --merge-output-format mp4 \
  -o 'public/internal/video/querypie-aip-hero-youtube.%(ext)s' \
  'https://www.youtube.com/watch?v=nJGSCd6itUE'
```

Verify the output before committing:

```bash
ffprobe -v error \
  -show_entries format=duration,size:stream=codec_name,width,height,avg_frame_rate \
  -of json public/internal/video/querypie-aip-hero-youtube.mp4
```

Session result: the fallback format downloaded a 640x360 H.264/AAC MP4, about 20 MiB, duration about 617 seconds.

## PR/workflow notes

- If the original internal-video demo PR has already merged, do not recreate its old branch. Start a new latest-main follow-up branch and PR.
- Keep production object storage/CDN/HLS rollout explicitly out of this demo PR unless the user changes scope.
- Tests should assert both the new downloaded video file and the removal of any temporary synthetic demo clip/poster.
