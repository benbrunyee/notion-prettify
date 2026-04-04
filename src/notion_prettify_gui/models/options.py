from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PrettifyOptions:
    """All arguments accepted by bs_notion_export_prettify.prettify()."""

    # Required
    input_file: Path | None = None

    # Optional file paths
    template: Path | None = None
    output: Path | None = None

    # Metadata
    title: str = ""
    subtitle: str = ""
    description: str = ""
    project: str = ""
    author: str = ""
    date: str = ""
    identifier: str = ""

    # Boolean toggles (None = use library default)
    cover_page: bool | None = None
    heading_numbers: bool | None = None
    strip_internal_info: bool | None = None
    table_of_contents: bool | None = None
