#!/usr/bin/env bash
set -e
pyinstaller --onefile --noconsole \
  --hidden-import fitz \
  --name "PDFTextReplacer" \
  main.py
echo "Build complete: dist/PDFTextReplacer"
