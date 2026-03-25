"""Entry point at repo root; adds ``src`` to ``sys.path`` and runs the package."""

from pathlib import Path
import sys

_SRC = Path(__file__).resolve().parent / "src"
_src_str = str(_SRC)
if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

from dataset_printer.main import main

if __name__ == "__main__":
    main()
