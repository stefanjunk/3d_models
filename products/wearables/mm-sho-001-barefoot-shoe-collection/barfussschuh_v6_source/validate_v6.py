#!/usr/bin/env python3
from pathlib import Path
import json
import trimesh

HERE=Path(__file__).resolve().parent
cfg=json.loads((HERE/'v6_config.json').read_text())
required=[
 'v6_sole_body_left.stl','v6_curved_lip_left.stl',
 'v6_upper_infill_envelope_left.stl','v6_upper_reinforcement_frame_left.stl',
 'v6_upper_fuzzy_shell_left.stl'
]
checks={}
ok=True
for name in required:
    p=HERE/name
    exists=p.exists(); checks[name]={'exists':exists}
    if not exists:
        ok=False; continue
    m=trimesh.load(p,force='mesh',process=True)
    checks[name].update(watertight=bool(m.is_watertight),components=int(len(m.split(only_watertight=False))),faces=int(len(m.faces)))
    ok &= bool(m.is_watertight)

checks['design_rules']={
 'lip_overlap_ge_2mm': cfg['lip_textile_overlap']>=2.0,
 'hex_line_ge_0_7mm': cfg['hex_line_width']>=0.7,
 'fuzzy_wall_ge_1_2mm_default_mesh': cfg['upper_fuzzy_wall_thickness']>=1.2,
 'infill_envelope_ge_4mm': cfg['upper_infill_envelope_thickness']>=4.0,
}
ok &= all(checks['design_rules'].values())
checks['overall_pass']=bool(ok)
print(json.dumps(checks,indent=2))
raise SystemExit(0 if ok else 2)
