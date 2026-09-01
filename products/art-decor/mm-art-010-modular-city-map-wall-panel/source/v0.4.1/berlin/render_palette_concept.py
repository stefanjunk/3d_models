#!/usr/bin/env python3
"""Render revision 0.4.1 with the selected physical four-spool palette."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
LEGACY_RENDERER = PRODUCT / "source" / "v0.4.0" / "berlin" / "render_display_modes_concept.py"
PARAMETER_SOURCE = HERE / "display-mode-parameters.json"


def load_legacy_renderer():
    spec = importlib.util.spec_from_file_location("mm_art_010_display_renderer", LEGACY_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load renderer: {LEGACY_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    renderer = load_legacy_renderer()
    parameters = json.loads(PARAMETER_SOURCE.read_text())
    renderer.PARAMETER_SOURCE = PARAMETER_SOURCE
    renderer.PARAMETERS = parameters
    renderer.PALETTE = parameters["shared"]["palette"]
    renderer.PALETTE_LABELS = parameters["shared"]["palette_labels"]
    renderer.OUTPUT = PRODUCT / "concepts" / "berlin-display-modes-concept-v04.png"
    renderer.REPORT = PRODUCT / "concepts" / "berlin-display-modes-concept-v04.json"
    renderer.main()


if __name__ == "__main__":
    main()
