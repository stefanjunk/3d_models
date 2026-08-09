#!/usr/bin/env python3
"""Build the three reference projects from source image through validated mesh."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from heightmap_common import write_json
from relief_patch import generate_from_config
from mesh_boolean import run_boolean
from validate_mesh import load_mesh, report_for


SKILL_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def ensure_sources(force: bool = False) -> None:
    expected = [
        SKILL_ROOT/"examples/01-unicorn-cylinder/source/unicorn-source.png",
        SKILL_ROOT/"examples/02-carbon-rounded-organizer/source/carbon-fiber-source.png",
        SKILL_ROOT/"examples/03-wood-honeycomb-shelf/source/wood-source.png",
    ]
    if force or not all(path.is_file() for path in expected):
        command = [
            sys.executable, str(SKILL_ROOT/"scripts/generate_example_images.py"),
            "--output-root", str(SKILL_ROOT), "--force",
        ]
        run(command)


def prepare_images(quality: str) -> None:
    circumference = 2*math.pi*40.0
    rounded_perimeter = 2*(90+65-4*8)+2*math.pi*8
    jobs: list[dict[str,Any]] = [
        {
            "example":"01-unicorn-cylinder","source":"unicorn-source.png",
            "output":f"unicorn-heightmap-{quality}.png",
            "width":circumference,"height":78.0,
            "pitch":0.60 if quality=="draft" else 0.25,"fit":"contain",
            "extra":[],
        },
        {
            "example":"02-carbon-rounded-organizer","source":"carbon-fiber-source.png",
            "output":f"carbon-heightmap-{quality}.png",
            "width":rounded_perimeter/3.0,"height":83.0,
            "pitch":0.45 if quality=="draft" else 0.20,"fit":"stretch",
            "extra":["--levels","0.5,99.5","--blur-mm","0.08"],
        },
        {
            "example":"03-wood-honeycomb-shelf","source":"wood-source.png",
            "output":f"wood-heightmap-{quality}.png",
            "width":120.0,"height":120.0,
            "target":"384x384" if quality=="draft" else "768x768","fit":"tile",
            "extra":["--levels","0.5,99.5"],
        },
    ]
    for job in jobs:
        base=SKILL_ROOT/"examples"/job["example"]
        source=base/"source"/job["source"]
        output=base/"prepared"/job["output"]
        command=[
            sys.executable,str(SKILL_ROOT/"scripts/prepare_heightmap.py"),
            str(source),str(output),
            "--physical-width-mm",str(job["width"]),
            "--physical-height-mm",str(job["height"]),
            "--fit",job["fit"],"--bit-depth","16",
            "--preview",str(output.with_name(output.stem+"-preview.png")),
            "--report",str(output.with_suffix(".report.json")),
        ]
        if "pitch" in job: command += ["--sample-pitch-mm",str(job["pitch"])]
        if "target" in job: command += ["--target-px",job["target"]]
        command += job["extra"]
        run(command)


def build_base(example: str, quality: str, output_dir: Path) -> None:
    script=SKILL_ROOT/"examples"/example/"cadquery/base_model.py"
    run([sys.executable,str(script),"--output-dir",str(output_dir),"--quality",quality])


def validate(path: Path) -> dict:
    report=report_for(load_mesh(path),str(path))
    if not report["watertight"] or report["nonmanifold_edges"]:
        raise RuntimeError(f"Mesh validation failed for {path}: {report}")
    return report


def build_one(example_number: str, quality: str, output_root: Path, skip_boolean: bool, engine: str) -> dict:
    if example_number=="1":
        example="01-unicorn-cylinder"
        config_names=[("unicorn-cutter",f"relief-{quality}.json")]
        base_name="gift-box-body.stl"; final_name="gift-box-engraved.stl"
    elif example_number=="2":
        example="02-carbon-rounded-organizer"
        config_names=[("carbon-cutter",f"relief-{quality}.json")]
        base_name="desk-organizer.stl"; final_name="desk-organizer-engraved.stl"
    elif example_number=="3":
        example="03-wood-honeycomb-shelf"
        config_names=[(f"{name}-cutter",f"{name}-{quality}.json") for name in
                      ("outer-wall","inner-wall","front-face","back-face")]
        base_name="honeycomb-shelf.stl"; final_name="honeycomb-shelf-engraved.stl"
    else:
        raise ValueError(example_number)

    out=output_root/example/quality
    out.mkdir(parents=True,exist_ok=True)
    build_base(example,quality,out)
    cutters=[]
    cutter_reports={}
    for output_stem,config_name in config_names:
        cutter=out/f"{output_stem}.stl"
        config=SKILL_ROOT/"examples"/example/"config"/config_name
        generated=generate_from_config(config,cutter,out/f"{output_stem}.report.json")
        if not generated["combined"]["watertight"]:
            raise RuntimeError(f"Non-watertight cutter: {cutter}")
        cutters.append(cutter)
        cutter_reports[output_stem]=generated["combined"]
    result={
        "example":example,"quality":quality,"base":validate(out/base_name),
        "cutters":cutter_reports,
    }
    if not skip_boolean:
        final=out/final_name
        detail=run_boolean(out/base_name,cutters,final,"difference",engine,os.environ.get("OPENSCAD","openscad"))
        result["boolean_engine"]=detail
        result["final"]=validate(final)
        if result["final"]["body_count"] != 1:
            raise RuntimeError(f"Expected one final body: {final}")
    return result


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--example",choices=("all","1","2","3"),default="all")
    p.add_argument("--quality",choices=("draft","print","both"),default="draft")
    p.add_argument("--output-root",type=Path,default=SKILL_ROOT/"build")
    p.add_argument("--skip-prepare",action="store_true")
    p.add_argument("--skip-boolean",action="store_true")
    p.add_argument("--engine",choices=("auto","manifold","blender","openscad"),default="auto")
    p.add_argument("--regenerate-sources",action="store_true")
    args=p.parse_args()
    ensure_sources(args.regenerate_sources)
    qualities=["draft","print"] if args.quality=="both" else [args.quality]
    if not args.skip_prepare:
        for quality in qualities: prepare_images(quality)
    examples=["1","2","3"] if args.example=="all" else [args.example]
    results=[]
    for quality in qualities:
        for example in examples:
            results.append(build_one(example,quality,args.output_root,args.skip_boolean,args.engine))
    summary={"results":results}
    write_json(summary,args.output_root/"build-summary.json")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        raise SystemExit(2)
