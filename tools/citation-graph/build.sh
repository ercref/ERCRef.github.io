#!/bin/sh
# Rebuild the homepage (index.html) from the latest EIPs and ERCs repositories.
# Needs: git, curl, python3, and sips (macOS) to resize avatars.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
WORK=${WORK:-"$HERE/.work"}
mkdir -p "$WORK/src" "$WORK/raw" "$WORK/av"

for r in EIPs ERCs; do
  dir=$(echo "$r" | tr a-z A-Z)
  if [ -d "$WORK/src/$r" ]; then git -C "$WORK/src/$r" pull -q --depth 1
  else git clone -q --depth 1 --filter=blob:none --sparse "https://github.com/ethereum/$r.git" "$WORK/src/$r"
       git -C "$WORK/src/$r" sparse-checkout set "$dir"; fi
done

DATE=$(date -u +%Y-%m-%d)
# First pass writes handles.txt; then fetch avatars; second pass embeds them.
python3 -I "$HERE/export_graph.py" "$WORK/src" "$WORK" "$WORK/av" "$ROOT/index.html" "$DATE"
while read -r h; do
  [ -f "$WORK/av/$h.jpg" ] && continue
  curl -sfL -m 20 -o "$WORK/raw/$h" "https://github.com/$h.png?size=64" || { echo "no avatar: $h"; continue; }
  sips -s format jpeg -s formatOptions 70 -z 64 64 "$WORK/raw/$h" --out "$WORK/av/$h.jpg" >/dev/null
done < "$WORK/handles.txt"
python3 -I "$HERE/export_graph.py" "$WORK/src" "$WORK" "$WORK/av" "$ROOT/index.html" "$DATE"
