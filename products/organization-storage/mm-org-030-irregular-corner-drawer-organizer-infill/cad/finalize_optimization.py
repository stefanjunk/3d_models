#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[2]; COMPARE=REPO/".agents/skills/optimize-fdm-design/scripts/compare_variants.py"; REV="0.1.0-draft.1"
REPORTS={"system-020":ROOT/"validation/slicer-system-020.json","system-028":ROOT/"validation/slicer-system-028.json"}


def sha(target): return hashlib.sha256(target.read_bytes()).hexdigest()
def record(target):
    try: display=str(target.relative_to(ROOT))
    except ValueError: display=str(target)
    return {"path":display,"sha256":sha(target),"size_bytes":target.stat().st_size}
def check(i,p,m,x=None): return {"id":i,"status":"PASS" if p else "FAIL","required":True,"message":m,"metrics":x or {},"evidence":[]}
def metrics(target):
    report=json.loads(target.read_text()); g=list(report["gcode_reports"].values())[0]; m=g["metrics"]; native=[i["warning_message"] for i in report["native_result"]["sliced_plates"] if i.get("warning_message","").strip()]
    return {"report_status":1 if report["status"]==g["status"]=="PASS" else 0,"layer_count":m["layers_from_comments"],"print_time_s":m["slicer_metadata_time_s"],"extruded_volume_mm3":m["extruded_volume_mm3"],"warning_count":len(m["warnings"])+len(native),"tool_changes":m["tool_changes"],"tools_seen":m["tools_seen"]}


def main():
    extracted={n:metrics(p) for n,p in REPORTS.items()}; variants=[{"name":n,"metrics":{**m,"protected_shell":1},"notes":["Exact whole-plate Kobra 3 Max PLA slice; no G-code retained."]} for n,m in extracted.items()]
    payload={"baseline":"system-020","objectives":[{"metric":"print_time_s","goal":"min"},{"metric":"extruded_volume_mm3","goal":"min"}],"constraints":[{"metric":"report_status","op":"==","value":1},{"metric":"warning_count","op":"==","value":0},{"metric":"tool_changes","op":"==","value":0},{"metric":"protected_shell","op":"==","value":1}],"variants":variants}; vp=ROOT/"reports/optimization-variants.json"; cp=ROOT/"reports/optimization-pareto.json"; mp=ROOT/"reports/optimization-pareto.md"; vp.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); subprocess.run([sys.executable,str(COMPARE),str(vp),"--output",str(cp)],check=True,stdout=subprocess.DEVNULL); subprocess.run([sys.executable,str(COMPARE),str(vp),"--markdown","--output",str(mp)],check=True,stdout=subprocess.DEVNULL); comparison=json.loads(cp.read_text()); selected=extracted["system-028"]; base=extracted["system-020"]; geometric=json.loads((ROOT/"reports/optimization-geometric.json").read_text()); interface=json.loads((ROOT/"validation/interface-report.json").read_text())
    time_delta=100*(selected["print_time_s"]-base["print_time_s"])/base["print_time_s"]; volume_delta=100*(selected["extruded_volume_mm3"]-base["extruded_volume_mm3"])/base["extruded_volume_mm3"]
    checks=[*[check(f"slicer:{n}",m["report_status"]==1,f"{n} reports PASS") for n,m in extracted.items()],check("warning-free",all(m["warning_count"]==0 for m in extracted.values()),"Both slices contain no native/parser warnings"),check("single-tool",all(m["tools_seen"]==[0] and m["tool_changes"]==0 for m in extracted.values()),"Both use one tool"),check("pareto",set(comparison["pareto_variants"])=={"system-020","system-028"},"Both time/material tradeoff variants are Pareto-efficient"),check("time-priority-selection",time_delta<0 and volume_delta<=12,"0.28 mm saves time while estimated extrusion growth stays within 12%",{"time_delta_percent":time_delta,"volume_delta_percent":volume_delta}),check("protected-shell",interface["metrics"]["interfaces"]["round-corner"]["wall_mm"]>=3,"Selected trays retain 3 mm walls"),check("light-rejected",geometric["light_variant"]["constraint"].startswith("REJECTED"),"Light shell remains rejected"),check("geometric",geometric["selected"]["reduction_percent"]>=80,"Irregular shells reduce proxy volume by at least 80%")]
    sources=[ROOT/"config/model-parameters.json",ROOT/"validation/interface-report.json",ROOT/"reports/optimization-geometric.json",COMPARE,*REPORTS.values(),vp,cp,mp]; report={"schema_version":"1.0","tool":"MM-ORG-030-finalize-optimization","tool_version":REV,"status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","profile":"draft","inputs":[record(p) for p in sources],"checks":checks,"metrics":{"selected_variant":"system-028","selection_policy":"time_priority_with_max_12_percent_estimated_extrusion_growth","feasible_variants":comparison["feasible_count"],"pareto_variants":comparison["pareto_variants"],"selected_print_time_s":selected["print_time_s"],"selected_extruded_volume_mm3":selected["extruded_volume_mm3"],"selected_layers":selected["layer_count"],"time_delta_percent_vs_020":time_delta,"volume_delta_percent_vs_020":volume_delta,"geometric_reduction_vs_proxy_percent":geometric["selected"]["reduction_percent"],"light_variant_reduction_percent":geometric["light_variant"]["reduction_percent_vs_selected_round"],"variant_metrics":extracted},"limitations":["Slicer estimates are not measured outcomes.","Physical fit, flex, drop and drawer cycles are deferred.","No G-code was retained."],"required_capabilities":[]}; target=ROOT/"validation/optimization-report.json"; target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"metrics":report["metrics"]},indent=2)); raise SystemExit(0 if report["status"]=="PASS" else 1)


if __name__=="__main__": main()
