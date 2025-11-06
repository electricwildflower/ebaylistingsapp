"""
Build script to create a standalone executable using PyInstaller
Run this script to create the .exe file: python build_exe.py

This creates a completely self-contained executable that includes
Python and all dependencies - no installation needed to run!
"""

import PyInstaller.__main__
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
app_script = os.path.join(script_dir, "ebaylistingapp.py")

PyInstaller.__main__.run([
    app_script,
    '--onefile',  # Create a single executable file (everything bundled)
    '--windowed',  # No console window (Windows only)
    '--name=Ebaylistingapp',  # Name of the executable
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Overwrite output without asking
    '--collect-all', 'tkinter',  # Ensure all tkinter files are included
])

