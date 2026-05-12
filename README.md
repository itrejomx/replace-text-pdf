# PDF Text Replacer

Desktop app to find and replace text across multiple PDF files while preserving the original font, size, color, and baseline position of the replaced text.

## Running from source

**Requirements:** Python 3.10+

```bash
# 1. Clone the repo
git clone https://github.com/itrejomx/replace-text-pdf.git
cd replace-text-pdf

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
python main.py
```

## Building a native app on macOS

Run the included build script — it creates a single-file binary at `dist/PDFTextReplacer`:

```bash
# Make sure your venv exists with dependencies installed (see above)
./build.sh
```

The output binary at `dist/PDFTextReplacer` can be moved anywhere and run without Python installed.

To wrap it as a `.app` bundle you can put in `/Applications`, use `--windowed` and `--name` with PyInstaller directly:

```bash
source venv/bin/activate
pip install pyinstaller

pyinstaller --onefile --windowed \
  --hidden-import fitz \
  --hidden-import customtkinter \
  --collect-all customtkinter \
  --name "PDFTextReplacer" \
  main.py
```

The `.app` bundle will be at `dist/PDFTextReplacer.app`.

## Building an EXE on Windows

Run the following in a Command Prompt or PowerShell from the project folder:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onefile --noconsole ^
  --hidden-import fitz ^
  --hidden-import customtkinter ^
  --collect-all customtkinter ^
  --name "PDFTextReplacer" ^
  main.py
```

The executable will be at `dist\PDFTextReplacer.exe`.

> **Note:** PyInstaller builds are platform-specific. You must run the Windows build on a Windows machine and the macOS build on a Mac.
