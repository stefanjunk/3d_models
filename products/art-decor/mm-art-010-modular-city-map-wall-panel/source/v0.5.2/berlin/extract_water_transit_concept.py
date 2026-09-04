#!/usr/bin/env python3
"""Extract concept-only Berlin water and S/U route layers from the frozen PBF.

The output is gate evidence for revision 0.5.2.  Production regeneration must
repeat the same semantic queries against a source that covers the complete
context-outline extent.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from shapely.geometry import shape


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PBF = PRODUCT / "source-data" / "v0.3.0" / "berlin" / "berlin-snapshot.osm.pbf"
OUTPUT = PRODUCT / "source-data" / "v0.5.2" / "berlin"
MANIFEST = OUTPUT / "concept-source-manifest.json"

QUERIES = {
    "water-areas.geojson": {
        "layer": "multipolygons",
        "where": (
            "natural = 'water' OR landuse IN ('reservoir','basin') OR "
            "other_tags LIKE '%\"waterway\"=>\"riverbank\"%'"
        ),
        "select": "osm_id,name,natural,landuse,other_tags",
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_features(path: Path) -> list[dict]:
    return json.loads(path.read_text())["features"]


def main() -> None:
    if not PBF.is_file():
        raise FileNotFoundError(PBF)
    if MANIFEST.exists() or any((OUTPUT / name).exists() for name in QUERIES):
        raise FileExistsError("Refusing to overwrite concept source evidence")
    OUTPUT.mkdir(parents=True, exist_ok=True)

    artifacts = {}
    for name, query in QUERIES.items():
        path = OUTPUT / name
        command = [
            "ogr2ogr",
            "-f",
            "GeoJSON",
            str(path),
            str(PBF),
            query["layer"],
            "-t_srs",
            "EPSG:25833",
            "-where",
            query["where"],
            "-select",
            query["select"],
            "-lco",
            "COORDINATE_PRECISION=3",
        ]
        subprocess.run(command, check=True)
        features = load_features(path)
        if not features:
            raise RuntimeError(f"Required concept layer is empty: {name}")
        artifacts[name] = {
            "sha256": sha256(path),
            "feature_count": len(features),
            "query": query,
        }

    water_features = load_features(OUTPUT / "water-areas.geojson")
    tegeler = [
        feature
        for feature in water_features
        if feature.get("properties", {}).get("osm_id") == "451908"
        or feature.get("properties", {}).get("name") == "Tegeler See"
    ]
    if len(tegeler) != 1:
        raise RuntimeError(f"Expected exactly one Tegeler See feature, got {len(tegeler)}")
    tegeler_geometry = shape(tegeler[0]["geometry"])
    if tegeler_geometry.is_empty or tegeler_geometry.area <= 0:
        raise RuntimeError("Tegeler See geometry is empty")

    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.2-concept-source-r1",
        "status": "PASS_CONCEPT_SOURCE_ONLY",
        "source": {
            "path": str(PBF.relative_to(PRODUCT)),
            "sha256": sha256(PBF),
            "crs": "EPSG:4326",
        },
        "output_crs": "EPSG:25833",
        "artifacts": artifacts,
        "named_regression_fixtures": {
            "tegeler_see": {
                "osm_relation_id": "451908",
                "feature_count": 1,
                "area_m2": tegeler_geometry.area,
                "bounds_m": list(tegeler_geometry.bounds),
                "required_representation": "through-part negative geometry",
            }
        },
        "semantic_contract": {
            "water": "all mapped water areas plus river/canal/stream centerlines become negative geometry",
            "sky_blue": "S-Bahn and U-Bahn route relations; context boundary and site marker retain their approved tool-4 assignment",
            "midnight": "street network including motorway and trunk classes",
        },
        "limitations": [
            "concept evidence only",
            "the local PBF does not cover the complete 12-percent context-outline margin",
            "production extraction requires reacquisition and hashing of the recorded context-complete source",
            "opposite route directions are visually overlaid here and must be dissolved before production buffering",
        ],
    }
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
