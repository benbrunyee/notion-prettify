#!/usr/bin/env bash
# Build NotionPrettify.app for macOS.
#
# Usage:
#   bash scripts/build_macos.sh
#
# Output:
#   dist/NotionPrettify.app   — drag this into /Applications to install
#
# Prerequisites:
#   - Python 3.x with this project and dependencies installed  (pip install -e .)
#   - notion-export-prettify available on PATH (installed separately)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

PYTHON="${PYTHON:-python3}"

echo "==> Ensuring project dependencies are installed..."
"$PYTHON" -m pip install --quiet --upgrade pip
"$PYTHON" -m pip install --quiet --upgrade -e .

echo "==> Installing / upgrading PyInstaller..."
"$PYTHON" -m pip install --quiet --upgrade pyinstaller

echo "==> Cleaning previous build artefacts..."
rm -rf build dist

echo "==> Building NotionPrettify.app..."
"$PYTHON" -m PyInstaller NotionPrettify.spec --noconfirm

APP_PATH="dist/NotionPrettify.app"

if [ -d "$APP_PATH" ]; then
    # Ad-hoc sign the whole bundle so Gatekeeper and nested dylibs stay consistent
    # after copying to /Applications (PyInstaller signs the outer app; --deep catches Frameworks).
    echo "==> Ad-hoc signing app bundle (deep)..."
    codesign --force --deep --sign - "$APP_PATH"

    # Strip extended attributes from the build output (e.g. quarantine/provenance from tools).
    # End users who downloaded a zip may still need: xattr -cr /Applications/NotionPrettify.app
    xattr -cr "$APP_PATH" 2>/dev/null || true

    echo ""
    echo "Build succeeded!"
    echo "  App: $ROOT_DIR/$APP_PATH"
    echo "  CPU: $(uname -m) (use the same architecture on the Mac you install to; arm64 vs x86_64)"
    echo ""
    echo "To install:"
    echo "  cp -R \"$ROOT_DIR/$APP_PATH\" /Applications/"
    echo ""
    echo "If double-click does nothing or macOS says the app can't be opened:"
    echo "  • First launch: right-click the app → Open → Open (trusts this unsigned build)."
    echo "  • Or run:  xattr -cr /Applications/NotionPrettify.app"
    echo "  • If it still quits immediately, see:  ~/Library/Logs/NotionPrettify/crash.log"
    echo ""
    echo "NOTE: notion-export-prettify must still be installed and on PATH."
    echo "      After installing it, also run:"
    echo "        python -m playwright install chromium"
    echo "      using the same Python where notion-export-prettify is installed."
    echo "      The GUI app launches notion-export-prettify as a subprocess,"
    echo "      which uses Playwright + Chromium to render the PDF."
else
    echo "Build failed — $APP_PATH not found." >&2
    exit 1
fi
