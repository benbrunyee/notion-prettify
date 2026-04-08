from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class _FilePickerRow(QWidget):
    """A label + entry + browse button row for picking a single file path."""

    def __init__(
        self,
        label: str,
        placeholder: str,
        file_filter: str,
        save_mode: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("role", "field-cell")
        self._file_filter = file_filter
        self._save_mode = save_mode

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setProperty("role", "section-label")
        layout.addWidget(label_widget)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._entry = QLineEdit()
        self._entry.setPlaceholderText(placeholder)
        self._entry.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        row.addWidget(self._entry)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(72)
        browse_btn.clicked.connect(self._browse)
        row.addWidget(browse_btn)

        layout.addLayout(row)

    def _browse(self) -> None:
        if self._save_mode:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save file", "", self._file_filter
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open file", "", self._file_filter
            )
        if path:
            self._entry.setText(path)

    def get(self) -> Path | None:
        value = self._entry.text().strip()
        return Path(value) if value else None

    def set(self, path: Path | None) -> None:
        self._entry.setText(str(path) if path is not None else "")


class FileSection(QGroupBox):
    """Groups the input file, output file, and template file pickers."""

    template_changed = Signal(object)  # emits Path | None

    _ZIP_FILTER = "ZIP / HTML files (*.zip *.html);;All files (*.*)"
    _PDF_FILTER = "PDF files (*.pdf);;All files (*.*)"
    _TEMPLATE_FILTER = "Config / template files (*.cfg *.toml *.yaml *.yml *.json);;All files (*.*)"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Files", parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._input_row = _FilePickerRow(
            label="Input file",
            placeholder="ExportBlock-*.zip or *.html from Notion",
            file_filter=self._ZIP_FILTER,
        )
        layout.addWidget(self._input_row)

        self._output_row = _FilePickerRow(
            label="Output PDF",
            placeholder="Leave blank to save alongside the input file",
            file_filter=self._PDF_FILTER,
            save_mode=True,
        )
        layout.addWidget(self._output_row)

        self._template_row = _FilePickerRow(
            label="Template",
            placeholder="Optional custom template / config file",
            file_filter=self._TEMPLATE_FILTER,
        )
        self._template_row._entry.textChanged.connect(self._on_template_text_changed)
        layout.addWidget(self._template_row)

    def _on_template_text_changed(self, text: str) -> None:
        value = text.strip()
        self.template_changed.emit(Path(value) if value else None)

    @property
    def input_file(self) -> Path | None:
        return self._input_row.get()

    @property
    def output(self) -> Path | None:
        return self._output_row.get()

    @property
    def template(self) -> Path | None:
        return self._template_row.get()
