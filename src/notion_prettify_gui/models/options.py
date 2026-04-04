from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PrettifyOptions:
    """All CLI arguments accepted by notion-export-prettify."""

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

    # Boolean toggles (None = omit flag, True = --flag, False = --no-flag)
    cover_page: bool | None = None
    heading_numbers: bool | None = None
    strip_internal_info: bool | None = None
    table_of_contents: bool | None = None

    def to_cli_args(self) -> list[str]:
        """Build the argument list for notion-export-prettify."""
        if self.input_file is None:
            raise ValueError("input_file is required")

        args: list[str] = [str(self.input_file)]

        if self.template is not None:
            args += ["--template", str(self.template)]

        if self.output is not None:
            args += ["--output", str(self.output)]

        metadata_flags: list[tuple[str, str]] = [
            ("--title", self.title),
            ("--subtitle", self.subtitle),
            ("--description", self.description),
            ("--project", self.project),
            ("--author", self.author),
            ("--date", self.date),
            ("--identifier", self.identifier),
        ]
        for meta_flag, meta_value in metadata_flags:
            if meta_value:
                args += [meta_flag, meta_value]

        boolean_flags: list[tuple[str, bool | None]] = [
            ("cover-page", self.cover_page),
            ("heading-numbers", self.heading_numbers),
            ("strip-internal-info", self.strip_internal_info),
            ("table-of-contents", self.table_of_contents),
        ]
        for bool_flag, bool_value in boolean_flags:
            if bool_value is True:
                args.append(f"--{bool_flag}")
            elif bool_value is False:
                args.append(f"--no-{bool_flag}")

        return args
