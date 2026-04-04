from __future__ import annotations

import platform
import sys
from types import TracebackType


def _install_frozen_crash_log() -> None:
    """Write uncaught exceptions to a log when running as a windowed .app (no console)."""
    if not getattr(sys, "frozen", False):
        return

    import traceback
    from pathlib import Path

    log_dir = Path.home() / "Library" / "Logs" / "NotionPrettify"

    def excepthook(
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType | None,
    ) -> None:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "crash.log").write_text(
                "".join(traceback.format_exception(exc_type, exc, tb)),
                encoding="utf-8",
            )
        except OSError:
            pass
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = excepthook


_install_frozen_crash_log()

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

from notion_prettify_gui.app import main  # noqa: E402

if __name__ == "__main__":
    main()
