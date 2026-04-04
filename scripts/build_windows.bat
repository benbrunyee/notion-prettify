@echo off
REM Build NotionPrettify.exe for Windows.
REM
REM Usage (from the project root or this scripts\ folder):
REM   scripts\build_windows.bat
REM
REM Output:
REM   dist\NotionPrettify.exe   — single-file executable, no install needed
REM
REM Prerequisites:
REM   - Python 3.x with this project installed  (pip install -e .)
REM   - notion-export-prettify available on PATH (installed separately)

setlocal EnableDelayedExpansion

REM Move to the project root regardless of where the script was invoked from
cd /d "%~dp0\.."

echo =^> Installing / upgrading PyInstaller...
pip install --quiet --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is on your PATH.
    exit /b 1
)

echo =^> Cleaning previous build artefacts...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo =^> Building NotionPrettify.exe...
pyinstaller NotionPrettify.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

set "EXE_PATH=dist\NotionPrettify.exe"

if exist "%EXE_PATH%" (
    echo.
    echo Build succeeded^^!
    echo   Executable: %CD%\%EXE_PATH%
    echo.
    echo To create a Desktop shortcut:
    echo   Right-click dist\NotionPrettify.exe ^> Send to ^> Desktop ^(create shortcut^)
    echo.
    echo NOTE: notion-export-prettify must still be installed and on PATH.
    echo       The GUI app launches it as a subprocess.
) else (
    echo ERROR: Build completed but %EXE_PATH% was not found.
    exit /b 1
)

endlocal
