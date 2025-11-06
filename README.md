# Ebaylistingapp

A simple self-contained Python application for Windows 11.

## Features

- Small window with white background and black text displaying "Ebaylistingapp"
- Menu bar with File > Exit option
- Standalone executable that can be run by double-clicking

## Building the Executable

To create a standalone .exe file that doesn't require Python to be installed:

1. Install PyInstaller (if not already installed):
   ```
   pip install -r requirements.txt
   ```

2. Build the executable:
   ```
   python build_exe.py
   ```

3. The executable will be created in the `dist` folder as `Ebaylistingapp.exe`

4. You can double-click `Ebaylistingapp.exe` to run the application

## Running Directly (if Python is installed)

If you have Python installed, you can also run the app directly:
```
python ebaylistingapp.py
```

Or on Windows, you can rename `ebaylistingapp.py` to `ebaylistingapp.pyw` and double-click it to run without a console window.

