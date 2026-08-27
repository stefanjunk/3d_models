import cadquery as cq

from submarine.threads import cut_external_thread, cut_internal_thread


def as_solid(obj) -> cq.Solid:
    sh = obj.val() if hasattr(obj, "val") else obj
    return sh if isinstance(sh, cq.Solid) else sh.Solids()[0]


def test_thread_engagement_zero_interference():
    pitch, depth = 4.0, 1.2
    bore_r = 12.0
    female = (
        cq.Workplane("XY").circle(18).extrude(28)
        - cq.Workplane("XY").circle(bore_r).extrude(28)
    )
    female = cut_internal_thread(female, bore_r, pitch, depth, 28)
    male = cq.Workplane("XY").circle(bore_r - 0.25).extrude(28)
    male = cut_external_thread(male, bore_r - 0.25, pitch, depth, 28)
    inter = as_solid(female).intersect(as_solid(male))
    assert inter.Volume() < 1e-6


def test_thread_cutter_removes_material():
    pitch, depth = 1.5, 1.0
    rod = cq.Workplane("XY").circle(6).extrude(8)
    rod = cut_external_thread(rod, 6, pitch, depth, 8)
    plain = cq.Workplane("XY").circle(6).extrude(8)
    removed = as_solid(plain).Volume() - as_solid(rod).Volume()
    assert removed > 20
