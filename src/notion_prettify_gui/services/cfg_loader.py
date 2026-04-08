from __future__ import annotations

import configparser
from dataclasses import dataclass, field
from pathlib import Path

_CONTROL_KEY_MAP: dict[str, str] = {
    "cover-page": "cover_page",
    "table-of-contents": "table_of_contents",
    "strip-internal-info": "strip_internal_info",
    "heading-numbers": "heading_numbers",
}

_TRUTHY = {"true", "yes", "1", "on"}
_FALSY = {"false", "no", "0", "off"}


@dataclass
class CfgData:
    """Parsed contents of a .cfg template file."""

    metadata: dict[str, str] = field(default_factory=dict)
    controls: dict[str, bool | None] = field(default_factory=dict)


def load_cfg(path: Path) -> CfgData:
    """Parse an INI-style .cfg template file into metadata and control values."""
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read(str(path), encoding="utf-8")

    data = CfgData()

    if parser.has_section("metadata"):
        for key, value in parser.items("metadata"):
            data.metadata[key] = value if value is not None else ""

    if parser.has_section("control"):
        for key, value in parser.items("control"):
            attr = _CONTROL_KEY_MAP.get(key)
            if attr is None:
                continue
            if not value:
                data.controls[attr] = None
            elif value.lower() in _TRUTHY:
                data.controls[attr] = True
            elif value.lower() in _FALSY:
                data.controls[attr] = False

    return data
