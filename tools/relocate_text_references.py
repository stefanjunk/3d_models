#!/usr/bin/env python3
"""Rewrite repository-relative and absolute paths after product relocation."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Physical moves, ordered from the most specific legacy path to the least.
MOVES = {
    "organizer/bathroom/ZEN_KINTSUGI_WAVE_FIFO_5R_v2.1.0_DRAFT_REVIEW_LITE": "products/organization-storage/mm-bth-002-toilet-paper-fifo-system/history/zen-kintsugi-v2.1.0-draft-review-lite",
    "organizer/bathroom/premium-parametric-over-toilet-shelf": "products/organization-storage/mm-bth-001-premium-over-toilet-shelf",
    "organizer/bathroom/toilettpaper_stand": "products/organization-storage/mm-bth-002-toilet-paper-fifo-system",
    "organizer/desk-drawer": "products/organization-storage/mm-org-003-modern-carbon-desk-organizer",
    "organizer/drawer-inlay": "products/organization-storage/mm-org-001-drawerfit-modular",
    "organizer/nameform-bookends": "products/organization-storage/mm-per-001-nameform-bookends",
    "organizer/shelffit-mini-bins": "products/organization-storage/mm-org-002-shelffit-mini-bins",
    "organizer/nozzle-box": "products/printer-workshop/mm-mkr-001-cybervault-nozzle-case",
    "organizer/external": "research/third-party/organization-storage",
    "3d-printing_addons/Kobra3Max_Gehaeuse_CAD_v1": "products/printer-workshop/mm-tool-001-kobra3max-enclosure",
    "3d-printing_addons/filament_box": "products/printer-workshop/mm-tool-002-filament-drybox-system",
    "3d-printing_addons/Anycubic-Kobra-3-Max-Poop-Bin-metriMade-R1": "products/printer-workshop/unregistered-kobra3max-poop-bin",
    "3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R5": "products/printer-workshop/unregistered-kobra3max-purge-catcher/current",
    "3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R4": "products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r4",
    "3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R3": "products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r3",
    "3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R2": "products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r2",
    "3d-printing_addons/Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1 (1)": "products/printer-workshop/unregistered-kobra3max-fan-cage/history/import-copy-1",
    "3d-printing_addons/Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1": "products/printer-workshop/unregistered-kobra3max-fan-cage/current",
    "3d-printing_addons/external": "research/third-party/printer-workshop",
    "camera_mount": "products/printer-workshop/mm-tool-003-kobra3max-camera-arm",
    "claw_hammer": "products/printer-workshop/mm-tool-004-claw-hammer-mesh",
    "mouse_jiggler": "products/printer-workshop/unregistered-magnetic-mouse-jiggler",
    "accessoires/honeycomb-hair-clip-r6-final(1)": "products/wearables/mm-acc-001-honeycomb-hair-clip",
    "barefoot": "products/wearables/mm-sho-001-barefoot-shoe-collection",
    "blasters": "products/toys-games/mm-toy-001-rubber-ball-toy-popper",
    "boats/fisher_boat_detailed": "products/toys-games/mm-boat-002-fisher-boat-detailed",
    "boats/flapping_submarine": "products/toys-games/mm-boat-003-flapping-tail-submarine",
    "boats/fisher_boat": "products/toys-games/mm-boat-001-fisher-boat",
    "boats/rocket_boat": "products/toys-games/mm-boat-004-rocket-boat",
    "boats/toy_boat": "products/toys-games/mm-boat-005-toy-boat",
    "boats/duck_boat": "products/toys-games/unregistered-duck-boat",
    "boats/external": "research/third-party/boats",
    "dice_tower": "products/toys-games/mm-hob-001-polygonal-dice-tower",
    "puzzles/parametric_labyrinth_gift_box": "products/toys-games/mm-puz-001-parametric-labyrinth-gift-box",
    "puzzles/puzzle-box": "products/toys-games/mm-puz-002-mystery-puzzle-box",
    "puzzles/external": "research/third-party/puzzles",
    "bowls": "products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray",
    "cup": "products/home-kitchen-garden/mm-home-001-cup-and-measuring-spoon",
    "garden": "products/home-kitchen-garden/mm-gar-001-rainwater-filter-well",
    "household": "products/home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap",
    "deco/duftspender": "products/home-kitchen-garden/unregistered-aroma-diffuser",
    "Fox": "products/art-decor/mm-art-001-fox-mesh-collection",
    "Opel_Grandland_2018": "products/art-decor/mm-auto-001-opel-grandland-2018-mesh",
    "Plants": "products/art-decor/mm-art-002-plant-mesh",
    "Unicorn": "products/art-decor/mm-art-003-unicorn-mesh-collection",
    "art/marble_tile": "products/art-decor/mm-dec-001-marble-tile",
    "art/roman_pillar": "products/art-decor/mm-dec-002-roman-pillar",
    "art/external_models": "research/third-party/art-models",
    "capybara": "products/art-decor/mm-art-004-capybara-mesh-collection",
    "fish": "products/art-decor/mm-art-005-fish-mesh-collection",
    "mouse": "products/art-decor/mm-art-006-mouse-mesh-collection",
    "racehorse": "products/art-decor/mm-art-007-racehorse-mesh-collection",
    "sportscar": "products/art-decor/mm-art-008-sports-car-mesh",
    "walls": "products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf",
    "whale": "products/art-decor/mm-art-009-whale-mesh-collection",
    "market_research": "research/market",
    "clips": "research/third-party/clips",
    "dough_cutter": "research/third-party/dough-cutters",
    "fidgets": "research/third-party/fidgets",
    "gravity_knife": "research/third-party/gravity-knife-fidgets",
    "music": "research/third-party/music-boxes",
    "shoes": "research/third-party/shoes",
    "stamps": "research/third-party/stamps",
    "systemmoebel_top20_cad/products/alex-inventory-workplace-tray-v0.2.0": "products/furniture-systems/mm-sys-001-alex-inventory-workplace-tray",
    "systemmoebel_top20_cad/products/bror-tool-shadow-tray-v0.2.0": "products/furniture-systems/mm-sys-002-bror-tool-shadow-tray",
}

TEXT_SUFFIXES = {
    ".csv",
    ".gitattributes",
    ".gitignore",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".scad",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SCAN_ROOTS = (ROOT / "business", ROOT / "products", ROOT / "research")
EXCLUDED_PARTS = {".git", ".venv311", "node_modules", "__pycache__"}


def candidate_files():
    for scan_root in SCAN_ROOTS:
        for path in scan_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if EXCLUDED_PARTS.intersection(path.parts):
                continue
            yield path
    yield ROOT / ".gitattributes"
    yield ROOT / ".gitignore"


def rewrite(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original
    for index, (old, new) in enumerate(
        sorted(MOVES.items(), key=lambda pair: len(pair[0]), reverse=True)
    ):
        old_prefix = old.rstrip("/") + "/"
        new_prefix = new.rstrip("/") + "/"
        placeholder = f"\x00PRODUCT_MOVE_{index}\x00"
        updated = updated.replace(new_prefix, placeholder)
        pattern = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(old_prefix))
        updated = pattern.sub(lambda _: new_prefix, updated)
        updated = updated.replace(placeholder, new_prefix)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def rewrite_system_product_absolute_paths() -> int:
    legacy_absolute = str(ROOT / "systemmoebel_top20_cad") + "/"
    changed = 0
    family = ROOT / "products/furniture-systems"
    for product in family.iterdir():
        if not product.is_dir() or product.name[:10] in {"mm-sys-001", "mm-sys-002"}:
            continue
        replacement = str(product) + "/"
        for path in product.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if EXCLUDED_PARTS.intersection(path.parts):
                continue
            original = path.read_text(encoding="utf-8")
            updated = original.replace(legacy_absolute, replacement)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    return changed


def main() -> int:
    changed = sum(rewrite(path) for path in candidate_files())
    system_changed = rewrite_system_product_absolute_paths()
    print(f"rewrote {changed} text files and {system_changed} system-product evidence files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
