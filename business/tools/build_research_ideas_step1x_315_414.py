#!/usr/bin/env python3
"""Build the 100 generative Step1X-3D research concepts SKU-315 through SKU-414.

The batch covers the six requested popular-model groups:

- Animals & creatures (SKU-315 to SKU-334)
- Cartoon, comic and stylized characters (SKU-335 to SKU-352)
- Toys, fidgets and kinetic objects (SKU-353 to SKU-370)
- Tools and functional desktop accessories (SKU-371 to SKU-386)
- Persons, figurines and humanoid statues (SKU-387 to SKU-400)
- Trending decor and viral objects (SKU-401 to SKU-414)

Every row is a P0 research hypothesis with an explicit generative route
(AI reference image -> Step1X-3D mesh -> CAD/mesh finishing), a structured R2
concept preflight, and a modeled commercial block that reuses the retained
Unit Economics cost model. No row is a demand proof, a rights clearance or a
product-release approval.
"""

from __future__ import annotations

import argparse
import csv
import io
import math
from pathlib import Path

from step1x_data import ITEMS

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "business/02-portfolio/research-ideas-additions-3.csv"
ASSESSED_ON = "2026-09-04"
ASSESSMENT_VERSION = "1.0"
SKU_START = 315
SKU_END = 414

PREFLIGHT_WEIGHTS = {
    "REQ": 7,
    "CTX": 5,
    "PAR": 10,
    "INT": 20,
    "CPL": 10,
    "MOT": 10,
    "GEO": 7,
    "PHY": 10,
    "MAT": 7,
    "EXT": 7,
    "VER": 7,
}

# Cost rates, waste, reserve, VAT, fee and price rules are taken unchanged from
# the retained research Unit Economics model so that the new rows stay
# comparable with SKU-001 through SKU-100 instead of introducing a second,
# incompatible cost basis.
COST_MODEL = {
    "material_eur_per_kg": {"PLA": 22.0, "PETG": 26.0, "ASA": 32.0, "TPU": 35.0},
    "density_g_per_cm3": {"PLA": 1.24, "PETG": 1.27, "ASA": 1.07, "TPU": 1.21},
    "waste_share": 0.08,
    "machine_eur_per_h": {"Core": 0.75, "Enclosed": 0.95, "Flexible": 0.85, "Large": 1.15},
    "labor_eur_per_h": 32.0,
    "qa_reserve_share": 0.05,
    "packaging_eur": {"S": 0.6, "M": 1.0, "L": 1.8},
    "minimum_net_price_eur": {"S": 7.5, "M": 12.5, "L": 25.0},
    "royalty_eur": 0.0,
    "vat_share": 0.19,
    "transaction_fee_share": 0.042,
    "net_price_cogs_multiple": 2.5,
}
COST_MODEL_BASIS = (
    "Modeled with the retained Unit Economics basis: material EUR/kg by polymer, 8% waste, machine rate by "
    "printer class, labor EUR 32/h on modeled hands-on minutes, 5% QA reserve, packaging and minimum net price "
    "by size class, recommended net = 2.5x modeled COGS rounded up to EUR 0.50, 19% VAT and a 4.2% transaction "
    "fee. Mass and print time are modeled from the bounding box, an archetype envelope-utilization factor and an "
    "archetype material-fill factor; no weighed part, no measured print and no sale confirms these values."
)

# Directional trend components. Tier -> points. The gate below requires the four
# components to sum above 70, and every component stays a documented planning
# judgment rather than measured demand.
TREND_TIERS = {
    "source_strength": {
        "PLATFORM_FIGURE": 28,      # named model or ranking figure read on the hosting platform
        "INDUSTRY_REPORT": 25,      # company, association or market report with concrete figures
        "PLATFORM_CATEGORY": 24,    # platform-published category or contest evidence, not per model
        "MARKETPLACE_METHOD": 20,   # marketplace trend or insight publication without per-item volume
        "SECONDARY_PRESS": 16,      # trade press or aggregated coverage only
    },
    "signal_magnitude": {
        "VERY_LARGE": 28,           # six-figure downloads/prints, or double-digit growth on a large base
        "LARGE": 24,
        "MODERATE": 20,
        "SMALL": 15,
    },
    "fit": {
        "CORE_FUNCTIONAL": 24,      # printed object does defined work; matches the functional core
        "STRONG": 22,               # desk or home object with a real use and a repeatable digital offer
        "MODERATE": 18,             # appearance-led, adjacent to the functional core
        "WEAK": 13,
    },
    "whitespace": {
        "OPEN": 13,                 # no comparable metriMade candidate and few controlled paid variants
        "PARTIAL": 10,              # crowded free-model niche; differentiation must come from execution
        "CROWDED": 6,
    },
}

GROUPS = {
    "ANIMALS": {
        "family": "AI-generated animals & creatures",
        "segment": "Adult desk-object buyers, animal and fantasy fans, gift buyers, 3D-print hobbyists",
        "strategy": "Core adjacent — appearance-led generative desk objects that reuse the controlled print and release workflow",
        "inputs": "Species or creature choice; size class; color/filament pair; optional name-plate text; articulated or static variant",
        "variables": "overall scale; segment count and joint clearance; wall thickness; base diameter; plate text; support-free orientation",
        "interface": "Generated organic surface plus the print-in-place joint clearance or the flat build-plate seat",
        "evidence": "E1 generative reference: own AI image plus Step1X-3D mesh; no measured animal anatomy and no scanned original are claimed",
        "verification": "Watertight and self-intersection audit, minimum-wall audit, joint-clearance audit, first-layer contact-area check, articulation cycle test where applicable",
        "gate": "Generate one reference image and one Step1X-3D mesh, repair to a watertight solid, then print one smallest-feature coupon before a full model",
        "risk": "Decorative adult desk object; not a toy for children under 3, no load-bearing, outdoor, food-contact or child-safety claim",
    },
    "CHARACTERS": {
        "family": "AI-generated cartoon & comic characters",
        "segment": "Tabletop and comic fans, desk-decor buyers, gift buyers, collectors of original stylized figures",
        "strategy": "Core adjacent — original stylized characters as controlled digital and printed desk objects",
        "inputs": "Archetype choice; pose variant; size class; color/filament pair; optional base text",
        "variables": "overall scale; base diameter and thickness; limb thickness floor; accessory scale; plate text; split-plane position",
        "interface": "Generated character surface plus the printable minimum-feature floor and the flat base seat",
        "evidence": "E1 generative reference: own AI image plus Step1X-3D mesh of an original archetype; no third-party character, likeness or trade dress is used",
        "verification": "Watertight and self-intersection audit, minimum-feature audit on fingers/weapons/accessories, overhang and support review, base contact check, rights and originality review",
        "gate": "Run the originality and trade-dress review, then generate one reference image, one Step1X-3D mesh and one printed minimum-feature coupon",
        "risk": "Original archetype only; no named third-party character, logo or trade dress, no child-under-3 use and no small-parts toy claim",
    },
    "TOYS": {
        "family": "AI-generated toys, fidgets & kinetic objects",
        "segment": "Adult fidget and desk-toy buyers, sensory-product users, supervised teens, gift buyers",
        "strategy": "Core adjacent — tactile kinetic desk objects with a repeatable mechanism and a controlled release gate",
        "inputs": "Mechanism choice; hand size class; color/filament pair; motion-resistance preference; optional name text",
        "variables": "overall scale; joint or gear clearance; spring-arm thickness; detent depth; travel limit; plate text",
        "interface": "Print-in-place clearance, gear backlash or compliant-spring root that must survive repeated actuation",
        "evidence": "E1 generative reference for the shell plus E2 parametric mechanism: clearances and spring roots are designed in CAD, not generated",
        "verification": "Clearance audit, free-motion check, 100-cycle actuation endurance test, pinch-gap review, small-parts and detachment inspection",
        "gate": "Print one mechanism coupon at the intended clearance, run the 100-cycle actuation test, then decide the toy-safety route before any sale",
        "risk": "Adult desk fidget; selling a physical unit as a toy triggers EU toy-safety conformity, so no child-use, age-grade or safety claim is made at research stage",
    },
    "TOOLS": {
        "family": "AI-generated tools & desktop utility",
        "segment": "Makers, hobby workshops, home offices, model builders, craft and repair users",
        "strategy": "Core — functional printed utility objects with exact commercial-off-the-shelf interfaces",
        "inputs": "Hand size class; the exact insert, bit, magnet or blade to be held; mounting surface; color/filament pair",
        "variables": "grip length and girth; socket depth and flats; magnet pocket depth; insert boss diameter; wall thickness; rail or clip pitch",
        "interface": "Exact commercial-off-the-shelf part or host feature that the printed body must retain or fit",
        "evidence": "E1 generative reference for the ergonomic shell plus E3 published nominal dimensions for the retained hardware; the exact local part remains unverified",
        "verification": "Interface dimension check against the published nominal, retention/pull-out test, hand-force and comfort review, repeated insertion cycles, layer-orientation strength review",
        "gate": "Print the interface coupon against the exact purchased hardware, measure retention, then confirm the grip geometry on a real task",
        "risk": "Hand-guided workshop or desk aid; no high-torque, no cutting-safety, no electrical, no lifting and no load-bearing claim",
    },
    "PERSONS": {
        "family": "AI-generated persons, figurines & statues",
        "segment": "Gift buyers, hobby and occupation gifting, interior-decor buyers, collectors of small statues",
        "strategy": "Core adjacent — original human-form figurines and statues as controlled digital and printed objects",
        "inputs": "Theme or occupation; pose variant; size class; color/filament pair; optional engraved plate text",
        "variables": "overall scale; base diameter; limb thickness floor; plate text; split-plane position; hollow-shell thickness",
        "interface": "Generated human-form surface plus the printable minimum-feature floor and the flat base seat",
        "evidence": "E1 generative reference: own AI image plus Step1X-3D mesh of a generic non-identifiable person; no real, recognizable or named individual is reproduced",
        "verification": "Watertight and self-intersection audit, minimum-feature audit on hands and thin limbs, overhang and support review, base stability check, likeness and rights review",
        "gate": "Run the likeness and rights review, then generate one reference image, one Step1X-3D mesh and one printed minimum-feature coupon",
        "risk": "Generic non-identifiable figure only; no portrait of a real person, no likeness-rights claim, decorative use only",
    },
    "DECOR": {
        "family": "AI-generated trending decor objects",
        "segment": "Home-decor buyers, plant owners, gift buyers, small-space renters, seasonal shoppers",
        "strategy": "Core — printed home objects with a defined function and a controlled release gate",
        "inputs": "Motif choice; size class; color/filament pair; plant-pot or insert size where applicable; optional text",
        "variables": "overall scale; wall thickness; drainage or insert diameter; relief depth; base footprint; text plate",
        "interface": "Defined insert, pot, candle cup, light-source keep-out or wall fixing that the printed body must accept",
        "evidence": "E1 generative reference for the decorative body plus E2 parametric interface for the insert, drainage or keep-out geometry",
        "verification": "Watertight and wall-thickness audit, insert/pot fit check, tip and stability check, water-path or keep-out review, surface-finish review",
        "gate": "Print one interface coupon for the insert, pot or keep-out, verify fit and stability, then decide the sealing and heat exclusions",
        "risk": "Dry decorative indoor use; no food contact, no direct soil-and-water containment without a liner, no open-flame and no electrical claim",
    },
}

ARCHETYPES = {
    "SCULPTURE_ORGANIC": {
        "label": "Appearance-led organic sculpture",
        "scores": {"REQ": 1, "CTX": 1, "PAR": 1, "INT": 1, "CPL": 0, "MOT": 0, "GEO": 3, "PHY": 0, "MAT": 1, "EXT": 0, "VER": 1},
        "difficulty": "Easy",
        "criticality": "K1",
        "am": "A generated organic form is printed on demand with no tooling; only the build-plate seat and the minimum-feature floor are engineered.",
        "digital_band": "4-10",
        "material": "PLA",
        "printer_class": "Core 250 mm",
        "supports": "Minimal / tree",
        "part_strategy": "Single generated body with a flattened base; optional split for tall variants",
        "secondary_bom": "None",
        "utilization": 0.35,
        "fill": 0.30,
        "throughput_g_per_h": 22.0,
        "hands_on_min": 6,
        "route": "Step1X-3D geometry from one isolated AI reference image, mesh repair to a watertight solid, planar base cut, minimum-feature thickening",
    },
    "PIP_FLEXI": {
        "label": "Print-in-place articulated body",
        "scores": {"REQ": 2, "CTX": 1, "PAR": 1, "INT": 2, "CPL": 1, "MOT": 2, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K1",
        "am": "Print-in-place ball or knuckle joints remove all assembly labor and cannot be injection molded as one piece.",
        "digital_band": "6-14",
        "material": "PLA",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "One print-in-place assembly; joints parametric, shell from the generative mesh",
        "secondary_bom": "None",
        "utilization": 0.20,
        "fill": 0.35,
        "throughput_g_per_h": 26.0,
        "hands_on_min": 7,
        "route": "Segmentation into links, parametric ball or knuckle joints with a calibrated clearance, support-free orientation",
    },
    "HYBRID_FUNCTIONAL": {
        "label": "Generative shell with a parametric function",
        "scores": {"REQ": 2, "CTX": 2, "PAR": 2, "INT": 2, "CPL": 1, "MOT": 0, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K1",
        "am": "The decorative envelope is generated while the working cavity, slot or dock is cut parametrically, which mass production cannot vary per order.",
        "digital_band": "6-16",
        "material": "PETG",
        "printer_class": "Core 250 mm",
        "supports": "Buildplate only",
        "part_strategy": "Generative outer body plus a parametric functional insert or cavity",
        "secondary_bom": "Optional felt pad or liner",
        "utilization": 0.30,
        "fill": 0.32,
        "throughput_g_per_h": 34.0,
        "hands_on_min": 8,
        "route": "Mesh repair, Boolean of the parametric cavity or dock, wall-thickness correction",
    },
    "ERGONOMIC_TOOL": {
        "label": "Generative grip with an exact hardware interface",
        "scores": {"REQ": 2, "CTX": 1, "PAR": 2, "INT": 3, "CPL": 1, "MOT": 1, "GEO": 2, "PHY": 2, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K2",
        "am": "An organic palm-fitting grip is generated and then joined to an exact socket, so a one-off ergonomic tool body costs one print.",
        "digital_band": "5-14",
        "material": "PETG",
        "printer_class": "Core 250 mm",
        "supports": "Minimal",
        "part_strategy": "Generative grip body with a parametric hardware socket; optional two-part clamshell",
        "secondary_bom": "Purchased bit, blade, magnet, insert or fastener",
        "utilization": 0.45,
        "fill": 0.45,
        "throughput_g_per_h": 36.0,
        "hands_on_min": 10,
        "route": "Mesh repair, Boolean of the published-nominal socket, wall and root reinforcement",
    },
    "KINETIC_MECHANICAL": {
        "label": "Parametric mechanism with a generative skin",
        "scores": {"REQ": 2, "CTX": 1, "PAR": 3, "INT": 2, "CPL": 2, "MOT": 2, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Hard",
        "criticality": "K2",
        "am": "Gears, irises and compliant detents print as one interlocked object with no assembly, tooling or fasteners.",
        "digital_band": "7-18",
        "material": "PETG",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "Parametric mechanism core plus generative decorative caps",
        "secondary_bom": "Optional bearing or steel pin",
        "utilization": 0.35,
        "fill": 0.40,
        "throughput_g_per_h": 28.0,
        "hands_on_min": 12,
        "route": "Parametric CAD mechanism first, generated geometry only for the decorative caps, Boolean merge and clearance verification",
    },
    "COMPLIANT_CLICK": {
        "label": "Compliant snap or click mechanism",
        "scores": {"REQ": 2, "CTX": 1, "PAR": 2, "INT": 2, "CPL": 1, "MOT": 2, "GEO": 2, "PHY": 1, "MAT": 2, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K2",
        "am": "A bistable dome, detent or living hinge is printed as one piece, so the click feel is a geometry parameter instead of a metal spring.",
        "digital_band": "5-12",
        "material": "PETG",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "Generative shell with a parametric compliant spring, detent or bistable diaphragm",
        "secondary_bom": "None",
        "utilization": 0.40,
        "fill": 0.40,
        "throughput_g_per_h": 30.0,
        "hands_on_min": 8,
        "route": "Mesh repair, parametric compliant-element design (root thickness, travel, over-centre geometry), cycle-life target",
    },
    "COTS_HOLDER": {
        "label": "Generative holder with an exact purchased-part interface",
        "scores": {"REQ": 2, "CTX": 2, "PAR": 2, "INT": 3, "CPL": 1, "MOT": 0, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K1",
        "am": "One printed body is matched to an exact purchased part or host edge, so a per-item holder costs one print instead of a tooling run.",
        "digital_band": "5-14",
        "material": "PETG",
        "printer_class": "Core 250 mm",
        "supports": "Buildplate only",
        "part_strategy": "Generative outer body with parametric pockets, clips or bosses for the purchased part",
        "secondary_bom": "Purchased magnet, insert, bearing or fastener",
        "utilization": 0.35,
        "fill": 0.35,
        "throughput_g_per_h": 38.0,
        "hands_on_min": 8,
        "route": "Mesh repair, Boolean of the published-nominal pocket or clip, datum alignment to the host surface",
    },
    "PUZZLE_INTERLOCK": {
        "label": "Interlocking multi-piece puzzle",
        "scores": {"REQ": 2, "CTX": 1, "PAR": 2, "INT": 2, "CPL": 2, "MOT": 1, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K2",
        "am": "Interlocking piece sets with per-piece tolerance print as one plate, which tooling cannot economically vary.",
        "digital_band": "6-14",
        "material": "PLA",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "Generated outer form split into a parametric interlocking piece set on one plate",
        "secondary_bom": "Optional storage tray",
        "utilization": 0.40,
        "fill": 0.40,
        "throughput_g_per_h": 30.0,
        "hands_on_min": 9,
        "route": "Mesh repair, parametric split planes with dovetail or lug clearances, per-piece fit tuning",
    },
    "RELIEF_PANEL": {
        "label": "Generative relief or wall panel",
        "scores": {"REQ": 1, "CTX": 1, "PAR": 2, "INT": 1, "CPL": 1, "MOT": 0, "GEO": 3, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 1},
        "difficulty": "Easy",
        "criticality": "K1",
        "am": "A generated relief prints flat without supports and scales to any panel size, so wall art becomes a print-on-demand file.",
        "digital_band": "5-12",
        "material": "PLA",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "Flat-backed relief panel with a parametric frame and keyhole or cleat fixing",
        "secondary_bom": "Adhesive strip or wall hook",
        "utilization": 0.55,
        "fill": 0.35,
        "throughput_g_per_h": 40.0,
        "hands_on_min": 6,
        "route": "Projection to a flat-backed relief, depth remap, parametric frame and fixing features",
    },
    "VESSEL_PLANTER": {
        "label": "Generative vessel, planter or holder",
        "scores": {"REQ": 2, "CTX": 1, "PAR": 2, "INT": 1, "CPL": 1, "MOT": 0, "GEO": 2, "PHY": 1, "MAT": 2, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K1",
        "am": "A generated outer form is combined with a parametric inner cavity and drainage, so one file serves several pot or insert sizes.",
        "digital_band": "5-12",
        "material": "PETG",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "Generative outer shell with a parametric inner cavity, drain and saucer interface",
        "secondary_bom": "Nursery pot, liner or saucer",
        "utilization": 0.30,
        "fill": 0.25,
        "throughput_g_per_h": 40.0,
        "hands_on_min": 7,
        "route": "Mesh repair, parametric cavity and drain Boolean, uniform wall-thickness rebuild",
    },
    "LAMP_DIFFUSER": {
        "label": "Generative passive light diffuser",
        "scores": {"REQ": 2, "CTX": 2, "PAR": 2, "INT": 2, "CPL": 1, "MOT": 0, "GEO": 2, "PHY": 1, "MAT": 2, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "criticality": "K2",
        "am": "Thin-wall generated shades print in single-wall spiral paths and diffuse light in shapes that molding cannot demold.",
        "digital_band": "6-14",
        "material": "PLA",
        "printer_class": "Core 250 mm",
        "supports": "None",
        "part_strategy": "Thin-wall generative shade with a parametric keep-out and cold-source seat; no electrical parts included",
        "secondary_bom": "Customer-supplied low-heat LED source",
        "utilization": 0.25,
        "fill": 0.15,
        "throughput_g_per_h": 45.0,
        "hands_on_min": 6,
        "route": "Shelling to a uniform thin wall, parametric keep-out volume and seat for a cold light source",
    },
}

TOOL_LICENCE_GATE = (
    "BLOCKING before any EU commercial use: Step1X-3D declares Apache-2.0 for code and weights [S122][S124], but twelve "
    "repository files retain a verbatim TENCENT HUNYUAN NON-COMMERCIAL LICENSE header, one of them in the geometry path "
    "that a geometry-only run imports and executes [S125]; that upstream licence excludes the European Union from its "
    "Territory and forbids use of the works' output outside it [S126]. Clarify with StepFun, replace the affected files, "
    "or take legal advice before a first sale. The SD-XL-based texture path additionally requires the CreativeML Open "
    "RAIL++-M use restrictions to be carried into metriMade's own customer terms [S127]."
)
MESH_QUALITY_GATE = (
    "Generative mesh gate before any print or file release [S122][S128][S129][S130]: manifold and hole repair, "
    "degenerate-face and open-edge removal, self-intersection check before any Boolean, minimum wall of at least three "
    "perimeters (1.35 mm at a 0.4 mm nozzle) and never below one perimeter, thin-protrusion and connection-point "
    "thickening above the nozzle width, floater and disconnected-shell count, explicit solid-versus-shell decision, "
    "deliberate millimetre scaling because the generator works in a normalised cube with no metric units, "
    "re-creation of every functional dimension parametrically because geometry is bounded by a 256 cubed TSDF grid, "
    "topology-preserving decimation, named human sign-off, and one physical test print at the released scale and material."
)
IP_BASIS = (
    "Original generative concept: the reference image comes from an own text prompt, no third-party model, "
    "character, likeness, logo or trade dress is used, and no external model file is imported. The rights review "
    "remains a release gate."
)
AI_TRANSPARENCY_DUTY = (
    "AI-assisted output: disclose the generative origin, the tools used and the human CAD work in the product record, "
    "the release package and every customer-facing listing, flag AI-generated content at platform upload [S92], and ship "
    "at least one photograph of a real print with each listing [S119]. The EU AI Act article number and application date "
    "for synthetic-content marking were NOT verified in this research pass and must be confirmed on EUR-Lex before any "
    "compliance statement cites them."
)
NOTES = (
    "metriMade generative research candidate only. Trend, price, cost, mesh quality, rights and demand remain "
    "hypotheses until a German marketplace check, a printed coupon and a rights review exist."
)
OPPORTUNITY_BASIS = (
    "Opportunity = 0.65 x directional trend score + 0.35 x modeled contribution margin in percent, capped at 99; "
    "it orders planning work only and is not validated demand or approved margin."
)

FIELDNAMES = [
    "SKU_ID", "Product", "Product_Family", "Concept_Type", "Purpose", "Customer_Job", "Target_Segment",
    "Trend_Signal", "Strategy_Fit", "AM_Advantage", "Customer_Inputs", "Parametric_Variables",
    "Max_L_mm", "Max_W_mm", "Max_H_mm", "Primary_Material", "Supports", "Difficulty", "Offer_Mode",
    "Digital_Price_Band_EUR", "Printed_Price_Band_EUR", "Risk_Score", "Risk_or_Limit", "Opportunity_Score",
    "Launch_Wave", "Source_IDs", "Design_Status", "Next_Gate", "Notes",
    "Trend_Source_Strength_0_30", "Trend_Signal_Magnitude_0_30", "Trend_MetriMade_Fit_0_25",
    "Trend_Whitespace_0_15", "Trend_Score_0_100", "Trend_Score_Basis", "Trend_Score_Status",
    "Preflight_Archetype", "Critical_Interface", "Evidence_Route", "Manufacturing_Baseline", "Verification_Plan",
    "REQ", "CTX", "PAR", "INT", "CPL", "MOT", "GEO", "PHY", "MAT", "EXT", "VER", "PC_0_100", "Complexity",
    "R_Scope", "R_Requirements", "R_Critical_Interfaces", "R_Manufacturing_Profile", "R_Verification",
    "Readiness", "Readiness_Basis", "Criticality", "Current_Lane", "Target_Lane_After_Evidence", "Confidence",
    "Design_Release", "Hard_Gates", "Preflight_Short", "Preflight_Status", "Assessed_On", "Assessment_Version",
    # Generative-pipeline columns.
    "Concept_Description", "Image_Prompt", "Generative_Route", "Mesh_Quality_Gate", "IP_Basis",
    "AI_Transparency_Duty", "Generative_Tool_Licence_Gate", "Trend_Evidence_Tier", "Opportunity_Score_Basis",
    # Manufacturing and commercial model. The names carrying a currency symbol match the
    # retained Unit Economics columns so that the workbook maps them into its own
    # commercial columns instead of creating a parallel vocabulary.
    "Size_Class", "Part_Strategy", "Secondary_BOM", "Printer_Class", "Enclosure", "Manufacturing Economics",
    "Mass g", "Print Time h", "Hands-on min", "Material", "Material €/kg", "Waste %", "Material Cost €",
    "Machine Class", "Machine €/h", "Machine Cost €", "Labor Cost €", "Packaging €",
    "Royalty / License €", "QA Reserve €", "Modeled Local COGS €", "Minimum Net Price €",
    "Recommended Net Price €", "VAT %", "Recommended Gross Price €", "Transaction Fee €",
    "Contribution €", "Contribution Margin", "Cost_Model_Basis",
]


def pc_score(scores: dict[str, int]) -> float:
    return round(sum(PREFLIGHT_WEIGHTS[key] * scores[key] / 4.0 for key in PREFLIGHT_WEIGHTS), 2)


def complexity_class(score: float) -> str:
    if score <= 14:
        return "C0"
    if score <= 24:
        return "C1"
    if score <= 39:
        return "C2"
    if score <= 59:
        return "C3"
    if score <= 79:
        return "C4"
    return "C5"


def target_lane(complexity: str, criticality: str) -> str:
    """Mirror the workbook's exact target-lane rule for a research estimate."""
    c = int(complexity[1:])
    k = int(criticality[1:])
    if k >= 4:
        return "E"
    if c >= 4 or k >= 3:
        return "D"
    if c >= 3 or k >= 2:
        return "C"
    if c <= 1 and k == 0:
        return "A"
    return "B"


def size_class(dimensions: tuple[float, float, float]) -> str:
    largest = max(dimensions)
    if largest < 110:
        return "S"
    if largest <= 240:
        return "M"
    return "L"


def round_up_half(value: float) -> float:
    return math.ceil(value * 2 - 1e-9) / 2


def economics(
    item: dict[str, object], archetype: dict[str, object], dimensions: tuple[float, float, float]
) -> dict[str, object]:
    """Model one unit cost and price block with the retained Unit Economics rules."""
    material = str(item.get("material") or archetype["material"])
    if material not in COST_MODEL["material_eur_per_kg"]:
        raise ValueError(f"Unknown material for SKU-{item['sku']}: {material}")
    machine_class = "Core"
    bounding_cm3 = dimensions[0] * dimensions[1] * dimensions[2] / 1000.0
    utilization = float(item.get("utilization") or archetype["utilization"])
    fill = float(item.get("fill") or archetype["fill"])
    mass_g = round(bounding_cm3 * utilization * fill * COST_MODEL["density_g_per_cm3"][material], 1)
    print_time_h = round(mass_g / float(archetype["throughput_g_per_h"]), 2)
    hands_on_min = int(item.get("hands_on_min") or archetype["hands_on_min"])
    klass = size_class(dimensions)
    material_eur_per_kg = COST_MODEL["material_eur_per_kg"][material]
    material_cost = round(mass_g / 1000.0 * (1 + COST_MODEL["waste_share"]) * material_eur_per_kg, 4)
    machine_rate = COST_MODEL["machine_eur_per_h"][machine_class]
    machine_cost = round(print_time_h * machine_rate, 4)
    labor_cost = round(hands_on_min / 60.0 * COST_MODEL["labor_eur_per_h"], 4)
    packaging = COST_MODEL["packaging_eur"][klass]
    royalty = COST_MODEL["royalty_eur"]
    qa_reserve = round(
        (material_cost + machine_cost + labor_cost + packaging + royalty) * COST_MODEL["qa_reserve_share"], 4
    )
    cogs = round(material_cost + machine_cost + labor_cost + packaging + royalty + qa_reserve, 4)
    net_price = round_up_half(cogs * COST_MODEL["net_price_cogs_multiple"])
    gross_price = round(net_price * (1 + COST_MODEL["vat_share"]), 2)
    fee = round(gross_price * COST_MODEL["transaction_fee_share"], 2)
    contribution = round(net_price - cogs - fee, 4)
    margin = round(contribution / net_price, 4)
    printed_band = f"{math.floor(gross_price * 0.9):g}-{math.ceil(gross_price * 1.25):g}"
    return {
        "Size_Class": klass,
        "Mass g": mass_g,
        "Print Time h": print_time_h,
        "Hands-on min": hands_on_min,
        "Material": material,
        "Material €/kg": material_eur_per_kg,
        "Waste %": COST_MODEL["waste_share"],
        "Material Cost €": material_cost,
        "Machine Class": machine_class,
        "Machine €/h": machine_rate,
        "Machine Cost €": machine_cost,
        "Labor Cost €": labor_cost,
        "Packaging €": packaging,
        "Royalty / License €": royalty,
        "QA Reserve €": qa_reserve,
        "Modeled Local COGS €": cogs,
        "Minimum Net Price €": COST_MODEL["minimum_net_price_eur"][klass],
        "Recommended Net Price €": net_price,
        "VAT %": COST_MODEL["vat_share"],
        "Recommended Gross Price €": gross_price,
        "Transaction Fee €": fee,
        "Contribution €": contribution,
        "Contribution Margin": margin,
        "Printed_Price_Band_EUR": printed_band,
        "Cost_Model_Basis": COST_MODEL_BASIS,
    }


def trend_components(item: dict[str, object]) -> tuple[int, int, int, int]:
    strength_tier, magnitude_tier, fit_tier, whitespace_tier = item["tiers"]
    return (
        TREND_TIERS["source_strength"][strength_tier],
        TREND_TIERS["signal_magnitude"][magnitude_tier],
        TREND_TIERS["fit"][fit_tier],
        TREND_TIERS["whitespace"][whitespace_tier],
    )


def build_rows() -> list[dict[str, object]]:
    expected_count = SKU_END - SKU_START + 1
    if len(ITEMS) != expected_count:
        raise ValueError(f"Expected {expected_count} generative items, found {len(ITEMS)}")
    if [int(item["sku"]) for item in ITEMS] != list(range(SKU_START, SKU_END + 1)):
        raise ValueError(f"Generative items must run from SKU-{SKU_START} to SKU-{SKU_END} in order")
    names = [str(item["name"]).strip().lower() for item in ITEMS]
    if len(names) != len(set(names)) or any(not name for name in names):
        raise ValueError("Generative items contain a blank or duplicate product name")

    rows: list[dict[str, object]] = []
    for item in ITEMS:
        sku_id = f"SKU-{int(item['sku']):03d}"
        group = GROUPS[str(item["group"])]
        archetype = ARCHETYPES[str(item["archetype"])]
        dimensions = tuple(float(value) for value in item["dims"])
        if len(dimensions) != 3 or dimensions[0] > 220 or dimensions[1] > 220 or dimensions[2] > 250:
            raise ValueError(f"{sku_id} exceeds the candidate 220 x 220 x 250 mm envelope")
        if min(dimensions) <= 0:
            raise ValueError(f"{sku_id} has a non-positive dimension")
        if len(str(item["purpose"]).strip()) < 20:
            raise ValueError(f"{sku_id} has no explicit purpose")

        strength, magnitude, fit, whitespace = trend_components(item)
        trend_score = strength + magnitude + fit + whitespace
        if trend_score <= 70:
            raise ValueError(f"{sku_id} fails the directional trend gate: {trend_score}")
        if not str(item["sources"]).strip():
            raise ValueError(f"{sku_id} has no cited research source")

        scores = dict(archetype["scores"])
        pc = pc_score(scores)
        complexity = complexity_class(pc)
        if complexity not in {"C1", "C2", "C3"}:
            raise ValueError(f"{sku_id} is outside the C1-C3 generative research band: {complexity}")
        criticality = str(item.get("criticality") or archetype["criticality"])
        if criticality not in {"K1", "K2"}:
            raise ValueError(f"{sku_id} is outside the K1-K2 generative research band: {criticality}")
        lane_after_evidence = target_lane(complexity, criticality)
        confidence = "LOW_UNKNOWN"

        commercial = economics(item, archetype, dimensions)
        margin_points = float(commercial["Contribution Margin"]) * 100.0
        opportunity = min(99.0, round(0.65 * trend_score + 0.35 * margin_points, 1))
        risk_score = int(item.get("risk_score") or (2 if criticality == "K2" else 1))
        g2 = str(item.get("g2", "WARN"))
        if g2 not in {"WARN", "FAIL"}:
            raise ValueError(f"{sku_id} has an invalid G2 evidence gate: {g2}")
        hard_gates = (
            f"G0 PASS; G1 PASS; G2 {g2}; G3 FAIL; G4 PASS; G5 PASS; G6 PASS; "
            "TOOL-LICENCE FAIL (Step1X-3D EU licence conflict)"
        )

        row = {
            "SKU_ID": sku_id,
            "Product": item["name"],
            "Product_Family": group["family"],
            "Concept_Type": item.get("concept_type", "New generative concept"),
            "Purpose": item["purpose"],
            "Customer_Job": item["purpose"],
            "Target_Segment": item.get("segment") or group["segment"],
            "Trend_Signal": item["trend"],
            "Strategy_Fit": item.get("strategy") or group["strategy"],
            "AM_Advantage": archetype["am"],
            "Customer_Inputs": group["inputs"],
            "Parametric_Variables": group["variables"],
            "Max_L_mm": f"{dimensions[0]:g}",
            "Max_W_mm": f"{dimensions[1]:g}",
            "Max_H_mm": f"{dimensions[2]:g}",
            "Primary_Material": commercial["Material"],
            "Supports": archetype["supports"],
            "Difficulty": archetype["difficulty"],
            "Offer_Mode": "Digital first; printed after fulfillment qualification",
            "Digital_Price_Band_EUR": archetype["digital_band"],
            "Printed_Price_Band_EUR": commercial["Printed_Price_Band_EUR"],
            "Risk_Score": risk_score,
            "Risk_or_Limit": item.get("risk") or group["risk"],
            "Opportunity_Score": opportunity,
            "Launch_Wave": "Research batch 4 — generative",
            "Source_IDs": item["sources"],
            "Design_Status": "P0 research backlog",
            "Next_Gate": (
                "Resolve the Step1X-3D licence conflict for EU commercial use first [S125][S126]; then: "
                + str(item.get("gate") or group["gate"])
            ),
            "Notes": NOTES,
            "Trend_Source_Strength_0_30": strength,
            "Trend_Signal_Magnitude_0_30": magnitude,
            "Trend_MetriMade_Fit_0_25": fit,
            "Trend_Whitespace_0_15": whitespace,
            "Trend_Score_0_100": trend_score,
            "Trend_Score_Basis": (
                "Primary-source strength + signal magnitude + metriMade strategy fit + nonduplicate portfolio "
                "whitespace, each from the documented tier table; the components are directional planning judgments."
            ),
            "Trend_Score_Status": "DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND",
            "Preflight_Archetype": str(item["archetype"]),
            "Critical_Interface": item.get("interface") or group["interface"],
            "Evidence_Route": group["evidence"],
            "Manufacturing_Baseline": (
                "Candidate baseline: common 220 x 220 x 250 mm FFF envelope, "
                f"{commercial['Material']}, {str(archetype['supports']).lower()} support strategy; the exact printer, "
                "filament product/color/batch, nozzle and process JSON remain UNKNOWN."
            ),
            "Verification_Plan": item.get("verification") or group["verification"],
            **scores,
            "PC_0_100": pc,
            "Complexity": complexity,
            "R_Scope": "R2",
            "R_Requirements": "R2",
            "R_Critical_Interfaces": "R2",
            "R_Manufacturing_Profile": "R2",
            "R_Verification": "R2",
            "Readiness": "R2",
            "Readiness_Basis": (
                "Purpose, exclusions, envelope, generative route, mesh-quality gate, critical interface, candidate "
                "process envelope and test method are specified; the exact generated mesh, the exact process profile "
                "and every rights, safety and demand check remain open."
            ),
            "Criticality": criticality,
            "Current_Lane": "E",
            "Target_Lane_After_Evidence": lane_after_evidence,
            "Confidence": confidence,
            "Design_Release": "CONCEPT_ONLY",
            "Hard_Gates": hard_gates,
            "Preflight_Short": f"{complexity} · R2 · {criticality} · Lane E · {confidence}",
            "Preflight_Status": "GENERATIVE STEP1X RESEARCH PREFLIGHT R2 — NOT PRODUCT RELEASE APPROVAL",
            "Assessed_On": ASSESSED_ON,
            "Assessment_Version": ASSESSMENT_VERSION,
            "Concept_Description": item["description"],
            "Image_Prompt": item["prompt"],
            "Generative_Route": f"{archetype['route']}; {item['route']}" if item.get("route") else archetype["route"],
            "Mesh_Quality_Gate": MESH_QUALITY_GATE,
            "IP_Basis": item.get("ip_basis") or IP_BASIS,
            "AI_Transparency_Duty": AI_TRANSPARENCY_DUTY,
            "Generative_Tool_Licence_Gate": TOOL_LICENCE_GATE,
            "Trend_Evidence_Tier": " / ".join(str(tier) for tier in item["tiers"]),
            "Opportunity_Score_Basis": OPPORTUNITY_BASIS,
            "Part_Strategy": archetype["part_strategy"],
            "Secondary_BOM": item.get("secondary_bom") or archetype["secondary_bom"],
            "Printer_Class": archetype["printer_class"],
            "Enclosure": "No",
            "Manufacturing Economics": archetype["label"],
        }
        row.update({key: value for key, value in commercial.items() if key != "Printed_Price_Band_EUR"})
        missing = [name for name in FIELDNAMES if name not in row]
        if missing:
            raise ValueError(f"{sku_id} is missing generated fields: {', '.join(missing)}")
        unknown = [name for name in row if name not in FIELDNAMES]
        if unknown:
            raise ValueError(f"{sku_id} produced unknown fields: {', '.join(unknown)}")
        rows.append(row)
    return rows


def render(rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the checked-in CSV is stale or missing.")
    args = parser.parse_args()
    content = render(build_rows())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale or missing generative research additions: {OUTPUT}")
        print(f"PASS: {OUTPUT} is current with {SKU_END - SKU_START + 1} generative research rows")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} with {SKU_END - SKU_START + 1} generative research rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
