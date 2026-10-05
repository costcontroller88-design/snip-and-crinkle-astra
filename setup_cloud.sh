#!/usr/bin/env bash
# One-time setup on a Linux (cloud) machine: ffmpeg, Python libs, and the Fredoka font (SIL OFL).
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v ffmpeg >/dev/null; then
  if sudo -n true 2>/dev/null; then SUDO=sudo; else SUDO=""; fi
  $SUDO apt-get update -y && $SUDO apt-get install -y ffmpeg
fi
python3 -m pip install --quiet pillow numpy
mkdir -p assets/fonts
if [ ! -f "assets/fonts/Fredoka[wdth,wght].ttf" ]; then
  curl -fsSL -o "assets/fonts/Fredoka[wdth,wght].ttf" \
    "https://github.com/google/fonts/raw/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf"
  curl -fsSL -o "assets/fonts/OFL.txt" "https://github.com/google/fonts/raw/main/ofl/fredoka/OFL.txt"
fi
python3 -c "import paperlib; print('font:', paperlib.ROUND_FONT)"
echo "setup ok"
