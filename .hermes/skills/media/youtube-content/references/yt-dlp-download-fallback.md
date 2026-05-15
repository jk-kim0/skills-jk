# yt-dlp media download fallback

Use this when a user asks to download a YouTube video asset (not just transcript text) for local demo/prototype work.

## Basic install

```bash
python3 -m pip install --user --quiet yt-dlp
python3 -m yt_dlp --version
```

## MP4 download command

```bash
python3 -m yt_dlp \
  -f 'bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4][height<=1080]/best[height<=1080]' \
  --merge-output-format mp4 \
  -o 'public/internal/video/<name>.%(ext)s' \
  'https://www.youtube.com/watch?v=<VIDEO_ID>'
```

## 403 fallback

If the default download fails with `HTTP Error 403: Forbidden` and warnings about SABR, missing URLs, or PO tokens, retry with Android + web player clients:

```bash
python3 -m yt_dlp \
  --extractor-args 'youtube:player_client=android,web' \
  -f 'bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4][height<=1080]/best[height<=1080]' \
  --merge-output-format mp4 \
  -o 'public/internal/video/<name>.%(ext)s' \
  'https://www.youtube.com/watch?v=<VIDEO_ID>'
```

This fallback succeeded for the corp-web-japan AIP hero video `nJGSCd6itUE` after the default client returned 403.

## Verify before committing

```bash
ffprobe -v error \
  -show_entries format=duration,size:stream=codec_name,width,height,avg_frame_rate \
  -of json public/internal/video/<name>.mp4
```

For repo work, commit only when redistribution/storage is within the requested scope. Prefer keeping long-term production video delivery on object storage + CDN rather than repo `public/` unless the user explicitly asks for a temporary public-directory demo.
