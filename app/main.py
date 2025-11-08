import tkinter as tk


def main() -> None:
    root = tk.Tk()
    root.title("Ebay Listing App")
    root.geometry("800x600")
    root.resizable(False, False)

    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu_bar)

    label = tk.Label(root, text="ebaylistingapp", font=("Helvetica", 14))
    label.pack(padx=20, pady=20)
    root.mainloop()


if __name__ == "__main__":
    main()
