from __future__ import annotations

import customtkinter as ctk

from notion_prettify_gui.models.options import PrettifyOptions
from notion_prettify_gui.services.runner import (
    PrettifyRunner,
    RunResult,
    RunStatus,
)
from notion_prettify_gui.widgets.file_section import FileSection
from notion_prettify_gui.widgets.metadata_section import MetadataSection
from notion_prettify_gui.widgets.options_section import OptionsSection

_APP_TITLE = "Notion Export Prettify"
_WINDOW_SIZE = "780x860"
_LOG_HEIGHT = 200


class App(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title(_APP_TITLE)
        self.geometry(_WINDOW_SIZE)
        self.minsize(640, 600)
        self.resizable(True, True)

        self._runner = PrettifyRunner()

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        outer = ctk.CTkScrollableFrame(self, label_text="")
        outer.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        outer.columnconfigure(0, weight=1)

        self._build_header(outer)
        self._build_sections(outer)
        self._build_run_area(outer)

    def _build_header(self, parent: ctk.CTkScrollableFrame) -> None:
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 4))
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=_APP_TITLE,
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Turn a Notion page export into a styled PDF document.",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray65"),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        ctk.CTkFrame(parent, height=1, fg_color=("gray75", "gray30")).grid(
            row=1, column=0, sticky="ew", padx=24, pady=(12, 0)
        )

    def _build_sections(self, parent: ctk.CTkScrollableFrame) -> None:
        self._file_section = FileSection(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray75", "gray30"),
        )
        self._file_section.grid(row=2, column=0, sticky="ew", padx=24, pady=(16, 0))

        self._metadata_section = MetadataSection(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray75", "gray30"),
        )
        self._metadata_section.grid(row=3, column=0, sticky="ew", padx=24, pady=(12, 0))

        self._options_section = OptionsSection(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray75", "gray30"),
        )
        self._options_section.grid(row=4, column=0, sticky="ew", padx=24, pady=(12, 0))

        # Add padding inside each section frame
        for section in (self._file_section, self._metadata_section, self._options_section):
            section.grid_configure(ipadx=16, ipady=14)

    def _build_run_area(self, parent: ctk.CTkScrollableFrame) -> None:
        run_frame = ctk.CTkFrame(parent, fg_color="transparent")
        run_frame.grid(row=5, column=0, sticky="ew", padx=24, pady=(16, 4))
        run_frame.columnconfigure(0, weight=1)

        button_row = ctk.CTkFrame(run_frame, fg_color="transparent")
        button_row.grid(row=0, column=0, sticky="ew")
        button_row.columnconfigure(0, weight=1)

        self._run_button = ctk.CTkButton(
            button_row,
            text="Generate PDF",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_run,
        )
        self._run_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._cancel_button = ctk.CTkButton(
            button_row,
            text="Cancel",
            height=40,
            width=90,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._on_cancel,
            state="disabled",
        )
        self._cancel_button.grid(row=0, column=1)

        self._status_label = ctk.CTkLabel(
            run_frame,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
        )
        self._status_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        log_label = ctk.CTkLabel(
            run_frame, text="Output", font=ctk.CTkFont(size=13, weight="bold"), anchor="w"
        )
        log_label.grid(row=2, column=0, sticky="w", pady=(12, 4))

        self._log_box = ctk.CTkTextbox(
            run_frame,
            height=_LOG_HEIGHT,
            font=ctk.CTkFont(family="monospace", size=12),
            state="disabled",
            wrap="word",
        )
        self._log_box.grid(row=3, column=0, sticky="ew", pady=(0, 20))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_run(self) -> None:
        if self._file_section.input_file is None:
            self._set_status("Please select an input file first.", error=True)
            return

        options = PrettifyOptions(
            input_file=self._file_section.input_file,
            output=self._file_section.output,
            template=self._file_section.template,
            title=self._metadata_section.title,
            subtitle=self._metadata_section.subtitle,
            description=self._metadata_section.description,
            project=self._metadata_section.project,
            author=self._metadata_section.author,
            date=self._metadata_section.date,
            identifier=self._metadata_section.identifier,
            cover_page=self._options_section.cover_page,
            heading_numbers=self._options_section.heading_numbers,
            strip_internal_info=self._options_section.strip_internal_info,
            table_of_contents=self._options_section.table_of_contents,
        )

        self._clear_log()
        self._set_running(True)
        self._set_status("Running…")

        self._runner.run(
            options,
            on_output=self._append_log_threadsafe,
            on_complete=self._on_complete_threadsafe,
        )

    def _on_cancel(self) -> None:
        self._runner.cancel()
        self._set_status("Cancelling…")

    def _on_complete_threadsafe(self, result: RunResult) -> None:
        self.after(0, self._on_complete, result)

    def _on_complete(self, result: RunResult) -> None:
        self._set_running(False)
        if result.status == RunStatus.SUCCESS:
            self._set_status("Done — PDF generated successfully.", error=False)
        else:
            code_str = f" (exit code {result.return_code})" if result.return_code else ""
            self._set_status(f"Failed{code_str}. See output below.", error=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_running(self, running: bool) -> None:
        self._run_button.configure(state="disabled" if running else "normal")
        self._cancel_button.configure(state="normal" if running else "disabled")

    def _set_status(self, message: str, error: bool = False) -> None:
        color = ("red", "#ff6b6b") if error else ("green", "#6bff8e")
        self._status_label.configure(text=message, text_color=color)

    def _clear_log(self) -> None:
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _append_log_threadsafe(self, text: str) -> None:
        self.after(0, self._append_log, text)

    def _append_log(self, text: str) -> None:
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")


def main() -> None:
    app = App()
    app.mainloop()
