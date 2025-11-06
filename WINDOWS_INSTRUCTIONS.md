# How to Run on Windows 11

## Option 1: Build and Run as Executable (Recommended - Completely Self-Contained)

This creates a **completely standalone .exe file** that includes Python and all dependencies bundled inside. Once built, you can:
- Double-click to run - **no Python installation needed**
- Copy to any Windows 11 computer and run it
- Share it with others - they don't need to install anything
- The .exe file is completely self-contained - no external files or dependencies required

### Step 1: Install Python (if not already installed)

**See `INSTALL_PYTHON.md` for detailed installation instructions!**

Quick steps:
1. Download Python from https://www.python.org/downloads/
2. During installation, **CHECK THE BOX "Add Python to PATH"** (very important!)
3. Complete the installation
4. **Restart your computer** (important for PATH to take effect)
5. Verify: Open Command Prompt and type `python --version` - you should see a version number

### Step 2: Build the Executable
1. Open File Explorer and navigate to the `ebaylistingsapp` folder
2. Double-click `build_exe.bat` (or right-click and select "Run as administrator" if needed)
3. Wait for the build process to complete
4. The executable will be created in the `dist` folder

### Step 3: Run the App
1. Go to the `dist` folder
2. Double-click `Ebaylistingapp.exe`
3. The app will open!

**Important:** The `Ebaylistingapp.exe` file is **completely self-contained**:
- ✅ No Python installation needed to run it
- ✅ No additional files or dependencies required
- ✅ Can be copied to any Windows 11 computer and run immediately
- ✅ Everything (Python runtime, tkinter, etc.) is bundled inside the .exe file
- ✅ Just double-click and it runs - that's it!

**Note:** You only need Python installed ONCE to build the executable. After that, the .exe file works independently on any Windows 11 computer without any installation.

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

