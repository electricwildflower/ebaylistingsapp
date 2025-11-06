#!/usr/bin/env python3
"""
Ebaylistingapp - A simple self-contained application
"""

import tkinter as tk
from tkinter import messagebox


class EbayListingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ebaylistingapp")
        self.root.geometry("400x300")
        self.root.configure(bg="white")
        
        # Create menu bar
        self.create_menu()
        
        # Create main content
        self.create_content()
        
        # Center the window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu(self):
        """Create the menu bar with exit button"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_exit)
    
    def create_content(self):
        """Create the main content area"""
        # Create a label with the text centered
        label = tk.Label(
            self.root,
            text="Ebaylistingapp",
            font=("Arial", 24, "bold"),
            fg="black",
            bg="white"
        )
        label.pack(expand=True)
    
    def on_exit(self):
        """Handle exit menu item"""
        self.root.quit()


def main():
    root = tk.Tk()
    app = EbayListingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

