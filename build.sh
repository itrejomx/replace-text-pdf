#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Error: venv not found. Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

pip install -q pyinstaller>=6.0.0

pyinstaller --onefile --noconsole \
  --hidden-import fitz \
  --hidden-import customtkinter \
  --collect-all customtkinter \
  --name "PDFTextReplacer" \
  main.py

echo "Build complete: dist/PDFTextReplacer"
