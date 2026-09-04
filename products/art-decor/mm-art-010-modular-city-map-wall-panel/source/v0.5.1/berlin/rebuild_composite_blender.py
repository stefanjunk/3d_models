#!/usr/bin/env python3
"""Run the unchanged revision 0.5.0 Blender Boolean for revision 0.5.1.

Any numerical micro-degenerate repair is deliberately performed after this
authoritative Boolean and is recorded separately by the revision 0.5.1 build
wrapper.  This keeps map geometry and Boolean tolerances unchanged.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "v0.5.0" / "berlin" / "rebuild_composite_blender.py"


def load_previous():
    spec = importlib.util.spec_from_file_location("mm_art_010_composite_v050", PREVIOUS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load previous composite builder: {PREVIOUS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

if __name__ == "__main__":
    previous = load_previous()
    previous.main()
