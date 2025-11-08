import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from .settings_view import SettingsView
except ImportError:
    from settings_view import SettingsView

try:
    from .firstrun import FirstRunWizard
except ImportError:
    from firstrun import FirstRunWizard


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

        self.config_path = os.path.join(os.path.dirname(__file__), "app_config.json")
        self.config = self._load_config()
        self.is_fullscreen = bool(self.config.get("fullscreen", False))
        self.storage_path: str | None = self.config.get("storage_path")

        self._configure_styles()
        self._create_menu()
        self._create_frames()
        self._apply_window_mode()
        if self.storage_path:
            self.show_main()
        else:
            self.show_first_run()

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

        add_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            background=self.card_bg,
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
        )
        add_menu.add_command(label="Add a New Category", command=self.show_add_category)
        add_menu.add_command(label="Add a New Item", command=self.show_add_item)
        menu_bar.add_cascade(label="Add", menu=add_menu)

        settings_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            background=self.card_bg,
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
        )
        settings_menu.add_command(label="App Settings", command=self.show_settings)
        settings_menu.add_command(label="Storage Config", command=self.show_storage_config)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menu_bar)

    def _create_frames(self) -> None:
        self.main_frame = tk.Frame(self.root, bg=self.primary_bg)
        self.settings_view = SettingsView(
            self.root,
            primary_bg=self.primary_bg,
            card_bg=self.card_bg,
            text_color=self.text_color,
            show_main_callback=self.show_main,
            toggle_fullscreen_callback=self.toggle_fullscreen_mode,
        )
        self.settings_view.update_toggle_label("Switch to Windowed" if self.is_fullscreen else "Switch to Fullscreen")
        self.add_category_frame = tk.Frame(self.root, bg=self.primary_bg)
        self.add_item_frame = tk.Frame(self.root, bg=self.primary_bg)
        self.storage_config_frame = tk.Frame(self.root, bg=self.primary_bg)

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

        category_label = tk.Label(
            self.add_category_frame,
            text="Add Category (placeholder)",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        category_label.pack(pady=40)

        item_label = tk.Label(
            self.add_item_frame,
            text="Add Item (placeholder)",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        item_label.pack(pady=40)

        storage_header = tk.Label(
            self.storage_config_frame,
            text="Storage Configuration",
            font=("Segoe UI Semibold", 22),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        storage_header.pack(pady=(40, 12))

        storage_description = tk.Label(
            self.storage_config_frame,
            text=(
                "Choose the default folder where listings, categories, and shared data will be stored.\n"
                "Pick a location that you and collaborators can both access."
            ),
            font=("Segoe UI", 12),
            bg=self.primary_bg,
            fg="#305170",
            justify="center",
        )
        storage_description.pack(pady=(0, 24))

        storage_card = tk.Frame(self.storage_config_frame, bg=self.card_bg, padx=30, pady=30)
        storage_card.pack(pady=10)

        initial_storage_value = (
            f"Current storage folder:\n{self.storage_path}"
            if self.storage_path
            else "No folder selected yet."
        )
        self.storage_value = tk.StringVar(value=initial_storage_value)

        storage_value_label = tk.Label(
            storage_card,
            textvariable=self.storage_value,
            font=("Segoe UI", 11),
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=420,
            justify="left",
        )
        storage_value_label.pack(fill="x")

        storage_button = ttk.Button(
            storage_card,
            text="Choose Storage Folder",
            command=self._select_storage_path,
            style="Primary.TButton",
        )
        storage_button.pack(pady=(18, 0), fill="x")

        back_from_storage = ttk.Button(
            self.storage_config_frame,
            text="Back to Dashboard",
            command=self.show_main,
            style="Secondary.TButton",
        )
        back_from_storage.pack(pady=(30, 10))

        default_base = self._default_storage_base_path()
        self.first_run_frame = FirstRunWizard(
            self.root,
            primary_bg=self.primary_bg,
            card_bg=self.card_bg,
            text_color=self.text_color,
            default_base_path=default_base,
            apply_path_callback=self._apply_storage_directory,
            on_complete=self._on_first_run_complete,
        )

    def _show_frame(self, frame: tk.Widget) -> None:
        for widget in (
            self.main_frame,
            self.settings_view,
            self.add_category_frame,
            self.add_item_frame,
            self.storage_config_frame,
            self.first_run_frame,
        ):
            widget.pack_forget()
        frame.pack(fill="both", expand=True)

    def show_main(self) -> None:
        self._show_frame(self.main_frame)

    def show_settings(self) -> None:
        self._show_frame(self.settings_view)

    def show_add_category(self) -> None:
        self._show_frame(self.add_category_frame)

    def show_add_item(self) -> None:
        self._show_frame(self.add_item_frame)

    def show_storage_config(self) -> None:
        self._show_frame(self.storage_config_frame)

    def show_first_run(self) -> None:
        self._show_frame(self.first_run_frame)

    def _select_storage_path(self) -> None:
        selected_dir = filedialog.askdirectory(
            parent=self.root,
            title="Select Storage Folder",
            mustexist=True,
        )
        if selected_dir:
            self._apply_storage_directory(selected_dir)

    def toggle_fullscreen_mode(self) -> None:
        if not self.is_fullscreen:
            self.is_fullscreen = True
        else:
            self.is_fullscreen = False
        self._apply_window_mode()
        self._save_config()

    def run(self) -> None:
        self.root.mainloop()

    def _apply_window_mode(self) -> None:
        if self.is_fullscreen:
            self.root.attributes("-fullscreen", True)
            self.settings_view.update_toggle_label("Switch to Windowed")
        else:
            self.root.attributes("-fullscreen", False)
            self.root.geometry(self.default_geometry)
            self.settings_view.update_toggle_label("Switch to Fullscreen")

    def _apply_storage_directory(self, base_path: str) -> bool:
        normalized = os.path.abspath(base_path)
        if os.path.basename(normalized.rstrip(os.sep)) == "ebaylistingsconfig":
            config_dir = normalized
        else:
            config_dir = os.path.join(normalized, "ebaylistingsconfig")

        try:
            os.makedirs(config_dir, exist_ok=True)
        except OSError as exc:
            messagebox.showerror(
                "Storage Configuration",
                f"Unable to prepare the storage folder.\n\n{exc}",
                parent=self.root,
            )
            return False

        self.storage_path = config_dir
        if hasattr(self, "storage_value"):
            self.storage_value.set(f"Current storage folder:\n{config_dir}")
        self._save_config()
        return True

    def _load_config(self) -> dict[str, object]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as config_file:
                    data = json.load(config_file)
                    if isinstance(data, dict):
                        return data
            except (OSError, json.JSONDecodeError):
                messagebox.showwarning(
                    "Settings",
                    "The settings file could not be read. Defaults will be used.",
                    parent=self.root,
                )
        return {}

    def _save_config(self) -> None:
        data = {
            "fullscreen": self.is_fullscreen,
            "storage_path": self.storage_path,
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as config_file:
                json.dump(data, config_file, indent=2)
        except OSError as exc:
            messagebox.showwarning(
                "Settings",
                f"Unable to save settings.\n\n{exc}",
                parent=self.root,
            )

    def _default_storage_base_path(self) -> str:
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.isdir(documents):
            return documents
        return os.path.expanduser("~")

    def _on_first_run_complete(self) -> None:
        if not self.storage_path:
            return
        self.show_main()


if __name__ == "__main__":
    app = EbayListingApp()
    app.run()
