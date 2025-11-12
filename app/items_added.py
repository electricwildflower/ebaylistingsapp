"""UI view for browsing items that have been added."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import tkinter as tk
from tkinter import ttk


class ItemsAddedView(tk.Frame):
    """Displays saved items with search and ordering controls."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        text_color: str,
        card_bg: str,
        items_provider: Iterable[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=primary_bg, **kwargs)
        self.primary_bg = primary_bg
        self.text_color = text_color
        self.card_bg = card_bg
        self._items: list[dict[str, Any]] = list(items_provider or [])
        self._filtered: list[dict[str, Any]] = []

        self.search_value = tk.StringVar()
        self.order_value = tk.StringVar(value="Newest added")
        self._is_mousewheel_bound = False

        self._build_layout()
        self.set_items(self._items)

    # --------------------------------------------------------------------------------------------
    # Layout
    # --------------------------------------------------------------------------------------------
    def _build_layout(self) -> None:
        container = tk.Frame(self, bg=self.primary_bg)
        container.pack(fill="both", expand=True, pady=(40, 0))

        self.canvas = tk.Canvas(
            container,
            bg=self.primary_bg,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._canvas_frame = tk.Frame(self.canvas, bg=self.primary_bg)
        self._canvas_window_id = self.canvas.create_window((0, 0), window=self._canvas_frame, anchor="nw")

        self._canvas_frame.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._match_canvas_width)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self._build_title(self._canvas_frame)
        self._build_filters(self._canvas_frame)
        self._build_list_container(self._canvas_frame)

    def _build_title(self, parent: tk.Frame) -> None:
        title_wrapper = tk.Frame(parent, bg=self.primary_bg)
        title_wrapper.pack(pady=(0, 24))

        ebay_palette = ("#E53238", "#0064D2", "#F5AF02", "#86B817")
        for index, char in enumerate("Items Added"):
            color = ebay_palette[index % len(ebay_palette)]
            tk.Label(
                title_wrapper,
                text=char,
                font=("Segoe UI Semibold", 28),
                bg=self.primary_bg,
                fg=color,
            ).pack(side="left")

    def _build_filters(self, parent: tk.Frame) -> None:
        filters = tk.Frame(parent, bg=self.primary_bg)
        filters.pack(fill="x", padx=40, pady=(0, 20))

        search_label = tk.Label(
            filters,
            text="Search",
            font=("Segoe UI", 11),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        search_label.grid(row=0, column=0, sticky="w")

        search_entry = ttk.Entry(
            filters,
            textvariable=self.search_value,
            width=32,
        )
        search_entry.grid(row=1, column=0, sticky="we", pady=(4, 0))
        search_entry.focus_set()
        self.search_value.trace_add("write", self._handle_filter_change)

        order_label = tk.Label(
            filters,
            text="Order",
            font=("Segoe UI", 11),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        order_label.grid(row=0, column=1, sticky="w", padx=(24, 0))

        order_combo = ttk.Combobox(
            filters,
            textvariable=self.order_value,
            values=("Newest added", "Oldest added"),
            state="readonly",
            width=20,
        )
        order_combo.grid(row=1, column=1, sticky="w", padx=(24, 0), pady=(4, 0))
        order_combo.bind("<<ComboboxSelected>>", lambda _event: self._handle_filter_change())

        filters.columnconfigure(0, weight=1)

    def _build_list_container(self, parent: tk.Frame) -> None:
        self.list_container = tk.Frame(parent, bg=self.primary_bg)
        self.list_container.pack(fill="both", expand=True, padx=40, pady=(10, 40))

    # --------------------------------------------------------------------------------------------
    # Data handling
    # --------------------------------------------------------------------------------------------
    def set_items(self, items: Iterable[dict[str, Any]]) -> None:
        self._items = list(items)
        self._apply_filters()

    def _handle_filter_change(self, *_: Any) -> None:
        self._apply_filters()

    def _apply_filters(self) -> None:
        search_text = self.search_value.get().strip().lower()
        if search_text:
            filtered = [
                item
                for item in self._items
                if search_text in (item.get("name") or "").lower()
                or search_text in (item.get("description") or "").lower()
                or search_text in (item.get("notes") or "").lower()
                or search_text in (item.get("category") or "").lower()
            ]
        else:
            filtered = list(self._items)

        reverse = self.order_value.get() != "Oldest added"

        def sort_key(item: dict[str, Any]) -> tuple[int, str]:
            raw = item.get("date_added") or ""
            try:
                parsed = datetime.fromisoformat(raw)
                timestamp = int(parsed.timestamp())
            except (TypeError, ValueError):
                timestamp = 0
            return (timestamp, raw)

        filtered.sort(key=sort_key, reverse=reverse)
        self._filtered = filtered
        self._render_items()

    # --------------------------------------------------------------------------------------------
    # Rendering
    # --------------------------------------------------------------------------------------------
    def _render_items(self) -> None:
        for child in self.list_container.winfo_children():
            child.destroy()

        if not self._filtered:
            tk.Label(
                self.list_container,
                text="No items match the current filters.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            ).pack(pady=20)
            self._sync_scroll_region(None)
            return

        for item in self._filtered:
            card = tk.Frame(
                self.list_container,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=20,
                pady=16,
            )
            card.pack(fill="x", pady=(0, 12))

            name = item.get("name") or item.get("description") or "Item"
            tk.Label(
                card,
                text=name,
                font=("Segoe UI Semibold", 15),
                bg=self.card_bg,
                fg=self.text_color,
            ).pack(anchor="w")

            subtitle_parts: list[str] = []
            if item.get("category"):
                subtitle_parts.append(f"Category: {item['category']}")
            if item.get("date_added"):
                subtitle_parts.append(f"Added: {item['date_added']}")
            if item.get("end_date"):
                subtitle_parts.append(f"End: {item['end_date']}")
            if subtitle_parts:
                tk.Label(
                    card,
                    text=" • ".join(subtitle_parts),
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#41566F",
                ).pack(anchor="w", pady=(4, 6))

            description = item.get("description")
            if description:
                tk.Label(
                    card,
                    text=description,
                    font=("Segoe UI", 11),
                    bg=self.card_bg,
                    fg="#28374A",
                    wraplength=520,
                    justify="left",
                ).pack(anchor="w", pady=(0, 6))

            notes = item.get("notes")
            if notes:
                tk.Label(
                    card,
                    text=f"Notes: {notes}",
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#60738A",
                    wraplength=520,
                    justify="left",
                ).pack(anchor="w")

        self._sync_scroll_region(None)

    # --------------------------------------------------------------------------------------------
    # Scroll helpers
    # --------------------------------------------------------------------------------------------
    def _sync_scroll_region(self, _: Any) -> None:
        if hasattr(self, "canvas"):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _match_canvas_width(self, event: Any) -> None:
        if hasattr(self, "canvas") and hasattr(self, "_canvas_window_id"):
            self.canvas.itemconfigure(self._canvas_window_id, width=event.width)

    def _bind_mousewheel(self, _: Any) -> None:
        if self._is_mousewheel_bound:
            return
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self._is_mousewheel_bound = True

    def _unbind_mousewheel(self, _: Any) -> None:
        if not self._is_mousewheel_bound:
            return
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        self._is_mousewheel_bound = False

    def _on_mousewheel(self, event: Any) -> None:
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self.canvas.yview_scroll(1, "units")

