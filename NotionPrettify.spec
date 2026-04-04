"""PyInstaller spec for Notion Prettify GUI.

Produces:
  - macOS : dist/NotionPrettify.app  (double-clickable .app bundle)
  - Windows: dist/NotionPrettify.exe  (single-file executable)

Run via the build scripts in scripts/, or directly with:
    pyinstaller NotionPrettify.spec
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# customtkinter ships theme JSON files and images that must travel with the binary.
datas = collect_data_files("customtkinter")
datas += collect_data_files("bs_notion_export_prettify")
# playwright bundles its own node.exe + JS driver package.  These are required so
# that ensure_chromium_installed() can invoke the driver to download Chromium at
# runtime without spawning sys.executable (which is the frozen app itself).
datas += collect_data_files("playwright")

# PyInstaller does not always follow customtkinter imports; force the full package tree.
_hidden_customtkinter = collect_submodules("customtkinter")
_hidden_bs_prettify = collect_submodules("bs_notion_export_prettify")

a = Analysis(
    ["main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=_hidden_customtkinter
    + _hidden_bs_prettify
    + [
        # tkinter backend modules sometimes need explicit inclusion
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        # playwright is used by bs_notion_export_prettify for PDF rendering
        "playwright",
        "playwright.sync_api",
        "bs_notion_export_prettify",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim unused heavy stdlib modules to shrink the bundle
        "unittest",
        "pydoc",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

if sys.platform == "darwin":
    # macOS: onedir mode is required for a proper .app bundle
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="NotionPrettify",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        argv_emulation=True,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name="NotionPrettify",
    )
    app = BUNDLE(
        coll,
        name="NotionPrettify.app",
        icon=None,
        bundle_identifier="com.brunyee.notion-prettify",
        info_plist={
            "CFBundleDisplayName": "Notion Prettify",
            "CFBundleShortVersionString": "0.1.0",
            "NSHighResolutionCapable": True,
            # Allow file picker access without extra entitlements
            "NSAppleEventsUsageDescription": "Notion Prettify needs access to open files.",
        },
    )
else:
    # Windows / Linux: single onefile executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="NotionPrettify",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
