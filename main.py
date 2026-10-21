"""Entrada de desenvolvimento: python main.py, sem instalação do pacote."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from castle_invasion.bootstrap import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
