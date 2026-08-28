#!/usr/bin/env python3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

ROOT=Path(__file__).resolve().parents[1]; REV="0.1.0-draft.1"


def main():
    names=["round-corner","rectangular-notch","skewed-corner"]; poses=[(0,0,0),(155,0,0),(0,155,0)]; colors=["#3d9997","#e0a83d","#5caf9f"]
    fig=plt.figure(figsize=(12,8),dpi=160); ax=fig.add_subplot(111,projection="3d")
    for name,pose,color in zip(names,poses,colors):
        mesh=trimesh.load_mesh(ROOT/f"exports/manufacturing/DRAFT-MM-ORG-030-{name}-{REV}.stl",force="mesh",process=False); mesh.apply_translation(pose); ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces],facecolor=color,edgecolor="#243b42",linewidth=.08))
    ax.set_xlim(0,305); ax.set_ylim(0,305); ax.set_zlim(0,100); ax.set_box_aspect((305,305,100)); ax.view_init(elev=32,azim=-53); ax.set_title("MM-ORG-030 · DrawerFit CornerLab 3 digital candidate",pad=18); ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Z (mm)"); ax.grid(False); fig.patch.set_facecolor("#f3efe6"); ax.set_facecolor("#f3efe6"); fig.tight_layout(); output=ROOT/"renders/MM-ORG-030-digital-candidate.png"; fig.savefig(output,bbox_inches="tight"); print(output)


if __name__=="__main__": main()
