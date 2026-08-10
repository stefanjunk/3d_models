#!/usr/bin/env python3
"""Compatibility entry point for the canonical mesh-validation skill."""

from __future__ import annotations

import importlib.util
from pathlib import Path


CORE_PATH = Path(__file__).resolve().parents[2] / "mesh-validation" / "scripts" / "validate_mesh.py"
SPEC = importlib.util.spec_from_file_location("canonical_mesh_validation", CORE_PATH)
CORE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CORE)

edge_counts = CORE.edge_counts
report_for = CORE.report_for


def load_mesh(path: str | Path):
    return CORE.load_mesh(Path(path), process=False)


def main() -> int:
    return CORE.main()


if __name__ == "__main__":
    raise SystemExit(main())
