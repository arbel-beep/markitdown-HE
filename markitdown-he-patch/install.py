#!/usr/bin/env python3
"""Installer for the Hebrew/RTL fix patch for Microsoft's markitdown.

What this does:
  1. If markitdown isn't installed, installs it from PyPI (markitdown[all]).
  2. Overwrites two converter files inside the installed markitdown
     package with patched versions that fix:
       - PDF: Hebrew/Arabic text getting mangled (reversed words,
         fragmented lines) when a PDF has no form-style pages.
       - CSV: a leftover UTF-8 BOM character leaking into the first
         cell's content (common in CSVs exported from Excel with
         Hebrew/non-ASCII text).
  3. Backs up the original files (.orig) before overwriting, so the
     patch can be reverted.

Usage:
    python install.py
    python install.py --uninstall
"""

import shutil
import subprocess
import sys
from pathlib import Path

PATCHED_FILES = ["_pdf_converter.py", "_csv_converter.py"]


def ensure_markitdown_installed() -> None:
    try:
        import markitdown  # noqa: F401

        print("markitdown is already installed.")
    except ImportError:
        print("markitdown not found - installing markitdown[all] from PyPI...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "markitdown[all]"]
        )


def get_converters_dir() -> Path:
    import markitdown.converters as converters_pkg

    return Path(converters_pkg.__file__).parent


def install_patch() -> None:
    ensure_markitdown_installed()
    converters_dir = get_converters_dir()
    patch_dir = Path(__file__).parent

    for filename in PATCHED_FILES:
        target = converters_dir / filename
        backup = converters_dir / (filename + ".orig")
        source = patch_dir / filename

        if not backup.exists():
            shutil.copy2(target, backup)
            print(f"Backed up original: {backup}")

        shutil.copy2(source, target)
        print(f"Patched: {target}")

    print("\nDone. Hebrew/RTL fixes applied to your markitdown installation.")


def uninstall_patch() -> None:
    converters_dir = get_converters_dir()

    for filename in PATCHED_FILES:
        target = converters_dir / filename
        backup = converters_dir / (filename + ".orig")

        if backup.exists():
            shutil.copy2(backup, target)
            backup.unlink()
            print(f"Restored original: {target}")
        else:
            print(f"No backup found for {filename}, skipping.")

    print("\nDone. Original markitdown files restored.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall_patch()
    else:
        install_patch()
