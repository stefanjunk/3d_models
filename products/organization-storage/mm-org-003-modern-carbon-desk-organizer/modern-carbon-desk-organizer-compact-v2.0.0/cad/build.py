#!/usr/bin/env python3
"""Bounded-memory deterministic build orchestrator for MM-ORG-003."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cad" / "build_compact_organizer.py"
FINALIZER = ROOT / "cad" / "finalize_compact_build.py"


def main() -> None:
    for part in ("housing", "drawer", "sorter", "fit_coupon", "texture_coupon"):
        subprocess.run([sys.executable, "-u", str(SOURCE), "--part", part], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "-u", str(FINALIZER)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
