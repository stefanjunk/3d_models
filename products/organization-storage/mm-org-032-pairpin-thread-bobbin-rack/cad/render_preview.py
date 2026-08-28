#!/usr/bin/env python3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "exports/manufacturing/DRAFT-MM-ORG-032-rack-0.1.0-draft.1.stl"
OUT = ROOT / "renders/MM-ORG-032-digital-candidate.png"


def main() -> None:
    mesh = trimesh.load_mesh(STL, force="mesh", process=True)
    fig = plt.figure(figsize=(10, 7), dpi=180, facecolor="#f3efe7"); ax = fig.add_subplot(111, projection="3d", facecolor="#f3efe7")
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor="#9b5570", edgecolor="#4a2634", linewidth=0.08, alpha=0.98))
    center = mesh.bounds.mean(axis=0); span = max(mesh.extents) * 0.60
    ax.set_xlim(center[0] - span, center[0] + span); ax.set_ylim(center[1] - span, center[1] + span); ax.set_zlim(0, max(mesh.bounds[1][2] * 1.1, 1)); ax.view_init(elev=28, azim=-55); ax.set_box_aspect((1.4, 1.0, 0.65)); ax.set_axis_off()
    ax.set_title("MM-ORG-032 · PairPin 8\nParametric digital print candidate", color="#4a2634", fontsize=15, pad=18)
    OUT.parent.mkdir(parents=True, exist_ok=True); plt.tight_layout(); fig.savefig(OUT, bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig); print(OUT)


if __name__ == "__main__": main()
