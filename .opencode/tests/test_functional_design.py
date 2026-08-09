import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "functional-3d-design"
    / "scripts"
    / "validate_design_spec.py"
)
POLICY_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "commercial-cad-provenance"
    / "references"
    / "commercial-license-policy.json"
)


def run_validation(
    spec: dict,
    provenance_status: str = "COMMERCIAL_LICENSE_PASS",
    provenance_project: str | None = None,
    manufacturing_profile: dict | None = None,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / "design-spec.json"
        manifest = root / "provenance.json"
        provenance = root / "commercial-license.json"
        manufacturing = root / "manufacturing-profile.json"
        manifest_payload = {
            "project": spec["project"],
            "items": [
                {
                    "id": "housing-geometry",
                    "kind": "generated_geometry",
                    "origin": "self",
                    "license": "LicenseRef-Proprietary",
                }
            ],
        }
        manifest_bytes = json.dumps(manifest_payload, sort_keys=True).encode("utf-8")
        manifest.write_bytes(manifest_bytes)
        spec = {
            **spec,
            "provenance_manifest": "provenance.json",
            "provenance_report": "commercial-license.json",
            "manufacturing_profile": "manufacturing-profile.json",
        }
        path.write_text(json.dumps(spec), encoding="utf-8")
        provenance.write_text(
            json.dumps(
                {
                    "status": provenance_status,
                    "project": provenance_project or spec["project"],
                    "checked_items": 1,
                    "approved_item_ids": ["housing-geometry"],
                    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                    "policy_sha256": hashlib.sha256(POLICY_PATH.read_bytes()).hexdigest(),
                }
            ),
            encoding="utf-8",
        )
        profile = manufacturing_profile or {
            "project": spec["project"],
            "strategy": "generic-customer-qualified-fdm",
            "support_matrix": [
                {
                    "component_id": "housing",
                    "nozzle_mm": 0.4,
                    "material": "PETG",
                    "status": "conditional",
                    "required_coupons": ["fit-coupon"],
                },
                {
                    "component_id": "housing",
                    "nozzle_mm": 0.6,
                    "material": "PETG",
                    "status": "conditional",
                    "required_coupons": ["fit-coupon"],
                },
            ],
        }
        manufacturing.write_text(json.dumps(profile), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--provenance-report",
                str(provenance),
                "--manufacturing-profile",
                str(manufacturing),
            ],
            check=False,
            capture_output=True,
            text=True,
        )


def valid_spec() -> dict:
    return {
        "project": "filament-feeder",
        "intent": "Feed filament with a driven roller",
        "commercial_product": True,
        "functions": [
            {
                "id": "feed",
                "description": "Transmit force to filament",
                "load_case": {
                    "magnitude": 20,
                    "unit": "N",
                    "direction": "tangential",
                    "duration": "continuous feed"
                },
                "life_requirement": {"value": 100000, "unit": "revolutions"},
                "failure_modes": ["roller wear", "shaft slip"],
            }
        ],
        "components": [
            {
                "id": "housing",
                "decision": "PRINT",
                "reason": "Custom low-wear geometry",
                "material_class": "PETG",
                "nozzle_classes": [0.4, 0.6],
                "geometry_origin": "self",
                "provenance_item_id": "housing-geometry",
            },
            {
                "id": "shaft",
                "decision": "BUY",
                "reason": "Precision wear surface",
                "interface_dimensions_mm": {"diameter": 5.0},
                "dimensional_source": "Selected shaft manufacturer drawing rev A",
            },
        ],
        "test_plan": [
            {
                "id": "fit-coupon",
                "type": "coupon",
                "targets": ["housing", "shaft"],
                "acceptance": {
                    "metric": "shaft_play",
                    "comparator": "<=",
                    "value": 0.2,
                    "unit": "mm"
                },
            }
        ],
    }


class FunctionalDesignTests(unittest.TestCase):
    def test_accepts_complete_engineering_package(self) -> None:
        result = run_validation(valid_spec())

        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "ENGINEERING_DECISION_PASS")

    def test_blocks_cad_when_load_case_is_missing(self) -> None:
        spec = valid_spec()
        del spec["functions"][0]["load_case"]

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)
        blockers = " ".join(json.loads(result.stdout)["blockers"])
        self.assertIn("load_case", blockers)

    def test_blocks_print_component_without_material_and_nozzle_class(self) -> None:
        spec = valid_spec()
        del spec["components"][0]["material_class"]
        del spec["components"][0]["nozzle_classes"]

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)
        blockers = " ".join(json.loads(result.stdout)["blockers"])
        self.assertIn("material_class", blockers)
        self.assertIn("nozzle_classes", blockers)

    def test_blocks_unresolved_component_decision(self) -> None:
        spec = valid_spec()
        spec["components"][0]["decision"] = "NEEDS_TEST"

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)

    def test_ignores_self_certified_gate_booleans_when_provenance_is_blocked(self) -> None:
        spec = valid_spec()
        spec["commercial_license_pass"] = True
        spec["engineering_decision_pass"] = True

        result = run_validation(spec, provenance_status="BLOCKED_LIBRARY_ASSET")

        self.assertEqual(result.returncode, 2)
        self.assertIn("provenance_report", " ".join(json.loads(result.stdout)["blockers"]))

    def test_blocks_provenance_report_from_different_project(self) -> None:
        result = run_validation(valid_spec(), provenance_project="different-product")

        self.assertEqual(result.returncode, 2)
        self.assertIn("project mismatch", " ".join(json.loads(result.stdout)["blockers"]))

    def test_blocks_placeholder_engineering_values(self) -> None:
        spec = valid_spec()
        spec["functions"][0]["load_case"] = {
            "magnitude": "TBD",
            "unit": "TBD",
            "direction": "unknown",
            "duration": "TBD",
        }

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)

    def test_blocks_invalid_nozzle_class(self) -> None:
        spec = valid_spec()
        spec["components"][0]["nozzle_classes"] = [1.75]

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)
        self.assertIn("nozzle_classes", " ".join(json.loads(result.stdout)["blockers"]))

    def test_blocks_specialist_material_without_justification(self) -> None:
        spec = valid_spec()
        spec["components"][0]["material_class"] = "PA-CF"

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)
        self.assertIn("specialist_material_reason", " ".join(json.loads(result.stdout)["blockers"]))

    def test_requires_commercial_product_true(self) -> None:
        spec = valid_spec()
        spec["commercial_product"] = False

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)

    def test_blocks_unverified_process_profile(self) -> None:
        profile = {
            "project": "filament-feeder",
            "strategy": "generic-customer-qualified-fdm",
            "support_matrix": [
                {
                    "component_id": "housing",
                    "nozzle_mm": 0.4,
                    "material": "PETG",
                    "status": "unverified",
                    "required_coupons": [],
                }
            ],
        }

        result = run_validation(valid_spec(), manufacturing_profile=profile)

        self.assertEqual(result.returncode, 2)
        self.assertIn("support_matrix", " ".join(json.loads(result.stdout)["blockers"]))

    def test_blocks_unstructured_or_unlinked_test(self) -> None:
        spec = valid_spec()
        spec["test_plan"][0] = {
            "id": "weak-test",
            "type": "anything",
            "targets": [],
            "acceptance": "wait 1 h",
        }

        result = run_validation(spec)

        self.assertEqual(result.returncode, 2)
        blockers = " ".join(json.loads(result.stdout)["blockers"])
        self.assertIn("type", blockers)
        self.assertIn("targets", blockers)


if __name__ == "__main__":
    unittest.main()
