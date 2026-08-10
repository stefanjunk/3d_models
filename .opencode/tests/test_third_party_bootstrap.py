import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[2] / "libraries" / "scripts" / "bootstrap_third_party.py"
LOCK = Path(__file__).parents[2] / "libraries" / "third-party-lock.json"
AVAILABLE = SCRIPT.is_file() and LOCK.is_file()
if AVAILABLE:
    SPEC = importlib.util.spec_from_file_location("bootstrap_third_party", SCRIPT)
    MODULE = importlib.util.module_from_spec(SPEC)
    assert SPEC and SPEC.loader
    SPEC.loader.exec_module(MODULE)
else:
    MODULE = None


@unittest.skipUnless(
    AVAILABLE,
    "optional pinned third-party library infrastructure is not installed in this checkout",
)
class ThirdPartyBootstrapTests(unittest.TestCase):
    def test_reset_directory_removes_stale_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "dependency"
            target.mkdir()
            (target / "stale.txt").write_text("old", encoding="utf-8")

            MODULE.reset_directory(target)

            self.assertTrue(target.is_dir())
            self.assertFalse((target / "stale.txt").exists())

    def test_atomic_replace_keeps_new_content_and_removes_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            staged = root / "staged"
            target.mkdir()
            staged.mkdir()
            (target / "old.txt").write_text("old", encoding="utf-8")
            (staged / "new.txt").write_text("new", encoding="utf-8")

            MODULE.atomic_replace_directory(staged, target)

            self.assertFalse((target / "old.txt").exists())
            self.assertEqual((target / "new.txt").read_text(encoding="utf-8"), "new")
            self.assertFalse((root / "target.previous").exists())

    def test_lock_records_full_cadquery_compatibility_fingerprint(self) -> None:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        cq = next(item for item in lock["libraries"] if item["name"] == "cq_warehouse")

        self.assertRegex(cq["compatibility"]["python"], r"^\d+\.\d+\.\d+$")
        self.assertIn("cadquery", cq["compatibility"]["packages"])
        self.assertIn("cadquery-ocp", cq["compatibility"]["packages"])


if __name__ == "__main__":
    unittest.main()
