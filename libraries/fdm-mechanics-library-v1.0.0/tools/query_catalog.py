#!/usr/bin/env python3
"""Search the generated sample catalog from a terminal or an OpenCode agent."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'catalog/catalog.json'

def norm(text: str) -> str:
    return re.sub(r'\s+',' ',text.lower()).strip()

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('query', nargs='*', help='Search terms, e.g. kugel leichtgängig')
    p.add_argument('--category', default='')
    p.add_argument('--family', default='')
    p.add_argument('--material', default='')
    p.add_argument('--hardware-free', action='store_true')
    p.add_argument('--limit', type=int, default=20)
    p.add_argument('--json', action='store_true')
    a=p.parse_args()
    records=json.loads(CATALOG.read_text(encoding='utf-8'))
    words=[norm(x) for x in a.query if x.strip()]
    out=[]
    for r in records:
        text=norm(' '.join([
            r['id'],r['title_de'],r['category_de'],r['family_slug'],r['variant_label_de'],
            r['principle_de'],r['use_de'],r['integration_de'],r['variant_note_de'],
            ' '.join(r['materials']),r['hardware'],json.dumps(r['params'],ensure_ascii=False)
        ]))
        if words and not all(w in text for w in words): continue
        if a.category and norm(a.category) not in norm(r['category']+' '+r['category_de']): continue
        if a.family and norm(a.family) not in norm(r['family_slug']+' '+r['title_de']): continue
        if a.material and norm(a.material) not in [norm(x) for x in r['materials']]: continue
        if a.hardware_free and not r['hardware'].lower().startswith('kein fremdteil'): continue
        out.append(r)
    out=out[:max(1,a.limit)]
    if a.json:
        print(json.dumps(out,ensure_ascii=False,indent=2))
    else:
        print(f"Treffer: {len(out)}")
        for r in out:
            print(f"{r['id']} | {r['title_de']} | {r['variant_label_de']} | {r['category_de']}")
            print(f"    samples/{r['relative_directory']}")
            print(f"    Parameter: {json.dumps(r['params'],ensure_ascii=False,sort_keys=True)}")
    return 0
if __name__=='__main__':
    raise SystemExit(main())
