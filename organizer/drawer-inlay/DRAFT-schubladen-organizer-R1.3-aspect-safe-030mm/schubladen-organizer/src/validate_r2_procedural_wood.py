#!/usr/bin/env python3
"""Strict digital validation for the unmarked R2 procedural-wood DRAFT pipeline."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REVISION_PREFIX = "R2-procedural-wood"
MODULES = ("driver-front", "driver-back", "hardware-front", "hardware-back")
ACCESSORIES = (
    "screwdriver-comb",
    "drawer-fit-corner-coupon",
    "connector-coupon-male",
    "connector-coupon-female",
)
EXPECTED_ENVELOPE = {"min": [0.0, 0.0, 0.0], "max": [227.0, 357.0, 64.0]}
EXPECTED_INPUTS = {
    "design_spec": "design-spec.yaml",
    "model_params": "config/model-params.json",
    "wood_config": "config/wood-texture-params.json",
    "build_source": "src/manifold_build.mjs",
    "mesh_export": "src/mesh_export.mjs",
    "model_source": "src/manifold_model.mjs",
    "wood_planner": "src/procedural_wood.mjs",
}
ASSEMBLY_FLOOR_SOURCE_ID = "assembly-global-organizer-floor"


def r2_stl_names() -> tuple[str, ...]:
    modules = tuple(f"DRAFT-R2-{module}-procedural-wood-unmarked.stl" for module in MODULES)
    accessories = (
        "DRAFT-R2-screwdriver-comb-procedural-wood-unmarked.stl",
        "DRAFT-R2-drawer-fit-corner-coupon.stl",
        "DRAFT-R2-connector-coupon-male.stl",
        "DRAFT-R2-connector-coupon-female.stl",
    )
    return modules + accessories + ("DRAFT-R2-procedural-wood-coupon.stl",)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_identity(root: Path, path: Path) -> dict:
    return {"path": str(path.relative_to(root)), "sha256": sha256_file(path)}


def close(a: float, b: float, tolerance: float = 1.0e-6) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tolerance)


def safe_relative_path(root: Path, value: str) -> Path | None:
    try:
        candidate = (root / value).resolve()
        candidate.relative_to(root.resolve())
        return candidate
    except (ValueError, OSError):
        return None


def verify_identity_bundle(
    root: Path,
    report_path: Path,
    report: dict,
    expected_inputs: dict[str, str],
    expected_artifacts: dict[str, str],
) -> list[str]:
    """Verify exact paths/hashes and report/artifact freshness for one build report."""
    errors: list[str] = []
    identities = report.get("identities", {})
    inputs = identities.get("inputs", {})
    artifacts = identities.get("artifacts", {})
    if set(inputs) != set(expected_inputs):
        errors.append(f"{report_path.name}: input identity keys are {sorted(inputs)}, expected {sorted(expected_inputs)}")
    if set(artifacts) != set(expected_artifacts):
        errors.append(
            f"{report_path.name}: artifact identity keys are {sorted(artifacts)}, expected {sorted(expected_artifacts)}"
        )

    input_paths: list[Path] = []
    artifact_paths: list[Path] = []
    for label, expected in expected_inputs.items():
        identity = inputs.get(label, {})
        if identity.get("path") != expected:
            errors.append(f"{report_path.name}: {label} path mismatch")
            continue
        path = safe_relative_path(root, expected)
        if path is None or not path.is_file():
            errors.append(f"{report_path.name}: missing input {expected}")
            continue
        input_paths.append(path)
        if identity.get("sha256") != sha256_file(path):
            errors.append(f"{report_path.name}: {label} SHA-256 mismatch")

    for label, expected in expected_artifacts.items():
        identity = artifacts.get(label, {})
        if identity.get("path") != expected:
            errors.append(f"{report_path.name}: {label} path mismatch")
            continue
        path = safe_relative_path(root, expected)
        if path is None or not path.is_file():
            errors.append(f"{report_path.name}: missing artifact {expected}")
            continue
        artifact_paths.append(path)
        if identity.get("sha256") != sha256_file(path):
            errors.append(f"{report_path.name}: {label} SHA-256 mismatch")

    if input_paths and artifact_paths:
        newest_input = max(path.stat().st_mtime_ns for path in input_paths)
        for path in artifact_paths:
            if path.stat().st_mtime_ns < newest_input:
                errors.append(f"{report_path.name}: stale artifact {path.relative_to(root)}")
    if report_path.is_file():
        newest_dependency = max(
            (path.stat().st_mtime_ns for path in input_paths + artifact_paths),
            default=0,
        )
        if report_path.stat().st_mtime_ns < newest_dependency:
            errors.append(f"{report_path.name}: stale report timestamp")
    else:
        errors.append(f"missing report {report_path.relative_to(root)}")
    return errors


def expected_report_artifacts(module: str) -> dict[str, str]:
    return {
        "stl": f"output/DRAFT/DRAFT-R2-{module}-procedural-wood-unmarked.stl",
        "mesh_cache": f"reports/mesh-cache/R2-{module}-procedural-wood-unmarked.meshbin",
    }


def check_r2_build_freshness(root: Path) -> tuple[list[str], dict[str, dict]]:
    """Reject stale/wrong-revision module, accessory, and coupon reports before aggregation."""
    errors: list[str] = []
    loaded: dict[str, dict] = {}
    active_revision = str(read_json(root / "config" / "model-params.json").get("model_revision", ""))
    for module in MODULES:
        path = root / "reports" / f"build-final-R2-{module}-procedural-wood-unmarked.json"
        if not path.is_file():
            errors.append(f"missing R2 module report {path.relative_to(root)}")
            continue
        report = read_json(path)
        loaded[module] = report
        if report.get("status") != "DRAFT" or report.get("revision") != active_revision:
            errors.append(f"{path.name}: wrong revision/status")
        if report.get("route") != "r2-procedural-wood-module-only" or report.get("module", {}).get("id") != module:
            errors.append(f"{path.name}: wrong R2 module route/id")
        expected_artifacts = expected_report_artifacts(module)
        if report.get("module", {}).get("file") != expected_artifacts["stl"]:
            errors.append(f"{path.name}: STL filename mismatch")
        if report.get("module", {}).get("mesh_cache") != expected_artifacts["mesh_cache"]:
            errors.append(f"{path.name}: mesh-cache filename mismatch")
        errors.extend(verify_identity_bundle(root, path, report, EXPECTED_INPUTS, expected_artifacts))

    accessory_path = root / "reports" / "build-final-R2-accessories-procedural-wood-unmarked.json"
    if not accessory_path.is_file():
        errors.append(f"missing R2 accessory report {accessory_path.relative_to(root)}")
    else:
        report = read_json(accessory_path)
        loaded["accessories"] = report
        expected = {
            "screwdriver-comb": "output/DRAFT/DRAFT-R2-screwdriver-comb-procedural-wood-unmarked.stl",
            "drawer-fit-corner-coupon": "output/DRAFT/DRAFT-R2-drawer-fit-corner-coupon.stl",
            "connector-coupon-male": "output/DRAFT/DRAFT-R2-connector-coupon-male.stl",
            "connector-coupon-female": "output/DRAFT/DRAFT-R2-connector-coupon-female.stl",
        }
        if report.get("status") != "DRAFT" or report.get("revision") != active_revision:
            errors.append(f"{accessory_path.name}: wrong revision/status")
        if report.get("route") != "r2-accessories-only" or set(report.get("artifacts", {})) != set(ACCESSORIES):
            errors.append(f"{accessory_path.name}: wrong route/artifact IDs")
        for artifact, expected_file in expected.items():
            if report.get("artifacts", {}).get(artifact, {}).get("file") != expected_file:
                errors.append(f"{accessory_path.name}: filename mismatch for {artifact}")
        errors.extend(verify_identity_bundle(root, accessory_path, report, EXPECTED_INPUTS, expected))

    coupon_path = root / "reports" / "build-final-wood-coupon.json"
    if not coupon_path.is_file():
        errors.append(f"missing R2 wood-coupon report {coupon_path.relative_to(root)}")
    else:
        report = read_json(coupon_path)
        loaded["wood-coupon"] = report
        expected = {"stl": "output/DRAFT/DRAFT-R2-procedural-wood-coupon.stl"}
        if report.get("status") != "DRAFT" or report.get("revision") != active_revision:
            errors.append(f"{coupon_path.name}: wrong revision/status")
        if report.get("route") != "wood-coupon-only" or report.get("coupon", {}).get("file") != expected["stl"]:
            errors.append(f"{coupon_path.name}: wrong R2 coupon route/file")
        errors.extend(verify_identity_bundle(root, coupon_path, report, EXPECTED_INPUTS, expected))
    return errors, loaded


def budget_metrics(module_rows: list[dict], budget: dict) -> dict:
    triangles = sum(int(row["triangles"]) for row in module_rows)
    stl_bytes = sum(int(row["file_bytes"]) for row in module_rows)
    baseline_triangles = int(budget["r1_3_baseline_triangles"])
    baseline_bytes = int(budget["r1_3_baseline_stl_bytes"])
    triangle_reduction = 1.0 - triangles / baseline_triangles
    byte_reduction = 1.0 - stl_bytes / baseline_bytes
    minimum_reduction = float(budget["minimum_triangle_and_byte_reduction_fraction"])
    peak_limit = float(budget["max_peak_rss_mib_per_module"])
    return {
        "aggregate_triangles": triangles,
        "aggregate_stl_bytes": stl_bytes,
        "r1_3_baseline_triangles": baseline_triangles,
        "r1_3_baseline_stl_bytes": baseline_bytes,
        "triangle_reduction_fraction": triangle_reduction,
        "byte_reduction_fraction": byte_reduction,
        "triangle_target_total": int(budget["triangle_target_total"]),
        "triangle_stop_total": int(budget["triangle_stop_total"]),
        "max_stl_bytes_total": int(budget["max_stl_bytes_total"]),
        "max_peak_rss_mib_per_module": peak_limit,
        "minimum_reduction_fraction": minimum_reduction,
        "per_module": module_rows,
        "checks": {
            "triangle_target": triangles <= int(budget["triangle_target_total"]),
            "triangle_stop": triangles <= int(budget["triangle_stop_total"]),
            "stl_byte_budget": stl_bytes <= int(budget["max_stl_bytes_total"]),
            "per_module_triangle_budget": all(int(row["triangles"]) <= 750_000 for row in module_rows),
            "per_module_peak_rss_budget": all(float(row["peak_rss_mib"]) <= peak_limit for row in module_rows),
            "triangle_reduction": triangle_reduction + 1.0e-12 >= minimum_reduction,
            "byte_reduction": byte_reduction + 1.0e-12 >= minimum_reduction,
        },
    }


def local_name(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        namespace, name = tag[1:].split("}", 1)
        return namespace, name
    return "", tag


def parse_transform(value: str | None) -> list[float]:
    if value is None:
        return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    values = [float(item) for item in value.split()]
    if len(values) != 12:
        raise ValueError("3MF build transform must contain 12 numbers")
    return values


def transform_point(point: tuple[float, float, float], matrix: list[float]) -> tuple[float, float, float]:
    x, y, z = point
    return (
        x * matrix[0] + y * matrix[3] + z * matrix[6] + matrix[9],
        x * matrix[1] + y * matrix[4] + z * matrix[7] + matrix[10],
        x * matrix[2] + y * matrix[5] + z * matrix[8] + matrix[11],
    )


def scan_3mf(path: Path) -> dict:
    """CRC-check and stream-parse Core objects, build transforms, metadata, and envelope."""
    with zipfile.ZipFile(path) as archive:
        names = sorted(archive.namelist())
        crc_pass = archive.testzip() is None
        objects: dict[int, dict] = {}
        items: list[dict] = []
        metadata: dict[str, str] = {}
        namespace_pass = True
        current: dict | None = None
        with archive.open("3D/3dmodel.model") as model:
            for event, element in ET.iterparse(model, events=("start", "end")):
                namespace, name = local_name(element.tag)
                if name in {
                    "model", "metadata", "resources", "object", "mesh", "vertices", "vertex",
                    "triangles", "triangle", "build", "item",
                } and namespace != CORE_NS:
                    namespace_pass = False
                if event == "start" and name == "object":
                    current = {
                        "id": int(element.attrib["id"]),
                        "name": element.attrib.get("name", ""),
                        "bounds_min_mm": [math.inf, math.inf, math.inf],
                        "bounds_max_mm": [-math.inf, -math.inf, -math.inf],
                        "triangles": 0,
                    }
                elif event == "start" and name == "vertex" and current is not None:
                    point = [float(element.attrib[axis]) for axis in ("x", "y", "z")]
                    for axis in range(3):
                        current["bounds_min_mm"][axis] = min(current["bounds_min_mm"][axis], point[axis])
                        current["bounds_max_mm"][axis] = max(current["bounds_max_mm"][axis], point[axis])
                elif event == "start" and name == "triangle" and current is not None:
                    current["triangles"] += 1
                elif event == "start" and name == "item":
                    items.append({
                        "object_id": int(element.attrib["objectid"]),
                        "transform": parse_transform(element.attrib.get("transform")),
                    })
                elif event == "end" and name == "metadata":
                    metadata[element.attrib.get("name", "")] = element.text or ""
                elif event == "end" and name == "object" and current is not None:
                    objects[current["id"]] = current
                    current = None
                if event == "end":
                    element.clear()

    envelope_min = [math.inf, math.inf, math.inf]
    envelope_max = [-math.inf, -math.inf, -math.inf]
    for item in items:
        obj = objects.get(item["object_id"])
        if obj is None:
            continue
        low, high = obj["bounds_min_mm"], obj["bounds_max_mm"]
        for x in (low[0], high[0]):
            for y in (low[1], high[1]):
                for z in (low[2], high[2]):
                    transformed = transform_point((x, y, z), item["transform"])
                    for axis in range(3):
                        envelope_min[axis] = min(envelope_min[axis], transformed[axis])
                        envelope_max[axis] = max(envelope_max[axis], transformed[axis])
    translation_only = all(
        all(close(matrix[index], expected) for index, expected in enumerate((1, 0, 0, 0, 1, 0, 0, 0, 1)))
        for matrix in (item["transform"] for item in items)
    )
    return {
        "zip_entries": names,
        "crc_pass": crc_pass,
        "core_namespace_pass": namespace_pass,
        "objects": [objects[key] for key in sorted(objects)],
        "build_items": items,
        "metadata": metadata,
        "translation_only_transforms": translation_only,
        "assembly_bounds_mm": {"min": envelope_min, "max": envelope_max},
    }


def exact_envelope(actual: dict, expected: dict = EXPECTED_ENVELOPE) -> bool:
    return all(close(actual[key][axis], expected[key][axis]) for key in ("min", "max") for axis in range(3))


def stl_header(path: Path) -> str:
    with path.open("rb") as handle:
        return handle.read(80).decode("ascii", errors="replace").rstrip("\x00 ")


def validate_topology_reports(root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    expected_names = r2_stl_names()
    actual = tuple(sorted(path.name for path in (root / "output" / "DRAFT").glob("DRAFT-R2-*.stl")))
    if set(actual) != set(expected_names) or len(actual) != 9:
        errors.append(f"R2 STL set mismatch: found {list(actual)}, expected {list(expected_names)}")
    results: list[dict] = []
    for name in expected_names:
        stl = root / "output" / "DRAFT" / name
        report_path = root / "reports" / f"R2-mesh-validation-{stl.stem}.json"
        if not stl.is_file() or not report_path.is_file():
            errors.append(f"missing STL or independent validation report for {name}")
            continue
        report = read_json(report_path)
        files = report.get("files", [])
        if len(files) != 1 or Path(files[0].get("file", "")).name != name:
            errors.append(f"{report_path.name}: does not validate exactly {name}")
            continue
        if not report.get("pass") or not files[0].get("pass"):
            errors.append(f"{report_path.name}: topology FAIL")
        if report_path.stat().st_mtime_ns < stl.stat().st_mtime_ns:
            errors.append(f"{report_path.name}: stale topology report")
        header = stl_header(stl).lower()
        if "draft" not in header or "r2" not in header:
            errors.append(f"{name}: non-DRAFT or wrong-revision STL header")
        results.append(files[0])
    aggregate_path = root / "reports" / "R2-procedural-wood-unmarked-mesh-validation.json"
    if not aggregate_path.is_file():
        errors.append("missing aggregate R2 topology report")
    else:
        aggregate = read_json(aggregate_path)
        aggregate_names = [Path(item.get("file", "")).name for item in aggregate.get("files", [])]
        if set(aggregate_names) != set(expected_names) or len(aggregate_names) != 9 or not aggregate.get("pass"):
            errors.append("aggregate R2 topology report is incomplete or failed")
    return errors, {"expected_files": list(expected_names), "actual_files": list(actual), "file_count": len(actual), "files": results}


def texture_plan_errors(label: str, plan: dict, expected_width: float, expected_depth: float) -> list[str]:
    errors: list[str] = []
    if plan.get("policy", {}).get("operation") != "engrave-only":
        errors.append(f"{label}: non-engrave policy")
    groove = plan.get("groove", {})
    if not close(groove.get("width_mm", -1), expected_width) or not close(
        groove.get("depth_mm", -1), expected_depth
    ):
        errors.append(f"{label}: wrong groove width/depth")
    features = list(plan.get("paths", []))
    for knot in plan.get("knots", []):
        features.extend(knot.get("contours", []))
    for feature in features:
        if not close(feature.get("width_mm", -1), expected_width) or not close(
            feature.get("depth_mm", -1), expected_depth
        ):
            errors.append(f"{label}: wrong path/knot width/depth")
    return errors


def rectangle_is_valid(rectangle: object) -> bool:
    if not isinstance(rectangle, dict) or set(rectangle) != {"min", "max"}:
        return False
    minimum = rectangle.get("min")
    maximum = rectangle.get("max")
    return (
        isinstance(minimum, list)
        and isinstance(maximum, list)
        and len(minimum) == 2
        and len(maximum) == 2
        and all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in minimum + maximum)
        and all(float(maximum[axis]) > float(minimum[axis]) for axis in range(2))
    )


def rectangles_close(first: object, second: object) -> bool:
    return rectangle_is_valid(first) and rectangle_is_valid(second) and all(
        close(first[key][axis], second[key][axis])
        for key in ("min", "max")
        for axis in range(2)
    )


def point_in_rectangle(point: object, rectangle: dict) -> bool:
    return (
        isinstance(point, list)
        and len(point) == 2
        and all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in point)
        and all(
            float(rectangle["min"][axis]) - 1.0e-6
            <= float(point[axis])
            <= float(rectangle["max"][axis]) + 1.0e-6
            for axis in range(2)
        )
    )


def polyline_length(points: list) -> float:
    return sum(
        math.hypot(
            float(points[index][0]) - float(points[index - 1][0]),
            float(points[index][1]) - float(points[index - 1][1]),
        )
        for index in range(1, len(points))
    )


def source_bounding_rectangle(targets: list[dict]) -> dict:
    return {
        "min": [min(float(target["rectangle_mm"]["min"][axis]) for target in targets) for axis in range(2)],
        "max": [max(float(target["rectangle_mm"]["max"][axis]) for target in targets) for axis in range(2)],
    }


def assembly_floor_source_rectangle(params: dict, wood: dict) -> dict:
    organizer = params["organizer"]
    wall = organizer.get("outer_wall_thickness_override")
    if wall is None:
        wall = organizer["base_wall_thickness"]
    margin = float(wood["grain"]["floor_margin_mm"])
    return {
        "min": [float(wall) + margin, float(wall) + margin],
        "max": [
            float(organizer["width_x"]) - float(wall) - margin,
            float(organizer["depth_y"]) - float(wall) - margin,
        ],
    }


def coherence_plan_errors(
    label: str,
    plan: dict,
    targets: list[dict],
    expected_width: float,
    nested_contours: int,
    expected_source_rectangle: dict,
    expected_module: str,
) -> list[str]:
    """Validate one serialized source-field plan and all of its clip rectangles."""
    errors: list[str] = []
    coherence = plan.get("coherence", {})
    policy = plan.get("policy", {})
    if policy.get("coherence_policy") != "plan-once-then-clip" or coherence.get(
        "coherence_policy"
    ) != "plan-once-then-clip":
        errors.append(f"{label}: missing plan-once-then-clip coherence policy")
    source_id = coherence.get("source_field_id")
    if not isinstance(source_id, str) or not source_id:
        errors.append(f"{label}: missing source-field identity")
    if plan.get("region", {}).get("id") != source_id:
        errors.append(f"{label}: source plan region is not the source-field identity")
    source_rectangle = coherence.get("source_rectangle_mm")
    if not rectangles_close(source_rectangle, expected_source_rectangle):
        errors.append(f"{label}: wrong source rectangle")
    if not rectangles_close(plan.get("region", {}).get("rectangle_mm"), expected_source_rectangle):
        errors.append(f"{label}: source plan region rectangle mismatch")

    target_rectangles = {target.get("region_id"): target.get("rectangle_mm") for target in targets}
    clip_rows = coherence.get("clip_rectangles", [])
    clip_ids = [clip.get("id") for clip in clip_rows if isinstance(clip, dict)]
    if len(clip_ids) != len(set(clip_ids)) or set(clip_ids) != set(target_rectangles):
        errors.append(f"{label}: clip rectangles do not exactly match source targets")
    clips = {clip.get("id"): clip for clip in clip_rows if isinstance(clip, dict)}
    radius = expected_width / 2.0
    for clip_id, target_rectangle in target_rectangles.items():
        clip = clips.get(clip_id, {})
        rectangle = clip.get("rectangle_mm")
        inset = clip.get("inset_centerline_rectangle_mm")
        if not rectangles_close(rectangle, target_rectangle):
            errors.append(f"{label}: clip {clip_id} changed its allowed rectangle")
            continue
        expected_inset = {
            "min": [float(value) + radius for value in target_rectangle["min"]],
            "max": [float(value) - radius for value in target_rectangle["max"]],
        }
        if not rectangles_close(inset, expected_inset):
            errors.append(f"{label}: clip {clip_id} lacks groove-half-width inset")

    declared_parents = coherence.get("parent_path_ids", [])
    if not isinstance(declared_parents, list) or len(declared_parents) != len(set(declared_parents)):
        errors.append(f"{label}: invalid parent path ID metadata")
        declared_parent_set: set[str] = set()
    else:
        declared_parent_set = set(declared_parents)
    used_parents: set[str] = set()
    for path in plan.get("paths", []):
        parent = path.get("parent_path_id")
        clip_id = path.get("clip_rectangle_id")
        points = path.get("points_mm", [])
        if not isinstance(parent, str) or not parent:
            errors.append(f"{label}: clipped path lacks parent path ID")
        else:
            used_parents.add(parent)
        if clip_id not in clips:
            errors.append(f"{label}: clipped path references an unknown clip rectangle")
            continue
        inset = clips[clip_id].get("inset_centerline_rectangle_mm")
        if not rectangle_is_valid(inset):
            continue
        if not isinstance(points, list) or len(points) < 2 or not all(point_in_rectangle(point, inset) for point in points):
            errors.append(f"{label}: clipped centerline leaves its inset safe rectangle")
            continue
        if any(points[index] == points[index - 1] for index in range(1, len(points))):
            errors.append(f"{label}: clipped centerline contains duplicate/zero-length points")
        if polyline_length(points) + 1.0e-6 < expected_width:
            errors.append(f"{label}: clipped centerline is shorter than one groove width")

    for knot in plan.get("knots", []):
        clip_id = knot.get("clip_rectangle_id")
        contours = knot.get("contours", [])
        if plan.get("region", {}).get("surface") != "floor" or knot.get("surface") != "floor":
            errors.append(f"{label}: knot exists outside a floor source plan")
        if knot.get("module") != expected_module:
            errors.append(f"{label}: knot is not module-scoped")
        if clip_id not in clips or not rectangle_is_valid(clips[clip_id].get("inset_centerline_rectangle_mm")):
            errors.append(f"{label}: knot lacks one safe containing clip rectangle")
            continue
        if not isinstance(contours, list) or len(contours) != nested_contours:
            errors.append(f"{label}: partial knot contour set retained")
            continue
        inset = clips[clip_id]["inset_centerline_rectangle_mm"]
        for contour in contours:
            parent = contour.get("parent_path_id")
            points = contour.get("points_mm", [])
            if isinstance(parent, str) and parent:
                used_parents.add(parent)
            else:
                errors.append(f"{label}: knot contour lacks parent path ID")
            if (
                contour.get("closed") is not True
                or contour.get("clip_rectangle_id") != clip_id
                or not isinstance(points, list)
                or len(points) < 4
                or points[0] != points[-1]
                or not all(point_in_rectangle(point, inset) for point in points)
            ):
                errors.append(f"{label}: knot contour is partial, open, or outside its safe clip")
    if used_parents != declared_parent_set:
        errors.append(f"{label}: parent path ID metadata does not match retained geometry")
    return errors


def module_coherence_errors(module: str, groups: list[dict], params: dict, wood: dict) -> list[str]:
    errors: list[str] = []
    width = float(wood["grain"]["groove_width_mm"])
    nested_contours = int(wood["knots"]["nested_contours"])
    for group in groups:
        group_id = group.get("id")
        targets = group.get("targets", [])
        plans = group.get("plans", [])
        targets_by_source: dict[str, list[dict]] = {}
        for target in targets:
            targets_by_source.setdefault(str(target.get("source_id")), []).append(target)
        plans_by_source: dict[str, list[dict]] = {}
        for plan in plans:
            source_id = str(plan.get("coherence", {}).get("source_field_id"))
            plans_by_source.setdefault(source_id, []).append(plan)
        if set(targets_by_source) != set(plans_by_source):
            errors.append(f"{module}:{group_id}: source plan identities do not match targets")
        if any(len(source_plans) != 1 for source_plans in plans_by_source.values()):
            errors.append(f"{module}:{group_id}: source field was independently replanned")
        if group_id == "floor":
            if set(targets_by_source) != {ASSEMBLY_FLOOR_SOURCE_ID} or len(plans) != 1:
                errors.append(f"{module}: floor is not one assembly-global source plan")
        for source_id, source_targets in targets_by_source.items():
            signatures = {
                json.dumps(
                    {
                        "plane": target.get("plane"),
                        "long_axis": target.get("long_axis"),
                    },
                    sort_keys=True,
                )
                for target in source_targets
            }
            if len(signatures) != 1:
                errors.append(f"{module}:{group_id}:{source_id}: one source ID crosses physical faces")
            source_plans = plans_by_source.get(source_id, [])
            if len(source_plans) != 1:
                continue
            expected_rectangle = (
                assembly_floor_source_rectangle(params, wood)
                if group_id == "floor"
                else source_bounding_rectangle(source_targets)
            )
            errors.extend(
                coherence_plan_errors(
                    f"{module}:{group_id}:{source_id}",
                    source_plans[0],
                    source_targets,
                    width,
                    nested_contours,
                    expected_rectangle,
                    module,
                )
            )
    return errors


def validate_surface_scope_and_policy(reports: dict[str, dict], params: dict, wood: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    expected_groups = {"floor", "inner-wall", "top"}
    width = float(wood["grain"]["groove_width_mm"])
    expected_depth = {
        "floor": float(wood["grain"]["floor_depth_mm"]),
        "inner-wall": float(wood["grain"]["inner_wall_depth_mm"]),
        "top": float(wood["grain"]["top_depth_mm"]),
    }
    module_metrics = []
    floor_fields = []
    for module in MODULES:
        report = reports.get(module, {})
        plan = report.get("module", {}).get("surface_plan", {})
        groups = plan.get("groups", [])
        group_ids = {group.get("id") for group in groups}
        if group_ids != expected_groups:
            errors.append(f"{module}: floor/wall/top scope mismatch {sorted(str(item) for item in group_ids)}")
        errors.extend(module_coherence_errors(module, groups, params, wood))
        counts = {}
        for group in groups:
            group_id = group.get("id")
            targets = group.get("targets", [])
            plans = group.get("plans", [])
            counts[str(group_id)] = {"targets": len(targets), "plans": len(plans)}
            if not targets or not plans:
                errors.append(f"{module}: omitted {group_id} targets/plans")
            for texture_plan in plans:
                errors.extend(
                    texture_plan_errors(
                        f"{module}:{group_id}", texture_plan, width, expected_depth.get(group_id, -2)
                    )
                )
        if report.get("relief_loaded") is not False or report.get("watermark") != {"loaded": False, "applied": False}:
            errors.append(f"{module}: relief or watermark loaded/applied")
        floor_group = next((group for group in groups if group.get("id") == "floor"), {})
        floor_plans = floor_group.get("plans", [])
        if len(floor_plans) == 1:
            floor_fields.append({
                "module": module,
                "source_field_id": floor_plans[0].get("coherence", {}).get("source_field_id"),
                "source_rectangle_mm": floor_plans[0].get("coherence", {}).get("source_rectangle_mm"),
                "seed": floor_plans[0].get("seed"),
            })
        module_metrics.append({"module": module, "groups": counts})

    expected_floor_rectangle = assembly_floor_source_rectangle(params, wood)
    if len(floor_fields) != len(MODULES) or any(
        field["source_field_id"] != ASSEMBLY_FLOOR_SOURCE_ID
        or field["seed"] != wood.get("seed")
        or not rectangles_close(field["source_rectangle_mm"], expected_floor_rectangle)
        for field in floor_fields
    ):
        errors.append("module floors do not share one identical assembly-global source field/rectangle/seed")

    accessory = reports.get("accessories", {})
    comb_plan = accessory.get("comb_texture_plan", {})
    if accessory.get("relief_loaded") is not False or accessory.get("watermark") != {"loaded": False, "applied": False}:
        errors.append("R2 accessories: relief or watermark loaded/applied")
    if comb_plan.get("policy", {}).get("operation") != "engrave-only":
        errors.append("R2 comb: non-engrave policy")
    comb_texture_plans = comb_plan.get("comb", {}).get("texture_plans", [])
    if not comb_texture_plans:
        errors.append("R2 comb: top texture scope omitted")
    if not close(comb_plan.get("policy", {}).get("groove_width_mm", -1), width) or not close(
        comb_plan.get("policy", {}).get("top_depth_mm", -1), expected_depth["top"]
    ):
        errors.append("R2 comb: wrong top groove width/depth")
    for texture_plan in comb_texture_plans:
        errors.extend(texture_plan_errors("R2 comb:top", texture_plan, width, expected_depth["top"]))
    coupon = reports.get("wood-coupon", {})
    if coupon.get("relief_loaded") is not False or coupon.get("watermark") != {"loaded": False, "applied": False}:
        errors.append("R2 wood coupon: relief or watermark loaded/applied")
    coupon_plan = coupon.get("coupon", {}).get("plan", {})
    if coupon_plan.get("policy", {}).get("operation") != "engrave-only":
        errors.append("R2 wood coupon: non-engrave policy")
    expected_coupon_depths = {
        "plain-baseline": 0.0,
        "horizontal-depth-0.12": 0.12,
        "horizontal-depth-0.16": 0.16,
        "horizontal-depth-0.20": 0.20,
        "vertical-wall-depth-0.16": 0.16,
        "corner-phase-transition-depth-0.16": 0.16,
        "safe-top-cap-depth-0.20": 0.20,
    }
    coupon_samples = {sample.get("id"): sample.get("depth_mm") for sample in coupon_plan.get("samples", [])}
    if set(coupon_samples) != set(expected_coupon_depths) or any(
        not close(coupon_samples.get(sample_id, -1), depth)
        for sample_id, depth in expected_coupon_depths.items()
    ):
        errors.append("R2 wood coupon: wrong/missing depth sample set")
    coupon_texture_plans = coupon_plan.get("plans", [])
    expected_plan_ids = set(expected_coupon_depths) - {"plain-baseline"}
    actual_plan_ids = {plan.get("region", {}).get("id") for plan in coupon_texture_plans}
    if actual_plan_ids != expected_plan_ids:
        errors.append("R2 wood coupon: wrong/missing texture plan IDs")
    for texture_plan in coupon_texture_plans:
        plan_id = texture_plan.get("region", {}).get("id")
        errors.extend(
            texture_plan_errors(
                f"R2 wood coupon:{plan_id}", texture_plan, width, expected_coupon_depths.get(plan_id, -1)
            )
        )

    approved = {
        "groove_width_mm": 0.90,
        "floor_depth_mm": 0.20,
        "inner_wall_depth_mm": 0.16,
        "top_depth_mm": 0.20,
    }
    actual = {
        "groove_width_mm": width,
        "floor_depth_mm": expected_depth["floor"],
        "inner_wall_depth_mm": expected_depth["inner-wall"],
        "top_depth_mm": expected_depth["top"],
    }
    for key, expected in approved.items():
        if not close(actual[key], expected):
            errors.append(f"wood config {key}={actual[key]} differs from approved {expected}")
    if wood.get("surface_policy", {}).get("operation") != "engrave-only":
        errors.append("wood config policy is not engrave-only")
    floor_residual = float(params["organizer"]["floor_thickness"]) - actual["floor_depth_mm"]
    wall_residual = float(params["organizer"]["base_wall_thickness"]) - 2.0 * actual["inner_wall_depth_mm"]
    if floor_residual + 1.0e-9 < 2.40 or wall_residual + 1.0e-9 < 2.88:
        errors.append("residual floor/wall reserve is below the approved minimum")
    return errors, {
        "approved_and_configured_grooves_mm": {
            key: {"approved": approved[key], "configured": actual[key]} for key in approved
        },
        "residual_reserves_mm": {
            "floor": floor_residual,
            "minimum_floor": 2.40,
            "double_sided_wall": wall_residual,
            "minimum_double_sided_wall": 2.88,
        },
        "module_scope_counts": module_metrics,
        "assembly_global_floor_fields": floor_fields,
        "operation": wood.get("surface_policy", {}).get("operation"),
    }


def validate_package(root: Path, params: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    package_path = root / "output" / "DRAFT" / "DRAFT-R2-procedural-wood-assembly.3mf"
    report_path = root / "reports" / "three-mf-package-R2-procedural-wood-unmarked.json"
    if not package_path.is_file() or not report_path.is_file():
        return ["missing R2 DRAFT 3MF or package report"], {}
    report = read_json(report_path)
    if report.get("status") != "DRAFT" or report.get("validation_status") != "PASS":
        errors.append("R2 3MF report is non-DRAFT or failed")
    if report.get("revision") != params.get("model_revision") or report.get("route") != "r2-unmarked":
        errors.append("R2 3MF report revision/route mismatch")
    if report.get("file") != str(package_path.relative_to(root)) or report.get("file_bytes") != package_path.stat().st_size:
        errors.append("R2 3MF report file identity/size mismatch")
    if report.get("watermark") != {"loaded": False, "applied": False}:
        errors.append("R2 3MF report indicates a loaded/applied watermark")

    input_paths: list[Path] = []
    identities = report.get("identities", {})
    inputs = identities.get("inputs", {})
    scalar_expected = {
        "model_params": "config/model-params.json",
        "package_source": "src/package_3mf.py",
    }
    for key, expected in scalar_expected.items():
        identity = inputs.get(key, {})
        path = root / expected
        if identity.get("path") != expected or not path.is_file() or identity.get("sha256") != sha256_file(path):
            errors.append(f"R2 3MF {key} identity mismatch")
        else:
            input_paths.append(path)
    expected_reports = [f"reports/build-final-R2-{module}-procedural-wood-unmarked.json" for module in MODULES]
    expected_caches = [f"reports/mesh-cache/R2-{module}-procedural-wood-unmarked.meshbin" for module in MODULES]
    for key, expected_list in (("module_reports", expected_reports), ("mesh_caches", expected_caches)):
        values = inputs.get(key, [])
        if [item.get("path") for item in values] != expected_list:
            errors.append(f"R2 3MF {key} path list mismatch")
            continue
        for identity, expected in zip(values, expected_list, strict=True):
            path = root / expected
            if not path.is_file() or identity.get("sha256") != sha256_file(path):
                errors.append(f"R2 3MF stale/mismatched input {expected}")
            else:
                input_paths.append(path)
    artifact_identity = identities.get("artifacts", {}).get("three_mf", {})
    if artifact_identity.get("path") != str(package_path.relative_to(root)) or artifact_identity.get("sha256") != sha256_file(package_path):
        errors.append("R2 3MF SHA-256 mismatch")
    if input_paths and package_path.stat().st_mtime_ns < max(path.stat().st_mtime_ns for path in input_paths):
        errors.append("R2 3MF is stale relative to inputs")
    if report_path.stat().st_mtime_ns < package_path.stat().st_mtime_ns:
        errors.append("R2 3MF package report is stale")

    try:
        scan = scan_3mf(package_path)
    except Exception as exc:  # report malformed ZIP/XML as a deterministic failure
        errors.append(f"R2 3MF scan failed: {exc}")
        return errors, {"file": str(package_path.relative_to(root)), "file_bytes": package_path.stat().st_size}
    object_names = [item["name"] for item in scan["objects"]]
    object_ids = [item["id"] for item in scan["objects"]]
    build_ids = [item["object_id"] for item in scan["build_items"]]
    translations = {
        "driver-front": [0.0, 0.0, 0.0],
        "driver-back": [0.0, float(params["layout"]["depth_split"]), 0.0],
        "hardware-front": [float(params["layout"]["screwdriver_zone_width"]), 0.0, 0.0],
        "hardware-back": [
            float(params["layout"]["screwdriver_zone_width"]),
            float(params["layout"]["depth_split"]),
            0.0,
        ],
    }
    actual_translations = [item["transform"][9:12] for item in scan["build_items"]]
    expected_translations = [translations[module] for module in MODULES]
    metadata_text = " ".join(f"{key} {value}" for key, value in scan["metadata"].items()).lower()
    checks = {
        "crc": scan["crc_pass"],
        "core_namespace": scan["core_namespace_pass"],
        "four_named_objects": object_names == list(MODULES) and object_ids == [1, 2, 3, 4],
        "four_build_items": build_ids == [1, 2, 3, 4],
        "translation_only_build_transforms": scan["translation_only_transforms"],
        "translations_from_model_params": all(
            all(close(actual[axis], expected[axis]) for axis in range(3))
            for actual, expected in zip(actual_translations, expected_translations, strict=True)
        ),
        "exact_envelope": exact_envelope(scan["assembly_bounds_mm"]),
        "draft_unmarked_metadata": "draft" in metadata_text and "unmarked" in metadata_text,
    }
    for key, passed in checks.items():
        if not passed:
            errors.append(f"R2 3MF check failed: {key}")
    return errors, {
        "file": str(package_path.relative_to(root)),
        "file_bytes": package_path.stat().st_size,
        "sha256": sha256_file(package_path),
        "zip_entries": scan["zip_entries"],
        "crc_pass": scan["crc_pass"],
        "core_namespace_pass": scan["core_namespace_pass"],
        "object_count": len(scan["objects"]),
        "object_names": object_names,
        "build_item_count": len(scan["build_items"]),
        "build_translations_mm": actual_translations,
        "assembly_bounds_mm": scan["assembly_bounds_mm"],
        "checks": checks,
    }


def validate_project(root: Path = ROOT) -> dict:
    errors: list[str] = []
    params = read_json(root / "config" / "model-params.json")
    wood = read_json(root / "config" / "wood-texture-params.json")
    revision = str(params.get("model_revision", ""))
    if not revision.startswith(REVISION_PREFIX):
        errors.append(f"wrong active revision: {revision}")
    freshness_errors, reports = check_r2_build_freshness(root)
    errors.extend(freshness_errors)

    topology_errors, topology = validate_topology_reports(root)
    errors.extend(topology_errors)
    scope_errors, surface = validate_surface_scope_and_policy(reports, params, wood)
    errors.extend(scope_errors)

    module_rows = []
    for module in MODULES:
        report = reports.get(module, {})
        module_data = report.get("module", {})
        stl_path = root / module_data.get("file", f"missing-{module}")
        module_rows.append({
            "id": module,
            "triangles": int(module_data.get("triangles", 0)),
            "file_bytes": int(stl_path.stat().st_size) if stl_path.is_file() else int(module_data.get("file_bytes", 0)),
            "peak_rss_mib": float(report.get("process_memory", {}).get("max_rss_mib", math.inf)),
        })
        if module_data.get("file_bytes") != module_rows[-1]["file_bytes"]:
            errors.append(f"{module}: reported STL bytes mismatch")
        if stl_path.is_file() and stl_path.stat().st_size != 84 + 50 * module_rows[-1]["triangles"]:
            errors.append(f"{module}: binary STL triangle/file arithmetic mismatch")
    budgets = budget_metrics(module_rows, wood["resource_budget"])
    for key, passed in budgets["checks"].items():
        if not passed:
            errors.append(f"resource/reduction budget failed: {key}")

    package_errors, package = validate_package(root, params)
    errors.extend(package_errors)
    naming_checks = {
        "revision_is_r2": revision.startswith(REVISION_PREFIX),
        "all_stls_are_draft_named": all(name.startswith("DRAFT-R2-") and "FINAL" not in name.upper() for name in r2_stl_names()),
        "three_mf_is_draft_unmarked_named": package.get("file") == "output/DRAFT/DRAFT-R2-procedural-wood-assembly.3mf",
        "reports_are_draft_unmarked": all(
            report.get("status") == "DRAFT"
            and report.get("relief_loaded") is False
            and report.get("watermark") == {"loaded": False, "applied": False}
            for report in reports.values()
        ) if reports else False,
    }
    for key, passed in naming_checks.items():
        if not passed:
            errors.append(f"DRAFT/unmarked naming/status failed: {key}")

    checks = {
        "fresh_current_r2_identities": not freshness_errors,
        "exact_nine_stl_set": not topology_errors and topology.get("file_count") == 9,
        "topology": not topology_errors and all(item.get("pass") for item in topology.get("files", [])),
        "surface_scope_policy_depth_reserve": not scope_errors,
        "resource_and_reduction_budgets": all(budgets["checks"].values()),
        "three_mf": not package_errors and all(package.get("checks", {}).values()),
        "draft_unmarked_only": all(naming_checks.values()),
    }
    return {
        "status": "PASS" if not errors and all(checks.values()) else "FAIL",
        "artifact_status": "DRAFT",
        "revision": revision,
        "validator": "R2-procedural-wood-digital-validation-v1",
        "checks": checks,
        "checked_metrics": {
            "identity_and_freshness": {"status": "PASS" if not freshness_errors else "FAIL", "errors": freshness_errors},
            "stl_topology": topology,
            "surface_texture": surface,
            "budgets": budgets,
            "three_mf": package,
            "naming_status": naming_checks,
        },
        "external_tests": {
            "slicer": {
                "availability": "UNAVAILABLE",
                "status": "NOT_RUN",
                "run": False,
                "passed": None,
                "note": "No exact slicer execution is available in this digital build environment.",
            },
            "physical": {
                "availability": "UNAVAILABLE",
                "status": "NOT_RUN",
                "run": False,
                "passed": None,
                "note": "No physical coupon/module print or drawer fit test was run.",
            },
        },
        "errors": errors,
    }


def main() -> int:
    try:
        report = validate_project(ROOT)
    except Exception as exc:
        report = {
            "status": "FAIL",
            "artifact_status": "DRAFT",
            "revision": None,
            "validator": "R2-procedural-wood-digital-validation-v1",
            "checks": {},
            "checked_metrics": {},
            "external_tests": {
                "slicer": {"availability": "UNAVAILABLE", "status": "NOT_RUN", "run": False, "passed": None},
                "physical": {"availability": "UNAVAILABLE", "status": "NOT_RUN", "run": False, "passed": None},
            },
            "errors": [f"validator exception: {exc}"],
        }
    destination = ROOT / "reports" / "R2-procedural-wood-digital-validation.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
