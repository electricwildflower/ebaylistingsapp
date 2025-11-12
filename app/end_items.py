"""UI view for items that have been ended."""

from __future__ import annotations

from typing import Any, Callable, Iterable

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date


def _format_date_display(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue
    return value


class EndItemsView(tk.Frame):
    """Displays items that have been marked as ended."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        text_color: str,
        card_bg: str,
        items_provider: Iterable[dict[str, Any]] | None = None,
        open_callback: Callable[[str], None] | None = None,
        edit_callback: Callable[[str, bool], None] | None = None,
        restore_callback: Callable[[str], None] | None = None,
        delete_callback: Callable[[str], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=primary_bg, **kwargs)
        self.primary_bg = primary_bg
        self.text_color = text_color
        self.card_bg = card_bg
        self._items: list[dict[str, Any]] = list(items_provider or [])
        self._filtered: list[dict[str, Any]] = []
        self._open_callback = open_callback
        self._edit_callback = edit_callback
        self._restore_callback = restore_callback
        self._delete_callback = delete_callback

        self.search_value = tk.StringVar()
        self._is_mousewheel_bound = False
        self._image_cache: dict[str, tk.PhotoImage] = {}
        self._card_images: list[tk.PhotoImage] = []

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

        tk.Label(
            title_wrapper,
            text="Ended Items",
            font=("Segoe UI Semibold", 26),
            bg=self.primary_bg,
            fg=self.text_color,
        ).pack()

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
        base_items = [
            item for item in self._items if (item.get("status") or "active").lower() == "ended"
        ]

        if search_text:
            filtered = [
                item
                for item in base_items
                if search_text in (item.get("name") or "").lower()
                or search_text in (item.get("description") or "").lower()
                or search_text in (item.get("notes") or "").lower()
                or search_text in (item.get("category") or "").lower()
                or search_text in _format_date_display(item.get("date_added")).lower()
                or search_text in _format_date_display(item.get("end_date")).lower()
            ]
        else:
            filtered = list(base_items)

        self._filtered = filtered
        self._render_items()

    # --------------------------------------------------------------------------------------------
    # Rendering
    # --------------------------------------------------------------------------------------------
    def _render_items(self) -> None:
        for child in self.list_container.winfo_children():
            child.destroy()
        self._card_images.clear()

        if not self._filtered:
            tk.Label(
                self.list_container,
                text="No ended items yet.",
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

            content = tk.Frame(card, bg=self.card_bg)
            content.pack(fill="x")

            image_url = item.get("image_url") or ""
            if image_url:
                image_label = tk.Label(content, bg=self.card_bg)
                image_label.pack(side="left", padx=(0, 16))
                photo = self._load_image(image_url)
                if photo:
                    image_label.configure(image=photo)
                    image_label.image = photo  # type: ignore[attr-defined]
                    self._card_images.append(photo)
                else:
                    image_label.configure(text="No image", fg="#60738A", font=("Segoe UI", 9))

            info = tk.Frame(content, bg=self.card_bg)
            info.pack(side="left", expand=True, fill="x")

            name = item.get("name") or item.get("description") or "Item"
            tk.Label(
                info,
                text=name,
                font=("Segoe UI Semibold", 15),
                bg=self.card_bg,
                fg=self.text_color,
            ).pack(anchor="w")

            subtitle_parts: list[str] = []
            if item.get("category"):
                subtitle_parts.append(f"Category: {item['category']}")
            if item.get("date_added"):
                subtitle_parts.append(f"Added: {_format_date_display(item.get('date_added'))}")
            if item.get("end_date"):
                subtitle_parts.append(f"Ended: {_format_date_display(item.get('end_date'))}")
            if subtitle_parts:
                tk.Label(
                    info,
                    text=" • ".join(subtitle_parts),
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#41566F",
                ).pack(anchor="w", pady=(4, 6))

            notes = item.get("notes")
            if notes:
                tk.Label(
                    info,
                    text=f"Notes: {notes}",
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#60738A",
                    wraplength=520,
                    justify="left",
                ).pack(anchor="w")

            actions = tk.Frame(card, bg=self.card_bg)
            actions.pack(anchor="e", pady=(12, 0))

            ttk.Button(
                actions,
                text="Open",
                style="Secondary.TButton",
                command=lambda item_id=item.get("id"): self._handle_open(item_id),
            ).pack(side="left", padx=(0, 8))

            ttk.Button(
                actions,
                text="Edit Item",
                style="Secondary.TButton",
                command=lambda item_id=item.get("id"): self._handle_edit(item_id),
            ).pack(side="left", padx=(0, 8))

            ttk.Button(
                actions,
                text="Restore",
                style="Secondary.TButton",
                command=lambda item_id=item.get("id"), name=item.get("name"): self._handle_restore(item_id, name),
            ).pack(side="left", padx=(0, 8))

            ttk.Button(
                actions,
                text="Delete",
                style="Secondary.TButton",
                command=lambda item_id=item.get("id"), name=item.get("name"): self._handle_delete(item_id, name),
            ).pack(side="left")

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

    # --------------------------------------------------------------------------------------------
    # Actions
    # --------------------------------------------------------------------------------------------
    def _handle_open(self, item_id: str | None) -> None:
        if item_id and self._open_callback:
            self._open_callback(item_id)

    def _handle_edit(self, item_id: str | None) -> None:
        if item_id and self._edit_callback:
            self._edit_callback(item_id, True)

    def _handle_restore(self, item_id: str | None, name: str | None) -> None:
        if not item_id or not self._restore_callback:
            return
        answer = messagebox.askyesno(
            "Restore Item",
            f"Move \"{name or 'this item'}\" back to active listings?",
            parent=self.winfo_toplevel(),
            icon="question",
        )
        if answer:
            self._restore_callback(item_id)
            self._apply_filters()

    def _handle_delete(self, item_id: str | None, name: str | None) -> None:
        if not item_id or not self._delete_callback:
            return
        answer = messagebox.askyesno(
            "Delete Item",
            f"Are you sure you want to delete \"{name or 'this item'}\"?",
            parent=self.winfo_toplevel(),
            icon="warning",
        )
        if answer:
            self._delete_callback(item_id)
            self._apply_filters()

    def _load_image(self, url: str) -> tk.PhotoImage | None:
        if not url:
            return None
        if url in self._image_cache:
            return self._image_cache[url]
        try:
            from PIL import Image, ImageTk  # type: ignore
            import urllib.request
            from io import BytesIO
        except Exception:  # pragma: no cover - Pillow optional
            return None
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
            image = Image.open(BytesIO(data))
            image.thumbnail((120, 120))
            photo = ImageTk.PhotoImage(image)
            self._image_cache[url] = photo
            return photo
        except Exception:  # pragma: no cover - best effort
            return None

