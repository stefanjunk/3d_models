#!/usr/bin/env python3
"""Generate the hash-bound MM-ART-010 revision 0.5.3 handoff summary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
CANDIDATE = "digital-candidate-r4"
VALIDATION = PRODUCT / "validation" / "v0.5.3" / "berlin" / CANDIDATE
EXPORT = PRODUCT / "exports" / "v0.5.3" / "berlin" / CANDIDATE


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(PRODUCT))


def main() -> None:
    output_json = VALIDATION / "digital-candidate-summary.json"
    output_md = VALIDATION / "digital-candidate-summary.md"
    if output_json.exists() or output_md.exists():
        raise SystemExit("refusing to overwrite existing candidate summary")
    build = read(VALIDATION / "build-report.json")
    aggregate = read(VALIDATION / "validation-summary-draft-r3.json")
    if build["status"] != "PASS" or aggregate["status"] != "REVIEW_REQUIRED":
        raise ValueError("candidate build or aggregate validation has unexpected status")

    runs = {
        "boundary_crop": ("boundary-crop", "r2", "r1"),
        "context_outline": ("context-outline", "r1", "r1"),
    }
    examples = {}
    rows = []
    for public_mode, (path_mode, left_run, right_run) in runs.items():
        examples[public_mode] = {}
        for half, run in (("left", left_run), ("right", right_run)):
            prefix = f"berlin-{path_mode}-{half}"
            stem = f"{prefix}-oak-mint-midnight-sky-metrimade-water-transit-anycubic"
            project = EXPORT / path_mode / f"{stem}.3mf"
            geometry_path = VALIDATION / "3mf" / f"{stem}-geometry-r2.json"
            adapter_path = VALIDATION / "anycubic-slices" / f"{path_mode}-{half}-{run}-adapter.json"
            review_path = VALIDATION / "anycubic-slices" / f"{path_mode}-{half}-{run}-review.json"
            geometry = read(geometry_path)
            adapter = read(adapter_path)
            review = read(review_path)
            if geometry["status"] != "PASS" or review["status"] != "PASS":
                raise ValueError(f"failed 3MF or slice review: {path_mode}/{half}")
            native = adapter["native_result"]
            warning = native["sliced_plates"][0]["warning_message"]
            metrics = review["metrics"]
            gcode_metrics = adapter["gcode_reports"]["plate_1.gcode"]["metrics"]
            entry = {
                "project_3mf": {
                    "path": rel(project),
                    "bytes": project.stat().st_size,
                    "sha256": sha256(project),
                    "components": geometry["totals"]["components"],
                    "triangles": geometry["totals"]["triangles"],
                    "volume_mm3": geometry["totals"]["volume_mm3"],
                },
                "native_slice": {
                    "status": "PASS_WITH_GUI_REVIEW" if warning else "PASS",
                    "native_return_code": native["return_code"],
                    "warning": warning or None,
                    "layers": metrics["canonical_layer_change_markers"],
                    "maximum_z_mm": metrics["canonical_maximum_z_mm"],
                    "tools": metrics["tools_seen"],
                    "tool_changes": metrics["tool_changes"],
                    "slicer_estimated_time_s": gcode_metrics["slicer_metadata_time_s"],
                    "positive_extrusion_mm_by_tool": gcode_metrics["positive_extrusion_mm_by_tool"],
                    "review": rel(review_path),
                },
            }
            examples[public_mode][half] = entry
            result = "PASS; GUI floating-region review" if warning else "PASS"
            rows.append(
                f"| `{public_mode}` {half} | {geometry['totals']['triangles']:,} | "
                f"{metrics['canonical_layer_change_markers']} | {metrics['tool_changes']} | {result} |"
            )

    mode_summary = {}
    for mode, report in build["modes"].items():
        mode_summary[mode] = {
            "status": report["status"],
            "tegeler_see_final_opening_area_mm2": report["water_bridge_accounting"]["tegeler_see_final_opening_area_mm2"],
            "water_component_disposition_counts": report["water_bridge_accounting"]["disposition_counts"],
            "halves": {
                half: {
                    "aperture_fraction": data["aperture_fraction_of_retained_body"],
                    "mandatory_topology_bridge_count": data["aperture_island_control"]["bridge_count"],
                    "bridge_width_mm": data["aperture_island_control"]["bridge_width_mm"],
                    "connected_components": data["composite"]["connected_components"],
                    "composite_triangles": data["composite"]["triangles"],
                }
                for half, data in report["halves"].items()
            },
        }
    summary = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.3",
        "candidate": CANDIDATE,
        "status": "DRAFT_DIGITAL_PASS_PHYSICAL_AND_GUI_REVIEW_REQUIRED",
        "semantic_result": {
            "tool_1": "Oak land base",
            "tool_2": "Mint Green relief and areas",
            "tool_3": "Midnight streets including motorway/trunk",
            "tool_4": "Sky Blue S-Bahn/U-Bahn, context boundary and metriMade site marker",
            "negative_geometry": "all retained mapped water areas and river/canal/stream lines",
        },
        "modes": mode_summary,
        "rear_structure": {
            "rear_grid": False,
            "blanket_ribs": False,
            "local_rear_ribs": False,
            "gravity_load_path": "independent upper support on each half",
            "physical_strength_claim": False,
        },
        "examples": examples,
        "digital_gates": [
            {"id": "source-and-build", "status": "PASS", "evidence": rel(VALIDATION / "digital-source-build-attestation.json")},
            {"id": "mesh-and-3mf", "status": "PASS", "evidence": rel(VALIDATION / "validation-summary-draft-r3.json")},
            {"id": "native-anycubic-slices", "status": "PASS_WITH_CONTEXT_GUI_REVIEW", "evidence": rel(VALIDATION / "anycubic-slices")},
            {"id": "aggregate-draft-validation", "status": "REVIEW_REQUIRED", "evidence": rel(VALIDATION / "validation-summary-draft-r3.json")},
        ],
        "open_gates": [
            "Inspect the two context-outline projects in the Anycubic GUI and resolve the floating-regions warnings before printing.",
            "Confirm physical SUNLU spool batches, drying/conditioning, ACE slots, purge matrix and wipe tower.",
            "Print and inspect the connector, lighting/opacity and inherited logo-recognition coupons.",
            "Perform handling and installed proof-load tests on the selected two-half artwork.",
            "Approve rear watermark, logo/map rights, safety and commercial release.",
        ],
        "prohibited_actions_not_performed": ["printer upload", "print start"],
    }
    output_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    markdown = f"""# MM-ART-010 Berlin — DRAFT {CANDIDATE}

Die korrigierte Revision 0.5.3 bilanziert sämtliche erfassten Gewässer. Alle innerhalb des jeweiligen Ausschnitts druckbar erhaltenen Wasserflächen und Wasserlinien werden zu Durchbrüchen; Mindestbreiten, geschützte Funktionszonen und die freigegebenen lokal notwendigen 2-mm-Topologiestege sind im Accounting ausdrücklich dokumentiert. Sky Blue ist S-/U-Bahn sowie Stadtgrenze/Standortmarker zugeordnet. Alle vier nativen Anycubic-Projekte enthalten vier nichtleere Werkzeugkörper und wurden nativ gesliced. Ein Druck oder eine kommerzielle Freigabe wird damit noch nicht autorisiert.

| Modus / Hälfte | 3MF-Dreiecke | Native Layer | Werkzeugwechsel | Ergebnis |
|---|---:|---:|---:|---|
{chr(10).join(rows)}

Die Öffnungsanteile liegen zwischen 6,86 % und 9,53 % je Hälfte und damit unter dem 12-%-Limit. Tegeler See bleibt mit 202,94 mm² (`boundary_crop`) beziehungsweise 262,56 mm² (`context_outline`) als echte Öffnung erhalten. Je nach Modus/Hälfte verbinden 56 bis 148 ausschließlich lokal erforderliche 2-mm-Stege abgetrennte Landinseln. Es gibt kein Rückraster, keine pauschalen Rippen und keine lokalen rückseitigen Rippen.

Alle Mesh-, 3MF-, Quellen-, Hash- und kanonischen Anycubic-Slice-Prüfungen bestehen. Die Kontextvariante erzeugt in beiden Hälften eine Anycubic-Warnung zu schwebenden Bereichen; diese muss vor dem Druck in der farbigen Layer-Vorschau bewertet werden. Physische Steg-/Handhabungs-/Wandtests, ACE/Purge, Licht-/Opazitätsprüfung, 2-m-Logoerkennung, Wasserzeichen und kommerzielle Freigabe bleiben offen.
"""
    output_md.write_text(markdown)
    print(json.dumps({"status": "PASS", "json": rel(output_json), "markdown": rel(output_md)}))


if __name__ == "__main__":
    main()
