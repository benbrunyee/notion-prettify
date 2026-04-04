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
#   - Python 3.x with this project installed  (pip install -e .)
#   - notion-export-prettify available on PATH (installed separately)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "==> Installing / upgrading PyInstaller..."
pip install --quiet --upgrade pyinstaller

echo "==> Cleaning previous build artefacts..."
rm -rf build dist

echo "==> Building NotionPrettify.app..."
pyinstaller NotionPrettify.spec

APP_PATH="dist/NotionPrettify.app"

if [ -d "$APP_PATH" ]; then
    echo ""
    echo "Build succeeded!"
    echo "  App: $ROOT_DIR/$APP_PATH"
    echo ""
    echo "To install:"
    echo "  cp -r \"$ROOT_DIR/$APP_PATH\" /Applications/"
    echo ""
    echo "NOTE: notion-export-prettify must still be installed and on PATH."
    echo "      The GUI app launches it as a subprocess."
else
    echo "Build failed — $APP_PATH not found." >&2
    exit 1
fi
