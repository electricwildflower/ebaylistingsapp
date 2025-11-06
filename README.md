# Ebaylistingapp

A simple self-contained Python application for Windows 11.

## Features

- Small window with white background and black text displaying "Ebaylistingapp"
- Menu bar with File > Exit option
- Standalone executable that can be run by double-clicking

## Quick Start for Windows 11

**See `WINDOWS_INSTRUCTIONS.md` for detailed step-by-step instructions!**

### Easiest Method (Creates Self-Contained Executable):
1. Double-click `build_exe.bat` to build the executable (only needed once)
2. Go to the `dist` folder
3. Double-click `Ebaylistingapp.exe` to run - **no installation needed!**

**The final .exe file is completely self-contained:**
- ✅ Includes Python and all dependencies bundled inside
- ✅ No installation required to run - just double-click
- ✅ Can be copied to any Windows 11 computer and run immediately
- ✅ No external files or dependencies needed

## Building the Executable

### Windows (Easiest):
Double-click `build_exe.bat`

### Manual Method:
1. Install PyInstaller (if not already installed):
   ```
   pip install -r requirements.txt
   ```

2. Build the executable:
   ```
   python build_exe.py
   ```
   Or: `python -m PyInstaller --onefile --windowed --name=Ebaylistingapp ebaylistingapp.py`

3. The executable will be created in the `dist` folder as `Ebaylistingapp.exe`

4. You can double-click `Ebaylistingapp.exe` to run the application

## Running Directly (if Python is installed)

If you have Python installed, you can also run the app directly:
```
python ebaylistingapp.py
```

Or on Windows, you can rename `ebaylistingapp.py` to `ebaylistingapp.pyw` and double-click it to run without a console window.

