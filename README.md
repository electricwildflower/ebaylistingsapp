# ebaylistingapp

Portable-friendly template for running and packaging a tiny Tkinter GUI without
installing Python system-wide.

## Folder Layout

```
ebaylistingapp/
├─ app/
│  ├─ __init__.py
│  └─ main.py
├─ python/                  ← drop the portable interpreter here (see below)
├─ tools/
│  └─ bootstrap_embed_python.py
├─ build.bat
├─ run.bat
├─ requirements.txt
└─ requirements-build.txt
```

## Portable Python Options

Choose **one** interpreter and extract it into the `python` folder so that
`python\python.exe` (and ideally `python\pythonw.exe`) exist.

### Option A: WinPython Portable (recommended)
1. Download a recent “WinPython64” release that matches your target architecture.
2. Extract the archive.
3. Copy the full extracted folder contents into `python\`.
   - The root of `python\` should now contain `python.exe`, `pythonw.exe`,
     `Scripts\pip.exe`, etc.

### Option B: Official Python Embeddable ZIP
1. Download the Windows embeddable ZIP for your Python version.
2. Extract it into `python\`.
3. Edit `python\python*.pth`:
   - Remove the leading `#` from `import site`.
4. Double-click `run.bat` once – it runs
   `tools\bootstrap_embed_python.py` to download & install `pip` into the
   portable interpreter.

> Both approaches are portable and require **no admin rights**.

## Run the App (development)

Double-click `run.bat`.

What it does:
1. Ensures pip exists inside the portable interpreter (bootstraps when needed).
2. Installs runtime dependencies from `requirements.txt` (currently none).
3. Launches `app\main.py` with `pythonw.exe` so no console window is visible.

## Build a Standalone EXE

1. Make sure your portable interpreter lives in `python\`.
2. Double-click `build.bat`.
   - Installs build requirements from `requirements-build.txt` (PyInstaller).
   - Cleans previous `dist\` and `build\` folders.
   - Generates `dist\ebaylistingapp\ebaylistingapp.exe`.
3. Copy the `dist\ebaylistingapp` folder to any Windows machine and run the EXE.

## Customisation Tips

- Modify `app\main.py` to build the real GUI.
- Add third-party libraries to `requirements.txt`; the next `run.bat` execution
  installs them locally inside the portable interpreter.
- If you upgrade Python, just replace the contents of the `python\` directory.

