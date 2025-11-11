"""UI components for the Add Category view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class AddCategoryView(tk.Frame):
    """Visual layout for the Add Category screen."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        text_color: str,
        **kwargs,
    ) -> None:
        super().__init__(master, bg=primary_bg, **kwargs)
        self.primary_bg = primary_bg
        self.text_color = text_color

        self.search_value = tk.StringVar()

        self._build_layout()

    def _build_layout(self) -> None:
        container = tk.Frame(self, bg=self.primary_bg)
        container.pack(fill="both", expand=True, pady=(60, 0))

        self._build_title(container)
        self._build_search(container)
        self._build_actions(container)

    def _build_title(self, parent: tk.Frame) -> None:
        title_frame = tk.Frame(parent, bg=self.primary_bg)
        title_frame.pack(pady=(0, 24))

        ebay_palette = ("#E53238", "#0064D2", "#F5AF02", "#86B817")
        for index, char in enumerate("Categories"):
            color = ebay_palette[index % len(ebay_palette)]
            letter = tk.Label(
                title_frame,
                text=char,
                font=("Segoe UI Semibold", 28),
                bg=self.primary_bg,
                fg=color,
            )
            letter.pack(side="left")

    def _build_search(self, parent: tk.Frame) -> None:
        search_container = tk.Frame(parent, bg=self.primary_bg)
        search_container.pack(pady=(0, 20))

        entry = ttk.Entry(
            search_container,
            width=36,
            textvariable=self.search_value,
            font=("Segoe UI", 12),
        )
        entry.pack(ipady=6)
        entry.focus_set()

    def _build_actions(self, parent: tk.Frame) -> None:
        ttk.Button(
            parent,
            text="Add a Category",
            style="Primary.TButton",
            command=self._handle_add_category,
        ).pack()

    def _handle_add_category(self) -> None:  # pragma: no cover - placeholder hook
        """Placeholder handler until business logic is wired up."""
        pass

