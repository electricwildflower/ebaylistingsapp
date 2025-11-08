import os
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable, Optional


class FirstRunWizard(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        card_bg: str,
        text_color: str,
        default_base_path: str,
        apply_path_callback: Callable[[str], bool],
        on_complete: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=primary_bg)

        self.primary_bg = primary_bg
        self.card_bg = card_bg
        self.text_color = text_color
        self.default_base_path = default_base_path
        self.apply_path_callback = apply_path_callback
        self.on_complete = on_complete

        self.selected_base_path: Optional[str] = None

        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Label(
            self,
            text="Set Up Shared Storage",
            font=("Segoe UI Semibold", 24),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(pady=(50, 12))

        subtitle = tk.Label(
            self,
            text=(
                "Choose where eBay listings data should be stored. Select a shared folder if multiple devices "
                "will manage the same listings."
            ),
            font=("Segoe UI", 12),
            bg=self.primary_bg,
            fg="#305170",
            wraplength=520,
            justify="center",
        )
        subtitle.pack(pady=(0, 30))

        card = tk.Frame(self, bg=self.card_bg, padx=32, pady=32)
        card.pack(pady=10)

        instruction = tk.Label(
            card,
            text="Choose a location to hold the `ebaylistingsconfig` folder.",
            font=("Segoe UI", 12),
            bg=self.card_bg,
            fg=self.text_color,
        )
        instruction.pack(anchor="w")

        default_label = tk.Label(
            card,
            text=f"Default location: {os.path.join(self.default_base_path, 'ebaylistingsconfig')}",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg="#305170",
            wraplength=480,
            justify="left",
        )
        default_label.pack(anchor="w", pady=(8, 18))

        button_row = tk.Frame(card, bg=self.card_bg)
        button_row.pack(fill="x")

        default_button = ttk.Button(
            button_row,
            text="Use Default Location",
            style="Primary.TButton",
            command=self._use_default_location,
        )
        default_button.pack(side="left", expand=True, fill="x", padx=(0, 8))

        browse_button = ttk.Button(
            button_row,
            text="Choose Existing Folder…",
            style="Secondary.TButton",
            command=self._browse_for_location,
        )
        browse_button.pack(side="left", expand=True, fill="x", padx=(8, 0))

        selection_header = tk.Label(
            card,
            text="Selected location:",
            font=("Segoe UI Semibold", 11),
            bg=self.card_bg,
            fg=self.text_color,
        )
        selection_header.pack(anchor="w", pady=(20, 4))

        self.selection_value = tk.StringVar(value="No folder selected yet.")

        selection_value_label = tk.Label(
            card,
            textvariable=self.selection_value,
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=480,
            justify="left",
        )
        selection_value_label.pack(anchor="w")

        self.save_button = ttk.Button(
            self,
            text="Save & Continue",
            style="Primary.TButton",
            command=self._save_selection,
            state="disabled",
        )
        self.save_button.pack(pady=(36, 12))

    def _use_default_location(self) -> None:
        self._update_selection(self.default_base_path)

    def _browse_for_location(self) -> None:
        selected_dir = filedialog.askdirectory(
            parent=self,
            title="Select Folder for ebaylistingsconfig",
            mustexist=True,
        )
        if selected_dir:
            self._update_selection(selected_dir)

    def _update_selection(self, base_path: str) -> None:
        normalized = os.path.abspath(base_path)
        self.selected_base_path = normalized
        display_path = os.path.join(normalized, "ebaylistingsconfig")
        if os.path.basename(normalized.rstrip(os.sep)) == "ebaylistingsconfig":
            display_path = normalized
        self.selection_value.set(display_path)
        self.save_button.config(state="normal")

    def _save_selection(self) -> None:
        if not self.selected_base_path:
            return
        success = self.apply_path_callback(self.selected_base_path)
        if success:
            self.on_complete()

