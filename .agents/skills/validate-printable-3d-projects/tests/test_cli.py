from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/fdm_ci.py"


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(CLI), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_doctor_is_machine_readable(self) -> None:
        completed = self.run_cli("doctor", "--profile", "draft")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["tool"], "doctor")
        self.assertIn("capability_groups", payload["environment"])

    def test_missing_mesh_fails(self) -> None:
        completed = self.run_cli("audit-mesh", "missing.stl")
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(json.loads(completed.stdout)["status"], "FAIL")

    def test_anycubic_slice_missing_source_fails_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "slice"
            completed = self.run_cli(
                "slice-anycubic-next",
                "missing.stl",
                str(output),
                "--slicer",
                "missing-slicer",
            )
            self.assertEqual(
                completed.returncode, 1, completed.stdout + completed.stderr
            )
            self.assertEqual(json.loads(completed.stdout)["status"], "FAIL")
            self.assertFalse(output.exists())

    def test_anycubic_p2_author_missing_source_fails_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            output = base / "candidate.3mf"
            completed = self.run_cli(
                "author-anycubic-3mf",
                str(output),
                str(base / "missing.stl"),
                "--machine-profile",
                str(base / "machine.json"),
                "--process-profile",
                str(base / "process.json"),
                "--filament-profile",
                str(base / "filament.json"),
                "--support-mode",
                "disabled",
            )
            self.assertEqual(
                completed.returncode, 1, completed.stdout + completed.stderr
            )
            self.assertEqual(json.loads(completed.stdout)["status"], "FAIL")
            self.assertFalse(output.exists())

    def test_validate_skill_from_arbitrary_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(CLI),
                    "validate-skill",
                    str(ROOT),
                    "--runtime",
                    "opencode",
                    "--profile",
                    "draft",
                ],
                cwd=tmp,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertNotEqual(json.loads(completed.stdout)["status"], "FAIL")

    def test_p2_stage_requires_four_distinct_hash_bound_artifacts_and_print_settings(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = Path(tmp) / "product"
            stage = product / "p2-stage"
            stage.mkdir(parents=True)
            description = stage / "product-description.en.md"
            description.write_text(
                "# Example product\n\nThis compact printable organizer keeps ordinary desk items separated. "
                "The candidate contains one support-free tray printed flat on its base. It is a digital "
                "development artifact only; fit, finish, strength, safety, rights and commercial release "
                "remain outside this description.\n",
                encoding="utf-8",
            )
            concept = stage / "concept.svg"
            concept.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><rect width="20" height="20" fill="blue"/></svg>',
                encoding="utf-8",
            )
            rendered = stage / "render.svg"
            rendered.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="8" fill="green"/></svg>',
                encoding="utf-8",
            )
            three_mf = stage / "print-set.3mf"
            model = '<?xml version="1.0"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"><resources><object id="2" type="model"><components><component objectid="1" p:path="/3D/Objects/tray.model"/></components></object></resources><build><item objectid="2"/></build></model>'
            tray_model = '<?xml version="1.0"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model" name="tray"><mesh><vertices><vertex x="0" y="0" z="0"/><vertex x="1" y="0" z="0"/><vertex x="0" y="1" z="0"/><vertex x="0" y="0" z="1"/></vertices><triangles><triangle v1="0" v2="2" v3="1"/><triangle v1="0" v2="1" v3="3"/><triangle v1="1" v2="2" v3="3"/><triangle v1="2" v2="0" v3="3"/></triangles></mesh></object></resources></model>'
            content_types = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
            relationships = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
            production_relationships = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/Objects/tray.model" Id="rel1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
            model_settings = '<?xml version="1.0"?><config><object id="1"><metadata key="name" value="tray"/><part id="1" subtype="normal_part"/></object><plate><model_instance><metadata key="object_id" value="1"/></model_instance></plate></config>'
            with zipfile.ZipFile(three_mf, "w") as archive:
                archive.writestr("[Content_Types].xml", content_types)
                archive.writestr("_rels/.rels", relationships)
                archive.writestr("3D/3dmodel.model", model)
                archive.writestr(
                    "3D/_rels/3dmodel.model.rels", production_relationships
                )
                archive.writestr("3D/Objects/tray.model", tray_model)
                archive.writestr(
                    "Metadata/project_settings.config",
                    json.dumps({"enable_support": "0"}),
                )
                archive.writestr("Metadata/model_settings.config", model_settings)

            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            manifest = {
                "schema_version": "1.0",
                "product": {
                    "record_id": "PORT-X",
                    "sku": "MM-TEST-001",
                    "name": "Example",
                    "revision": "0.1.0",
                    "lifecycle_stage": "P2 Digital candidate",
                    "root": "..",
                },
                "artifacts": {
                    "description_en": {
                        "path": "p2-stage/product-description.en.md",
                        "sha256": digest(description),
                        "language": "en",
                    },
                    "concept_image": {
                        "path": "p2-stage/concept.svg",
                        "sha256": digest(concept),
                        "scope": "whole-product",
                        "approval_state": "retrospective-unapproved",
                    },
                    "rendered_image": {
                        "path": "p2-stage/render.svg",
                        "sha256": digest(rendered),
                        "basis": "current-model",
                    },
                    "print_set_3mf": {
                        "path": "p2-stage/print-set.3mf",
                        "sha256": digest(three_mf),
                        "all_print_parts_included": True,
                        "print_parts": [{"name": "tray", "quantity": 1}],
                        "orientation": {
                            "status": "considered",
                            "encoding": "embedded-slicer-project",
                            "summary": "Flat base placed directly on the build plate.",
                        },
                        "supports": {
                            "status": "considered",
                            "mode": "disabled",
                            "encoding": "embedded-slicer-project",
                            "summary": "Geometry is intentionally support-free in this orientation.",
                        },
                    },
                },
                "limitations": ["Digital candidate only."],
            }
            manifest_path = stage / "p2-manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            completed = self.run_cli("validate-p2-stage", str(manifest_path))
            self.assertEqual(
                completed.returncode, 0, completed.stdout + completed.stderr
            )
            self.assertEqual(json.loads(completed.stdout)["status"], "PASS")

            manifest["artifacts"]["rendered_image"] = {
                "path": "p2-stage/concept.svg",
                "sha256": digest(concept),
                "basis": "current-model",
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            completed = self.run_cli("validate-p2-stage", str(manifest_path))
            self.assertEqual(completed.returncode, 1)
            self.assertEqual(json.loads(completed.stdout)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
