#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        text=True,
        capture_output=True,
        check=False,
    )


class ScriptTests(unittest.TestCase):
    def test_initializer_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "clearance"
            created = run(
                "new_commercial_3d_project.py",
                "--name",
                "Test Hook",
                "--seller-country",
                "DE",
                "--markets",
                "EU,US",
                "--release-type",
                "both",
                "--output",
                project,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue((project / "project.json").is_file())
            self.assertTrue((project / "07-release/provenance.json").is_file())

            audited = run("audit_commercial_release.py", project)
            self.assertEqual(audited.returncode, 2)
            self.assertIn("Decision: **BLOCK**", audited.stdout)
            self.assertIn("ready_for_release", audited.stdout)

    def test_completed_low_risk_digital_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "clearance"
            created = run(
                "new_commercial_3d_project.py",
                "--name",
                "Original Cable Label",
                "--seller-country",
                "DE",
                "--markets",
                "EU",
                "--release-type",
                "digital",
                "--release-id",
                "LABEL-2026-001",
                "--output",
                project,
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            def write_evidence(relative: str, text: str) -> str:
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
                return hashlib.sha256(path.read_bytes()).hexdigest()

            source_hash = write_evidence(
                "01-sources/evidence/original-sketch.txt",
                "Original sketch made by Example Seller on 2026-08-10.",
            )
            write_evidence(
                "01-sources/evidence/employee-assignment.txt",
                "Test-only evidence of owned original work.",
            )
            write_evidence(
                "02-tools/evidence/openscad-license.txt",
                "Test-only snapshot of OpenSCAD GPLv2 license and commercial output review.",
            )
            write_evidence(
                "04-authorship/versions/commit.txt",
                "Human selected dimensions, type placement, and fit after two prototypes.",
            )
            write_evidence(
                "05-clearance/searches/classification.txt",
                "Test fixture classification and EU market review.",
            )

            def write_csv(relative: str, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
                with (project / relative).open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

            source_fields = (ROOT / "assets/source-register.csv").read_text(
                encoding="utf-8"
            ).splitlines()[0].split(",")
            write_csv(
                "01-sources/source-register.csv",
                source_fields,
                [
                    {
                        "source_id": "SRC-0001",
                        "design_stage": "concept",
                        "title": "Original employee sketch",
                        "creator": "Example Seller",
                        "source_type": "original",
                        "source_url": "not_applicable",
                        "local_path": "01-sources/evidence/original-sketch.txt",
                        "sha256": source_hash,
                        "acquired_at": "2026-08-10",
                        "license_expression": "LicenseRef-Owned-Original",
                        "license_evidence_path": "01-sources/evidence/employee-assignment.txt",
                        "terms_effective_date": "2026-08-10",
                        "commercial_use": "yes",
                        "derivatives": "yes",
                        "ai_input": "not_applicable",
                        "redistribute_digital": "yes",
                        "physical_sale": "not_applicable",
                        "attribution_required": "no",
                        "attribution_text": "not_applicable",
                        "patent_rights": "not_applicable",
                        "trademark_privacy_publicity": "pass",
                        "used_in_outputs": "model.stl",
                        "reviewer": "IP Reviewer",
                        "review_date": "2026-08-10",
                        "status": "pass",
                        "notes": "Original low-risk test fixture",
                    }
                ],
            )

            tool_fields = (ROOT / "assets/tool-register.csv").read_text(
                encoding="utf-8"
            ).splitlines()[0].split(",")
            write_csv(
                "02-tools/tool-register.csv",
                tool_fields,
                [
                    {
                        "tool_id": "TOOL-0001",
                        "design_stage": "CAD",
                        "name": "OpenSCAD",
                        "provider": "OpenSCAD project",
                        "version": "test-version",
                        "build_hash": "not_applicable",
                        "purpose": "Parametric CAD",
                        "license_expression": "GPL-2.0-only",
                        "plan": "open-source desktop",
                        "terms_url": "https://openscad.org/about.html",
                        "terms_evidence_path": "02-tools/evidence/openscad-license.txt",
                        "terms_effective_date": "2026-08-10",
                        "commercial_use": "yes",
                        "input_confidentiality": "local processing approved",
                        "output_restrictions": "none identified for original geometry",
                        "plugins_assets_dependencies": "none",
                        "distribution_obligations": "none; application not distributed",
                        "reviewer": "IP Reviewer",
                        "review_date": "2026-08-10",
                        "status": "pass",
                        "notes": "Test fixture",
                    }
                ],
            )

            component_fields = (ROOT / "assets/component-register.csv").read_text(
                encoding="utf-8"
            ).splitlines()[0]
            (project / "03-components/component-register.csv").write_text(
                component_fields + "\n", encoding="utf-8"
            )

            human_fields = (ROOT / "assets/human-contribution-log.csv").read_text(
                encoding="utf-8"
            ).splitlines()[0].split(",")
            write_csv(
                "04-authorship/human-contribution-log.csv",
                human_fields,
                [
                    {
                        "timestamp": "2026-08-10T12:00:00Z",
                        "contributor": "Example Seller",
                        "artifact_or_commit": "LABEL-2026-001",
                        "design_problem": "Readable reusable cable label",
                        "choice_or_change": "Selected dimensions and asymmetric letter placement",
                        "constraints_and_alternatives": "Rejected two weak thin-wall variants",
                        "human_contribution": "Authored geometry and dimensional constraints",
                        "ai_or_tool_role": "OpenSCAD executed human-authored parameters",
                        "source_ids": "SRC-0001",
                        "evidence_path": "04-authorship/versions/commit.txt",
                        "reviewer": "Engineering Reviewer",
                    }
                ],
            )

            market_fields = (ROOT / "assets/market-matrix.csv").read_text(
                encoding="utf-8"
            ).splitlines()[0].split(",")
            write_csv(
                "05-clearance/market-matrix.csv",
                market_fields,
                [
                    {
                        "market": "EU",
                        "channel": "direct download store",
                        "release_type": "digital",
                        "product_classification": "ordinary digital manufacturing file",
                        "ai_classification": "no AI used",
                        "ip_searches": "documented low-risk name and design search",
                        "product_safety_framework": "digital file risk review completed",
                        "conformity_and_label": "CE not applicable with written rationale",
                        "consumer_digital_terms": "EU digital-content flow implemented",
                        "tax_epr": "VAT owner approved; no physical packaging",
                        "privacy": "minimal checkout data reviewed",
                        "export_sanctions": "non-controlled file and customer screening",
                        "language": "English and target checkout language",
                        "official_source": "05-clearance/searches/classification.txt",
                        "effective_date": "2026-08-10",
                        "evidence_path": "05-clearance/searches/classification.txt",
                        "owner": "Compliance Owner",
                        "status": "pass",
                        "notes": "Test-only market row",
                    }
                ],
            )

            completed_docs = {
                "05-clearance/RIGHTS-CLEARANCE.md": "# Rights Clearance\n\nAll seven gates passed for this low-risk test fixture with evidence recorded.\n",
                "06-engineering/PRODUCT-TECHNICAL-FILE.md": "# Product Technical File\n\nDigital file risks, dimensional checks, instructions, and correction workflow passed.\n",
                "07-release/COMMERCIAL-MODEL-LICENSE.md": "# Commercial Model License\n\nCounsel-reviewed test license permits customer printing and prohibits file redistribution.\n",
                "07-release/THIRD-PARTY-NOTICES.md": "# Third-Party Notices\n\nNo third-party materials are included in this release.\n",
                "07-release/AI-DISCLOSURE.md": "# AI Use\n\nNo AI system was used to create this release; tool history is documented.\n",
            }
            for relative, text in completed_docs.items():
                (project / relative).write_text(text, encoding="utf-8")

            artifact = project / "07-release/artifacts/model.stl"
            artifact.write_bytes(b"solid original_label\nendsolid original_label\n")
            artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()

            project_json = json.loads((project / "project.json").read_text(encoding="utf-8"))
            project_json.update(
                {
                    "intended_use": "Printable identification label for indoor cables",
                    "product_category": "low-risk cable label digital model",
                    "safety_critical": "no",
                    "status": "ready_for_release",
                }
            )
            (project / "project.json").write_text(
                json.dumps(project_json, indent=2) + "\n", encoding="utf-8"
            )

            provenance_path = project / "07-release/provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance.update(
                {
                    "release_date": "2026-08-10",
                    "intended_use": "Printable identification label for indoor cables",
                    "prohibited_uses": ["safety-critical cable retention"],
                    "artifacts": [
                        {
                            "path": "07-release/artifacts/model.stl",
                            "sha256": artifact_hash,
                            "role": "printable mesh",
                            "license": "LicenseRef-Commercial-Model-1.0",
                        }
                    ],
                }
            )
            provenance["seller"].update(
                {
                    "legal_name": "Example Seller GmbH",
                    "postal_address": "Example Street 1, 10115 Berlin, Germany",
                    "electronic_address": "support@example.invalid",
                }
            )
            provenance["product_classification"].update(
                {
                    "status": "pass",
                    "classification": "low-risk digital cable-label manufacturing file",
                    "evidence_path": "05-clearance/searches/classification.txt",
                }
            )
            provenance["ai_use"].update({"used": "no"})
            provenance["outgoing_licenses"].update(
                {
                    "geometry": "LicenseRef-Commercial-Model-1.0",
                    "software": "not_applicable: no software distributed",
                    "documentation": "LicenseRef-Proprietary-Documentation-1.0",
                }
            )
            provenance["watermark"].update(
                {
                    "geometry_mark": "LABEL-2026-001",
                    "geometry_location": "rear nonfunctional face; print verified",
                    "metadata": "sidecar and filename because STL has no durable metadata",
                }
            )
            provenance["clearance"].update(
                {
                    "copyright_authorship": "pass",
                    "patent": "not_applicable",
                    "design": "pass",
                    "trademark": "pass",
                    "privacy_publicity": "not_applicable",
                }
            )
            provenance["compliance"].update(
                {
                    "risk_assessment": "pass",
                    "test_reports": "pass",
                    "labels_and_instructions": "pass",
                    "consumer_terms": "pass",
                    "traceability": "pass",
                    "technical_file": "pass",
                }
            )
            provenance["export"].update(
                {
                    "classification": "not_applicable",
                    "screening": "pass",
                }
            )
            provenance_path.write_text(
                json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
            )

            manifest_hash = hashlib.sha256(provenance_path.read_bytes()).hexdigest()
            evidence_manifest = project / "08-approvals/EVIDENCE-SHA256SUMS"
            frozen = run(
                "hash_release.py",
                project,
                "--output",
                evidence_manifest,
                "--exclude",
                "08-approvals",
                "--exclude",
                "09-incidents",
                "--exclude",
                "reports",
            )
            self.assertEqual(frozen.returncode, 0, frozen.stdout + frozen.stderr)
            evidence_manifest_hash = hashlib.sha256(
                evidence_manifest.read_bytes()
            ).hexdigest()
            approval_path = project / "08-approvals/release-approval.json"
            approval = json.loads(approval_path.read_text(encoding="utf-8"))
            approval.update(
                {
                    "manifest_sha256": manifest_hash,
                    "evidence_manifest_sha256": evidence_manifest_hash,
                    "decision": "PASS",
                    "approved_at": "2026-08-10T15:00:00Z",
                    "approvers": [
                        {
                            "name": "Engineering Reviewer",
                            "role": "engineering",
                            "authority": "Design release authority",
                            "decision": "PASS",
                            "signed_at": "2026-08-10T15:00:00Z",
                            "signature_reference": "test-signature-engineering",
                        },
                        {
                            "name": "IP Reviewer",
                            "role": "ip_legal",
                            "authority": "IP release authority",
                            "decision": "PASS",
                            "signed_at": "2026-08-10T15:00:00Z",
                            "signature_reference": "test-signature-ip",
                        },
                        {
                            "name": "Business Owner",
                            "role": "business_owner",
                            "authority": "Commercial release authority",
                            "decision": "PASS",
                            "signed_at": "2026-08-10T15:00:00Z",
                            "signature_reference": "test-signature-business",
                        },
                    ],
                }
            )
            approval_path.write_text(
                json.dumps(approval, indent=2) + "\n", encoding="utf-8"
            )

            audited = run("audit_commercial_release.py", project)
            self.assertEqual(audited.returncode, 0, audited.stdout + audited.stderr)
            self.assertIn("Decision: **PASS**", audited.stdout)

            (project / "05-clearance/RIGHTS-CLEARANCE.md").write_text(
                "# Rights Clearance\n\nChanged after approval and therefore invalid.\n",
                encoding="utf-8",
            )
            tampered = run("audit_commercial_release.py", project)
            self.assertEqual(tampered.returncode, 2)
            self.assertIn("Evidence hash mismatch", tampered.stdout)

    def test_hash_generation_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            release = Path(temporary) / "release"
            release.mkdir()
            (release / "model.stl").write_bytes(b"solid test\nendsolid test\n")
            (release / "README.md").write_text("Test\n", encoding="utf-8")
            sums = Path(temporary) / "SHA256SUMS"

            generated = run("hash_release.py", release, "--output", sums)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            verified = run("hash_release.py", release, "--verify", sums)
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

            (release / "model.stl").write_bytes(b"tampered")
            failed = run("hash_release.py", release, "--verify", sums)
            self.assertEqual(failed.returncode, 2)
            self.assertIn("hash mismatch", failed.stdout)

    def test_3mf_embed_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            source = temporary_path / "input.3mf"
            output = temporary_path / "output.3mf"
            content_types = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                "</Types>"
            )
            relationships = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
                'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                "</Relationships>"
            )
            model = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<model unit="millimeter" xml:lang="en-US" '
                'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
                "<resources/>"
                "<build/>"
                "</model>"
            )
            with zipfile.ZipFile(source, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("[Content_Types].xml", content_types)
                archive.writestr("_rels/.rels", relationships)
                archive.writestr("3D/3dmodel.model", model)

            embedded = run(
                "embed_3mf_provenance.py",
                source,
                output,
                "--release-id",
                "TEST-2026-001",
                "--designer",
                "Example Seller",
                "--license-terms",
                "See license",
                "--ai-use",
                "AI-assisted; human reviewed",
                "--manifest-uri",
                "provenance.json",
            )
            self.assertEqual(embedded.returncode, 0, embedded.stdout + embedded.stderr)
            verified = run(
                "verify_3mf_provenance.py",
                output,
                "--expect-release-id",
                "TEST-2026-001",
                "--expect-designer",
                "Example Seller",
                "--expect-ai-use",
                "AI-assisted; human reviewed",
                "--expect-manifest-uri",
                "provenance.json",
            )
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)


if __name__ == "__main__":
    unittest.main()
