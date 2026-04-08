from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from notion_prettify_gui import styles
from notion_prettify_gui.models.options import PrettifyOptions
from notion_prettify_gui.services.cfg_loader import load_cfg
from notion_prettify_gui.services.runner import PrettifyRunner, RunResult, RunStatus
from notion_prettify_gui.widgets.file_section import FileSection
from notion_prettify_gui.widgets.metadata_section import MetadataSection
from notion_prettify_gui.widgets.options_section import OptionsSection

_APP_TITLE = "Notion Export Prettify"
_APP_VERSION = "0.1.0"
_LOG_MIN_HEIGHT = 180


class _RunButton(QWidget):
    """CTA button with status label below it."""

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from PySide6.QtWidgets import QPushButton

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._button = QPushButton("Generate PDF")
        self._button.setProperty("role", "primary")
        self._button.setMinimumHeight(42)
        self._button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._button.clicked.connect(self.clicked)
        layout.addWidget(self._button)

        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = QFont()
        font.setPointSize(10)
        self._status.setFont(font)
        layout.addWidget(self._status)

    def set_running(self, running: bool) -> None:
        self._button.setEnabled(not running)
        if running:
            self._button.setText("Generating…")
        else:
            self._button.setText("Generate PDF")

    def set_status(self, message: str, *, error: bool = False) -> None:
        self._status.setText(message)
        self._status.setProperty("role", "status-error" if error else "status-success")
        self._status.style().unpolish(self._status)
        self._status.style().polish(self._status)


class App(QMainWindow):
    """Main application window."""

    _log_signal = Signal(str)
    _complete_signal = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(_APP_TITLE)
        self.setMinimumSize(700, 700)
        self.resize(800, 880)

        self._runner = PrettifyRunner()

        self._log_signal.connect(self._append_log)
        self._complete_signal.connect(self._on_complete)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_divider(), 0)
        layout.addSpacing(16)

        self._file_section = FileSection()
        self._file_section.template_changed.connect(self._on_template_changed)
        layout.addWidget(self._file_section)
        layout.addSpacing(12)

        self._metadata_section = MetadataSection()
        layout.addWidget(self._metadata_section)
        layout.addSpacing(12)

        self._options_section = OptionsSection()
        layout.addWidget(self._options_section)
        layout.addSpacing(20)

        self._run_widget = _RunButton()
        self._run_widget.clicked.connect(self._on_run)
        layout.addWidget(self._run_widget)
        layout.addSpacing(12)

        layout.addWidget(self._build_log_area())
        layout.addSpacing(8)
        layout.addStretch()

    def _build_header(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("header")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title = QLabel(_APP_TITLE)
        title.setProperty("role", "heading")
        title_font = QFont()
        title_font.setPointSize(17)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title_row.addWidget(title)

        version = QLabel(f"v{_APP_VERSION}")
        version.setProperty("role", "subtitle")
        version_font = QFont()
        version_font.setPointSize(10)
        version.setFont(version_font)
        version.setAlignment(Qt.AlignmentFlag.AlignBottom)
        title_row.addWidget(version)
        title_row.addStretch()

        layout.addLayout(title_row)

        subtitle = QLabel("Turn a Notion page export into a styled PDF document.")
        subtitle.setProperty("role", "subtitle")
        sub_font = QFont()
        sub_font.setPointSize(11)
        subtitle.setFont(sub_font)
        layout.addWidget(subtitle)

        return widget

    def _build_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        return line

    def _build_log_area(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel("Output")
        label_font = QFont()
        label_font.setPointSize(11)
        label_font.setWeight(QFont.Weight.DemiBold)
        label.setFont(label_font)
        layout.addWidget(label)

        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setMinimumHeight(_LOG_MIN_HEIGHT)
        self._log_box.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._log_box)

        return widget

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_template_changed(self, path: Path | None) -> None:
        if path is None or path.suffix.lower() != ".cfg":
            return
        if not path.exists():
            return
        try:
            cfg = load_cfg(path)
        except Exception:
            return

        for field, value in cfg.metadata.items():
            if field == "description":
                continue
            try:
                self._metadata_section.set(field, value)
            except KeyError:
                pass

        for field, value in cfg.controls.items():
            self._options_section.set(field, value)

    def _on_run(self) -> None:
        if self._file_section.input_file is None:
            self._run_widget.set_status(
                "Please select an input file first.", error=True
            )
            return

        options = PrettifyOptions(
            input_file=self._file_section.input_file,
            output=self._file_section.output,
            template=self._file_section.template,
            title=self._metadata_section.title,
            subtitle=self._metadata_section.subtitle,
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
        self._run_widget.set_running(True)
        self._run_widget.set_status("Running…")

        self._runner.run(
            options,
            on_output=self._log_signal.emit,
            on_complete=self._complete_signal.emit,
        )

    def _on_complete(self, result: RunResult) -> None:
        self._run_widget.set_running(False)
        if result.status == RunStatus.SUCCESS:
            self._run_widget.set_status("Done — PDF generated successfully.")
        else:
            code_str = (
                f" (exit code {result.return_code})" if result.return_code else ""
            )
            self._run_widget.set_status(
                f"Failed{code_str}. See output below.", error=True
            )

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _clear_log(self) -> None:
        self._log_box.clear()

    def _append_log(self, text: str) -> None:
        self._log_box.moveCursor(self._log_box.textCursor().MoveOperation.End)
        self._log_box.insertPlainText(text)
        self._log_box.ensureCursorVisible()


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    assert isinstance(app, QApplication)
    app.setStyleSheet(styles.STYLESHEET)
    window = App()
    window.show()
    sys.exit(app.exec())
