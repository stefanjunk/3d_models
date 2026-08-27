#!/usr/bin/env python3
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'renders/MM-ORG-008-digital-candidate.png'; LIGHT=np.array([-.5,-.6,.9]); LIGHT/=np.linalg.norm(LIGHT)
def add(ax,path,move,color):
 m=trimesh.load_mesh(path,force='mesh',process=False); m.apply_translation(move); tri=m.vertices[m.faces]; k=.65+.42*(np.clip(m.face_normals@LIGHT,-.4,1)+.4)/1.4; base=np.array(to_rgb(color)); ax.add_collection3d(Poly3DCollection(tri,facecolors=np.clip(base[None,:]*k[:,None]+.04,0,1),edgecolors=(.1,.15,.2,.18),linewidths=.1))
def main():
 fig=plt.figure(figsize=(11,7.8),dpi=150,facecolor='#101620'); ax=fig.add_subplot(111,projection='3d',facecolor='#101620'); add(ax,ROOT/'exports/manufacturing/DRAFT-MM-ORG-008-grid-0.1.0-draft.1.stl',(0,0,0),'#8c6fb2'); add(ax,ROOT/'exports/coupons/DRAFT-MM-ORG-008-diameter-guide-0.1.0-draft.1.stl',(4,-52,0),'#d29558'); ax.set_xlim(-5,170); ax.set_ylim(-58,115); ax.set_zlim(0,70); ax.set_box_aspect((175,173,70)); ax.view_init(elev=29,azim=-57); ax.set_axis_off(); fig.subplots_adjust(left=0,right=1,bottom=.05,top=.88); fig.text(.055,.94,'MM-ORG-008 · CUSTOM LIPSTICK & TUBE GRID',color='#eef4fb',fontsize=17,fontweight='bold'); fig.text(.057,.905,'4 × 3 mixed-diameter grid · separate 14–26 mm capture guide',color='#aebed0',fontsize=10.5); fig.text(.057,.035,'DRAFT digital candidate · real-tube fit, tipping and cleanability pending',color='#91a2b6',fontsize=9); OUT.parent.mkdir(parents=True,exist_ok=True); fig.savefig(OUT,facecolor=fig.get_facecolor(),pad_inches=.08); plt.close(fig); print(OUT)
if __name__=='__main__': main()
