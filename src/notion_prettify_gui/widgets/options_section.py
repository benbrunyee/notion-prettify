from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_TOGGLE_FIELDS: list[tuple[str, str, str]] = [
    # (attribute_name, label_text, description)
    ("cover_page", "Cover page", "Add a cover page defined in the template"),
    ("heading_numbers", "Heading numbers", "Prefix headings with hierarchical numbers"),
    (
        "strip_internal_info",
        "Strip internal info",
        "Remove callouts and database properties",
    ),
    ("table_of_contents", "Table of contents", "Add a ToC if present in Notion"),
]

_STATE_CYCLE: list[bool | None] = [None, True, False]
_STATE_LABELS: dict[bool | None, str] = {None: "default", True: "on", False: "off"}
_STATE_ROLES: dict[bool | None, str] = {
    None: "toggle-default",
    True: "toggle-on",
    False: "toggle-off",
}


class _TriStateToggle(QWidget):
    """A label row with a pill-shaped button cycling: default → on → off."""

    def __init__(
        self, label: str, description: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._state: bool | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(label)
        text_col.addWidget(label_widget)

        desc_widget = QLabel(description)
        desc_widget.setProperty("role", "hint")
        text_col.addWidget(desc_widget)

        layout.addLayout(text_col, stretch=1)

        self._button = QPushButton(_STATE_LABELS[self._state])
        self._button.setProperty("role", _STATE_ROLES[self._state])
        self._button.setFixedWidth(68)
        self._button.clicked.connect(self._cycle)
        layout.addWidget(self._button)

    def _cycle(self) -> None:
        current_idx = _STATE_CYCLE.index(self._state)
        self._state = _STATE_CYCLE[(current_idx + 1) % len(_STATE_CYCLE)]
        self._button.setText(_STATE_LABELS[self._state])
        self._button.setProperty("role", _STATE_ROLES[self._state])
        # Force QSS re-evaluation after dynamic property change
        self._button.style().unpolish(self._button)
        self._button.style().polish(self._button)

    @property
    def value(self) -> bool | None:
        return self._state


class OptionsSection(QGroupBox):
    """Four tri-state toggles for the boolean CLI flags."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Options", parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self._toggles: dict[str, _TriStateToggle] = {}
        for attr, label, description in _TOGGLE_FIELDS:
            toggle = _TriStateToggle(label=label, description=description)
            layout.addWidget(toggle)
            self._toggles[attr] = toggle

        hint = QLabel(
            "Button cycles: default (omit flag)  →  on (--flag)  →  off (--no-flag)"
        )
        hint.setProperty("role", "hint")
        layout.addWidget(hint)

    @property
    def cover_page(self) -> bool | None:
        return self._toggles["cover_page"].value

    @property
    def heading_numbers(self) -> bool | None:
        return self._toggles["heading_numbers"].value

    @property
    def strip_internal_info(self) -> bool | None:
        return self._toggles["strip_internal_info"].value

    @property
    def table_of_contents(self) -> bool | None:
        return self._toggles["table_of_contents"].value
