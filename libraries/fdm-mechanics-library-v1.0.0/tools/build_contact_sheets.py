#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument(
    '--write-concept',
    action='store_true',
    help='also overwrite the gated concept asset; omit for production/catalog refreshes',
)
args=parser.parse_args()
records=json.loads((ROOT/'catalog/catalog.json').read_text(encoding='utf-8'))
font=ImageFont.load_default()

def sheet(items, out, cols=5, thumb=(320,240), label_h=42, title=None):
    rows=(len(items)+cols-1)//cols
    title_h=54 if title else 0
    canvas=Image.new('RGB',(cols*thumb[0],title_h+rows*(thumb[1]+label_h)),(244,246,248))
    draw=ImageDraw.Draw(canvas)
    if title:
        draw.text((12,18),title,fill=(18,28,38),font=font)
    for idx,r in enumerate(items):
        x=(idx%cols)*thumb[0]; y=title_h+(idx//cols)*(thumb[1]+label_h)
        img=Image.open(ROOT/'samples'/r['relative_directory']/'preview.png').convert('RGB')
        img.thumbnail(thumb)
        px=x+(thumb[0]-img.width)//2; py=y+(thumb[1]-img.height)//2
        canvas.paste(img,(px,py))
        label=f"{r['id']}  {r['title_de']}\n{r['variant_label_de']}"
        draw.text((x+7,y+thumb[1]+4),label,fill=(18,28,38),font=font)
    out.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(out,optimize=True)

first=[]
seen=set()
for r in records:
    if r['family_number'] not in seen:
        seen.add(r['family_number']); first.append(r)
family_count=len(first); sample_count=len(records)
current_dynamic={
    f'contact-sheet-{family_count}-families.png',
    f'contact-sheet-all-{sample_count}.png',
}
for pattern in ('contact-sheet-*-families.png','contact-sheet-all-*.png'):
    for old in (ROOT/'catalog').glob(pattern):
        if old.name not in current_dynamic:
            old.unlink()
sheet(first,ROOT/'catalog'/f'contact-sheet-{family_count}-families.png',cols=5)
for category in sorted({r['category'] for r in records}):
    subset=[r for r in records if r['category']==category]
    sheet(subset,ROOT/'catalog'/f'contact-sheet-{category}.png',cols=4,thumb=(300,225),label_h=38)
sheet(records,ROOT/'catalog'/f'contact-sheet-all-{sample_count}.png',cols=8,thumb=(220,165),label_h=34)
if args.write_concept:
    extension=[r for r in first if 31 <= r['family_number'] <= 39]
    sheet(
        extension,
        ROOT/'concept'/'families-31-39-r1.1.0-draft.1.png',
        cols=3,
        thumb=(400,300),
        label_h=52,
        title='Concept review — families 31–39 — specification 1.1.0-draft.1',
    )
print('catalog contact sheets created; concept asset ' + ('updated' if args.write_concept else 'preserved'))
