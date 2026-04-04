from __future__ import annotations

import os
import platform
import sys

# ---- Playwright persistent browser path (must be before all other imports) ----
# In PyInstaller onefile mode the app extracts to a new _MEI* temp directory on
# every run.  Playwright resolves its default browser storage relative to its
# package location inside that temp dir, so any previously-downloaded Chromium
# binary appears "missing" on the next launch.  Redirect to a stable user-data
# directory so the installation persists across runs.
if getattr(sys, "frozen", False):
    _appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    os.environ.setdefault(
        "PLAYWRIGHT_BROWSERS_PATH",
        os.path.join(_appdata, "NotionPrettify", "playwright-browsers"),
    )
# ---------------------------------------------------------------------------------

# PyInstaller bundles often report an empty macOS version string; darkdetect (used by
# customtkinter) parses platform.mac_ver()[0] and crashes with int(''). Supply a safe
# fallback before importing the GUI stack.
if getattr(sys, "frozen", False) and sys.platform == "darwin":
    _orig_mac_ver = platform.mac_ver

    def _mac_ver() -> tuple[str, tuple[str, str, str], str]:
        release, info, machine = _orig_mac_ver()
        if not release or not release.strip():
            release = "15.0"
        return (release, info, machine)

    platform.mac_ver = _mac_ver  # type: ignore[assignment]

# ---- Fix playwright browser install when frozen --------------------------------
# browser_setup.ensure_chromium_installed() tries to locate a Python interpreter
# via shutil.which("python3"/"python").  When the app is bundled with PyInstaller
# there is no guarantee that Python is on PATH (e.g. uv-managed installs).
# Replace the function with one that invokes playwright's own bundled node.exe +
# cli.js driver directly — no Python in PATH required.
if getattr(sys, "frozen", False):
    import bs_notion_export_prettify.browser_setup as _browser_setup
    import bs_notion_export_prettify.pdf_maker as _pdf_maker
    from pathlib import Path
    from playwright._impl._driver import compute_driver_executable

    def _frozen_ensure_chromium_installed() -> None:
        import subprocess as _subprocess

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            executable = p.chromium.executable_path

        if Path(executable).exists():
            return

        print("Playwright Chromium browser not found. Installing now...")
        node_exe, cli_js = compute_driver_executable()
        _subprocess.run([str(node_exe), str(cli_js), "install", "chromium"], check=True)
        print("Chromium installation complete.")

    # Patch both the module-level attribute and the local binding that pdf_maker
    # created via `from .browser_setup import ensure_chromium_installed` at import
    # time.  Without patching pdf_maker too, the original function keeps running.
    _browser_setup.ensure_chromium_installed = _frozen_ensure_chromium_installed
    _pdf_maker.ensure_chromium_installed = _frozen_ensure_chromium_installed
# ---------------------------------------------------------------------------------

from notion_prettify_gui.app import main  # noqa: E402

if __name__ == "__main__":
    main()
