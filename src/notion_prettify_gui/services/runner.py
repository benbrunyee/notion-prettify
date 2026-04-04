from __future__ import annotations

import os
import shutil
import site
import subprocess
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

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


def _path_for_cli_lookup() -> str:
    """PATH used to resolve the CLI and for subprocess env on macOS.

    Apps launched from Finder receive a minimal PATH that omits Homebrew and
    user-local script directories, so ``shutil.which`` fails even when the tool
    is installed.
    """
    base = os.environ.get("PATH", "")
    if sys.platform != "darwin":
        return base
    home = Path.home()
    extra: list[str] = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        str(home / ".local" / "bin"),
    ]
    pyenv_root = os.environ.get("PYENV_ROOT")
    pyenv_shims = Path(pyenv_root) / "shims" if pyenv_root else home / ".pyenv" / "shims"
    extra.append(str(pyenv_shims))
    user_base = site.getuserbase()
    if user_base:
        extra.append(str(Path(user_base) / "bin"))
    return os.pathsep.join([*extra, base])


class PrettifyRunner:
    """Runs notion-export-prettify as a subprocess, streaming its output.

    All I/O happens on a background thread so the UI remains responsive.
    """

    CLI_COMMAND = "notion-export-prettify"

    def __init__(self) -> None:
        self._zip_handler = ZipHandler()
        self._process: subprocess.Popen[str] | None = None
        self._thread: threading.Thread | None = None

    def run(
        self,
        options: PrettifyOptions,
        on_output: OutputCallback,
        on_complete: CompletionCallback,
    ) -> None:
        """Start the CLI in a background thread.

        *on_output* is called with each line of stdout/stderr.
        *on_complete* is called once the process exits.
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError("A run is already in progress.")

        self._thread = threading.Thread(
            target=self._run_worker,
            args=(options, on_output, on_complete),
            daemon=True,
        )
        self._thread.start()

    def cancel(self) -> None:
        """Attempt to terminate a running process."""
        if self._process and self._process.poll() is None:
            self._process.terminate()

    def _run_worker(
        self,
        options: PrettifyOptions,
        on_output: OutputCallback,
        on_complete: CompletionCallback,
    ) -> None:
        path_for_cli = _path_for_cli_lookup()
        executable = shutil.which(self.CLI_COMMAND, path=path_for_cli)
        if executable is None:
            on_output(
                f"Error: '{self.CLI_COMMAND}' not found on PATH. "
                "Make sure notion-export-prettify is installed.\n"
            )
            on_complete(RunResult(RunStatus.FAILED))
            return

        try:
            resolved_input = self._zip_handler.resolve(options.input_file)  # type: ignore[arg-type]
        except (ZipExtractionError, ValueError) as exc:
            on_output(f"Error: {exc}\n")
            on_complete(RunResult(RunStatus.FAILED))
            return

        effective_options = PrettifyOptions(
            input_file=resolved_input,
            template=options.template,
            output=options.output,
            title=options.title,
            subtitle=options.subtitle,
            description=options.description,
            project=options.project,
            author=options.author,
            date=options.date,
            identifier=options.identifier,
            cover_page=options.cover_page,
            heading_numbers=options.heading_numbers,
            strip_internal_info=options.strip_internal_info,
            table_of_contents=options.table_of_contents,
        )

        try:
            cli_args = effective_options.to_cli_args()
        except ValueError as exc:
            on_output(f"Error: {exc}\n")
            on_complete(RunResult(RunStatus.FAILED))
            return

        cmd = [executable, *cli_args]
        on_output(f"$ {' '.join(cmd)}\n\n")

        return_code: int | None = None
        try:
            proc_env = {**os.environ, "PYTHONUTF8": "1"}
            if sys.platform == "darwin":
                proc_env["PATH"] = path_for_cli
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=proc_env,
            )
            assert self._process.stdout is not None
            for line in self._process.stdout:
                on_output(line)
            return_code = self._process.wait()
        except OSError as exc:
            on_output(f"Error launching process: {exc}\n")
            on_complete(RunResult(RunStatus.FAILED))
            return
        finally:
            # Move PDF out of the temp extraction dir before it is deleted.
            if return_code == 0 and options.output is None:
                self._relocate_pdf(options, on_output)
            self._zip_handler.cleanup()

        status = RunStatus.SUCCESS if return_code == 0 else RunStatus.FAILED
        on_complete(RunResult(status=status, return_code=return_code))

    def _relocate_pdf(self, options: PrettifyOptions, on_output: OutputCallback) -> None:
        """Move a PDF written into the temp extraction dir to the original input's directory.

        Called only when no explicit output path was given and the run succeeded.
        Has no effect when no temp extraction dir was created (input was already an
        ExportBlock-*.zip or an HTML file — in that case the PDF is already in the
        right place).
        """
        extraction_dir = self._zip_handler.extraction_dir
        if extraction_dir is None or options.input_file is None:
            return

        pdfs = list(extraction_dir.glob("*.pdf"))
        if not pdfs:
            return

        destination_dir = options.input_file.parent
        for pdf in pdfs:
            dest = destination_dir / pdf.name
            shutil.move(str(pdf), str(dest))
            on_output(f"PDF saved to: {dest}\n")
