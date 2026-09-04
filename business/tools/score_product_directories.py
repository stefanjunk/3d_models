#!/usr/bin/env python3
"""Score every product directory on the shared research market/priority scale.

The 314 research ideas already carry `Trend_Score_0_100`, `Priority_Score_0_100`,
`Opportunity_Score_0_100`, `Risk_Score_1_5` and the ten 1-5 planning components.
Product directories did not, so the leading `Portfolio` worksheet could not be
sorted or filtered on one column across both record types.

This builder closes that gap without inventing product-specific demand evidence:

* A product mapped to a research idea inherits that idea's recorded scores.
* Every other product is scored from its own documented repository evidence:
  the live preflight scorecard and complexity dimensions, the product-register
  strategy fit, rights/provenance state, safety-risk note and model status, and
  the directional trend of the research family its category belongs to.

Every row keeps a readable basis, a rationale and an explicit status string. The
result is a directional planning order, not validated demand, margin, safety or
release approval.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import statistics
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_DIR = REPO_ROOT / "business/02-portfolio"
PORTFOLIO_CSV = PORTFOLIO_DIR / "product-portfolio.csv"
PRIORITY_CSV = PORTFOLIO_DIR / "research-idea-priority.csv"
PRODUCTS_ROOT = REPO_ROOT / "products"
OUTPUT = PORTFOLIO_DIR / "product-directory-scoring.csv"

SCORED_ON = "2026-09-04"
SCORING_VERSION = "1.0"
SCORE_STATUS = "DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND OR RELEASE APPROVAL"

FIELDS = [
    "Product_Path",
    "Working_SKU",
    "Product",
    "Product_Family_or_Category",
    "Score_Basis",
    "Trend_Score_0_100",
    "Priority_Score_0_100",
    "Opportunity_Score_0_100",
    "Risk_Score_1_5",
    "Estimated_Market_Fit_1_5",
    "Market_Evidence_Confidence_1_5",
    "Creation_Effort_1_5",
    "Validation_Effort_1_5",
    "Commercial_Risk_1_5",
    "Strategy_Fit_1_5",
    "AM_Differentiation_1_5",
    "Portfolio_Leverage_1_5",
    "Digital_First_Fit_1_5",
    "Economics_1_5",
    "Trend_Basis",
    "Scoring_Rationale",
    "Score_Status",
    "Scored_On",
    "Scoring_Version",
]

COMPONENT_FIELDS = [
    "Estimated_Market_Fit_1_5",
    "Market_Evidence_Confidence_1_5",
    "Creation_Effort_1_5",
    "Validation_Effort_1_5",
    "Commercial_Risk_1_5",
    "Strategy_Fit_1_5",
    "AM_Differentiation_1_5",
    "Portfolio_Leverage_1_5",
    "Digital_First_Fit_1_5",
    "Economics_1_5",
]

# Product-register category -> research family whose recorded trend evidence covers
# the same customer job. `None` means no primary-source research family exists for
# that category, so the no-evidence baseline applies instead of a borrowed signal.
CATEGORY_TREND_FAMILY: dict[str, str | None] = {
    # Named host-furniture systems are covered by the Germany-inclusive IKEA storage survey.
    "System-furniture insert": "Named-system furniture organization",
    "System-furniture storage": "Named-system furniture organization",
    "System-furniture organizer": "Named-system furniture organization",
    "System-furniture dock": "Named-system furniture organization",
    "System-furniture display": "Collectible display and storage",
    "System-furniture shelf accessory": "Exact-fit shelf organization",
    "System-furniture tool storage": "Workshop tool organization",
    "System-furniture media accessory": "Physical-media organization",
    "System-furniture rail": "Modular pegboard & wall-storage ecosystems",
    "System-furniture cable accessory": "Cable-management systems",
    # A generative appearance shell does not change the customer job: SKU-331 cites the
    # cable-management family directly as its verified trend source, so it maps there.
    "Generative desk cable organization": "Cable-management systems",
    # Dry organization and exact-fit storage.
    "Exact-fit storage": "Exact-fit shelf organization",
    "Desk organizer": "Custom desk & drawer organizers",
    "Wall storage": "Modular pegboard & wall-storage ecosystems",
    "Integrated bathroom storage": "Bathroom & shower organizers",
    "Bathroom storage": "Bathroom & shower organizers",
    "Shower-drain accessory": "Bathroom & shower organizers",
    "Shower-drain accessory concept": "Bathroom & shower organizers",
    # Wall relief has its own recorded research family; a generic decorative mesh does not.
    "Decorative wall relief": "3D wall art, reliefs & gallery panels",
    "Decorative topographic wall relief": "3D wall art, reliefs & gallery panels",
    "Decorative tray": "Vases & sculptural containers",
    "Decorative mesh": None,
    "Decorative/vehicle mesh": None,
    "Decorative surface": None,
    "Decorative object": None,
    "Vehicle-themed model": None,
    # Printer and workshop work is covered, and its recorded trend is deliberately low.
    "Printer accessory": "3D-printer workshop organization",
    "Printer camera mount": "3D-printer workshop organization",
    "Printer printhead cover": "3D-printer workshop organization",
    "Printer purge-waste bin": "3D-printer workshop organization",
    "Printer purge-waste diverter": "3D-printer workshop organization",
    "Maker storage": "Workshop tool organization",
    "Tool-shaped model": None,
    "Desktop mechanism concept": None,
    # Hobby and gift objects.
    "Hobby accessory": "Board-game inserts, card holders & dice towers",
    "Puzzle container": "Adult desk fidgets & original collectibles",
    "Personalized container": "Sentimental display and archive",
    # No primary-source research family: powered toys, RC/FPV vehicles, wearables, wet systems.
    "Toy/decor boat": None,
    "Toy/decor boat concept": None,
    "Powered toy boat": None,
    "Projectile toy": None,
    "Hybrid five-inch FPV quadcopter": None,
    "Tethered three-thruster mini ROV": None,
    "Low-speed FPV RC camera-rover payload system": None,
    "Low-speed self-balancing FPV camera rover": None,
    "Wearable accessory": None,
    "Footwear": None,
    "Garden water system": None,
    "Food-contact household item": None,
    "Aroma-diffuser concept": None,
    # Built timber furniture cut by a panel service. Every research trend family in
    # this repository surveys 3D-printed products, so none of them is a truthful
    # comparator for a cut-list cabinet. Reviewed decision: no research family.
    "Solid-wood corner cabinet, cut-list furniture": None,
}

# No research family cites a primary source for the category, so the product starts
# below every scored research family (the lowest recorded family median is 51.5).
NO_FAMILY_TREND_BASELINE = 35

# Approximates re-scoring the documented 0-25 metriMade-fit trend component for a
# product whose register strategy fit differs from an on-strategy research idea.
STRATEGY_TREND_ADJUSTMENT = {5: 0, 4: -3, 3: -8, 1: -18}

STRATEGY_FIT_SCORE = {"core adjacent": 4, "core": 5, "adjacent": 3, "off-strategy": 1}

CRITICALITY_VALIDATION_EFFORT = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
CRITICALITY_RISK = {0: 1, 1: 2, 2: 4, 3: 5, 4: 5}
COMPLEXITY_CREATION_EFFORT = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
COMPLEXITY_ECONOMICS = {0: 4, 1: 4, 2: 4, 3: 3, 4: 2, 5: 1}

AM_KEYWORDS = ("exact-fit", "exact named", "measurement", "named-", "defined-set", "personalized", "modular")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def product_dirs() -> list[Path]:
    """Return every live products/<family>/<product> directory."""
    return sorted(
        product
        for family in PRODUCTS_ROOT.iterdir()
        if family.is_dir()
        for product in family.iterdir()
        if product.is_dir() and product.name.startswith(("mm-", "unregistered-"))
    )


def band(value: str, prefix: str) -> int:
    matches = [int(match) for match in re.findall(rf"{prefix}([0-5])", value or "")]
    return max(matches) if matches else 0


def clamp(value: float, low: int = 1, high: int = 5) -> int:
    return int(max(low, min(high, round(value))))


def inverse_component(score: int, weight: float) -> float:
    return ((5 - score) / 4) * weight


def priority_score(scores: dict[str, int]) -> float:
    """Reuse the documented research priority weights without modification."""
    total = (
        scores["Estimated_Market_Fit_1_5"] / 5 * 20
        + scores["Strategy_Fit_1_5"] / 5 * 15
        + scores["AM_Differentiation_1_5"] / 5 * 10
        + scores["Portfolio_Leverage_1_5"] / 5 * 15
        + scores["Digital_First_Fit_1_5"] / 5 * 5
        + scores["Economics_1_5"] / 5 * 5
        + scores["Market_Evidence_Confidence_1_5"] / 5 * 5
        + inverse_component(scores["Creation_Effort_1_5"], 8)
        + inverse_component(scores["Validation_Effort_1_5"], 8)
        + inverse_component(scores["Commercial_Risk_1_5"], 9)
    )
    return round(total, 1)


def family_trend_medians() -> dict[str, float]:
    medians: dict[str, list[float]] = {}
    for row in read_csv(PRIORITY_CSV):
        if row["Trend_Score_0_100"]:
            medians.setdefault(row["Product_Family"], []).append(float(row["Trend_Score_0_100"]))
    return {family: statistics.median(values) for family, values in medians.items()}


def strategy_tier(strategy_fit: str) -> int:
    text = (strategy_fit or "").strip().lower()
    for prefix in ("core adjacent", "core", "adjacent", "off-strategy"):
        if text.startswith(prefix):
            return STRATEGY_FIT_SCORE[prefix]
    return 3


def market_fit_from_trend(trend: int) -> int:
    for threshold, score in ((90, 5), (80, 4), (65, 3), (45, 2)):
        if trend >= threshold:
            return score
    return 1


def rights_risk(rights: str) -> tuple[int, str]:
    text = (rights or "").strip()
    upper = text.upper()
    if upper.startswith("BLOCK"):
        return 5, "rights BLOCK"
    if upper.startswith("UNKNOWN"):
        return 4, "rights UNKNOWN"
    if "recorded" in text or "declares" in text or "are CC BY" in text:
        return 2, "rights partly recorded"
    if text.startswith("Local"):
        return 3, "local source, commercial register open"
    return 4, "rights not documented"


def safety_risk(safety: str) -> tuple[int, str]:
    text = (safety or "").strip().lower()
    if text.startswith("very high"):
        return 5, "safety very high"
    if "high" in text and "medium to high" not in text and not text.startswith("low"):
        return 4, "safety high"
    if "medium to high" in text:
        return 4, "safety medium to high"
    if text.startswith("unknown"):
        return 4, "safety unknown"
    if "portfolio risk 1/5" in text or "portfolio risk 2/5" in text:
        return 2, "portfolio safety screen 1-2/5"
    if text.startswith("low to medium") or text.startswith("low"):
        return 2, "safety low"
    if "medium" in text or text.startswith("k2"):
        return 3, "safety medium"
    return 3, "safety not graded"


def derive_scores(
    product: dict[str, str],
    preflight: dict[str, object],
    family_size: int,
    medians: dict[str, float],
) -> tuple[dict[str, int], int, str, str]:
    """Return the ten components, the trend score, its basis and a rationale."""
    complexity = preflight["complexity"]
    dimensions: dict[str, int] = {key: int(value) for key, value in complexity["dimension_scores"].items()}
    c = band(str(complexity["class"]), "C")
    r = band(str(preflight["readiness"]["level"]), "R")
    k = band(str(preflight["criticality"]["level"]), "K")

    category = product["Category"]
    tier = strategy_tier(product["Strategy_Fit"])
    model_status = product["Model_Status"]
    controlled_source = model_status.startswith("YES — controlled")
    no_model = model_status.startswith("NO")
    digital_evidence = product["Digital_Evidence"]
    strategy_text = product["Strategy_Fit"].lower()

    if category in medians:
        family = category
        family_median = medians[family]
        evidence_confidence = 3
        trend_basis = f"Research family '{family}' median {family_median:g}; exact category match"
    else:
        if category not in CATEGORY_TREND_FAMILY:
            raise ValueError(
                f"Product category has no reviewed trend-family decision: {category!r}. "
                "Add an explicit research family or None to CATEGORY_TREND_FAMILY."
            )
        family = CATEGORY_TREND_FAMILY[category]
        if family is not None and family in medians:
            family_median = medians[family]
            evidence_confidence = 2
            trend_basis = f"Research family '{family}' median {family_median:g}; mapped from category '{category}'"
        else:
            family_median = float(NO_FAMILY_TREND_BASELINE)
            evidence_confidence = 1
            trend_basis = (
                f"NO PRIMARY-SOURCE RESEARCH FAMILY for category '{category}'; "
                f"baseline {NO_FAMILY_TREND_BASELINE} below every scored research family"
            )

    adjustment = STRATEGY_TREND_ADJUSTMENT[tier]
    trend = int(max(20, min(99, round(family_median + adjustment))))
    trend_basis = f"{trend_basis}; strategy-fit adjustment {adjustment:+d}"

    creation = COMPLEXITY_CREATION_EFFORT[c] - (1 if controlled_source else 0) + (1 if no_model else 0)

    validation = CRITICALITY_VALIDATION_EFFORT[k]
    if r <= 1:
        validation += 1
    if dimensions.get("PHY", 0) >= 3 or dimensions.get("MOT", 0) >= 3:
        validation += 1

    rights_value, rights_note = rights_risk(product["Rights_Provenance"])
    safety_value, safety_note = safety_risk(product["Safety_Risk"])
    risk = max(CRITICALITY_RISK[k], rights_value, safety_value)

    if any(keyword in strategy_text for keyword in AM_KEYWORDS):
        am = 5
    elif tier >= 4:
        am = 4
    else:
        am = 2 if tier == 1 else 3
    if dimensions.get("EXT", 0) >= 4:
        am = min(am, 3)

    leverage = 1
    if controlled_source:
        leverage += 1
    if "Parametric source" in digital_evidence or "parametric" in digital_evidence.lower():
        leverage += 1
    if family_size >= 6:
        leverage += 1
    if category.startswith("System-furniture") or any(
        keyword in strategy_text for keyword in ("modular", "reusable", "interface")
    ):
        leverage += 1

    digital = 5 - (dimensions.get("EXT", 0) + 1) // 2
    if dimensions.get("MOT", 0) >= 2:
        digital -= 1
    if dimensions.get("PHY", 0) >= 3:
        digital -= 1
    if k >= 2:
        digital -= 1
    # Only a blocked *digital* offer removes digital-first suitability. The same wording
    # on Printed_Offer means printed fulfillment is out of scope, which is digital-first.
    digital_offer = product["Digital_Offer"]
    if digital_offer.startswith("Block") and "digital-first scope" in digital_offer:
        digital = 1

    economics = COMPLEXITY_ECONOMICS[c]
    if dimensions.get("EXT", 0) >= 4:
        economics -= 1
    if tier == 5:
        economics += 1

    scores = {
        "Estimated_Market_Fit_1_5": market_fit_from_trend(trend),
        "Market_Evidence_Confidence_1_5": evidence_confidence,
        "Creation_Effort_1_5": clamp(creation),
        "Validation_Effort_1_5": clamp(validation),
        "Commercial_Risk_1_5": clamp(risk),
        "Strategy_Fit_1_5": tier,
        "AM_Differentiation_1_5": clamp(am),
        "Portfolio_Leverage_1_5": clamp(leverage),
        "Digital_First_Fit_1_5": clamp(digital),
        "Economics_1_5": clamp(economics),
    }
    rationale = (
        f"Derived from the live preflight {complexity['class']}/{preflight['readiness']['level']}/"
        f"{preflight['criticality']['level']} (EXT={dimensions.get('EXT', 0)}, MOT={dimensions.get('MOT', 0)}, "
        f"PHY={dimensions.get('PHY', 0)}), register strategy fit '{product['Strategy_Fit']}', "
        f"{rights_note}, {safety_note}, model status '{model_status.split(';')[0]}', "
        f"and {family_size} sibling products in its product family. Economics is a complexity and "
        f"purchased-content proxy only; no product COGS or price is recorded yet."
    )
    return scores, trend, trend_basis, rationale


def build_rows() -> list[dict[str, str]]:
    portfolio = {row["Source_Path"]: row for row in read_csv(PORTFOLIO_CSV)}
    priority_by_working = {
        row["Mapped_Working_SKU"]: row for row in read_csv(PRIORITY_CSV) if row["Mapped_Working_SKU"]
    }
    medians = family_trend_medians()
    directories = product_dirs()
    family_sizes: dict[str, int] = {}
    for directory in directories:
        family_sizes[directory.parent.name] = family_sizes.get(directory.parent.name, 0) + 1

    rows: list[dict[str, str]] = []
    for directory in directories:
        relative = f"products/{directory.relative_to(PRODUCTS_ROOT).as_posix()}"
        product = portfolio.get(relative)
        if product is None:
            raise ValueError(f"Product directory is missing from product-portfolio.csv: {relative}")
        preflight_path = directory / "preflight/preflight-result.json"
        if not preflight_path.is_file():
            raise ValueError(f"Product directory lacks a preflight result: {relative}")
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        working_sku = product["Working_SKU"]
        mapped = priority_by_working.get(working_sku)

        if mapped is not None:
            scores = {field: int(float(mapped[field])) for field in COMPONENT_FIELDS}
            trend = int(float(mapped["Trend_Score_0_100"]))
            basis = f"INHERITED — MAPPED RESEARCH IDEA {mapped['SKU_ID']}"
            trend_basis = (
                f"Recorded trend of mapped research idea {mapped['SKU_ID']} "
                f"({mapped['Product_Family']}); sources {mapped['Source_IDs']}"
            )
            rationale = mapped["Scoring_Rationale"]
            score = float(mapped["Priority_Score_0_100"])
        else:
            scores, trend, trend_basis, rationale = derive_scores(
                product, preflight, family_sizes[directory.parent.name], medians
            )
            basis = f"DERIVED — PRODUCT PREFLIGHT AND REGISTER EVIDENCE v{SCORING_VERSION}"
            score = priority_score(scores)

        rows.append(
            {
                "Product_Path": relative,
                "Working_SKU": working_sku,
                "Product": product["Product_or_Model"],
                "Product_Family_or_Category": product["Category"],
                "Score_Basis": basis,
                "Trend_Score_0_100": f"{trend:g}",
                "Priority_Score_0_100": f"{score:g}",
                "Opportunity_Score_0_100": f"{min(99, trend + 2):g}",
                "Risk_Score_1_5": str(scores["Commercial_Risk_1_5"]),
                **{field: str(scores[field]) for field in COMPONENT_FIELDS},
                "Trend_Basis": trend_basis,
                "Scoring_Rationale": rationale,
                "Score_Status": SCORE_STATUS,
                "Scored_On": SCORED_ON,
                "Scoring_Version": SCORING_VERSION,
            }
        )

    paths = [row["Product_Path"] for row in rows]
    skus = [row["Working_SKU"] for row in rows]
    if len(paths) != len(set(paths)) or len(skus) != len(set(skus)):
        raise ValueError("Product scoring rows must have unique paths and working SKUs")
    if len(rows) != len(directories):
        raise ValueError("Product scoring must cover every product directory exactly once")
    for row in rows:
        for field in ["Trend_Score_0_100", "Priority_Score_0_100", "Opportunity_Score_0_100"]:
            if not 0 <= float(row[field]) <= 100:
                raise ValueError(f"{field} out of range for {row['Product_Path']}")
        for field in ["Risk_Score_1_5", *COMPONENT_FIELDS]:
            if not 1 <= int(row[field]) <= 5:
                raise ValueError(f"{field} out of range for {row['Product_Path']}")
    return rows


def render(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the checked-in scoring is stale")
    args = parser.parse_args()
    rows = build_rows()
    content = render(rows)
    inherited = sum(1 for row in rows if row["Score_Basis"].startswith("INHERITED"))
    derived = len(rows) - inherited
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale or missing product-directory scoring: {OUTPUT}")
        print(f"PASS: {OUTPUT} is current with {len(rows)} products ({inherited} inherited, {derived} derived)")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(rows)} products ({inherited} inherited, {derived} derived)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
