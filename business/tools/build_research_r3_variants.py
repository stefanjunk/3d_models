#!/usr/bin/env python3
"""Build evidence-backed specific research variants SKU-301 through SKU-314."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_ROOT = REPO_ROOT / "business/02-portfolio"
OUTPUT = PORTFOLIO_ROOT / "research-ideas-r3-variants.csv"
PRIORITY_CSV = PORTFOLIO_ROOT / "research-idea-priority.csv"
PROCESS_BASELINE = PORTFOLIO_ROOT / "research-r3-process-baseline.json"
ASSESSED_ON = "2026-08-31"
ASSESSMENT_VERSION = "1.0"

WEIGHTS = {
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

ARCHETYPES = {
    "SIMPLE_DISPLAY": {
        "scores": {"REQ": 1, "CTX": 1, "PAR": 1, "INT": 1, "CPL": 0, "MOT": 0, "GEO": 1, "PHY": 0, "MAT": 1, "EXT": 1, "VER": 1},
        "difficulty": "Easy",
        "verification": "Inspect the source-defined planform, print one two-datum contact coupon, and verify free insertion/removal, edge condition, 10-degree bump stability and no visible marking on one real item.",
        "acceptance": "All source-defined datums are within 0.30 mm on the coupon; the item inserts and removes without force, remains upright after a 10-degree base tilt, and shows no visible mark after 20 cycles.",
        "risk": "Dry adult tabletop display only; no archival, impact-protection, security, child-use or wall/vehicle-use claim.",
        "prices": ("6-12", "18-32"),
    },
    "EXACT_CRADLE": {
        "scores": {"REQ": 2, "CTX": 2, "PAR": 1, "INT": 2, "CPL": 1, "MOT": 0, "GEO": 1, "PHY": 1, "MAT": 2, "EXT": 1, "VER": 2},
        "difficulty": "Moderate",
        "verification": "Generate an interface coupon from the cited nominal drawing, inspect it dimensionally, then test free insertion/removal, stable support, keep-out clearance, surface marking and 100 placement cycles with the exact named product revision.",
        "acceptance": "Coupon datums are within 0.30 mm; insertion requires no force; all declared keep-outs remain open; the item remains stable at 10 degrees base tilt; no visible marking or functional interference occurs after 100 cycles.",
        "risk": "Dry stationary adult desk use only; no charging, carry, vehicle, wall, impact-protection, RF-performance, security or child-use claim.",
        "prices": ("9-18", "27-55"),
    },
    "COIN_TRAY": {
        "scores": {"REQ": 2, "CTX": 1, "PAR": 1, "INT": 2, "CPL": 1, "MOT": 0, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 1, "VER": 2},
        "difficulty": "Moderate",
        "verification": "Inspect every denomination recess, print the tightest three-recess coupon, and verify free placement/removal, denomination separation, tip stability and 100 sorting cycles with circulating euro coins.",
        "acceptance": "Each denomination enters its labeled open recess without force and can be removed by finger notch; no coin enters a smaller-denomination recess; the loaded tray remains stable at 10 degrees and passes 100 sorting cycles without cracking.",
        "risk": "Adult dry coin sorting only; no secure storage, authentication, counting-machine, child-use or financial-protection claim.",
        "prices": ("8-16", "24-45"),
    },
    "SYSTEM_INSERT": {
        "scores": {"REQ": 3, "CTX": 2, "PAR": 3, "INT": 3, "CPL": 2, "MOT": 0, "GEO": 2, "PHY": 2, "MAT": 2, "EXT": 2, "VER": 3},
        "difficulty": "Moderate",
        "verification": "Build a three-value fit gauge around the official companion-product envelope, inspect every module and seam, then test the gauge and unloaded modular set in one exact host article before any compatibility statement.",
        "acceptance": "The minus/nominal/plus gauge identifies a freely removable fit without rubbing; all modules remain inside the selected nominal envelope, seams stay below 0.50 mm under light hand pressure, the host closes normally, and 100 removal cycles cause no visible marking.",
        "risk": "Adult dry removable organization only; no structural furniture, load-bearing, anti-tip, child-use or guaranteed cross-revision compatibility claim.",
        "prices": ("16-32", "55-120"),
    },
}

COMMON = {
    "Target_Segment": "Adults seeking precise, low-risk organization or display accessories",
    "Strategy_Fit": "Core — exact named-format or named-product organization with a guided metriMade proposition",
    "AM_Advantage": "A named nominal interface can become a low-volume exact variant while the generic parent remains available for other dimensions.",
    "Primary_Material": "SUNLU PETG Black",
    "Supports": "None",
    "Offer_Mode": "Digital first after physical qualification; printed later after fulfillment qualification",
    "Design_Status": "P0 evidence-backed specific variant",
    "Manufacturing_Baseline": "MM-R3-K3MAX-PETG-0P4-0P20-2026-08-31; flat stable base down; support-free",
    "Process_Profile_Refs": "business/02-portfolio/research-r3-process-baseline.json",
    "Readiness_Basis": "The exact variant, intended use and exclusions are fixed; critical interface nominals come from a cited primary source; one exact hashed printer/material/nozzle/orientation/process baseline is pinned; acceptance criteria and a coupon/prototype method are defined. Independent dimensional and physical validation is still missing, so readiness stops at R3.",
    "Hard_Gates": "G0 PASS; G1 PASS; G2 PASS; G3 PASS; G4 PASS; G5 PASS; G6 PASS",
    "Confidence": "CONDITIONAL",
    "Design_Release": "GO_WITH_CONTROLS",
    "Preflight_Status": "STRUCTURED SPECIFIC-VARIANT PREFLIGHT R3 — NOT PRODUCT RELEASE APPROVAL",
}


VARIANTS = [
    {
        "sku": "SKU-301",
        "parent": "SKU-005",
        "product": "iPhone 17 Pro no-case passive desk cradle",
        "family": "Named-device passive desk stands",
        "purpose": "Support one uncased 2025 iPhone 17 Pro on a stable dry desk in portrait or landscape while leaving Apple-defined camera, control, connector and radio keep-outs unobstructed.",
        "trend": (29, 28, 25, 11),
        "trend_signal": "The parent passive-phone-stand opportunity scores 93; this variant narrows it to Apple's current iPhone 17 Pro dimensional drawing without treating specificity as new demand proof.",
        "sources": "S03; S05; S09; S11; S19; S37; S38; S53",
        "interface_sources": "S37; S38",
        "archetype": "EXACT_CRADLE",
        "interface": "Uncased iPhone 17 Pro external envelope and Apple-defined accessory keep-outs",
        "nominals": "Apple drawing dated 2025-09-09 plus official 71.9 x 150.0 x 8.75 mm body envelope; retain all drawing-defined camera, control, connector, magnetic and radio keep-outs.",
        "evidence_limit": "Apple nominal drawing only; no case, skin, tolerance stack, damaged device or future revision is covered, and Apple's terms/trademark rules require release review.",
        "inputs": "Exact model confirmation: iPhone 17 Pro introduced 2025; uncased use only; portrait/landscape choice; optional label text",
        "variables": "viewing angle; portrait/landscape stop; nominal clearance; base depth; label; keep-out margins",
        "dims": (140, 110, 100),
        "opportunity": 93,
        "next_gate": "Create a drawing-derived keep-out coupon, inspect it, and test the exact uncased device before any compatibility wording or full stand.",
        "notes": "Specific child of the generic passive phone stand; commercial release also needs Apple guideline and trademark review.",
    },
    {
        "sku": "SKU-302",
        "parent": "SKU-236",
        "product": "TRAVELER'S notebook Regular Black starter-kit desk bridge",
        "family": "Named-notebook desk organization",
        "purpose": "Park one current TRAVELER'S notebook Regular Black starter kit No.13714006 in a dry desk bridge without compressing its leather cover, elastic or bookmark.",
        "trend": (30, 28, 25, 11),
        "trend_signal": "The parent journaling concept scores 94; the current manufacturer starter-kit dimensions make this a measurable variant but do not prove variant demand.",
        "sources": "S36; S01; S32; S39; S53",
        "interface_sources": "S39",
        "archetype": "EXACT_CRADLE",
        "interface": "TRAVELER'S notebook Regular Black No.13714006 closed leather-cover envelope",
        "nominals": "Leather cover H220 x W120 x D10 mm; supplied refill H210 x W110 x D4 mm; all elastic and bookmark paths remain open.",
        "evidence_limit": "Leather is compliant and may age or swell; only the named current black starter kit is in scope until a real sample closes tolerance and surface-contact evidence.",
        "inputs": "Exact starter-kit article No.13714006; closed cover; one supplied refill; optional pen-zone and label text",
        "variables": "ledge clearance; back angle; open elastic keep-out; pen-zone count; label",
        "dims": (170, 120, 105),
        "opportunity": 94,
        "next_gate": "Print a 120 x 10 mm contact coupon and test the exact starter kit for free placement, elastic clearance and leather marking.",
        "notes": "Specific child of the generic traveler-notebook template station; no other historical Regular-size envelope is implied.",
    },
    {
        "sku": "SKU-303",
        "parent": "SKU-231",
        "product": "Field Notes Original Kraft 89 x 140 memo-book station",
        "family": "Named-notebook desk organization",
        "purpose": "Register one closed Field Notes Original Kraft memo book against two loose desk datums for a repeatable writing and display position without clamping its spine.",
        "trend": (30, 28, 25, 11),
        "trend_signal": "The parent analog-writing concept scores 94; the official Original Kraft dimensions enable a precise child variant without adding demand evidence.",
        "sources": "S36; S01; S32; S40; S53",
        "interface_sources": "S40",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "Field Notes Original Kraft memo-book planform",
        "nominals": "3.5 x 5.5 in, published as 89 x 140 mm; open top and spine side mean thickness is not a fit interface.",
        "evidence_limit": "Only the published planform is controlled; cover bow, corner wear and future edition changes remain physical-test variables.",
        "inputs": "Field Notes Original Kraft 89 x 140 mm; left- or right-spine datum; optional label",
        "variables": "datum clearance; desk angle; finger relief; label",
        "dims": (175, 115, 55),
        "opportunity": 94,
        "next_gate": "Print the two-datum corner coupon and verify one current Original Kraft book without clamping or cover marking.",
        "notes": "Specific child of the generic notebook desk bridge; no other Field Notes edition is implied.",
    },
    {
        "sku": "SKU-304",
        "parent": "SKU-287",
        "product": "instax mini 86 x 54 two-datum photo dock",
        "family": "Named instant-photo display",
        "purpose": "Display one developed FUJIFILM instax mini print on an open-front two-datum desk dock without gripping or claiming archival protection.",
        "trend": (28, 28, 25, 11),
        "trend_signal": "The parent celebration photo dock scores 92; the official instax mini format creates an exact child interface, not separate demand proof.",
        "sources": "S33; S01; S32; S41; S53",
        "interface_sources": "S41",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "Developed FUJIFILM instax mini photo planform",
        "nominals": "Film/photo format 86 x 54 mm; image area 62 x 46 mm; open front and side prevent thickness from becoming a fit-critical interface.",
        "evidence_limit": "No archival, fresh-development, chemical, UV or long-term storage claim; physical print flatness and surface marking remain unverified.",
        "inputs": "One fully developed dry instax mini print; portrait or landscape; optional name/date",
        "variables": "orientation; datum clearance; viewing angle; label; base proportions",
        "dims": (125, 85, 80),
        "opportunity": 92,
        "next_gate": "Print one 86 x 54 mm contact coupon and test a fully developed dry print for free removal, stability and marking.",
        "notes": "Specific child of the generic card-and-photo dock; thickness is deliberately non-retaining.",
    },
    {
        "sku": "SKU-305",
        "parent": "SKU-287",
        "product": "instax SQUARE 86 x 72 two-datum photo dock",
        "family": "Named instant-photo display",
        "purpose": "Display one developed FUJIFILM instax SQUARE print on an open-front two-datum desk dock without gripping or claiming archival protection.",
        "trend": (28, 28, 25, 11),
        "trend_signal": "The parent celebration photo dock scores 92; the official instax SQUARE format creates an exact child interface, not separate demand proof.",
        "sources": "S33; S01; S32; S42; S53",
        "interface_sources": "S42",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "Developed FUJIFILM instax SQUARE photo planform",
        "nominals": "Film/photo format 86 x 72 mm; image area 62 x 62 mm; open front and side prevent thickness from becoming a fit-critical interface.",
        "evidence_limit": "No archival, fresh-development, chemical, UV or long-term storage claim; physical print flatness and surface marking remain unverified.",
        "inputs": "One fully developed dry instax SQUARE print; optional name/date",
        "variables": "datum clearance; viewing angle; label; base proportions",
        "dims": (125, 95, 95),
        "opportunity": 92,
        "next_gate": "Print one 86 x 72 mm contact coupon and test a fully developed dry print for free removal, stability and marking.",
        "notes": "Specific child of the generic card-and-photo dock; thickness is deliberately non-retaining.",
    },
    {
        "sku": "SKU-306",
        "parent": "SKU-287",
        "product": "instax WIDE 108 x 86 two-datum photo dock",
        "family": "Named instant-photo display",
        "purpose": "Display one developed FUJIFILM instax WIDE print on an open-front two-datum desk dock without gripping or claiming archival protection.",
        "trend": (28, 28, 25, 11),
        "trend_signal": "The parent celebration photo dock scores 92; the official instax WIDE format creates an exact child interface, not separate demand proof.",
        "sources": "S33; S01; S32; S43; S53",
        "interface_sources": "S43",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "Developed FUJIFILM instax WIDE photo planform",
        "nominals": "Film/photo format 108 x 86 mm; open front and side prevent thickness from becoming a fit-critical interface.",
        "evidence_limit": "No archival, fresh-development, chemical, UV or long-term storage claim; physical print flatness and surface marking remain unverified.",
        "inputs": "One fully developed dry instax WIDE print; portrait or landscape; optional name/date",
        "variables": "orientation; datum clearance; viewing angle; label; base proportions",
        "dims": (150, 115, 105),
        "opportunity": 92,
        "next_gate": "Print one 108 x 86 mm contact coupon and test a fully developed dry print for free removal, stability and marking.",
        "notes": "Specific child of the generic card-and-photo dock; thickness is deliberately non-retaining.",
    },
    {
        "sku": "SKU-307",
        "parent": "SKU-287",
        "product": "Polaroid i-Type 107 x 88 two-datum photo dock",
        "family": "Named instant-photo display",
        "purpose": "Display one fully developed Polaroid i-Type print on an open-front two-datum desk dock without gripping or claiming archival protection.",
        "trend": (28, 28, 25, 11),
        "trend_signal": "The parent celebration photo dock scores 92; Polaroid's official i-Type dimensions create an exact child interface, not separate demand proof.",
        "sources": "S33; S01; S32; S44; S53",
        "interface_sources": "S44",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "Developed Polaroid i-Type photo planform",
        "nominals": "Official format 107 x 88 mm; open front and side prevent media thickness from becoming a fit-critical interface.",
        "evidence_limit": "No archival, fresh-development, chemical, UV or long-term storage claim; current film is reported thicker than historical film and must be tested physically.",
        "inputs": "One fully developed dry Polaroid i-Type print; optional name/date",
        "variables": "datum clearance; viewing angle; label; base proportions",
        "dims": (150, 115, 105),
        "opportunity": 92,
        "next_gate": "Print one 107 x 88 mm contact coupon and test a fully developed current i-Type print for free removal, stability and marking.",
        "notes": "Specific child of the generic card-and-photo dock; no vintage-film fit or protection claim.",
    },
    {
        "sku": "SKU-308",
        "parent": "SKU-287",
        "product": "Polaroid Go 66.6 x 53.9 two-datum photo dock",
        "family": "Named instant-photo display",
        "purpose": "Display one fully developed Polaroid Go print on an open-front two-datum desk dock without gripping or claiming archival protection.",
        "trend": (28, 28, 25, 11),
        "trend_signal": "The parent celebration photo dock scores 92; Polaroid's official Go dimensions create an exact child interface, not separate demand proof.",
        "sources": "S33; S01; S32; S45; S53",
        "interface_sources": "S45",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "Developed Polaroid Go photo planform",
        "nominals": "Official format 66.6 x 53.9 mm; image area 47 x 46 mm; open front and side prevent thickness from becoming a fit-critical interface.",
        "evidence_limit": "No archival, fresh-development, chemical, UV or long-term storage claim; physical print flatness and marking remain unverified.",
        "inputs": "One fully developed dry Polaroid Go print; optional name/date",
        "variables": "datum clearance; viewing angle; label; base proportions",
        "dims": (110, 80, 80),
        "opportunity": 92,
        "next_gate": "Print one 66.6 x 53.9 mm contact coupon and test a fully developed Go print for free removal, stability and marking.",
        "notes": "Specific child of the generic card-and-photo dock; thickness is deliberately non-retaining.",
    },
    {
        "sku": "SKU-309",
        "parent": "SKU-225",
        "product": "DIN C6 114 x 162 empty-envelope vertical file",
        "family": "Standard-format correspondence organization",
        "purpose": "Keep empty DIN C6 envelopes upright in a loose open-top desk file with format labeling and finger access, without claiming postal accuracy or a fixed sheet capacity.",
        "trend": (28, 27, 25, 11),
        "trend_signal": "The pen-pal/envelope parent scores 91; Deutsche Post's published C6 dimensions make the interface nominally complete but do not validate German product demand.",
        "sources": "S36; S01; S32; S46; S53",
        "interface_sources": "S46",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "DIN C6 empty-envelope planform",
        "nominals": "DIN C6 nominal 114 x 162 mm; one loose 18 mm open-top bay; no fixed envelope count or thickness fit claim.",
        "evidence_limit": "Paper thickness, closure, contents, bow and manufacturer tolerances vary; only empty C6 format and a loose bay are in scope.",
        "inputs": "Empty DIN C6 envelopes only; one 18 mm loose bay; optional category label",
        "variables": "bay count; bay depth; finger relief; label; base depth",
        "dims": (200, 95, 145),
        "opportunity": 91,
        "next_gate": "Print one C6 bay coupon and test at least three empty-envelope brands for free insertion, snagging and tip stability.",
        "notes": "Specific child of the generic envelope-size file; capacity remains a measured option rather than a count promise.",
    },
    {
        "sku": "SKU-310",
        "parent": "SKU-211",
        "product": "Euro eight-denomination weekly sorting tray",
        "family": "Standardized coin organization",
        "purpose": "Sort circulating euro coins from 1 cent through 2 euro into eight labeled, open finger-access recesses during an adult weekly pocket-emptying routine.",
        "trend": (28, 27, 24, 11),
        "trend_signal": "The weekly pocket-purge parent scores 90; ECB coin dimensions make the child interface exact but do not create additional market evidence.",
        "sources": "S31; S32; S47; S53",
        "interface_sources": "S47",
        "archetype": "COIN_TRAY",
        "interface": "Eight circulating euro-coin denomination envelopes",
        "nominals": "ECB nominal diameter/thickness in mm: 2 EUR 25.75/2.20; 1 EUR 23.25/2.33; 50c 24.25/2.38; 20c 22.25/2.14; 10c 19.75/1.93; 5c 21.25/1.67; 2c 18.75/1.67; 1c 16.25/1.67; open circular recesses use 0.60 mm diametral design clearance and finger notches.",
        "evidence_limit": "Nominal ECB dimensions do not replace physical checks across mints, wear and contamination; no authentication, secure-storage or automated-counting claim.",
        "inputs": "Circulating euro coins; denomination set; optional labels; maximum 20 coins per open recess",
        "variables": "recess layout; 0.60 mm nominal diameter clearance; finger notch; label; tray footprint",
        "dims": (210, 150, 28),
        "opportunity": 90,
        "next_gate": "Print the 50c/20c/5c tightest discrimination coupon and test worn circulating coins before the full eight-recess tray.",
        "notes": "Specific child of the generic weekly coin-and-receipt tray; denomination geometry is standardized while demand remains directional.",
    },
    {
        "sku": "SKU-311",
        "parent": "SKU-038",
        "product": "Gamegenic Prime 66 x 91 single-card display rail",
        "family": "Named board-game card accessories",
        "purpose": "Hold one card inside a current Gamegenic Prime 66 x 91 mm sleeve on an open-front tabletop rail for reading during adult play without retaining a deck or promising protection.",
        "trend": (27, 22, 18, 9),
        "trend_signal": "The generic tabletop card-holder parent scores 76; the current Gamegenic Prime sleeve specification raises interface maturity, not trend or demand confidence.",
        "sources": "S01; S04; S11; S16; S48; S53",
        "interface_sources": "S48",
        "archetype": "SIMPLE_DISPLAY",
        "interface": "One current Gamegenic Prime standard sleeved card planform",
        "nominals": "Prime sleeve 66 x 91 mm for cards up to 64 x 89 mm; open front and side mean card/sleeve stack thickness is not a fit interface.",
        "evidence_limit": "Only one current Prime-sleeved card is in scope; deck stacks, other sleeve lines, double sleeves and protective claims require separate variants.",
        "inputs": "One current Gamegenic Prime 66 x 91 mm sleeved card; tabletop viewing angle; optional label",
        "variables": "datum clearance; viewing angle; rail length; label; finger relief",
        "dims": (130, 85, 75),
        "opportunity": 76,
        "next_gate": "Print one 66 x 91 mm two-datum coupon and test a current Prime sleeve for free insertion, visibility and marking.",
        "notes": "Specific child of the generic tabletop card holder; no deck-capacity or protection claim.",
    },
    {
        "sku": "SKU-312",
        "parent": "SKU-220",
        "product": "AirTag 2nd-generation open-top desk display tile",
        "family": "Named keepsake and tracker display",
        "purpose": "Present one 2026 AirTag (2nd generation) in a shallow open-top adult desk tile without covering it, carrying it or claiming RF, speaker, battery, water or impact performance.",
        "trend": (28, 28, 24, 12),
        "trend_signal": "The sentimental-object rotation parent scores 92; Apple's 2026 dimensions define a new-revision child interface but do not prove variant demand.",
        "sources": "S31; S32; S49; S53",
        "interface_sources": "S49",
        "archetype": "EXACT_CRADLE",
        "interface": "AirTag (2nd generation, 2026) open-top circular envelope",
        "nominals": "Diameter 31.9 mm; height 8.0 mm; weight 11.8 g; open top, 0.60 mm diametral design clearance and a full finger notch.",
        "evidence_limit": "No first-generation interchangeability, retention, carry, loss prevention, RF, speaker, battery, water or impact claim; nominal dimensions lack production tolerances.",
        "inputs": "One AirTag 2nd generation introduced 2026; open tabletop display; optional label",
        "variables": "diametral clearance; recess depth; finger notch; label; tile footprint",
        "dims": (80, 80, 16),
        "opportunity": 92,
        "next_gate": "Print the 32.5 mm open recess coupon and test one exact second-generation AirTag for free removal, sound opening and surface marking.",
        "notes": "Specific child of the generic sentimental-object rotation tray; explicitly excludes a protective or carry accessory.",
    },
    {
        "sku": "SKU-313",
        "parent": "SKU-001",
        "product": "IKEA ALEX 004.735.46 upper-drawer modular inlay set",
        "family": "Named-system furniture organization",
        "purpose": "Tile the nominal footprint evidenced by IKEA ALEX drawer unit 004.735.46 and companion insert 305.951.55 with removable dry desk-item modules while preserving the generic DrawerFit product separately.",
        "trend": (30, 29, 25, 12),
        "trend_signal": "The exact-fit drawer parent scores 96; the named ALEX unit and its official companion insert provide a high-priority nominal variant, not a cross-revision compatibility guarantee.",
        "sources": "S05; S06; S11; S19; S31; S32; S50; S51; S53",
        "interface_sources": "S50; S51",
        "archetype": "SYSTEM_INSERT",
        "interface": "IKEA ALEX 004.735.46 drawer envelope represented by official companion insert 305.951.55",
        "nominals": "ALEX 004.735.46 published internal drawer depth 520 mm; companion insert 305.951.55 external L520 x W300 x H50 mm and explicitly intended for ALEX drawers; printed set stays inside a 517 x 297 x 47 mm design envelope and is split into common-bed modules.",
        "evidence_limit": "The 520 x 300 x 50 mm companion insert is an official nominal envelope proxy, not a unit-specific drawer tolerance; article, market, assembly and wear still require a three-value gauge.",
        "inputs": "IKEA ALEX article 004.735.46; exact drawer position; nominal companion-insert envelope; item list; optional labels",
        "variables": "module grid; 517 x 297 x 47 mm maximum assembled envelope; seam clearance; compartment layout; finger relief; labels",
        "dims": (210, 198, 47),
        "opportunity": 96,
        "next_gate": "Print 296.3/297.0/297.7 mm width gauges and a 210 mm seam coupon, then measure one exact ALEX 004.735.46 unit before any compatibility wording.",
        "notes": "Specific R3 child of generic DrawerFit; the existing ALEX measurement pilot remains at its current evidence level and is not silently upgraded.",
    },
    {
        "sku": "SKU-314",
        "parent": "SKU-117",
        "product": "IKEA KALLAX 703.402.99 nominal-envelope divider matrix",
        "family": "Named-system furniture organization",
        "purpose": "Create a removable multi-part divider matrix that stays inside the official KALLAX 703.402.99 insert envelope while preserving the generic cubby-divider concept for other furniture.",
        "trend": (30, 25, 25, 8),
        "trend_signal": "IKEA's storage signal and the named KALLAX companion insert support an 88-point directional planning score; this is not German product-level demand proof.",
        "sources": "S31; S11; S19; S32; S52; S53",
        "interface_sources": "S52",
        "archetype": "SYSTEM_INSERT",
        "interface": "KALLAX cubby envelope represented by official insert 703.402.99",
        "nominals": "Official KALLAX insert 703.402.99 external W330 x D380 x H330 mm and explicitly intended for KALLAX; divider assembly stays within a 327 x 375 x 327 mm design envelope and is split into common-bed modules.",
        "evidence_limit": "The official insert envelope is a nominal compatibility proxy, not a unit-specific cubby tolerance; shelf squareness, finish, revision and assembly variation require a three-value gauge.",
        "inputs": "KALLAX host and country/article confirmation; nominal 703.402.99 envelope; collection-item sizes; divider layout; labels",
        "variables": "module split; 327 x 375 x 327 mm assembled envelope; seam clearance; cell count; access relief; labels",
        "dims": (210, 190, 210),
        "opportunity": 88,
        "next_gate": "Print 326.3/327.0/327.7 mm span gauges and one module seam, then test one exact KALLAX unit before any compatibility wording.",
        "notes": "Specific R3 child of the generic cubby divider; the broad KALLAX family and internal variants remain outside the claim.",
    },
]

FIELDNAMES = [
    "SKU_ID", "Parent_SKU_ID", "Product", "Product_Family", "Concept_Type", "Purpose", "Customer_Job",
    "Target_Segment", "Trend_Signal", "Strategy_Fit", "AM_Advantage", "Customer_Inputs", "Parametric_Variables",
    "Max_L_mm", "Max_W_mm", "Max_H_mm", "Primary_Material", "Supports", "Difficulty", "Offer_Mode",
    "Digital_Price_Band_EUR", "Printed_Price_Band_EUR", "Risk_Score", "Risk_or_Limit", "Opportunity_Score",
    "Launch_Wave", "Source_IDs", "Design_Status", "Next_Gate", "Notes", "Trend_Source_Strength_0_30",
    "Trend_Signal_Magnitude_0_30", "Trend_MetriMade_Fit_0_25", "Trend_Whitespace_0_15", "Trend_Score_0_100",
    "Trend_Score_Basis", "Trend_Score_Status", "Preflight_Archetype", "Interface_Source_IDs", "Critical_Interface",
    "Interface_Nominals", "Evidence_Route", "Interface_Evidence_Limit", "Manufacturing_Baseline", "Process_Profile_Refs",
    "Verification_Plan", "Acceptance_Criteria", "REQ", "CTX", "PAR", "INT", "CPL", "MOT", "GEO", "PHY",
    "MAT", "EXT", "VER", "PC_0_100", "Complexity", "R_Scope", "R_Requirements", "R_Critical_Interfaces",
    "R_Manufacturing_Profile", "R_Verification", "Readiness", "Readiness_Basis", "Criticality", "Current_Lane",
    "Target_Lane_After_Evidence", "Confidence", "Design_Release", "Hard_Gates", "Preflight_Short", "Preflight_Status",
    "Assessed_On", "Assessment_Version",
]


def read_dict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_process_baseline() -> None:
    baseline = json.loads(PROCESS_BASELINE.read_text(encoding="utf-8"))
    if baseline.get("status") != "RESEARCH_DESIGN_BASELINE_ONLY":
        raise ValueError("Research R3 process baseline lacks its release boundary")
    for artifact in baseline["profile_artifacts"]:
        path = REPO_ROOT / artifact["path"]
        if not path.is_file():
            raise ValueError(f"Missing process-baseline artifact: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != artifact["sha256"]:
            raise ValueError(f"Process-baseline hash mismatch: {path}")


def complexity_for(scores: dict[str, int]) -> tuple[float, str]:
    for field, value in scores.items():
        if field not in WEIGHTS or not 0 <= value <= 4:
            raise ValueError(f"Invalid preflight score {field}={value}")
    pc = round(sum(WEIGHTS[field] * scores[field] / 4 for field in WEIGHTS), 2)
    complexity = "C0" if pc <= 14 else "C1" if pc <= 24 else "C2" if pc <= 39 else "C3" if pc <= 59 else "C4" if pc <= 79 else "C5"
    return pc, complexity


def build_rows() -> list[dict[str, object]]:
    validate_process_baseline()
    parent_rows = {row["SKU_ID"]: row for row in read_dict_rows(PRIORITY_CSV) if int(row["SKU_ID"].split("-")[1]) <= 300}
    expected_parents = {variant["parent"] for variant in VARIANTS}
    if expected_parents.difference(parent_rows):
        raise ValueError(f"Unknown parent SKU(s): {sorted(expected_parents.difference(parent_rows))}")
    expected_ids = {f"SKU-{number:03d}" for number in range(301, 315)}
    actual_ids = {variant["sku"] for variant in VARIANTS}
    if actual_ids != expected_ids or len(actual_ids) != len(VARIANTS):
        raise ValueError("Specific variants must contain each SKU-301 through SKU-314 exactly once")

    output: list[dict[str, object]] = []
    for variant in VARIANTS:
        archetype = ARCHETYPES[variant["archetype"]]
        scores = archetype["scores"]
        pc, complexity = complexity_for(scores)
        if complexity not in {"C1", "C2", "C3"}:
            raise ValueError(f"Specific variant exceeds the intended C1-C3 scope: {variant['sku']}")
        lane = "C" if complexity == "C3" else "B"
        trend = sum(variant["trend"])
        if trend <= 70:
            raise ValueError(f"Specific variant trend gate failed: {variant['sku']}")
        price_digital, price_printed = archetype["prices"]
        launch_wave = "R3 advancement wave 1 — high trend / low complexity" if complexity in {"C1", "C2"} and trend >= 85 else "R3 advancement wave 2 — specific COTS/system interface"
        row: dict[str, object] = {
            "SKU_ID": variant["sku"],
            "Parent_SKU_ID": variant["parent"],
            "Product": variant["product"],
            "Product_Family": variant["family"],
            "Concept_Type": f"Specific R3 variation of {variant['parent']}",
            "Purpose": variant["purpose"],
            "Customer_Job": variant["purpose"],
            "Target_Segment": COMMON["Target_Segment"],
            "Trend_Signal": variant["trend_signal"],
            "Strategy_Fit": COMMON["Strategy_Fit"],
            "AM_Advantage": COMMON["AM_Advantage"],
            "Customer_Inputs": variant["inputs"],
            "Parametric_Variables": variant["variables"],
            "Max_L_mm": variant["dims"][0],
            "Max_W_mm": variant["dims"][1],
            "Max_H_mm": variant["dims"][2],
            "Primary_Material": COMMON["Primary_Material"],
            "Supports": COMMON["Supports"],
            "Difficulty": archetype["difficulty"],
            "Offer_Mode": COMMON["Offer_Mode"],
            "Digital_Price_Band_EUR": price_digital,
            "Printed_Price_Band_EUR": price_printed,
            "Risk_Score": 2 if complexity == "C3" or variant["sku"] == "SKU-301" else 1,
            "Risk_or_Limit": archetype["risk"],
            "Opportunity_Score": variant["opportunity"],
            "Launch_Wave": launch_wave,
            "Source_IDs": variant["sources"],
            "Design_Status": COMMON["Design_Status"],
            "Next_Gate": variant["next_gate"],
            "Notes": variant["notes"] + " Trend and opportunity remain directional; R3 is design-input maturity, not demand or product qualification.",
            "Trend_Source_Strength_0_30": variant["trend"][0],
            "Trend_Signal_Magnitude_0_30": variant["trend"][1],
            "Trend_MetriMade_Fit_0_25": variant["trend"][2],
            "Trend_Whitespace_0_15": variant["trend"][3],
            "Trend_Score_0_100": trend,
            "Trend_Score_Basis": f"Inherited from or calibrated to parent {variant['parent']} and kept separate from the new interface evidence; specificity does not count as demand proof.",
            "Trend_Score_Status": "INHERITED DIRECTIONAL PLANNING SCORE — NOT VALIDATED VARIANT DEMAND",
            "Preflight_Archetype": variant["archetype"],
            "Interface_Source_IDs": variant["interface_sources"],
            "Critical_Interface": variant["interface"],
            "Interface_Nominals": variant["nominals"],
            "Evidence_Route": "E3 primary-source nominal data for the exact named variant; independent measurement and physical fit remain open.",
            "Interface_Evidence_Limit": variant["evidence_limit"],
            "Manufacturing_Baseline": COMMON["Manufacturing_Baseline"],
            "Process_Profile_Refs": COMMON["Process_Profile_Refs"],
            "Verification_Plan": archetype["verification"],
            "Acceptance_Criteria": archetype["acceptance"],
            **scores,
            "PC_0_100": pc,
            "Complexity": complexity,
            "R_Scope": "R3",
            "R_Requirements": "R3",
            "R_Critical_Interfaces": "R3",
            "R_Manufacturing_Profile": "R3",
            "R_Verification": "R3",
            "Readiness": "R3",
            "Readiness_Basis": COMMON["Readiness_Basis"],
            "Criticality": "K1",
            "Current_Lane": lane,
            "Target_Lane_After_Evidence": lane,
            "Confidence": COMMON["Confidence"],
            "Design_Release": COMMON["Design_Release"],
            "Hard_Gates": COMMON["Hard_Gates"],
            "Preflight_Short": f"{complexity} · R3 · K1 · Lane {lane} · CONDITIONAL",
            "Preflight_Status": COMMON["Preflight_Status"],
            "Assessed_On": ASSESSED_ON,
            "Assessment_Version": ASSESSMENT_VERSION,
        }
        output.append(row)
    return output


def render(rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the generated variant CSV is missing or stale.")
    args = parser.parse_args()
    content = render(build_rows())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale or missing generated specific-variant register: {OUTPUT}")
        print(f"PASS: {OUTPUT} is current with {len(VARIANTS)} specific R3 variants")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(VARIANTS)} specific R3 variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
