@echo off
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "PYTHON_DIR=%PROJECT_DIR%python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PYTHONW_EXE=%PYTHON_DIR%\pythonw.exe"

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

echo [*] Ensuring runtime requirements are installed...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check --no-warn-script-location --requirement "%PROJECT_DIR%requirements.txt"
if errorlevel 1 (
    echo [!] pip install failed.
    pause
    exit /b 1
)

if not exist "%PYTHONW_EXE%" (
    set "PYTHONW_EXE=%PYTHON_EXE%"
)

echo [*] Launching ebaylistingapp...
start "" "%PYTHONW_EXE%" "%PROJECT_DIR%app\main.py"
endlocal
exit /b 0


