"""Minimal Tkinter GUI placeholder for ebaylistingapp."""

from __future__ import annotations

import tkinter as tk


def main() -> None:
    """Launch the placeholder GUI window."""
    root = tk.Tk()
    root.title("ebaylistingapp")
    root.configure(background="white")
    root.geometry("480x320")

    label = tk.Label(
        root,
        text="ebaylistingapp",
        font=("Segoe UI", 24, "bold"),
        background="white",
        foreground="#333333",
    )
    label.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()


