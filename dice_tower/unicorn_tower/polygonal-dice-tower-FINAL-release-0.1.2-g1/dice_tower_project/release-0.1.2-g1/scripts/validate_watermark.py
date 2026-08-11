#!/usr/bin/env python3
"""Validate the actual JSI-WM-001-R1 recess in the exported candidate STL."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

from matplotlib.path import Path as PlotPath
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "just-innovation-watermark" / "manifest.yaml"
DEFAULT_PARAMETERS = ROOT / "parameters" / "geometry-r0.1.2.json"

STL_DTYPE = np.dtype(
    [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]
)


def read_stl(path: Path) -> np.ndarray:
    with path.open("rb") as handle:
        handle.read(80)
        count = struct.unpack("<I", handle.read(4))[0]
        records = np.fromfile(handle, dtype=STL_DTYPE, count=count)
    if len(records) != count or path.stat().st_size != 84 + count * 50:
        raise ValueError(f"Invalid binary STL: {path}")
    return records["vertices"].astype(np.float64)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_volume(triangles: np.ndarray) -> float:
    return float(
        np.einsum(
            "ij,ij->i",
            triangles[:, 0],
            np.cross(triangles[:, 1], triangles[:, 2]),
        ).sum()
        / 6.0
    )


def parse_dxf_polylines(path: Path) -> list[np.ndarray]:
    lines = path.read_text(encoding="utf-8").splitlines()
    polygons: list[np.ndarray] = []
    polygon: list[list[float]] | None = None
    vertex: dict[str, float] | None = None

    def finish_vertex() -> None:
        nonlocal vertex
        if polygon is not None and vertex is not None and "x" in vertex and "y" in vertex:
            polygon.append([vertex["x"], vertex["y"]])
        vertex = None

    def finish_polygon() -> None:
        nonlocal polygon
        finish_vertex()
        if polygon is not None and len(polygon) >= 3:
            polygons.append(np.asarray(polygon, dtype=float))
        polygon = None

    for index in range(0, len(lines) - 1, 2):
        code = lines[index].strip()
        value = lines[index + 1].strip()
        if code == "0":
            finish_vertex()
            if value == "POLYLINE":
                finish_polygon()
                polygon = []
            elif value == "VERTEX":
                vertex = {}
            elif value == "SEQEND":
                finish_polygon()
        elif vertex is not None and code == "10":
            vertex["x"] = float(value)
        elif vertex is not None and code == "20":
            vertex["y"] = float(value)
    finish_polygon()
    return polygons


def placed_polygons(parameters: dict) -> list[np.ndarray]:
    watermark = parameters["watermark"]
    dxf = (ROOT / "parameters" / watermark["dxf"]).resolve()
    polygons = parse_dxf_polylines(dxf)
    transformed = []
    angle = math.radians(watermark["rotationDegrees"])
    rotation = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
    for polygon in polygons:
        current = polygon.copy()
        if watermark["mirrorWorldXForReadableUnderside"]:
            current[:, 0] *= -1
        current *= watermark["uniformScale"]
        current = current @ rotation.T
        transformed.append(current)
    all_points = np.concatenate(transformed)
    centre = (all_points.min(axis=0) + all_points.max(axis=0)) / 2
    translation = np.array([watermark["centerX"], watermark["centerY"]]) - centre
    return [polygon + translation for polygon in transformed]


def sample_mark_points(polygons: list[np.ndarray], spacing: float = 0.28) -> np.ndarray:
    points = np.concatenate(polygons)
    xs = np.arange(points[:, 0].min() + spacing / 2, points[:, 0].max(), spacing)
    ys = np.arange(points[:, 1].min() + spacing / 2, points[:, 1].max(), spacing)
    grid_x, grid_y = np.meshgrid(xs, ys)
    samples = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    inside = np.zeros(len(samples), dtype=bool)
    for polygon in polygons:
        inside ^= PlotPath(polygon, closed=True).contains_points(samples)
    return samples[inside]


def vertical_intersections(point: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    xy = triangles[..., :2]
    bounds_min = xy.min(axis=1)
    bounds_max = xy.max(axis=1)
    candidate = triangles[
        (bounds_min[:, 0] <= point[0])
        & (bounds_max[:, 0] >= point[0])
        & (bounds_min[:, 1] <= point[1])
        & (bounds_max[:, 1] >= point[1])
    ]
    if not len(candidate):
        return np.empty(0)
    first = candidate[:, 0, :2]
    edge0 = candidate[:, 1, :2] - first
    edge1 = candidate[:, 2, :2] - first
    relative = point - first
    denominator = edge0[:, 0] * edge1[:, 1] - edge0[:, 1] * edge1[:, 0]
    valid = np.abs(denominator) > 1e-12
    u = np.zeros(len(candidate))
    v = np.zeros(len(candidate))
    u[valid] = (relative[valid, 0] * edge1[valid, 1] - relative[valid, 1] * edge1[valid, 0]) / denominator[valid]
    v[valid] = (edge0[valid, 0] * relative[valid, 1] - edge0[valid, 1] * relative[valid, 0]) / denominator[valid]
    inside = valid & (u >= -1e-8) & (v >= -1e-8) & (u + v <= 1 + 1e-8)
    selected = candidate[inside]
    u = u[inside]
    v = v[inside]
    return selected[:, 0, 2] + u * (selected[:, 1, 2] - selected[:, 0, 2]) + v * (selected[:, 2, 2] - selected[:, 0, 2])


def horizontal_local_segments(triangles: np.ndarray, height: float, bounds: np.ndarray) -> np.ndarray:
    segments = []
    for triangle in triangles:
        if triangle[:, 2].min() > height or triangle[:, 2].max() < height:
            continue
        points = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            a = triangle[first]
            b = triangle[second]
            da = a[2] - height
            db = b[2] - height
            if abs(da) < 1e-9:
                points.append(a[:2])
            if da * db < 0:
                fraction = da / (da - db)
                points.append((a + fraction * (b - a))[:2])
        unique = []
        for point in points:
            if not any(np.linalg.norm(point - existing) < 1e-7 for existing in unique):
                unique.append(point)
        if len(unique) >= 2:
            midpoint = (unique[0] + unique[1]) / 2
            if np.all(midpoint >= bounds[0]) and np.all(midpoint <= bounds[1]):
                segments.append(np.asarray([unique[0], unique[1]]))
    return np.asarray(segments)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=DEFAULT_PARAMETERS)
    parser.add_argument("--plain", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--topology", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parameters_path = args.parameters.resolve()
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    revision = parameters["revision"]
    plain_path = (args.plain or (
        ROOT / "result" / f"polygonal-dice-tower-DRAFT-no-watermark-{revision}.stl"
    )).resolve()
    candidate_path = (args.candidate or (
        ROOT / "result" / f"polygonal-dice-tower-DRAFT-watermarked-{revision}.stl"
    )).resolve()
    topology_path = (args.topology or (
        ROOT / "reports" / f"topology-DRAFT-watermarked-{revision}.json"
    )).resolve()
    report_path = (args.report or (
        ROOT / "reports" / f"watermark-validation-{revision}.json"
    )).resolve()
    watermark = parameters["watermark"]
    plain = read_stl(plain_path)
    candidate = read_stl(candidate_path)
    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    polygons = placed_polygons(parameters)
    all_points = np.concatenate(polygons)
    envelope = all_points.max(axis=0) - all_points.min(axis=0)
    samples = sample_mark_points(polygons)

    underside = []
    top = []
    for point in samples:
        intersections = vertical_intersections(point, plain)
        if len(intersections) >= 2:
            underside.append(float(intersections.min()))
            top.append(float(intersections.max()))
    underside_values = np.asarray(underside)
    top_values = np.asarray(top)
    cutter_top = watermark["localUndersideZ"] + watermark["depth"]
    actual_depths = cutter_top - underside_values
    residual_walls = top_values - cutter_top

    local_bounds = np.asarray([all_points.min(axis=0) - 1, all_points.max(axis=0) + 1])
    layers = {}
    for height in (0.10, 0.30, 0.50):
        segments = horizontal_local_segments(candidate, height, local_bounds)
        layers[f"z{height:.2f}"] = {
            "segmentCount": int(len(segments)),
            "totalContourLengthMm": float(np.linalg.norm(segments[:, 1] - segments[:, 0], axis=1).sum()) if len(segments) else 0.0,
        }

    scaled_minimum_stroke = manifest["reference_process"]["minimum_stroke_mm"] * watermark["uniformScale"]
    scaled_minimum_gap = manifest["reference_process"]["minimum_clear_gap_mm"] * watermark["uniformScale"]
    plain_bounds_min = plain.reshape(-1, 3).min(axis=0)
    candidate_bounds_min = candidate.reshape(-1, 3).min(axis=0)
    report = {
        "geometryRevision": revision,
        "candidateFile": str(candidate_path),
        "candidateSha256": sha256(candidate_path),
        "assetId": watermark["assetId"],
        "variant": watermark["variant"],
        "operation": "recessed",
        "placement": {
            "surface": "print-bed-facing underside / forecourt",
            "centerMm": [watermark["centerX"], watermark["centerY"], watermark["localUndersideZ"]],
            "actualEnvelopeMm": envelope.tolist(),
            "uniformScale": watermark["uniformScale"],
            "rotationDegrees": watermark["rotationDegrees"],
            "mirroredWorldX": watermark["mirrorWorldXForReadableUnderside"],
            "minimumProductEdgeClearanceMm": watermark["minimumProductEdgeClearance"],
            "minimumFeatureClearanceMm": watermark["minimumFeatureClearance"],
        },
        "depth": {
            "nominalMm": watermark["depth"],
            "actualMinimumMm": float(actual_depths.min()),
            "actualMaximumMm": float(actual_depths.max()),
            "actualMeanMm": float(actual_depths.mean()),
            "sampleCount": int(len(actual_depths)),
        },
        "hostWall": {
            "minimumBeforeMm": float((top_values - underside_values).min()),
            "minimumAfterMm": float(residual_walls.min()),
            "requiredMinimumMm": parameters["tower"]["hardMinimumWall"],
        },
        "bedDatum": {
            "plainMinimumZMm": float(plain_bounds_min[2]),
            "candidateMinimumZMm": float(candidate_bounds_min[2]),
            "unchanged": abs(float(plain_bounds_min[2] - candidate_bounds_min[2])) <= 1e-9,
            "protrusionBelowOriginal": False,
        },
        "processFeatures": {
            "scaledMinimumStrokeMm": scaled_minimum_stroke,
            "scaledMinimumGapMm": scaled_minimum_gap,
            "nozzleMm": parameters["manufacturing"]["nozzle"],
            "layerHeightMm": parameters["manufacturing"]["layerHeight"],
        },
        "layerSections": layers,
        "topology": {
            "watertight": topology["watertightByEdgeIncidence"],
            "components": topology["connectedFaceComponents"],
            "boundaryEdges": topology["boundaryEdges"],
            "overconnectedEdges": topology["overconnectedEdges"],
            "positiveVolume": topology["positiveVolume"],
        },
        "removedVolumeMm3": signed_volume(plain) - signed_volume(candidate),
        "reviewAsset": f"reports/watermark-release-review-{revision}.jpg",
        "gcodeSlicerPreviewStillRequiredBeforePrinting": True,
    }
    checks = {
        "assetIdentity": watermark["assetId"] == manifest["asset_id"],
        "envelope": bool(np.allclose(envelope, watermark["actualEnvelope"], atol=0.01)),
        "depth": float(actual_depths.min()) >= 0.39 and float(actual_depths.max()) <= 0.42,
        "residualWall": float(residual_walls.min()) >= parameters["tower"]["hardMinimumWall"],
        "bedDatum": report["bedDatum"]["unchanged"],
        "processFeatures": scaled_minimum_stroke >= 2 * parameters["manufacturing"]["nozzle"] and scaled_minimum_gap >= 0.6,
        "firstTwoLayers": layers["z0.10"]["segmentCount"] > 0 and layers["z0.30"]["segmentCount"] > 0,
        "recessEndsAboveLayer2": layers["z0.50"]["segmentCount"] == 0,
        "topology": topology["watertightByEdgeIncidence"] and topology["connectedFaceComponents"] == 1 and topology["positiveVolume"],
    }
    report["checks"] = checks
    report["passed"] = all(checks.values())
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
