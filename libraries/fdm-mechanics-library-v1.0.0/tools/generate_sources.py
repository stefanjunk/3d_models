#!/usr/bin/env python3
"""Generate OpenSCAD sample wrappers and documentation from library_spec.py."""
from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path
from typing import Any

from library_spec import BASELINE, FAMILIES

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
FAMILY_COUNT = len(FAMILIES)
SAMPLE_COUNT = sum(len(family["variants"]) for family in FAMILIES)
GENERIC_CLAIM_DISCLAIMER_DE = (
    "Digitale Geometrieprüfung ist keine Funktions-, Last-, Dichtheits-, "
    "Lebensdauer- oder Sicherheitsqualifikation."
)


def write_if_changed(path: Path, content: str) -> None:
    """Write generated text only when its bytes actually changed."""
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def scad_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(scad_value(x) for x in value) + "]"
    if isinstance(value, float):
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return text if text else "0"
    return str(value)


def safe_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")


def wrapper_text(sample: dict[str, Any]) -> str:
    params = ",\n    ".join(f"{k}={scad_value(v)}" for k, v in sample["params"].items())
    return f'''/*
Sample {sample["id"]}: {sample["title_de"]} — {sample["variant_label_de"]}
Generated from the FDM Mechanical Sample Library.
Units: millimetres.

Override examples:
  openscad -o custom.stl -D 'view="plate"' -D 'render_fn=64' model.scad
  openscad -o preview.png -D 'view="assembly"' model.scad
*/
use <../../../library/fdm_mechanisms.scad>

render_fn = is_undef(render_fn) ? 48 : render_fn;
view = is_undef(view) ? "plate" : view;
$fn = render_fn;

{sample["module"]}(
    view=view,
    {params}
);
'''


def readme_text(sample: dict[str, Any]) -> str:
    params = "\n".join(f"- `{k}`: `{v}`" for k, v in sample["params"].items())
    parts = "\n".join(f"- {p}" for p in sample["part_names"])
    plate_note = (
        "\n> **Print-in-Place:** Für die vorgesehene Funktion muss `print_plate.stl` als unveränderte gemeinsame Anordnung gedruckt werden. "
        "Die Dateien unter `parts/` dienen nur zur Geometrieinspektion oder Weiterkonstruktion.\n"
        if sample.get("must_print_as_plate")
        else ""
    )
    material = ", ".join(sample["materials"])
    plate_description = (
        "experimentelle DRAFT-Druckanordnung; nicht physisch qualifiziert"
        if sample["artifact_status"] == "experimental-draft"
        else "Druckanordnung des 1.0.0-Basispakets; in diesem DRAFT nicht neu qualifiziert"
    )
    return f'''# {sample["id"]} — {sample["title_de"]}

**Variante:** {sample["variant_label_de"]}  
**Kategorie:** {sample["category_de"]}  
**Mechanikfamilie:** `{sample["family_slug"]}`

## Status und Qualifikation

- Artefaktstatus: `{sample["artifact_status"]}`
- Qualifikationsstatus: `{sample["qualification_status"]}`
- Einordnung: {sample["status_de"]}
- Anspruchsgrenze: {sample["claims_de"]}

![Vorschau](preview.png)

## Prinzip

{sample["principle_de"]}

## Typische Verwendung

{sample["use_de"]}

## Enthaltene Dateien

- `model.scad` — parametrische OpenSCAD-Quelle
- `print_plate.stl` — {plate_description}
- `preview.png` — Explosions-/Montagevorschau
- `parts/part_XX.stl` — automatisch getrennte Einzelkörper für CAD-Import
- `components.json` — Abmessungen und ursprüngliche Position jeder Komponente
- `metadata.json` — maschinenlesbare Dokumentation

Vorgesehene Komponenten:

{parts}
{plate_note}
## Parameter dieser Variante

{params}

**Variantenhinweis:** {sample["variant_note_de"]}

## FDM-Empfehlung

- Material: {material}
- Düse: {BASELINE["nozzle_mm"]:.1f} mm
- Schichthöhe: {BASELINE["layer_height_mm"]:.1f} mm
- Außenlinien: mindestens {BASELINE["perimeters"]}
- Infill: {BASELINE["infill_percent"]} % als Startwert; funktionskritische Bereiche bei Bedarf lokal erhöhen
- Supportbedarf: grundsätzlich gering; die familienspezifischen Hinweise und die eigene Slicer-Vorschau beachten

{sample["print_de"]}

## Montage und Nacharbeit

{sample["postprocess_de"]}

## Integration in ein Projekt

{sample["integration_de"]}

## Fremdteile

{sample["hardware"]}

## Grenzen und Sicherheit

{sample["limitations_de"]}

Die Geometrie wurde digital auf geschlossene, positive Volumenkörper geprüft. Sie wurde nicht physisch auf jedem Drucker und Material gedruckt. Vor Lastanwendung zuerst die passende Toleranzvariante testen. Nicht für Personenlasten, Schutzfunktionen oder sonstige sicherheitskritische Anwendungen verwenden.
'''


def make_sample_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    number = 1
    for family in FAMILIES:
        for variant_index, variant in enumerate(family["variants"], 1):
            sample_id = f"{number:03d}"
            folder_name = f"{sample_id}-{family['slug']}-{safe_slug(variant['code'])}"
            rel_dir = Path(family["category"]) / folder_name
            is_extension = family["family"] >= 31
            record = {
                "id": sample_id,
                "number": number,
                "family_number": family["family"],
                "family_slug": family["slug"],
                "title_de": family["title_de"],
                "category": family["category"],
                "category_de": family["category_de"],
                "module": family["module"],
                "principle_de": family["principle_de"],
                "use_de": family["use_de"],
                "integration_de": family["integration_de"],
                "print_de": family["print_de"],
                "postprocess_de": family["postprocess_de"],
                "limitations_de": family["limitations_de"],
                "materials": family["materials"],
                "hardware": family["hardware"],
                "part_names": family["part_names"],
                "must_print_as_plate": bool(family.get("must_print_as_plate", False)),
                "variant_index": variant_index,
                "variant_code": variant["code"],
                "variant_label_de": variant["label_de"],
                "variant_note_de": variant["note_de"],
                "params": variant["params"],
                "relative_directory": rel_dir.as_posix(),
                "model_path": (Path("samples") / rel_dir / "model.scad").as_posix(),
                "stl_path": (Path("samples") / rel_dir / "print_plate.stl").as_posix(),
                "preview_path": (Path("samples") / rel_dir / "preview.png").as_posix(),
                "baseline": BASELINE,
                "artifact_status": "experimental-draft" if is_extension else "base-release-1.0.0",
                "qualification_status": "unqualified",
                "status_de": (
                    "Experimenteller DRAFT der Erweiterung 1.1.0; digital geprüft, nicht physisch qualifiziert."
                    if is_extension
                    else "Basismuster aus Release 1.0.0; im DRAFT-Prüfpunkt 1.1.0 nicht physisch requalifiziert."
                ),
                "claims_de": family.get("claim_disclaimer_de", GENERIC_CLAIM_DISCLAIMER_DE),
                "license_code": "MIT",
                "license_generated_geometry": "CC0-1.0",
            }
            records.append(record)
            number += 1
    return records


def write_html(records: list[dict[str, Any]]) -> None:
    cards = []
    for r in records:
        cards.append(f'''<article class="card" data-id="{r['id']}" data-cat="{html.escape(r['category'])}">
<a href="samples/{html.escape(r['relative_directory'])}/README.md"><img loading="lazy" src="samples/{html.escape(r['relative_directory'])}/preview.png" alt="{html.escape(r['title_de'])}"></a>
<div class="body"><div class="id">{r['id']} · {html.escape(r['category_de'])}</div><h2>{html.escape(r['title_de'])}</h2><p>{html.escape(r['variant_label_de'])}</p><p class="status">{html.escape(r['artifact_status'])} · {html.escape(r['qualification_status'])}</p><p class="claims">{html.escape(r['claims_de'])}</p><code>{html.escape(str(r['params']))}</code></div>
</article>''')
    doc = f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FDM Mechanikbibliothek — {SAMPLE_COUNT} Muster</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;background:#f3f5f7;color:#17202a}}header{{padding:2rem;max-width:1500px;margin:auto}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem;padding:0 2rem 3rem;max-width:1500px;margin:auto}}.card{{background:white;border-radius:14px;overflow:hidden;box-shadow:0 3px 16px #0001}}img{{width:100%;aspect-ratio:4/3;object-fit:cover;background:#faf8e8}}.body{{padding:1rem}}h2{{font-size:1.05rem;margin:.35rem 0}}p{{margin:.2rem 0 .7rem}}code{{font-size:.72rem;white-space:normal}}.id{{font-size:.74rem;opacity:.66}}.status{{font-weight:700;color:#8a4b00}}.claims{{font-size:.78rem;line-height:1.35}}</style></head><body><header><h1>FDM Mechanikbibliothek</h1><p>{SAMPLE_COUNT} parametrische Muster. Erweiterung 121–156: <strong>experimental-draft</strong>, <strong>unqualified</strong>; keine physische Funktions-, Dichtheits- oder Lebensdauerqualifikation.</p></header><main>{''.join(cards)}</main></body></html>'''
    write_if_changed(ROOT / "CATALOG.html", doc)


def main() -> None:
    records = make_sample_records()
    for record in records:
        folder = SAMPLES / record["relative_directory"]
        (folder / "parts").mkdir(parents=True, exist_ok=True)
        write_if_changed(folder / "model.scad", wrapper_text(record))
        write_if_changed(folder / "README.md", readme_text(record))
        write_if_changed(folder / "metadata.json", json.dumps(record, ensure_ascii=False, indent=2))

    write_if_changed(ROOT / "catalog" / "catalog.json", json.dumps(records, ensure_ascii=False, indent=2))
    with (ROOT / "catalog" / "catalog.csv").open("w", encoding="utf-8", newline="") as fh:
        fields = ["id", "family_number", "family_slug", "title_de", "category", "category_de", "variant_code", "variant_label_de", "relative_directory", "model_path", "stl_path", "preview_path", "artifact_status", "qualification_status", "status_de", "claims_de", "materials", "hardware", "params"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in records:
            row = {k: r[k] for k in fields}
            row["materials"] = ", ".join(r["materials"])
            row["params"] = json.dumps(r["params"], ensure_ascii=False, sort_keys=True)
            writer.writerow(row)

    lines = [f"# Katalog — {SAMPLE_COUNT} FDM-Mechanikmuster", "", "Erweiterung 121–156: `experimental-draft` / `unqualified`; keine physische Funktions-, Dichtheits- oder Lebensdauerqualifikation.", "", "| ID | Familie | Variante | Kategorie | Status |", "|---:|---|---|---|---|"]
    for r in records:
        link = f"../samples/{r['relative_directory']}/README.md"
        lines.append(f"| {r['id']} | [{r['title_de']}]({link}) | {r['variant_label_de']} | {r['category_de']} | `{r['artifact_status']}` / `{r['qualification_status']}` |")
    write_if_changed(ROOT / "catalog" / "CATALOG_DE.md", "\n".join(lines) + "\n")
    write_html(records)
    print(f"Generated {len(records)} sample source folders")


if __name__ == "__main__":
    main()
