"""Execute no Windows para gerar dist/CastleInvasion.exe (PyInstaller)."""

import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "CastleInvasion",
        "--paths",
        str(root / "src"),
        "--collect-data",
        "castle_invasion",
        str(root / "main.py"),
    ],
    cwd=root,
    check=True,
)
