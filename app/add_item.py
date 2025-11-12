"""UI components and data handling for adding items."""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import date
from io import BytesIO
from typing import Any, Callable
from uuid import uuid4

import calendar

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
        self._is_mousewheel_bound = False
        self._date_picker_window: tk.Toplevel | None = None
        self._date_picker_state: dict[str, Any] = {}
        self._dialog_canvas: tk.Canvas | None = None
        self._dialog_mousewheel_bound = False
        self._dialog_canvas_window_id: int | None = None
        self._editing_item_id: str | None = None
        self._editing_item_status: str = "active"
        self._restore_on_save: bool = False

        self._load_items()
        self._build_layout()
        self._render_items_list()

    # --------------------------------------------------------------------------------------------
    # UI construction
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

        header = tk.Label(
            self._canvas_frame,
            text="Add Items",
            font=("Segoe UI Semibold", 22),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(pady=(0, 20))

        ttk.Button(
            self._canvas_frame,
            text="Add a New Item",
            style="Primary.TButton",
            command=self.open_add_item_dialog,
        ).pack()

        self.items_list_container = tk.Frame(self._canvas_frame, bg=self.primary_bg)
        self.items_list_container.pack(fill="both", expand=True, pady=(30, 0))

    def open_add_item_dialog(self, item_id: str | None = None) -> None:
        if not self.storage_path:
            messagebox.showerror(
                "Add Item",
                "Please configure a storage location before adding items.",
                parent=self.winfo_toplevel(),
            )
            return

        self._editing_item_id = item_id
        if item_id is None:
            self._restore_on_save = False
        item_data = self._find_item(item_id) if item_id else None
        self._editing_item_status = item_data.get("status", "active") if item_data else "active"

        if self._dialog_backdrop and self._dialog_backdrop.winfo_exists():
            self._close_dialog()

        self._dialog_backdrop = tk.Frame(self, bg=self.primary_bg)
        self._dialog_backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._dialog_backdrop.lift()

        wrapper = tk.Frame(self._dialog_backdrop, bg=self.primary_bg)
        wrapper.pack(expand=True, pady=40, padx=20)

        header = tk.Label(
            wrapper,
            text="Edit Item" if item_data else "Add a New Item",
            font=("Segoe UI Semibold", 20),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(pady=(0, 16))

        self._dialog_canvas = tk.Canvas(
            wrapper,
            bg=self.card_bg,
            highlightthickness=0,
            borderwidth=0,
            height=520,
            width=560,
        )
        self._dialog_canvas.pack(fill="both", expand=True)

        inner = tk.Frame(self._dialog_canvas, bg=self.card_bg)
        self._dialog_canvas_window_id = self._dialog_canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", self._sync_dialog_scroll_region)
        self._dialog_canvas.bind("<Configure>", self._match_dialog_canvas_width)
        self._dialog_canvas.bind("<Enter>", self._bind_dialog_mousewheel)
        self._dialog_canvas.bind("<Leave>", self._unbind_dialog_mousewheel)

        self._dialog = tk.Frame(inner, bg=self.card_bg, padx=26, pady=26)
        self._dialog.pack(fill="both", expand=True)

        self._build_form(self._dialog, item_data=item_data)

    def _build_form(self, parent: tk.Frame, item_data: dict[str, Any] | None = None) -> None:
        categories = self._category_names()
        self._dialog_vars["category"] = tk.StringVar(value=categories[0] if categories else "")
        self._dialog_vars["name"] = tk.StringVar()
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

        ttk.Label(parent, text="Item Name", style="TLabel").grid(row=2, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self._dialog_vars["name"]).grid(row=3, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Description", style="TLabel").grid(row=4, column=0, sticky="w")
        self._description_text = tk.Text(parent, width=44, height=4, font=("Segoe UI", 11))
        self._description_text.grid(row=5, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Notes", style="TLabel").grid(row=6, column=0, sticky="w")
        self._notes_text = tk.Text(parent, width=44, height=3, font=("Segoe UI", 11))
        self._notes_text.grid(row=7, column=0, sticky="we", pady=(4, 16))

        ttk.Label(parent, text="Date Added (YYYY-MM-DD)", style="TLabel").grid(row=8, column=0, sticky="w")
        date_added_row = tk.Frame(parent, bg=self.card_bg)
        date_added_row.grid(row=9, column=0, sticky="we", pady=(4, 16))
        date_added_row.columnconfigure(0, weight=1)
        ttk.Entry(date_added_row, textvariable=self._dialog_vars["date_added"]).grid(row=0, column=0, sticky="we")
        ttk.Button(date_added_row, text="Pick Date", command=lambda: self._open_date_picker("date_added")).grid(
            row=0, column=1, padx=(12, 0)
        )

        ttk.Label(parent, text="End Date (YYYY-MM-DD)", style="TLabel").grid(row=10, column=0, sticky="w")
        end_date_row = tk.Frame(parent, bg=self.card_bg)
        end_date_row.grid(row=11, column=0, sticky="we", pady=(4, 16))
        end_date_row.columnconfigure(0, weight=1)
        ttk.Entry(end_date_row, textvariable=self._dialog_vars["end_date"]).grid(row=0, column=0, sticky="we")
        ttk.Button(end_date_row, text="Pick Date", command=lambda: self._open_date_picker("end_date")).grid(
            row=0, column=1, padx=(12, 0)
        )

        ttk.Label(parent, text="Image URL", style="TLabel").grid(row=12, column=0, sticky="w")
        url_row = tk.Frame(parent, bg=self.card_bg)
        url_row.grid(row=13, column=0, sticky="we", pady=(4, 12))
        url_row.columnconfigure(0, weight=1)

        ttk.Entry(url_row, textvariable=self._dialog_vars["image_url"]).grid(row=0, column=0, sticky="we", padx=(0, 12))
        ttk.Button(url_row, text="Preview", command=self._update_image_preview, width=10).grid(row=0, column=1)

        preview_container = tk.Frame(parent, bg=self.card_bg)
        preview_container.grid(row=14, column=0, sticky="we", pady=(4, 16))
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
        button_row.grid(row=15, column=0, sticky="e", pady=(10, 0))

        ttk.Button(button_row, text="Save", style="Primary.TButton", command=self._handle_save).pack(side="left")
        ttk.Button(button_row, text="Cancel", style="Secondary.TButton", command=self._close_dialog).pack(
            side="left", padx=(12, 0)
        )

        parent.columnconfigure(0, weight=1)

        if item_data:
            self._populate_form(item_data)

    def _populate_form(self, item: dict[str, Any]) -> None:
        self._dialog_vars["category"].set(item.get("category", ""))
        self._dialog_vars["name"].set(item.get("name", ""))
        self._dialog_vars["date_added"].set(item.get("date_added", ""))
        self._dialog_vars["end_date"].set(item.get("end_date", ""))
        self._dialog_vars["image_url"].set(item.get("image_url", ""))
        self._editing_item_status = item.get("status", "active")
        if self._description_text is not None:
            self._description_text.delete("1.0", "end")
            self._description_text.insert("1.0", item.get("description", ""))
        if self._notes_text is not None:
            self._notes_text.delete("1.0", "end")
            self._notes_text.insert("1.0", item.get("notes", ""))

    # --------------------------------------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------------------------------------
    def _handle_save(self) -> None:
        if not self._dialog:
            return

        category = self._dialog_vars["category"].get().strip()
        name = self._dialog_vars["name"].get().strip()
        description = (self._description_text.get("1.0", "end").strip() if self._description_text else "")
        notes = self._notes_text.get("1.0", "end").strip() if self._notes_text else ""
        date_added = self._dialog_vars["date_added"].get().strip()
        end_date = self._dialog_vars["end_date"].get().strip()
        image_url = self._dialog_vars["image_url"].get().strip()

        if not category:
            messagebox.showerror("Add Item", "Please select a category.", parent=self.winfo_toplevel())
            return

        if not name:
            messagebox.showerror("Add Item", "Please provide a name for the item.", parent=self.winfo_toplevel())
            return

        if not description:
            messagebox.showerror("Add Item", "Please provide a description for the item.", parent=self.winfo_toplevel())
            return

        status = self._editing_item_status or "active"
        if self._restore_on_save and status.lower() == "ended":
            status = "active"

        item = {
            "id": self._editing_item_id or uuid4().hex,
            "category": category,
            "name": name,
            "description": description,
            "notes": notes,
            "date_added": date_added,
            "end_date": end_date,
            "image_url": image_url,
            "status": status,
        }

        if self._editing_item_id:
            for index, existing in enumerate(self.items):
                if existing.get("id") == self._editing_item_id:
                    self.items[index] = item
                    break
        else:
            self.items.append(item)

        self._editing_item_status = status
        self._restore_on_save = False

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
        self._unbind_dialog_mousewheel(None)
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
        self._dialog_canvas = None
        self._dialog_canvas_window_id = None
        self._dialog_mousewheel_bound = False
        self._editing_item_id = None
        self._editing_item_status = "active"
        self._restore_on_save = False
        self._close_date_picker()

    # --------------------------------------------------------------------------------------------
    # Rendering
    # --------------------------------------------------------------------------------------------
    def _render_items_list(self) -> None:
        for child in self.items_list_container.winfo_children():
            child.destroy()

        active_items = [
            item for item in self.items if (item.get("status") or "active").lower() != "ended"
        ]

        if not active_items:
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
        for item in reversed(active_items):
            card = tk.Frame(
                self.items_list_container,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=16,
                pady=12,
            )
            card.pack(fill="x", padx=40, pady=(0, 12))

            name_label = tk.Label(
                card,
                text=item.get("name") or "Unnamed Item",
                font=("Segoe UI Semibold", 14),
                bg=self.card_bg,
                fg=self.text_color,
            )
            name_label.pack(anchor="w")

            title = tk.Label(
                card,
                text=f"{item.get('category', 'No category')} • {item.get('date_added') or 'No date'}",
                font=("Segoe UI", 11),
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

        self._sync_scroll_region(None)

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
                normalized = dict(entry)
                normalized["id"] = str(normalized.get("id") or uuid4().hex)
                normalized["name"] = str(normalized.get("name", "")).strip()
                normalized["description"] = str(normalized.get("description", "")).strip()
                normalized["notes"] = str(normalized.get("notes", "")).strip()
                normalized["category"] = str(normalized.get("category", "")).strip()
                normalized["date_added"] = str(normalized.get("date_added", "")).strip()
                normalized["end_date"] = str(normalized.get("end_date", "")).strip()
                normalized["image_url"] = str(normalized.get("image_url", "")).strip()
                normalized["status"] = str(normalized.get("status", "active")).strip() or "active"
                parsed.append(normalized)
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

    # --------------------------------------------------------------------------------------------
    # External operations
    # --------------------------------------------------------------------------------------------
    def edit_item(self, item_id: str, restore_on_save: bool = False) -> None:
        self._restore_on_save = restore_on_save
        self.open_add_item_dialog(item_id=item_id)

    def delete_item(self, item_id: str) -> None:
        index = next((i for i, item in enumerate(self.items) if item.get("id") == item_id), None)
        if index is None:
            return
        del self.items[index]
        self._persist_items()
        self._render_items_list()
        self._notify_items_changed()

    def end_item(self, item_id: str) -> None:
        for item in self.items:
            if item.get("id") == item_id:
                item["status"] = "ended"
                break
        else:
            return
        self._persist_items()
        self._render_items_list()
        self._notify_items_changed()

    def restore_item(self, item_id: str) -> None:
        for item in self.items:
            if item.get("id") == item_id:
                item["status"] = "active"
                break
        else:
            return
        self._persist_items()
        self._render_items_list()
        self._notify_items_changed()

    def open_item_details(self, item_id: str) -> None:
        item = self._find_item(item_id)
        if not item:
            return

        detail = tk.Toplevel(self)
        detail.title(item.get("name") or "Item details")
        detail.configure(bg=self.primary_bg)
        detail.transient(self.winfo_toplevel())
        detail.grab_set()
        detail.resizable(False, False)

        frame = tk.Frame(detail, bg=self.primary_bg, padx=24, pady=24)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=item.get("name") or "Item",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        ).pack(anchor="w")

        subtitle_parts = []
        if item.get("category"):
            subtitle_parts.append(f"Category: {item['category']}")
        if item.get("date_added"):
            subtitle_parts.append(f"Added: {item['date_added']}")
        if item.get("end_date"):
            subtitle_parts.append(f"Ends: {item['end_date']}")
        if subtitle_parts:
            tk.Label(
                frame,
                text=" • ".join(subtitle_parts),
                font=("Segoe UI", 11),
                bg=self.primary_bg,
                fg="#41566F",
            ).pack(anchor="w", pady=(6, 12))

        if item.get("image_url"):
            image_frame = tk.Frame(frame, bg=self.primary_bg)
            image_frame.pack(anchor="w", pady=(0, 12))
            image_label = tk.Label(image_frame, bg=self.primary_bg)
            image_label.pack()
            self._load_image_into_label(item.get("image_url"), image_label, max_size=(400, 300))

        if item.get("description"):
            tk.Label(
                frame,
                text=item["description"],
                font=("Segoe UI", 11),
                bg=self.primary_bg,
                fg="#28374A",
                wraplength=520,
                justify="left",
            ).pack(anchor="w", pady=(0, 10))

        if item.get("notes"):
            tk.Label(
                frame,
                text=f"Notes: {item['notes']}",
                font=("Segoe UI", 10),
                bg=self.primary_bg,
                fg="#5A6D82",
                wraplength=520,
                justify="left",
            ).pack(anchor="w")

        ttk.Button(frame, text="Close", command=detail.destroy).pack(anchor="e", pady=(18, 0))

    def _find_item(self, item_id: str | None) -> dict[str, Any] | None:
        if not item_id:
            return None
        return next((dict(item) for item in self.items if item.get("id") == item_id), None)

    def _load_image_into_label(self, url: str, label: tk.Label, max_size: tuple[int, int]) -> None:
        if Image is None or ImageTk is None:
            label.configure(text="Image preview requires Pillow.")
            return
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
            image = Image.open(BytesIO(data))
            image.thumbnail(max_size)
            photo = ImageTk.PhotoImage(image)
            label.configure(image=photo, text="")
            label.image = photo  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover
            label.configure(text=f"Unable to load image.\n{exc}")

    # --------------------------------------------------------------------------------------------
    # Scrolling helpers
    # --------------------------------------------------------------------------------------------
    def _sync_scroll_region(self, _: Any) -> None:
        if hasattr(self, "canvas"):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _match_canvas_width(self, event: Any) -> None:
        if hasattr(self, "canvas"):
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
    # Date picker helpers
    # --------------------------------------------------------------------------------------------
    def _open_date_picker(self, target_field: str) -> None:
        if not self._dialog:
            return

        self._close_date_picker()

        today = date.today()
        current_value = self._dialog_vars[target_field].get().strip()
        year = today.year
        month = today.month
        try:
            if current_value:
                parsed = date.fromisoformat(current_value)
                year = parsed.year
                month = parsed.month
        except ValueError:
            pass

        self._date_picker_state = {"field": target_field, "year": year, "month": month}

        self._date_picker_window = tk.Toplevel(self._dialog)
        self._date_picker_window.transient(self._dialog)
        self._date_picker_window.grab_set()
        self._date_picker_window.resizable(False, False)
        self._date_picker_window.title("Select Date")

        frame = tk.Frame(self._date_picker_window, bg=self.primary_bg, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        header = tk.Frame(frame, bg=self.primary_bg)
        header.pack(fill="x", pady=(0, 8))

        ttk.Button(header, text="<", width=3, command=lambda: self._shift_date_month(-1)).pack(side="left")
        self._date_label = tk.Label(
            header,
            text="",
            font=("Segoe UI Semibold", 12),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        self._date_label.pack(side="left", expand=True)
        ttk.Button(header, text=">", width=3, command=lambda: self._shift_date_month(1)).pack(side="right")

        self._calendar_container = tk.Frame(frame, bg=self.primary_bg)
        self._calendar_container.pack()

        ttk.Button(
            frame,
            text="Cancel",
            style="Secondary.TButton",
            command=self._close_date_picker,
        ).pack(pady=(10, 0))

        self._render_calendar_grid()

    def _shift_date_month(self, delta: int) -> None:
        if not self._date_picker_state:
            return
        year = self._date_picker_state["year"]
        month = self._date_picker_state["month"] + delta
        while month < 1:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        self._date_picker_state["year"] = year
        self._date_picker_state["month"] = month
        self._render_calendar_grid()

    def _render_calendar_grid(self) -> None:
        if not self._date_picker_state:
            return

        for child in self._calendar_container.winfo_children():
            child.destroy()

        year = self._date_picker_state["year"]
        month = self._date_picker_state["month"]

        if hasattr(self, "_date_label"):
            self._date_label.configure(text=f"{calendar.month_name[month]} {year}")

        weekday_header = tk.Frame(self._calendar_container, bg=self.primary_bg)
        weekday_header.pack()
        for weekday in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            tk.Label(
                weekday_header,
                text=weekday,
                width=4,
                font=("Segoe UI", 10),
                bg=self.primary_bg,
                fg=self.text_color,
            ).pack(side="left")

        for week in calendar.monthcalendar(year, month):
            row = tk.Frame(self._calendar_container, bg=self.primary_bg)
            row.pack()
            for day in week:
                if day == 0:
                    tk.Label(row, text=" ", width=4, bg=self.primary_bg).pack(side="left")
                    continue

                btn = ttk.Button(
                    row,
                    text=str(day),
                    width=4,
                    command=lambda d=day: self._select_date(d),
                )
                btn.pack(side="left")

    def _select_date(self, day: int) -> None:
        if not self._date_picker_state:
            return
        try:
            selected = date(
                self._date_picker_state["year"],
                self._date_picker_state["month"],
                day,
            )
        except ValueError:
            return
        field = self._date_picker_state.get("field")
        if field and field in self._dialog_vars:
            self._dialog_vars[field].set(selected.isoformat())
        self._close_date_picker()

    def _close_date_picker(self) -> None:
        if self._date_picker_window and self._date_picker_window.winfo_exists():
            self._date_picker_window.grab_release()
            self._date_picker_window.destroy()
        self._date_picker_window = None
        self._date_picker_state = {}

    # --------------------------------------------------------------------------------------------
    # Dialog scrolling helpers
    # --------------------------------------------------------------------------------------------
    def _sync_dialog_scroll_region(self, _: Any) -> None:
        if self._dialog_canvas:
            self._dialog_canvas.configure(scrollregion=self._dialog_canvas.bbox("all"))

    def _match_dialog_canvas_width(self, event: Any) -> None:
        if self._dialog_canvas and self._dialog_canvas_window_id is not None:
            self._dialog_canvas.itemconfigure(self._dialog_canvas_window_id, width=event.width)

    def _bind_dialog_mousewheel(self, _: Any) -> None:
        if self._dialog_mousewheel_bound or not self._dialog_canvas:
            return
        self._dialog_canvas.bind_all("<MouseWheel>", self._on_dialog_mousewheel)
        self._dialog_canvas.bind_all("<Button-4>", self._on_dialog_mousewheel)
        self._dialog_canvas.bind_all("<Button-5>", self._on_dialog_mousewheel)
        self._dialog_mousewheel_bound = True

    def _unbind_dialog_mousewheel(self, _: Any) -> None:
        if not self._dialog_mousewheel_bound or not self._dialog_canvas:
            return
        self._dialog_canvas.unbind_all("<MouseWheel>")
        self._dialog_canvas.unbind_all("<Button-4>")
        self._dialog_canvas.unbind_all("<Button-5>")
        self._dialog_mousewheel_bound = False

    def _on_dialog_mousewheel(self, event: Any) -> None:
        if not self._dialog_canvas:
            return
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self._dialog_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self._dialog_canvas.yview_scroll(1, "units")


