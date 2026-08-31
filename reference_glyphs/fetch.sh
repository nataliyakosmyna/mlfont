#!/bin/bash
set -e
cd "$(dirname "$0")"
SLUGS=(
  affective-computing biomechatronics camera-culture
  center-for-constructive-communication city-science conformable-decoders
  critical-matter cyborg-psychology fluid-interfaces future-sketches
  human-dynamics lifelong-kindergarten molecular-machines
  multisensory-intelligence nano-cybernetic-biotrek opera-of-the-future
  personal-robots responsive-environments sculpting-evolution
  signal-kinetics social-algorithms space-enabled tangible-media
  viral-communications
)
for s in "${SLUGS[@]}"; do
  url="https://www.media.mit.edu/group-glyphs/$s/full/"
  out="$s.glyph"
  curl -sSL -A "Mozilla/5.0" -o "$out" "$url"
  ct=$(file -b --mime-type "$out")
  size=$(wc -c <"$out")
  # rename based on detected type
  case "$ct" in
    image/svg+xml) mv "$out" "$s.svg";;
    image/png)     mv "$out" "$s.png";;
    image/jpeg)    mv "$out" "$s.jpg";;
    image/gif)     mv "$out" "$s.gif";;
    *) ext="bin";;
  esac
  printf "%-40s %-15s %s bytes\n" "$s" "$ct" "$size"
done