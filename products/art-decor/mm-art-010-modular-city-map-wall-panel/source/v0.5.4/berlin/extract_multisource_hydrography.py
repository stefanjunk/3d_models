#!/usr/bin/env python3
"""Freeze revision 0.5.4 map layers with three-source hydrography evidence.

OSM remains the detailed all-context map source.  The official Berlin
Gewässerkarte is unioned into the production water geometry inside Berlin.
BKG DLM250 hydrography is retained as an independent nationwide regression
reference for named lakes and the Havel corridor.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS = PRODUCT / "source-data" / "v0.5.3" / "berlin"
OUTPUT = PRODUCT / "source-data" / "v0.5.4" / "berlin"
PREVIOUS_EXTRACTOR = PRODUCT / "source" / "v0.5.3" / "berlin" / "extract_production_layers.py"
BOUNDS_EPSG25833 = [357796.5793918899, 5794991.9300077595, 427990.7480931101, 5841788.04247524]
BOUNDS_WGS84 = [12.915122544462, 52.286863833626, 13.933841707589, 52.721180774853]
BERLIN_WFS = "https://gdi.berlin.de/services/wfs/gewaesserkarte"
BKG_WFS = "https://sgx.geodatenzentrum.de/wfs_dlm250_inspire"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(path: Path, feature_count: int | None = None) -> dict:
    result = {"path": str(path.relative_to(PRODUCT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
    if feature_count is not None:
        result["feature_count"] = feature_count
    return result


def read_features(path: Path) -> list[dict]:
    return json.loads(path.read_text())["features"]


def write_geojson(path: Path, name: str, features: list[dict]) -> None:
    path.write_text(json.dumps({
        "type": "FeatureCollection",
        "name": name,
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::25833"}},
        "features": features,
    }, ensure_ascii=False, separators=(",", ":")) + "\n")


def copy_verified_previous(name: str, previous_manifest: dict) -> None:
    source = PREVIOUS / name
    expected = previous_manifest["artifacts"][name]["sha256"]
    if sha256(source) != expected:
        raise RuntimeError(f"revision 0.5.3 source hash changed: {name}")
    destination = OUTPUT / name
    destination.write_bytes(source.read_bytes())


def ogr_wfs(layer: str, destination: Path) -> list[str]:
    command = [
        "ogr2ogr", "-f", "GeoJSON", str(destination),
        f"WFS:{BERLIN_WFS}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities",
        layer,
        "-t_srs", "EPSG:25833",
        "-spat", *(str(value) for value in BOUNDS_EPSG25833),
        "-spat_srs", "EPSG:25833",
        "-lco", "COORDINATE_PRECISION=3",
    ]
    subprocess.run(command, check=True)
    return command


def bkg_request(type_name: str, raw_path: Path, destination: Path) -> tuple[str, list[str]]:
    query = urllib.parse.urlencode({
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "typeNames": type_name,
        "outputFormat": "application/geo+json",
        "srsName": "EPSG:4326",
        "BBOX": ",".join(str(value) for value in BOUNDS_WGS84) + ",EPSG:4326",
        "COUNT": "5000",
    })
    url = f"{BKG_WFS}?{query}"
    with urllib.request.urlopen(url, timeout=120) as response:
        raw_path.write_bytes(response.read())
    command = [
        "ogr2ogr", "-f", "GeoJSON", str(destination), str(raw_path),
        "-s_srs", "EPSG:4326", "-t_srs", "EPSG:25833",
        "-lco", "COORDINATE_PRECISION=3",
    ]
    subprocess.run(command, check=True)
    return url, command


def source_name(properties: dict) -> str:
    try:
        return properties["geographicalName"]["GeographicalName"]["spelling"]["SpellingOfName"]["text"]
    except (KeyError, TypeError):
        return ""


def polygons(features: list[dict]):
    for feature in features:
        geometry = shape(feature["geometry"])
        if geometry.geom_type == "Polygon":
            yield geometry
        elif geometry.geom_type == "MultiPolygon":
            yield from geometry.geoms
        elif hasattr(geometry, "geoms"):
            for child in geometry.geoms:
                if child.geom_type == "Polygon":
                    yield child


def lines(features: list[dict]):
    for feature in features:
        geometry = shape(feature["geometry"])
        if geometry.geom_type in {"LineString", "MultiLineString"}:
            yield geometry


def coverage(reference, candidate) -> dict:
    intersection = reference.intersection(candidate).area
    return {
        "reference_area_m2": reference.area,
        "candidate_area_m2": candidate.area,
        "intersection_area_m2": intersection,
        "reference_covered_fraction": intersection / reference.area if reference.area else 0.0,
        "candidate_covered_fraction": intersection / candidate.area if candidate.area else 0.0,
        "hausdorff_distance_m": reference.hausdorff_distance(candidate),
    }


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("refusing to overwrite existing revision 0.5.4 source evidence")
    previous_manifest_path = PREVIOUS / "source-manifest.json"
    previous_manifest = json.loads(previous_manifest_path.read_text())
    if previous_manifest.get("status") != "PASS":
        raise RuntimeError("revision 0.5.3 OSM source manifest is not PASS")
    OUTPUT.mkdir(parents=True)

    for name in ("boundary.geojson", "roads-major.geojson", "sbahn-routes.geojson", "ubahn-routes.geojson"):
        copy_verified_previous(name, previous_manifest)
    for source_name_file, target in (
        ("water-areas.geojson", "water-areas-osm.geojson"),
        ("water-lines.geojson", "water-lines-osm.geojson"),
    ):
        source = PREVIOUS / source_name_file
        if sha256(source) != previous_manifest["artifacts"][source_name_file]["sha256"]:
            raise RuntimeError(f"revision 0.5.3 source hash changed: {source_name_file}")
        (OUTPUT / target).write_bytes(source.read_bytes())

    commands: dict[str, object] = {}
    berlin_area = OUTPUT / "water-areas-berlin-official.geojson"
    berlin_line = OUTPUT / "water-lines-berlin-official.geojson"
    commands[berlin_area.name] = ogr_wfs("gewaesserkarte:e_gew_gewaesser_fl", berlin_area)
    commands[berlin_line.name] = ogr_wfs("gewaesserkarte:gew_nur_li", berlin_line)

    with tempfile.TemporaryDirectory(prefix="mm-art-010-v054-bkg-") as temporary:
        temp = Path(temporary)
        bkg_standing = OUTPUT / "water-standing-bkg-reference.geojson"
        bkg_watercourse = OUTPUT / "watercourse-bkg-reference.geojson"
        standing_url, standing_command = bkg_request("hy-p:StandingWater", temp / "standing.json", bkg_standing)
        watercourse_url, watercourse_command = bkg_request("hy-p:Watercourse", temp / "watercourse.json", bkg_watercourse)
        commands[bkg_standing.name] = {"request_url": standing_url, "transform": standing_command}
        commands[bkg_watercourse.name] = {"request_url": watercourse_url, "transform": watercourse_command}

    osm_areas = read_features(OUTPUT / "water-areas-osm.geojson")
    berlin_areas = read_features(berlin_area)
    union_area = unary_union([*polygons(osm_areas), *polygons(berlin_areas)]).buffer(0)
    union_polygons = list(union_area.geoms) if union_area.geom_type == "MultiPolygon" else [union_area]
    final_area_features = [{
        "type": "Feature",
        "properties": {"derived_id": f"water-union-{index:05d}", "sources": "OSM+Berlin_Gewaesserkarte"},
        "geometry": mapping(geometry),
    } for index, geometry in enumerate(union_polygons, start=1) if not geometry.is_empty]
    write_geojson(OUTPUT / "water-areas.geojson", "water-areas-production-union", final_area_features)

    osm_lines = read_features(OUTPUT / "water-lines-osm.geojson")
    berlin_lines = read_features(berlin_line)
    union_line = unary_union([*lines(osm_lines), *lines(berlin_lines)])
    write_geojson(OUTPUT / "water-lines.geojson", "water-lines-production-union", [{
        "type": "Feature",
        "properties": {"derived_id": "water-line-union-00001", "sources": "OSM+Berlin_Gewaesserkarte"},
        "geometry": mapping(union_line),
    }])

    bkg_standing_features = read_features(OUTPUT / "water-standing-bkg-reference.geojson")
    bkg_watercourse_features = read_features(OUTPUT / "watercourse-bkg-reference.geojson")
    osm_tegeler = unary_union([
        shape(feature["geometry"]) for feature in osm_areas
        if str(feature["properties"].get("osm_id")) == "451908" or feature["properties"].get("name") == "Tegeler See"
    ]).buffer(0)
    berlin_tegeler = unary_union([
        shape(feature["geometry"]) for feature in berlin_areas
        if feature["properties"].get("gewname") == "Tegeler See"
    ]).buffer(0)
    bkg_tegeler = unary_union([
        shape(feature["geometry"]) for feature in bkg_standing_features
        if source_name(feature["properties"]) == "Tegeler See"
    ]).buffer(0)
    berlin_havel = unary_union([
        shape(feature["geometry"]) for feature in berlin_areas
        if "Havel" in (feature["properties"].get("gewname") or "")
    ]).buffer(0)
    bkg_havel = unary_union([
        shape(feature["geometry"]) for feature in bkg_watercourse_features
        if source_name(feature["properties"]) == "Havel" and shape(feature["geometry"]).geom_type in {"Polygon", "MultiPolygon"}
    ]).buffer(0)
    osm_union = unary_union(list(polygons(osm_areas))).buffer(0)
    production_union = unary_union(list(polygons(final_area_features))).buffer(0)

    checks = {
        "tegeler_see_official_vs_osm": coverage(berlin_tegeler, osm_tegeler),
        "tegeler_see_official_vs_bkg": coverage(berlin_tegeler, bkg_tegeler),
        "tegeler_see_official_vs_production": coverage(berlin_tegeler, production_union),
        "havel_official_vs_osm": coverage(berlin_havel, osm_union),
        "havel_official_vs_bkg": coverage(berlin_havel, bkg_havel),
        "havel_official_vs_production": coverage(berlin_havel, production_union),
    }
    required = {
        "tegeler_osm_fraction_min": 0.90,
        "tegeler_bkg_fraction_min": 0.85,
        "tegeler_production_fraction_min": 0.99,
        "havel_osm_fraction_min": 0.90,
        "havel_bkg_fraction_min": 0.75,
        "havel_production_fraction_min": 0.99,
    }
    passed = (
        checks["tegeler_see_official_vs_osm"]["reference_covered_fraction"] >= required["tegeler_osm_fraction_min"]
        and checks["tegeler_see_official_vs_bkg"]["reference_covered_fraction"] >= required["tegeler_bkg_fraction_min"]
        and checks["tegeler_see_official_vs_production"]["reference_covered_fraction"] >= required["tegeler_production_fraction_min"]
        and checks["havel_official_vs_osm"]["reference_covered_fraction"] >= required["havel_osm_fraction_min"]
        and checks["havel_official_vs_bkg"]["reference_covered_fraction"] >= required["havel_bkg_fraction_min"]
        and checks["havel_official_vs_production"]["reference_covered_fraction"] >= required["havel_production_fraction_min"]
    )

    geojson_names = [path.name for path in OUTPUT.glob("*.geojson")]
    artifacts = {name: artifact(OUTPUT / name, len(read_features(OUTPUT / name))) for name in sorted(geojson_names)}
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.4",
        "status": "PASS" if passed else "FAIL",
        "retrieved": "2026-09-04",
        "working_crs": "EPSG:25833",
        "selected_context_bounds_epsg25833": BOUNDS_EPSG25833,
        "selected_context_bounds_wgs84": BOUNDS_WGS84,
        "source_roles": {
            "OpenStreetMap_Geofabrik_2026-08-30": "detailed primary map and context hydrography inherited by verified hash from revision 0.5.3",
            "Berlin_Gewaesserkarte_WFS": "official detailed Berlin water-area and water-line authority unioned into production geometry",
            "BKG_DLM250_INSPIRE_WFS": "independent nationwide named-water and Havel continuity reference; not used to replace detailed shorelines",
        },
        "source_endpoints": {
            "berlin_metadata": "https://gdi.berlin.de/geonetwork/srv/api/records/353f1716-9b5c-3a1d-9528-8c49e4f47aee",
            "berlin_wfs": BERLIN_WFS,
            "bkg_product": "https://gdz.bkg.bund.de/index.php/default/inspire-wfs-digital-landscape-model-1-250-000-wfs-dlm250-inspire.html",
            "bkg_wfs": BKG_WFS,
            "osm_manifest": str(previous_manifest_path.relative_to(PRODUCT)),
            "osm_manifest_sha256": sha256(previous_manifest_path),
        },
        "artifacts": artifacts,
        "commands": commands,
        "cross_source_checks": checks,
        "acceptance_thresholds": required,
        "named_regression_fixtures": {
            "tegeler_see": {
                "official_name": "Tegeler See",
                "osm_relation_id": "451908",
                "official_area_m2": berlin_tegeler.area,
                "bounds_m": list(berlin_tegeler.bounds),
                "required_final_front_coverage_fraction": 0.90,
            },
            "havel_corridor": {
                "official_feature_names": ["Havel", "Alte Havel", "Havelschlenke"],
                "official_area_m2": berlin_havel.area,
                "bounds_m": list(berlin_havel.bounds),
                "required_final_front_coverage_fraction": 0.90,
                "required_ordered_corridor_sections": ["northern_boundary", "spandauer_see", "pichelssee", "wannsee", "glienicker_lake"],
            },
        },
        "semantic_contract": {
            "water": "production water is the union of OSM and the official Berlin Gewässerkarte; BKG DLM250 independently gates named coverage and corridor continuity",
            "protected_geometry": "only exact functional support footprints and logged local bridges may interrupt water; generic logo or oversized mounting keep-outs are prohibited",
        },
        "attribution": [
            "Map data © OpenStreetMap contributors · ODbL 1.0; extracts distributed by Geofabrik GmbH.",
            "Geoportal Berlin / Gewässerkarte · Datenlizenz Deutschland – Zero – Version 2.0.",
            "© GeoBasis-DE / BKG 2026; modified for regression analysis.",
        ],
    }
    manifest_path = OUTPUT / "source-manifest.json"
    manifest_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": report["status"], "manifest": str(manifest_path), "checks": checks}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
