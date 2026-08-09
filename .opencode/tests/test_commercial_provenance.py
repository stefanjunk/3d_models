import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "commercial-cad-provenance"
    / "scripts"
    / "check_provenance.py"
)


def run_check(
    manifest: dict,
    artifacts: dict[str, bytes] | None = None,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / "provenance.json"
        for relative_path, content in (artifacts or {}).items():
            artifact = root / relative_path
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(content)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )


def run_check_with_attributions(manifest: dict) -> tuple[subprocess.CompletedProcess[str], str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "provenance.json"
        notices = Path(tmp) / "ATTRIBUTIONS.md"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--attributions", str(notices)],
            check=False,
            capture_output=True,
            text=True,
        )
        return result, notices.read_text(encoding="utf-8") if notices.exists() else ""


def attributed_asset(content: bytes = b"example-step") -> tuple[dict, dict[str, bytes]]:
    import hashlib

    relative_path = "assets/part.step"
    license_path = "licenses/CC-BY-4.0.txt"
    license_text = b"Creative Commons Attribution 4.0"
    item = {
        "id": "attributed-part",
        "kind": "third_party_asset",
        "origin": "third_party",
        "license": "CC-BY-4.0",
        "source_url": "https://example.test/part.step",
        "version_or_commit": "asset-revision-1",
        "artifact_path": relative_path,
        "sha256": hashlib.sha256(content).hexdigest(),
        "distribution": "redistributed",
        "license_file": license_path,
        "license_sha256": hashlib.sha256(license_text).hexdigest(),
        "attribution": {
            "title": "Example part",
            "author": "Example Author",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "modifications": "Scaled preview envelope only",
        },
    }
    return item, {relative_path: content, license_path: license_text}


def permissive_library(content: bytes = b"library-wheel") -> tuple[dict, dict[str, bytes]]:
    import hashlib

    artifact_path = "artifacts/library.whl"
    license_path = "licenses/Apache-2.0.txt"
    license_text = b"Apache License Version 2.0"
    item = {
        "id": "cad-library",
        "kind": "library",
        "origin": "third_party",
        "license": "Apache-2.0",
        "source_url": "https://example.test/library",
        "version_or_commit": "commit-123",
        "artifact_path": artifact_path,
        "sha256": hashlib.sha256(content).hexdigest(),
        "distribution": "build_only",
        "license_file": license_path,
        "license_sha256": hashlib.sha256(license_text).hexdigest(),
    }
    return item, {artifact_path: content, license_path: license_text}


class CommercialProvenanceTests(unittest.TestCase):
    def test_blocks_unknown_asset_license(self) -> None:
        result = run_check(
            {
                "project": "test-product",
                "items": [
                    {
                        "id": "catalog-bearing",
                        "kind": "third_party_asset",
                        "origin": "third_party",
                        "license": "UNKNOWN",
                        "source_url": "https://example.test/bearing.step",
                    }
                ],
            }
        )

        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "BLOCKED_LIBRARY_ASSET")

    def test_accepts_cc_by_only_with_complete_attribution(self) -> None:
        item, artifacts = attributed_asset()

        missing = json.loads(
            run_check({"project": "p", "items": [{**item, "attribution": {}}]}, artifacts).stdout
        )
        complete = run_check({"project": "p", "items": [item]}, artifacts)

        self.assertEqual(missing["status"], "BLOCKED_LIBRARY_ASSET")
        self.assertEqual(complete.returncode, 0)
        self.assertEqual(json.loads(complete.stdout)["status"], "COMMERCIAL_LICENSE_PASS")

    def test_blocks_copyleft_and_share_alike(self) -> None:
        for license_id in ("GPL-3.0-only", "LGPL-3.0-only", "CC-BY-SA-4.0"):
            with self.subTest(license_id=license_id):
                result = run_check(
                    {
                        "project": "p",
                        "items": [
                            {
                                "id": "blocked",
                                "kind": "third_party_asset",
                                "origin": "third_party",
                                "license": license_id,
                                "source_url": "https://example.test/source",
                                "version_or_commit": "revision-1",
                            }
                        ],
                    }
                )
                self.assertEqual(result.returncode, 2)

    def test_accepts_self_owned_proprietary_geometry(self) -> None:
        result = run_check(
            {
                "project": "p",
                "items": [
                    {
                        "id": "own-model",
                        "kind": "generated_geometry",
                        "origin": "self",
                        "license": "LicenseRef-Proprietary",
                    }
                ],
            }
        )

        self.assertEqual(result.returncode, 0)

    def test_writes_cc_by_attribution_notice(self) -> None:
        item, artifacts = attributed_asset()
        item["attribution"]["modifications"] = "Converted to a simplified envelope"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative_path, content in artifacts.items():
                artifact = root / relative_path
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(content)
            manifest = root / "provenance.json"
            notices_path = root / "ATTRIBUTIONS.md"
            manifest.write_text(
                json.dumps({"project": "commercial-product", "items": [item]}),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(manifest), "--attributions", str(notices_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            notices = notices_path.read_text(encoding="utf-8") if notices_path.exists() else ""

        self.assertEqual(result.returncode, 0)
        self.assertIn("Example part", notices)
        self.assertIn("Example Author", notices)
        self.assertIn("Converted to a simplified envelope", notices)

    def test_blocks_unknown_kind_bypass(self) -> None:
        result = run_check(
            {
                "project": "p",
                "items": [
                    {
                        "id": "bypass",
                        "kind": "image",
                        "origin": "third_party",
                        "license": "MIT",
                        "source_url": "https://example.test/asset.step",
                        "attribution": {
                            "title": "Asset",
                            "author": "Author",
                            "license_url": "https://opensource.org/license/mit",
                            "modifications": "None",
                        },
                    }
                ],
            }
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported kind", " ".join(json.loads(result.stdout)["blockers"]))

    def test_blocks_asset_when_actual_hash_does_not_match(self) -> None:
        item, artifacts = attributed_asset(content=b"actual-content")
        item["sha256"] = "0" * 64

        result = run_check({"project": "p", "items": [item]}, artifacts)

        self.assertEqual(result.returncode, 2)
        self.assertIn("sha256 mismatch", " ".join(json.loads(result.stdout)["blockers"]))

    def test_generates_third_party_notice_by_default(self) -> None:
        item, artifacts = attributed_asset()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative_path, content in artifacts.items():
                artifact = root / relative_path
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(content)
            manifest = root / "provenance.json"
            manifest.write_text(json.dumps({"project": "p", "items": [item]}), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(manifest)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue((root / "THIRD_PARTY_NOTICES.md").is_file())
            self.assertTrue((root / "ATTRIBUTIONS.md").is_file())

    def test_requires_version_or_commit_for_third_party_library(self) -> None:
        item, artifacts = permissive_library()
        del item["version_or_commit"]

        result = run_check({"project": "p", "items": [item]}, artifacts)

        self.assertEqual(result.returncode, 2)
        self.assertIn("version_or_commit", " ".join(json.loads(result.stdout)["blockers"]))

    def test_requires_real_artifact_and_license_hashes_for_build_only_library(self) -> None:
        result = run_check(
            {
                "project": "p",
                "items": [
                    {
                        "id": "cad-library",
                        "kind": "library",
                        "origin": "third_party",
                        "license": "Apache-2.0",
                        "source_url": "https://example.test/library",
                        "version_or_commit": "commit-123",
                        "distribution": "build_only",
                    }
                ],
            }
        )

        self.assertEqual(result.returncode, 2)
        blockers = " ".join(json.loads(result.stdout)["blockers"])
        self.assertIn("artifact_path", blockers)
        self.assertIn("license_file", blockers)

    def test_requires_real_artifact_for_third_party_generated_geometry(self) -> None:
        result = run_check(
            {
                "project": "p",
                "items": [
                    {
                        "id": "generated-by-someone-else",
                        "kind": "generated_geometry",
                        "origin": "third_party",
                        "license": "MIT",
                        "source_url": "https://example.test/model",
                        "version_or_commit": "rev-1",
                    }
                ],
            }
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("artifact_path", " ".join(json.loads(result.stdout)["blockers"]))

    def test_report_binds_project_manifest_policy_and_approved_ids(self) -> None:
        item, artifacts = permissive_library()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative_path, content in artifacts.items():
                artifact = root / relative_path
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(content)
            manifest = root / "provenance.json"
            report_path = root / "commercial-license.json"
            manifest.write_text(json.dumps({"project": "p", "items": [item]}), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(manifest), "--report", str(report_path)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["project"], "p")
            self.assertEqual(report["approved_item_ids"], ["cad-library"])
            self.assertRegex(report["manifest_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(report["policy_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
