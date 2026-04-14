#!/usr/bin/env python3
# This is NOT a setuptools setup.py.
# This is the Flask Boilerplate project setup wizard.
# Run once after cloning: python setup.py
from __future__ import annotations

import sys
from pathlib import Path

if not (Path(__file__).parent / "app" / "__init__.py").exists():
    print("Error: run this script from the project root directory.")
    sys.exit(1)

from setup import main  # noqa: E402

if __name__ == "__main__":
    main()
