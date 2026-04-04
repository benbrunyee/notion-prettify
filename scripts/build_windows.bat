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
REM   - uv (https://docs.astral.sh/uv/) installed and on PATH
REM   - notion-export-prettify available on PATH (installed separately)

setlocal EnableDelayedExpansion

REM Move to the project root regardless of where the script was invoked from
cd /d "%~dp0\.."

echo =^> Syncing dependencies (including build group)...
uv sync --group build
if errorlevel 1 (
    echo ERROR: uv sync failed. Make sure uv is installed and on your PATH.
    exit /b 1
)

echo =^> Cleaning previous build artefacts...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo =^> Building NotionPrettify.exe...
uv run pyinstaller NotionPrettify.spec
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
