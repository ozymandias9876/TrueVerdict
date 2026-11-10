#!/bin/bash
set -e

echo "=== RENDER STILL FRAMES FOR AUDIT ==="
npx remotion still TrueVerdictLaunch-16x9 out/frame-45.png --frame=45
npx remotion still TrueVerdictLaunch-16x9 out/frame-140.png --frame=140
npx remotion still TrueVerdictLaunch-16x9 out/frame-280.png --frame=280
npx remotion still TrueVerdictLaunch-16x9 out/frame-420.png --frame=420
npx remotion still TrueVerdictLaunch-16x9 out/frame-540.png --frame=540

echo "=== RENDER FULL 20s VIDEO (1080p MP4) ==="
npx remotion render TrueVerdictLaunch-16x9 out/TrueVerdict-Launch.mp4 --codec=h264 --crf=18

echo "=== GENERATE HIGH QUALITY GIF PREVIEW ==="
ffmpeg -y -i out/TrueVerdict-Launch.mp4 \
  -vf "fps=12,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" \
  out/TrueVerdict-Launch.gif

echo "=== COMPLETE ==="
