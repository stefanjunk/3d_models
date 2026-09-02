#!/usr/bin/env python3
"""Build Berlin revision 0.5.0 with a parameterized raised site marker.

The approved revision 0.4.0 map, split, interfaces and semantic Z bands remain
the geometry base.  This revision adds one replaceable monochrome artwork
profile at a frozen address/coordinate.  The profile becomes part of tool 4,
replaces lower color bodies in its footprint, and never creates a fifth tool.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import tempfile
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh
import yaml
import PIL
from PIL import Image
from scipy import ndimage
from skimage import measure, morphology

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
BASE_DIR = PRODUCT / "source" / "v0.4.0" / "berlin"
BASE_SCRIPT = BASE_DIR / "build_berlin_modes.py"
SITE_PARAMETERS_PATH = HERE / "site-marker-parameters.json"
PALETTE_CATALOG_PATH = PRODUCT / "palette-catalog.yaml"
BLENDER_COMPOSITE_SCRIPT = HERE / "rebuild_composite_blender.py"
RSVG_CONVERT = Path("/usr/bin/rsvg-convert")

spec = importlib.util.spec_from_file_location("mm_art_010_base_v040", BASE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load base generator: {BASE_SCRIPT}")
BASE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BASE)
BASE.BLENDER_COMPOSITE_SCRIPT = BLENDER_COMPOSITE_SCRIPT

SITE_PARAMETERS = json.loads(SITE_PARAMETERS_PATH.read_text())
PALETTE_CATALOG = yaml.safe_load(PALETTE_CATALOG_PATH.read_text())
MODES = BASE.MODES
TOOL_KEYS = ("bone-white", "nardo-grey", "black", "orange")
TOOL_SUFFIX = {
    "bone-white": "tool1-base",
    "nardo-grey": "tool2-relief",
    "black": "tool3-streets",
    "orange": "tool4-boundary-marker",
}
TOOL_LABEL = {
    "bone-white": "Tool 1 — land base",
    "nardo-grey": "Tool 2 — relief and areas",
    "black": "Tool 3 — street network",
    "orange": "Tool 4 — boundary, accents and site marker",
}
SELECTED_PALETTE = PALETTE_CATALOG["selected_pilot_palette"]
PALETTE = {
    entry["order"]: entry
    for entry in PALETTE_CATALOG["presets"][SELECTED_PALETTE]["colors"]
}
MARKER_RASTER_PITCH_MM = 0.05
MARKER_APERTURE_CLEARANCE_MM = 12.0
MARKER_APERTURE_CLEARANCE_RASTER_MARGIN_MM = BASE.RASTER_PITCH_MM
MARKER_SECTION_SIMPLIFY_MM = 0.015
TOOL_SIMPLIFY_MM = {
    "bone-white": BASE.MESH_SIMPLIFY_TOLERANCE_MM,
    "nardo-grey": 0.015,
    "black": 0.015,
    "orange": 0.015,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def resolve_parameter_path(value: str) -> Path:
    path = (HERE / value).resolve()
    if not path.is_file():
        raise ValueError(f"parameter path does not exist: {path}")
    return path


def load_location() -> tuple[list[float], Path, dict]:
    location = SITE_PARAMETERS["site_marker"]["location"]
    geocode_path = resolve_parameter_path(location["frozen_geocode"])
    geocode = json.loads(geocode_path.read_text())
    override = location.get("coordinate_override_epsg25833")
    coordinate = override if override is not None else geocode["geocode"]["coordinate"]
    if not isinstance(coordinate, list) or len(coordinate) != 2:
        raise ValueError("site-marker coordinate must contain exactly X and Y")
    return [float(coordinate[0]), float(coordinate[1])], geocode_path, geocode


def render_artwork_mask() -> tuple[np.ndarray, Path, dict]:
    marker = SITE_PARAMETERS["site_marker"]
    artwork = marker["artwork"]
    placement = marker["placement"]
    asset = resolve_parameter_path(artwork["asset"])
    width_mm = float(placement["width_mm"])
    height_mm = float(placement["resolved_height_mm"])
    width_px = max(8, round(width_mm / MARKER_RASTER_PITCH_MM))
    kind = artwork["kind"]
    renderer: dict[str, object]
    if kind in {"vector_logo", "vector_icon"}:
        if asset.suffix.lower() != ".svg":
            raise ValueError("the current vector renderer requires an SVG asset")
        with tempfile.TemporaryDirectory(prefix="mm-art-010-marker-") as temporary:
            png = Path(temporary) / "marker.png"
            command = [
                str(RSVG_CONVERT),
                "--keep-aspect-ratio",
                "--width",
                str(width_px),
                "--output",
                str(png),
                str(asset),
            ]
            completed = subprocess.run(command, text=True, capture_output=True, check=False)
            if completed.returncode != 0 or not png.is_file() or png.stat().st_size == 0:
                raise RuntimeError(
                    f"rsvg-convert failed with {completed.returncode}: "
                    f"{completed.stderr or completed.stdout}"
                )
            rgba = np.asarray(Image.open(png).convert("RGBA"), dtype=np.uint8)
        mask = rgba[:, :, 3] >= 128
        version = subprocess.run(
            [str(RSVG_CONVERT), "--version"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        renderer = {
            "name": "rsvg-convert",
            "version": version,
            "path": str(RSVG_CONVERT),
            "sha256": sha256(RSVG_CONVERT.resolve()),
        }
    elif kind == "monochrome_raster_mask":
        image = Image.open(asset).convert("RGBA")
        rgba = np.asarray(image, dtype=np.uint8)
        alpha = rgba[:, :, 3]
        luminance = np.asarray(image.convert("L"), dtype=np.uint8)
        mask = alpha >= 128 if np.any(alpha < 255) else luminance < 128
        renderer = {"name": "Pillow monochrome mask", "version": PIL.__version__}
    else:
        raise ValueError(f"unsupported artwork kind: {kind}")
    if not mask.any():
        raise ValueError("artwork raster is empty")
    labels, components = ndimage.label(mask)
    counts = np.bincount(labels.ravel())
    renderer.update(
        {
            "raster_size_px": [int(mask.shape[1]), int(mask.shape[0])],
            "component_count": int(components),
            "smallest_component_pixels": int(counts[1:].min()) if components else 0,
            "physical_size_mm": [width_mm, height_mm],
            "pitch_nominal_mm": MARKER_RASTER_PITCH_MM,
        }
    )
    return mask, asset, renderer


def marker_cross_section(
    mask: np.ndarray,
    center_mm: tuple[float, float],
    width_mm: float,
    height_mm: float,
    angle_deg: float,
) -> m3d.CrossSection:
    padded = np.pad(mask.astype(np.uint8), 1)
    raw_contours = measure.find_contours(padded, 0.5, fully_connected="high")
    contours: list[np.ndarray] = []
    angle = math.radians(angle_deg)
    rotation = np.array(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]],
        dtype=np.float64,
    )
    for contour in raw_contours:
        contour = measure.approximate_polygon(contour, tolerance=0.35)
        if len(contour) < 4:
            continue
        rows = contour[:, 0] - 1.0
        columns = contour[:, 1] - 1.0
        x = columns * width_mm / mask.shape[1] - width_mm / 2.0
        y = height_mm / 2.0 - rows * height_mm / mask.shape[0]
        xy = np.column_stack((x, y)) @ rotation.T
        xy[:, 0] += center_mm[0]
        xy[:, 1] += center_mm[1]
        contours.append(xy.astype(np.float64))
    section = m3d.CrossSection(contours, m3d.FillRule.EvenOdd).simplify(
        MARKER_SECTION_SIMPLIFY_MM
    )
    if section.is_empty() or section.area() <= 0:
        raise ValueError("artwork did not produce a positive cross-section")
    return section


def marker_global_raster(
    mask: np.ndarray,
    center_mm: tuple[float, float],
    width_mm: float,
    height_mm: float,
    angle_deg: float,
    shape: tuple[int, int],
) -> np.ndarray:
    pitch = BASE.RASTER_PITCH_MM
    size = (max(1, round(width_mm / pitch)), max(1, round(height_mm / pitch)))
    image = Image.fromarray((mask * 255).astype(np.uint8)).resize(
        size, Image.Resampling.NEAREST
    )
    if abs(angle_deg) > 1e-9:
        image = image.rotate(-angle_deg, resample=Image.Resampling.NEAREST, expand=True)
    canvas = Image.new("L", (shape[1], shape[0]), 0)
    left = round(center_mm[0] / pitch - image.width / 2.0)
    top = round((400.0 - center_mm[1]) / pitch - image.height / 2.0)
    canvas.paste(image, (left, top))
    return np.asarray(canvas, dtype=np.uint8) >= 128


def save_preview(masks: dict, marker_mask: np.ndarray, path: Path) -> None:
    def rgb(hex_value: str) -> tuple[int, int, int]:
        value = hex_value.lstrip("#")
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))

    height, width = masks["outer"].shape
    pixels = np.zeros((height, width, 4), dtype=np.uint8)
    pixels[masks["outer"]] = (*rgb(PALETTE[1]["display_hex"]), 255)
    pixels[masks["nardo"]] = (*rgb(PALETTE[2]["display_hex"]), 255)
    pixels[masks["black"]] = (*rgb(PALETTE[3]["display_hex"]), 255)
    pixels[masks["orange"] | marker_mask] = (*rgb(PALETTE[4]["display_hex"]), 255)
    pixels[masks["apertures"]] = (255, 200, 87, 255)
    Image.fromarray(pixels).resize((1200, 800), Image.Resampling.LANCZOS).save(path)


def update_aperture_keepout(masks: dict, marker_mask: np.ndarray) -> dict:
    pitch = BASE.RASTER_PITCH_MM
    aperture_before = masks["apertures"].copy()
    radius_px = math.ceil(
        (MARKER_APERTURE_CLEARANCE_MM + MARKER_APERTURE_CLEARANCE_RASTER_MARGIN_MM)
        / pitch
    )
    keepout = morphology.dilation(marker_mask, footprint=morphology.disk(radius_px))
    masks["apertures"] &= ~keepout
    distance = ndimage.distance_transform_edt(~marker_mask) * pitch
    remaining = masks["apertures"]
    clearance = float(distance[remaining].min()) if remaining.any() else float("inf")
    split_column = round(300.0 / pitch)
    half_slices = {
        "left": slice(0, split_column),
        "right": slice(split_column + 1, masks["outer"].shape[1]),
    }
    for half, column_slice in half_slices.items():
        components = ndimage.label(
            masks["outer"][:, column_slice] & ~masks["apertures"][:, column_slice]
        )[1]
        masks["aperture_bridges"][half]["retained_raster_components"] = int(components)
    return {
        "required_clearance_mm": MARKER_APERTURE_CLEARANCE_MM,
        "raster_margin_mm": MARKER_APERTURE_CLEARANCE_RASTER_MARGIN_MM,
        "measured_clearance_mm": clearance,
        "removed_aperture_area_mm2": float(
            np.count_nonzero(aperture_before & ~masks["apertures"]) * pitch**2
        ),
        "direct_overlap_before_pixels": int(np.count_nonzero(aperture_before & marker_mask)),
        "direct_overlap_after_pixels": int(np.count_nonzero(masks["apertures"] & marker_mask)),
    }


def build_mode(
    mode: str,
    export_dir: Path,
    validation_dir: Path,
    artwork_mask: np.ndarray,
    coordinate_epsg25833: list[float],
) -> dict:
    placement_path, placement = BASE.load_placement(mode)
    boundary = BASE.read_geojson(BASE.SOURCE / "boundary.geojson")
    outer = BASE.outer_geometry(mode, boundary, placement)
    masks = BASE.raster_masks(mode, boundary, outer, placement)
    transform = placement["transform"]
    center = (
        coordinate_epsg25833[0] * transform["uniform_scale_mm_per_source_m"]
        + transform["translate_mm"][0],
        coordinate_epsg25833[1] * transform["uniform_scale_mm_per_source_m"]
        + transform["translate_mm"][1],
    )
    marker_cfg = SITE_PARAMETERS["site_marker"]
    marker_width = float(marker_cfg["placement"]["width_mm"])
    marker_height = float(marker_cfg["placement"]["resolved_height_mm"])
    marker_angle = float(marker_cfg["placement"]["orientation_deg"])
    source_marker_section = marker_cross_section(
        artwork_mask, center, marker_width, marker_height, marker_angle
    )
    outer_section = BASE.to_cross_section(outer)
    marker_outside_area = (source_marker_section - outer_section).area()
    marker_raster = marker_global_raster(
        artwork_mask,
        center,
        marker_width,
        marker_height,
        marker_angle,
        masks["outer"].shape,
    )
    if np.any(marker_raster & ~masks["outer"]):
        raise ValueError(f"{mode}: marker raster extends outside retained body")
    # All map semantics are manufactured on the approved 0.25 mm raster.  Use
    # that same grid for the marker Boolean footprint to avoid sub-grid sliver
    # faces where the high-resolution artwork crosses relief-cell boundaries.
    marker_section = (
        BASE.mask_to_cross_section(marker_raster, BASE.RASTER_PITCH_MM)
        ^ outer_section
    )
    upper_tool_clearance_mm = float(
        marker_cfg["relief"]["minimum_xy_clearance_to_other_upper_tools_mm"]
    )
    upper_keepout_radius_px = math.ceil(
        upper_tool_clearance_mm / BASE.RASTER_PITCH_MM
    )
    marker_upper_keepout_raster = morphology.dilation(
        marker_raster, footprint=morphology.disk(upper_keepout_radius_px)
    )
    marker_upper_keepout_section = (
        BASE.mask_to_cross_section(
            marker_upper_keepout_raster, BASE.RASTER_PITCH_MM
        )
        ^ outer_section
    )
    aperture_keepout = update_aperture_keepout(masks, marker_raster)

    upper_color_section = BASE.to_cross_section(
        outer.buffer(-BASE.UPPER_COLOR_EDGE_INSET_MM)
    )
    support_reference_sections = {
        name: BASE.mask_to_cross_section(masks[name], BASE.RASTER_PITCH_MM)
        ^ upper_color_section
        for name in ("nardo", "black", "orange")
    }
    # Apply the keep-out to the shared manufacturing raster before contouring.
    # Subtracting two independently simplified vector contours can create a
    # point-touching vertical edge after STL serialization.
    masks["nardo"] &= ~marker_upper_keepout_raster
    masks["black"] &= ~marker_upper_keepout_raster
    sections = {
        name: BASE.mask_to_cross_section(masks[name], BASE.RASTER_PITCH_MM)
        ^ upper_color_section
        for name in ("nardo", "black", "orange")
    }
    sections["apertures"] = (
        BASE.mask_to_cross_section(masks["apertures"], BASE.RASTER_PITCH_MM)
        ^ outer_section
    )
    support_top_z = BASE.Z_BANDS["bone-white"][1]
    support_hits = {}
    for key in ("nardo", "black", "orange"):
        overlap_area = (support_reference_sections[key] ^ marker_section).area()
        support_hits[key] = overlap_area
        if overlap_area > 1e-6:
            band_key = {
                "nardo": "nardo-grey",
                "black": "black",
                "orange": "orange",
            }[key]
            support_top_z = max(support_top_z, BASE.Z_BANDS[band_key][1])
    marker_top_z = support_top_z + float(
        marker_cfg["relief"]["height_above_highest_local_face_mm"]
    )

    preview = validation_dir / f"berlin-{mode.replace('_', '-')}-site-marker-top-preview.png"
    save_preview(masks, marker_raster, preview)

    half_definitions = {
        "left": (0.0, 300.0 - BASE.SEAM_GAP_MM / 2.0),
        "right": (300.0 + BASE.SEAM_GAP_MM / 2.0, 600.0),
    }
    artifacts = [preview]
    half_reports = {}
    for half, (x0, x1) in half_definitions.items():
        local_width = x1 - x0
        half_global = BASE.to_cross_section(BASE.box(x0, 0.0, x1, 400.0))
        upper_half_global = BASE.to_cross_section(
            BASE.box(
                x0 + BASE.UPPER_COLOR_EDGE_INSET_MM,
                BASE.UPPER_COLOR_EDGE_INSET_MM,
                x1 - BASE.UPPER_COLOR_EDGE_INSET_MM,
                400.0 - BASE.UPPER_COLOR_EDGE_INSET_MM,
            )
        )
        local_sections = {
            name: (
                section ^ (half_global if name == "apertures" else upper_half_global)
            ).translate((-x0, 0.0))
            for name, section in sections.items()
        }
        local_outer = (outer_section ^ half_global).translate((-x0, 0.0))
        local_marker = (marker_section ^ half_global).translate((-x0, 0.0))
        marker_area = local_marker.area()
        local_marker_upper_keepout = (
            marker_upper_keepout_section ^ half_global
        ).translate((-x0, 0.0))
        body_sections = {
            "bone-white": local_outer - local_sections["apertures"],
            "nardo-grey": local_sections["nardo"],
            "black": local_sections["black"],
            "orange": local_sections["orange"],
        }
        manifolds = {
            "bone-white": BASE.extrude_section(
                body_sections["bone-white"], *BASE.Z_BANDS["bone-white"]
            )
            - BASE.rear_cutters(half, local_width, placement),
            "nardo-grey": BASE.extrude_section(
                body_sections["nardo-grey"], *BASE.Z_BANDS["nardo-grey"]
            ),
            "black": BASE.extrude_section(
                body_sections["black"], *BASE.Z_BANDS["black"]
            ),
            "orange": BASE.extrude_section(
                body_sections["orange"], *BASE.Z_BANDS["orange"]
            ),
        }
        if marker_area > 1e-6:
            manifolds["orange"] += BASE.extrude_section(
                local_marker, BASE.Z_BANDS["bone-white"][1], marker_top_z
            )
        pairwise_overlap_mm3 = {}
        for index, first in enumerate(TOOL_KEYS):
            for second in TOOL_KEYS[index + 1 :]:
                pairwise_overlap_mm3[f"{first}__{second}"] = float(
                    (manifolds[first] ^ manifolds[second]).volume()
                )

        tool_reports = {}
        tool_paths: list[Path] = []
        prefix = f"berlin-{mode.replace('_', '-')}-{half}"
        for tool_key in TOOL_KEYS:
            manifold = manifolds[tool_key].simplify(TOOL_SIMPLIFY_MM[tool_key])
            manifolds[tool_key] = manifold
            if manifold.is_empty() or manifold.volume() <= 0:
                raise ValueError(f"{mode}/{half}/{tool_key} is empty")
            path = export_dir / f"{prefix}-{TOOL_SUFFIX[tool_key]}.stl"
            mesh = BASE.manifold_to_trimesh(manifold)
            mesh.export(path)
            artifacts.append(path)
            tool_paths.append(path)
            roundtrip = BASE.roundtrip_stl_metrics(path)
            tool_reports[tool_key] = {
                "semantic_name": TOOL_LABEL[tool_key],
                "physical_filament": PALETTE[TOOL_KEYS.index(tool_key) + 1]["name"],
                "section_area_mm2": body_sections[tool_key].area(),
                "simplify_tolerance_mm": TOOL_SIMPLIFY_MM[tool_key],
                **roundtrip,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }

        composite_path = export_dir / f"{prefix}-composite.stl"
        raw_composite_path = (
            validation_dir.parent
            / "composite-raw"
            / f"{prefix}-composite-blender-raw.stl"
        )
        composite_roundtrip, composite_trace = BASE.rebuild_composite(
            tool_paths, raw_composite_path, composite_path
        )
        artifacts.extend((composite_path, raw_composite_path))
        aperture_area = local_sections["apertures"].area()
        retained_area = local_outer.area()
        half_reports[half] = {
            "local_width_mm": local_width,
            "retained_outer_area_mm2": retained_area,
            "aperture_area_mm2": aperture_area,
            "aperture_fraction_of_retained_body": aperture_area / retained_area,
            "aperture_limit": BASE.LIGHT["maximum_open_area_fraction_per_half"],
            "aperture_island_control": masks["aperture_bridges"][half],
            "site_marker": {
                "present": marker_area > 1e-6,
                "area_mm2": marker_area,
                "center_global_mm": list(center),
                "support_top_z_mm": support_top_z if marker_area > 1e-6 else None,
                "top_z_mm": marker_top_z if marker_area > 1e-6 else None,
                "relief_above_support_mm": (
                    marker_top_z - support_top_z if marker_area > 1e-6 else None
                ),
                "upper_tool_xy_clearance_mm": upper_tool_clearance_mm,
                "upper_tool_keepout_area_mm2": local_marker_upper_keepout.area(),
            },
            "pairwise_tool_overlap_mm3": pairwise_overlap_mm3,
            "tools": tool_reports,
            "composite": {
                **composite_roundtrip,
                "bytes": composite_path.stat().st_size,
                "sha256": sha256(composite_path),
                "rebuild_trace": composite_trace,
            },
        }

    expected_marker_half = "left" if center[0] < 300.0 else "right"
    mode_pass = (
        marker_outside_area <= 0.01
        and abs(300.0 - center[0]) - marker_width / 2.0
        >= float(marker_cfg["placement"]["minimum_clearance_to_center_seam_mm"])
        and aperture_keepout["measured_clearance_mm"]
        >= MARKER_APERTURE_CLEARANCE_MM
        and half_reports[expected_marker_half]["site_marker"]["present"]
        and not half_reports[
            "right" if expected_marker_half == "left" else "left"
        ]["site_marker"]["present"]
        and all(
            report["composite"]["watertight"]
            and report["composite"]["positive_volume"]
            and report["composite"]["connected_components"] == 1
            and report["composite"]["boundary_edges"] == 0
            and report["composite"]["nonmanifold_edges"] == 0
            and report["composite"]["degenerate_faces"] == 0
            and report["composite"]["duplicate_faces"] == 0
            and report["composite"]["triangles"] <= 750_000
            and report["aperture_fraction_of_retained_body"]
            <= report["aperture_limit"]
            and report["aperture_island_control"]["retained_raster_components"] == 1
            and max(report["pairwise_tool_overlap_mm3"].values(), default=0.0)
            <= 1e-5
            and all(
                tool["watertight"]
                and tool["positive_volume"]
                and tool["boundary_edges"] == 0
                and tool["nonmanifold_edges"] == 0
                and tool["degenerate_faces"] == 0
                and tool["duplicate_faces"] == 0
                for tool in report["tools"].values()
            )
            for report in half_reports.values()
        )
    )
    return {
        "status": "PASS" if mode_pass else "FAIL",
        "placement_manifest": {
            "path": str(placement_path.relative_to(PRODUCT)),
            "sha256": sha256(placement_path),
        },
        "outer_bounds_mm": list(outer.bounds),
        "outer_area_mm2": outer.area,
        "panel_transform": transform,
        "site_marker": {
            "center_mm": list(center),
            "expected_half": expected_marker_half,
            "width_mm": marker_width,
            "height_mm": marker_height,
            "orientation_deg": marker_angle,
            "source_section_area_mm2": source_marker_section.area(),
            "manufacturing_section_area_mm2": marker_section.area(),
            "manufacturing_raster_pitch_mm": BASE.RASTER_PITCH_MM,
            "upper_tool_xy_clearance_mm": upper_tool_clearance_mm,
            "outside_retained_body_area_mm2": marker_outside_area,
            "support_intersection_area_mm2": support_hits,
            "support_top_z_mm": support_top_z,
            "top_z_mm": marker_top_z,
            "aperture_keepout": aperture_keepout,
        },
        "halves": half_reports,
        "preview": str(preview.relative_to(PRODUCT)),
        "artifacts": [
            {
                "path": str(path.relative_to(PRODUCT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in artifacts
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate",
        required=True,
        help="new immutable output ID, for example digital-candidate-r1",
    )
    args = parser.parse_args()
    if not args.candidate.replace("-", "").isalnum():
        raise SystemExit("candidate must contain only letters, digits and hyphens")

    coordinate, geocode_path, geocode = load_location()
    artwork_mask, artwork_path, renderer = render_artwork_mask()
    required = [
        BASE_SCRIPT,
        BASE.PARAMETERS_PATH,
        BASE.INTERFACE_PARAMETERS_PATH,
        BASE.BLENDER,
        BLENDER_COMPOSITE_SCRIPT,
        SITE_PARAMETERS_PATH,
        PALETTE_CATALOG_PATH,
        geocode_path,
        artwork_path,
        BASE.SOURCE / "source-manifest.json",
        BASE.SOURCE / "boundary.geojson",
        BASE.SOURCE / "roads-major.geojson",
        BASE.SOURCE / "roads-accent.geojson",
        BASE.SOURCE / "rail.geojson",
        BASE.SOURCE / "waterways.geojson",
        BASE.PLACEMENT_DIR / "boundary-crop-placement.json",
        BASE.PLACEMENT_DIR / "context-outline-placement.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing source or gate input(s): {missing}")
    if json.loads((BASE.SOURCE / "source-manifest.json").read_text()).get("status") != "PASS":
        raise SystemExit("base source manifest is not PASS")

    export_root = PRODUCT / "exports" / "v0.5.0" / "berlin" / args.candidate
    validation_root = PRODUCT / "validation" / "v0.5.0" / "berlin" / args.candidate
    if export_root.exists() or validation_root.exists():
        raise SystemExit("refusing destructive overwrite of an existing candidate directory")
    export_root.mkdir(parents=True)
    (validation_root / "renders").mkdir(parents=True)

    reports = {}
    for mode in MODES:
        mode_export = export_root / mode.replace("_", "-")
        mode_export.mkdir()
        reports[mode] = build_mode(
            mode,
            mode_export,
            validation_root / "renders",
            artwork_mask,
            coordinate,
        )
    status = "PASS" if all(report["status"] == "PASS" for report in reports.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.0",
        "candidate": args.candidate,
        "status": status,
        "representation": "two display modes, two permanent halves per mode, four named disjoint semantic tool solids per half, with a raised parameterized site marker in tool 4",
        "base_geometry": {
            "revision": "0.4.0",
            "generator": str(BASE_SCRIPT.relative_to(PRODUCT)),
            "generator_sha256": sha256(BASE_SCRIPT),
            "parameters": str(BASE.PARAMETERS_PATH.relative_to(PRODUCT)),
            "parameters_sha256": sha256(BASE.PARAMETERS_PATH),
        },
        "site_marker": {
            "parameters": str(SITE_PARAMETERS_PATH.relative_to(PRODUCT)),
            "parameters_sha256": sha256(SITE_PARAMETERS_PATH),
            "artwork": str(artwork_path.relative_to(PRODUCT)),
            "artwork_sha256": sha256(artwork_path),
            "geocode": str(geocode_path.relative_to(PRODUCT)),
            "geocode_sha256": sha256(geocode_path),
            "coordinate_epsg25833": coordinate,
            "address": geocode["address_input"],
            "renderer": renderer,
            "semantic_tool": int(SITE_PARAMETERS["site_marker"]["relief"]["semantic_tool"]),
        },
        "selected_palette": {
            "preset": SELECTED_PALETTE,
            "catalog": str(PALETTE_CATALOG_PATH.relative_to(PRODUCT)),
            "catalog_sha256": sha256(PALETTE_CATALOG_PATH),
            "tools": [PALETTE[index] for index in sorted(PALETTE)],
        },
        "tool_z_bands_mm": BASE.Z_BANDS,
        "manufacturing_raster_pitch_mm": BASE.RASTER_PITCH_MM,
        "marker_raster_pitch_mm": MARKER_RASTER_PITCH_MM,
        "upper_color_edge_inset_mm": BASE.UPPER_COLOR_EDGE_INSET_MM,
        "modes": reports,
        "shared_secondary_parts": {
            "seam_connector": "exports/v0.3.0/interfaces/seam-connector-c025.stl",
            "upper_hanger": "exports/v0.3.0/interfaces/upper-hanger-18mm.stl",
            "lower_standoff": "exports/v0.3.0/interfaces/lower-standoff-18mm.stl",
            "interface_coupon": "coupons/v0.3.0/interface-coupon-all-clearances.stl",
            "reuse_basis": "shape authority unchanged; site-marker geometry does not touch the rear interfaces",
        },
        "mesh_policy": {
            "status": "not-beneficial for an additional post-build decimation",
            "tool_simplify_tolerances_mm": TOOL_SIMPLIFY_MM,
            "protected_regions": [
                "site-marker silhouette and relief top",
                "outer perimeter and center seam",
                "rear connector and mounting pockets",
                "light apertures and retained bridges",
                "bed-contact plane",
            ],
            "triangle_target_per_main_half": 750_000,
            "triangle_stop_per_main_half": 1_500_000,
            "peak_memory_gib": 4.0,
            "max_mesh_mib_per_main_half": 75.0,
            "max_exact_slice_seconds_per_half": 600,
        },
        "limitations": [
            "DRAFT digital candidate; connector/socket compensation and logo readability remain physical-coupon controlled.",
            "Exact ACE slot identity, directed purge matrix, wall anchors, physical load, lit appearance, brand clearance, watermark and release are not approved.",
            "The marker is a monochrome semantic-tool solid. A replacement asset must be regenerated and revalidated rather than painted manually in the slicer.",
        ],
    }
    report_path = validation_root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    manifest = {
        "schema_version": "1.0",
        "generator": str(Path(__file__).resolve().relative_to(PRODUCT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "build_report": str(report_path.relative_to(PRODUCT)),
        "build_report_sha256": sha256(report_path),
    }
    (validation_root / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "status": status,
                "report": str(report_path),
                "export_root": str(export_root),
            }
        )
    )
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
