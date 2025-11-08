import tkinter as tk
from tkinter import ttk


class EbayListingApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Ebay Listing App")
        self.default_geometry = "800x600"
        self.root.geometry(self.default_geometry)
        self.root.resizable(False, False)
        self.is_fullscreen = False

        self.primary_bg = "#F2F7FF"
        self.accent_color = "#1E88E5"
        self.accent_hover = "#1565C0"
        self.card_bg = "#FFFFFF"
        self.text_color = "#0A2239"

        self.root.configure(bg=self.primary_bg)
        self.root.option_add("*Font", "{Segoe UI} 11")

        self._configure_styles()
        self._create_menu()
        self._create_frames()
        self.show_main()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TLabel", background=self.primary_bg, foreground=self.text_color)

        style.configure(
            "Primary.TButton",
            padding=(16, 10),
            font=("Segoe UI Semibold", 11),
            background=self.accent_color,
            foreground="#FFFFFF",
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.accent_hover)],
            foreground=[("disabled", "#B0BEC5")],
        )

        style.configure(
            "Secondary.TButton",
            padding=(16, 10),
            font=("Segoe UI", 11),
            background="#E3F2FD",
            foreground=self.text_color,
            borderwidth=0,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#D2E7FB")],
            foreground=[("disabled", "#90A4AE")],
        )

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(
            self.root,
            background=self.primary_bg,
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
            borderwidth=0,
            tearoff=False,
        )

        file_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            background=self.card_bg,
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
        )
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            background=self.card_bg,
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
        )
        settings_menu.add_command(label="App Settings", command=self.show_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menu_bar)

    def _create_frames(self) -> None:
        self.main_frame = tk.Frame(self.root, bg=self.primary_bg)
        self.settings_frame = tk.Frame(self.root, bg=self.primary_bg)

        hero_title = tk.Label(
            self.main_frame,
            text="eBay Listing Manager",
            font=("Segoe UI Semibold", 26),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        hero_title.pack(pady=(60, 10))

        hero_subtitle = tk.Label(
            self.main_frame,
            text="Streamline your listing workflow with a clean and modern interface.",
            font=("Segoe UI", 13),
            bg=self.primary_bg,
            fg="#305170",
        )
        hero_subtitle.pack(pady=(0, 40))

        card = tk.Frame(self.main_frame, bg=self.card_bg, padx=40, pady=40)
        card.pack(pady=10, ipadx=10, ipady=10)

        card_label = tk.Label(
            card,
            text="Welcome to the refreshed experience!",
            font=("Segoe UI Semibold", 14),
            bg=self.card_bg,
            fg=self.text_color,
        )
        card_label.pack()

        settings_header = tk.Label(
            self.settings_frame,
            text="App Settings",
            font=("Segoe UI Semibold", 22),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        settings_header.pack(pady=(40, 15))

        settings_subtitle = tk.Label(
            self.settings_frame,
            text="Customize how the app looks and feels to suit your workspace.",
            font=("Segoe UI", 12),
            bg=self.primary_bg,
            fg="#305170",
        )
        settings_subtitle.pack(pady=(0, 30))

        controls_container = tk.Frame(self.settings_frame, bg=self.card_bg, padx=30, pady=30)
        controls_container.pack(pady=10)

        toggle_label = tk.Label(
            controls_container,
            text="Display",
            font=("Segoe UI Semibold", 13),
            bg=self.card_bg,
            fg=self.text_color,
        )
        toggle_label.pack(anchor="w")

        self.toggle_button = ttk.Button(
            controls_container,
            text="Switch to Fullscreen",
            command=self.toggle_fullscreen_mode,
            style="Primary.TButton",
        )
        self.toggle_button.pack(pady=(12, 0), fill="x")

        back_button = ttk.Button(
            self.settings_frame,
            text="Back to Dashboard",
            command=self.show_main,
            style="Secondary.TButton",
        )
        back_button.pack(pady=(30, 10))

    def show_main(self) -> None:
        self.settings_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

    def show_settings(self) -> None:
        self.main_frame.pack_forget()
        self.settings_frame.pack(fill="both", expand=True)

    def toggle_fullscreen_mode(self) -> None:
        if not self.is_fullscreen:
            self.root.attributes("-fullscreen", True)
            self.toggle_button.config(text="Switch to Windowed")
        else:
            self.root.attributes("-fullscreen", False)
            self.root.geometry(self.default_geometry)
            self.toggle_button.config(text="Switch to Fullscreen")
        self.is_fullscreen = not self.is_fullscreen

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = EbayListingApp()
    app.run()
