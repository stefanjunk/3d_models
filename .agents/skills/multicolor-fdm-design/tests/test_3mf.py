from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

TRIMESH_AVAILABLE = importlib.util.find_spec("trimesh") is not None
if TRIMESH_AVAILABLE:
    import trimesh

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
if TRIMESH_AVAILABLE:
    from three_mf import write_multicolor_3mf  # noqa: E402
    from validate_multicolor_3mf import validate  # noqa: E402


@unittest.skipUnless(TRIMESH_AVAILABLE, "trimesh not installed")
class ThreeMFTests(unittest.TestCase):
    def test_write_and_validate_two_part_assembly(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            a = trimesh.creation.box([10, 10, 2])
            b = trimesh.creation.box([4, 4, 1])
            b.apply_translation([0, 0, 1.5])
            a_path = root / "a.stl"
            b_path = root / "b.stl"
            a.export(a_path)
            b.export(b_path)
            out = root / "test.3mf"
            report = write_multicolor_3mf([
                {"id": "base", "material_name": "Base", "display_hex": "#FF0000", "path": str(a_path)},
                {"id": "accent", "material_name": "Accent", "display_hex": "#FFFFFF", "path": str(b_path)},
            ], out)
            self.assertEqual(report["part_count"], 2)
            validation = validate(out)
            self.assertTrue(validation["valid"], json.dumps(validation, indent=2))
            self.assertEqual(validation["mesh_object_count"], 2)
            self.assertEqual(validation["assembly_object_count"], 1)


if __name__ == "__main__":
    unittest.main()
