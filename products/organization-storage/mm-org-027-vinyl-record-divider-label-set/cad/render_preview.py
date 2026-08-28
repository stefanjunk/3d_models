#!/usr/bin/env python3
"""Render an installed ShelfCue assembly preview from manufacturing meshes."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())
BATCH = json.loads((ROOT / "config/label-batch.json").read_text())
REVISION = PARAMS["project"]["revision"]


def slug(value: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def add_mesh(ax, path: Path, transform, color: str, alpha: float = 1.0) -> None:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    vertices = transform(np.asarray(mesh.vertices))
    faces = vertices[np.asarray(mesh.faces)]
    collection = Poly3DCollection(faces, facecolor=color, edgecolor="#173e48", linewidth=0.08, alpha=alpha)
    ax.add_collection3d(collection)


def carrier_transform(vertices: np.ndarray, carrier_x: float) -> np.ndarray:
    result = np.empty_like(vertices)
    result[:, 0] = vertices[:, 2] + carrier_x
    result[:, 1] = vertices[:, 0] + 2.4
    result[:, 2] = vertices[:, 1]
    return result


def cap_transform(vertices: np.ndarray, cap_x: float) -> np.ndarray:
    result = np.empty_like(vertices)
    result[:, 0] = vertices[:, 0] + cap_x
    result[:, 1] = vertices[:, 2]
    result[:, 2] = vertices[:, 1] + 15.0
    return result


def main() -> None:
    carrier_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-027-smooth-carrier-print-six-{REVISION}.stl"
    fig = plt.figure(figsize=(12, 7), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    for assembly_index, item in enumerate(BATCH["labels"][:3]):
        cap_x = assembly_index * 105.0
        slot_local_x = PARAMS["label_cap"]["width_mm"] / 2.0 + item["slot_center_x_mm"]
        carrier_x = cap_x + slot_local_x - PARAMS["carrier"]["thickness_mm"] / 2.0
        cap_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-027-label-cap-{item['index']:02d}-{slug(item['normalized_label'])}-{REVISION}.stl"
        add_mesh(ax, carrier_path, lambda vertices, x=carrier_x: carrier_transform(vertices, x), "#3b6f78", 0.92)
        add_mesh(ax, cap_path, lambda vertices, x=cap_x: cap_transform(vertices, x), "#e0a83d", 1.0)
    ax.set_xlim(-5, 295)
    ax.set_ylim(-5, 240)
    ax.set_zlim(0, 70)
    ax.set_box_aspect((300, 245, 85))
    ax.view_init(elev=26, azim=-62)
    ax.set_title("MM-ORG-027 ShelfCue — three installed tab offsets", fontsize=15, pad=18)
    ax.set_xlabel("shelf row / label width (mm)")
    ax.set_ylabel("carrier depth into shelf (mm)")
    ax.set_zlabel("height (mm)")
    ax.grid(False)
    fig.patch.set_facecolor("#f2eee5")
    ax.set_facecolor("#f2eee5")
    output = ROOT / "renders/MM-ORG-027-digital-candidate.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    print(json.dumps({"status": "PASS", "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
