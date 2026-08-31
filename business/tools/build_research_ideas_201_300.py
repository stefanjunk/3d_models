#!/usr/bin/env python3
"""Build the curated metriMade research batch SKU-201 through SKU-300."""

from __future__ import annotations

import argparse
import csv
import io
import re
from pathlib import Path

from build_product_workbook import RESEARCH_WORKBOOK, read_xlsx_sheet


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "business/02-portfolio/research-ideas-additions-2.csv"
EXISTING_ADDITIONS = REPO_ROOT / "business/02-portfolio/research-ideas-additions.csv"
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
    "SIMPLE": {
        "scores": {"REQ": 1, "CTX": 1, "PAR": 1, "INT": 1, "CPL": 0, "MOT": 0, "GEO": 1, "PHY": 0, "MAT": 1, "EXT": 0, "VER": 1},
        "difficulty": "Easy",
        "am": "A small personalized one-part layout can be generated without stocking many label, count or proportion variants.",
        "prices": ("5-10", "16-34"),
        "drivers": "INT=1 defined item interface; PAR=1 one simple part; REQ=1 few non-conflicting requirements",
    },
    "EXACT_FIT": {
        "scores": {"REQ": 2, "CTX": 2, "PAR": 1, "INT": 2, "CPL": 1, "MOT": 0, "GEO": 1, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "am": "Measured envelope and item dimensions become a one-off exact-fit insert that mass products cannot economically match.",
        "prices": ("8-16", "24-52"),
        "drivers": "INT=2 host and item interfaces; REQ=2 quantitative fit requirements; VER=2 fit and use tests",
    },
    "MODULAR": {
        "scores": {"REQ": 2, "CTX": 1, "PAR": 2, "INT": 2, "CPL": 2, "MOT": 0, "GEO": 1, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Moderate",
        "am": "A small coordinated module family adapts count, spacing and labels to a defined collection while reusing one interface system.",
        "prices": ("9-17", "28-58"),
        "drivers": "INT=2 item and module interfaces; CPL=2 shared module datum; PAR=2 two-to-five printed parts",
    },
    "DISPLAY": {
        "scores": {"REQ": 2, "CTX": 2, "PAR": 1, "INT": 1, "CPL": 1, "MOT": 0, "GEO": 2, "PHY": 1, "MAT": 1, "EXT": 0, "VER": 2},
        "difficulty": "Easy",
        "am": "Object footprint, viewing angle, label and visual motif can be personalized in a compact premium display without tooling.",
        "prices": ("7-15", "22-49"),
        "drivers": "GEO=2 styled visible geometry; REQ=2 display plus personalization requirements; CTX=2 object variation",
    },
}

GROUPS = {
    "small_space": {
        "family": "Small-space dry organization",
        "segment": "Adults in compact homes, rentals and home offices",
        "trend": "IKEA's Germany-inclusive 2026 survey reports catch-all storage in 68% of homes, kitchen counters as the leading clutter point, and strong sentimental retention.",
        "sources": "S31; S32",
        "trend_components": (30, 24, 25),
        "strategy": "Core — exact-fit or defined-set organization for small living and office spaces",
        "inputs": "Available envelope; item list and count; largest item dimensions; access direction; optional label text",
        "variables": "length; width; height; compartment count; divider positions; access cutouts; labels; corner radius",
        "interface": "Measured dry host envelope and the defined light-item set",
        "evidence": "E2 route: customer measurement guide plus scaled overhead photo and one independent control dimension; exact variant remains unknown.",
        "verification": "Dimension check, insertion/removal test, finger-access review, rocking/tip check and surface-mark inspection with inert representative items.",
        "risk": "Dry indoor organization for light personal items only; no secure-storage, structural, electrical, protective or child-use claim.",
        "gate": "Run the measurement workflow on one real envelope, then print the smallest fit corner or divider coupon before a full prototype.",
    },
    "pen_pal": {
        "family": "Pen-pal and correspondence organization",
        "segment": "Adult stationery buyers, journalers and pen-pal communities",
        "trend": "Pinterest Predicts 2026 reports cute stamps +105%, pen-pal ideas +90% and snail-mail gifts +110%; Etsy also reports an analog journaling and keepsake revival.",
        "sources": "S36; S01; S32",
        "trend_components": (28, 27, 24),
        "strategy": "Core — personalized analog-ritual organization with a compact premium desk presence",
        "inputs": "Paper and envelope formats; stamp or card formats; category count; desk footprint; optional names or labels",
        "variables": "slot width; slot count; paper angle; finger relief; label field; base depth; motif",
        "interface": "Defined paper, envelope, stamp or stationery formats and a freestanding desk footprint",
        "evidence": "E2 route: published paper-format nominal dimensions plus customer control measurement for nonstandard stationery.",
        "verification": "Paper-format fit, one-hand access, edge-snag, tip/rocking and label-legibility tests using blank stationery.",
        "risk": "Adult paper and stationery organization only; no postal-accuracy, archival-preservation, fire, security or child-use claim.",
        "gate": "Verify the declared stationery formats with blank samples and print one slot/label coupon before the complete organizer.",
    },
    "poetcore": {
        "family": "Journaling and writing rituals",
        "segment": "Adult journalers, readers, writers and fountain-pen users",
        "trend": "Pinterest Predicts 2026 reports poet aesthetic +175% and poet core +75%; Etsy reports traveler-journal searches doubled and memory journals +189%.",
        "sources": "S36; S01; S32",
        "trend_components": (28, 30, 24),
        "strategy": "Core — personalized functional desk decor for tactile writing and memory rituals",
        "inputs": "Notebook, card or pen envelope; item count; desk footprint; preferred viewing angle; optional text",
        "variables": "slot width; pitch; angle; stop height; label; motif; footprint; divider count",
        "interface": "Defined notebook, card, bookmark or capped-writing-tool envelope",
        "evidence": "E2 route: customer dimension entry with a scaled top photo or a controlled paper/pen preset and one control dimension.",
        "verification": "Fit, removal, scratch/mark, tip stability, edge comfort and label-legibility checks with inert or capped items.",
        "risk": "Adult writing and stationery use only; no ergonomic, archival, instrument-protection, ink-containment or child-use claim.",
        "gate": "Confirm one real item set and print a representative slot/edge coupon before the complete desk object.",
    },
    "needlecraft": {
        "family": "Needlecraft and sewing organization",
        "segment": "Adult sewing, knitting, crochet, embroidery and visible-mending hobbyists",
        "trend": "Michaels reports analog-hobby searches +136%, needlepoint +251%, sewing patterns +152%, yarn-accessory sales +40% and visible mending +144% in 2026.",
        "sources": "S33; S01; S32",
        "trend_components": (25, 30, 25),
        "strategy": "Core — defined-set craft organization with personalized labels and compact storage",
        "inputs": "Tool or material dimensions; count; size labels; storage envelope; project categories; access direction",
        "variables": "slot pitch; bore or channel size; count; divider height; label; module split; footprint",
        "interface": "Defined adult craft-tool or dry-material set and its storage envelope",
        "evidence": "E2 route: measured sample set, scaled photo with control dimension, and manufacturer nominal size where available.",
        "verification": "Fit/removal, snag, edge, label, tip stability and 100-cycle handling test with capped or non-sharp samples.",
        "risk": "Adult dry craft storage only; sharp tools must be removed or capped; no child-use, carry-handle or tool-performance claim.",
        "gate": "Measure one representative set and print the tightest slot or channel coupon before the full organizer.",
    },
    "social_craft": {
        "family": "Social and paper-craft organization",
        "segment": "Adult paper, painting, model-making and group-craft hobbyists",
        "trend": "Michaels reports craft-night searches +103%, girls-night crafts +242%, paint-party kits +329%, guided-kit sales +86% and DIY home decor +79%.",
        "sources": "S33; S01; S32",
        "trend_components": (25, 30, 24),
        "strategy": "Core — compact defined-set organization for social and analog creative routines",
        "inputs": "Material formats; tool envelopes; category and participant count; table footprint; optional labels",
        "variables": "lane width; well size; divider count; module count; access relief; label; footprint",
        "interface": "Defined dry craft materials or capped tools within a freestanding tabletop envelope",
        "evidence": "E2 route: measured material/tool samples plus a scaled layout photo and one control dimension.",
        "verification": "Fit/removal, snag, spill-from-compartment, tip, edge and cleanup checks using inert dry substitutes.",
        "risk": "Adult dry craft organization only; no hot tools, solvents, blades, food, load-bearing, protective or child-use claim.",
        "gate": "Confirm the smallest and largest real formats, then print the densest compartment coupon before a full set.",
    },
    "collecting": {
        "family": "Sentimental display and archive",
        "segment": "Adult collectors, travelers and memory-keeping gift buyers",
        "trend": "Etsy reports wall-art decor +110% and gallery prints +80% for 'Everyday Exhibits'; IKEA finds 82% keep sentimental objects and eBay reports broad hobby reconnection.",
        "sources": "S01; S31; S34; S32",
        "trend_components": (28, 24, 24),
        "strategy": "Core adjacent — personalized functional decor for small sentimental collections",
        "inputs": "Object or card footprint; count; viewing angle; shelf footprint; label text; maximum item mass",
        "variables": "recess size; pitch; angle; stop height; base depth; label; module count; motif",
        "interface": "Defined lightweight collectible footprint and a stable freestanding shelf or desk contact",
        "evidence": "E2 route: scaled orthogonal photo with one control dimension and recorded mass for each allowed object class.",
        "verification": "Fit/removal, contact-mark, tip/rocking, bump and label-legibility checks with inert dummy objects.",
        "risk": "Stable dry display only; no conservation, authentication, security, anti-theft, impact-protection or child-use claim.",
        "gate": "Validate one inert object or card set and print a contact/recess coupon before the complete display.",
    },
    "celebration": {
        "family": "Personalized celebration displays",
        "segment": "Adult gift, milestone, housewarming and small-event buyers",
        "trend": "Michaels reports party decorations +125% and party banners doubled; Etsy reports petit cadeau +277% and strong just-because gifting behavior.",
        "sources": "S33; S01; S32",
        "trend_components": (26, 30, 24),
        "strategy": "Core — useful personalized gifting and compact premium functional decor",
        "inputs": "Card, photo or token size; item count; names/dates; viewing angle; desk or shelf footprint",
        "variables": "slot size; count; angle; label; motif; base proportions; module spacing",
        "interface": "Defined lightweight card, photo or token format and a freestanding display footprint",
        "evidence": "E2 route: standard paper/photo preset or customer control dimension plus approved personalization proof.",
        "verification": "Format fit, tip/rocking, edge, label spelling, visual hierarchy and bump checks with blank media.",
        "risk": "Adult decorative desk or shelf display only; no child-use, structural, secure-storage, memorial-service or protection claim.",
        "gate": "Approve one personalization proof and print a representative slot/text coupon before the complete display.",
    },
    "scent": {
        "family": "Fragrance ritual organization",
        "segment": "Adult fragrance enthusiasts and beauty-collection organizers",
        "trend": "Pinterest Predicts 2026 reports niche-perfume collection +500%, perfume-layering combinations +125%, scent layering +75% and perfume notes +80%.",
        "sources": "S36; S31; S32",
        "trend_components": (28, 30, 23),
        "strategy": "Core adjacent — premium personalized organization for a defined fragrance ritual",
        "inputs": "Card, cap, sealed sleeve or token dimensions; count; category labels; drawer or desk envelope",
        "variables": "slot width; bore; pitch; count; divider height; labels; footprint; viewing angle",
        "interface": "Defined dry cards, caps, labels or sealed sample sleeves and a freestanding/drawer envelope",
        "evidence": "E2 route: measured dry samples or manufacturer nominal envelope plus one independent control dimension.",
        "verification": "Fit/removal, label, edge, tip and surface-mark checks with clean dry or inert samples only.",
        "risk": "Clean dry accessories or sealed cool consumer samples only; no direct formulation contact, leak containment, fire/heat, transport-protection or child-use claim.",
        "gate": "Confirm one clean dry sample set and print the smallest slot/label coupon before the full organizer.",
    },
}


IDEAS = [
    # Small-space and exact-fit organization: SKU-201..220
    ("Exact-fit sofa-side remote and notepad insert", "Fit one measured sofa-console or side-table cubby to separate remotes, a notepad and capped pens.", "small_space", "EXACT_FIT", (210, 150, 85), 13, "New"),
    ("Narrow-bookcase stationery tower insert", "Turn a measured narrow bookcase gap into vertical zones for notebooks, envelopes and capped pens.", "small_space", "EXACT_FIT", (210, 120, 220), 12, "New"),
    ("Desk-pedestal side-gap vertical file", "Use the measured gap beside a desk pedestal for upright folders and current-project papers.", "small_space", "EXACT_FIT", (220, 90, 220), 12, "New"),
    ("Folded-clothing shelf separator pair", "Keep two light folded-clothing stacks distinct on one measured dry wardrobe shelf.", "small_space", "MODULAR", (220, 180, 160), 10, "Variation of SKU-117"),
    ("Sock-pair drawer lane insert", "Create labeled removable lanes for a defined sock collection inside one measured drawer.", "small_space", "EXACT_FIT", (220, 210, 75), 12, "Variation of SKU-001"),
    ("Necktie-roll drawer matrix", "Store a measured set of rolled neckties in visible labeled cells without stacking.", "small_space", "EXACT_FIT", (220, 210, 85), 12, "New"),
    ("Hair-accessory drawer channel set", "Separate adult scrunchies, barrettes and cool hair accessories in a measured vanity drawer.", "small_space", "MODULAR", (220, 180, 65), 11, "Variation of SKU-010"),
    ("Handbag dust-bag shelf label corral", "Keep folded empty dust bags upright and labeled beside their handbags on a dry shelf.", "small_space", "EXACT_FIT", (200, 140, 160), 12, "New"),
    ("Bedside glasses-and-earplug valet", "Give glasses, their case and packaged earplugs fixed places on a compact bedside surface.", "small_space", "SIMPLE", (170, 120, 45), 9, "New"),
    ("Paper-size drawer stair organizer", "Separate A4-folded, A5, A6 and note-card stock by visible stepped height in one drawer.", "small_space", "EXACT_FIT", (220, 210, 80), 12, "New"),
    ("Weekly coin-and-receipt purge tray", "Split pocket change, receipts and action slips into a small tray designed for a weekly clear-out ritual.", "small_space", "SIMPLE", (180, 120, 35), 11, "Variation of SKU-173"),
    ("Reusable-shopping-bag shelf file", "Hold folded reusable shopping bags upright by size in a measured cabinet or shelf cubby.", "small_space", "EXACT_FIT", (210, 150, 180), 12, "New"),
    ("Garment-repair kit drawer cassette", "Keep spare buttons, thread cards and capped repair notions visible in one removable drawer cassette.", "small_space", "MODULAR", (200, 150, 45), 11, "New"),
    ("Laundry pocket-find sorting tray", "Create temporary labeled zones for dry coins, notes and small objects removed before washing.", "small_space", "SIMPLE", (180, 110, 35), 10, "New"),
    ("Seasonal-accessory drawer divider set", "Reconfigure one drawer between light scarves, gloves and summer accessories using labeled dividers.", "small_space", "MODULAR", (220, 210, 100), 11, "New platform variant"),
    ("Travel-document pre-trip staging tray", "Stage passports, blank forms and itinerary cards together before adult travel without claiming secure storage.", "small_space", "SIMPLE", (200, 140, 32), 10, "New"),
    ("Household spare-key labeled cassette", "Separate identified spare keys in a drawer cassette without presenting it as secure key storage.", "small_space", "MODULAR", (180, 120, 32), 10, "New"),
    ("Warranty-and-manual mini file", "Sort current small manuals, receipts and warranty cards by room or device in a compact dry file.", "small_space", "MODULAR", (220, 150, 180), 11, "New"),
    ("Ribbon-offcut and gift-tag drawer file", "Separate reusable dry ribbon offcuts, blank tags and string cards inside one craft drawer.", "small_space", "EXACT_FIT", (210, 160, 65), 11, "New"),
    ("Sentimental-object rotation tray", "Store a small defined set of keepsakes in labeled cells while one selected object is displayed elsewhere.", "small_space", "MODULAR", (200, 160, 45), 13, "Variation of SKU-179"),

    # Pen-pal and correspondence: SKU-221..230
    ("Correspondence desk station", "Combine envelopes, writing paper, stamps and capped pens in one personalized freestanding writing station.", "pen_pal", "MODULAR", (210, 150, 120), 13, "New"),
    ("Incoming-reply-archive letter sorter", "Separate letters awaiting reply, active correspondence and completed keepsakes in three visible slots.", "pen_pal", "MODULAR", (220, 140, 170), 12, "New"),
    ("Postage-stamp sheet flat tray", "Keep defined stamp-sheet and booklet formats flat, visible and removable on a writing desk.", "pen_pal", "EXACT_FIT", (190, 140, 28), 11, "New"),
    ("Stamp-booklet pocket dispenser", "Present a measured stack of stamp booklets with one-hand finger access and a refill indicator.", "pen_pal", "EXACT_FIT", (110, 80, 42), 12, "New"),
    ("Envelope-size vertical file", "Separate a chosen set of envelope formats in a compact personalized vertical desk file.", "pen_pal", "MODULAR", (220, 110, 150), 12, "New"),
    ("Address-label and sticker-roll dock", "Park non-adhesive-backed label rolls and sticker sheets beside a correspondence station.", "pen_pal", "MODULAR", (180, 120, 90), 11, "New"),
    ("Wax-seal stamp cool-storage stand", "Store clean, cool wax-seal stamp handles upright by motif when they are not in use.", "pen_pal", "EXACT_FIT", (160, 90, 80), 10, "New"),
    ("Pen-pal gift-enclosure sorting tray", "Stage flat stickers, blank cards and lightweight enclosures by recipient before packing a letter.", "pen_pal", "MODULAR", (200, 150, 35), 12, "New"),
    ("Postcard-writing angle stand", "Hold one postcard at a chosen low writing/viewing angle with a separate capped-pen rest.", "pen_pal", "DISPLAY", (180, 120, 90), 10, "New"),
    ("Snail-mail outgoing date queue", "Arrange completed letters by planned posting date using removable personalized dividers.", "pen_pal", "MODULAR", (220, 120, 150), 13, "New"),

    # Journaling and poetcore: SKU-231..240
    ("Fountain-pen and notebook desk bridge", "Keep one closed notebook and a small set of capped pens together in a sculptural desk bridge.", "poetcore", "DISPLAY", (200, 120, 95), 12, "New"),
    ("Reading-log card catalog file", "Store reading-log cards by status in a compact open file inspired by a card catalog.", "poetcore", "MODULAR", (180, 130, 100), 11, "New"),
    ("Quote-card archive stand", "Organize handwritten quote and prompt cards by theme in a personalized stepped stand.", "poetcore", "MODULAR", (170, 110, 95), 11, "New"),
    ("Bookmark rotation stand", "Display current bookmarks while storing a small rotation set upright without bending them.", "poetcore", "DISPLAY", (150, 90, 140), 10, "New"),
    ("Journal-sticker sheet vertical file", "Separate sticker sheets and flat ephemera by journal project in a compact vertical file.", "poetcore", "EXACT_FIT", (200, 100, 160), 12, "New"),
    ("Traveler-notebook template station", "Keep writing guides, blotting cards and insert templates aligned beside a traveler notebook.", "poetcore", "EXACT_FIT", (180, 120, 55), 12, "Variation of SKU-026"),
    ("Paper-ephemera sorting fan", "Sort tickets, labels and paper ephemera into visible angled lanes before journaling.", "poetcore", "MODULAR", (190, 130, 90), 11, "New"),
    ("Daily-writing prompt token tray", "Present a personalized set of adult writing-prompt tokens in today, used and archive zones.", "poetcore", "MODULAR", (160, 110, 38), 12, "New"),
    ("Ink-swatch card stepped rail", "Display dry fountain-pen ink swatch cards by color family in a labeled stepped rail.", "poetcore", "DISPLAY", (200, 90, 95), 11, "New"),
    ("Notebook-band and charm staging tray", "Keep removable notebook bands and adult journal charms organized while they are off the notebook.", "poetcore", "MODULAR", (170, 120, 32), 11, "Variation of SKU-043"),

    # Needlecraft and sewing: SKU-241..255
    ("Sewing-pattern envelope size sorter", "Separate active sewing-pattern envelopes by project and format in a compact shelf file.", "needlecraft", "MODULAR", (220, 150, 190), 13, "New"),
    ("Fabric-swatch card index", "Organize labeled fabric swatch cards by project, fiber or color in removable sections.", "needlecraft", "MODULAR", (190, 130, 110), 13, "New"),
    ("Visible-mending patch palette tray", "Stage dry repair patches and thread cards by garment before a visible-mending session.", "needlecraft", "MODULAR", (190, 140, 32), 12, "New"),
    ("Darning-mushroom and thread stand", "Store one darning mushroom, capped needle tube and current thread cards together between sessions.", "needlecraft", "EXACT_FIT", (160, 120, 100), 11, "New"),
    ("Thimble-and-notions drawer micro-grid", "Create labeled cells for adult thimbles, clips and closed notions in one measured craft drawer.", "needlecraft", "EXACT_FIT", (200, 160, 42), 12, "New"),
    ("Needlepoint-canvas roll end cradles", "Support both ends of a rolled dry needlepoint canvas horizontally on a shelf between sessions.", "needlecraft", "MODULAR", (220, 120, 80), 10, "New"),
    ("Embroidery-hoop size nesting stand", "Store a measured set of empty embroidery hoops upright and labeled by diameter.", "needlecraft", "EXACT_FIT", (220, 140, 180), 12, "New"),
    ("Punch-needle tool rest", "Park clean, capped punch-needle tools and current thread cards in a compact adult craft stand.", "needlecraft", "EXACT_FIT", (150, 100, 85), 10, "New"),
    ("Quilt-block layout label token tray", "Sort reusable row, column and orientation labels used while arranging quilt blocks.", "needlecraft", "MODULAR", (170, 110, 32), 11, "New"),
    ("Quilting-template vertical file", "Separate measured acrylic or card quilting templates upright by shape and project.", "needlecraft", "EXACT_FIT", (220, 120, 180), 11, "New"),
    ("Circular-knitting cable size cassette", "Store disconnected circular-knitting cables in labeled loose coils without sharp needle tips.", "needlecraft", "MODULAR", (210, 160, 42), 12, "New"),
    ("Knitting-needle pair divider modules", "Keep capped straight knitting-needle pairs separated by size in modular horizontal channels.", "needlecraft", "MODULAR", (220, 160, 85), 12, "New"),
    ("Crochet-gauge swatch archive rack", "Store labeled dry crochet gauge swatches upright for later project reference.", "needlecraft", "MODULAR", (200, 130, 140), 12, "New"),
    ("Yarn-label archive card file", "Keep removed yarn labels and matching sample cards organized by project and fiber.", "needlecraft", "MODULAR", (180, 120, 100), 12, "New"),
    ("Portable craft-project container insert", "Fit one customer-owned box with removable zones for a current small needlecraft project without acting as its handle.", "needlecraft", "EXACT_FIT", (220, 180, 70), 13, "Variation of SKU-151"),

    # Social, paper and model craft: SKU-256..270
    ("Paper-quilling strip color divider", "Keep dry quilling strips separated by color and length in a measured drawer or box insert.", "social_craft", "EXACT_FIT", (220, 170, 55), 12, "New"),
    ("Origami-paper size step sorter", "Separate square paper formats by visible stepped height without bending the sheets.", "social_craft", "MODULAR", (220, 220, 65), 12, "New"),
    ("Polymer-clay cutter silhouette index tray", "Arrange clean dry adult craft cutters by outline so missing shapes are visible before use.", "social_craft", "EXACT_FIT", (220, 180, 38), 13, "New"),
    ("Jewelry-wire spool label comb", "Separate small dry craft-wire spools by gauge in a freestanding labeled comb.", "social_craft", "EXACT_FIT", (200, 120, 100), 11, "New"),
    ("Charm-bar component sorting palette", "Stage adult craft charms and connectors by project in removable personalized wells.", "social_craft", "MODULAR", (190, 140, 28), 13, "New"),
    ("Friendship-bracelet thread project tray", "Separate pre-cut thread groups, labels and finished adult craft samples for one bracelet project.", "social_craft", "MODULAR", (200, 140, 32), 12, "New"),
    ("Scrapbook die-cut sorting fan", "Sort dry paper die-cuts by theme in visible angled lanes before assembly.", "social_craft", "MODULAR", (190, 130, 100), 12, "New"),
    ("Washi sample-card index base", "Display dry washi sample cards by palette and project without dispensing tape.", "social_craft", "DISPLAY", (180, 100, 95), 11, "Variation of SKU-146"),
    ("Rubber-stamp impression card file", "Archive dry stamped sample cards by theme so adult users can select a stamp without unpacking it.", "social_craft", "MODULAR", (180, 120, 110), 11, "Variation of SKU-158"),
    ("Paint-party brush-and-name station", "Assign clean dry capped brushes and name cards to adult participants before a paint session.", "social_craft", "MODULAR", (200, 130, 75), 13, "New"),
    ("Craft-night personal boundary tray", "Give each adult participant a named shallow dry-parts zone on a shared table.", "social_craft", "SIMPLE", (180, 130, 24), 12, "Variation of SKU-160"),
    ("Mosaic-tessera color staging grid", "Stage small inert adult mosaic pieces by color in removable shallow cells before placement.", "social_craft", "MODULAR", (190, 150, 25), 12, "New"),
    ("Miniature-basing sample archive", "Store sealed dry basing-material sample bags and labeled result cards by project.", "social_craft", "MODULAR", (190, 140, 80), 10, "New"),
    ("Model-decal sheet flat file", "Separate unused dry decal sheets and instruction cards by model project without folding.", "social_craft", "EXACT_FIT", (220, 170, 32), 11, "New"),
    ("Pressed-flower dry sorting frame insert", "Arrange fully dried pressed-flower pieces by size inside a customer-owned flat frame or box before composition.", "social_craft", "EXACT_FIT", (220, 180, 25), 12, "New"),

    # Sentimental collections and everyday exhibits: SKU-271..285
    ("Ticket-stub chronological desk archive", "Store dry ticket stubs upright by year or event in a personalized compact archive.", "collecting", "MODULAR", (190, 130, 110), 13, "New"),
    ("Concert-wristband memory spool", "Display cleaned dry fabric event wristbands on a removable labeled spool without claiming preservation.", "collecting", "DISPLAY", (150, 100, 120), 12, "New"),
    ("Photo-booth strip vertical display", "Present one or more standard or measured photo-booth strips in a stable personalized desk display.", "collecting", "DISPLAY", (150, 90, 160), 12, "New"),
    ("Event-lanyard badge archive rack", "Store lightweight inactive event badges and lanyards on a freestanding shelf rack by year.", "collecting", "MODULAR", (210, 140, 190), 12, "New"),
    ("Souvenir-token story tray", "Arrange a small measured set of travel tokens beside short story labels in a shallow display tray.", "collecting", "DISPLAY", (200, 150, 32), 13, "New"),
    ("Keychain-collection freestanding rail", "Display a light adult keychain collection on a freestanding low rail with personalized category labels.", "collecting", "MODULAR", (210, 100, 150), 11, "New"),
    ("Empty-matchbook-cover archive file", "Store empty paper matchbook covers only in measured dry divider lanes for adult collectors.", "collecting", "MODULAR", (180, 120, 95), 11, "New"),
    ("Transit-ticket route divider box", "Sort expired dry transit tickets by city or route in a personalized compact file.", "collecting", "MODULAR", (180, 120, 100), 12, "New"),
    ("Travel-patch presentation tile", "Present unattached dry travel patches on a freestanding textured tile without adhesive or wall mounting.", "collecting", "DISPLAY", (180, 120, 95), 11, "New"),
    ("Brooch drawer-card cassette", "Separate adult brooches on customer-provided cards inside a measured drawer cassette.", "collecting", "EXACT_FIT", (200, 150, 42), 13, "New"),
    ("Lapel-pin outfit-selection stand", "Stage a small adult lapel-pin selection on customer-provided cards beside a wardrobe without garment attachment.", "collecting", "DISPLAY", (160, 100, 130), 11, "New"),
    ("Heirloom-jewelry story-card plinth", "Display one lightweight jewelry item on its customer-provided card beside a personalized provenance note.", "collecting", "DISPLAY", (160, 110, 90), 12, "New"),
    ("Souvenir-magnet tabletop display board", "Display a small lightweight magnet collection on a customer-provided steel card in a freestanding frame.", "collecting", "DISPLAY", (190, 120, 150), 12, "New"),
    ("Today's-memory postcard stand", "Show one selected postcard while storing a short rotation set behind it in a personalized desk stand.", "collecting", "DISPLAY", (180, 100, 140), 12, "Variation of SKU-112"),
    ("Collectible certificate-and-object plinth", "Pair one lightweight object with its non-secure certificate card in a fitted shelf display.", "collecting", "DISPLAY", (200, 140, 110), 13, "New"),

    # Personalized gifting and celebration: SKU-286..295
    ("Little-wins token staircase", "Display personalized tokens for small completed goals in a compact stepped desk object.", "celebration", "DISPLAY", (170, 100, 100), 13, "New"),
    ("Congratulations card-and-photo dock", "Pair one greeting card and one photo in a personalized freestanding milestone display.", "celebration", "DISPLAY", (180, 110, 120), 12, "New"),
    ("Anniversary year-ring keepsake stand", "Arrange removable year tokens around one lightweight keepsake in a personalized shelf stand.", "celebration", "DISPLAY", (180, 140, 80), 13, "New"),
    ("New-home paint-chip and key memory plinth", "Display one inactive spare key and selected dry paint-color cards as a housewarming keepsake.", "celebration", "DISPLAY", (170, 110, 100), 12, "New"),
    ("Retirement message-card fan stand", "Present a measured set of colleague message cards in a personalized freestanding fan layout.", "celebration", "MODULAR", (210, 130, 130), 13, "New"),
    ("Graduation tassel-and-card plinth", "Display one dry tassel and a graduation card on a stable personalized shelf plinth.", "celebration", "DISPLAY", (180, 120, 120), 12, "New"),
    ("Craft-night name-and-tool pod", "Assign each adult guest a personalized pod for clean capped tools and a name card.", "celebration", "MODULAR", (160, 110, 70), 13, "Variation of SKU-160"),
    ("Birthday-month token row", "Display removable named birthday tokens by month as a compact freestanding household reminder.", "celebration", "MODULAR", (220, 90, 75), 12, "New"),
    ("Friendship-memory note capsule stand", "Hold customer-provided closed paper-note capsules in a personalized adult desk display.", "celebration", "DISPLAY", (170, 120, 90), 11, "New"),
    ("Hobby-milestone badge display", "Present earned adult hobby badges or tokens by date in a personalized freestanding display.", "celebration", "DISPLAY", (190, 110, 130), 13, "New"),

    # Fragrance ritual without direct formulation contact: SKU-296..300
    ("Fragrance-note card index stand", "Organize dry fragrance-note and preference cards by family in a premium labeled desk stand.", "scent", "MODULAR", (180, 110, 110), 12, "New"),
    ("Scent-layering recipe card file", "Store customer-written dry layering recipe cards by season or occasion without holding fragrance containers.", "scent", "MODULAR", (180, 120, 100), 13, "New"),
    ("Sealed perfume-sample sleeve sorter", "Separate manufacturer-sealed cool sample sleeves by fragrance family in a measured drawer insert.", "scent", "EXACT_FIT", (200, 150, 42), 12, "New"),
    ("Perfume-cap display tray", "Arrange clean dry removable perfume caps only by bottle or fragrance family in fitted shallow recesses.", "scent", "EXACT_FIT", (190, 140, 32), 11, "New"),
    ("Daily scent-selection token rail", "Use personalized dry tokens to plan a daily fragrance rotation without contacting bottles or formulations.", "scent", "DISPLAY", (180, 90, 85), 13, "New"),
]


FIELDNAMES = [
    "SKU_ID", "Product", "Product_Family", "Concept_Type", "Purpose", "Customer_Job", "Target_Segment",
    "Trend_Signal", "Strategy_Fit", "AM_Advantage", "Customer_Inputs", "Parametric_Variables",
    "Max_L_mm", "Max_W_mm", "Max_H_mm", "Primary_Material", "Supports", "Difficulty", "Offer_Mode",
    "Digital_Price_Band_EUR", "Printed_Price_Band_EUR", "Risk_Score", "Risk_or_Limit", "Opportunity_Score",
    "Launch_Wave", "Source_IDs", "Design_Status", "Next_Gate", "Notes",
    "Trend_Source_Strength_0_30", "Trend_Signal_Magnitude_0_30", "Trend_MetriMade_Fit_0_25",
    "Trend_Whitespace_0_15", "Trend_Score_0_100", "Trend_Score_Basis", "Trend_Score_Status",
    "Preflight_Archetype", "Critical_Interface", "Evidence_Route", "Manufacturing_Baseline", "Verification_Plan",
    "REQ", "CTX", "PAR", "INT", "CPL", "MOT", "GEO", "PHY", "MAT", "EXT", "VER", "PC_0_100",
    "Complexity", "R_Scope", "R_Requirements", "R_Critical_Interfaces", "R_Manufacturing_Profile",
    "R_Verification", "Readiness", "Readiness_Basis", "Criticality", "Current_Lane",
    "Target_Lane_After_Evidence", "Confidence", "Design_Release", "Hard_Gates", "Preflight_Short",
    "Preflight_Status", "Assessed_On", "Assessment_Version",
]


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def pc_score(scores: dict[str, int]) -> float:
    return round(sum(WEIGHTS[key] * scores[key] / 4 for key in WEIGHTS), 2)


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


def existing_product_names() -> set[str]:
    legacy = read_xlsx_sheet(RESEARCH_WORKBOOK, "Product Matrix")
    product_index = legacy[0].index("Product")
    names = {normalized(str(row[product_index])) for row in legacy[1:]}
    with EXISTING_ADDITIONS.open(newline="", encoding="utf-8") as handle:
        names.update(normalized(row["Product"]) for row in csv.DictReader(handle))
    return names


def build_rows() -> list[dict[str, object]]:
    if len(IDEAS) != 100:
        raise ValueError(f"Expected 100 curated ideas, found {len(IDEAS)}")
    old_names = existing_product_names()
    new_names = [normalized(item[0]) for item in IDEAS]
    if len(new_names) != len(set(new_names)):
        raise ValueError("Curated batch contains a duplicate normalized product name")
    collisions = sorted(set(new_names).intersection(old_names))
    if collisions:
        raise ValueError(f"Curated batch duplicates existing product names: {', '.join(collisions)}")

    rows: list[dict[str, object]] = []
    for number, (product, job, group_key, archetype_key, dimensions, whitespace, concept_type) in enumerate(IDEAS, start=201):
        group = GROUPS[group_key]
        archetype = ARCHETYPES[archetype_key]
        source_strength, signal_magnitude, strategy_fit = group["trend_components"]
        trend_score = source_strength + signal_magnitude + strategy_fit + whitespace
        scores = archetype["scores"]
        pc = pc_score(scores)
        complexity = complexity_class(pc)
        if trend_score <= 70 or complexity not in {"C0", "C1", "C2"}:
            raise ValueError(f"Strict trend/complexity gate failed for SKU-{number:03d}")
        digital_price, printed_price = archetype["prices"]
        rows.append(
            {
                "SKU_ID": f"SKU-{number:03d}",
                "Product": product,
                "Product_Family": group["family"],
                "Concept_Type": concept_type,
                "Purpose": job,
                "Customer_Job": job,
                "Target_Segment": group["segment"],
                "Trend_Signal": group["trend"],
                "Strategy_Fit": group["strategy"],
                "AM_Advantage": archetype["am"],
                "Customer_Inputs": group["inputs"],
                "Parametric_Variables": group["variables"],
                "Max_L_mm": dimensions[0],
                "Max_W_mm": dimensions[1],
                "Max_H_mm": dimensions[2],
                "Primary_Material": "PLA or PETG",
                "Supports": "None",
                "Difficulty": archetype["difficulty"],
                "Offer_Mode": "Digital first; printed after fulfillment qualification",
                "Digital_Price_Band_EUR": digital_price,
                "Printed_Price_Band_EUR": printed_price,
                "Risk_Score": 1,
                "Risk_or_Limit": group["risk"],
                "Opportunity_Score": min(99, trend_score + 2),
                "Launch_Wave": "Research batch 3",
                "Source_IDs": group["sources"],
                "Design_Status": "P0 research backlog",
                "Next_Gate": group["gate"],
                "Notes": "metriMade candidate only; trend, price and demand remain hypotheses until German marketplace and customer validation.",
                "Trend_Source_Strength_0_30": source_strength,
                "Trend_Signal_Magnitude_0_30": signal_magnitude,
                "Trend_MetriMade_Fit_0_25": strategy_fit,
                "Trend_Whitespace_0_15": whitespace,
                "Trend_Score_0_100": trend_score,
                "Trend_Score_Basis": "Primary-source strength + signal magnitude + metriMade strategy fit + nonduplicate portfolio whitespace; components are directional planning judgments.",
                "Trend_Score_Status": "DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND",
                "Preflight_Archetype": archetype_key,
                "Critical_Interface": group["interface"],
                "Evidence_Route": group["evidence"],
                "Manufacturing_Baseline": "Candidate baseline: common 220 x 220 x 250 mm FFF envelope, PLA or PETG, support-free orientation; exact printer, filament product/color/batch, nozzle and process JSON remain UNKNOWN.",
                "Verification_Plan": group["verification"],
                **scores,
                "PC_0_100": pc,
                "Complexity": complexity,
                "R_Scope": "R2",
                "R_Requirements": "R2",
                "R_Critical_Interfaces": "R2",
                "R_Manufacturing_Profile": "R2",
                "R_Verification": "R2",
                "Readiness": "R2",
                "Readiness_Basis": "Purpose, exclusions, envelope, measurable inputs, critical-interface route, candidate process envelope and test method are specified; exact customer variant and complete process evidence remain open.",
                "Criticality": "K1",
                "Current_Lane": "E",
                "Target_Lane_After_Evidence": "B",
                "Confidence": "LOW_UNKNOWN",
                "Design_Release": "CONCEPT_ONLY",
                "Hard_Gates": "G0 PASS; G1 PASS; G2 WARN; G3 FAIL; G4 PASS; G5 PASS; G6 PASS",
                "Preflight_Short": f"{complexity} · R2 · K1 · Lane E · LOW_UNKNOWN",
                "Preflight_Status": "STRUCTURED RESEARCH PREFLIGHT R2 — NOT PRODUCT RELEASE APPROVAL",
                "Assessed_On": ASSESSED_ON,
                "Assessment_Version": ASSESSMENT_VERSION,
            }
        )
    return rows


def render(rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the generated CSV is missing or stale.")
    args = parser.parse_args()
    content = render(build_rows())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale or missing generated research batch: {OUTPUT}")
        print(f"PASS: {OUTPUT} is current with 100 curated ideas")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} with 100 curated ideas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
