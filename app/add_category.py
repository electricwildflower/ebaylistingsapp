"""UI components for the Add Category view."""

from __future__ import annotations

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
        **kwargs,
    ) -> None:
        super().__init__(master, bg=primary_bg, **kwargs)
        self.primary_bg = primary_bg
        self.text_color = text_color
        self.card_bg = "#FFFFFF"
        self.categories: list[dict[str, str]] = []
        self._dialog: tk.Toplevel | None = None
        self._dialog_name_var: tk.StringVar | None = None
        self._dialog_days_var: tk.StringVar | None = None
        self._dialog_description: tk.Text | None = None

        self.search_value = tk.StringVar()

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
        self.cards_container = tk.Frame(parent, bg=self.primary_bg)
        self.cards_container.pack(fill="both", expand=True, pady=(30, 0))

    def _handle_add_category(self) -> None:
        if self._dialog and self._dialog.winfo_exists():
            self._dialog.lift()
            self._dialog.focus_force()
            return

        self._dialog = tk.Toplevel(self)
        self._dialog.title("Add Category")
        self._dialog.configure(bg=self.primary_bg)
        self._dialog.transient(self.winfo_toplevel())
        self._dialog.grab_set()
        self._dialog.resizable(False, False)
        self._dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)

        dialog_frame = tk.Frame(self._dialog, bg=self.primary_bg, padx=24, pady=24)
        dialog_frame.pack(fill="both", expand=True)

        self._dialog_name_var = tk.StringVar()
        self._dialog_days_var = tk.StringVar(value="30")

        ttk.Label(dialog_frame, text="Category Name", style="TLabel").grid(row=0, column=0, sticky="w")
        name_entry = ttk.Entry(dialog_frame, width=40, textvariable=self._dialog_name_var)
        name_entry.grid(row=1, column=0, sticky="we", pady=(4, 16))
        name_entry.focus_set()

        ttk.Label(dialog_frame, text="Description", style="TLabel").grid(row=2, column=0, sticky="w")
        self._dialog_description = tk.Text(dialog_frame, width=40, height=5, font=("Segoe UI", 11))
        self._dialog_description.grid(row=3, column=0, sticky="we", pady=(4, 16))

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

        button_row = tk.Frame(dialog_frame, bg=self.primary_bg)
        button_row.grid(row=6, column=0, sticky="e")

        ttk.Button(button_row, text="Save", style="Primary.TButton", command=self._save_category).pack()

        self._dialog.columnconfigure(0, weight=1)
        dialog_frame.columnconfigure(0, weight=1)

    def _close_dialog(self) -> None:
        if self._dialog and self._dialog.winfo_exists():
            self._dialog.grab_release()
            self._dialog.destroy()
        self._dialog = None
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
            messagebox.showerror("Add Category", "Please enter a category name.", parent=self._dialog)
            return

        if not days_value.isdigit() or int(days_value) <= 0:
            messagebox.showerror("Add Category", "Please enter a valid number of days.", parent=self._dialog)
            return

        category = {
            "name": name,
            "description": description,
            "days": days_value,
        }
        self.categories.append(category)
        self._render_category_cards()
        self._close_dialog()

    def _render_category_cards(self) -> None:
        for child in self.cards_container.winfo_children():
            child.destroy()

        if not self.categories:
            placeholder = tk.Label(
                self.cards_container,
                text="No categories yet. Click \"Add a Category\" to create one.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            )
            placeholder.pack(pady=10)
            return

        for category in self.categories:
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

            ttk.Button(
                card,
                text="Open Category",
                style="Secondary.TButton",
                command=lambda cat=category: self._open_category(cat),
            ).pack(anchor="e")

    def _open_category(self, category: dict[str, str]) -> None:  # pragma: no cover - placeholder
        messagebox.showinfo(
            "Open Category",
            f"The category \"{category['name']}\" will open listings soon.",
            parent=self.winfo_toplevel(),
        )

