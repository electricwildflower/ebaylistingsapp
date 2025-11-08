import tkinter as tk


def main() -> None:
    root = tk.Tk()
    root.title("Ebay Listing App")
    root.geometry("480x480")
    root.resizable(False, False)
    label = tk.Label(root, text="ebaylistingapp", font=("Helvetica", 14))
    label.pack(padx=20, pady=20)
    root.mainloop()


if __name__ == "__main__":
    main()
