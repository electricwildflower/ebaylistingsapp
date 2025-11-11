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

try:
    from .add_category import AddCategoryView
except ImportError:
    from add_category import AddCategoryView


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
        self.root.option_add("*Menu.borderWidth", 0)
        self.root.option_add("*Menu.relief", "flat")
        self.root.option_add("*Menu.activeBorderWidth", 0)

        self.config_path = self._resolve_config_path()
        self.config = self._load_config()
        self.is_fullscreen = bool(self.config.get("fullscreen", False))
        self.storage_path: str | None = self.config.get("storage_path")

        self._configure_styles()
        self._create_top_bar()
        self._create_content_container()
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

        style.configure(
            "TopNav.TMenubutton",
            font=("Segoe UI Semibold", 11),
            padding=(12, 8),
            background="#FFFFFF",
            foreground=self.text_color,
            borderwidth=0,
        )
        style.map(
            "TopNav.TMenubutton",
            background=[("active", "#E3F2FD"), ("pressed", "#D2E7FB")],
        )
        style.layout(
            "TopNav.TMenubutton",
            [
                (
                    "Menubutton.border",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Menubutton.focus",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Menubutton.padding",
                                            {
                                                "sticky": "nswe",
                                                "children": [
                                                    ("Menubutton.label", {"sticky": "nswe"})
                                                ],
                                            },
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        # Placeholder style slot for future top bar buttons if needed.

    def _create_top_bar(self) -> None:
        self.top_bar = tk.Frame(self.root, bg="#FFFFFF")
        self.top_bar_visible = False

        row = tk.Frame(self.top_bar, bg="#FFFFFF")
        row.pack(side="top", fill="x")

        nav_container = tk.Frame(row, bg="#FFFFFF")
        nav_container.pack(side="left", padx=(16, 8), pady=4)

        file_button = ttk.Menubutton(nav_container, text="File", style="TopNav.TMenubutton", direction="below")
        file_menu = tk.Menu(
            file_button,
            tearoff=0,
            background="#FFFFFF",
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
            borderwidth=0,
            relief="flat",
            activeborderwidth=0,
        )
        file_menu.add_command(label="Exit", command=self.root.quit)
        file_button.configure(menu=file_menu)
        file_button.pack(side="left", padx=4)

        home_button = ttk.Button(
            nav_container,
            text="Home",
            style="TopNav.TMenubutton",
            command=self.show_main,
        )
        home_button.pack(side="left", padx=4)

        categories_button = ttk.Menubutton(
            nav_container, text="Categories", style="TopNav.TMenubutton", direction="below"
        )
        categories_menu = tk.Menu(
            categories_button,
            tearoff=0,
            background="#FFFFFF",
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
            borderwidth=0,
            relief="flat",
            activeborderwidth=0,
        )
        categories_menu.add_command(label="Add/Edit/Delete Categories", command=self.show_add_category)
        categories_button.configure(menu=categories_menu)
        categories_button.pack(side="left", padx=4)

        items_button = ttk.Menubutton(nav_container, text="Listings", style="TopNav.TMenubutton", direction="below")
        items_menu = tk.Menu(
            items_button,
            tearoff=0,
            background="#FFFFFF",
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
            borderwidth=0,
            relief="flat",
            activeborderwidth=0,
        )
        items_menu.add_command(label="Add a New Item", command=self.show_add_item)
        items_menu.add_command(label="Re-add an Item", command=self.show_readd_item)
        items_menu.add_command(label="Remove an Item", command=self.show_remove_item)
        items_menu.add_command(label="End an Item", command=self.show_end_item)
        items_button.configure(menu=items_menu)
        items_button.pack(side="left", padx=4)

        settings_button = ttk.Menubutton(nav_container, text="Settings", style="TopNav.TMenubutton", direction="below")
        settings_menu = tk.Menu(
            settings_button,
            tearoff=0,
            background="#FFFFFF",
            foreground=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white",
            borderwidth=0,
            relief="flat",
            activeborderwidth=0,
        )
        settings_menu.add_command(label="App Settings", command=self.show_settings)
        settings_menu.add_command(label="Storage Config", command=self.show_storage_config)
        settings_button.configure(menu=settings_menu)
        settings_button.pack(side="left", padx=4)

        spacer = tk.Frame(row, bg="#FFFFFF")
        spacer.pack(side="left", expand=True, fill="x")

        accent = tk.Frame(self.top_bar, bg="#0064D2", height=2)
        accent.pack(side="top", fill="x")

    def _create_content_container(self) -> None:
        self.content_container = tk.Frame(self.root, bg=self.primary_bg)
        self.content_container.pack(fill="both", expand=True)

    def _create_frames(self) -> None:
        self.main_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self.settings_view = SettingsView(
            self.content_container,
            primary_bg=self.primary_bg,
            card_bg=self.card_bg,
            text_color=self.text_color,
            show_main_callback=self.show_main,
            toggle_fullscreen_callback=self.toggle_fullscreen_mode,
        )
        self.settings_view.update_toggle_label("Switch to Windowed" if self.is_fullscreen else "Switch to Fullscreen")
        self.add_category_frame = AddCategoryView(
            self.content_container,
            primary_bg=self.primary_bg,
            text_color=self.text_color,
            storage_path=self.storage_path,
            on_categories_changed=self._update_categories_display,
        )
        self.add_item_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self.readd_item_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self.remove_item_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self.end_item_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self.storage_config_frame = tk.Frame(self.content_container, bg=self.primary_bg)

        self._build_main_hero_title()

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

        self._build_main_categories_section()

        item_label = tk.Label(
            self.add_item_frame,
            text="Add Item (placeholder)",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        item_label.pack(pady=40)

        readd_label = tk.Label(
            self.readd_item_frame,
            text="Re-add Item (placeholder)",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        readd_label.pack(pady=40)

        remove_label = tk.Label(
            self.remove_item_frame,
            text="Remove Item (placeholder)",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        remove_label.pack(pady=40)

        end_label = tk.Label(
            self.end_item_frame,
            text="End Item (placeholder)",
            font=("Segoe UI Semibold", 18),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        end_label.pack(pady=40)

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

        self._render_main_categories(self.add_category_frame.get_categories())

        default_base = self._default_storage_base_path()
        self.first_run_frame = FirstRunWizard(
            self.content_container,
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
            self.readd_item_frame,
            self.remove_item_frame,
            self.end_item_frame,
            self.storage_config_frame,
            self.first_run_frame,
        ):
            widget.pack_forget()
        frame.pack(fill="both", expand=True)

    def show_main(self) -> None:
        self._show_top_bar()
        self._show_frame(self.main_frame)

    def show_settings(self) -> None:
        self._show_top_bar()
        self._show_frame(self.settings_view)

    def show_add_category(self) -> None:
        self._show_top_bar()
        self._show_frame(self.add_category_frame)

    def show_add_item(self) -> None:
        self.show_add_category()

    def show_readd_item(self) -> None:
        self._show_top_bar()
        self._show_frame(self.readd_item_frame)

    def show_remove_item(self) -> None:
        self._show_top_bar()
        self._show_frame(self.remove_item_frame)

    def show_end_item(self) -> None:
        self._show_top_bar()
        self._show_frame(self.end_item_frame)

    def show_storage_config(self) -> None:
        self._show_top_bar()
        self._show_frame(self.storage_config_frame)

    def show_first_run(self) -> None:
        self._hide_top_bar()
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
        if hasattr(self, "add_category_frame"):
            self.add_category_frame.set_storage_path(config_dir)
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
        config_dir = os.path.dirname(self.config_path)
        try:
            os.makedirs(config_dir, exist_ok=True)
        except OSError as exc:
            messagebox.showwarning(
                "Settings",
                f"Unable to create settings folder.\n\n{exc}",
                parent=self.root,
            )
            return

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

    def _resolve_config_path(self) -> str:
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        base_dir = documents if os.path.isdir(documents) else os.path.expanduser("~")
        config_dir = os.path.join(base_dir, "ebaylistingapp")
        return os.path.join(config_dir, "app_config.json")

    def _on_first_run_complete(self) -> None:
        if not self.storage_path:
            return
        self.show_main()

    def _build_main_hero_title(self) -> None:
        if hasattr(self, "hero_title_frame") and self.hero_title_frame.winfo_exists():
            self.hero_title_frame.destroy()

        self.hero_title_frame = tk.Frame(self.main_frame, bg=self.primary_bg)
        self.hero_title_frame.pack(pady=(60, 10))

        palette = ("#E53238", "#0064D2", "#F5AF02", "#86B817")
        title_text = "eBay Listing Manager"
        palette_index = 0

        for char in title_text:
            if char == " ":
                spacer = tk.Label(self.hero_title_frame, text=" ", font=("Segoe UI Semibold", 26), bg=self.primary_bg)
                spacer.pack(side="left")
                continue

            color = palette[palette_index % len(palette)]
            label = tk.Label(
                self.hero_title_frame,
                text=char,
                font=("Segoe UI Semibold", 26),
                bg=self.primary_bg,
                fg=color,
            )
            label.pack(side="left")
            palette_index += 1

    def _build_main_categories_section(self) -> None:
        self.main_categories_section = tk.Frame(self.main_frame, bg=self.primary_bg)
        self.main_categories_section.pack(fill="x", padx=40, pady=(30, 0))

        header = tk.Label(
            self.main_categories_section,
            text="Categories",
            font=("Segoe UI Semibold", 20),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        header.pack(anchor="w")

        self.main_categories_container = tk.Frame(self.main_categories_section, bg=self.primary_bg)
        self.main_categories_container.pack(fill="x", pady=(12, 0))

    def _render_main_categories(self, categories: list[dict[str, str]]) -> None:
        for child in self.main_categories_container.winfo_children():
            child.destroy()

        if not categories:
            placeholder = tk.Label(
                self.main_categories_container,
                text="No categories to display yet.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            )
            placeholder.pack(anchor="w")
            return

        for category in categories:
            card = tk.Frame(
                self.main_categories_container,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=16,
                pady=14,
            )
            card.pack(fill="x", pady=(0, 12))

            name_label = tk.Label(
                card,
                text=category.get("name", ""),
                font=("Segoe UI Semibold", 14),
                bg=self.card_bg,
                fg=self.text_color,
            )
            name_label.pack(anchor="w")

            description = category.get("description", "")
            if description:
                description_label = tk.Label(
                    card,
                    text=description,
                    font=("Segoe UI", 11),
                    bg=self.card_bg,
                    fg="#41566F",
                    wraplength=480,
                    justify="left",
                )
                description_label.pack(anchor="w", pady=(4, 6))

            days = category.get("days")
            if days:
                meta_label = tk.Label(
                    card,
                    text=f"Duration: {days} day(s)",
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#6F7F92",
                )
                meta_label.pack(anchor="w")

    def _update_categories_display(self, categories: list[dict[str, str]]) -> None:
        if hasattr(self, "main_categories_container"):
            self._render_main_categories(categories)

    def _show_top_bar(self) -> None:
        if not getattr(self, "top_bar_visible", False):
            self.top_bar.pack(side="top", fill="x")
            self.content_container.pack_forget()
            self.content_container.pack(fill="both", expand=True)
            self.top_bar_visible = True

    def _hide_top_bar(self) -> None:
        if getattr(self, "top_bar_visible", False):
            self.top_bar.pack_forget()
            self.top_bar_visible = False


if __name__ == "__main__":
    app = EbayListingApp()
    app.run()
