#!/usr/bin/env python3
"""Resolve the selected surface profile without mutating versioned configuration."""

from __future__ import annotations

import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def surface_index(root: Path) -> tuple[Path, dict]:
    path = root / "config" / "surface-texture.json"
    return path, read_json(path)


def surface_choices(root: Path) -> tuple[str, ...]:
    _, index = surface_index(root)
    return tuple(index["profiles"].keys())


def resolve_surface_profile(root: Path, requested: str | None = None) -> tuple[str, Path, dict]:
    index_path, index = surface_index(root)
    profile_id = requested or index["default_profile"]
    try:
        relative = index["profiles"][profile_id]
    except KeyError as exc:
        choices = ", ".join(index["profiles"])
        raise ValueError(f"unknown surface profile {profile_id!r}; choose one of: {choices}") from exc
    profile_path = (index_path.parent / relative).resolve()
    profile = read_json(profile_path)
    if profile.get("profile_id") != profile_id:
        raise ValueError(f"surface profile id mismatch in {profile_path}")
    return profile_id, profile_path, profile


def formatted_export(params: dict, key: str, profile_id: str) -> str:
    return str(params["export"][key]).format(surface=profile_id)
