from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk


class _FilePickerRow(ctk.CTkFrame):
    """A label + entry + browse button row for picking a single file path."""

    def __init__(
        self,
        master: ctk.CTkFrame,
        label: str,
        placeholder: str,
        file_types: list[tuple[str, str]],
        save_mode: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._file_types = file_types
        self._save_mode = save_mode

        self.columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text=label, anchor="w", width=90).grid(
            row=0, column=0, padx=(0, 8), sticky="w"
        )
        self._entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self._entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ctk.CTkButton(self, text="Browse", width=80, command=self._browse).grid(
            row=0, column=2
        )

    def _browse(self) -> None:
        if self._save_mode:
            path = filedialog.asksaveasfilename(filetypes=self._file_types)
        else:
            path = filedialog.askopenfilename(filetypes=self._file_types)
        if path:
            self._entry.delete(0, "end")
            self._entry.insert(0, path)

    def get(self) -> Path | None:
        value = self._entry.get().strip()
        return Path(value) if value else None

    def set(self, path: Path | None) -> None:
        self._entry.delete(0, "end")
        if path is not None:
            self._entry.insert(0, str(path))


class FileSection(ctk.CTkFrame):
    """Groups the input file, output file, and template file pickers."""

    _ZIP_TYPES = [
        ("ZIP files", "*.zip"),
        ("HTML files", "*.html"),
        ("All files", "*.*"),
    ]
    _PDF_TYPES = [("PDF files", "*.pdf"), ("All files", "*.*")]
    _TEMPLATE_TYPES = [("Config / template files", "*.*")]

    def __init__(self, master: ctk.CTkFrame, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Files", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        self._input_row = _FilePickerRow(
            self,
            label="Input file",
            placeholder="ExportBlock-*.zip or *.html from Notion",
            file_types=self._ZIP_TYPES,
        )
        self._input_row.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        self._output_row = _FilePickerRow(
            self,
            label="Output PDF",
            placeholder="Leave blank to save alongside the input file",
            file_types=self._PDF_TYPES,
            save_mode=True,
        )
        self._output_row.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self._template_row = _FilePickerRow(
            self,
            label="Template",
            placeholder="Optional custom template / config file",
            file_types=self._TEMPLATE_TYPES,
        )
        self._template_row.grid(row=3, column=0, sticky="ew")

    @property
    def input_file(self) -> Path | None:
        return self._input_row.get()

    @property
    def output(self) -> Path | None:
        return self._output_row.get()

    @property
    def template(self) -> Path | None:
        return self._template_row.get()
