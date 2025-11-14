import json
import os
import tkinter as tk
from datetime import date, datetime
from typing import Any
from tkinter import filedialog, messagebox, ttk

try:
    from .settings_view import SettingsView
except ImportError:  # pragma: no cover
    from settings_view import SettingsView

try:
    from .firstrun import FirstRunWizard
except ImportError:  # pragma: no cover
    from firstrun import FirstRunWizard

try:
    from .add_category import AddCategoryView
except ImportError:  # pragma: no cover
    from add_category import AddCategoryView

try:
    from .add_item import AddItemView
except ImportError:  # pragma: no cover
    from add_item import AddItemView

try:
    from .items_added import ItemsAddedView
except ImportError:  # pragma: no cover
    from items_added import ItemsAddedView

try:
    from .end_items import EndItemsView
except ImportError:  # pragma: no cover
    from end_items import EndItemsView


def _format_date_display(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue
    return value


class EbayListingApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("eBay Listing App")
        self.default_geometry = "1100x760"
        self.root.geometry(self.default_geometry)
        self.root.minsize(960, 640)

        self.primary_bg = "#F2F7FF"
        self.accent_color = "#1E88E5"
        self.accent_hover = "#1565C0"
        self.card_bg = "#FFFFFF"
        self.text_color = "#0A2239"

        self.items: list[dict[str, Any]] = []

        self._configure_styles()

        self.config_path = self._resolve_config_path()
        self.config = self._load_config()
        self.is_fullscreen = bool(self.config.get("fullscreen", False))
        self.storage_path: str | None = self.config.get("storage_path")

        self._create_top_bar()
        self._create_content_container()
        self._active_frame: tk.Widget | None = None
        self._create_frames()
        self._apply_window_mode()

        if self.storage_path:
            self.add_item_frame.set_storage_path(self.storage_path)
            self.add_category_frame.set_storage_path(self.storage_path)
            self.show_main()
        else:
            self.show_first_run()

    # --------------------------------------------------------------------------------------------
    # UI setup
    # --------------------------------------------------------------------------------------------
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
            padding=(12, 8),
            font=("Segoe UI", 10),
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

    def _create_top_bar(self) -> None:
        self.top_bar = tk.Frame(self.root, bg="#FFFFFF")
        self.top_bar_visible = False

        row = tk.Frame(self.top_bar, bg="#FFFFFF")
        row.pack(side="top", fill="x")

        nav_container = tk.Frame(row, bg="#FFFFFF")
        nav_container.pack(side="left", padx=(16, 8), pady=4)

        def _create_menu_button(label: str, items: list[tuple[str, Callable[[], None]]]) -> ttk.Button:
            btn = ttk.Button(nav_container, text=label, style="TopNav.TMenubutton")
            menu = tk.Menu(
                btn,
                tearoff=0,
                background="#FFFFFF",
                foreground=self.text_color,
                activebackground=self.accent_color,
                activeforeground="white",
                borderwidth=0,
                relief="flat",
            )
            for text, command in items:
                menu.add_command(label=text, command=command)

            def show_menu(_: Any | None = None) -> None:
                x = btn.winfo_rootx()
                y = btn.winfo_rooty() + btn.winfo_height()
                try:
                    menu.tk_popup(x, y)
                finally:
                    menu.grab_release()

            btn.configure(command=show_menu)
            btn.pack(side="left", padx=4)
            return btn

        _create_menu_button("File", [("Exit", self.root.quit)])

        ttk.Button(
            nav_container,
            text="Home",
            style="TopNav.TMenubutton",
            command=self.show_main,
        ).pack(side="left", padx=4)

        _create_menu_button(
            "Categories",
            [("Add/Edit/Delete Categories", self.show_add_category)],
        )

        _create_menu_button(
            "Listings",
            [
                ("Add a New Item", self.show_add_item),
                ("Items Added", self.show_items_added),
                ("Items Ended", self.show_end_item),
            ],
        )

        _create_menu_button(
            "Settings",
            [
                ("App Settings", self.show_settings),
                ("Storage Config", self.show_storage_config),
            ],
        )

        ttk.Button(
            nav_container,
            text="Trending",
            style="TopNav.TMenubutton",
            command=self.show_trending,
        ).pack(side="left", padx=4)

        spacer = tk.Frame(row, bg="#FFFFFF")
        spacer.pack(side="left", fill="x", expand=True)

        accent = tk.Frame(self.top_bar, bg="#0064D2", height=2)
        accent.pack(side="top", fill="x")

    def _create_content_container(self) -> None:
        self.content_container = tk.Frame(self.root, bg=self.primary_bg)
        self.content_container.pack(fill="both", expand=True)

    def _create_frames(self) -> None:
        self.main_scroll_canvas = tk.Canvas(
            self.content_container,
            bg=self.primary_bg,
            highlightthickness=0,
            borderwidth=0,
        )
        self.main_scroll_canvas.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.main_scroll_canvas, bg=self.primary_bg)
        self.main_scroll_window = self.main_scroll_canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw"
        )

        self.main_frame.bind("<Configure>", self._sync_main_scroll_region)
        self.main_scroll_canvas.bind("<Configure>", self._match_main_canvas_width)
        self.main_scroll_canvas.bind("<Enter>", self._bind_main_mousewheel)
        self.main_scroll_canvas.bind("<Leave>", self._unbind_main_mousewheel)

        self.settings_view = SettingsView(
            self.content_container,
            primary_bg=self.primary_bg,
            card_bg=self.card_bg,
            text_color=self.text_color,
            show_main_callback=self.show_main,
            toggle_fullscreen_callback=self.toggle_fullscreen_mode,
        )

        self.add_category_frame = AddCategoryView(
            self.content_container,
            primary_bg=self.primary_bg,
            text_color=self.text_color,
            storage_path=self.storage_path,
            on_categories_changed=self._update_categories_display,
            items_provider=self._get_items_list,
            edit_item_callback=self._edit_item,
            delete_item_callback=self._delete_item,
            open_item_callback=self._open_item_details,
            end_item_callback=self._end_item,
            add_item_callback=self._add_item_for_category,
            rename_category_callback=self._rename_category_items,
        )

        self.add_item_frame = AddItemView(
            self.content_container,
            primary_bg=self.primary_bg,
            text_color=self.text_color,
            storage_path=self.storage_path,
            categories_provider=self.add_category_frame.get_categories,
            on_items_changed=self._update_items_display,
        )

        self.items_added_frame = ItemsAddedView(
            self.content_container,
            primary_bg=self.primary_bg,
            text_color=self.text_color,
            card_bg=self.card_bg,
            items_provider=self.items,
            edit_callback=self._edit_item,
            delete_callback=self._delete_item,
            open_callback=self._open_item_details,
            end_callback=self._end_item,
        )

        self.end_item_frame = EndItemsView(
            self.content_container,
            primary_bg=self.primary_bg,
            text_color=self.text_color,
            card_bg=self.card_bg,
            items_provider=self.items,
            open_callback=self._open_item_details,
            edit_callback=self._edit_item,
            restore_callback=self._restore_item,
            delete_callback=self._delete_item,
        )

        self.storage_config_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self._build_storage_config_view()
        self.trending_frame = tk.Frame(self.content_container, bg=self.primary_bg)
        self._build_trending_view()

        self._build_main_hero_title()

        heading = tk.Label(
            self.main_frame,
            text="Manage your listings at a glance",
            font=("Segoe UI Semibold", 24),
            bg=self.primary_bg,
            fg=self.text_color,
        )
        heading.pack(pady=(12, 16))

        self._build_global_search()

        self.dashboard_container = tk.Frame(self.main_frame, bg=self.primary_bg)
        self.dashboard_container.pack(fill="both", expand=True, padx=40, pady=(12, 40))
        self.dashboard_container.columnconfigure(0, weight=2)
        self.dashboard_container.columnconfigure(1, weight=1)
        self.dashboard_container.rowconfigure(0, weight=1)

        self._build_main_categories_section()
        self._build_recent_items_section()
        self._search_mode = False

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

    # --------------------------------------------------------------------------------------------
    # Top bar helpers
    # --------------------------------------------------------------------------------------------
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

    def _show_frame(self, frame: tk.Widget) -> None:
        for widget in (
            self.main_scroll_canvas,
            self.settings_view,
            self.add_category_frame,
            self.add_item_frame,
            self.items_added_frame,
            self.end_item_frame,
            self.storage_config_frame,
            self.trending_frame,
            self.first_run_frame,
        ):
            widget.pack_forget()
        frame.pack(fill="both", expand=True)
        self._active_frame = frame
        if frame is self.main_scroll_canvas:
            self._sync_main_scroll_region(None)
        if frame is not self.add_item_frame and hasattr(self, "add_item_frame"):
            self.add_item_frame.close_item_details()

    # --------------------------------------------------------------------------------------------
    # Navigation
    # --------------------------------------------------------------------------------------------
    def show_main(self) -> None:
        self._show_top_bar()
        self._show_frame(self.main_scroll_canvas)
        if hasattr(self, "global_search_var"):
            self._clear_search()
        self._render_recent_items()
        self._render_main_categories(self.add_category_frame.get_categories())

    def show_settings(self) -> None:
        self._show_top_bar()
        self._show_frame(self.settings_view)

    def show_add_category(self) -> None:
        self._show_top_bar()
        self._show_frame(self.add_category_frame)

    def show_add_item(self) -> None:
        previous_frame = getattr(self, "_active_frame", None)
        self._show_top_bar()
        self._show_frame(self.add_item_frame)
        self.add_item_frame.open_add_item_dialog(
            on_close=lambda cancelled: self._return_to_frame(previous_frame)
        )

    def show_items_added(self) -> None:
        self._show_top_bar()
        self.items_added_frame.set_items(self.items)
        self._show_frame(self.items_added_frame)

    def show_end_item(self) -> None:
        self._show_top_bar()
        self.end_item_frame.set_items(self.items)
        self._show_frame(self.end_item_frame)

    def show_trending(self) -> None:
        self._show_top_bar()
        self._show_frame(self.trending_frame)

    def show_storage_config(self) -> None:
        self._show_top_bar()
        self._update_storage_config_view()
        self._show_frame(self.storage_config_frame)

    def show_first_run(self) -> None:
        self._hide_top_bar()
        self._show_frame(self.first_run_frame)

    # --------------------------------------------------------------------------------------------
    # Dashboard rendering
    # --------------------------------------------------------------------------------------------
    def _build_main_hero_title(self) -> None:
        self.hero_title_frame = tk.Frame(self.main_frame, bg=self.primary_bg)
        self.hero_title_frame.pack(pady=(32, 8))

        palette = ("#E53238", "#0064D2", "#F5AF02", "#86B817")
        title_text = "eBay Listings Manager"
        palette_index = 0

        for char in title_text:
            if char == " ":
                tk.Label(self.hero_title_frame, text=" ", font=("Segoe UI Semibold", 26), bg=self.primary_bg).pack(side="left")
                continue

            color = palette[palette_index % len(palette)]
            tk.Label(
                self.hero_title_frame,
                text=char,
                font=("Segoe UI Semibold", 26),
                bg=self.primary_bg,
                fg=color,
            ).pack(side="left")
            palette_index += 1

    def _build_main_categories_section(self) -> None:
        self.main_categories_section = tk.Frame(self.dashboard_container, bg=self.primary_bg)
        self.main_categories_section.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        tk.Label(
            self.main_categories_section,
            text="Categories",
            font=("Segoe UI Semibold", 20),
            bg=self.primary_bg,
            fg=self.text_color,
        ).pack(anchor="w")

        self.main_categories_container = tk.Frame(self.main_categories_section, bg=self.primary_bg)
        self.main_categories_container.pack(fill="both", expand=True, pady=(12, 0))

    def _build_recent_items_section(self) -> None:
        self.main_recent_section = tk.Frame(self.dashboard_container, bg=self.primary_bg)
        self.main_recent_section.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            self.main_recent_section,
            text="Items Overview",
            font=("Segoe UI Semibold", 20),
            bg=self.primary_bg,
            fg=self.text_color,
        ).pack(anchor="w")

        notebook_container = tk.Frame(self.main_recent_section, bg=self.primary_bg)
        notebook_container.pack(fill="both", expand=True, pady=(12, 0))

        self.main_recent_notebook = ttk.Notebook(notebook_container)
        self.main_recent_notebook.pack(fill="both", expand=True)

        self.recent_items_tab = tk.Frame(self.main_recent_notebook, bg=self.primary_bg)
        self.ended_items_tab = tk.Frame(self.main_recent_notebook, bg=self.primary_bg)
        self.main_recent_notebook.add(self.recent_items_tab, text="Recently Added")
        self.main_recent_notebook.add(self.ended_items_tab, text="Items Ended")

        self.main_recent_container = tk.Frame(self.recent_items_tab, bg=self.primary_bg)
        self.main_recent_container.pack(fill="both", expand=True, padx=4, pady=4)

        self.main_ended_container = tk.Frame(self.ended_items_tab, bg=self.primary_bg)
        self.main_ended_container.pack(fill="both", expand=True, padx=4, pady=4)

    def _render_main_categories(self, categories: list[dict[str, str]]) -> None:
        for child in self.main_categories_container.winfo_children():
            child.destroy()

        columns = 2
        for col in range(columns):
            self.main_categories_container.grid_columnconfigure(col, weight=1, uniform="categories")

        if not categories:
            tk.Label(
                self.main_categories_container,
                text="No categories to display yet.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            ).grid(row=0, column=0, sticky="w")
            return

        for index, category in enumerate(categories):
            row = index // columns
            column = index % columns
            card = tk.Frame(
                self.main_categories_container,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=14,
                pady=12,
            )
            card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

            tk.Label(
                card,
                text=category.get("name", ""),
                font=("Segoe UI Semibold", 13),
                bg=self.card_bg,
                fg=self.text_color,
            ).pack(anchor="w")

            description = category.get("description", "")
            if description:
                tk.Label(
                    card,
                    text=description,
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#41566F",
                    wraplength=200,
                    justify="left",
                ).pack(anchor="w", pady=(4, 6))

            days = category.get("days")
            if days:
                tk.Label(
                    card,
                    text=f"Duration: {days} day(s)",
                    font=("Segoe UI", 9),
                    bg=self.card_bg,
                    fg="#6F7F92",
                ).pack(anchor="w")

            item_total = sum(
                1
                for item in self.items
                if item.get("category") == category.get("name")
                and (item.get("status") or "active").lower() != "ended"
            )
            tk.Label(
                card,
                text=f"Active items: {item_total}",
                font=("Segoe UI", 9),
                bg=self.card_bg,
                fg="#1E88E5" if item_total else "#6F7F92",
            ).pack(anchor="w", pady=(4, 8))

            ttk.Button(
                card,
                text="Open",
                style="Secondary.TButton",
                command=lambda cat=dict(category): self._open_category_from_main(cat),
            ).pack(anchor="e")

        self._sync_main_scroll_region(None)

    def _open_category_from_main(self, category: dict[str, str]) -> None:
        self.show_add_category()
        self.add_category_frame._open_category_items(category)

    def _update_categories_display(self, categories: list[dict[str, str]]) -> None:
        if hasattr(self, "main_categories_container"):
            self._render_main_categories(categories)
        if hasattr(self, "global_search_var"):
            self._perform_global_search(self.global_search_var.get())

    def _render_recent_items(self) -> None:
        if not hasattr(self, "main_recent_container") or not hasattr(self, "main_ended_container"):
            return

        for container in (self.main_recent_container, self.main_ended_container):
            for child in container.winfo_children():
                child.destroy()

        active_items = [
            item for item in self.items if (item.get("status") or "active").lower() != "ended"
        ]
        recent_items = list(reversed(active_items[-10:]))
        if not recent_items:
            tk.Label(
                self.main_recent_container,
                text="No items have been added yet.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            ).pack(anchor="w")
        else:
            for item in recent_items:
                self._render_item_card(self.main_recent_container, item, ended=False)

        ended_items = [
            item for item in self.items if (item.get("status") or "active").lower() == "ended"
        ]
        ended_items.sort(key=lambda itm: abs(self._days_left(itm) or 0))
        ended_items = ended_items[:10]
        if not ended_items:
            tk.Label(
                self.main_ended_container,
                text="No ended items.",
                font=("Segoe UI", 12),
                bg=self.primary_bg,
                fg="#5A6D82",
            ).pack(anchor="w")
        else:
            for item in ended_items:
                self._render_item_card(self.main_ended_container, item, ended=True)

    def _render_item_card(self, container: tk.Frame, item: dict[str, Any], *, ended: bool) -> None:
        card = tk.Frame(
            container,
            bg=self.card_bg,
            highlightthickness=1,
            highlightbackground="#D7E3F5",
            padx=16,
            pady=12,
        )
        card.pack(fill="x", pady=(0, 10))

        header = tk.Frame(card, bg=self.card_bg)
        header.pack(fill="x")

        name = item.get("name") or item.get("description", "Item")
        tk.Label(
            header,
            text=name,
            font=("Segoe UI Semibold", 13),
            bg=self.card_bg,
            fg=self.text_color,
        ).pack(side="left")

        days_left = self._days_left(item)
        if ended:
            ended_text = "Ended"
            if days_left is not None and days_left < 0:
                ended_text = f"Ended {abs(days_left)} day(s) ago"
            tk.Label(
                header,
                text=ended_text,
                font=("Segoe UI Semibold", 11),
                bg=self.card_bg,
                fg="#C62828",
            ).pack(side="right")
        elif days_left is not None:
            tk.Label(
                header,
                text=f"{max(days_left, 0)} day(s) left",
                font=("Segoe UI Semibold", 11),
                bg=self.card_bg,
                fg="#1E88E5" if days_left > 0 else "#C62828",
            ).pack(side="right")

        details = []
        if item.get("category"):
            details.append(f"Category: {item['category']}")
        if item.get("date_added"):
            details.append(f"Added: {_format_date_display(item.get('date_added'))}")
        if item.get("end_date"):
            details.append(f"End: {_format_date_display(item.get('end_date'))}")
        status = (item.get("status") or "active").capitalize()
        details.append(f"Status: {status}")
        tk.Label(
            card,
            text=" • ".join(details),
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg="#41566F",
        ).pack(anchor="w", pady=(4, 4))

        notes = item.get("notes")
        if notes:
            tk.Label(
                card,
                text=f"Notes: {notes}",
                font=("Segoe UI", 10),
                bg=self.card_bg,
                fg="#60738A",
                wraplength=420,
                justify="left",
            ).pack(anchor="w")

        ttk.Button(
            card,
            text="Open",
            style="Secondary.TButton",
            command=lambda item_id=item.get("id"): self._open_item_details(item_id),
        ).pack(anchor="e", pady=(8, 0))

    def _days_left(self, item: dict[str, Any]) -> int | None:
        end = item.get("end_date")
        if not end:
            return None
        try:
            end_date = date.fromisoformat(end)
        except ValueError:
            return None
        return (end_date - date.today()).days

    def _update_items_display(self, items: list[dict[str, Any]]) -> None:
        self.items = items
        self._render_recent_items()
        self._render_main_categories(self.add_category_frame.get_categories())
        self.items_added_frame.set_items(items)
        self.end_item_frame.set_items(items)
        self.add_category_frame.refresh_open_category_items()
        if hasattr(self, "global_search_var"):
            self._perform_global_search(self.global_search_var.get())

    def _edit_item(self, item_id: str, restore: bool = False) -> None:
        previous_frame = getattr(self, "_active_frame", None)
        self._show_top_bar()
        self._show_frame(self.add_item_frame)
        self.add_item_frame.edit_item(
            item_id,
            restore_on_save=restore,
            on_close=lambda cancelled: self._return_to_frame(previous_frame),
        )

    def _delete_item(self, item_id: str) -> None:
        self.add_item_frame.delete_item(item_id)

    def _end_item(self, item_id: str) -> None:
        self.add_item_frame.end_item(item_id)

    def _restore_item(self, item_id: str) -> None:
        self.add_item_frame.restore_item(item_id)

    def _open_item_details(self, item_id: str) -> None:
        previous_frame = getattr(self, "_active_frame", None)
        self._show_top_bar()
        self._show_frame(self.add_item_frame)
        self.add_item_frame.open_item_details(
            item_id,
            on_back=lambda: self._return_to_frame(previous_frame),
        )

    # --------------------------------------------------------------------------------------------
    # Global search helpers
    # --------------------------------------------------------------------------------------------
    def _build_global_search(self) -> None:
        self.global_search_wrapper = tk.Frame(self.main_frame, bg=self.primary_bg)
        self.global_search_wrapper.pack(fill="x", padx=40, pady=(0, 24))

        ttk.Label(
            self.global_search_wrapper,
            text="Search across categories and items",
            background=self.primary_bg,
            foreground=self.text_color,
            font=("Segoe UI", 11),
        ).pack(anchor="w")

        row = tk.Frame(self.global_search_wrapper, bg=self.primary_bg)
        row.pack(fill="x", pady=(8, 0))

        self.global_search_var = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.global_search_var, width=50)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda _: self._perform_global_search(self.global_search_var.get()))

        ttk.Button(
            row,
            text="Search",
            style="Secondary.TButton",
            command=lambda: self._perform_global_search(self.global_search_var.get()),
        ).pack(side="left", padx=(8, 0))

        self.global_search_clear_btn = ttk.Button(
            row,
            text="Clear",
            style="Secondary.TButton",
            command=self._clear_search,
        )
        self.global_search_clear_btn.pack(side="left", padx=(8, 0))
        self._set_clear_search_enabled(False)

        self.global_search_results = tk.Frame(self.global_search_wrapper, bg=self.primary_bg)

        self.global_search_var.trace_add("write", self._handle_global_search_update)

    def _handle_global_search_update(self, *_: Any) -> None:
        query = self.global_search_var.get().strip()
        if not query:
            self._clear_global_search_results()
            self._set_search_mode(False)
            self._set_clear_search_enabled(False)
        else:
            self._perform_global_search(query)

    def _clear_global_search_results(self) -> None:
        for child in self.global_search_results.winfo_children():
            child.destroy()

    def _perform_global_search(self, query: str) -> None:
        raw_query = query or ""
        query_str = raw_query.strip()
        if not query_str:
            self._clear_global_search_results()
            self._set_search_mode(False)
            self._set_clear_search_enabled(False)
            return

        query_lower = query_str.lower()
        self._clear_global_search_results()

        categories = self.add_category_frame.get_categories()
        items = self.add_item_frame.get_items()
        results: list[tuple[str, dict[str, Any]]] = []

        for category in categories:
            name = category.get("name", "")
            description = category.get("description", "")
            if query_lower in name.lower() or query_lower in description.lower():
                results.append(("category", category))

        for item in items:
            if (
                query_lower in (item.get("name") or "").lower()
                or query_lower in (item.get("description") or "").lower()
                or query_lower in (item.get("notes") or "").lower()
            ):
                results.append(("item", item))

        self._set_search_mode(True)
        self._set_clear_search_enabled(True)

        if not results:
            tk.Label(
                self.global_search_results,
                text="No matches found.",
                font=("Segoe UI", 11),
                bg=self.primary_bg,
                fg="#5A6D82",
            ).pack(anchor="w")
            return

        for result_type, payload in results[:12]:
            card = tk.Frame(
                self.global_search_results,
                bg=self.card_bg,
                highlightthickness=1,
                highlightbackground="#D7E3F5",
                padx=14,
                pady=10,
            )
            card.pack(fill="x", pady=(0, 8))

            if result_type == "category":
                name = payload.get("name", "Category")
                tk.Label(
                    card,
                    text=f"Category • {name}",
                    font=("Segoe UI Semibold", 12),
                    bg=self.card_bg,
                    fg=self.text_color,
                ).pack(anchor="w")

                summary = payload.get("description") or ""
                if summary:
                    tk.Label(
                        card,
                        text=summary,
                        font=("Segoe UI", 10),
                        bg=self.card_bg,
                        fg="#41566F",
                        wraplength=460,
                        justify="left",
                    ).pack(anchor="w", pady=(4, 6))

                ttk.Button(
                    card,
                    text="Open Category",
                    style="Secondary.TButton",
                    command=lambda cat=dict(payload): self._open_category_from_main(cat),
                ).pack(anchor="e")
            else:
                name = payload.get("name") or payload.get("description", "Item")
                tk.Label(
                    card,
                    text=f"Item • {name}",
                    font=("Segoe UI Semibold", 12),
                    bg=self.card_bg,
                    fg=self.text_color,
                ).pack(anchor="w")

                details = []
                if payload.get("category"):
                    details.append(f"Category: {payload['category']}")
                if payload.get("date_added"):
                    details.append(f"Added: {_format_date_display(payload.get('date_added'))}")
                if payload.get("end_date"):
                    details.append(f"End: {_format_date_display(payload.get('end_date'))}")
                status = (payload.get("status") or "active").capitalize()
                details.append(f"Status: {status}")
                tk.Label(
                    card,
                    text=" • ".join(details),
                    font=("Segoe UI", 10),
                    bg=self.card_bg,
                    fg="#41566F",
                ).pack(anchor="w", pady=(4, 4))

                ttk.Button(
                    card,
                    text="Open Item",
                    style="Secondary.TButton",
                    command=lambda item_id=payload.get("id"): self._open_item_details(item_id),
                ).pack(anchor="e")

    # --------------------------------------------------------------------------------------------
    # Configuration helpers
    # --------------------------------------------------------------------------------------------
    def _select_storage_path(self) -> None:
        selected_dir = filedialog.askdirectory(
            parent=self.root,
            title="Select Storage Folder",
            mustexist=True,
        )
        if selected_dir:
            self._apply_storage_directory(selected_dir)

    def toggle_fullscreen_mode(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self._apply_window_mode()
        self._save_config()

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
        self.add_item_frame.set_storage_path(config_dir)
        self.add_category_frame.set_storage_path(config_dir)
        self._update_storage_config_view()
        self._save_config()
        self.show_main()
        return True

    def _default_storage_base_path(self) -> str:
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.isdir(documents):
            return documents
        return os.path.expanduser("~")

    def _resolve_config_path(self) -> str:
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        base_dir = documents if os.path.isdir(documents) else os.path.expanduser("~")
        config_dir = os.path.join(base_dir, "ebaylistingapp")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "app_config.json")

    def _load_config(self) -> dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as cfg:
                    data = json.load(cfg)
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
            with open(self.config_path, "w", encoding="utf-8") as cfg:
                json.dump(data, cfg, indent=2)
        except OSError as exc:
            messagebox.showwarning(
                "Settings",
                f"Unable to save settings.\n\n{exc}",
                parent=self.root,
            )

    def _on_first_run_complete(self) -> None:
        if not self.storage_path:
            return
        self.show_main()

    # --------------------------------------------------------------------------------------------
    # Canvas helpers
    # --------------------------------------------------------------------------------------------
    def _sync_main_scroll_region(self, _: Any) -> None:
        self.main_scroll_canvas.configure(scrollregion=self.main_scroll_canvas.bbox("all"))

    def _match_main_canvas_width(self, event: Any) -> None:
        self.main_scroll_canvas.itemconfigure(self.main_scroll_window, width=event.width)

    def _bind_main_mousewheel(self, _: Any) -> None:
        self.main_scroll_canvas.bind_all("<MouseWheel>", self._on_main_mousewheel)
        self.main_scroll_canvas.bind_all("<Button-4>", self._on_main_mousewheel)
        self.main_scroll_canvas.bind_all("<Button-5>", self._on_main_mousewheel)

    def _unbind_main_mousewheel(self, _: Any) -> None:
        self.main_scroll_canvas.unbind_all("<MouseWheel>")
        self.main_scroll_canvas.unbind_all("<Button-4>")
        self.main_scroll_canvas.unbind_all("<Button-5>")

    def _on_main_mousewheel(self, event: Any) -> None:
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self.main_scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self.main_scroll_canvas.yview_scroll(1, "units")

    def _get_items_list(self) -> list[dict[str, Any]]:
        return self.add_item_frame.get_items()

    def _set_search_mode(self, active: bool) -> None:
        current = getattr(self, "_search_mode", False)
        if active and not current:
            if self.dashboard_container.winfo_ismapped():
                self.dashboard_container.pack_forget()
            if hasattr(self, "global_search_results"):
                self.global_search_results.pack(fill="both", expand=True, pady=(12, 0))
            self._search_mode = True
        elif not active and current:
            if hasattr(self, "global_search_results") and self.global_search_results.winfo_ismapped():
                self.global_search_results.pack_forget()
            if not self.dashboard_container.winfo_ismapped():
                self.dashboard_container.pack(fill="both", expand=True, padx=40, pady=(12, 40))
            self._search_mode = False

    def _set_clear_search_enabled(self, enabled: bool) -> None:
        if not hasattr(self, "global_search_clear_btn"):
            return
        if enabled:
            self.global_search_clear_btn.state(["!disabled"])
        else:
            self.global_search_clear_btn.state(["disabled"])

    def _clear_search(self) -> None:
        if not hasattr(self, "global_search_var"):
            return
        self.global_search_var.set("")
        self._clear_global_search_results()
        self._set_search_mode(False)
        self._set_clear_search_enabled(False)

    def _return_to_frame(self, frame: tk.Widget | None) -> None:
        if hasattr(self, "add_item_frame"):
            self.add_item_frame.close_item_details()
        if frame is self.main_scroll_canvas or frame is None:
            self.show_main()
        elif frame is self.items_added_frame:
            self.show_items_added()
        elif frame is self.end_item_frame:
            self.show_end_item()
        elif frame is self.add_category_frame:
            self.show_add_category()
        elif frame is self.settings_view:
            self.show_settings()
        elif frame is self.trending_frame:
            self.show_trending()
        elif frame is self.storage_config_frame:
            self.show_storage_config()
        else:
            self.show_main()

    def _add_item_for_category(self, category_name: str) -> None:
        previous_frame = getattr(self, "_active_frame", None)
        self._show_top_bar()
        self._show_frame(self.add_item_frame)
        self.add_item_frame.open_add_item_dialog(
            on_close=lambda cancelled: self._return_to_frame(previous_frame),
            default_category=category_name,
        )

    def _rename_category_items(self, old_name: str, new_name: str) -> None:
        self.add_item_frame.rename_category(old_name, new_name)

    def _build_storage_config_view(self) -> None:
        frame = self.storage_config_frame
        frame.configure(bg=self.primary_bg)

        container = tk.Frame(frame, bg=self.primary_bg)
        container.pack(fill="both", expand=True, padx=40, pady=60)

        self._create_colored_heading(container, "Storage Configuration")

        description = tk.Label(
            container,
            text=(
                "Choose where to store your configuration files. "
                "Selecting a shared folder lets multiple installations share data."
            ),
            font=("Segoe UI", 11),
            bg=self.primary_bg,
            fg="#41566F",
            wraplength=620,
            justify="left",
        )
        description.pack(anchor="w", pady=(16, 20))

        info_row = tk.Frame(container, bg=self.primary_bg)
        info_row.pack(fill="x", pady=(0, 24))

        tk.Label(
            info_row,
            text="Current location:",
            font=("Segoe UI Semibold", 11),
            bg=self.primary_bg,
            fg=self.text_color,
        ).pack(anchor="w")

        self.storage_info_var = tk.StringVar()
        tk.Label(
            info_row,
            textvariable=self.storage_info_var,
            font=("Segoe UI", 11),
            bg=self.primary_bg,
            fg="#1E3A5F",
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Button(
            container,
            text="Choose Folder",
            style="Primary.TButton",
            command=self._select_storage_path,
        ).pack(anchor="w")

        self._update_storage_config_view()

    def _update_storage_config_view(self) -> None:
        if not hasattr(self, "storage_info_var"):
            return
        if self.storage_path:
            self.storage_info_var.set(self.storage_path)
        else:
            self.storage_info_var.set("No storage location selected yet.")

    def _build_trending_view(self) -> None:
        frame = self.trending_frame
        frame.configure(bg=self.primary_bg)

        container = tk.Frame(frame, bg=self.primary_bg)
        container.pack(fill="both", expand=True, padx=40, pady=60)

        self._create_colored_heading(container, "Trending")

        tk.Label(
            container,
            text="Trending",
            font=("Segoe UI", 13),
            bg=self.primary_bg,
            fg="#41566F",
        ).pack(anchor="w")

    def _create_colored_heading(
        self,
        parent: tk.Misc,
        text: str,
        *,
        font: tuple[str, int] = ("Segoe UI Semibold", 20),
        pady: tuple[int, int] = (0, 16),
    ) -> tk.Frame:
        container = tk.Frame(parent, bg=self.primary_bg)
        container.pack(anchor="w", pady=pady)
        palette = ("#E53238", "#0064D2", "#F5AF02", "#86B817")
        idx = 0
        for char in text:
            if char == " ":
                tk.Label(container, text=" ", font=font, bg=self.primary_bg).pack(side="left")
                continue
            color = palette[idx % len(palette)]
            tk.Label(container, text=char, font=font, bg=self.primary_bg, fg=color).pack(side="left")
            idx += 1
        return container


def main() -> None:
    app = EbayListingApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
