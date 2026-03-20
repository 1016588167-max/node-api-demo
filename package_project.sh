#!/usr/bin/env bash
set -euo pipefail

OUT="pdf-excel-autofill-project.zip"
zip -r "$OUT" README.md pdf_to_excel_app.py requirements.txt package_project.sh
printf 'Created %s\n' "$OUT"
