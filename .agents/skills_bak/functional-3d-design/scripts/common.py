#!/usr/bin/env python3
"""Shared helpers for the functional-3d-design skill."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = SKILL_ROOT / "data"
TEMPLATE_ROOT = SKILL_ROOT / "templates"


def load_structured(path: str | Path) -> Any:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    if p.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - dependency message
            raise SystemExit("PyYAML is required for YAML files: python -m pip install PyYAML") from exc
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported structured file extension: {p.suffix}")


def dump_json(data: Any, path: str | Path | None = None) -> str:
    text = json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False)
    if path is not None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    return text


def load_data(filename: str) -> Any:
    return load_structured(DATA_ROOT / filename)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
