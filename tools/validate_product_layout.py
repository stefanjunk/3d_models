#!/usr/bin/env python3
"""Fail-closed checks for the self-contained product folder contract."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "products"
PORTFOLIO = ROOT / "business/02-portfolio/product-portfolio.csv"
FAMILIES = {
    "art-decor",
    "furniture-systems",
    "home-kitchen-garden",
    "organization-storage",
    "printer-workshop",
    "toys-games",
    "wearables",
}
FAMILY_FORBIDDEN = {
    "assets",
    "build",
    "exports",
    "profiles",
    "releases",
    "scripts",
    "source",
    "tests",
    "validation",
    "vendor",
}
LEGACY_TOP_LEVEL = {
    "3d-printing_addons",
    "Fox",
    "Opel_Grandland_2018",
    "Plants",
    "Unicorn",
    "accessoires",
    "art",
    "barefoot",
    "blasters",
    "boats",
    "bowls",
    "camera_mount",
    "capybara",
    "claw_hammer",
    "clips",
    "cup",
    "deco",
    "dice_tower",
    "dough_cutter",
    "fidgets",
    "fish",
    "garden",
    "gravity_knife",
    "household",
    "market_research",
    "metrimade-watermark",
    "mouse",
    "mouse_jiggler",
    "music",
    "organizer",
    "puzzles",
    "racehorse",
    "shoes",
    "sportscar",
    "stamps",
    "systemmoebel_top20_cad",
    "walls",
    "whale",
}
SOURCE_DIR_NAMES = {"cad", "scripts", "source", "src"}
SOURCE_SUFFIXES = {".js", ".json", ".mjs", ".py", ".scad", ".yaml", ".yml"}
IGNORED_GENERATED_DIRS = {".venv311", "__pycache__", "node_modules"}
PRODUCT_PATH = re.compile(r"(?<![A-Za-z0-9_.-])products/([a-z0-9-]+)/([a-z0-9-]+)/")
OUTSIDE_DEPENDENCY = re.compile(r"(?:\.\./){2,}(?:libraries|tools)/")


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def source_files(product: Path):
    for child in product.iterdir():
        if child.is_dir() and child.name in SOURCE_DIR_NAMES:
            for path in child.rglob("*"):
                if (
                    not IGNORED_GENERATED_DIRS.intersection(path.parts)
                    and path.is_file()
                    and path.suffix.lower() in SOURCE_SUFFIXES
                ):
                    yield path
        elif child.is_file() and (
            child.suffix.lower() in SOURCE_SUFFIXES
            or child.name in {"design-spec.yaml", "validation-project.json"}
        ):
            yield child


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    actual_families = {
        path.name for path in PRODUCTS.iterdir() if path.is_dir()
    }
    if actual_families != FAMILIES:
        errors.append(
            f"family set mismatch: expected {sorted(FAMILIES)}, got {sorted(actual_families)}"
        )

    product_roots: set[Path] = set()
    for family_name in sorted(FAMILIES):
        family = PRODUCTS / family_name
        if not family.is_dir():
            continue
        for forbidden in sorted(FAMILY_FORBIDDEN):
            if (family / forbidden).exists():
                errors.append(f"family-level shared directory is forbidden: {family / forbidden}")
        for child in family.iterdir():
            if child.name == "README.md":
                continue
            if not child.is_dir():
                errors.append(f"unexpected family-level file: {child}")
                continue
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", child.name):
                errors.append(f"non-canonical product directory name: {child}")
            product_roots.add(child.resolve())

    with PORTFOLIO.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    seen_sources: set[str] = set()
    for row in rows:
        sku = row["Working_SKU"]
        source_text = row["Source_Path"]
        source = (ROOT / source_text).resolve()
        parts = Path(source_text).parts
        if len(parts) != 3 or parts[0] != "products" or parts[1] not in FAMILIES:
            errors.append(f"{sku}: source is not a product leaf: {source_text}")
        if source_text in seen_sources:
            errors.append(f"{sku}: duplicate product source: {source_text}")
        seen_sources.add(source_text)
        if source not in product_roots:
            errors.append(f"{sku}: source directory missing or unregistered in tree: {source_text}")

        evidence_text = row.get("Model_Evidence_Path", "")
        if evidence_text:
            evidence = (ROOT / evidence_text).resolve()
            if not evidence.is_file():
                errors.append(f"{sku}: evidence file missing: {evidence_text}")
            elif not is_relative_to(evidence, source):
                errors.append(f"{sku}: evidence escapes product folder: {evidence_text}")

    for product in sorted(product_roots):
        if any(
            path.is_symlink()
            for path in product.rglob("*")
            if not IGNORED_GENERATED_DIRS.intersection(path.parts)
        ):
            errors.append(f"symlinks are not allowed inside a self-contained product: {product}")
        own_relative = product.relative_to(ROOT)
        own_key = (own_relative.parts[1], own_relative.parts[2])
        for path in source_files(product):
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                warnings.append(f"non-UTF-8 source skipped: {path.relative_to(ROOT)}")
                continue
            for match in PRODUCT_PATH.finditer(content):
                target_key = (match.group(1), match.group(2))
                if target_key != own_key:
                    errors.append(
                        f"cross-product source dependency in {path.relative_to(ROOT)}: "
                        f"products/{target_key[0]}/{target_key[1]}/"
                    )
            if OUTSIDE_DEPENDENCY.search(content):
                errors.append(
                    f"repository-level dependency in {path.relative_to(ROOT)}; vendor it locally"
                )

    for legacy in sorted(LEGACY_TOP_LEVEL):
        if (ROOT / legacy).exists():
            errors.append(f"legacy top-level product grouping still exists: {legacy}")

    registered = len(rows)
    unregistered = sum(path.name.startswith("unregistered-") for path in product_roots)
    print(
        f"families={len(actual_families)} products={len(product_roots)} "
        f"registered={registered} unregistered={unregistered} "
        f"warnings={len(warnings)} errors={len(errors)}"
    )
    for warning in warnings:
        print(f"WARNING {warning}")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
