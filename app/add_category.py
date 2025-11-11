"""UI components for the Add Category view."""

from __future__ import annotations

import json
import os
from typing import Any

import tkinter as tk
from tkinter import messagebox, ttk


class AddCategoryView(tk.Frame):
    """Visual layout for the Add Category screen."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        text_color: str,
        storage_path: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(master, bg=primary_bg, **kwargs)
        self.primary_bg = primary_bg
        self.text_color = text_color
        self.card_bg = "#FFFFFF"
        self.storage_path = storage_path
        self.categories: list[dict[str, str]] = []
        self._dialog_backdrop: tk.Frame | None = None
        self._dialog: tk.Frame | None = None
        self._dialog_mode: str | None = None
        self._editing_index: int | None = None
        self._dialog_name_var: tk.StringVar | None = None
        self._dialog_days_var: tk.StringVar | None = None
        self._dialog_description: tk.Text | None = None

        self.search_value = tk.StringVar()
        self.search_value.trace_add("write", self._handle_search_change)
        self._is_mousewheel_bound = False

        self._load_categories()
        self._build_layout()
        self._render_category_cards()

    def _build_layout(self) -> None:
        container = tk.Frame(self, bg=self.primary_bg)
        container.pack(fill="both", expand=True, pady=(60, 0))

        self._build_title(container)
        self._build_search(container)
        self._build_actions(container)
        self._build_categories_container(container)

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

    def _build_categories_container(self, parent: tk.Frame) -> None:
        container = tk.Frame(parent, bg=self.primary_bg)
        container.pack(fill="both", expand=True, pady=(30, 0))

        self.cards_canvas = tk.Canvas(
            container,
            bg=self.primary_bg,
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.cards_canvas.yview)
        self.cards_canvas.configure(yscrollcommand=scrollbar.set)

        self.cards_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cards_container = tk.Frame(self.cards_canvas, bg=self.primary_bg)
        self._cards_window_id = self.cards_canvas.create_window((0, 0), window=self.cards_container, anchor="nw")

        self.cards_container.bind("<Configure>", self._sync_scroll_region)
        self.cards_canvas.bind("<Enter>", self._bind_mousewheel)
        self.cards_canvas.bind("<Leave>", self._unbind_mousewheel)
        self.cards_canvas.bind("<Configure>", self._match_canvas_width)

    def _handle_add_category(self) -> None:
        if not self.storage_path:
            messagebox.showerror(
                "Add Category",
                "Please configure a storage location before adding categories.",
                parent=self.winfo_toplevel(),
            )
            return

        self._open_category_dialog(mode="add")

    def _handle_edit_category(self, index: int) -> None:
        if not self.storage_path:
            messagebox.showerror(
                "Edit Category",
                "Please configure a storage location before editing categories.",
                parent=self.winfo_toplevel(),
            )
            return

        if index < 0 or index >= len(self.categories):
            return

        self._open_category_dialog(mode="edit", index=index)

    def _delete_category(self, index: int) -> None:
        if index < 0 or index >= len(self.categories):
            return

        category = self.categories[index]
        confirmed = messagebox.askyesno(
            "Delete Category",
            f"Are you sure you want to delete \"{category['name']}\"?",
            parent=self.winfo_toplevel(),
            icon="warning",
        )
        if not confirmed:
            return

        del self.categories[index]
        self._persist_categories()
        self._render_category_cards()

    def _open_category_dialog(self, mode: str, index: int | None = None) -> None:
        if self._dialog_backdrop and self._dialog_backdrop.winfo_exists():
            self._close_dialog()

        category: dict[str, str] | None = None
        if mode == "edit" and index is not None and 0 <= index < len(self.categories):
            category = self.categories[index]

        self._dialog_mode = mode
        self._editing_index = index
        self._dialog_backdrop = tk.Frame(self, bg=self.primary_bg)
        self._dialog_backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._dialog_backdrop.lift()

        wrapper = tk.Frame(self._dialog_backdrop, bg=self.primary_bg)
        wrapper.pack(expand=True, pady=60)

        title = "Edit Category" if mode == "edit" else "Add Category"
        header = tk.Label(
            wrapper,
            text=title,
            font=("Segoe UI Semibold", 20),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(pady=(0, 16))

        self._dialog = tk.Frame(wrapper, bg=self.card_bg, padx=24, pady=24)
        self._dialog.pack()

        dialog_frame = self._dialog

        default_name = category["name"] if category else ""
        default_days = category["days"] if category else "30"
        default_description = category["description"] if category else ""

        self._dialog_name_var = tk.StringVar(value=default_name)
        self._dialog_days_var = tk.StringVar(value=default_days or "30")

        ttk.Label(dialog_frame, text="Category Name", style="TLabel").grid(row=0, column=0, sticky="w")
        name_entry = ttk.Entry(dialog_frame, width=40, textvariable=self._dialog_name_var)
        name_entry.grid(row=1, column=0, sticky="we", pady=(4, 16))
        name_entry.focus_set()
        name_entry.icursor("end")

        ttk.Label(dialog_frame, text="Description", style="TLabel").grid(row=2, column=0, sticky="w")
        self._dialog_description = tk.Text(dialog_frame, width=40, height=5, font=("Segoe UI", 11))
        self._dialog_description.grid(row=3, column=0, sticky="we", pady=(4, 16))
        if default_description:
            self._dialog_description.insert("1.0", default_description)

        tk.Label(
            dialog_frame,
            text="Duration (days)",
            bg=self.primary_bg,
            fg=self.text_color,
            font=("Segoe UI", 11),
        ).grid(row=4, column=0, sticky="w")
        days_spinbox = tk.Spinbox(
            dialog_frame,
            from_=1,
            to=90,
            width=6,
            textvariable=self._dialog_days_var,
            justify="center",
        )
        days_spinbox.grid(row=5, column=0, sticky="w", pady=(4, 20))

        button_row = tk.Frame(dialog_frame, bg=self.card_bg)
        button_row.grid(row=6, column=0, sticky="e")

        ttk.Button(button_row, text="Save", style="Primary.TButton", command=self._save_category).pack(side="left")
        ttk.Button(button_row, text="Cancel", style="Secondary.TButton", command=self._close_dialog).pack(
            side="left", padx=(12, 0)
        )

        self._dialog.columnconfigure(0, weight=1)
        dialog_frame.columnconfigure(0, weight=1)

    def _close_dialog(self) -> None:
        if self._dialog and self._dialog.winfo_exists():
            self._dialog.destroy()
        if self._dialog_backdrop and self._dialog_backdrop.winfo_exists():
            self._dialog_backdrop.place_forget()
            self._dialog_backdrop.destroy()
        self._dialog_backdrop = None
        self._dialog = None
        self._dialog_mode = None
        self._editing_index = None
        self._dialog_name_var = None
        self._dialog_days_var = None
        self._dialog_description = None

    def _save_category(self) -> None:
        if not (self._dialog_name_var and self._dialog_days_var and self._dialog_description):
            return

        name = self._dialog_name_var.get().strip()
        description = self._dialog_description.get("1.0", "end").strip()
        days_value = self._dialog_days_var.get().strip()

        if not name:
            messagebox.showerror("Add Category", "Please enter a category name.", parent=self.winfo_toplevel())
            return

        if not days_value.isdigit() or int(days_value) <= 0:
            messagebox.showerror("Add Category", "Please enter a valid number of days.", parent=self.winfo_toplevel())
            return

        category = {
            "name": name,
            "description": description,
            "days": days_value,
        }
        if self._dialog_mode == "edit" and self._editing_index is not None:
            self.categories[self._editing_index] = category
        else:
            self.categories.append(category)

        self._persist_categories()
        self._render_category_cards()
        self._close_dialog()

    def _render_category_cards(self) -> None:
        for child in self.cards_container.winfo_children():
            child.destroy()

        filter_text = self.search_value.get().strip().lower()
        if filter_text:
            filtered = [
                (index, category)
                for index, category in enumerate(self.categories)
                if filter_text in category["name"].lower() or filter_text in category["description"].lower()
            ]
        else:
            filtered = list(enumerate(self.categories))

        if not filtered:
            placeholder = tk.Label(
                self.cards_container,
                text=(
                    "No categories match your search."
                    if filter_text
                    else "No categories yet. Click \"Add a Category\" to create one."
                ),
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            )
            placeholder.pack(pady=10)
            return

        for original_index, category in filtered:
            card = tk.Frame(
                self.cards_container,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=20,
                pady=16,
            )
            card.pack(fill="x", padx=60, pady=(0, 14))

            name_label = tk.Label(
                card,
                text=category["name"],
                font=("Segoe UI Semibold", 16),
                bg=self.card_bg,
                fg=self.text_color,
            )
            name_label.pack(anchor="w")

            if category["description"]:
                description_label = tk.Label(
                    card,
                    text=category["description"],
                    font=("Segoe UI", 11),
                    bg=self.card_bg,
                    fg="#41566F",
                    wraplength=520,
                    justify="left",
                )
                description_label.pack(anchor="w", pady=(6, 10))

            meta_label = tk.Label(
                card,
                text=f"Duration: {category['days']} day(s)",
                font=("Segoe UI", 10),
                bg=self.card_bg,
                fg="#6F7F92",
            )
            meta_label.pack(anchor="w", pady=(0, 12))

            actions = tk.Frame(card, bg=self.card_bg)
            actions.pack(anchor="e", pady=(8, 0))

            ttk.Button(
                actions,
                text="Open",
                style="Secondary.TButton",
                command=lambda cat=category: self._open_category(cat),
            ).pack(side="left", padx=(0, 8))

            ttk.Button(
                actions,
                text="Edit",
                style="Secondary.TButton",
                command=lambda idx=original_index: self._handle_edit_category(idx),
            ).pack(side="left", padx=(0, 8))

            ttk.Button(
                actions,
                text="Delete",
                style="Secondary.TButton",
                command=lambda idx=original_index: self._delete_category(idx),
            ).pack(side="left")

    def _open_category(self, category: dict[str, str]) -> None:  # pragma: no cover - placeholder
        messagebox.showinfo(
            "Open Category",
            f"The category \"{category['name']}\" will open listings soon.",
            parent=self.winfo_toplevel(),
        )

    def set_storage_path(self, storage_path: str) -> None:
        self.storage_path = storage_path
        self._load_categories()
        self._render_category_cards()

    def _handle_search_change(self, *_: Any) -> None:
        if hasattr(self, "cards_container"):
            self._render_category_cards()

    def _sync_scroll_region(self, _: Any) -> None:
        self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))

    def _match_canvas_width(self, event: Any) -> None:
        self.cards_canvas.itemconfigure(self._cards_window_id, width=event.width)

    def _bind_mousewheel(self, _: Any) -> None:
        if self._is_mousewheel_bound:
            return
        self.cards_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.cards_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.cards_canvas.bind_all("<Button-5>", self._on_mousewheel)
        self._is_mousewheel_bound = True

    def _unbind_mousewheel(self, _: Any) -> None:
        if not self._is_mousewheel_bound:
            return
        self.cards_canvas.unbind_all("<MouseWheel>")
        self.cards_canvas.unbind_all("<Button-4>")
        self.cards_canvas.unbind_all("<Button-5>")
        self._is_mousewheel_bound = False

    def _on_mousewheel(self, event: Any) -> None:
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self.cards_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self.cards_canvas.yview_scroll(1, "units")

    def _data_file_path(self) -> str | None:
        if not self.storage_path:
            return None
        return os.path.join(self.storage_path, "categories.json")

    def _load_categories(self) -> None:
        data_path = self._data_file_path()
        if not data_path or not os.path.exists(data_path):
            self.categories = []
            return

        try:
            with open(data_path, "r", encoding="utf-8") as file:
                raw_data: Any = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showwarning(
                "Categories",
                f"Unable to load categories data.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )
            self.categories = []
            return

        parsed: list[dict[str, str]] = []
        if isinstance(raw_data, list):
            for entry in raw_data:
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("name", "")).strip()
                description = str(entry.get("description", "")).strip()
                days = str(entry.get("days", "")).strip()
                if name:
                    parsed.append({"name": name, "description": description, "days": days or "0"})
        self.categories = parsed

    def _persist_categories(self) -> None:
        data_path = self._data_file_path()
        if not data_path:
            return

        try:
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            with open(data_path, "w", encoding="utf-8") as file:
                json.dump(self.categories, file, indent=2)
        except OSError as exc:
            messagebox.showerror(
                "Categories",
                f"Unable to save categories data.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )

