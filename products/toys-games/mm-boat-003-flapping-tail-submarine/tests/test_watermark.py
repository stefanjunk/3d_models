import json
from pathlib import Path

from submarine.geometry import _keel_watermark_cutter


ROOT = Path(__file__).resolve().parents[1]


def test_watermark_identity_and_selector_match(cfg):
    metadata = json.loads(
        (
            ROOT
            / "assets/metrimade-watermark/generated"
            / "MM-BOAT-003_v1.1.0-draft.1_compact"
            / "metrimade-watermark-MM-BOAT-003-v1.1.0-draft.1-compact.json"
        ).read_text()
    )
    selector = json.loads(
        (ROOT / "validation/watermark-selector-v1.1.0-draft.1.json").read_text()
    )
    assert metadata["asset_revision"] == cfg.watermark_asset_revision
    assert metadata["product_id"] == cfg.watermark_product_id
    assert metadata["version"] == cfg.watermark_version
    assert metadata["layout_tier"] == cfg.watermark_layout_tier
    assert metadata["domain_visible"] is True
    assert selector["status"] == "PASS"
    assert selector["selection"]["uniform_scale"] == 1.0


def test_watermark_cutter_fits_safe_keel_region(cfg):
    cutter = _keel_watermark_cutter(cfg).val()
    bb = cutter.BoundingBox()
    keel_x0 = cfg.keel_center_x - cfg.keel_l / 2.0
    keel_x1 = cfg.keel_center_x + cfg.keel_l / 2.0
    keel_y0, keel_y1 = -cfg.keel_w / 2.0, cfg.keel_w / 2.0
    assert bb.xmin - keel_x0 >= 2.0
    assert keel_x1 - bb.xmax >= 2.0
    assert bb.ymin - keel_y0 >= 2.0
    assert keel_y1 - bb.ymax >= 2.0
    assert abs(bb.zlen - (cfg.watermark_depth + cfg.watermark_overlap)) < 1e-6
    assert cfg.keel_wall - cfg.watermark_depth >= 0.8


def test_finished_capsule_has_recess_without_bed_datum_change(parts, cfg):
    capsule = parts["capsule_body"].solid.val()
    cutter = _keel_watermark_cutter(cfg).val()
    keel_bottom_z = -cfg.capsule_od / 2.0 - cfg.keel_h
    assert capsule.intersect(cutter).Volume() < 1e-6
    assert abs(capsule.BoundingBox().zmin - keel_bottom_z) < 1e-5
