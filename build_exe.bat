@echo off
echo Building Ebaylistingapp executable...
echo.

REM Try to find Python - check multiple methods
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :found_python
)

REM Python not found
echo ========================================
echo ERROR: Python is not installed or not in PATH
echo ========================================
echo.
echo To fix this:
echo 1. Download Python from: https://www.python.org/downloads/
echo 2. During installation, CHECK THE BOX "Add Python to PATH"
echo 3. Complete the installation
echo 4. Close and reopen this window, then try again
echo.
echo If Python is already installed:
echo - You may need to restart your computer after installation
echo - Or manually add Python to your system PATH
echo.
pause
exit /b 1

:found_python
echo Found Python! Using: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Install PyInstaller if not already installed
echo Installing/updating PyInstaller...
%PYTHON_CMD% -m pip install --upgrade pyinstaller

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install PyInstaller
    echo Try running as Administrator or install manually: pip install pyinstaller
    pause
    exit /b 1
)

REM Build the executable
echo.
echo Building standalone executable (this may take a few minutes)...
%PYTHON_CMD% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=Ebaylistingapp ^
    --clean ^
    --noconfirm ^
    --collect-all tkinter ^
    ebaylistingapp.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo SUCCESS! The executable has been created in the 'dist' folder.
echo You can now double-click 'dist\Ebaylistingapp.exe' to run the app.
echo.
pause

