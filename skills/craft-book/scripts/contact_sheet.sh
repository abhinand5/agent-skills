#!/bin/sh
# Render every PDF page to PNG and tile them into contact sheets for a visual pass.
#   contact_sheet.sh BOOK.pdf OUTDIR [DPI]
# Look at every sheet, then zoom into any page with a diagram, table, or long equation.
set -eu
pdf=$1
out=$2
dpi=${3:-100}
rm -rf "$out"
mkdir -p "$out"
pdftoppm -png -r "$dpi" "$pdf" "$out/page"
if command -v montage >/dev/null 2>&1; then
  montage "$out"/page-*.png -thumbnail 150x214 -tile 5x4 -geometry +7+7 "$out/contact-%02d.png"
fi
ls "$out" | grep -c '^page-' | sed 's/^/pages rendered: /'
ls "$out"/contact-*.png 2>/dev/null || echo "montage not installed: view page-*.png directly"
