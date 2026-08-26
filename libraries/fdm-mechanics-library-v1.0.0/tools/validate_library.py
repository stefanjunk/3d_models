#!/usr/bin/env python3
"""Validate release structure and generated artifacts without rebuilding geometry."""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path

from validate_extension import validate_contract

ROOT=Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--report',default='validation/library-validation.json'); p.add_argument('--summary',default='validation/library-validation.txt'); a=p.parse_args()
    records=json.loads((ROOT/'catalog/catalog.json').read_text(encoding='utf-8'))
    build=json.loads((ROOT/'validation/build-summary.json').read_text(encoding='utf-8'))
    extension_build_path=ROOT/'validation/extension-build-summary.json'
    extension_validation_path=ROOT/'validation/extension-validation.json'
    extension_claims_path=ROOT/'validation/extension-claims-validation.json'
    extension_build=json.loads(extension_build_path.read_text(encoding='utf-8')) if extension_build_path.is_file() else {}
    extension_validation=json.loads(extension_validation_path.read_text(encoding='utf-8')) if extension_validation_path.is_file() else {}
    extension_claims=json.loads(extension_claims_path.read_text(encoding='utf-8')) if extension_claims_path.is_file() else {}
    current_extension_contract,current_extension_errors=validate_contract(require_fresh_build_summary=True)
    current_claims=current_extension_contract.get('claims_bounded',{})
    errors=[]; samples=[]
    required=['model.scad','print_plate.stl','preview.png','README.md','metadata.json','components.json']
    report_status={}
    for path in (ROOT/'validation/samples').glob('*.json'):
        data=json.loads(path.read_text(encoding='utf-8'))
        report_status[data.get('id',path.stem)]=data.get('status')
    for r in records:
        d=ROOT/'samples'/r['relative_directory']
        missing=[name for name in required if not (d/name).is_file()]
        parts=sorted((d/'parts').glob('part_*.stl')) if (d/'parts').is_dir() else []
        comp=json.loads((d/'components.json').read_text(encoding='utf-8')) if (d/'components.json').is_file() else {}
        ok=not missing and len(parts)==comp.get('combined',{}).get('components') and all(x.get('watertight') for x in comp.get('components',[]))
        if not ok: errors.append({'id':r['id'],'missing':missing,'part_files':len(parts),'component_count':comp.get('combined',{}).get('components')})
        samples.append({'id':r['id'],'ok':ok,'parts':len(parts)})
    checks={
        'catalog_has_156_samples':len(records)==156,
        'catalog_has_39_families':len({r['family_number'] for r in records})==39,
        'build_summary_has_156_passed':build.get('passed')==156 and build.get('warning')==0 and build.get('failed')==0,
        'sample_reports_have_156_passed':len(report_status)==156 and all(report_status.get(r['id'])=='passed' for r in records),
        'all_sample_files_complete':not errors,
        'opencode_skill_present':(ROOT/'.opencode/skills/fdm-mechanical-sample-library/SKILL.md').is_file(),
        'shared_scad_library_present':(ROOT/'library/fdm_mechanisms.scad').is_file(),
        'contact_sheets_present':(ROOT/'catalog/contact-sheet-39-families.png').is_file() and (ROOT/'catalog/contact-sheet-all-156.png').is_file(),
        'extension_fresh_build_passed':extension_build.get('samples_requested')==36 and extension_build.get('passed')==36 and extension_build.get('warning')==0 and extension_build.get('failed')==0 and all(not x.get('stl_reused') and x.get('stl_render_seconds',0)>0 for x in extension_build.get('results',[])),
        'extension_contract_and_regression_passed':extension_validation.get('status')=='passed' and len(extension_validation.get('geometry_regression',[]))==36 and all(x.get('passed') for x in extension_validation.get('geometry_regression',[])) and len(extension_validation.get('boundary_results',[]))==27 and all(x.get('passed') for x in extension_validation.get('boundary_results',[])),
        'extension_claims_bounded_passed':extension_claims.get('status')=='passed' and extension_claims.get('checks',{}).get('claims_bounded',{}).get('passed') is True and extension_claims.get('checks',{}).get('claims_bounded',{}).get('extension_records_checked')==36,
        'extension_current_inputs_passed':not current_extension_errors and current_extension_contract.get('extension_record_count')==36 and not current_extension_contract.get('generated_artifact_errors') and current_claims.get('passed') is True and all(current_claims.get(key)==36 for key in ('extension_records_checked','catalog_json_checked','catalog_csv_checked','metadata_checked','readmes_checked','catalog_html_cards_checked','catalog_markdown_rows_checked')) and current_claims.get('sealing_records_checked')==20 and current_claims.get('family_39_records_checked')==4 and not current_claims.get('record_errors'),
    }
    if current_extension_errors:
        errors.append({'scope':'current_extension_contract','errors':current_extension_errors})
    report={'root':str(ROOT),'checks':checks,'passed':all(checks.values()),'errors':errors,'current_extension_contract':current_extension_contract,'sample_count':len(records),'part_stl_count':sum(x['parts'] for x in samples),'samples':samples}
    out=ROOT/a.report; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    summary={**checks,'part_stl_count':report['part_stl_count'],'passed':report['passed']}
    summary_text=json.dumps(summary,ensure_ascii=False,indent=2)+"\n"
    summary_out=ROOT/a.summary; summary_out.parent.mkdir(parents=True,exist_ok=True); summary_out.write_text(summary_text,encoding='utf-8')
    print(summary_text,end='')
    return 0 if report['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
