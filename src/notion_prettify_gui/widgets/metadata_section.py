from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

_METADATA_FIELDS: list[tuple[str, str, str]] = [
    # (attribute_name, label_text, placeholder)
    ("title", "Title", "Document title"),
    ("subtitle", "Subtitle", "Document subtitle"),
    ("description", "Description", "Brief description"),
    ("project", "Project", "Project name"),
    ("author", "Author", "Author name"),
    ("date", "Date", "e.g. 2024-01-15"),
    ("identifier", "Identifier", "Doc identifier / number"),
]


class MetadataSection(QGroupBox):
    """Two-column grid of labelled text entry fields for document metadata."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Metadata", parent)

        grid = QGridLayout(self)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self._entries: dict[str, QLineEdit] = {}
        for idx, (attr, label_text, placeholder) in enumerate(_METADATA_FIELDS):
            col = idx % 2
            row = idx // 2

            cell = QWidget()
            cell.setProperty("role", "field-cell")
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(4)

            label = QLabel(label_text)
            label.setProperty("role", "section-label")
            cell_layout.addWidget(label)

            entry = QLineEdit()
            entry.setPlaceholderText(placeholder)
            cell_layout.addWidget(entry)

            self._entries[attr] = entry
            grid.addWidget(cell, row, col)

    def get(self, field: str) -> str:
        return self._entries[field].text().strip()

    def set(self, field: str, value: str) -> None:
        self._entries[field].setText(value)

    @property
    def title(self) -> str:
        return self.get("title")

    @property
    def subtitle(self) -> str:
        return self.get("subtitle")

    @property
    def description(self) -> str:
        return self.get("description")

    @property
    def project(self) -> str:
        return self.get("project")

    @property
    def author(self) -> str:
        return self.get("author")

    @property
    def date(self) -> str:
        return self.get("date")

    @property
    def identifier(self) -> str:
        return self.get("identifier")
