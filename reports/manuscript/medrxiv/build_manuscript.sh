#!/bin/bash
# Build the medRxiv manuscript: Word (.docx) via pandoc and the style template, PDF via pandoc HTML + headless Chrome.
# Usage (from the project root): bash reports/manuscript/medrxiv/build_manuscript.sh
# Figures are drawn first: Rscript R/manuscript_figures_design.R; Rscript R/manuscript_figures.R;
# Rscript R/manuscript_figures_results.R
set -euo pipefail
cd "$(dirname "$0")"
PANDOC=/opt/anaconda3/bin/pandoc
CHROME="/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
[ -x "$CHROME" ] || CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

python3 make_reference_docx.py
"$PANDOC" MANUSCRIPT_medRxiv_v1.md -f markdown -t docx --reference-doc=reference.docx --resource-path=. \
  -o MANUSCRIPT_medRxiv_v1.docx
"$PANDOC" MANUSCRIPT_medRxiv_v1.md -f markdown -t html5 -s --embed-resources --css=manuscript_print.css \
  -M document-css=false --resource-path=. -o "$TMP/manuscript.html"
"$CHROME" --headless --disable-gpu --no-first-run --user-data-dir="$TMP/profile" --no-pdf-header-footer \
  --print-to-pdf="$PWD/MANUSCRIPT_medRxiv_v1.pdf" "file://$TMP/manuscript.html" 2>/dev/null
echo "built MANUSCRIPT_medRxiv_v1.docx and MANUSCRIPT_medRxiv_v1.pdf"
