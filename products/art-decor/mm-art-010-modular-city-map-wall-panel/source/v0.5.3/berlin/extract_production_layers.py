#!/usr/bin/env python3
"""Freeze bounded MM-ART-010 Berlin/Brandenburg production layers.

The transport PBFs stay outside Git. This extractor verifies their immutable
hashes, runs the approved OSM filters against both same-date Geofabrik extracts,
deduplicates overlapping features and writes only the bounded EPSG:25833
derivatives required by the product.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from shapely.geometry import shape


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
OUTPUT = PRODUCT / "source-data" / "v0.5.3" / "berlin"
EXTRACTION_BBOX = [12.9, 52.28, 13.95, 52.73]
SELECTED_CONTEXT_BOUNDS_WGS84 = [
    12.915122544462,
    52.286863833626,
    13.933841707589,
    52.721180774853,
]
SELECTED_CONTEXT_BOUNDS_EPSG25833 = [
    357796.5793918899,
    5794991.9300077595,
    427990.7480931101,
    5841788.04247524,
]

TRANSPORTS = {
    "berlin": {
        "filename": "berlin-260830.osm.pbf",
        "bytes": 99132753,
        "md5": "f8abc6fea7f28079476afcb115171076",
        "sha256": "44878bac7391c7d1e9d86e583a0cbd9713a69d164ac47ad1e4ab7e7d374d407c",
        "provider_url": "https://download.geofabrik.de/europe/germany/berlin-260830.osm.pbf",
    },
    "brandenburg": {
        "filename": "brandenburg-260830.osm.pbf",
        "bytes": 299230738,
        "md5": "6d6087f52dedb66b6b99ba7b1c191ccf",
        "sha256": "4f7321ad35a111060ff9d3fe3e388063336f94421583295ce1ed029a281e89af",
        "provider_url": "https://download.geofabrik.de/europe/germany/brandenburg-260830.osm.pbf",
    },
}

QUERIES = {
    "boundary.geojson": {
        "layer": "multipolygons",
        "where": "boundary = 'administrative' AND admin_level = '4' AND name = 'Berlin'",
        "select": "osm_id,name,boundary,admin_level",
    },
    "roads-major.geojson": {
        "layer": "lines",
        "where": (
            "highway IN ('motorway','motorway_link','trunk','trunk_link',"
            "'primary','primary_link','secondary','secondary_link','tertiary',"
            "'tertiary_link','residential','unclassified','living_street')"
        ),
        "select": "osm_id,name,highway",
    },
    "water-areas.geojson": {
        "layer": "multipolygons",
        "where": (
            "natural = 'water' OR landuse IN ('reservoir','basin') OR "
            "other_tags LIKE '%\"waterway\"=>\"riverbank\"%'"
        ),
        "select": "osm_id,osm_way_id,name,natural,landuse,other_tags",
    },
    "water-lines.geojson": {
        "layer": "lines",
        "where": "waterway IN ('river','canal','stream')",
        "select": "osm_id,name,waterway",
    },
    "sbahn-routes.geojson": {
        "layer": "multilinestrings",
        "where": (
            "other_tags LIKE '%\"route\"=>\"light_rail\"%' AND "
            "other_tags LIKE '%\"network:metro\"=>\"s-bahn\"%'"
        ),
        "select": "osm_id,name,other_tags",
    },
    "ubahn-routes.geojson": {
        "layer": "multilinestrings",
        "where": (
            "other_tags LIKE '%\"route\"=>\"subway\"%' AND "
            "other_tags LIKE '%\"network:metro\"=>\"u-bahn\"%'"
        ),
        "select": "osm_id,name,other_tags",
    },
}


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def verify_transport(label: str, path: Path) -> dict:
    expected = TRANSPORTS[label]
    actual = {
        "bytes": path.stat().st_size,
        "md5": digest(path, "md5"),
        "sha256": digest(path, "sha256"),
    }
    for key, value in actual.items():
        if value != expected[key]:
            raise RuntimeError(f"{label} transport {key} mismatch: {value} != {expected[key]}")
    return {**expected, "path_supplied": str(path.resolve()), "verified": True}


def extract_one(source: Path, query: dict, destination: Path) -> list[str]:
    command = [
        "ogr2ogr",
        "-f", "GeoJSON",
        str(destination),
        str(source),
        query["layer"],
        "-spat", *(str(value) for value in EXTRACTION_BBOX),
        "-t_srs", "EPSG:25833",
        "-where", query["where"],
        "-select", query["select"],
        "-lco", "COORDINATE_PRECISION=3",
    ]
    subprocess.run(command, check=True)
    return command


def feature_key(feature: dict) -> tuple[str, str, str]:
    properties = feature.get("properties", {})
    identity = str(properties.get("osm_id") or properties.get("osm_way_id") or "")
    geometry = json.dumps(feature.get("geometry"), sort_keys=True, separators=(",", ":"))
    return identity, hashlib.sha256(geometry.encode()).hexdigest(), feature.get("geometry", {}).get("type", "")


def merge_geojson(paths: list[Path], destination: Path) -> tuple[int, int]:
    features: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    duplicate_count = 0
    for path in paths:
        data = json.loads(path.read_text())
        for feature in data.get("features", []):
            if not feature.get("geometry"):
                continue
            key = feature_key(feature)
            if key in seen:
                duplicate_count += 1
                continue
            seen.add(key)
            features.append(feature)
    document = {
        "type": "FeatureCollection",
        "name": destination.stem,
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::25833"}},
        "features": features,
    }
    destination.write_text(json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n")
    return len(features), duplicate_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--berlin-pbf", type=Path, required=True)
    parser.add_argument("--brandenburg-pbf", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = OUTPUT / "source-manifest.json"
    if manifest_path.exists() or any((OUTPUT / name).exists() for name in QUERIES):
        raise FileExistsError("refusing to overwrite existing revision 0.5.3 source evidence")
    transports = {
        "berlin": verify_transport("berlin", args.berlin_pbf),
        "brandenburg": verify_transport("brandenburg", args.brandenburg_pbf),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)

    commands: dict[str, list[list[str]]] = {}
    artifacts: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="mm-art-010-v053-") as temporary:
        temp = Path(temporary)
        for name, query in QUERIES.items():
            parts: list[Path] = []
            commands[name] = []
            for label, source in (("berlin", args.berlin_pbf), ("brandenburg", args.brandenburg_pbf)):
                part = temp / f"{label}-{name}"
                commands[name].append(extract_one(source, query, part))
                parts.append(part)
            output = OUTPUT / name
            feature_count, duplicates_removed = merge_geojson(parts, output)
            if feature_count == 0:
                raise RuntimeError(f"required production layer is empty: {name}")
            artifacts[name] = {
                "bytes": output.stat().st_size,
                "sha256": digest(output, "sha256"),
                "feature_count": feature_count,
                "duplicates_removed": duplicates_removed,
                "query": query,
            }

    boundary_features = json.loads((OUTPUT / "boundary.geojson").read_text())["features"]
    if len(boundary_features) != 1 or boundary_features[0]["properties"].get("osm_id") != "62422":
        raise RuntimeError("expected exactly Berlin boundary relation 62422")

    water_features = json.loads((OUTPUT / "water-areas.geojson").read_text())["features"]
    tegeler = [
        feature for feature in water_features
        if feature.get("properties", {}).get("osm_id") == "451908"
        or feature.get("properties", {}).get("name") == "Tegeler See"
    ]
    if len(tegeler) != 1:
        raise RuntimeError(f"expected exactly one Tegeler See feature, got {len(tegeler)}")
    tegeler_geometry = shape(tegeler[0]["geometry"])
    if tegeler_geometry.is_empty or tegeler_geometry.area <= 0:
        raise RuntimeError("Tegeler See geometry is empty")

    strict_coverage = all(
        outer_low < inner_low and inner_high < outer_high
        for outer_low, inner_low, inner_high, outer_high in zip(
            EXTRACTION_BBOX[0:2],
            SELECTED_CONTEXT_BOUNDS_WGS84[0:2],
            SELECTED_CONTEXT_BOUNDS_WGS84[2:4],
            EXTRACTION_BBOX[2:4],
        )
    )
    if not strict_coverage:
        raise RuntimeError("selected context bounds are not strictly inside extraction bbox")

    gdal_version = subprocess.run(
        ["ogr2ogr", "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.3",
        "status": "PASS",
        "retrieved": "2026-09-04",
        "source_crs": "EPSG:4326",
        "working_crs": "EPSG:25833",
        "transports": transports,
        "extraction_bbox_wgs84": EXTRACTION_BBOX,
        "selected_context_bounds_wgs84": SELECTED_CONTEXT_BOUNDS_WGS84,
        "selected_context_bounds_epsg25833": SELECTED_CONTEXT_BOUNDS_EPSG25833,
        "coverage_check": {
            "method": "selected context bbox is strictly contained by the combined Berlin/Brandenburg extraction bbox",
            "pass": strict_coverage,
        },
        "gdal_version": gdal_version,
        "artifacts": artifacts,
        "commands": commands,
        "named_regression_fixtures": {
            "berlin_boundary": {"osm_relation_id": "62422", "feature_count": 1},
            "tegeler_see": {
                "osm_relation_id": "451908",
                "feature_count": 1,
                "area_m2": tegeler_geometry.area,
                "bounds_m": list(tegeler_geometry.bounds),
                "required_representation": "through-part negative geometry",
            },
        },
        "semantic_contract": {
            "water": "all water polygons and river/canal/stream lines are negative geometry subject only to logged topology bridges and protected keep-outs",
            "tool_3": "all selected street classes including motorway and trunk",
            "tool_4": "S-Bahn and U-Bahn route relations plus context boundary and site marker; no independent motorway accent",
        },
        "attribution": "Map data © OpenStreetMap contributors · ODbL 1.0; extracts distributed by Geofabrik GmbH.",
    }
    manifest_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "status": report["status"],
        "manifest": str(manifest_path),
        "feature_counts": {name: data["feature_count"] for name, data in artifacts.items()},
        "tegeler_see_area_m2": tegeler_geometry.area,
    }, indent=2))


if __name__ == "__main__":
    main()
