"""UI components and data handling for adding items."""

from __future__ import annotations

import json
import os
import urllib.request
from io import BytesIO
from typing import Any, Callable
from uuid import uuid4

import tkinter as tk
from tkinter import messagebox, ttk

try:
    from PIL import Image, ImageTk  # type: ignore
except ImportError:  # pragma: no cover - handled by runtime dependency
    Image = None  # type: ignore
    ImageTk = None  # type: ignore


class AddItemView(tk.Frame):
    """Visual layout and form handling for adding items."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        text_color: str,
        storage_path: str | None = None,
        categories_provider: Callable[[], list[dict[str, str]]] | None = None,
        on_items_changed: Callable[[list[dict[str, Any]]], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=primary_bg, **kwargs)
        self.primary_bg = primary_bg
        self.text_color = text_color
        self.card_bg = "#FFFFFF"
        self.storage_path = storage_path
        self.categories_provider = categories_provider
        self._items_changed_callback = on_items_changed

        self.items: list[dict[str, Any]] = []
        self._dialog_backdrop: tk.Frame | None = None
        self._dialog: tk.Frame | None = None
        self._dialog_vars: dict[str, tk.Variable] = {}
        self._description_text: tk.Text | None = None
        self._notes_text: tk.Text | None = None
        self._image_preview_label: tk.Label | None = None
        self._image_photo: tk.PhotoImage | None = None  # keep reference

        self._load_items()
        self._build_layout()
        self._render_items_list()

    # --------------------------------------------------------------------------------------------
    # UI construction
    # --------------------------------------------------------------------------------------------
    def _build_layout(self) -> None:
        container = tk.Frame(self, bg=self.primary_bg)
        container.pack(fill="both", expand=True, pady=(40, 0))

        header = tk.Label(
            container,
            text="Add Items",
            font=("Segoe UI Semibold", 22),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(pady=(0, 20))

        ttk.Button(
            container,
            text="Add a New Item",
            style="Primary.TButton",
            command=self.open_add_item_dialog,
        ).pack()

        self.items_list_container = tk.Frame(container, bg=self.primary_bg)
        self.items_list_container.pack(fill="both", expand=True, pady=(30, 0))

    def open_add_item_dialog(self) -> None:
        if not self.storage_path:
            messagebox.showerror(
                "Add Item",
                "Please configure a storage location before adding items.",
                parent=self.winfo_toplevel(),
            )
            return

        if self._dialog_backdrop and self._dialog_backdrop.winfo_exists():
            self._close_dialog()

        self._dialog_backdrop = tk.Frame(self, bg=self.primary_bg)
        self._dialog_backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._dialog_backdrop.lift()

        wrapper = tk.Frame(self._dialog_backdrop, bg=self.primary_bg)
        wrapper.pack(expand=True, pady=40)

        header = tk.Label(
            wrapper,
            text="Add a New Item",
            font=("Segoe UI Semibold", 20),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(pady=(0, 16))

        self._dialog = tk.Frame(wrapper, bg=self.card_bg, padx=26, pady=26)
        self._dialog.pack()

        self._build_form(self._dialog)

    def _build_form(self, parent: tk.Frame) -> None:
        categories = self._category_names()
        self._dialog_vars["category"] = tk.StringVar(value=categories[0] if categories else "")
        self._dialog_vars["date_added"] = tk.StringVar()
        self._dialog_vars["end_date"] = tk.StringVar()
        self._dialog_vars["image_url"] = tk.StringVar()

        ttk.Label(parent, text="Category", style="TLabel").grid(row=0, column=0, sticky="w")
        self.category_combo = ttk.Combobox(
            parent,
            values=categories,
            textvariable=self._dialog_vars["category"],
            state="readonly",
            width=42,
        )
        self.category_combo.grid(row=1, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Description", style="TLabel").grid(row=2, column=0, sticky="w")
        self._description_text = tk.Text(parent, width=44, height=4, font=("Segoe UI", 11))
        self._description_text.grid(row=3, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Notes", style="TLabel").grid(row=4, column=0, sticky="w")
        self._notes_text = tk.Text(parent, width=44, height=3, font=("Segoe UI", 11))
        self._notes_text.grid(row=5, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Date Added (YYYY-MM-DD)", style="TLabel").grid(row=6, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self._dialog_vars["date_added"]).grid(row=7, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="End Date (YYYY-MM-DD)", style="TLabel").grid(row=8, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self._dialog_vars["end_date"]).grid(row=9, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Image URL", style="TLabel").grid(row=10, column=0, sticky="w")
        url_row = tk.Frame(parent, bg=self.card_bg)
        url_row.grid(row=11, column=0, sticky="we", pady=(4, 12))
        url_row.columnconfigure(0, weight=1)

        ttk.Entry(url_row, textvariable=self._dialog_vars["image_url"]).grid(row=0, column=0, sticky="we", padx=(0, 12))
        ttk.Button(url_row, text="Preview", command=self._update_image_preview, width=10).grid(row=0, column=1)

        preview_container = tk.Frame(parent, bg=self.card_bg)
        preview_container.grid(row=12, column=0, sticky="we", pady=(4, 16))
        preview_container.columnconfigure(0, weight=1)

        self._image_preview_label = tk.Label(
            preview_container,
            text="Image preview will appear here.",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg="#60738A",
            justify="center",
        )
        self._image_preview_label.pack(fill="both", expand=True)

        button_row = tk.Frame(parent, bg=self.card_bg)
        button_row.grid(row=13, column=0, sticky="e", pady=(10, 0))

        ttk.Button(button_row, text="Save", style="Primary.TButton", command=self._handle_save).pack(side="left")
        ttk.Button(button_row, text="Cancel", style="Secondary.TButton", command=self._close_dialog).pack(
            side="left", padx=(12, 0)
        )

        parent.columnconfigure(0, weight=1)

    # --------------------------------------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------------------------------------
    def _handle_save(self) -> None:
        if not self._dialog:
            return

        category = self._dialog_vars["category"].get().strip()
        description = (self._description_text.get("1.0", "end").strip() if self._description_text else "")
        notes = self._notes_text.get("1.0", "end").strip() if self._notes_text else ""
        date_added = self._dialog_vars["date_added"].get().strip()
        end_date = self._dialog_vars["end_date"].get().strip()
        image_url = self._dialog_vars["image_url"].get().strip()

        if not category:
            messagebox.showerror("Add Item", "Please select a category.", parent=self.winfo_toplevel())
            return

        if not description:
            messagebox.showerror("Add Item", "Please provide a description for the item.", parent=self.winfo_toplevel())
            return

        item = {
            "id": uuid4().hex,
            "category": category,
            "description": description,
            "notes": notes,
            "date_added": date_added,
            "end_date": end_date,
            "image_url": image_url,
        }

        self.items.append(item)
        self._persist_items()
        self._render_items_list()
        self._notify_items_changed()
        self._close_dialog()

    def _update_image_preview(self) -> None:
        if not self._image_preview_label:
            return

        url = self._dialog_vars["image_url"].get().strip()
        if not url:
            self._image_preview_label.configure(text="Enter an image URL above and click Preview.")
            self._image_photo = None
            return

        if Image is None or ImageTk is None:
            self._image_preview_label.configure(text="Image preview requires the Pillow library.")
            return

        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
        except Exception as exc:  # pragma: no cover - UI feedback
            self._image_preview_label.configure(text=f"Unable to load image.\n{exc}")
            self._image_photo = None
            return

        try:
            image = Image.open(BytesIO(data))
            image.thumbnail((320, 240))
            self._image_photo = ImageTk.PhotoImage(image)
        except Exception as exc:  # pragma: no cover - UI feedback
            self._image_preview_label.configure(text=f"Unable to display image.\n{exc}")
            self._image_photo = None
            return

        self._image_preview_label.configure(image=self._image_photo, text="")

    def _close_dialog(self) -> None:
        if self._dialog and self._dialog.winfo_exists():
            self._dialog.destroy()
        if self._dialog_backdrop and self._dialog_backdrop.winfo_exists():
            self._dialog_backdrop.place_forget()
            self._dialog_backdrop.destroy()

        self._dialog = None
        self._dialog_backdrop = None
        self._dialog_vars.clear()
        self._description_text = None
        self._notes_text = None
        self._image_preview_label = None
        self._image_photo = None

    # --------------------------------------------------------------------------------------------
    # Rendering
    # --------------------------------------------------------------------------------------------
    def _render_items_list(self) -> None:
        for child in self.items_list_container.winfo_children():
            child.destroy()

        if not self.items:
            placeholder = tk.Label(
                self.items_list_container,
                text="No items added yet. Click \"Add a New Item\" to get started.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            )
            placeholder.pack(pady=10)
            return

        # Show most recent first
        for item in reversed(self.items):
            card = tk.Frame(
                self.items_list_container,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=16,
                pady=12,
            )
            card.pack(fill="x", padx=40, pady=(0, 12))

            title = tk.Label(
                card,
                text=f"{item.get('category', '')} • {item.get('date_added') or 'No date'}",
                font=("Segoe UI Semibold", 13),
                bg=self.card_bg,
                fg=self.text_color,
            )
            title.pack(anchor="w")

            description = item.get("description", "")
            if description:
                tk.Label(
                    card,
                    text=description,
                    font=("Segoe UI", 11),
                    bg=self.card_bg,
                    fg="#41566F",
                    wraplength=520,
                    justify="left",
                ).pack(anchor="w", pady=(6, 4))

            notes = item.get("notes")
            if notes:
                tk.Label(
                    card,
                    text=f"Notes: {notes}",
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#5A6D82",
                    wraplength=520,
                    justify="left",
                ).pack(anchor="w", pady=(0, 4))

            end_date = item.get("end_date")
            if end_date:
                tk.Label(
                    card,
                    text=f"End Date: {end_date}",
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#6F7F92",
                ).pack(anchor="w")

    # --------------------------------------------------------------------------------------------
    # Data helpers
    # --------------------------------------------------------------------------------------------
    def set_storage_path(self, storage_path: str) -> None:
        self.storage_path = storage_path
        self._load_items()
        self._render_items_list()
        self._notify_items_changed()

    def get_items(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self.items]

    def _persist_items(self) -> None:
        data_path = self._data_file_path()
        if not data_path:
            return

        try:
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            with open(data_path, "w", encoding="utf-8") as file:
                json.dump(self.items, file, indent=2)
        except OSError as exc:
            messagebox.showerror(
                "Items",
                f"Unable to save items data.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )

    def _load_items(self) -> None:
        data_path = self._data_file_path()
        if not data_path or not os.path.exists(data_path):
            self.items = []
            return

        try:
            with open(data_path, "r", encoding="utf-8") as file:
                raw_data: Any = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showwarning(
                "Items",
                f"Unable to load items data.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )
            self.items = []
            return

        parsed: list[dict[str, Any]] = []
        if isinstance(raw_data, list):
            for entry in raw_data:
                if not isinstance(entry, dict):
                    continue
                parsed.append(dict(entry))
        self.items = parsed

    def _data_file_path(self) -> str | None:
        if not self.storage_path:
            return None
        return os.path.join(self.storage_path, "items.json")

    def _category_names(self) -> list[str]:
        if not self.categories_provider:
            return []
        return [category.get("name", "") for category in self.categories_provider() if category.get("name")]

    def _notify_items_changed(self) -> None:
        if self._items_changed_callback:
            self._items_changed_callback(self.get_items())


