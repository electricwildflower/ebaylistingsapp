import tkinter as tk


class EbayListingApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Ebay Listing App")
        self.default_geometry = "800x600"
        self.root.geometry(self.default_geometry)
        self.root.resizable(False, False)
        self.is_fullscreen = False

        self._create_menu()
        self._create_frames()
        self.show_main()

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="App Settings", command=self.show_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menu_bar)

    def _create_frames(self) -> None:
        self.main_frame = tk.Frame(self.root)
        self.settings_frame = tk.Frame(self.root)

        label = tk.Label(self.main_frame, text="ebaylistingapp", font=("Helvetica", 14))
        label.pack(padx=20, pady=20)

        settings_header = tk.Label(self.settings_frame, text="App Settings", font=("Helvetica", 16, "bold"))
        settings_header.pack(pady=(20, 10))

        self.toggle_button = tk.Button(
            self.settings_frame,
            text="Switch to Fullscreen",
            command=self.toggle_fullscreen_mode,
            width=25,
        )
        self.toggle_button.pack(pady=10)

        back_button = tk.Button(
            self.settings_frame,
            text="Back",
            command=self.show_main,
            width=25,
        )
        back_button.pack(pady=(0, 20))

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
