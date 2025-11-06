# How to Run on Windows 11

## Option 1: Build and Run as Executable (Recommended - No Python needed after building)

This creates a standalone .exe file that you can double-click to run without needing Python installed.

### Step 1: Install Python (if not already installed)
1. Download Python from https://www.python.org/downloads/
2. During installation, **check the box "Add Python to PATH"** (important!)
3. Complete the installation

### Step 2: Build the Executable
1. Open File Explorer and navigate to the `ebaylistingsapp` folder
2. Double-click `build_exe.bat` (or right-click and select "Run as administrator" if needed)
3. Wait for the build process to complete
4. The executable will be created in the `dist` folder

### Step 3: Run the App
1. Go to the `dist` folder
2. Double-click `Ebaylistingapp.exe`
3. The app will open!

**Note:** After building, you can copy `Ebaylistingapp.exe` to any location and run it - it doesn't need Python or any other files.

---

## Option 2: Run Directly with Python (If Python is installed)

If you already have Python installed:

1. Open Command Prompt or PowerShell in the `ebaylistingsapp` folder
2. Run: `python ebaylistingapp.py`

Or simply:
- Double-click `ebaylistingapp.py` (if Python is set as default for .py files)

---

## Troubleshooting

### "Python is not recognized"
- Python is not installed or not in your PATH
- Reinstall Python and make sure to check "Add Python to PATH" during installation
- Or manually add Python to your system PATH

### "pip is not recognized"
- Python was installed but pip wasn't included
- Try: `python -m ensurepip --upgrade`

### Build fails
- Make sure you're in the correct folder
- Try running Command Prompt as Administrator
- Check that all files are in the same folder

### App won't open
- Check Windows Defender or antivirus - sometimes it blocks new .exe files
- Right-click the .exe and select "Run as administrator"
- Check if Python is still needed (shouldn't be for the .exe)

