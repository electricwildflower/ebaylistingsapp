import tkinter as tk
from tkinter import ttk
from typing import Callable


class SettingsView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        primary_bg: str,
        card_bg: str,
        text_color: str,
        show_main_callback: Callable[[], None],
        toggle_fullscreen_callback: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=primary_bg)

        header = tk.Label(
            self,
            text="App Settings",
            font=("Segoe UI Semibold", 22),
            bg=primary_bg,
            fg=text_color,
        )
        header.pack(pady=(40, 15))

        subtitle = tk.Label(
            self,
            text="Customize how the app looks and feels to suit your workspace.",
            font=("Segoe UI", 12),
            bg=primary_bg,
            fg="#305170",
        )
        subtitle.pack(pady=(0, 30))

        controls_container = tk.Frame(self, bg=card_bg, padx=30, pady=30)
        controls_container.pack(pady=10)

        toggle_label = tk.Label(
            controls_container,
            text="Display",
            font=("Segoe UI Semibold", 13),
            bg=card_bg,
            fg=text_color,
        )
        toggle_label.pack(anchor="w")

        self.toggle_button = ttk.Button(
            controls_container,
            text="Switch to Fullscreen",
            command=toggle_fullscreen_callback,
            style="Primary.TButton",
        )
        self.toggle_button.pack(pady=(12, 0), fill="x")

        back_button = ttk.Button(
            self,
            text="Back to Dashboard",
            command=show_main_callback,
            style="Secondary.TButton",
        )
        back_button.pack(pady=(30, 10))

    def update_toggle_label(self, text: str) -> None:
        self.toggle_button.config(text=text)

