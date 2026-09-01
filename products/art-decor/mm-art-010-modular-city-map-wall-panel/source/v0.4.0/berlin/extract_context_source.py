#!/usr/bin/env python3
"""Freeze the Berlin metropolitan line source and derive production layers.

The large Geofabrik transport PBF is an input, not a repository artifact.  The
bounded GeoPackage and the projected semantic GeoJSON layers are the immutable
project sources used by the 0.4.0 context example.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
DEFAULT_BOUNDARY = PRODUCT / "source-data" / "v0.3.0" / "berlin" / "boundary.geojson"

TRANSPORT_FILENAME = "germany-260830.osm.pbf"
TRANSPORT_BYTES = 4_828_999_134
TRANSPORT_MD5 = "67f6fe1597784796ebe0d36ac5fb990f"
TRANSPORT_SHA256 = "505860193092ce58cc8e4bb7f3b657b5f7de5f6d329d2b1bed44561cdfa7da55"
TRANSPORT_URL = "https://download.geofabrik.de/europe/germany/germany-260830.osm.pbf"
MIRROR_URL = "https://ftp5.gwdg.de/pub/misc/openstreetmap/download.geofabrik.de/germany-latest.osm.pbf"

# The extraction extent deliberately exceeds the selected context rectangle so
# buffered paths at the artwork edge cannot be truncated by source acquisition.
EXTRACTION_BBOX_WGS84 = [12.90, 52.28, 13.95, 52.73]
CONTEXT_BOUNDS_EPSG25833 = [
    357796.5793918899,
    5794991.9300077595,
    427990.7480931101,
    5841788.04247524,
]
CONTEXT_BOUNDS_WGS84 = [
    12.915122544462,
    52.286863833626,
    13.933841707589,
    52.721180774853,
]

SEMANTIC_FILTERS = {
    "roads-major.geojson": (
        "highway IN ('motorway','motorway_link','trunk','trunk_link',"
        "'primary','primary_link','secondary','secondary_link','tertiary',"
        "'tertiary_link','residential','unclassified','living_street')"
    ),
    "roads-accent.geojson": "highway IN ('motorway','motorway_link','trunk','trunk_link')",
    "rail.geojson": "railway IN ('rail','light_rail','subway','tram')",
    "waterways.geojson": "waterway IN ('river','canal')",
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def refuse_existing(paths: list[Path]) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise SystemExit("Refusing destructive overwrite of: " + ", ".join(existing))


def geojson_count(path: Path) -> int:
    return len(json.loads(path.read_text())["features"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transport_pbf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--boundary", type=Path, default=DEFAULT_BOUNDARY)
    parser.add_argument(
        "--reuse-snapshot",
        action="store_true",
        help="Reuse a completed metropolitan-lines-snapshot.gpkg after an identical recorded ogr2ogr run",
    )
    args = parser.parse_args()

    transport = args.transport_pbf.resolve()
    output = args.output_dir.resolve()
    boundary = args.boundary.resolve()
    if not transport.is_file() or not boundary.is_file():
        raise SystemExit("Transport PBF and approved Berlin boundary must exist")
    if transport.name != TRANSPORT_FILENAME:
        raise SystemExit(f"Expected frozen transport filename {TRANSPORT_FILENAME}")
    if transport.stat().st_size != TRANSPORT_BYTES:
        raise SystemExit("Transport byte count does not match the frozen source")
    if digest(transport, "md5") != TRANSPORT_MD5:
        raise SystemExit("Transport MD5 does not match the provider sidecar")
    if digest(transport, "sha256") != TRANSPORT_SHA256:
        raise SystemExit("Transport SHA-256 does not match the frozen source")

    output.mkdir(parents=True, exist_ok=True)
    snapshot = output / "metropolitan-lines-snapshot.gpkg"
    derived = [output / name for name in SEMANTIC_FILTERS]
    boundary_out = output / "boundary.geojson"
    manifest = output / "source-manifest.json"
    refuse_existing([boundary_out, manifest, *derived])
    if args.reuse_snapshot:
        if not snapshot.is_file() or snapshot.stat().st_size == 0:
            raise SystemExit("--reuse-snapshot requires a non-empty bounded GeoPackage")
    else:
        refuse_existing([snapshot])

    bbox = [str(value) for value in EXTRACTION_BBOX_WGS84]
    if not args.reuse_snapshot:
        run([
            "ogr2ogr", "-f", "GPKG", str(snapshot), str(transport), "lines",
            "-spat", *bbox,
            "-where", "highway IS NOT NULL OR railway IS NOT NULL OR waterway IS NOT NULL",
            "-nln", "transport_lines", "-nlt", "PROMOTE_TO_MULTI",
            "-lco", "SPATIAL_INDEX=YES",
        ])
    for filename, where in SEMANTIC_FILTERS.items():
        run([
            "ogr2ogr", "-f", "GeoJSON", str(output / filename), str(snapshot),
            "transport_lines", "-where", where, "-t_srs", "EPSG:25833",
            "-nlt", "PROMOTE_TO_MULTI", "-lco", "COORDINATE_PRECISION=6",
        ])
    run([
        "ogr2ogr", "-f", "GeoJSON", str(boundary_out), str(boundary),
        "-t_srs", "EPSG:25833", "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "COORDINATE_PRECISION=6",
    ])

    gdal_version = subprocess.run(
        ["ogr2ogr", "--version"], check=True, text=True, capture_output=True
    ).stdout.strip()
    artifacts = [snapshot, boundary_out, *derived]
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.4.0",
        "status": "PASS",
        "transport": {
            "filename": TRANSPORT_FILENAME,
            "bytes": TRANSPORT_BYTES,
            "md5": TRANSPORT_MD5,
            "sha256": TRANSPORT_SHA256,
            "provider_url": TRANSPORT_URL,
            "retrieval_mirror_url": MIRROR_URL,
            "retrieved": "2026-09-01",
        },
        "source_crs": "EPSG:4326",
        "working_crs": "EPSG:25833",
        "extraction_bbox_wgs84": EXTRACTION_BBOX_WGS84,
        "selected_context_bounds_wgs84": CONTEXT_BOUNDS_WGS84,
        "selected_context_bounds_epsg25833": CONTEXT_BOUNDS_EPSG25833,
        "coverage_check": {
            "method": "selected context bbox must be strictly contained by the transport extraction bbox",
            "pass": (
                EXTRACTION_BBOX_WGS84[0] < CONTEXT_BOUNDS_WGS84[0]
                and EXTRACTION_BBOX_WGS84[1] < CONTEXT_BOUNDS_WGS84[1]
                and EXTRACTION_BBOX_WGS84[2] > CONTEXT_BOUNDS_WGS84[2]
                and EXTRACTION_BBOX_WGS84[3] > CONTEXT_BOUNDS_WGS84[3]
            ),
        },
        "gdal_version": gdal_version,
        "snapshot_reused_after_identical_command": args.reuse_snapshot,
        "semantic_filters": SEMANTIC_FILTERS,
        "feature_counts": {path.name: geojson_count(path) for path in [boundary_out, *derived]},
        "artifacts": [
            {
                "path": str(path.relative_to(PRODUCT)),
                "bytes": path.stat().st_size,
                "sha256": digest(path, "sha256"),
            }
            for path in artifacts
        ],
        "attribution": "Map data © OpenStreetMap contributors · ODbL 1.0; extract distributed by Geofabrik GmbH and retrieved through the GWDG mirror.",
    }
    if not report["coverage_check"]["pass"] or any(value == 0 for value in report["feature_counts"].values()):
        report["status"] = "FAIL"
    manifest.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] != "PASS":
        raise SystemExit("Source derivation failed closed; inspect source-manifest.json")
    print(json.dumps({"status": "PASS", "manifest": str(manifest), "counts": report["feature_counts"]}))


if __name__ == "__main__":
    main()
