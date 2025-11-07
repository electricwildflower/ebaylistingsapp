"""
Bootstrap pip inside a portable or embeddable Python distribution.

This script is safe to run multiple times. It only downloads `get-pip.py`
when pip is missing inside the bundled interpreter.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlretrieve

GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


def _pip_exists(python_dir: Path) -> bool:
    scripts_dir = python_dir / "Scripts"
    pip_exe = scripts_dir / "pip.exe"
    return pip_exe.exists()


def ensure_pip(python_dir: Path) -> None:
    if _pip_exists(python_dir):
        return

    print("pip not found; downloading get-pip.py...")
    with tempfile.TemporaryDirectory() as tmpdir:
        get_pip_path = Path(tmpdir) / "get-pip.py"
        urlretrieve(GET_PIP_URL, get_pip_path)
        print("Installing pip into portable interpreter...")
        subprocess.check_call(
            [
                sys.executable,
                str(get_pip_path),
                "--no-warn-script-location",
            ],
            cwd=python_dir,
        )


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    python_dir = project_root / "python"

    if not python_dir.exists():
        raise SystemExit(
            "Expected a portable Python in the 'python' folder. "
            "Download the embeddable package or WinPython and extract it there."
        )

    ensure_pip(python_dir)


if __name__ == "__main__":
    main()


