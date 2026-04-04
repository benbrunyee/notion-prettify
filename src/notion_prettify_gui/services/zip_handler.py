from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path


class ZipExtractionError(Exception):
    pass


class ZipHandler:
    """Resolves the actual ExportBlock-*.zip that notion-export-prettify expects.

    Notion wraps its export ZIP inside a generic outer ZIP when downloaded
    from the web. If the user selects a ZIP whose name does not start with
    "ExportBlock-", this handler extracts it and locates the inner ExportBlock-*.zip.
    """

    def __init__(self, keep_temp: bool = False) -> None:
        self._keep_temp = keep_temp
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None

    def resolve(self, input_path: Path) -> Path:
        """Return the path that should be passed to notion-export-prettify.

        If *input_path* is already an ExportBlock-*.zip or not a zip at all, it is
        returned unchanged.  Otherwise the zip is extracted and the first
        ExportBlock-*.zip found inside is returned.
        """
        if input_path.suffix.lower() != ".zip":
            return input_path

        if input_path.name.startswith("ExportBlock-"):
            return input_path

        return self._extract_and_find_export_zip(input_path)

    def _extract_and_find_export_zip(self, outer_zip: Path) -> Path:
        if not zipfile.is_zipfile(outer_zip):
            raise ZipExtractionError(f"'{outer_zip}' is not a valid ZIP file.")

        self._temp_dir = tempfile.TemporaryDirectory(
            prefix="notion-prettify-", delete=self._keep_temp
        )
        extract_dir = Path(self._temp_dir.name)

        with zipfile.ZipFile(outer_zip) as zf:
            zf.extractall(extract_dir)

        matches = list(extract_dir.rglob("ExportBlock-*.zip"))
        if not matches:
            raise ZipExtractionError(
                f"No 'ExportBlock-*.zip' found inside '{outer_zip.name}'. "
                "Make sure the file is a valid Notion export."
            )

        return matches[0]

    def cleanup(self) -> None:
        """Remove any temporary extraction directory."""
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None
