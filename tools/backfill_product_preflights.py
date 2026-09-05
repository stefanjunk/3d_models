#!/usr/bin/env python3
"""Backfill auditable preflight and purpose documents for every product.

The script is intentionally conservative: it derives only from repository
evidence, records absent facts as unknown, and never releases a product when a
hard gate fails.  It also verifies the explicit archive moves made during the
2026-08-31 repository cleanup and writes a portfolio-level audit.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_ROOT = REPO_ROOT / "products"
ASSESSMENT_DATE = "2026-08-31"
ASSESSMENT_VERSION = "0.1.0"
UNKNOWN_REVISION = "UNVERSIONED-CURRENT"

sys.path.insert(0, str(REPO_ROOT / ".agents/skills/3d-design-preflight/scripts"))
from validate_preflight import validate_document  # noqa: E402

PRUNED_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    ".venv311",
    "__pycache__",
    "archive",
    "build",
    "external",
    "node_modules",
    "preflight",
    "vendor",
}

TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}
GEOMETRY_SUFFIXES = {".3mf", ".blend", ".fcstd", ".glb", ".obj", ".scad", ".step", ".stl"}

WEIGHTS = {
    "REQ": 7,
    "CTX": 5,
    "PAR": 10,
    "INT": 20,
    "CPL": 10,
    "MOT": 10,
    "GEO": 7,
    "PHY": 10,
    "MAT": 7,
    "EXT": 7,
    "VER": 7,
}

PURPOSE_OVERRIDES = {
    "art-decor/mm-art-001-fox-mesh-collection":
        "Provide printable fox-themed decorative meshes and their reference assets for non-functional display use.",
    "art-decor/mm-art-002-plant-mesh":
        "Provide a printable decorative plant mesh for non-functional display use.",
    "art-decor/mm-art-003-unicorn-mesh-collection":
        "Provide printable unicorn-themed decorative meshes for non-functional display use.",
    "art-decor/mm-art-004-capybara-mesh-collection":
        "Provide printable capybara-themed decorative meshes for non-functional display use.",
    "art-decor/mm-art-005-fish-mesh-collection":
        "Provide printable fish-themed decorative meshes for non-functional display use.",
    "art-decor/mm-art-006-mouse-mesh-collection":
        "Provide printable mouse-themed decorative meshes for non-functional display use.",
    "art-decor/mm-art-007-racehorse-mesh-collection":
        "Provide a printable racehorse display model and related trophy-concept evidence for decorative use.",
    "art-decor/mm-art-008-sports-car-mesh":
        "Provide a printable sports-car-shaped decorative mesh for non-functional display use.",
    "art-decor/mm-art-009-whale-mesh-collection":
        "Provide printable whale-themed decorative meshes for non-functional display use.",
    "art-decor/mm-auto-001-opel-grandland-2018-mesh":
        "Provide a printable decorative representation of a 2018 Opel Grandland X; it is not a vehicle component or fit reference.",
    "art-decor/mm-dec-001-marble-tile":
        "Develop a decorative marble-style tile or master together with printable negative-mold test geometry for casting experiments.",
    "art-decor/mm-dec-002-roman-pillar":
        "Provide a decorative Roman-column model and a printable two-part negative mold for casting trials.",
    "home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap":
        "Develop a removable segmented insert that retains hair in a linear shower drain while preserving drainage and cleanability.",
    "home-kitchen-garden/mm-dec-003-sunflower-bowl-tray":
        "Provide a sunflower-inspired printable bowl or tray for decorative storage of dry, non-food items.",
    "home-kitchen-garden/mm-gar-001-rainwater-filter-well":
        "Develop a printable rainwater filter-well assembly that separates debris while maintaining a serviceable water path.",
    "home-kitchen-garden/mm-home-001-cup-and-measuring-spoon":
        "Provide a lidded cup and small measuring spoon for storing and portioning a dry supplement; volume and mass claims require calibration.",
    "home-kitchen-garden/unregistered-aroma-diffuser":
        "Document and develop a printable aroma-diffuser concept; the fragrance medium, heat source, and safe operating method are not yet defined.",
    "home-kitchen-garden/unregistered-shower-drain-hairtrap":
        "Develop or collect a printable shower-drain hair trap; the target drain variant and functional requirements are not yet documented.",
    "organization-storage/mm-org-001-drawerfit-modular":
        "Provide a modular fitted drawer-organizer system with rebuildable compartment and surface variants, pending physical drawer and connector fit validation.",
    "organization-storage/mm-org-003-modern-carbon-desk-organizer":
        "Provide a compact compartmented desk organizer with a carbon-inspired visual surface treatment for dry indoor stationery storage.",
    "organization-storage/mm-wall-001-honeycomb-wood-wall-shelf":
        "Develop a modular honeycomb wall shelf and display system with wood-inspired surfaces and printable mounting interfaces.",
    "printer-workshop/mm-mkr-001-cybervault-nozzle-case":
        "Store, identify, and protect interchangeable 3D-printer nozzles in a printable CyberVault case with fit-coupon verification.",
    "printer-workshop/mm-tool-001-kobra3max-enclosure":
        "Provide a modular enclosure and accessory-mount system for an Anycubic Kobra 3 Max workspace; thermal and machine-clearance performance remain test-gated.",
    "printer-workshop/mm-tool-002-filament-drybox-system":
        "Support dry filament storage and routing with printable holders, feedthroughs, desiccant containers, and an inline feeding mechanism.",
    "printer-workshop/mm-tool-003-kobra3max-camera-arm":
        "Mount and position an Anycubic printer camera on a slim articulated arm attached to a Kobra 3 Max.",
    "printer-workshop/mm-tool-004-claw-hammer-mesh":
        "Provide a claw-hammer-shaped printable reference or display mesh; it is not validated for striking or load-bearing tool use.",
    "printer-workshop/unregistered-kobra3max-fan-cage":
        "Develop a printable protective fan cage or printhead cover for a Kobra 3 Max while preserving airflow, motion clearances, and service access.",
    "printer-workshop/unregistered-kobra3max-poop-bin":
        "Collect purge waste from an Anycubic Kobra 3 Max in a printable bin and mounting-bracket system.",
    "printer-workshop/unregistered-magnetic-mouse-jiggler":
        "Develop a magnetic flexure-based mouse-jiggler mechanism; its drive method, host compatibility, and endurance targets remain unconfirmed.",
    "toys-games/mm-boat-001-fisher-boat":
        "Provide a printable fisherman-boat display or supervised toy mesh without a validated propulsion or flotation claim.",
    "toys-games/mm-boat-002-fisher-boat-detailed":
        "Provide a detailed printable fisherman-boat display or supervised toy mesh without a validated propulsion or flotation claim.",
    "toys-games/mm-boat-004-rocket-boat":
        "Provide a rocket-boat-shaped printable display or supervised toy concept; propulsion, flotation, and safety are not yet defined.",
    "toys-games/mm-boat-005-toy-boat":
        "Provide a printable toy-boat mesh for supervised play or display; flotation and durability are not yet validated.",
    "toys-games/mm-hob-001-polygonal-dice-tower":
        "Guide tabletop dice through a printable polygonal tower and deliver randomized rolls into a controlled collection area.",
    "toys-games/mm-toy-001-rubber-ball-toy-popper":
        "Develop a supervised play mechanism that launches or pops a soft rubber ball; projectile energy and user safety remain unvalidated.",
    "toys-games/unregistered-duck-boat":
        "Develop a duck-shaped printable boat concept for supervised play or display; flotation and propulsion are not yet defined.",
    "wearables/mm-sho-001-barefoot-shoe-collection":
        "Develop a parametric barefoot-shoe system with flexible sole, upper, and foot-fit interfaces for walking prototypes, not production footwear release.",
}


ARCHIVE_MOVES: dict[str, list[str]] = {
    "home-kitchen-garden/mm-gar-001-rainwater-filter-well": [
        "regenwasser-filterbrunnen_R2_DRAFT",
        "regenwasser-filterbrunnen_R2_DRAFT.zip",
    ],
    "organization-storage/mm-bth-002-toilet-paper-fifo-system": ["history"],
    "organization-storage/mm-org-001-drawerfit-modular": [
        "DRAFT-schubladen-organizer-R1.zip",
        "DRAFT-schubladen-organizer-R1.1-continuous16.zip",
        "DRAFT-schubladen-organizer-R1.2-rebuildable-030mm.zip",
        "DRAFT-schubladen-organizer-R1.3-aspect-safe-030mm",
        "DRAFT-schubladen-organizer-R1.3-aspect-safe-030mm.zip",
        "DRAFT-schubladen-organizer-R1.4-procedural-steel",
        "DRAFT-schubladen-organizer-R1.4-procedural-steel.zip",
        "DRAFT-schubladen-organizer-R1.5-procedural-walnut",
        "DRAFT-schubladen-organizer-R1.5-procedural-walnut.zip",
    ],
    "organization-storage/mm-org-002-shelffit-mini-bins": ["history"],
    "organization-storage/mm-org-003-modern-carbon-desk-organizer": [
        "modern-carbon-desk-organizer-v1.1.2",
        "modern-carbon-desk-organizer-v1.1.2.zip",
    ],
    "printer-workshop/mm-tool-001-kobra3max-enclosure": ["legacy-package-v1.zip"],
    "printer-workshop/mm-tool-002-filament-drybox-system": [
        "slim_inline_filament_feeder_v2_normally_open",
        "slim_inline_filament_feeder_v2_normally_open.zip",
        "slim_inline_filament_feeder_v3_modular_8x",
        "slim_inline_filament_feeder_v3_modular_8x.zip",
    ],
    "printer-workshop/unregistered-kobra3max-fan-cage": ["history"],
    "printer-workshop/unregistered-kobra3max-poop-bin": ["legacy-package-r1.zip"],
    "toys-games/mm-drn-001-openquad-cf5-fpv-quadcopter": ["legacy-package"],
    "toys-games/mm-puz-002-mystery-puzzle-box": ["history"],
    "toys-games/mm-rov-001-tethys-mini-rov": ["legacy-package"],
    "wearables/mm-acc-001-honeycomb-hair-clip": ["legacy-package-r6.zip"],
    "wearables/mm-sho-001-barefoot-shoe-collection": [
        "barfussschuh_v4_integriert",
        "barfussschuh_v4_integriert.zip",
        "barfussschuh_v4_1_optimiert",
        "barfussschuh_v4_1_optimiert.zip",
        "parametrisch/Parametrischer_Barfussschuh_v0.1.0",
        "parametrisch/Parametrischer_Barfussschuh_v0.1.0.zip",
    ],
    "home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap": [
        "abflusssieb/shower_drain_hairtrap_945x65_funnel_v1",
        "abflusssieb/shower_drain_hairtrap_945x65_funnel_v1.zip",
        "abflusssieb/shower_drain_hairtrap_945x65_funnel_flush_v1_1",
        "abflusssieb/shower_drain_hairtrap_945x65_funnel_flush_v1_1.zip",
        "abflusssieb/shower_drain_hairtrap_945x65_funnel_open_v1_2",
        "abflusssieb/shower_drain_hairtrap_945x65_funnel_open_v1_2.zip",
        "abflusssieb/shower_drain_hairtrap_945x65_uprofile_v1",
        "abflusssieb/shower_drain_hairtrap_945x65_uprofile_v1.zip",
        "abflusssieb/shower_drain_hairtrap_v2_snap_945x65x20",
        "abflusssieb/shower_drain_hairtrap_v2_snap_945x65x20.zip",
    ],
}


CURRENT_SELECTIONS = {
    "home-kitchen-garden/mm-gar-001-rainwater-filter-well": ["regenwasser-filterbrunnen_R3_DRAFT"],
    "organization-storage/mm-org-001-drawerfit-modular": [
        "DRAFT-schubladen-organizer-R1.6-parametric-surfaces",
        "MM-ORG-001-metod-maximera-60 (separate active host-specific line)",
    ],
    "organization-storage/mm-org-003-modern-carbon-desk-organizer": ["modern-carbon-desk-organizer-compact-v2.0.0"],
    "printer-workshop/mm-tool-002-filament-drybox-system": [
        "slim_inline_filament_feeder_v4_retained_female",
        "other differently sized component lines remain current independently",
    ],
    "home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap": [
        "abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21",
    ],
    "wearables/mm-sho-001-barefoot-shoe-collection": [
        "barfussschuh_v6_2_freeform",
        "barfussschuh_v6_source (shared active source line)",
    ],
    "printer-workshop/unregistered-kobra3max-fan-cage": [
        "current",
        "redesign-v2 (active redesign line)",
    ],
}


ROOT_REVIEW_EXCEPTIONS = {
    "home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap":
        "The older v1_3 tree remains outside archive because all_panels.3mf had a pre-existing local modification; moving it would mix unrelated user content into this commit.",
    "printer-workshop/unregistered-kobra3max-fan-cage":
        "The root contains an untracked R1 import plus current and redesign-v2 work. Their ownership/currentness is ambiguous, so no active or untracked content was moved.",
    "wearables/mm-sho-001-barefoot-shoe-collection":
        "The root contains a pre-existing untracked 90 MiB duplicate named barfussschuh_v6_1_fitfix (2); the v6.1 pair was left in place to avoid absorbing user-owned binary content.",
}


@dataclass
class ProductContext:
    root: Path
    key: str
    family: str
    slug: str
    project_id: str
    product_name: str
    revision: str
    purpose: str
    purpose_source: str
    evidence_files: list[Path]
    basis_refs: list[str]
    selected_spec: Path | None
    selected_spec_data: dict[str, Any]
    evidence_text: str
    generated_at: str


def product_dirs() -> list[Path]:
    return sorted(
        product
        for family in PRODUCTS_ROOT.iterdir()
        if family.is_dir()
        for product in family.iterdir()
        if product.is_dir()
        and product.name.startswith(("mm-", "unregistered-"))
    )


def iter_product_files(product: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(product):
        dirnames[:] = sorted(d for d in dirnames if d not in PRUNED_DIRS and not d.startswith(".venv"))
        base = Path(dirpath)
        for filename in sorted(filenames):
            path = base / filename
            if path.name in {"PURPOSE.md", "preflight-result.json", "preflight-report.md", "preflight-input.yaml"}:
                continue
            yield path


def safe_read(path: Path, limit: int = 2_000_000) -> str:
    try:
        if path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def safe_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def is_generated_inventory_spec(path: Path) -> bool:
    if path.name != "design-spec.yaml" or path.parent.parent.name == "products":
        return False
    data = safe_yaml(path)
    return (
        nested_get(data, "product", "status") == "retrospective-inventory"
        and nested_get(data, "source_of_truth", "status") == "retrospective-index"
    )


def relative(path: Path, product: Path) -> str:
    return path.relative_to(product).as_posix()


def version_tuple(text: str) -> tuple[int, ...]:
    matches = re.findall(r"(?i)(?:^|[^a-z0-9])(?:v|r|release[-_]?)(\d+(?:[._-]\d+)*)", text)
    if not matches:
        return ()
    versions = [tuple(int(p) for p in re.split(r"[._-]", item)) for item in matches]
    return max(versions)


def spec_rank(path: Path, product: Path) -> tuple[int, tuple[int, ...], int]:
    rel = relative(path, product).lower()
    score = 1000 if path.parent == product else 100
    if any(token in rel for token in ("/current/", "redesign-v2", "v6_2", "v3_", "release")):
        score += 200
    if any(token in rel for token in ("legacy", "old", "backup")):
        score -= 500
    return score, version_tuple(rel), -len(path.parts)


def choose_spec(product: Path, files: list[Path]) -> tuple[Path | None, dict[str, Any]]:
    candidates = [p for p in files if p.name == "design-spec.yaml"]
    if not candidates:
        return None, {}
    path = max(candidates, key=lambda p: spec_rank(p, product))
    return path, safe_yaml(path)


def nested_get(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def clean_prose(value: str, max_length: int = 700) -> str:
    value = " ".join(value.split()).strip()
    if len(value) <= max_length:
        return value
    shortened = value[:max_length]
    stop = max(shortened.rfind(". "), shortened.rfind("; "))
    return shortened[: stop + 1] if stop > 100 else shortened.rstrip() + "…"


def readme_purpose(product: Path, files: list[Path]) -> tuple[str | None, str | None]:
    readmes = [p for p in files if p.name.lower().startswith("readme") and p.suffix.lower() in {".md", ".txt"}]
    if not readmes:
        return None, None
    readmes.sort(key=lambda p: (0 if p.parent == product else 1, -spec_rank(p, product)[0], len(p.parts)))
    for readme in readmes:
        text = safe_read(readme)
        for paragraph in re.split(r"\n\s*\n", text):
            lines = [
                line.strip()
                for line in paragraph.splitlines()
                if line.strip()
                and not line.lstrip().startswith(("#", "[", "!", "|", "```", "- ", ">"))
            ]
            prose = clean_prose(" ".join(lines))
            if len(prose) >= 25:
                return prose, relative(readme, product)
    return None, None


def purpose_from_spec(key: str, spec: dict[str, Any]) -> str | None:
    for path in (
        ("function", "summary"),
        ("requirements", "function"),
        ("product", "purpose"),
        ("purpose",),
    ):
        value: Any = spec
        for item in path:
            value = value.get(item) if isinstance(value, dict) else None
        if isinstance(value, str) and value.strip():
            return clean_prose(value)

    match = re.search(r"mm-sys-(\d+)", key)
    models = spec.get("models")
    if match and isinstance(models, list):
        model_id = int(match.group(1))
        for model in models:
            if isinstance(model, dict) and model.get("id") == model_id and isinstance(model.get("function"), str):
                return clean_prose(
                    f"Provide a parametric one-piece FDM concept for a {model['function']}; "
                    "the host-furniture interface remains provisional until measured and physically tested."
                )
    return None


def project_identity(product: Path, spec: dict[str, Any]) -> tuple[str, str, str]:
    slug = product.name
    match = re.match(r"(mm-[a-z]+-\d+)(?:-|$)", slug, re.IGNORECASE)
    project_id = match.group(1).upper() if match else slug.upper().replace("_", "-")
    product_name = slug
    revision: Any = None

    project = spec.get("project")
    if isinstance(project, dict):
        project_id = str(project.get("id") or project_id)
        revision = project.get("revision") or project.get("version")
        product_name = str(project.get("name") or product_name)
    elif isinstance(project, str) and project.strip():
        project_id = project.strip()

    product_data = spec.get("product")
    if isinstance(product_data, dict):
        project_id = str(product_data.get("id") or project_id)
        product_name = str(product_data.get("name") or product_name)
        revision = revision or product_data.get("version") or product_data.get("revision")

    revision = revision or spec.get("revision") or spec.get("version") or UNKNOWN_REVISION
    product_name = product_name.replace("-", " ").replace("_", " ").strip().title()
    return project_id, str(revision), product_name


def evidence_rank(path: Path, product: Path) -> tuple[int, int, str]:
    rel = relative(path, product).lower()
    name = path.name.lower()
    score = 0
    if path.parent == product:
        score += 40
    if name == "design-spec.yaml":
        score += 100
    elif name.startswith("readme"):
        score += 90
    elif "validation-project" in name:
        score += 80
    elif "test" in name or "validation" in rel:
        score += 65
    elif "print" in name or "profile" in rel:
        score += 55
    elif path.suffix.lower() in GEOMETRY_SUFFIXES:
        score += 45
    elif path.suffix.lower() in TEXT_SUFFIXES:
        score += 35
    score += min(20, len(version_tuple(rel)) * 5)
    return score, -len(path.parts), rel


def basis_refs(product: Path, files: list[Path], selected_spec: Path | None) -> list[str]:
    refs: list[str] = []
    if selected_spec is not None:
        refs.append(relative(selected_spec, product))
    for path in sorted(files, key=lambda p: evidence_rank(p, product), reverse=True):
        if path.suffix.lower() not in TEXT_SUFFIXES | GEOMETRY_SUFFIXES:
            continue
        rel = relative(path, product)
        if rel not in refs:
            refs.append(rel)
        if len(refs) >= 8:
            break
    return refs or ["."]


def build_context(product: Path, generated_at: str) -> ProductContext:
    key = product.relative_to(PRODUCTS_ROOT).as_posix()
    files = [path for path in iter_product_files(product) if not is_generated_inventory_spec(path)]
    selected_spec, spec = choose_spec(product, files)
    project_id, revision, product_name = project_identity(product, spec)

    if key in PURPOSE_OVERRIDES:
        purpose = PURPOSE_OVERRIDES[key]
        purpose_source = "retrospective repository evidence and product identity"
    else:
        purpose = purpose_from_spec(key, spec)
        purpose_source = relative(selected_spec, product) if purpose and selected_spec else ""
        if not purpose:
            purpose, readme_source = readme_purpose(product, files)
            purpose_source = readme_source or "product identity only"
        if not purpose:
            purpose = f"Maintain the printable product concept identified as {product.name}; intended function remains to be specified."
            purpose_source = "product identity only"

    refs = basis_refs(product, files, selected_spec)
    text_paths = [
        p for p in sorted(files, key=lambda p: evidence_rank(p, product), reverse=True)
        if p.suffix.lower() in TEXT_SUFFIXES
    ][:20]
    evidence_text = "\n".join(safe_read(p, 300_000) for p in text_paths).lower()
    return ProductContext(
        root=product,
        key=key,
        family=product.parent.name,
        slug=product.name,
        project_id=project_id,
        product_name=product_name,
        revision=revision,
        purpose=clean_prose(purpose),
        purpose_source=purpose_source,
        evidence_files=files,
        basis_refs=refs,
        selected_spec=selected_spec,
        selected_spec_data=spec,
        evidence_text=evidence_text,
        generated_at=generated_at,
    )


def family_base(family: str) -> dict[str, int]:
    bases = {
        "art-decor": dict(REQ=0, CTX=0, PAR=1, INT=0, CPL=0, MOT=0, GEO=2, PHY=0, MAT=1, EXT=0, VER=0),
        "furniture-systems": dict(REQ=2, CTX=2, PAR=1, INT=2, CPL=1, MOT=0, GEO=1, PHY=2, MAT=2, EXT=1, VER=2),
        "furniture-cabinetry": dict(REQ=2, CTX=2, PAR=3, INT=3, CPL=2, MOT=2, GEO=1, PHY=2, MAT=2, EXT=2, VER=2),
        "home-kitchen-garden": dict(REQ=1, CTX=1, PAR=1, INT=1, CPL=0, MOT=0, GEO=1, PHY=1, MAT=1, EXT=0, VER=1),
        "organization-storage": dict(REQ=2, CTX=2, PAR=2, INT=2, CPL=1, MOT=0, GEO=1, PHY=1, MAT=2, EXT=0, VER=2),
        "printer-workshop": dict(REQ=2, CTX=2, PAR=2, INT=3, CPL=2, MOT=1, GEO=2, PHY=2, MAT=2, EXT=2, VER=3),
        "toys-games": dict(REQ=1, CTX=2, PAR=2, INT=2, CPL=1, MOT=2, GEO=2, PHY=2, MAT=2, EXT=1, VER=2),
        "wearables": dict(REQ=3, CTX=4, PAR=3, INT=4, CPL=3, MOT=3, GEO=4, PHY=3, MAT=4, EXT=1, VER=4),
    }
    return dict(bases[family])


def keyword_any(text: str, words: Iterable[str]) -> bool:
    return any(word in text for word in words)


def complexity_scores(ctx: ProductContext) -> dict[str, int]:
    scores = family_base(ctx.family)
    # Use the product identity and purpose for semantic classification.  Full
    # evidence text can include generic portfolio reports or sibling concepts
    # and would otherwise inflate unrelated product scores.
    text = f"{ctx.key} {ctx.purpose}".lower()
    file_stems = {p.stem.lower() for p in ctx.evidence_files if p.suffix.lower() in {".stl", ".step", ".3mf"}}
    geometry_count = len(file_stems)

    if keyword_any(text, ("mold", "negative", "casting", "guss", "plaster")):
        scores.update(REQ=max(scores["REQ"], 2), INT=max(scores["INT"], 2), GEO=max(scores["GEO"], 3), PHY=max(scores["PHY"], 2), MAT=max(scores["MAT"], 3), VER=max(scores["VER"], 2))
    if keyword_any(text, ("drain", "filter", "flow", "fluid", "water", "airflow", "filament", "humidity", "diffuser")):
        scores["PHY"] = max(scores["PHY"], 3)
        scores["INT"] = max(scores["INT"], 3)
        scores["VER"] = max(scores["VER"], 3)
    if keyword_any(text, ("hinge", "rotary", "flexure", "feeder", "moving", "motion", "rover", "quadcopter", "submarine", "snap", "latch")):
        scores["MOT"] = max(scores["MOT"], 3)
        scores["CPL"] = max(scores["CPL"], 2)
    if keyword_any(text, ("motor", "sensor", "camera", "firmware", "electronic", "quadcopter", "rover", "rov")):
        scores["EXT"] = max(scores["EXT"], 3)
    if keyword_any(text, ("human", "user", "thumb", "hair", "shoe", "foot", "wearable")):
        scores["CTX"] = max(scores["CTX"], 3)
        scores["INT"] = max(scores["INT"], 3)
    if keyword_any(text, ("shoe", "foot-fit", "anatom", "barefoot")):
        scores["CTX"] = 4
        scores["INT"] = 4
        scores["GEO"] = 4
        scores["MAT"] = 4
    if keyword_any(text, ("freeform", "organic", "mesh", "sculpt", "relief")):
        scores["GEO"] = max(scores["GEO"], 2 if ctx.family == "art-decor" else 3)
    if keyword_any(text, ("wall", "shelf", "rail", "load", "cantilever", "mount")):
        scores["PHY"] = max(scores["PHY"], 2)
        scores["INT"] = max(scores["INT"], 2)
        scores["VER"] = max(scores["VER"], 2)
    if geometry_count > 30:
        scores["PAR"] = max(scores["PAR"], 4)
    elif geometry_count > 10:
        scores["PAR"] = max(scores["PAR"], 3)
    elif geometry_count > 2:
        scores["PAR"] = max(scores["PAR"], 2)
    if ctx.selected_spec and keyword_any(ctx.evidence_text, ("acceptance_criteria", "release_gates", "acceptance criteria")):
        scores["REQ"] = max(scores["REQ"], 2)
    return {key: max(0, min(4, int(value))) for key, value in scores.items()}


def complexity_result(scores: dict[str, int]) -> tuple[float, str]:
    total = round(sum(WEIGHTS[key] * scores[key] / 4 for key in WEIGHTS), 1)
    if total < 15:
        return total, "C0"
    if total < 25:
        return total, "C1"
    if total < 40:
        return total, "C2"
    if total < 60:
        return total, "C3"
    if total < 80:
        return total, "C4"
    return total, "C5"


def score_rationales(ctx: ProductContext, scores: dict[str, int]) -> dict[str, str]:
    has_spec = ctx.selected_spec is not None
    geometry_count = len({p.stem.lower() for p in ctx.evidence_files if p.suffix.lower() in GEOMETRY_SUFFIXES})
    rationales = {
        "REQ": "A design specification or requirement record exists, but release criteria may still be incomplete." if has_spec else "Only product-level intent and artifact names are available; quantified requirements are incomplete.",
        "CTX": "The use context includes a host, environment, or user variant that must be confirmed." if scores["CTX"] >= 2 else "The documented use is a narrow decorative or static context.",
        "PAR": f"The current evidence exposes approximately {geometry_count} distinct geometry-file stems; exports may duplicate physical parts.",
        "INT": "At least one functional host, human, medium, or assembly boundary governs success." if scores["INT"] else "No fit-critical functional interface is evidenced beyond display/support.",
        "CPL": "Changes can propagate across multiple parts, datums, or functional subsystems." if scores["CPL"] >= 2 else "The available architecture appears locally coupled or monolithic.",
        "MOT": "The purpose or evidence includes repeated motion, flexure, or a guided mechanism." if scores["MOT"] >= 2 else "The primary product state is static apart from assembly handling.",
        "GEO": "Freeform, organic, hidden, thin, or reconstructed geometry is present or implied." if scores["GEO"] >= 3 else "Geometry appears conventional or non-fit-critical, although exact dimensions were not re-derived.",
        "PHY": "Load, heat, airflow, water, fatigue, or another functional physical domain must be tested." if scores["PHY"] >= 2 else "Only low static or cosmetic loading is evident.",
        "MAT": "Material behavior, anisotropy, flexibility, surface process, or post-processing affects function." if scores["MAT"] >= 2 else "A conventional single-material FDM route is sufficient at the documented level.",
        "EXT": "Purchased hardware, printer equipment, electronics, or software participates in the system." if scores["EXT"] >= 2 else "Little or no external-component integration is evidenced.",
        "VER": "Several fit, function, flow, load, motion, or process checks are required." if scores["VER"] >= 2 else "Inspection and a basic print/stability check cover the evidenced scope.",
    }
    return rationales


def criticality(ctx: ProductContext) -> tuple[str, str, list[str]]:
    key = ctx.key.lower()
    k3_tokens = (
        "mm-bth-001-", "mm-wall-001-", "mm-sho-001-", "mm-drn-001-", "mm-rov-001-",
        "mm-toy-001-", "mm-toy-002-", "mm-toy-003-", "mm-boat-003-",
        "mm-tool-001-", "mm-tool-003-", "fan-cage",
    )
    k2_tokens = (
        "drain", "filter", "diffuser", "drybox", "purge-catcher", "poop-bin", "hair-clip",
        "mm-boat-", "wall-panel", "toilet-paper", "shelf", "rail", "riser", "mold", "pillar",
    )
    decorative = ctx.family == "art-decor" and not keyword_any(key, ("wall-panel", "marble-tile", "roman-pillar"))
    if decorative or "claw-hammer-mesh" in key:
        return "K0", "The documented scope is decorative/display-only; failure primarily wastes a print or degrades appearance.", ["cosmetic dissatisfaction", "wasted print"]
    if keyword_any(key, k3_tokens):
        return "K3", "A human-load, powered vehicle, machine-adjacent, projectile, or wall-mounted interface can plausibly cause injury or significant property damage.", ["injury", "damage to host equipment", "loss of controlled function"]
    if keyword_any(key, k2_tokens):
        return "K2", "The product involves load, flow, motion, heat-adjacent use, or direct body contact and therefore requires controlled functional testing.", ["functional failure", "leakage, obstruction, or detachment", "minor injury or property damage"]
    return "K1", "Failure is expected to cause inconvenience, fit loss, or limited property impact without credible high energy in the documented scope.", ["loss of intended function", "minor item or surface damage"]


def manufacturing_facts(ctx: ProductContext) -> tuple[dict[str, Any], dict[str, bool]]:
    text = ctx.evidence_text
    facts: dict[str, Any] = {
        "printer": None,
        "process": "FDM/FFF",
        "nozzle_mm": None,
        "material": None,
        "orientation_known": False,
    }
    nozzle = re.search(r"(?:nozzle(?:_mm)?|düse)\s*[:=]?\s*[\"']?([0-9]+(?:[.,][0-9]+)?)", text)
    if nozzle:
        facts["nozzle_mm"] = float(nozzle.group(1).replace(",", "."))
    material = re.search(r"(?:material(?:_primary)?|filament)\s*[:=]\s*[\"']?([a-z0-9+_-]{3,24})", text)
    if material:
        facts["material"] = material.group(1).upper()
    printer = re.search(r"(?:printer|machine)\s*[:=]\s*[\"']?([^\n,#\]}]{3,80})", text)
    if printer:
        facts["printer"] = printer.group(1).strip(" '\"")
    facts["orientation_known"] = keyword_any(text, ("orientation:", "print orientation", "druckorientierung"))
    paths = [relative(p, ctx.root).lower() for p in ctx.evidence_files]
    flags = {
        "profile": any("profile" in path or "/profiles/" in f"/{path}/" for path in paths),
        "printer": facts["printer"] is not None or keyword_any(text, ("kobra 3 max", "kobra3max", "anycubic")),
        "nozzle": facts["nozzle_mm"] is not None,
        "material": facts["material"] is not None,
        "orientation": bool(facts["orientation_known"]),
    }
    return facts, flags


def readiness(ctx: ProductContext) -> tuple[dict[str, str], str, float, list[str], dict[str, bool]]:
    has_files = bool(ctx.evidence_files)
    has_readme = any(p.name.lower().startswith("readme") for p in ctx.evidence_files)
    has_geometry = any(p.suffix.lower() in GEOMETRY_SUFFIXES for p in ctx.evidence_files)
    has_validation = any("validation" in relative(p, ctx.root).lower() or "test" in p.name.lower() for p in ctx.evidence_files)
    has_interface = "interface" in ctx.evidence_text or "fit" in ctx.evidence_text or "passung" in ctx.evidence_text
    has_acceptance = keyword_any(ctx.evidence_text, ("acceptance_criteria", "acceptance criteria", "release_gates", "akzeptanz"))
    has_test_plan = any("test" in p.name.lower() or "validation-project" in p.name.lower() for p in ctx.evidence_files)
    _, mfg_flags = manufacturing_facts(ctx)
    exact_profile = all(mfg_flags.values())

    scope = "R0" if not has_files else "R3" if ctx.selected_spec and ctx.revision != UNKNOWN_REVISION else "R2" if has_readme else "R1"
    requirements = "R0" if not has_files else "R3" if has_acceptance else "R2" if ctx.selected_spec else "R1"
    interfaces = "R0" if not has_files else "R2" if has_interface and has_validation else "R1"
    manufacturing = "R3" if exact_profile else "R2" if mfg_flags["material"] and mfg_flags["nozzle"] and has_geometry else "R1" if has_geometry else "R0"
    verification = "R3" if has_validation and has_acceptance and has_test_plan else "R2" if has_validation or has_test_plan else "R1" if has_geometry else "R0"
    components = {
        "scope_variant": scope,
        "requirements": requirements,
        "critical_interfaces": interfaces,
        "manufacturing_profile": manufacturing,
        "verification": verification,
    }
    level_num = min(int(value[1]) for value in components.values())
    level = f"R{level_num}"
    completeness = round(sum(int(value[1]) for value in components.values()) / 25 * 100, 1)
    unknowns: list[str] = []
    if ctx.revision == UNKNOWN_REVISION:
        unknowns.append("stable current product revision")
    if interfaces in {"R0", "R1", "R2"}:
        unknowns.append("variant-confirmed critical interface dimensions, tolerances, and uncertainty")
    if not exact_profile:
        unknowns.append("complete printer/material/nozzle/orientation/process-profile set")
    if not has_acceptance:
        unknowns.append("measurable acceptance criteria")
    if not has_test_plan:
        unknowns.append("verification plan and physical result references")
    return components, level, completeness, unknowns, {
        "has_files": has_files,
        "has_acceptance": has_acceptance,
        "has_test_plan": has_test_plan,
        "has_interface": has_interface,
        "has_validation": has_validation,
        "exact_profile": exact_profile,
    }


def interface_profile(ctx: ProductContext, product_k: str, scores: dict[str, int], readiness_level: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    text = f"{ctx.key} {ctx.purpose}".lower()
    printed_name = ctx.product_name
    entities = [{"id": "E-PRINT-001", "kind": "PRINTED_PART", "name": printed_name}]
    if keyword_any(text, ("shoe", "hair-clip", "thumb", "wearable", "user")):
        entities.append({"id": "E-HUM-001", "kind": "HUMAN", "name": "Intended user or body interface"})
        profile = dict(id="IF-HUM-HUM-USR-BODY-001", name="Printed product to intended user/body", endpoint_b="E-HUM-001", boundary="HUM", domains=["GEO", "MEC", "HUM"], function="USR", geometry="BODY")
    elif keyword_any(text, ("drain", "filter", "water", "flow", "diffuser")):
        entities.append({"id": "E-MED-001", "kind": "MEDIUM", "name": "Intended fluid or process medium"})
        profile = dict(id="IF-ENV-FLU-FLW-VOLUME-001", name="Printed product to process medium", endpoint_b="E-MED-001", boundary="ENV", domains=["GEO", "FLU", "ENV"], function="FLW", geometry="VOLUME")
    elif ctx.family in {"printer-workshop", "furniture-systems", "furniture-cabinetry", "organization-storage"}:
        entities.append({"id": "E-HOST-001", "kind": "HOST_OBJECT", "name": "Intended host object or storage envelope"})
        profile = dict(id="IF-EXT-GEO-CON-MIXED-001", name="Printed product to intended host", endpoint_b="E-HOST-001", boundary="EXT", domains=["GEO", "MEC"], function="CON", geometry="MIXED")
    elif ctx.family == "toys-games":
        entities.append({"id": "E-ENV-001", "kind": "ENVIRONMENT", "name": "Supervised use environment"})
        profile = dict(id="IF-ENV-MEC-LOD-BODY-001", name="Printed product to supervised use environment", endpoint_b="E-ENV-001", boundary="ENV", domains=["MEC", "ENV"], function="LOD", geometry="BODY")
    else:
        entities.append({"id": "E-ENV-001", "kind": "ENVIRONMENT", "name": "Display or use surface"})
        profile = dict(id="IF-ENV-GEO-SUP-PLN-001", name="Printed product to display or use surface", endpoint_b="E-ENV-001", boundary="ENV", domains=["GEO", "MEC"], function="SUP", geometry="PLN")

    evidence_level = "E0" if readiness_level == "R0" else "E2" if readiness_level in {"R2", "R3", "R4", "R5"} else "E1"
    ic_axes = {
        "GEO": scores["GEO"],
        "KIN": min(4, scores["MOT"]),
        "TOL": min(4, scores["INT"]),
        "PHY": min(4, scores["PHY"]),
        "VAR": min(4, scores["CTX"]),
        "LIF": 3 if scores["MOT"] >= 3 or scores["PHY"] >= 3 else 2 if product_k != "K0" else 1,
    }
    total = sum(ic_axes.values())
    tier = "I0" if total <= 3 else "I1" if total <= 7 else "I2" if total <= 11 else "I3" if total <= 15 else "I4" if total <= 19 else "I5"
    criticality_label = "SAFETY_CRITICAL" if product_k in {"K3", "K4"} else "FUNCTION_CRITICAL" if product_k == "K2" else "FIT_CRITICAL" if product_k == "K1" else "COSMETIC"
    verification_method = "expert_review" if product_k in {"K3", "K4"} else "prototype_test" if product_k == "K2" else "test_coupon" if product_k == "K1" else "inspection"
    contract: dict[str, Any] = {
        **profile,
        "endpoint_a": "E-PRINT-001",
        "lifecycle_states": ["assembly", "use", "cleaning", "service", "disassembly", "storage"],
        "dimensions": [{
            "id": "DIM-PRIMARY-001",
            "feature": "Primary interface envelope and functional allowance",
            "nominal_mm": None,
            "lower_mm": None,
            "upper_mm": None,
            "clearance_mm": None,
            "uncertainty_mm": None,
            "status": "UNKNOWN",
            "source_ref": ctx.basis_refs[0],
            "criticality": criticality_label,
        }],
        "evidence": {
            "level": evidence_level,
            "sources": ctx.basis_refs,
            "variant_confirmed": False,
            "coverage_percent": 0 if evidence_level == "E0" else 35 if evidence_level == "E1" else 55,
            "uncertainty_note": "The retrospective audit did not establish a variant-confirmed tolerance and uncertainty budget.",
            "observability": "UNKNOWN" if evidence_level == "E0" else "INFERRED" if evidence_level == "E1" else "PARTLY_OBSERVED",
        },
        "interface_complexity": {**ic_axes, "total": total, "tier": tier},
        "criticality": product_k,
        "failure_modes": [{
            "mode": "Primary interface does not meet fit or functional intent",
            "effect": "Loss of intended function and the credible failure effects recorded at product level",
            "mitigation": "Confirm the exact variant, measure the interface, define tolerances, and test a coupon or controlled prototype.",
        }],
        "verification": {
            "method": verification_method,
            "acceptance_criteria": ["Variant-confirmed, measurable interface criteria are approved and the planned verification passes before release."],
            "status": "PLANNED",
            "result_refs": [],
        },
        "owner": "product owner",
        "version": "0.1",
    }
    return entities, contract


def gates_and_decision(
    ctx: ProductContext,
    product_k: str,
    complexity_class: str,
    readiness_level: str,
    components: dict[str, str],
    flags: dict[str, bool],
) -> tuple[dict[str, str], dict[str, str]]:
    g0 = "FAIL" if components["scope_variant"] == "R0" else "PASS" if components["scope_variant"] >= "R2" and ctx.revision != UNKNOWN_REVISION else "WARN"
    g1 = "FAIL" if components["critical_interfaces"] == "R0" else "PASS" if components["critical_interfaces"] >= "R2" else "WARN"
    if product_k == "K0":
        g2 = "PASS" if components["critical_interfaces"] >= "R1" else "WARN"
    elif product_k == "K1":
        g2 = "PASS" if components["critical_interfaces"] >= "R3" else "WARN" if components["critical_interfaces"] == "R2" else "FAIL"
    else:
        g2 = "PASS" if components["critical_interfaces"] >= "R4" else "WARN" if components["critical_interfaces"] == "R3" else "FAIL"
    g3 = "PASS" if flags["exact_profile"] else "FAIL"
    g4 = "PASS" if flags["has_acceptance"] and flags["has_test_plan"] else "WARN" if flags["has_acceptance"] or flags["has_test_plan"] else "FAIL"
    g5 = "FAIL" if product_k == "K4" else "WARN" if product_k == "K3" else "PASS"
    lifecycle_evidence = keyword_any(ctx.evidence_text, ("assembly", "montage", "service", "cleaning", "reinigung", "lifecycle"))
    g6 = "PASS" if lifecycle_evidence else "FAIL" if product_k in {"K3", "K4"} else "WARN"
    gates = {"G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6}

    has_fail = "FAIL" in gates.values()
    if product_k == "K4":
        lane = "E"
        release = "CONCEPT_ONLY"
    elif has_fail or readiness_level in {"R0", "R1"}:
        lane = "E"
        release = "HOLD"
    elif product_k == "K3" or complexity_class in {"C4", "C5"}:
        lane = "D"
        release = "GO_WITH_CONTROLS"
    elif complexity_class in {"C2", "C3"}:
        lane = "C"
        release = "GO_WITH_CONTROLS"
    elif complexity_class == "C1":
        lane = "B"
        release = "GO_WITH_CONTROLS"
    else:
        lane = "A"
        release = "GO"

    if product_k in {"K3", "K4"}:
        confidence = "NOT_AUTONOMOUSLY_RELEASABLE"
    elif readiness_level in {"R0", "R1", "R2"}:
        confidence = "LOW_UNKNOWN"
    elif complexity_class in {"C3", "C4"} or readiness_level == "R3":
        confidence = "CONDITIONAL"
    elif complexity_class in {"C0", "C1", "C2"}:
        confidence = "HIGH"
    else:
        confidence = "MEDIUM_HIGH"
    decision = {
        "lane": lane,
        "confidence": confidence,
        "design_release": release,
        "rationale": "The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.",
    }
    return gates, decision


def warnings_for(ctx: ProductContext, product_k: str, components: dict[str, str], flags: dict[str, bool], scores: dict[str, int]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if ctx.revision == UNKNOWN_REVISION:
        warnings.append({"code": "VARIANT_UNKNOWN", "severity": "WARN", "message": "No stable current product revision is evidenced at the product boundary."})
    if components["critical_interfaces"] in {"R0", "R1", "R2"} and product_k != "K0":
        warnings.append({"code": "CRITICAL_INTERFACE_UNKNOWN", "severity": "BLOCKER", "message": "The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence."})
    if not flags["exact_profile"]:
        warnings.append({"code": "VERIFICATION_NOT_DEFINED", "severity": "BLOCKER", "message": "Printer, material, nozzle, orientation, and process profile are not documented as one complete exact set."})
    if product_k == "K3":
        warnings.append({"code": "SAFETY_EXPERT_REQUIRED", "severity": "BLOCKER", "message": "K3 scope requires expert-in-the-loop review and controlled prototypes; autonomous release is prohibited."})
        warnings.append({"code": "AUTONOMOUS_RELEASE_PROHIBITED", "severity": "BLOCKER", "message": "The credible failure consequence exceeds autonomous release authority."})
    text = f"{ctx.key} {ctx.purpose}".lower()
    if keyword_any(text, ("water", "drain", "filter", "flow", "diffuser", "airflow")):
        warnings.append({"code": "THERMAL_OR_FLOW_CRITICAL", "severity": "WARN" if product_k != "K3" else "BLOCKER", "message": "Flow, drainage, humidity, heat, or airflow performance needs a controlled functional test."})
    if scores["MOT"] >= 3:
        warnings.append({"code": "DYNAMIC_OR_FATIGUE_LOAD", "severity": "WARN" if product_k != "K3" else "BLOCKER", "message": "Repeated motion, flexure, vibration, or dynamic contact needs cycle and failure testing."})
    if keyword_any(text, ("shoe", "hair-clip", "thumb", "wearable")):
        warnings.append({"code": "DEFORMABLE_HUMAN_INTERFACE", "severity": "WARN" if product_k != "K3" else "BLOCKER", "message": "Human geometry, deformation, comfort, and use-state variation are not controlled by repository evidence alone."})
    return warnings


def next_actions(ctx: ProductContext, product_k: str, flags: dict[str, bool]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if product_k in {"K3", "K4"}:
        actions.append({"priority": 1, "action": "Obtain an expert review of credible failure modes and the staged prototype plan.", "exit_criterion": "A named reviewer approves the test scope, controls, and stop conditions."})
    actions.append({"priority": len(actions) + 1, "action": "Confirm the exact product/host variant and complete the primary interface contract.", "exit_criterion": "Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence."})
    if not flags["exact_profile"]:
        actions.append({"priority": len(actions) + 1, "action": "Record the exact manufacturing profile.", "exit_criterion": "Printer, material, nozzle, orientation, and complete process profile are uniquely identified and source-linked."})
    if not (flags["has_acceptance"] and flags["has_test_plan"]):
        actions.append({"priority": len(actions) + 1, "action": "Define measurable acceptance criteria and a minimal coupon/prototype test.", "exit_criterion": "Each critical interface and credible failure mode has a method, threshold, and result-record location."})
    return actions[:4]


def drivers(scores: dict[str, int], rationales: dict[str, str]) -> list[str]:
    ordered = sorted(scores, key=lambda key: (WEIGHTS[key] * scores[key], scores[key], key), reverse=True)[:3]
    return [f"{key}={scores[key]}: {rationales[key]}" for key in ordered]


def build_result(ctx: ProductContext) -> tuple[dict[str, Any], dict[str, str]]:
    scores = complexity_scores(ctx)
    score, complexity_class = complexity_result(scores)
    rationales = score_rationales(ctx, scores)
    product_k, k_rationale, effects = criticality(ctx)
    components, readiness_level, completeness, unknowns, flags = readiness(ctx)
    entities, interface = interface_profile(ctx, product_k, scores, readiness_level)
    gates, decision = gates_and_decision(ctx, product_k, complexity_class, readiness_level, components, flags)
    assessment_slug = re.sub(r"[^A-Z0-9]+", "-", ctx.project_id.upper()).strip("-")
    result = {
        "assessment_id": f"PREFLIGHT-{assessment_slug}-001",
        "assessment_version": ASSESSMENT_VERSION,
        "assessment_date": ASSESSMENT_DATE,
        "product": ctx.product_name,
        "scope": {
            "intended_use": ctx.purpose,
            "user_context": "Retrospectively derived from the current product folder; exact user, host variant, environment, and release state remain limited to cited evidence.",
            "variants": [ctx.revision],
            "out_of_scope": ["Claims not explicitly supported by the cited repository evidence", "Production release without closure of blocking gates"],
        },
        "entities": entities,
        "interfaces": [interface],
        "complexity": {
            "dimension_scores": scores,
            "score_0_100": score,
            "class": complexity_class,
            "drivers": drivers(scores, rationales),
        },
        "readiness": {
            "level": readiness_level,
            "component_levels": components,
            "blocking_unknowns": unknowns,
            "completeness_percent": completeness,
        },
        "criticality": {"level": product_k, "rationale": k_rationale, "credible_failure_effects": effects},
        "gates": gates,
        "decision": decision,
        "warnings": warnings_for(ctx, product_k, components, flags, scores),
        "next_actions": next_actions(ctx, product_k, flags),
        "traceability": {
            "mode": "RETROSPECTIVE",
            "project_id": ctx.project_id,
            "project_revision": ctx.revision,
            "basis_refs": ctx.basis_refs,
            "change_triggers": ["backfill_missing_preflight", "portfolio_documentation_audit", "product_root_version_cleanup"],
            "previous_assessment_id": None,
            "created_at": ctx.generated_at,
            "updated_at": ctx.generated_at,
        },
    }
    return result, rationales


def preflight_input(ctx: ProductContext, result: dict[str, Any]) -> dict[str, Any]:
    facts, _ = manufacturing_facts(ctx)
    return {
        "product": ctx.product_name,
        "intended_use": ctx.purpose,
        "user_context": result["scope"]["user_context"],
        "host_variant": {"manufacturer": None, "model": None, "revision": None, "variant_confirmed": False},
        "lifecycle_states": ["transport", "assembly", "use", "cleaning", "service", "disassembly", "storage", "failure"],
        "requirements": ["Preserve the explicit purpose within the cited scope.", "Close every blocking preflight gate before production release."],
        "known_components": [entity["name"] for entity in result["entities"]],
        "available_evidence": ctx.basis_refs,
        "manufacturing_profile": facts,
        "known_loads_environment": {"loads": [], "temperature_c": None, "media": [], "duration": None},
        "safety_notes": [result["criticality"]["rationale"]],
        "interfaces": [contract["id"] for contract in result["interfaces"]],
    }


def purpose_markdown(ctx: ProductContext, result: dict[str, Any]) -> str:
    refs = "\n".join(f"- `{ref}`" for ref in ctx.basis_refs)
    return f"""# Purpose — {ctx.product_name}

{ctx.purpose}

## Scope status

- Product ID: `{ctx.project_id}`
- Assessed revision: `{ctx.revision}`
- Purpose source: {ctx.purpose_source}
- Purpose confidence: retrospective and limited to the evidence below
- Release meaning: this purpose statement is not a production, safety, compatibility, food-contact, or performance approval

## Evidence basis

{refs}

The current preflight decision is `{result['decision']['design_release']}`. See
[`preflight/preflight-report.md`](preflight/preflight-report.md) for unknowns,
gates, and the required next evidence.
"""


def report_markdown(ctx: ProductContext, result: dict[str, Any], rationales: dict[str, str]) -> str:
    c = result["complexity"]
    r = result["readiness"]
    k = result["criticality"]
    d = result["decision"]
    scorecard = f"{ctx.product_name} | {c['class']} ({c['score_0_100']}/100) | {r['level']} | {k['level']} | Lane {d['lane']} | {d['confidence']}"
    dimension_rows = "\n".join(f"| {name} | {score} | {rationales[name]} |" for name, score in c["dimension_scores"].items())
    component_rows = "\n".join(f"| {name} | {level} |" for name, level in r["component_levels"].items())
    gate_rows = "\n".join(f"| {name} | {status} |" for name, status in result["gates"].items())
    interface_rows = "\n".join(
        f"| `{interface['id']}` | {interface['name']} | {interface['evidence']['level']} | {interface['criticality']} | {interface['verification']['status']} |"
        for interface in result["interfaces"]
    )
    unknowns = "\n".join(f"- {item}" for item in r["blocking_unknowns"]) or "- None recorded."
    warnings = "\n".join(f"- `{item['code']}` ({item['severity']}): {item['message']}" for item in result["warnings"]) or "- None."
    actions = "\n".join(f"{item['priority']}. {item['action']} Exit: {item['exit_criterion']}" for item in result["next_actions"])
    refs = "\n".join(f"- `{ref}`" for ref in ctx.basis_refs)
    fmea = ""
    if k["level"] in {"K2", "K3", "K4"}:
        fmea = """
## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |
"""
    return f"""# Retrospective 3D-design preflight — {ctx.product_name}

`{scorecard}`

## Decision

- Release: `{d['design_release']}`
- Lane: `{d['lane']}`
- Rationale: {d['rationale']}
- Purpose: {ctx.purpose}

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
{dimension_rows}

## Readiness

| Component | Level |
|---|---|
{component_rows}

Blocking unknowns:

{unknowns}

## Criticality

`{k['level']}` — {k['rationale']}

Credible effects: {', '.join(k.get('credible_failure_effects', []))}.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
{interface_rows}

The JSON contract records the primary discovered boundary. Because the audit
does not prove complete interface discovery, G1/G2 remain conservative.

## Hard gates

| Gate | Status |
|---|---|
{gate_rows}

## Warnings

{warnings}
{fmea}
## Next evidence

{actions}

## Traceability basis

{refs}
"""


def workflow_block(result: dict[str, Any]) -> str:
    return "\n".join([
        "  preflight:",
        "    status: current",
        f"    mode: {result['traceability']['mode']}",
        "    artifact: preflight/preflight-result.json",
        f"    assessment_id: {result['assessment_id']}",
        f"    assessment_version: {result['assessment_version']}",
        f"    assessed_project_revision: {json.dumps(result['traceability']['project_revision'], ensure_ascii=False)}",
        f"    updated_at: {json.dumps(result['traceability']['updated_at'], ensure_ascii=False)}",
        "    change_triggers:",
        "      - backfill_missing_preflight",
        "      - portfolio_documentation_audit",
        "      - product_root_version_cleanup",
    ])


def update_design_spec_text(text: str, result: dict[str, Any]) -> str:
    block = workflow_block(result)
    lines = text.rstrip().splitlines()
    workflow_index = next((i for i, line in enumerate(lines) if line.rstrip() == "workflow:" and not line.startswith((" ", "\t"))), None)
    if workflow_index is None:
        return "\n".join(lines) + "\n\nworkflow:\n" + block + "\n"

    workflow_end = len(lines)
    for i in range(workflow_index + 1, len(lines)):
        if lines[i] and not lines[i].startswith((" ", "\t", "#")):
            workflow_end = i
            break
    preflight_index = next((i for i in range(workflow_index + 1, workflow_end) if lines[i].rstrip() == "  preflight:"), None)
    if preflight_index is None:
        lines[workflow_index + 1:workflow_index + 1] = block.splitlines()
    else:
        preflight_end = workflow_end
        for i in range(preflight_index + 1, workflow_end):
            if lines[i].startswith("  ") and not lines[i].startswith("    ") and lines[i].strip():
                preflight_end = i
                break
        lines[preflight_index:preflight_end] = block.splitlines()
    return "\n".join(lines) + "\n"


def create_root_design_spec(ctx: ProductContext, result: dict[str, Any]) -> str:
    source_refs = "\n".join(f"    - {json.dumps(ref, ensure_ascii=False)}" for ref in ctx.basis_refs)
    return f"""schema_version: 1
product:
  id: {json.dumps(ctx.project_id, ensure_ascii=False)}
  name: {json.dumps(ctx.product_name, ensure_ascii=False)}
  version: {json.dumps(ctx.revision, ensure_ascii=False)}
  status: retrospective-inventory

function:
  summary: {json.dumps(ctx.purpose, ensure_ascii=False)}

source_of_truth:
  status: retrospective-index
  current_artifact_refs:
{source_refs}

workflow:
{workflow_block(result)}
  requirements: review-required
  concept: existing-artifacts
  final_release: blocked-by-preflight
"""


def archive_readme(ctx: ProductContext) -> str | None:
    archive = ctx.root / "archive"
    if not archive.exists():
        return None
    entries = sorted(p.relative_to(archive).as_posix() for p in archive.iterdir() if p.name != "README.md")
    current = CURRENT_SELECTIONS.get(ctx.key, ["Current product files remain outside archive; consult PURPOSE.md and preflight/preflight-report.md."])
    exception = ROOT_REVIEW_EXCEPTIONS.get(ctx.key)
    current_lines = "\n".join(f"- `{item}`" for item in current)
    entry_lines = "\n".join(f"- `{item}`" for item in entries) or "- No archived entry recorded."
    exception_text = f"\n## Root review exception\n\n{exception}\n" if exception else ""
    content = f"""# Product archive

This directory contains older or explicitly legacy product versions. Files are
preserved, not deleted. New design work must use the current selection outside
this directory unless a decision log explicitly restores an archived version.

## Current selection

{current_lines}

## Archived entries

{entry_lines}
{exception_text}
"""
    return content.rstrip() + "\n"


def write_text(path: Path, content: str, write: bool) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    changed = previous != content
    if changed and write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return changed


def write_json(path: Path, data: Any, write: bool) -> bool:
    return write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", write)


def write_yaml(path: Path, data: Any, write: bool) -> bool:
    return write_text(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110), write)


def verify_archive_moves() -> list[str]:
    errors: list[str] = []
    for key, entries in ARCHIVE_MOVES.items():
        product = PRODUCTS_ROOT / key
        for entry in entries:
            source = product / entry
            destination = product / "archive" / entry
            if source.exists():
                errors.append(f"source still exists: {source.relative_to(REPO_ROOT)}")
            if not destination.exists():
                errors.append(f"archive target missing: {destination.relative_to(REPO_ROOT)}")
    return errors


def existing_current_result(ctx: ProductContext) -> dict[str, Any] | None:
    """Preserve existing assessments; an invalid intake is never a missing one."""
    purpose_path = ctx.root / "PURPOSE.md"
    result_path = ctx.root / "preflight/preflight-result.json"
    input_path = ctx.root / "preflight/preflight-input.yaml"
    report_path = ctx.root / "preflight/preflight-report.md"
    spec_path = ctx.root / "design-spec.yaml"
    if not result_path.exists():
        workflow = nested_get(safe_yaml(spec_path), "workflow", "preflight") if spec_path.is_file() else None
        if input_path.exists() or report_path.exists() or workflow:
            raise ValueError(f"{ctx.key}: existing preflight companions/link have no result")
        return None
    missing = [path.relative_to(ctx.root).as_posix() for path in
               (purpose_path, result_path, input_path, report_path, spec_path) if not path.is_file()]
    if missing:
        raise ValueError(f"{ctx.key}: existing preflight has missing companions: {', '.join(missing)}")
    purpose = purpose_path.read_text(encoding="utf-8", errors="replace")
    if not valid_purpose(purpose):
        raise ValueError(f"{ctx.key}: purpose needs a title and non-placeholder description")
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"{ctx.key}: unreadable existing preflight/spec: {exc}") from exc
    if not isinstance(result, dict) or not isinstance(spec, dict):
        raise ValueError(f"{ctx.key}: existing preflight and spec must be objects")
    errors, _ = validate_document(result, expected_project_id=ctx.project_id)
    if errors:
        raise ValueError(f"{ctx.key}: invalid existing preflight: {'; '.join(errors)}")
    trace = result.get("traceability")
    workflow = nested_get(spec, "workflow", "preflight")
    if not isinstance(trace, dict) or not isinstance(workflow, dict):
        raise ValueError(f"{ctx.key}: workflow.preflight link missing")
    expected_workflow = {
        "status": "current",
        "artifact": "preflight/preflight-result.json",
        "mode": trace["mode"].upper(),
        "assessment_id": result.get("assessment_id"),
        "assessment_version": result.get("assessment_version"),
        "assessed_project_revision": trace.get("project_revision"),
    }
    mismatched = [field for field, value in expected_workflow.items()
                  if (str(workflow.get(field, "")).upper() if field == "mode"
                      else workflow.get(field)) != value]
    if mismatched:
        raise ValueError(f"{ctx.key}: stale workflow.preflight fields: {', '.join(mismatched)}")
    # A validated product-owned preflight is the authority for its assessed
    # revision.  The inventory context derives a revision heuristically from
    # every file below the product root; adding a later render, P2 package, or
    # other evidence must not make the backfill overwrite that current record.
    if not trace.get("basis_refs"):
        raise ValueError(f"{ctx.key}: existing preflight has no basis refs")
    return result


def valid_purpose(text: str) -> bool:
    """Allow product-authored headings while rejecting empty/scaffold documents."""
    title, _, body = text.strip().partition("\n")
    return title.startswith("# ") and bool(body.strip()) and "TODO" not in text


def process_product(ctx: ProductContext, write: bool) -> tuple[dict[str, Any], list[str]]:
    current_result = existing_current_result(ctx)
    if current_result is not None:
        changed: list[str] = []
        archive_content = archive_readme(ctx)
        if archive_content is not None and write_text(ctx.root / "archive" / "README.md", archive_content, write):
            changed.append((ctx.root / "archive" / "README.md").relative_to(REPO_ROOT).as_posix())
        return current_result, changed

    result, rationales = build_result(ctx)
    changed: list[str] = []
    outputs = {
        ctx.root / "PURPOSE.md": purpose_markdown(ctx, result),
        ctx.root / "preflight" / "preflight-report.md": report_markdown(ctx, result, rationales),
    }
    for path, content in outputs.items():
        if write_text(path, content, write):
            changed.append(path.relative_to(REPO_ROOT).as_posix())
    if write_json(ctx.root / "preflight" / "preflight-result.json", result, write):
        changed.append((ctx.root / "preflight" / "preflight-result.json").relative_to(REPO_ROOT).as_posix())
    if write_yaml(ctx.root / "preflight" / "preflight-input.yaml", preflight_input(ctx, result), write):
        changed.append((ctx.root / "preflight" / "preflight-input.yaml").relative_to(REPO_ROOT).as_posix())

    root_spec = ctx.root / "design-spec.yaml"
    if root_spec.exists():
        spec_content = update_design_spec_text(root_spec.read_text(encoding="utf-8"), result)
    else:
        spec_content = create_root_design_spec(ctx, result)
    if write_text(root_spec, spec_content, write):
        changed.append(root_spec.relative_to(REPO_ROOT).as_posix())

    archive_content = archive_readme(ctx)
    if archive_content is not None and write_text(ctx.root / "archive" / "README.md", archive_content, write):
        changed.append((ctx.root / "archive" / "README.md").relative_to(REPO_ROOT).as_posix())
    return result, changed


def portfolio_audit(contexts: list[ProductContext], results: dict[str, dict[str, Any]], archive_errors: list[str], generated_at: str) -> dict[str, Any]:
    entries = []
    for ctx in contexts:
        result = results[ctx.key]
        entries.append({
            "product": ctx.key,
            "project_id": ctx.project_id,
            "revision": result["traceability"]["project_revision"],
            "purpose_document": "PURPOSE.md",
            "preflight_result": "preflight/preflight-result.json",
            "scorecard": {
                "complexity": result["complexity"]["class"],
                "score_0_100": result["complexity"]["score_0_100"],
                "readiness": result["readiness"]["level"],
                "criticality": result["criticality"]["level"],
                "lane": result["decision"]["lane"],
                "confidence": result["decision"]["confidence"],
                "release": result["decision"]["design_release"],
            },
            "archive": {
                "moved_entries": ARCHIVE_MOVES.get(ctx.key, []),
                "root_status": "REVIEW_REQUIRED" if ctx.key in ROOT_REVIEW_EXCEPTIONS else "CLEAN_OR_NO_VERSION_CONFLICT",
                "exception": ROOT_REVIEW_EXCEPTIONS.get(ctx.key),
            },
        })
    return {
        "audit_id": "PRODUCT-PREFLIGHT-AUDIT-2026-08-31",
        "generated_at": generated_at,
        "scope": "Current products/<family>/<product> inventory; product-owned preflights remain authoritative",
        "product_count": len(contexts),
        "purpose_document_count": len(contexts),
        "preflight_document_count": len(contexts),
        "archive_move_count": sum(len(items) for items in ARCHIVE_MOVES.values()),
        "root_review_required_count": len(ROOT_REVIEW_EXCEPTIONS),
        "archive_verification_errors": archive_errors,
        "products": entries,
    }


def portfolio_markdown(audit: dict[str, Any]) -> str:
    rows = []
    for item in audit["products"]:
        score = item["scorecard"]
        rows.append(
            f"| `{item['product']}` | {score['complexity']} ({score['score_0_100']}) | {score['readiness']} | {score['criticality']} | {score['lane']} | {score['release']} | {item['archive']['root_status']} |"
        )
    exception_lines = "\n".join(
        f"- `{item['product']}`: {item['archive']['exception']}"
        for item in audit["products"] if item["archive"]["exception"]
    )
    errors = "\n".join(f"- {error}" for error in audit["archive_verification_errors"]) or "- None."
    return f"""# Product preflight and purpose audit — 2026-08-31

## Outcome

- Products audited: **{audit['product_count']}**
- Explicit `PURPOSE.md` documents: **{audit['purpose_document_count']}**
- Preflight document sets: **{audit['preflight_document_count']}**
- Older/legacy entries moved into product-local `archive/`: **{audit['archive_move_count']}**
- Roots requiring human review because of pre-existing dirty or ambiguous content: **{audit['root_review_required_count']}**

Each product retains its own prospective or retrospective assessment and
assessed revision. Missing assessments are backfilled retrospectively from
repository evidence. A `HOLD` is an explicit result, not a validation failure
of the document; the aggregate does not grant design or release approval.

## Root review exceptions

{exception_lines}

## Archive move verification

{errors}

## Product scorecards

| Product | Complexity | Readiness | Criticality | Lane | Release | Root status |
|---|---:|---:|---:|---:|---|---|
{chr(10).join(rows)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write generated documents; otherwise perform a dry run.")
    args = parser.parse_args()
    existing_audit = PRODUCTS_ROOT / "PRODUCT-PREFLIGHT-AUDIT-2026-08-31.json"
    generated_at: str | None = None
    if existing_audit.exists():
        try:
            previous = json.loads(existing_audit.read_text(encoding="utf-8"))
            if previous.get("audit_id") == "PRODUCT-PREFLIGHT-AUDIT-2026-08-31":
                generated_at = previous.get("generated_at")
        except (OSError, json.JSONDecodeError):
            generated_at = None
    generated_at = generated_at or datetime.now().astimezone().replace(microsecond=0).isoformat()
    contexts = [build_context(product, generated_at) for product in product_dirs()]
    archive_errors = verify_archive_moves()
    # Check the entire inventory before the first write. A broken product-owned
    # record must not cause a partial rewrite of other products or the aggregate.
    errors: list[str] = []
    for ctx in contexts:
        try:
            existing_current_result(ctx)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    if errors or archive_errors:
        print(json.dumps({
            "mode": "write" if args.write else "dry-run",
            "products": len(contexts), "changed_files": 0, "changed_paths": [],
            "blocked": True, "errors": errors, "archive_errors": archive_errors,
        }, indent=2, ensure_ascii=False))
        return 1
    results: dict[str, dict[str, Any]] = {}
    changed: list[str] = []
    for ctx in contexts:
        result, product_changes = process_product(ctx, args.write)
        results[ctx.key] = result
        changed.extend(product_changes)

    audit = portfolio_audit(contexts, results, archive_errors, generated_at)
    audit_json = PRODUCTS_ROOT / "PRODUCT-PREFLIGHT-AUDIT-2026-08-31.json"
    audit_md = PRODUCTS_ROOT / "PRODUCT-PREFLIGHT-AUDIT-2026-08-31.md"
    if write_json(audit_json, audit, args.write):
        changed.append(audit_json.relative_to(REPO_ROOT).as_posix())
    if write_text(audit_md, portfolio_markdown(audit), args.write):
        changed.append(audit_md.relative_to(REPO_ROOT).as_posix())

    summary = {
        "mode": "write" if args.write else "dry-run",
        "products": len(contexts),
        "changed_files": len(changed),
        "changed_paths": changed,
        "archive_moves_expected": sum(len(items) for items in ARCHIVE_MOVES.values()),
        "archive_errors": archive_errors,
        "root_review_exceptions": len(ROOT_REVIEW_EXCEPTIONS),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if archive_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
