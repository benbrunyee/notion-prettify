from __future__ import annotations

import contextlib
import io
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from bs_notion_export_prettify import prettify

from notion_prettify_gui.models.options import PrettifyOptions
from notion_prettify_gui.services.zip_handler import ZipExtractionError, ZipHandler


class RunStatus(Enum):
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()


@dataclass
class RunResult:
    status: RunStatus
    return_code: int | None = None


OutputCallback = Callable[[str], None]
CompletionCallback = Callable[[RunResult], None]


class _TextCallback(io.TextIOBase):
    """Forwards write() calls to an OutputCallback."""

    def __init__(self, callback: OutputCallback) -> None:
        self._callback = callback

    def write(self, s: str) -> int:
        if s:
            self._callback(s)
        return len(s)

    def flush(self) -> None:
        pass


class _LogHandler(logging.Handler):
    """Forwards logging records to an OutputCallback."""

    def __init__(self, callback: OutputCallback) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        self._callback(self.format(record) + "\n")


class PrettifyRunner:
    """Calls bs_notion_export_prettify.prettify() on a background thread."""

    def __init__(self) -> None:
        self._zip_handler = ZipHandler()
        self._thread: threading.Thread | None = None

    def run(
        self,
        options: PrettifyOptions,
        on_output: OutputCallback,
        on_complete: CompletionCallback,
    ) -> None:
        """Start the prettify call in a background thread.

        *on_output* receives each captured log/stdout line.
        *on_complete* is called once the operation finishes.
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError("A run is already in progress.")

        self._thread = threading.Thread(
            target=self._run_worker,
            args=(options, on_output, on_complete),
            daemon=True,
        )
        self._thread.start()

    def _run_worker(
        self,
        options: PrettifyOptions,
        on_output: OutputCallback,
        on_complete: CompletionCallback,
    ) -> None:
        try:
            resolved_input = self._zip_handler.resolve(options.input_file)  # type: ignore[arg-type]
        except (ZipExtractionError, ValueError) as exc:
            on_output(f"Error: {exc}\n")
            on_complete(RunResult(RunStatus.FAILED))
            return

        # When no output path is given, write next to the original input file
        # so the PDF never ends up inside a temporary extraction directory.
        effective_output = options.output
        if effective_output is None and options.input_file is not None:
            effective_output = _derive_output_path(options)

        stream = _TextCallback(on_output)
        log_handler = _LogHandler(on_output)
        log_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        module_logger = logging.getLogger("bs_notion_export_prettify")
        module_logger.addHandler(log_handler)
        original_level = module_logger.level
        module_logger.setLevel(logging.DEBUG)

        kwargs = _build_prettify_kwargs(options, resolved_input, effective_output)
        on_output(f"Running prettify on: {resolved_input}\n\n")

        output_path: Path | None = None
        try:
            with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                output_path = prettify(**kwargs)
        except Exception as exc:
            on_output(f"Error: {exc}\n")
            on_complete(RunResult(RunStatus.FAILED))
            return
        finally:
            module_logger.removeHandler(log_handler)
            module_logger.setLevel(original_level)
            self._zip_handler.cleanup()

        if output_path is not None:
            on_output(f"\nPDF saved to: {output_path}\n")
        on_complete(RunResult(status=RunStatus.SUCCESS))


def _derive_output_path(options: PrettifyOptions) -> Path:
    """Compute a sensible output path next to the original input file."""
    assert options.input_file is not None
    project = options.project.strip()
    title = options.title.strip()
    if project and title:
        stem = f"{project} - {title}"
    elif not title and project:
        stem = project
    elif title:
        stem = title
    else:
        stem = options.input_file.stem
    return options.input_file.parent / f"{stem}.pdf"


def _build_prettify_kwargs(
    options: PrettifyOptions,
    resolved_input: Path,
    effective_output: Path | None,
) -> dict[str, object]:
    kwargs: dict[str, object] = {"input_file": str(resolved_input)}

    if effective_output is not None:
        kwargs["output"] = str(effective_output)
    if options.template is not None:
        kwargs["template"] = str(options.template)

    for field in ("title", "subtitle", "project", "author", "date"):
        value: str = getattr(options, field)
        if value:
            kwargs[field] = value
    if options.identifier:
        kwargs["identifier"] = options.identifier

    for flag in (
        "cover_page",
        "heading_numbers",
        "strip_internal_info",
        "table_of_contents",
    ):
        value_bool: bool | None = getattr(options, flag)
        if value_bool is not None:
            kwargs[flag] = value_bool

    return kwargs
