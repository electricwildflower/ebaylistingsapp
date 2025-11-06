@echo off
echo Building Ebaylistingapp executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Installing/updating PyInstaller...
python -m pip install --upgrade pyinstaller

REM Build the executable
echo.
echo Building standalone executable (this may take a few minutes)...
python -m PyInstaller ^
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

