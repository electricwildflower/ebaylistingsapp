@echo off
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "PYTHON_DIR=%PROJECT_DIR%python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Portable Python not found. Extract WinPython or the Embeddable ZIP into:
    echo     %PYTHON_DIR%
    pause
    exit /b 1
)

set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"

if not exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo [*] Bootstrapping pip inside the portable interpreter...
    "%PYTHON_EXE%" "%PROJECT_DIR%tools\bootstrap_embed_python.py"
    if errorlevel 1 (
        echo [!] Unable to bootstrap pip. Please review README.md for manual steps.
        pause
        exit /b 1
    )
)

echo [*] Installing build dependencies...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check --no-warn-script-location --requirement "%PROJECT_DIR%requirements-build.txt"
if errorlevel 1 (
    echo [!] Failed to install build dependencies.
    pause
    exit /b 1
)

set "DIST_DIR=%PROJECT_DIR%dist"
set "BUILD_DIR=%PROJECT_DIR%build"

if exist "%DIST_DIR%" (
    echo [*] Cleaning previous dist output...
    rmdir /s /q "%DIST_DIR%"
)

if exist "%BUILD_DIR%" (
    echo [*] Cleaning previous build artifacts...
    rmdir /s /q "%BUILD_DIR%"
)

echo [*] Building standalone executable with PyInstaller...
"%PYTHON_EXE%" -m PyInstaller ^
    --noconfirm ^
    --noconsole ^
    --clean ^
    --name ebaylistingapp ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_DIR%" ^
    --specpath "%BUILD_DIR%" ^
    "%PROJECT_DIR%app\main.py"

if errorlevel 1 (
    echo [!] PyInstaller build failed.
    pause
    exit /b 1
)

echo [✓] Build complete. Check the dist folder for ebaylistingapp.exe.
pause
endlocal
exit /b 0


