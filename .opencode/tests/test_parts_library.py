import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "skills" / "functional-3d-design" / "scripts" / "parts_library.py"


class PartsLibraryTests(unittest.TestCase):
    def test_local_qualification_requires_process_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "parts.json"
            entry = root / "entry.json"
            entry.write_text(
                json.dumps(
                    {
                        "part_id": "test-spacer",
                        "revision": "0.1.0",
                        "status": "experimental",
                        "source_type": "printed",
                        "category": "spacer",
                        "validation": [],
                        "test_evidence": [],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "init"],
                check=True,
                capture_output=True,
                text=True,
            )
            add = subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "add", "--entry", str(entry)],
                check=False,
                capture_output=True,
                text=True,
            )
            promote = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--library",
                    str(library),
                    "promote",
                    "--part-id",
                    "test-spacer",
                    "--status",
                    "qualified-local",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(add.returncode, 0, add.stderr)
        self.assertEqual(promote.returncode, 1)
        self.assertFalse(json.loads(promote.stdout)["passed"])

    def test_add_rejects_direct_qualified_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "parts.json"
            entry = root / "entry.json"
            entry.write_text(
                json.dumps(
                    {
                        "part_id": "unsafe",
                        "revision": "1.0.0",
                        "status": "qualified-local",
                        "source_type": "printed",
                        "category": "fixture",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "add", "--entry", str(entry)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("only through promote", result.stdout)

    def test_failed_evidence_cannot_qualify_part(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "parts.json"
            entry = root / "entry.json"
            process = {
                "printer": "local-printer",
                "material": "PETG batch A",
                "nozzle_mm": 0.6,
                "profile_id": "profile-sha256",
            }
            entry.write_text(
                json.dumps(
                    {
                        "part_id": "failed-part",
                        "revision": "1.0.0",
                        "status": "experimental",
                        "source_type": "printed",
                        "category": "fixture",
                        "material_process": process,
                        "validation": [
                            {
                                "path": "mesh.json",
                                "passed": True,
                                "part_revision": "1.0.0",
                                "material_process": process,
                            }
                        ],
                        "test_evidence": [
                            {
                                "path": "failed-test.json",
                                "passed": False,
                                "part_revision": "1.0.0",
                                "material_process": process,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "init"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "add", "--entry", str(entry)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--library",
                    str(library),
                    "promote",
                    "--part-id",
                    "failed-part",
                    "--status",
                    "qualified-local",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no passing test matches", result.stdout)

    def test_failed_validation_cannot_qualify_part(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "parts.json"
            entry = root / "entry.json"
            process = {
                "printer": "local-printer",
                "material": "PETG batch A",
                "nozzle_mm": 0.6,
                "profile_id": "profile-sha256",
            }
            evidence_base = {
                "part_revision": "1.0.0",
                "material_process": process,
            }
            entry.write_text(
                json.dumps(
                    {
                        "part_id": "bad-geometry",
                        "revision": "1.0.0",
                        "status": "experimental",
                        "source_type": "printed",
                        "category": "fixture",
                        "material_process": process,
                        "validation": [{**evidence_base, "path": "mesh.json", "passed": False}],
                        "test_evidence": [{**evidence_base, "path": "test.json", "passed": True}],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "init"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "add", "--entry", str(entry)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--library",
                    str(library),
                    "promote",
                    "--part-id",
                    "bad-geometry",
                    "--status",
                    "qualified-local",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no passing validation matches", result.stdout)

    def test_hashed_project_evidence_can_qualify_matching_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "parts.json"
            entry = root / "entry.json"
            validation_report = root / "mesh-validation.json"
            physical_report = root / "physical-test.json"
            process = {
                "printer": "local-printer",
                "material": "PETG batch A",
                "nozzle_mm": 0.6,
                "profile_id": "profile-sha256",
            }
            validation_report.write_text(
                json.dumps(
                    {
                        "passed": True,
                        "part_revision": "1.0.0",
                        "material_process": process,
                    }
                ),
                encoding="utf-8",
            )
            physical_report.write_text(
                json.dumps(
                    {
                        "passed": True,
                        "part_revision": "1.0.0",
                        "material_process": process,
                        "measurements": {"proof_load_n": 100},
                    }
                ),
                encoding="utf-8",
            )
            evidence_base = {
                "part_revision": "1.0.0",
                "material_process": process,
                "passed": True,
            }
            entry.write_text(
                json.dumps(
                    {
                        "part_id": "qualified-fixture",
                        "revision": "1.0.0",
                        "status": "experimental",
                        "source_type": "printed",
                        "category": "fixture",
                        "material_process": process,
                        "validation": [
                            {
                                **evidence_base,
                                "evidence_type": "geometry-validation",
                                "path": validation_report.name,
                                "sha256": hashlib.sha256(validation_report.read_bytes()).hexdigest(),
                            }
                        ],
                        "test_evidence": [
                            {
                                **evidence_base,
                                "evidence_type": "physical-test",
                                "path": physical_report.name,
                                "sha256": hashlib.sha256(physical_report.read_bytes()).hexdigest(),
                                "measurements": {"proof_load_n": 100},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "init"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "add", "--entry", str(entry)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--library",
                    str(library),
                    "--evidence-root",
                    str(root),
                    "promote",
                    "--part-id",
                    "qualified-fixture",
                    "--status",
                    "qualified-local",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
