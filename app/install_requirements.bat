@echo off
echo ==============================================
echo   Python Dependency Installer
echo ==============================================

REM Check if Python is installed
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python from https://python.org/downloads
    pause
    exit /b
)

REM Check if pip is available
echo Checking for pip...
py -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo pip not found, installing...
    py -m ensurepip --default-pip
)

REM Upgrade pip (optional but recommended)
echo Upgrading pip...
py -m pip install --upgrade pip

REM Install requirements
if exist requirements.txt (
    echo Installing required packages from requirements.txt...
    py -m pip install -r requirements.txt
) else (
    echo No requirements.txt found in this folder.
)

echo ==============================================
echo   Installation complete!
echo ==============================================
pause

