#!/usr/bin/env python3
"""Validate preservation, cylindrical wall reserve, floor, and bed fit."""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARAMETERS_PATH = ROOT / "parameters" / "geometry-r0.1.2.json"

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


def transform_source(triangles: np.ndarray, parameters: dict) -> np.ndarray:
    transformed = np.empty_like(triangles)
    scale = parameters["source"]["scale"]
    transformed[..., 0] = triangles[..., 0] * scale
    transformed[..., 1] = -triangles[..., 2] * scale
    transformed[..., 2] = (
        triangles[..., 1] - parameters["source"]["sourceMinY"]
    ) * scale
    return transformed


def segment_distance(points: np.ndarray, first: np.ndarray, second: np.ndarray) -> np.ndarray:
    direction = second - first
    denominator = np.einsum("...i,...i->...", direction, direction)
    fraction = np.einsum("...i,...i->...", points - first, direction) / np.maximum(denominator, 1e-30)
    fraction = np.clip(fraction, 0.0, 1.0)
    closest = first + fraction[..., None] * direction
    return np.linalg.norm(points - closest, axis=-1)


def point_triangle_distance(points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """Distances for points shaped (n,k,3) and triangles shaped (n,k,3,3)."""
    first = triangles[..., 0, :]
    second = triangles[..., 1, :]
    third = triangles[..., 2, :]
    edge0 = second - first
    edge1 = third - first
    relative = points - first
    dot00 = np.einsum("...i,...i->...", edge0, edge0)
    dot01 = np.einsum("...i,...i->...", edge0, edge1)
    dot11 = np.einsum("...i,...i->...", edge1, edge1)
    dot20 = np.einsum("...i,...i->...", relative, edge0)
    dot21 = np.einsum("...i,...i->...", relative, edge1)
    denominator = dot00 * dot11 - dot01 * dot01
    bary_v = (dot11 * dot20 - dot01 * dot21) / np.maximum(denominator, 1e-30)
    bary_w = (dot00 * dot21 - dot01 * dot20) / np.maximum(denominator, 1e-30)
    bary_u = 1.0 - bary_v - bary_w
    inside = (bary_u >= -1e-8) & (bary_v >= -1e-8) & (bary_w >= -1e-8)

    normal = np.cross(edge0, edge1)
    normal_length = np.linalg.norm(normal, axis=-1)
    plane_distance = np.abs(np.einsum("...i,...i->...", relative, normal)) / np.maximum(normal_length, 1e-30)
    edge_distance = np.minimum.reduce(
        [
            segment_distance(points, first, second),
            segment_distance(points, second, third),
            segment_distance(points, third, first),
        ]
    )
    return np.where(inside, plane_distance, edge_distance)


def nearest_surface_distances(points: np.ndarray, triangles: np.ndarray, candidates: int = 512) -> np.ndarray:
    centroids = triangles.mean(axis=1)
    tree = cKDTree(centroids)
    k = min(candidates, len(triangles))
    output = np.empty(len(points), dtype=np.float64)
    for start in range(0, len(points), 400):
        chunk = points[start : start + 400]
        indices = tree.query(chunk, k=k, workers=-1)[1]
        if k == 1:
            indices = indices[:, None]
        candidate_triangles = triangles[indices]
        expanded_points = np.broadcast_to(chunk[:, None, :], candidate_triangles.shape[:-2] + (3,))
        distances = point_triangle_distance(expanded_points, candidate_triangles)
        output[start : start + len(chunk)] = distances.min(axis=1)
    return output


def entry_roi(points: np.ndarray, parameters: dict) -> np.ndarray:
    tower = parameters["tower"]
    entry = parameters["entry"]
    if entry.get("mode") in {"angled-lined-channel", "angled-round-lined-channel"}:
        start = np.asarray(entry["clearStart"], dtype=float)
        end = np.asarray(entry["clearEnd"], dtype=float)
        if entry["mode"] == "angled-round-lined-channel":
            radius = entry["linerOuterDiameter"] / 2 + 3.0
        else:
            radius = max(entry["linerOuterWidth"], entry["linerOuterHeight"]) / 2 + 3.0
        return segment_distance(points, start, end) <= radius
    return (
        (np.abs(points[:, 0] - tower["axisX"]) <= 22.0)
        & (points[:, 1] >= -5.0)
        & (points[:, 1] <= 65.0)
        & (points[:, 2] >= 142.0)
        & (points[:, 2] <= 195.0)
    )


def exit_roi(points: np.ndarray, parameters: dict) -> np.ndarray:
    tower = parameters["tower"]
    exit_parameters = parameters["exit"]
    if exit_parameters.get("mode") == "rounded-lined-channel":
        outer_top = exit_parameters["linerShoulderZ"] + exit_parameters["linerArchRadius"]
        return (
            (np.abs(points[:, 0] - tower["axisX"]) <= exit_parameters["linerOuterWidth"] / 2 + 3.0)
            & (points[:, 1] >= exit_parameters["clearOuterY"] - 3.0)
            & (points[:, 1] <= exit_parameters["clearInnerY"] + 3.0)
            & (points[:, 2] >= exit_parameters["linerBottomZ"] - 3.0)
            & (points[:, 2] <= outer_top + 3.0)
        )
    return (
        (np.abs(points[:, 0] - tower["axisX"]) <= 24.0)
        & (points[:, 1] >= -43.0)
        & (points[:, 1] <= 36.0)
        & (points[:, 2] >= 20.0)
        & (points[:, 2] <= 62.0)
    )


def internal_roi(points: np.ndarray, parameters: dict) -> np.ndarray:
    tower = parameters["tower"]
    radius = np.hypot(points[:, 0] - tower["axisX"], points[:, 1] - tower["axisY"])
    return (
        (radius <= tower["cavityRadius"] + 2.0)
        & (points[:, 2] >= -0.1)
        & (points[:, 2] <= tower["cavityTopZ"] + 2.5)
    )


def watermark_roi(points: np.ndarray, parameters: dict) -> np.ndarray:
    watermark = parameters["watermark"]
    width, height = watermark["actualEnvelope"]
    return (
        (np.abs(points[:, 0] - watermark["centerX"]) <= width / 2 + 1.0)
        & (np.abs(points[:, 1] - watermark["centerY"]) <= height / 2 + 1.0)
        & (points[:, 2] <= 1.0)
    )


def stats(values: np.ndarray) -> dict[str, float | int]:
    return {
        "samples": int(len(values)),
        "medianMm": float(np.median(values)),
        "p95Mm": float(np.percentile(values, 95)),
        "p99Mm": float(np.percentile(values, 99)),
        "maximumMm": float(values.max(initial=0.0)),
    }


def triangle_plane_segments(triangles: np.ndarray, height: float) -> np.ndarray:
    minimum = triangles[..., 2].min(axis=1)
    maximum = triangles[..., 2].max(axis=1)
    active = triangles[(minimum <= height) & (maximum >= height) & (maximum - minimum > 1e-9)]
    segments: list[list[np.ndarray]] = []
    for triangle in active:
        intersections: list[np.ndarray] = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            a = triangle[first]
            b = triangle[second]
            da = a[2] - height
            db = b[2] - height
            if abs(da) <= 1e-9:
                intersections.append(a[:2])
            if da * db < 0:
                fraction = da / (da - db)
                intersections.append((a + fraction * (b - a))[:2])
        unique: list[np.ndarray] = []
        for point in intersections:
            if not any(np.linalg.norm(point - existing) <= 1e-7 for existing in unique):
                unique.append(point)
        if len(unique) >= 2:
            segments.append([unique[0], unique[1]])
    return np.asarray(segments, dtype=np.float64)


def radial_hits(segments: np.ndarray, origin: np.ndarray, angles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    starts = segments[:, 0]
    vectors = segments[:, 1] - starts
    relative = starts - origin
    distances = np.full(len(angles), np.nan)
    hit_points = np.full((len(angles), 2), np.nan)
    for index, angle in enumerate(angles):
        direction = np.array([math.cos(angle), math.sin(angle)])
        denominator = direction[0] * vectors[:, 1] - direction[1] * vectors[:, 0]
        valid_denominator = np.abs(denominator) > 1e-12
        ray_distance = np.full(len(segments), np.inf)
        segment_fraction = np.full(len(segments), np.inf)
        ray_distance[valid_denominator] = (
            relative[valid_denominator, 0] * vectors[valid_denominator, 1]
            - relative[valid_denominator, 1] * vectors[valid_denominator, 0]
        ) / denominator[valid_denominator]
        segment_fraction[valid_denominator] = (
            relative[valid_denominator, 0] * direction[1]
            - relative[valid_denominator, 1] * direction[0]
        ) / denominator[valid_denominator]
        valid = (ray_distance >= 0) & (segment_fraction >= -1e-8) & (segment_fraction <= 1 + 1e-8)
        if np.any(valid):
            nearest = np.min(ray_distance[valid])
            distances[index] = nearest
            hit_points[index] = origin + nearest * direction
    return distances, hit_points


def wall_reserve(source: np.ndarray, parameters: dict) -> dict[str, object]:
    tower = parameters["tower"]
    origin = np.array([tower["axisX"], tower["axisY"]])
    angles = np.linspace(0, 2 * math.pi, 360, endpoint=False)
    records = []
    all_reserves = []
    heights = np.arange(math.ceil(tower["cavityBottomZ"]), tower["cavityTopZ"] + 1e-6, 1.0)
    for height in heights:
        segments = triangle_plane_segments(source, float(height))
        distances, points = radial_hits(segments, origin, angles)
        valid = np.isfinite(distances)
        xyz = np.column_stack([points, np.full(len(points), height)])
        valid &= ~entry_roi(xyz, parameters)
        valid &= ~exit_roi(xyz, parameters)
        reserves = distances[valid] - tower["cavityRadius"]
        if len(reserves):
            all_reserves.append(reserves)
            records.append({
                "zMm": float(height),
                "minimumMm": float(reserves.min()),
                "p05Mm": float(np.percentile(reserves, 5)),
            })
    combined = np.concatenate(all_reserves)
    minimum_index = int(np.argmin([record["minimumMm"] for record in records]))
    return {
        "samples": int(len(combined)),
        "minimumMm": float(combined.min()),
        "p01Mm": float(np.percentile(combined, 1)),
        "p05Mm": float(np.percentile(combined, 5)),
        "hardMinimumMm": tower["hardMinimumWall"],
        "passed": float(combined.min()) >= tower["hardMinimumWall"],
        "minimumStation": records[minimum_index],
        "stations": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=DEFAULT_PARAMETERS_PATH)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parameters_path = args.parameters.resolve()
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    source_path = (parameters_path.parent / parameters["source"]["path"]).resolve()
    result_path = args.result or (
        ROOT / "result" / f"polygonal-dice-tower-DRAFT-no-watermark-{parameters['revision']}.stl"
    )
    report_path = args.report or (
        ROOT / "reports" / f"geometry-validation-{parameters['revision']}.json"
    )
    source = transform_source(read_stl(source_path), parameters)
    result = read_stl(result_path)
    entry_liner = read_stl(
        ROOT
        / "inserts"
        / f"rear-upper-entry-channel-liner-{parameters['revision']}.stl"
    )
    exit_liner = read_stl(
        ROOT
        / "inserts"
        / f"front-exit-channel-liner-{parameters['revision']}.stl"
    )
    source_centroids = source.mean(axis=1)
    result_centroids = result.mean(axis=1)

    source_mask = ~(
        entry_roi(source_centroids, parameters)
        | exit_roi(source_centroids, parameters)
        | watermark_roi(source_centroids, parameters)
    )
    result_mask = ~(
        entry_roi(result_centroids, parameters)
        | exit_roi(result_centroids, parameters)
        | internal_roi(result_centroids, parameters)
        | watermark_roi(result_centroids, parameters)
    )
    source_to_result = nearest_surface_distances(source_centroids[source_mask], result)
    result_to_source = nearest_surface_distances(result_centroids[result_mask], source)

    horn_mask = (
        (source_centroids[:, 2] >= 194.0)
        & (source_centroids[:, 1] <= 35.0)
    )
    rear_wall_mask = (
        (source_centroids[:, 1] >= parameters["tower"]["axisY"] + 20.0)
        & (source_centroids[:, 2] >= 35.0)
        & (source_centroids[:, 2] <= 160.0)
        & ~entry_roi(source_centroids, parameters)
        & ~exit_roi(source_centroids, parameters)
    )
    horn_distances = nearest_surface_distances(source_centroids[horn_mask], result)
    rear_wall_distances = nearest_surface_distances(source_centroids[rear_wall_mask], result)

    floor_minimum = (
        min(parameters["floorRamp"]["frontTopZ"], parameters["floorRamp"]["rearTopZ"])
        - float(source[..., 2].min())
    )
    result_bounds_min = result.reshape(-1, 3).min(axis=0)
    result_bounds_max = result.reshape(-1, 3).max(axis=0)
    result_extents = result_bounds_max - result_bounds_min
    bed = np.asarray(parameters["manufacturing"].get("buildVolume", [420, 420, 500]), dtype=float)
    if "buildVolume" not in parameters["manufacturing"]:
        bed = np.array([420.0, 420.0, 500.0])

    preservation = {
        "sourceToResult": stats(source_to_result),
        "resultToSource": stats(result_to_source),
        "limitsMm": {"p95": 0.20, "maximum": 1.00},
    }
    preservation["passed"] = (
        preservation["sourceToResult"]["p95Mm"] <= 0.20
        and preservation["sourceToResult"]["maximumMm"] <= 1.00
        and preservation["resultToSource"]["p95Mm"] <= 0.20
        and preservation["resultToSource"]["maximumMm"] <= 1.00
    )
    wall = wall_reserve(source, parameters)
    entry = parameters["entry"]
    exit_parameters = parameters["exit"]
    if entry.get("mode") == "angled-round-lined-channel":
        entry_wall = (entry["linerOuterDiameter"] - entry["clearDiameter"]) / 2
    elif entry.get("mode") == "angled-lined-channel":
        entry_wall = min(
            entry["linerOuterWidth"] - entry["clearWidth"],
            entry["linerOuterHeight"] - entry["clearHeight"],
        ) / 2
    else:
        entry_wall = None
    if exit_parameters.get("mode") == "rounded-lined-channel":
        exit_walls = {
            "sideMm": (exit_parameters["linerOuterWidth"] - exit_parameters["clearWidth"]) / 2,
            "crownMm": exit_parameters["linerArchRadius"] - exit_parameters["archRadius"],
            "floorMm": exit_parameters["bottomZ"] - exit_parameters["linerBottomZ"],
        }
    else:
        exit_walls = None

    entry_direction = np.asarray(entry["linerStart"], dtype=float) - np.asarray(
        entry["linerEnd"], dtype=float
    )
    entry_direction /= np.linalg.norm(entry_direction)
    entry_reference = np.asarray(entry["estimatedExteriorIntersectionCenter"], dtype=float)
    entry_projection = float(
        np.max((entry_liner.reshape(-1, 3) - entry_reference) @ entry_direction)
    )
    exit_direction = np.array([0.0, -1.0, 0.0])
    exit_reference = np.array(
        [
            parameters["tower"]["axisX"],
            exit_parameters["estimatedExteriorWallFaceY"],
            exit_parameters["channelCenterZ"],
        ]
    )
    exit_projection = float(
        np.max((exit_liner.reshape(-1, 3) - exit_reference) @ exit_direction)
    )
    channel_projections = {
        "entry": {
            "targetMm": entry["visibleProjectionMm"],
            "exportedLinerMm": entry_projection,
            "toleranceMm": 0.02,
            "passed": abs(entry_projection - entry["visibleProjectionMm"]) <= 0.02,
        },
        "exit": {
            "targetMm": exit_parameters["channelLengthOutsideTowerApprox"],
            "exportedLinerMm": exit_projection,
            "toleranceMm": 0.02,
            "passed": abs(
                exit_projection - exit_parameters["channelLengthOutsideTowerApprox"]
            )
            <= 0.02,
        },
    }
    channel_projections["passed"] = bool(
        channel_projections["entry"]["passed"]
        and channel_projections["exit"]["passed"]
    )
    report = {
        "geometryRevision": parameters["revision"],
        "result": str(result_path),
        "preservationOutsideApprovedRoi": preservation,
        "protectedFeatures": {
            "roofHorn": {
                **stats(horn_distances),
                "maximumAllowedMm": 0.05,
                "passed": bool(len(horn_distances) and horn_distances.max() <= 0.05),
            },
            "rearWallOutsideEntryRoi": {
                **stats(rear_wall_distances),
                "maximumAllowedMm": 0.05,
                "passed": bool(len(rear_wall_distances) and rear_wall_distances.max() <= 0.05),
            },
        },
        "cylindricalWallReserve": wall,
        "linedChannels": {
            "entryNominalWallMm": entry_wall,
            "exitNominalWallsMm": exit_walls,
            "hardMinimumMm": parameters["tower"]["hardMinimumWall"],
            "passed": bool(
                entry_wall is not None
                and entry_wall >= parameters["tower"]["hardMinimumWall"]
                and exit_walls is not None
                and min(exit_walls.values()) >= parameters["tower"]["hardMinimumWall"]
            ),
        },
        "visibleChannelProjections": channel_projections,
        "floor": {
            "minimumResidualMm": floor_minimum,
            "hardMinimumMm": parameters["tower"]["hardMinimumWall"],
            "passed": floor_minimum >= parameters["tower"]["hardMinimumWall"],
        },
        "bedFit": {
            "resultBoundsMinMm": result_bounds_min.tolist(),
            "resultBoundsMaxMm": result_bounds_max.tolist(),
            "resultExtentsMm": result_extents.tolist(),
            "buildVolumeMm": bed.tolist(),
            "passed": bool(np.all(result_extents <= bed + 1e-6)),
        },
        "manufacturing": {
            "baffleUndersideDegrees": parameters["baffles"]["ribUndersideDegrees"],
            "maximumDesignedBridgeSpanMm": 32.0,
            "trappedSupportRequired": False,
            "bridgeCouponRequiredBeforeFullPrint": True,
        },
    }
    report["passed"] = all(
        [
            preservation["passed"],
            report["protectedFeatures"]["roofHorn"]["passed"],
            report["protectedFeatures"]["rearWallOutsideEntryRoi"]["passed"],
            wall["passed"],
            report["linedChannels"]["passed"],
            report["visibleChannelProjections"]["passed"],
            report["floor"]["passed"],
            report["bedFit"]["passed"],
        ]
    )
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": report["passed"],
        "preservation": preservation,
        "protectedFeatures": report["protectedFeatures"],
        "wall": {key: value for key, value in wall.items() if key != "stations"},
        "linedChannels": report["linedChannels"],
        "visibleChannelProjections": report["visibleChannelProjections"],
        "floor": report["floor"],
        "bedFit": report["bedFit"],
    }, indent=2))
    if not report["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
