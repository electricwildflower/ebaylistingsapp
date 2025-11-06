# Installing Python on Windows 11

## Quick Installation Guide

### Step 1: Download Python
1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow "Download Python" button (downloads the latest version)

### Step 2: Install Python
1. Run the downloaded installer (e.g., `python-3.12.x.exe`)
2. **IMPORTANT:** On the first screen, check the box that says:
   - ✅ **"Add Python to PATH"** (or "Add python.exe to PATH")
3. Click "Install Now"
4. Wait for installation to complete
5. Click "Close" when done

### Step 3: Verify Installation
1. Close any open Command Prompt or PowerShell windows
2. Open a NEW Command Prompt (press Windows key, type "cmd", press Enter)
3. Type: `python --version`
4. You should see something like: `Python 3.12.x`

If you see an error, Python wasn't added to PATH. See "Troubleshooting" below.

### Step 4: Build the App
1. Navigate to the `ebaylistingsapp` folder
2. Double-click `build_exe.bat`
3. Wait for it to build (may take a few minutes)
4. Your executable will be in the `dist` folder!

---

## Troubleshooting

### "Python is not recognized" after installation

**Option 1: Reinstall Python (Easiest)**
1. Uninstall Python from Settings > Apps
2. Download and install again
3. **Make sure to check "Add Python to PATH" this time**
4. Restart your computer
5. Try again

**Option 2: Manually Add Python to PATH**
1. Find where Python is installed (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx\` or `C:\Python3xx\`)
2. Press Windows key, type "environment variables", press Enter
3. Click "Environment Variables" button
4. Under "User variables", select "Path" and click "Edit"
5. Click "New" and add:
   - `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx\`
   - `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx\Scripts\`
6. Click OK on all windows
7. **Restart your computer**
8. Try again

### "pip is not recognized"
- Python might be installed but pip is missing
- Try: `python -m ensurepip --upgrade` in Command Prompt

### Still having issues?
- Make sure you restarted your computer after installing Python
- Try running Command Prompt as Administrator
- Check that you're using a 64-bit Python installer (most common)

---

## Alternative: Use Python Launcher

Windows 10/11 includes a Python launcher. Try:
- `py --version` instead of `python --version`

The updated `build_exe.bat` now tries this automatically!

