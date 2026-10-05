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
  if ! { curl -fsSL -o "assets/fonts/Fredoka[wdth,wght].ttf" \
           "https://github.com/google/fonts/raw/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf" &&
         curl -fsSL -o "assets/fonts/OFL.txt" "https://github.com/google/fonts/raw/main/ofl/fredoka/OFL.txt"; }; then
    # raw.githubusercontent can be blocked in cloud sessions: fetch just that folder with git instead
    tmp="$(mktemp -d)"
    GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts "$tmp/fonts"
    git -C "$tmp/fonts" sparse-checkout set ofl/fredoka
    cp "$tmp/fonts/ofl/fredoka/Fredoka[wdth,wght].ttf" "$tmp/fonts/ofl/fredoka/OFL.txt" assets/fonts/
    rm -rf "$tmp"
  fi
fi
python3 -c "import paperlib; print('font:', paperlib.ROUND_FONT)"
echo "setup ok"
