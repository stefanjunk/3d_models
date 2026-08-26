from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return data


def save_json(path: str | Path, data: Any) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_hex(value: str) -> str:
    value = value.strip().upper()
    if not value.startswith("#"):
        value = "#" + value
    if len(value) == 9:
        value = value[:7]
    if len(value) != 7 or any(c not in "#0123456789ABCDEF" for c in value):
        raise ValueError(f"Invalid RGB hex color: {value!r}")
    return value


def hex_to_rgb01(value: str) -> tuple[float, float, float]:
    value = normalize_hex(value)
    return tuple(int(value[i : i + 2], 16) / 255.0 for i in (1, 3, 5))


def hex_to_rgb8(value: str) -> tuple[int, int, int]:
    value = normalize_hex(value)
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))


def load_palette(path: str | Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    filaments = data.get("filaments")
    if not isinstance(filaments, list) or not filaments:
        raise ValueError("Palette must contain a non-empty 'filaments' list")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(filaments):
        if not isinstance(item, dict):
            raise ValueError(f"Palette entry {index} is not a mapping")
        filament_id = str(item.get("id", "")).strip()
        if not filament_id or filament_id in seen:
            raise ValueError(f"Palette entry has missing or duplicate id: {filament_id!r}")
        seen.add(filament_id)
        entry = dict(item)
        entry["id"] = filament_id
        entry["name"] = str(entry.get("name", filament_id))
        entry["display_hex"] = normalize_hex(str(entry.get("display_hex", "#808080")))
        normalized.append(entry)
    return normalized


def resolve_manifest_path(manifest_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (manifest_path.parent / path).resolve()
