from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

DEPENDENCIES_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("numpy", "PIL", "scipy", "skimage"))
if DEPENDENCIES_AVAILABLE:
    import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
if DEPENDENCIES_AVAILABLE:
    from quantize_texture import map_rgb_to_palette, cleanup_small_islands  # noqa: E402


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "multicolor image dependencies not installed")
class QuantizationTests(unittest.TestCase):
    def test_exact_palette_mapping(self):
        palette = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=float)
        image = palette.reshape(2, 2, 3)
        labels, error = map_rgb_to_palette(image, palette)
        self.assertEqual(labels.tolist(), [[0, 1], [2, 3]])
        self.assertLess(float(error.max()), 1e-5)

    def test_small_island_cleanup(self):
        labels = np.zeros((5, 5), dtype=np.int16)
        labels[2, 2] = 1
        cleaned, report = cleanup_small_islands(labels, 2, 0)
        self.assertEqual(int(cleaned[2, 2]), 0)
        self.assertEqual(report["components_removed"], 1)


if __name__ == "__main__":
    unittest.main()
