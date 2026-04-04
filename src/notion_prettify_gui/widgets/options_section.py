from __future__ import annotations

import customtkinter as ctk

_TOGGLE_FIELDS: list[tuple[str, str, str]] = [
    # (attribute_name, label_text, tooltip_text)
    ("cover_page", "Cover page", "Add a cover page (if defined in the template)"),
    ("heading_numbers", "Heading numbers", "Prefix headings with hierarchical numbers"),
    (
        "strip_internal_info",
        "Strip internal info",
        "Remove callouts and database properties from output",
    ),
    ("table_of_contents", "Table of contents", "Add a table of contents (if present in Notion)"),
]

# Maps each switch to three states: None → unset, True → on, False → off
_STATE_CYCLE: list[bool | None] = [None, True, False]
_STATE_LABELS: dict[bool | None, str] = {None: "default", True: "on", False: "off"}


class _TriStateSwitch(ctk.CTkFrame):
    """A switch that cycles through three states: default / on / off."""

    def __init__(self, master: ctk.CTkFrame, label: str, tooltip: str, **kwargs: object) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._state: bool | None = None

        self.columnconfigure(1, weight=1)

        self._switch = ctk.CTkSwitch(
            self,
            text="",
            width=44,
            command=self._on_toggle,
        )
        self._switch.grid(row=0, column=0, padx=(0, 8))

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=0, column=1, sticky="ew")
        inner.columnconfigure(0, weight=1)

        ctk.CTkLabel(inner, text=label, anchor="w").grid(row=0, column=0, sticky="w")
        self._state_label = ctk.CTkLabel(
            inner,
            text="default",
            anchor="w",
            text_color=("gray50", "gray60"),
            font=ctk.CTkFont(size=11),
        )
        self._state_label.grid(row=1, column=0, sticky="w")

    def _on_toggle(self) -> None:
        # The underlying CTkSwitch is binary; we use it as a trigger and
        # cycle through our own three-state logic instead.
        current_idx = _STATE_CYCLE.index(self._state)
        next_idx = (current_idx + 1) % len(_STATE_CYCLE)
        self._state = _STATE_CYCLE[next_idx]
        self._sync_switch()

    def _sync_switch(self) -> None:
        if self._state is True:
            self._switch.select()
        else:
            self._switch.deselect()
        self._state_label.configure(text=_STATE_LABELS[self._state])

    @property
    def value(self) -> bool | None:
        return self._state


class OptionsSection(ctk.CTkFrame):
    """Four tri-state toggles for the boolean CLI flags."""

    def __init__(self, master: ctk.CTkFrame, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        self.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self, text="Options", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        self._switches: dict[str, _TriStateSwitch] = {}
        for idx, (attr, label, tooltip) in enumerate(_TOGGLE_FIELDS):
            col = idx % 2
            row = (idx // 2) + 1
            switch = _TriStateSwitch(self, label=label, tooltip=tooltip)
            switch.grid(row=row, column=col, sticky="ew", padx=(0, 12) if col == 0 else 0, pady=4)
            self._switches[attr] = switch

        note = "Switches cycle: default (omit flag) → on (--flag) → off (--no-flag)"
        ctk.CTkLabel(
            self, text=note, anchor="w", text_color=("gray50", "gray60"), font=ctk.CTkFont(size=11)
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

    @property
    def cover_page(self) -> bool | None:
        return self._switches["cover_page"].value

    @property
    def heading_numbers(self) -> bool | None:
        return self._switches["heading_numbers"].value

    @property
    def strip_internal_info(self) -> bool | None:
        return self._switches["strip_internal_info"].value

    @property
    def table_of_contents(self) -> bool | None:
        return self._switches["table_of_contents"].value
