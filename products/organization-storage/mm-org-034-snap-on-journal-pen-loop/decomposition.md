# Decomposition

| Component | Source of truth | Material | Interface |
|---|---|---|---|
| PETG S/M/L cover clips | `cad/build.py` + parameters | PETG | common external mushroom rail |
| Replaceable loop insert | `cad/build.py` + parameters | TPU | compliant C-socket over rail |
| One-piece universal variant | `cad/build.py` + parameters | TPU | integral cover clip and pen ring |
| Pen fit gauge | `cad/build.py` + parameters | TPU | 9/12/15 mm physical reference bores |
| Material plates | deterministic 3MF builder | PETG or TPU | separate single-material jobs |

Datums: functional X is cover insertion depth, Y is notebook-edge/pen axis, and Z is cover-normal direction. Manufacturing meshes rotate Y onto printer Z. The modular insert is 12 mm wide; the integral TPU loop is flush with one side of its 30 mm cover clip so its ring and connector begin at build-plate Z=0 instead of starting as a floating mid-height section.
