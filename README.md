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

---

# PDF Text Replacer — Español

App de escritorio para buscar y reemplazar texto en varios archivos PDF conservando la fuente, tamaño, color y posición original del texto reemplazado.

## Ejecutar desde el código fuente

**Requisitos:** Python 3.10+

```bash
# 1. Clonar el repositorio
git clone https://github.com/itrejomx/replace-text-pdf.git
cd replace-text-pdf

# 2. Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar la app
python main.py
```

## Compilar una app nativa en macOS

Ejecuta el script incluido — genera un binario en `dist/PDFTextReplacer`:

```bash
# Asegúrate de tener el venv creado con las dependencias instaladas (ver arriba)
./build.sh
```

El binario en `dist/PDFTextReplacer` se puede mover a cualquier carpeta y ejecutar sin tener Python instalado.

Para empaquetarlo como un bundle `.app` que puedas poner en `/Applications`, usa PyInstaller directamente:

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

El bundle quedará en `dist/PDFTextReplacer.app`.

## Compilar un EXE en Windows

Ejecuta lo siguiente en una ventana de Símbolo del sistema o PowerShell desde la carpeta del proyecto:

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

El ejecutable quedará en `dist\PDFTextReplacer.exe`.

> **Nota:** Los binarios generados con PyInstaller son específicos de cada plataforma. El build de Windows hay que hacerlo en Windows y el de macOS en una Mac.
