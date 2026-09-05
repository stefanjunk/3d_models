"""R3 study: two continuous ribbed petals, not a cut wavy vessel rim.

Exact body/root correspondence; crown ribs converge with petal width.
The tip pole is explicitly closed; there are no coincident zero-area quads.
"""
import math
import numpy as np
from build_fluent import spline, smoothstep


def envelope(p, na=None, nz=None):
    na = na or p["angular_samples"]
    if na % 4:
        raise ValueError("Angular resolution must be divisible by four")
    nz = nz or p["height_samples"]
    split = p.get("petal_split_fraction", 0.55)
    body_n = int(nz * split)
    petal_n = nz - body_n
    vertices, faces = [], []
    radius_curve = spline(p["radius_stations"])
    center_curve = spline(p["center_x_stations"])
    twist_curve = spline(p["twist_stations"])

    def xyz(z, u, angle_material=None, petal_s=None, inner=False):
        h = z / p["height_mm"]
        theta = u if angle_material is None else angle_material
        angle = theta + math.radians(15 + p["twist_deg"] * float(twist_curve(h)))
        amp = p["rib_depth_mm"] * float(smoothstep((h-.035)/.18))
        amp *= 1 - .80 * float(smoothstep((h-.73)/.27))
        if petal_s is not None:
            amp *= 1-float(smoothstep((petal_s-.45)/.55))
        ridge = (.5+.5*math.cos(p["rib_count"]*u))**2
        rmid = float(radius_curve(h)) - p["radial_shell_mm"]/2 + amp*ridge
        thickness = p["radial_shell_mm"]
        if petal_s is not None:
            # Soft pole cap over the final 4% of petal length.
            q = max(0, (petal_s-.96)/.04)
            thickness *= math.sqrt(max(0,1-q*q))
        r = rmid + (-.5 if inner else .5)*thickness
        return ((r*math.cos(angle)+float(center_curve(h)))*p["width_mm"]/92,
                r*math.sin(angle)*p["depth_mm"]/92,z)

    body = []
    for inner in (False, True):
        rows = []
        for z in np.linspace(p["foot_height_mm"], split*p["height_mm"], body_n+1):
            row = []
            for i in range(na):
                row.append(len(vertices))
                vertices.append(xyz(float(z),2*math.pi*i/na,inner=inner))
            rows.append(row)
        body.append(rows)
        for j in range(body_n):
            for i in range(na):
                k=(i+1)%na
                q=(rows[j][i],rows[j][k],rows[j+1][k],rows[j+1][i])
                faces.append(q[::-1] if inner else q)
    for i in range(na):
        k=(i+1)%na
        faces.append((body[1][0][i],body[1][0][k],body[0][0][k],body[0][0][i]))

    # Two petals share the body root ring; the edges separate above that ring.
    for petal in (0,1):
        center = petal*math.pi
        top_z = p["height_mm"]*(1 - 2*p["crown_asymmetry_fraction"]*petal)
        zstart = split*p["height_mm"]
        indices=[(int(petal*na/2-na/4)+i)%na for i in range(na//2+1)]
        qs=np.linspace(-1,1,len(indices))
        surfaces=[]
        for inner in (False,True):
            rows=[[body[int(inner)][-1][i] for i in indices]]
            for j in range(1,petal_n):
                s=j/petal_n
                z=zstart+(top_z-zstart)*s
                halfwidth=(math.pi/2)*math.sqrt(max(0,1-s**1.35))
                row=[]
                for q in qs:
                    row.append(len(vertices))
                    vertices.append(xyz(z,center+q*math.pi/2,
                                        center+q*halfwidth,s,inner))
                rows.append(row)
            surfaces.append(rows)
            for j in range(petal_n-1):
                for i in range(len(indices)-1):
                    q=(rows[j][i],rows[j][i+1],rows[j+1][i+1],rows[j+1][i])
                    faces.append(q[::-1] if inner else q)
        for j in range(petal_n-1):
            left=(surfaces[0][j][0],surfaces[0][j+1][0],surfaces[1][j+1][0],surfaces[1][j][0])
            right=(surfaces[0][j][-1],surfaces[1][j][-1],surfaces[1][j+1][-1],surfaces[0][j+1][-1])
            faces.extend((left,right))
        tip=len(vertices)
        vertices.append(xyz(top_z,center,center,1.0,False))
        outer,inner=surfaces[0][-1],surfaces[1][-1]
        for i in range(len(indices)-1):
            faces.append((outer[i],outer[i+1],tip))
            faces.append((inner[i+1],inner[i],tip))
        faces.extend(((outer[0],tip,inner[0]),(outer[-1],inner[-1],tip)))
    return np.array(vertices),faces
