from __future__ import annotations

import customtkinter as ctk

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


class MetadataSection(ctk.CTkFrame):
    """Two-column grid of labelled text entry fields for document metadata."""

    def __init__(self, master: ctk.CTkFrame, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        self.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self, text="Metadata", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        self._entries: dict[str, ctk.CTkEntry] = {}
        for idx, (attr, label, placeholder) in enumerate(_METADATA_FIELDS):
            col = idx % 2
            row = (idx // 2) + 1
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.grid(row=row, column=col, sticky="ew", padx=(0, 8) if col == 0 else 0, pady=3)
            frame.columnconfigure(0, weight=1)

            ctk.CTkLabel(frame, text=label, anchor="w").grid(
                row=0, column=0, sticky="w", pady=(0, 2)
            )
            entry = ctk.CTkEntry(frame, placeholder_text=placeholder)
            entry.grid(row=1, column=0, sticky="ew")
            self._entries[attr] = entry

    def get(self, field: str) -> str:
        return str(self._entries[field].get()).strip()

    def set(self, field: str, value: str) -> None:
        entry = self._entries[field]
        entry.delete(0, "end")
        entry.insert(0, value)

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
