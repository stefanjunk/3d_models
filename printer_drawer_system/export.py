"""
Export all parts to STL.

Run:
    cd printer_drawer_system
    python export.py
"""

import sys
import pathlib
import cadquery as cq

OUT = pathlib.Path(__file__).parent / "stl"
OUT.mkdir(exist_ok=True)

def save(name: str, shape):
    path = str(OUT / f"{name}.stl")
    cq.exporters.export(shape if isinstance(shape, cq.Shape) else shape.val(), path)
    print(f"  ✓  {path}")

print("Building frame …")
import frame
save("frame", frame.frame)

print("Building drawers …")
import drawer
save("drawer_standard", drawer.drawer_std)
save("drawer_tall",     drawer.drawer_tall)

print("Building nozzle insert …")
import insert_nozzles
save("insert_nozzles", insert_nozzles.insert)

print("Building screw insert …")
import insert_screws
save("insert_screws", insert_screws.insert)

print("Building tool insert …")
import insert_tools
save("insert_tools", insert_tools.insert)

print("\nAll done →", OUT)
