#!/usr/bin/env python3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"exports/master/DRAFT-MM-ORG-005-kit-preview-0.1.0-draft.1.stl"
OUTPUT=ROOT/"renders/MM-ORG-005-digital-candidate.png"

def main():
    m=trimesh.load_mesh(SOURCE,force="mesh",process=False); tri=m.vertices[m.faces]
    fig=plt.figure(figsize=(11,7.8),dpi=150,facecolor="#101620"); ax=fig.add_subplot(111,projection="3d",facecolor="#101620")
    ax.add_collection3d(Poly3DCollection(tri,facecolors="#6f879d",edgecolors=(0.12,0.17,0.22,0.32),linewidths=.16))
    b=m.bounds; e=m.extents; ax.set_xlim(b[0,0]-8,b[1,0]+8); ax.set_ylim(b[0,1]-8,b[1,1]+8); ax.set_zlim(-3,max(35,b[1,2]+8)); ax.set_box_aspect((e[0]+16,e[1]+16,38)); ax.view_init(elev=30,azim=-58); ax.set_axis_off(); fig.subplots_adjust(left=0,right=1,bottom=.05,top=.88)
    fig.text(.055,.94,"MM-ORG-005 · DESK-EDGE CABLE CLIP KIT",color="#eef4fb",fontsize=18,fontweight="bold"); fig.text(.057,.905,"12 / 15 / 18 mm desk targets · 3.5 / 5.0 / 7.0 mm cable presets",color="#aebed0",fontsize=10.5); fig.text(.057,.035,"DRAFT digital candidate · PETG force, fatigue, pinch and marking tests pending",color="#91a2b6",fontsize=9)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); fig.savefig(OUTPUT,facecolor=fig.get_facecolor(),pad_inches=.08); plt.close(fig); print(OUTPUT)
if __name__=="__main__": main()
