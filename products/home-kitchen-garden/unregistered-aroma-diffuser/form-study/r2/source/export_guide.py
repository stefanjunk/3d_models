"""Export a densely evaluated petal rib rail for the shared fairness diagnostic."""
import json
from pathlib import Path
import numpy as np
from build_fluent import ROOT
from petal_envelope import envelope

p=json.loads((ROOT/"parameters.json").read_text())
na,nz=12,4096
nb=int(nz*0.55)
np_rows=nz-nb
body_len=(nb+1)*na
row_len=na//2+1
v,_=envelope(p,na=na,nz=nz)
rail=np.concatenate((v[:body_len:na],
                     v[2*body_len+na//4:2*body_len+(np_rows-1)*row_len:row_len],
                     v[2*body_len+2*(np_rows-1)*row_len][None,:]))
target=ROOT/"validation/petal-rail-dense.csv"
np.savetxt(target,rail,delimiter=",",header="x,y,z",comments="")
print(target)
