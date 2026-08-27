#!/usr/bin/env python3
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np, trimesh
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"renders/MM-ORG-006-digital-candidate.png"; LIGHT=np.array([-.45,-.7,.85]); LIGHT=LIGHT/np.linalg.norm(LIGHT)
def add(ax,path,move,color):
    m=trimesh.load_mesh(path,force="mesh",process=False); m.apply_translation(move); tri=m.vertices[m.faces]; intensity=np.clip(m.face_normals@LIGHT,-.4,1); intensity=.68+.42*(intensity+.4)/1.4; base=np.array(to_rgb(color)); colors=np.clip(base[None,:]*intensity[:,None]+.05,0,1); ax.add_collection3d(Poly3DCollection(tri,facecolors=colors,edgecolors=(.12,.17,.22,.22),linewidths=.12))
def main():
    p=__import__('json').load(open(ROOT/"config/model-parameters.json")); xs=[(j-(p['bar']['socket_count']-1)/2)*p['bar']['socket_pitch'] for j in range(p['bar']['socket_count'])]; bar=ROOT/f"exports/manufacturing/DRAFT-MM-ORG-006-bar-0.1.0-draft.1.stl"
    fig=plt.figure(figsize=(11,7.8),dpi=150,facecolor="#101620"); ax=fig.add_subplot(111,projection="3d",facecolor="#101620"); add(ax,bar,(0,0,0),"#60788f")
    bar_bounds=trimesh.load_mesh(bar,force='mesh').bounds; x0=(bar_bounds[0,0]+bar_bounds[1,0])/2; y0=(bar_bounds[0,1]+bar_bounds[1,1])/2
    for x,d in zip(xs,p['insert']['cable_diameters']):
        key=str(d).replace('.','p'); path=ROOT/f"exports/manufacturing/DRAFT-MM-ORG-006-insert_{key}-0.1.0-draft.1.stl"; m=trimesh.load_mesh(path,force='mesh'); add(ax,path,(x0+x-m.extents[0]/2,y0-m.extents[1]/2,p['socket']['pocket_floor']),"#e38a56")
    ax.set_xlim(-10,175); ax.set_ylim(-12,58); ax.set_zlim(-3,38); ax.set_box_aspect((185,70,41)); ax.view_init(elev=27,azim=-60); ax.set_axis_off(); fig.subplots_adjust(left=0,right=1,bottom=.05,top=.88); fig.text(.055,.94,"MM-ORG-006 · CHARGING-CABLE DOCKING BAR",color="#eef4fb",fontsize=18,fontweight="bold"); fig.text(.057,.905,"PETG datum bar · four replaceable TPU cable cartridges",color="#aebed0",fontsize=10.5); fig.text(.057,.035,"DRAFT digital candidate · exact PETG/TPU fit, cycles and stability pending",color="#91a2b6",fontsize=9); OUT.parent.mkdir(parents=True,exist_ok=True); fig.savefig(OUT,facecolor=fig.get_facecolor(),pad_inches=.08); plt.close(fig); print(OUT)
if __name__=="__main__": main()
