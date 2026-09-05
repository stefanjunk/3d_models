"""Regression checks for preserving product-owned assessments during intake."""

import contextlib
import dataclasses
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import backfill_product_preflights as backfill


class BackfillPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.products = self.root / "products"
        self.product = self.products / "art-decor/mm-art-001-fox-mesh-collection"
        source = ROOT / "products/art-decor/mm-art-001-fox-mesh-collection"
        for relative in (
            "PURPOSE.md", "design-spec.yaml", "preflight/preflight-result.json",
            "preflight/preflight-input.yaml", "preflight/preflight-report.md",
        ):
            target = self.product / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
        for name, value in (
            ("REPO_ROOT", self.root), ("PRODUCTS_ROOT", self.products),
            ("ARCHIVE_MOVES", {}), ("ROOT_REVIEW_EXCEPTIONS", {}),
        ):
            patcher = patch.object(backfill, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.context = backfill.build_context(self.product, "2026-09-05T00:00:00+02:00")
        self.result_path = self.product / "preflight/preflight-result.json"
        self.result = json.loads(self.result_path.read_text())

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def run_cli(self, *arguments):
        output = io.StringIO()
        with patch.object(sys, "argv", ["backfill", *arguments]), contextlib.redirect_stdout(output):
            status = backfill.main()
        return status, json.loads(output.getvalue())

    def test_mode_case_preserves_product_bytes(self):
        spec_path = self.product / "design-spec.yaml"
        for mode in ("RETROSPECTIVE", "retrospective"):
            with self.subTest(mode=mode):
                spec = yaml.safe_load(spec_path.read_text())
                spec["workflow"]["preflight"]["mode"] = mode
                spec_path.write_text(yaml.safe_dump(spec, sort_keys=False))
                before = self.snapshot()
                result, changed = backfill.process_product(self.context, write=True)
                self.assertEqual(self.result, result)
                self.assertEqual([], changed)
                self.assertEqual(before, self.snapshot())

    def test_inventory_revision_does_not_replace_assessment_revision(self):
        context = dataclasses.replace(self.context, revision="99.0.0")
        before = self.snapshot()
        result, changed = backfill.process_product(context, write=True)
        audit = backfill.portfolio_audit([context], {context.key: result}, [], "2026-09-05")
        self.assertEqual(self.result["traceability"]["project_revision"], audit["products"][0]["revision"])
        self.assertEqual([], changed)
        self.assertEqual(before, self.snapshot())

    def test_product_authored_purpose_heading_is_preserved(self):
        path = self.product / "PURPOSE.md"
        path.write_text("# Fox collection\n\nDecorative fox meshes for dry indoor display.\n")
        before = self.snapshot()
        self.assertEqual(self.result, backfill.existing_current_result(self.context))
        self.assertEqual(before, self.snapshot())
        self.assertFalse(backfill.valid_purpose("# Fox collection\n"))
        self.assertFalse(backfill.valid_purpose("# Fox collection\n\nTODO\n"))

    def test_broken_existing_intake_blocks_all_writes(self):
        # This new product sorts first and would otherwise get written before
        # the broken existing product is discovered.
        new = self.products / "aaa/mm-new-001-empty-intake"
        new.mkdir(parents=True)
        broken = self.product / "preflight/preflight-report.md"
        broken.unlink()
        before = self.snapshot()
        status, report = self.run_cli("--write")
        self.assertEqual(1, status)
        self.assertTrue(report["blocked"])
        self.assertEqual(0, report["changed_files"])
        self.assertEqual(before, self.snapshot())

    def test_invalid_existing_result_is_never_regenerated(self):
        for content in ("{broken", "{}", json.dumps({**self.result, "gates": {}})):
            with self.subTest(content=content[:30]):
                self.result_path.write_text(content)
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    backfill.process_product(self.context, write=True)
                self.assertEqual(before, self.snapshot())

    def test_stale_workflow_link_is_never_auto_approved(self):
        self.result["assessment_version"] = "99.0.0"
        self.result_path.write_text(json.dumps(self.result))
        before = self.snapshot()
        status, report = self.run_cli("--write")
        self.assertEqual(1, status)
        self.assertTrue(report["errors"])
        self.assertEqual(before, self.snapshot())

    def test_missing_result_with_existing_companions_is_not_backfilled(self):
        self.result_path.unlink()
        before = self.snapshot()
        status, report = self.run_cli("--write")
        self.assertEqual(1, status)
        self.assertTrue(report["blocked"])
        self.assertEqual(before, self.snapshot())

    def test_other_project_identity_is_rejected(self):
        self.result["traceability"]["project_id"] = "MM-OTHER-001"
        self.result_path.write_text(json.dumps(self.result))
        with self.assertRaises(ValueError):
            backfill.existing_current_result(self.context)

    def test_new_backfill_and_aggregate_are_idempotent(self):
        new = self.products / "art-decor/mm-art-999-decoration"
        new.mkdir()
        status, report = self.run_cli("--write")
        self.assertEqual(0, status)
        self.assertGreater(report["changed_files"], 0)
        result = json.loads((new / "preflight/preflight-result.json").read_text())
        self.assertEqual("RETROSPECTIVE", result["traceability"]["mode"])
        self.assertEqual([], backfill.validate_document(result)[0])
        before = self.snapshot()
        status, report = self.run_cli()
        self.assertEqual(0, status)
        self.assertEqual([], report["changed_paths"])
        self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
