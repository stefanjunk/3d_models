#!/usr/bin/env python3
"""Plan and prepare the four mandatory P2 artifacts in portfolio order.

The tool never overwrites an existing P2 directory or portfolio source. Use
``--initialize-plan`` first, review the generated plan, then run ``--prepare``.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

BUSINESS = Path(__file__).resolve().parents[1]
WORKSPACE = BUSINESS.parent
PORTFOLIO = BUSINESS / "02-portfolio" / "product-portfolio.csv"
PLAN = BUSINESS / "02-portfolio" / "p2-stage-source-plan.json"
FDM_CLI = WORKSPACE / ".agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py"
MESH_PREVIEW = WORKSPACE / ".agents/skills/functional-3d-design/scripts/mesh_preview.py"
PROFILE_ROOT = (
    WORKSPACE / "archive/local-tool-state/anycubic-slicer-next/ota/profiles/Anycubic"
)
GENERIC_MACHINE = PROFILE_ROOT / "machine/Anycubic Kobra 3 Max 0.4 nozzle.json"
GENERIC_PROCESS = (
    PROFILE_ROOT / "process/0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle.json"
)
GENERIC_FILAMENTS = {
    "PLA": PROFILE_ROOT / "filament/Anycubic PLA @Anycubic Kobra 3 Max 0.4 nozzle.json",
    "PETG": PROFILE_ROOT
    / "filament/Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle.json",
    "TPU": PROFILE_ROOT / "filament/Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle.json",
}
TREE_MACHINE = (
    WORKSPACE
    / "products/home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap/abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/profiles/anycubic-slicer-next/machine-kobra3max-hardened-0p4.json"
)
TREE_PROCESS = (
    WORKSPACE
    / "products/organization-storage/mm-org-041-octopus-cable-wrap-organizer/profiles/process-0p20-petg-tool-k3max-treesupport.json"
)
TREE_FILAMENT = (
    WORKSPACE
    / "products/home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap/abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/profiles/anycubic-slicer-next/filament-sunlu-petg-black-k3max-0p4.json"
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
IGNORED_PARTS = {
    ".git",
    "archive",
    "external",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "p2-stage",
}

DEMOTIONS = {
    "MM-ROV-001": "The active root contains no current manufacturing meshes or 3MF; the imported 13-part reference has ten winding/positive-volume review findings and no exact process.",
    "MM-ART-010": "Revision 0.5.4 has per-half candidate projects, but its design specification still records complete 3MF packaging as pending and the secondary connector/hanger print-set coverage is not evidenced in one project.",
    "MM-ART-011": "Revision 0.3.0 has four per-half 3MFs, but no single complete product print set including the declared connector and hanger/standoff parts.",
    "ANYCUBIC-K3MAX-PURGE-CATCHER-R7": "The product README explicitly says there is no current print 3MF and marks the former balanced geometry as rejected and not to print.",
}

PETG_SKUS = {
    "MM-BTH-003",
    "MM-BTH-001",
    "MM-BTH-002",
    "MM-TOOL-001",
    "MM-ACC-001",
    "MM-GAR-001",
    "MM-WALL-001",
    "MM-BOAT-003",
    "UNREGISTERED-K3M-PHC",
    "MM-ORG-041",
    "MM-ORG-042",
    "MM-ORG-043",
    "MM-DEC-004",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path, base: Path = WORKSPACE) -> str:
    return path.resolve().relative_to(base.resolve()).as_posix()


def product_relative(path: Path, product: Path) -> str:
    return path.resolve().relative_to(product.resolve()).as_posix()


def product_files(product: Path, suffixes: set[str] | None = None) -> list[Path]:
    result = []
    for path in product.rglob("*"):
        if not path.is_file():
            continue
        parts = {item.lower() for item in path.relative_to(product).parts}
        if parts & IGNORED_PARTS:
            continue
        if suffixes is None or path.suffix.lower() in suffixes:
            result.append(path)
    return sorted(result)


def yaml_data(path: Path) -> dict[str, Any]:
    try:
        import yaml

        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def design_spec(product: Path) -> tuple[Path | None, dict[str, Any]]:
    candidates = [product / "design-spec.yaml"]
    candidates.extend(
        path
        for path in product.rglob("design-spec.yaml")
        if not (
            {part.lower() for part in path.relative_to(product).parts} & IGNORED_PARTS
        )
    )
    scored = []
    for path in dict.fromkeys(candidates):
        if not path.is_file():
            continue
        data = yaml_data(path)
        project = data.get("project") if isinstance(data.get("project"), dict) else {}
        revision = str(project.get("revision") or data.get("revision") or "")
        score = (
            0 if path.parent == product else 10,
            0 if revision else 10,
            -path.stat().st_mtime,
        )
        scored.append((score, path, data))
    if not scored:
        return None, {}
    _, path, data = min(scored, key=lambda item: item[0])
    return path, data


def revision_for(product: Path) -> str:
    _, data = design_spec(product)
    project = data.get("project") if isinstance(data.get("project"), dict) else {}
    revision = project.get("revision") or data.get("revision")
    if revision:
        return str(revision)
    purpose = product / "PURPOSE.md"
    if purpose.is_file():
        match = re.search(
            r"Assessed revision:\s*`?([^`\n]+)", purpose.read_text(encoding="utf-8")
        )
        if match:
            return match.group(1).strip()
    return "unversioned-p2"


def concept_from_spec(product: Path) -> tuple[Path | None, str]:
    _, data = design_spec(product)
    workflow = data.get("workflow") if isinstance(data.get("workflow"), dict) else {}
    nodes = []
    for key in ("concept_approval", "concept"):
        value = workflow.get(key)
        if isinstance(value, dict):
            nodes.append(value)
    for node in nodes:
        raw = node.get("asset") or node.get("image")
        if isinstance(raw, str):
            candidate = product / raw
            if candidate.is_file() and candidate.suffix.lower() in IMAGE_SUFFIXES:
                status = str(node.get("status", "pending")).lower()
                approval = "approved" if status == "approved" else "pending"
                return candidate, approval
    return None, "retrospective-unapproved"


def choose_concept(product: Path) -> tuple[Path | None, str]:
    selected, approval = concept_from_spec(product)
    if selected:
        return selected, approval
    candidates = []
    for path in product_files(product, IMAGE_SUFFIXES):
        label = path.relative_to(product).as_posix().lower()
        if "concept" not in label and "konzept" not in label:
            continue
        score = (
            0 if "concept-product" in label else 1 if "concept-v" in label else 2,
            0 if "context" in label or "whole" in label else 1,
            -path.stat().st_mtime,
            len(path.parts),
        )
        candidates.append((score, path))
    return (
        (min(candidates, key=lambda item: item[0])[1], approval)
        if candidates
        else (None, approval)
    )


def choose_render(product: Path) -> Path | None:
    revision = revision_for(product).lower()
    revision_tokens = {
        revision,
        revision.removeprefix("v"),
        revision.replace(".", "-"),
        revision.replace(".", "_"),
    }
    candidates = []
    for path in product_files(product, IMAGE_SUFFIXES):
        label = path.relative_to(product).as_posix().lower()
        if (
            "concept" in label
            or "konzept" in label
            or any(
                token in label
                for token in (
                    "watermark",
                    "coupon",
                    "heightmap",
                    "prompt",
                    "source-image",
                )
            )
        ):
            continue
        keyword = next(
            (
                index
                for index, token in enumerate(
                    (
                        "production-three-quarter",
                        "three-quarter",
                        "digital-candidate",
                        "assembly_overview",
                        "assembly-overview",
                        "assembly-preview",
                        "production-geometry-review",
                        "iso",
                        "preview",
                    )
                )
                if token in label
            ),
            None,
        )
        if keyword is None:
            continue
        current_revision = any(token and token in label for token in revision_tokens)
        candidates.append(
            (
                (
                    0 if current_revision else 1,
                    keyword,
                    -path.stat().st_mtime,
                    len(path.parts),
                ),
                path,
            )
        )
    return min(candidates, key=lambda item: item[0])[1] if candidates else None


def existing_3mf_embedded(path: Path) -> tuple[bool, str | None]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            embedded = {
                "Metadata/project_settings.config",
                "Metadata/model_settings.config",
            } <= names
            if not embedded:
                return False, None
            settings = json.loads(archive.read("Metadata/project_settings.config"))
            return True, str(
                settings.get("enable_support")
            ) if "enable_support" in settings else None
    except Exception:
        return False, None


def default_3mf(row: dict[str, str], product: Path) -> list[Path]:
    evidence = WORKSPACE / row.get("Model_Evidence_Path", "")
    if (
        evidence.is_file()
        and evidence.suffix.lower() == ".3mf"
        and product.resolve() in evidence.resolve().parents
    ):
        return [evidence]
    candidates = []
    for path in product_files(product, {".3mf"}):
        label = path.relative_to(product).as_posix().lower()
        if any(
            token in label for token in ("coupon", "gauge", "inspection", "reference")
        ):
            continue
        embedded, _ = existing_3mf_embedded(path)
        score = (
            0
            if any(
                token in label
                for token in ("complete", "print-set", "full", "kit", "assembly")
            )
            else 1,
            0 if embedded else 1,
            -path.stat().st_mtime,
            -path.stat().st_size,
        )
        candidates.append((score, path))
    return [min(candidates, key=lambda item: item[0])[1]] if candidates else []


def source_overrides(sku: str, product: Path, row: dict[str, str]) -> list[Path] | None:
    rel: list[str] | None = None
    if sku == "MM-ORG-001":
        rel = [
            "DRAFT-schubladen-organizer-R1.6-parametric-surfaces/schubladen-organizer/output/DRAFT/DRAFT-R1.6-carbon-assembly.3mf"
        ]
    elif sku == "MM-PER-001":
        rel = [
            "exports/v0.4.1/generated/MARITA/reinforced-run01/candidate/DRAFT-nameform-MA-left-wood-C-v0.4.1.stl",
            "exports/v0.4.1/generated/MARITA/reinforced-run01/candidate/DRAFT-nameform-RITA-right-wood-C-v0.4.1.stl",
        ]
    elif sku == "MM-ORG-003":
        rel = [
            "modern-carbon-desk-organizer-compact-v2.0.0/exports/3mf/DRAFT-MM-ORG-003-modern-carbon-compact-2.0.0-draft.2.3mf"
        ]
    elif sku == "MM-BTH-002":
        rel = ["exports/draft/3mf/DRAFT_ZEN_KINTSUGI_WAVE_FIFO_R3_assembly.3mf"]
    elif sku == "MM-ACC-001":
        rel = [
            "output-r6-final/extra_large/masculine-honeycomb-hair-clip-r6-extra-large.3mf"
        ]
    elif sku == "MM-SHO-001":
        rel = [
            "barfussschuh_v6_1_fitfix/v6_sole_left.3mf",
            "barfussschuh_v6_1_fitfix/v6_sole_right.3mf",
            *sorted(
                path.relative_to(product).as_posix()
                for path in (
                    product / "barfussschuh_v6_2_freeform/exports/manufacturing"
                ).glob("*6.2.0-draft.3*.stl")
            ),
        ]
    elif sku == "MM-PUZ-001":
        rel = ["exports/custom/inner.stl", "exports/custom/outer.stl"]
    elif sku == "MM-WALL-001":
        base = "setzkasten/honeycomb-wood-wall-shelf/generated/"
        rel = [
            base + "honeycomb-module-textured.stl",
            base + "bridge-clip.stl",
            base + "rear-wall-spacer.stl",
        ]
    elif sku == "MM-ORG-014":
        rel = [
            "exports/3mf/DRAFT-MM-ORG-014-palette-dock-and-fit-coupon-0.1.0-draft.1.3mf"
        ]
    elif sku == "MM-ORG-041":
        rel = ["organic/work/run-005/optimization/octopus-100k.stl"]
    elif sku == "MM-ORG-042":
        rel = ["source/generated/divider-block.stl"]
    elif sku == "MM-ORG-043":
        rel = ["source/generated/coin-tray.stl"]
    elif sku == "MM-DEC-004":
        rel = ["organic/work/run-004/04-cavity-and-drain-clean.stl"]
    elif sku == "MM-BTH-001":
        folder = product / "output/rev-0.2.0-draft/stl"
        paths = sorted(
            path
            for path in folder.glob("*_print.stl")
            if "coupon" not in path.name.lower()
        )
        expanded = []
        for path in paths:
            expanded.extend([path, path] if "_2x" in path.stem else [path])
        return expanded
    elif sku == "MM-TOOL-001":
        root = product / "kobra3max_enclosure_project"
        legacy = [
            path
            for path in sorted((root / "STL").glob("*.stl"))
            if "coupon" not in path.name.lower()
        ]
        current = [
            path
            for path in sorted((root / "exports/DRAFT/STL").glob("*.stl"))
            if not any(token in path.name.lower() for token in ("coupon", "test_pin"))
        ]
        current_keys = {path.name.lower().removeprefix("draft_") for path in current}
        return [
            path for path in legacy if path.name.lower() not in current_keys
        ] + current
    elif sku == "MM-GAR-001":
        folder = product / "regenwasser-filterbrunnen_R3_DRAFT/build/draft-r3/stl"
        return [
            path
            for path in sorted(folder.glob("*.stl"))
            if "coupon" not in path.name.lower()
        ]
    elif sku.startswith("MM-SYS-") and sku not in {"MM-SYS-001", "MM-SYS-002"}:
        evidence = WORKSPACE / row.get("Model_Evidence_Path", "")
        return [evidence] if evidence.is_file() else []
    if rel is None:
        return None
    return [product / value for value in rel]


def profile_choice(sku: str, sources: list[Path]) -> tuple[Path, Path, Path, str]:
    if sku in {"MM-ORG-041", "MM-DEC-004"}:
        return TREE_MACHINE, TREE_PROCESS, TREE_FILAMENT, "enabled"
    if len(sources) == 1 and sources[0].suffix.lower() == ".3mf":
        embedded, support = existing_3mf_embedded(sources[0])
        if embedded and support in {"0", "1"}:
            material = (
                "TPU" if sku == "MM-SHO-001" else "PETG" if sku in PETG_SKUS else "PLA"
            )
            return (
                GENERIC_MACHINE,
                GENERIC_PROCESS,
                GENERIC_FILAMENTS[material],
                "enabled" if support == "1" else "disabled",
            )
    material = "TPU" if sku == "MM-SHO-001" else "PETG" if sku in PETG_SKUS else "PLA"
    return GENERIC_MACHINE, GENERIC_PROCESS, GENERIC_FILAMENTS[material], "disabled"


def create_plan(path: Path) -> dict[str, Any]:
    with PORTFOLIO.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["Lifecycle_Stage"].startswith("P2")
        ]
    products = []
    for order, row in enumerate(rows, 1):
        product = WORKSPACE / row["Source_Path"]
        sku = row["Working_SKU"]
        if sku in DEMOTIONS:
            products.append(
                {
                    "order": order,
                    "record_id": row["Record_ID"],
                    "sku": sku,
                    "name": row["Product_or_Model"],
                    "lifecycle_stage": row["Lifecycle_Stage"],
                    "product_root": row["Source_Path"],
                    "revision": revision_for(product),
                    "action": "demote",
                    "reason": DEMOTIONS[sku],
                }
            )
            continue
        override = source_overrides(sku, product, row)
        sources = override if override is not None else default_3mf(row, product)
        concept, approval = choose_concept(product)
        render = choose_render(product)
        machine, process, filament, support = profile_choice(sku, sources)
        missing = [str(item) for item in sources if not item.is_file()]
        products.append(
            {
                "order": order,
                "record_id": row["Record_ID"],
                "sku": sku,
                "name": row["Product_or_Model"],
                "lifecycle_stage": row["Lifecycle_Stage"],
                "product_root": row["Source_Path"],
                "revision": revision_for(product),
                "action": "prepare",
                "concept_image": relative(concept) if concept else None,
                "concept_approval_state": approval,
                "rendered_image": relative(render) if render else None,
                "print_sources": [relative(item) for item in sources],
                "source_error": f"Missing print sources: {missing}"
                if missing or not sources
                else None,
                "support_mode": support,
                "machine_profile": relative(machine),
                "process_profile": relative(process),
                "filament_profile": relative(filament),
            }
        )
    payload = {
        "schema_version": "1.0",
        "portfolio": relative(PORTFOLIO),
        "products": products,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def purpose_summary(product: Path, fallback: str) -> str:
    purpose = product / "PURPOSE.md"
    if not purpose.is_file():
        return fallback
    paragraphs = re.split(r"\n\s*\n", purpose.read_text(encoding="utf-8").strip())
    for paragraph in paragraphs[1:]:
        plain = " ".join(
            line.strip()
            for line in paragraph.splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "-", "["))
        )
        if len(plain.split()) >= 8:
            german_markers = re.findall(
                r"\b(?:der|die|das|ein|eine|einer|und|für|mit|ohne|über|ist|sind|wird|werden|soll|sollen|druck|regal|fläche)\b",
                plain.lower(),
            )
            if len(german_markers) < 2:
                return plain
    return fallback


def render_missing(product: Path, sources: list[Path], target: Path) -> None:
    direct_meshes = [
        path for path in sources if path.suffix.lower() in {".stl", ".obj"}
    ]
    with tempfile.TemporaryDirectory(prefix="metrimade-p2-render-") as temporary:
        temporary_root = Path(temporary)
        extracted: list[Path] = []
        for index, source in enumerate(
            (path for path in sources if path.suffix.lower() == ".3mf"), 1
        ):
            extraction = temporary_root / f"source-{index}"
            extraction.mkdir()
            completed = subprocess.run(
                ["AnycubicSlicerNext", "--export-stl", str(source.resolve())],
                cwd=extraction,
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"Could not extract render mesh from {source}: {completed.stderr}"
                )
            extracted.extend(sorted((extraction / "stl").glob("*.stl")))
        meshes = [*direct_meshes, *extracted]
        if not meshes:
            raise RuntimeError(
                "No STL/OBJ/3MF geometry is available for the missing current-model render"
            )
        render_source = meshes[0]
        if len(meshes) > 1:
            import trimesh

            loaded = [trimesh.load_mesh(path, process=False) for path in meshes]
            combined = trimesh.util.concatenate(loaded)
            render_source = temporary_root / "combined-current-model.stl"
            combined.export(render_source)
        subprocess.run(
            [
                sys.executable,
                "-B",
                str(MESH_PREVIEW),
                str(render_source),
                "--out",
                str(target),
            ],
            check=True,
        )


def retrospective_concept(
    product: Path,
    target: Path,
    render: Path,
    sku: str,
    name: str,
    revision: str,
    summary: str,
) -> None:
    mime = (
        "image/svg+xml"
        if render.suffix.lower() == ".svg"
        else "image/jpeg"
        if render.suffix.lower() in {".jpg", ".jpeg"}
        else "image/png"
    )
    encoded = base64.b64encode(render.read_bytes()).decode("ascii")
    lines = textwrap.wrap(re.sub(r"\s+", " ", summary), width=58)[:5]
    text_nodes = "".join(
        f'<text x="830" y="{285 + index * 38}" class="body">{html.escape(line)}</text>'
        for index, line in enumerate(lines)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0d1b24"/><stop offset="1" stop-color="#173847"/></linearGradient><filter id="shadow"><feDropShadow dx="0" dy="12" stdDeviation="16" flood-opacity=".35"/></filter></defs>
<style>.eyebrow{{font:600 22px sans-serif;letter-spacing:3px;fill:#75d1ce}}.title{{font:700 44px sans-serif;fill:#f5f1e8}}.meta{{font:500 22px sans-serif;fill:#c7d5d9}}.body{{font:400 25px sans-serif;fill:#e9eff1}}.note{{font:600 19px sans-serif;fill:#f3c982}}</style>
<rect width="1400" height="900" fill="url(#bg)"/><text x="70" y="75" class="eyebrow">RETROSPECTIVE PRODUCT CONCEPT</text><text x="70" y="135" class="title">{html.escape(name)}</text><text x="70" y="178" class="meta">{html.escape(sku)} · revision {html.escape(revision)}</text>
<rect x="65" y="225" width="700" height="585" rx="30" fill="#f8f7f2" filter="url(#shadow)"/><image x="90" y="250" width="650" height="535" preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{encoded}"/>
<text x="830" y="235" class="eyebrow">DESIGN INTENT</text>{text_nodes}<line x1="830" y1="520" x2="1320" y2="520" stroke="#75d1ce" stroke-width="2"/><text x="830" y="570" class="note">CURRENT-MODEL BASIS</text><text x="830" y="610" class="body">Complete product candidate shown</text><text x="830" y="648" class="body">in its digital model state.</text><text x="830" y="720" class="note">P2 LIMIT</text><text x="830" y="760" class="body">Not a real print or release proof.</text><text x="830" y="798" class="body">No physical or commercial claim.</text>
</svg>"""
    target.write_text(svg, encoding="utf-8")


def project_objects(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "Metadata/model_settings.config" in names:
            root = ET.fromstring(archive.read("Metadata/model_settings.config"))
            items = []
            for index, obj in enumerate(root.findall("object"), 1):
                name_node = next(
                    (
                        node
                        for node in obj.findall("metadata")
                        if node.get("key") == "name"
                    ),
                    None,
                )
                name = (
                    name_node.get("value")
                    if name_node is not None
                    else f"print-object-{index}"
                )
                items.append({"name": name, "quantity": 1})
            if items:
                return items
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        build = model.find("m:build", ns)
        return (
            [
                {"name": f"print-object-{index}", "quantity": 1}
                for index, _ in enumerate(build.findall("m:item", ns), 1)
            ]
            if build is not None
            else []
        )


def write_description(
    path: Path,
    name: str,
    sku: str,
    revision: str,
    summary: str,
    parts: list[dict[str, Any]],
) -> None:
    part_text = ", ".join(item["name"] for item in parts[:12])
    if len(parts) > 12:
        part_text += f", and {len(parts) - 12} additional declared print objects"
    text = f"""# {name}

{summary}

## P2 digital-candidate contents

This English development description applies to `{sku}` revision `{revision}`.
The complete candidate 3MF contains {len(parts)} declared print object(s):
{part_text}. The included project preserves the selected build orientation and
the recorded support decision for the candidate.

## Development boundary

This is a digital P2 candidate, not a photograph or a physically qualified or
commercially released product. Fit, finish, strength, safety, rights clearance,
material behaviour and storefront claims remain governed by their separate
evidence and approval gates.
"""
    path.write_text(text, encoding="utf-8")


def prepare_entry(entry: dict[str, Any]) -> dict[str, Any]:
    product = WORKSPACE / entry["product_root"]
    stage = product / "p2-stage"
    if stage.exists():
        raise RuntimeError(f"Refusing existing P2 directory: {stage}")
    if entry.get("source_error"):
        raise RuntimeError(entry["source_error"])
    sources = [WORKSPACE / value for value in entry["print_sources"]]
    stage.mkdir(parents=True)
    try:
        render = (
            WORKSPACE / entry["rendered_image"]
            if entry.get("rendered_image")
            else stage / "current-model-render.png"
        )
        if not render.is_file():
            render_missing(product, sources, render)

        summary = purpose_summary(
            product, f"Digital printable candidate for {entry['name']}."
        )
        concept = (
            WORKSPACE / entry["concept_image"]
            if entry.get("concept_image")
            else stage / "retrospective-concept.svg"
        )
        approval = entry.get("concept_approval_state", "retrospective-unapproved")
        if not concept.is_file():
            retrospective_concept(
                product,
                concept,
                render,
                entry["sku"],
                entry["name"],
                entry["revision"],
                summary,
            )
            approval = "retrospective-unapproved"

        embedded, embedded_support = (
            existing_3mf_embedded(sources[0])
            if len(sources) == 1 and sources[0].suffix.lower() == ".3mf"
            else (False, None)
        )
        if embedded and (
            (entry["support_mode"] == "disabled" and embedded_support == "0")
            or (entry["support_mode"] == "enabled" and embedded_support == "1")
        ):
            print_set = sources[0]
            author_report = None
        else:
            safe_revision = re.sub(r"[^A-Za-z0-9._-]+", "-", entry["revision"])
            print_set = stage / f"{entry['sku']}-{safe_revision}-print-set.3mf"
            author_report = stage / "3mf-authoring.json"
            command = [
                sys.executable,
                "-B",
                str(FDM_CLI),
                "author-anycubic-3mf",
                str(print_set),
                *[str(path) for path in sources],
                "--machine-profile",
                str(WORKSPACE / entry["machine_profile"]),
                "--process-profile",
                str(WORKSPACE / entry["process_profile"]),
                "--filament-profile",
                str(WORKSPACE / entry["filament_profile"]),
                "--support-mode",
                entry["support_mode"],
                "--json-out",
                str(author_report),
            ]
            completed = subprocess.run(
                command, text=True, capture_output=True, check=False
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"3MF authoring failed: {completed.stdout}{completed.stderr}"
                )

        parts = project_objects(print_set)
        if not parts:
            raise RuntimeError("The selected 3MF has no printable objects")
        description = stage / "product-description.en.md"
        write_description(
            description, entry["name"], entry["sku"], entry["revision"], summary, parts
        )

        manifest = {
            "schema_version": "1.0",
            "product": {
                "record_id": entry["record_id"],
                "sku": entry["sku"],
                "name": entry["name"],
                "revision": entry["revision"],
                "lifecycle_stage": entry["lifecycle_stage"],
                "root": "..",
            },
            "artifacts": {
                "description_en": {
                    "path": product_relative(description, product),
                    "sha256": sha256(description),
                    "language": "en",
                },
                "concept_image": {
                    "path": product_relative(concept, product),
                    "sha256": sha256(concept),
                    "scope": "whole-product",
                    "approval_state": approval,
                },
                "rendered_image": {
                    "path": product_relative(render, product),
                    "sha256": sha256(render),
                    "basis": "current-model",
                },
                "print_set_3mf": {
                    "path": product_relative(print_set, product),
                    "sha256": sha256(print_set),
                    "all_print_parts_included": True,
                    "print_parts": parts,
                    "orientation": {
                        "status": "considered",
                        "encoding": "embedded-slicer-project",
                        "summary": "Source rotations are preserved; objects are arranged and placed on the build plate in the authored manufacturing orientation.",
                    },
                    "supports": {
                        "status": "considered",
                        "mode": entry["support_mode"],
                        "encoding": "embedded-slicer-project",
                        "summary": "Tree/automatic support is embedded for the selected organic candidate."
                        if entry["support_mode"] == "enabled"
                        else "Generated support is disabled for the authored orientation; layer-level review remains required before P3.",
                    },
                },
            },
            "limitations": [
                "P2 is digital evidence only and is not physical, rights, safety, appearance or commercial approval.",
                "Part-list completeness is reviewed against the named candidate revision and remains subject to product-owner approval.",
            ],
        }
        manifest_path = stage / "p2-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        validation = stage / "p2-validation.json"
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(FDM_CLI),
                "validate-p2-stage",
                str(manifest_path),
                "--json-out",
                str(validation),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"P2 validation failed: {completed.stdout}{completed.stderr}"
            )
        return {
            "sku": entry["sku"],
            "status": "PASS",
            "manifest": relative(manifest_path),
            "validation": relative(validation),
            "print_objects": len(parts),
            "authored_3mf": author_report is not None,
        }
    except Exception:
        shutil.rmtree(stage)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--initialize-plan", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--sku", action="append", default=[])
    args = parser.parse_args()
    if args.initialize_plan:
        if args.plan.exists():
            raise SystemExit(f"Refusing to overwrite existing plan: {args.plan}")
        payload = create_plan(args.plan)
        print(
            json.dumps(
                {
                    "plan": relative(args.plan),
                    "products": len(payload["products"]),
                    "demotions": sum(
                        item["action"] == "demote" for item in payload["products"]
                    ),
                },
                indent=2,
            )
        )
        return 0
    if not args.prepare:
        parser.error("select --initialize-plan or --prepare")
    payload = json.loads(args.plan.read_text(encoding="utf-8"))
    selected = set(args.sku)
    results = []
    for entry in payload["products"]:
        if selected and entry["sku"] not in selected:
            continue
        if entry["action"] == "demote":
            results.append(
                {"sku": entry["sku"], "status": "DEMOTE", "reason": entry["reason"]}
            )
            continue
        try:
            result = prepare_entry(entry)
            results.append(result)
            print(f"{entry['order']:02d} {entry['sku']} PASS")
        except Exception as exc:
            results.append(
                {
                    "sku": entry["sku"],
                    "status": "FAIL",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"{entry['order']:02d} {entry['sku']} FAIL: {exc}", file=sys.stderr)
            break
    print(json.dumps({"results": results}, indent=2, ensure_ascii=False))
    return 1 if any(item["status"] == "FAIL" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
