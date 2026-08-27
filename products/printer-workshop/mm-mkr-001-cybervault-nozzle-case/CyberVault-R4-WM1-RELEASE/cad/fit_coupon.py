#!/usr/bin/env python3
"""Generate a three-variant Kobra 3 Max quick-swap nozzle fit coupon.

The geometry is a single height-field solid.  This intentionally limits the
coupon to support-free, open saddles and avoids claiming a full reconstruction
from one product image.  Units are millimetres.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import struct
import zipfile

import numpy as np


@dataclass(frozen=True)
class CouponParams:
    plate_length: float = 56.0
    plate_width: float = 44.0
    base_thickness: float = 2.4
    saddle_axis_z: float = 8.0
    grid_mm: float = 0.25

    nozzle_length: float = 45.0
    upper_diameter: float = 5.0
    lower_diameter_estimate: float = 5.6
    flange_free_width: float = 11.0

    clearances_each_side: tuple[float, ...] = (0.25, 0.35, 0.45)
    row_centres: tuple[float, ...] = (7.5, 22.0, 36.5)
    saddle_width: float = 11.5

    rear_stop_x0: float = 1.0
    rear_stop_x1: float = 3.0
    upper_saddle_x0: float = 4.0
    upper_saddle_x1: float = 12.0
    lower_saddle_x0: float = 23.0
    lower_saddle_x1: float = 35.0

    marker_height: float = 0.6
    marker_radius: float = 0.55

    def validate(self) -> None:
        assert self.plate_length > self.nozzle_length + self.rear_stop_x1
        assert self.plate_width > 0 and self.base_thickness >= 2.0
        assert self.saddle_axis_z > self.base_thickness
        assert len(self.clearances_each_side) == len(self.row_centres) == 3
        assert all(c > 0 for c in self.clearances_each_side)
        assert self.flange_free_width >= 10.5
        assert self.lower_saddle_x1 < self.nozzle_length
        assert self.grid_mm <= 0.30


def _inside(value: np.ndarray, low: float, high: float) -> np.ndarray:
    return (value >= low) & (value <= high)


def build_top_surface(p: CouponParams) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return regular X/Y grids and a printable top surface Z."""
    p.validate()
    nx = int(round(p.plate_length / p.grid_mm)) + 1
    ny = int(round(p.plate_width / p.grid_mm)) + 1
    xs = np.linspace(0.0, p.plate_length, nx, dtype=np.float64)
    ys = np.linspace(0.0, p.plate_width, ny, dtype=np.float64)
    x, y = np.meshgrid(xs, ys, indexing="xy")
    z = np.full_like(x, p.base_thickness)

    for row_index, (yc, clearance) in enumerate(
        zip(p.row_centres, p.clearances_each_side, strict=True)
    ):
        half_block = p.saddle_width / 2.0
        row_band = np.abs(y - yc) <= half_block

        # Flat axial datum at the rear end.  It is deliberately narrower than
        # the free flange region and does not clamp the nozzle.
        stop = row_band & _inside(x, p.rear_stop_x0, p.rear_stop_x1)
        z[stop] = np.maximum(z[stop], p.saddle_axis_z)

        for x0, x1, nominal_diameter in (
            (p.upper_saddle_x0, p.upper_saddle_x1, p.upper_diameter),
            (p.lower_saddle_x0, p.lower_saddle_x1, p.lower_diameter_estimate),
        ):
            block = row_band & _inside(x, x0, x1)
            z[block] = np.maximum(z[block], p.saddle_axis_z)

            radius = nominal_diameter / 2.0 + clearance
            dy = np.abs(y - yc)
            groove = block & (dy <= radius)
            groove_floor = p.saddle_axis_z - np.sqrt(
                np.maximum(0.0, radius * radius - dy * dy)
            )
            z[groove] = np.minimum(z[groove], groove_floor[groove])

        # One/two/three dots identify 0.25/0.35/0.45 mm without relying on
        # fine printed text.  Marker count follows row order.
        marker_count = row_index + 1
        marker_centres = np.linspace(
            52.5 - (marker_count - 1),
            52.5 + (marker_count - 1),
            marker_count,
        )
        for mx in marker_centres:
            marker = (x - mx) ** 2 + (y - yc) ** 2 <= p.marker_radius**2
            z[marker] = np.maximum(z[marker], p.base_thickness + p.marker_height)

    return xs, ys, z


def mesh_height_field(
    xs: np.ndarray, ys: np.ndarray, z: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Build a closed, consistently oriented triangle mesh."""
    ny, nx = z.shape
    assert nx == len(xs) and ny == len(ys)

    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    top = np.column_stack((xx.ravel(), yy.ravel(), z.ravel()))
    bottom = np.column_stack((xx.ravel(), yy.ravel(), np.zeros(nx * ny)))
    vertices = np.vstack((top, bottom)).astype(np.float64)

    top_idx = np.arange(nx * ny, dtype=np.int64).reshape(ny, nx)
    bot_idx = top_idx + nx * ny
    tris: list[tuple[int, int, int]] = []

    for j in range(ny - 1):
        for i in range(nx - 1):
            t00 = int(top_idx[j, i])
            t10 = int(top_idx[j, i + 1])
            t11 = int(top_idx[j + 1, i + 1])
            t01 = int(top_idx[j + 1, i])
            b00 = int(bot_idx[j, i])
            b10 = int(bot_idx[j, i + 1])
            b11 = int(bot_idx[j + 1, i + 1])
            b01 = int(bot_idx[j + 1, i])
            tris.extend(
                (
                    (t00, t10, t11),
                    (t00, t11, t01),
                    (b00, b11, b10),
                    (b00, b01, b11),
                )
            )

    # y = 0, outward -Y
    for i in range(nx - 1):
        b0, b1 = int(bot_idx[0, i]), int(bot_idx[0, i + 1])
        t0, t1 = int(top_idx[0, i]), int(top_idx[0, i + 1])
        tris.extend(((b0, b1, t1), (b0, t1, t0)))

    # y = max, outward +Y
    for i in range(nx - 1):
        b0, b1 = int(bot_idx[-1, i]), int(bot_idx[-1, i + 1])
        t0, t1 = int(top_idx[-1, i]), int(top_idx[-1, i + 1])
        tris.extend(((b0, t1, b1), (b0, t0, t1)))

    # x = 0, outward -X
    for j in range(ny - 1):
        b0, b1 = int(bot_idx[j, 0]), int(bot_idx[j + 1, 0])
        t0, t1 = int(top_idx[j, 0]), int(top_idx[j + 1, 0])
        tris.extend(((b0, t1, b1), (b0, t0, t1)))

    # x = max, outward +X
    for j in range(ny - 1):
        b0, b1 = int(bot_idx[j, -1]), int(bot_idx[j + 1, -1])
        t0, t1 = int(top_idx[j, -1]), int(top_idx[j + 1, -1])
        tris.extend(((b0, b1, t1), (b0, t1, t0)))

    return vertices, np.asarray(tris, dtype=np.int64)


def triangle_metrics(
    vertices: np.ndarray, triangles: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    a = vertices[triangles[:, 0]]
    b = vertices[triangles[:, 1]]
    c = vertices[triangles[:, 2]]
    cross = np.cross(b - a, c - a)
    twice_area = np.linalg.norm(cross, axis=1)
    normals = np.zeros_like(cross)
    good = twice_area > 1e-12
    normals[good] = cross[good] / twice_area[good, None]
    return normals, twice_area * 0.5, np.einsum("ij,ij->i", a, np.cross(b, c)) / 6.0


def validate_mesh(vertices: np.ndarray, triangles: np.ndarray) -> dict[str, object]:
    normals, areas, signed_tetra = triangle_metrics(vertices, triangles)
    edges = np.vstack(
        (
            triangles[:, [0, 1]],
            triangles[:, [1, 2]],
            triangles[:, [2, 0]],
        )
    )
    edges.sort(axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    bbox_min = vertices.min(axis=0)
    bbox_max = vertices.max(axis=0)
    report: dict[str, object] = {
        "mesh_revision": "FIT-COUPON-DRAFT-A",
        "units": "mm",
        "vertex_count": int(len(vertices)),
        "triangle_count": int(len(triangles)),
        "bounding_box_min_mm": bbox_min.round(6).tolist(),
        "bounding_box_max_mm": bbox_max.round(6).tolist(),
        "bounding_box_size_mm": (bbox_max - bbox_min).round(6).tolist(),
        "signed_volume_mm3": float(signed_tetra.sum()),
        "surface_area_mm2": float(areas.sum()),
        "degenerate_triangle_count": int(np.count_nonzero(areas <= 1e-12)),
        "edge_incidence": {
            "minimum": int(counts.min()),
            "maximum": int(counts.max()),
            "non_two_count": int(np.count_nonzero(counts != 2)),
        },
        "watertight_by_indexed_edge_test": bool(np.all(counts == 2)),
        "outward_oriented_by_positive_volume": bool(signed_tetra.sum() > 0),
        "finite_normals": bool(np.isfinite(normals).all()),
    }
    report["status"] = "PASS" if (
        report["watertight_by_indexed_edge_test"]
        and report["outward_oriented_by_positive_volume"]
        and report["degenerate_triangle_count"] == 0
    ) else "FAIL"
    return report


def write_binary_stl(
    path: Path, vertices: np.ndarray, triangles: np.ndarray, title: str
) -> None:
    normals, _, _ = triangle_metrics(vertices, triangles)
    header = title.encode("ascii", "replace")[:80].ljust(80, b" ")
    with path.open("wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", len(triangles)))
        for normal, tri in zip(normals, triangles, strict=True):
            a, b, c = vertices[tri]
            fh.write(
                struct.pack(
                    "<12fH",
                    *normal.astype(np.float32),
                    *a.astype(np.float32),
                    *b.astype(np.float32),
                    *c.astype(np.float32),
                    0,
                )
            )


def write_3mf(path: Path, vertices: np.ndarray, triangles: np.ndarray) -> None:
    vertex_xml = "".join(
        f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>'
        for x, y, z in vertices
    )
    triangle_xml = "".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in triangles
    )
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="de-DE" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<metadata name="Title">Kobra 3 Max Fit Coupon DRAFT</metadata>'
        '<metadata name="Designer">JuSt Innovation</metadata>'
        '<resources><object id="1" type="model"><mesh><vertices>'
        + vertex_xml
        + '</vertices><triangles>'
        + triangle_xml
        + '</triangles></mesh></object></resources>'
        '<build><item objectid="1"/></build></model>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>'
    )
    relationships = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("3D/3dmodel.model", model)


def write_preview(path: Path, xs: np.ndarray, ys: np.ndarray, z: np.ndarray) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x, y = np.meshgrid(xs, ys, indexing="xy")
    stride = max(1, int(round(1.0 / (xs[1] - xs[0]))))
    fig = plt.figure(figsize=(13.5, 7.5), constrained_layout=True)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    ax.plot_surface(
        x[::stride, ::stride],
        y[::stride, ::stride],
        z[::stride, ::stride],
        cmap="viridis",
        linewidth=0.15,
        edgecolor=(0.1, 0.1, 0.12, 0.28),
        antialiased=True,
    )
    ax.view_init(elev=28, azim=-58)
    ax.set_box_aspect((56, 44, 18))
    ax.set_title("Kobra 3 Max Passcoupon – DRAFT")
    ax.set_xlabel("Duesenachse X [mm]")
    ax.set_ylabel("Varianten Y [mm]")
    ax.set_zlabel("Z [mm]")

    top = fig.add_subplot(1, 2, 2)
    image = top.imshow(
        z,
        origin="lower",
        extent=(xs[0], xs[-1], ys[0], ys[-1]),
        cmap="viridis",
        aspect="equal",
    )
    labels = ("1 Punkt: 0,25", "2 Punkte: 0,35", "3 Punkte: 0,45")
    for yc, label in zip(CouponParams().row_centres, labels, strict=True):
        top.text(0.8, yc, label, va="center", ha="left", fontsize=9, color="white")
    top.set_title("Draufsicht und Varianten [mm Spiel je Seite]")
    top.set_xlabel("X [mm]")
    top.set_ylabel("Y [mm]")
    fig.colorbar(image, ax=top, shrink=0.72, label="Oberflaechenhoehe Z [mm]")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--grid-mm", type=float, default=0.25)
    args = parser.parse_args()

    p = CouponParams(grid_mm=args.grid_mm)
    project_dir = args.project_dir.resolve()
    export_dir = project_dir / "exports" / "draft"
    report_dir = project_dir / "reports"
    render_dir = project_dir / "renders"
    export_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)

    xs, ys, z = build_top_surface(p)
    vertices, triangles = mesh_height_field(xs, ys, z)
    validation = validate_mesh(vertices, triangles)
    validation["parameters"] = asdict(p)
    validation["physical_qualification"] = "PENDING"
    validation["release_status"] = "DRAFT"
    if validation["status"] != "PASS":
        raise RuntimeError(f"Coupon mesh validation failed: {validation}")

    stl_path = export_dir / "kobra3max_fit_coupon_DRAFT.stl"
    three_mf_path = export_dir / "kobra3max_fit_coupon_DRAFT.3mf"
    report_path = report_dir / "fit-coupon-validation.json"
    preview_path = render_dir / "fit-coupon-preview.png"

    write_binary_stl(stl_path, vertices, triangles, "Kobra 3 Max fit coupon DRAFT")
    write_3mf(three_mf_path, vertices, triangles)
    report_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    write_preview(preview_path, xs, ys, z)

    print(json.dumps({
        "status": validation["status"],
        "stl": str(stl_path),
        "3mf": str(three_mf_path),
        "report": str(report_path),
        "preview": str(preview_path),
        "triangles": validation["triangle_count"],
        "bbox_mm": validation["bounding_box_size_mm"],
    }, indent=2))


if __name__ == "__main__":
    main()
