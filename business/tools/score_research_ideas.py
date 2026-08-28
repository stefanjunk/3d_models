#!/usr/bin/env python3
"""Create a deterministic implementation-priority queue for all research ideas."""

from __future__ import annotations

import argparse
import csv
import io
import math
from pathlib import Path

from build_product_workbook import read_xlsx_sheet


ROOT = Path(__file__).resolve().parents[1]
LEGACY_WORKBOOK = ROOT.parent / "research" / "market" / "JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx"
ADDITIONS_CSV = ROOT / "02-portfolio" / "research-ideas-additions.csv"
IMPLEMENTATION_CSV = ROOT / "02-portfolio" / "research-ideas-implementation.csv"
OUTPUT_CSV = ROOT / "02-portfolio" / "research-idea-priority.csv"
SCORED_ON = "2026-08-27"
SCORING_VERSION = "1.0"

CURRENT_FINISH_ORDER = {
    "SKU-001": 1,
    "SKU-002": 2,
    "SKU-003": 3,
    "SKU-005": 4,
    "SKU-004": 5,
}

LEGACY_STRATEGY_FIT = {
    "Custom desk & drawer organizers": 5,
    "Cable-management systems": 5,
    "Phone/tablet stands & passive docks": 4,
    "Makeup & vanity organizers": 4,
    "3D wall art, reliefs & gallery panels": 3,
    "Mahjong racks, pushers & tile trays": 3,
    "Personalized signs, house numbers & event decor": 4,
    "Vases & sculptural containers": 2,
    "Headphone, controller & VR stands": 3,
    "Bookends, vinyl & display stands": 4,
    "Journaling & stationery accessories": 4,
    "Bathroom & shower organizers": 2,
    "Board-game inserts, card holders & dice towers": 3,
    "Non-safety-critical replacement parts": 2,
    "Wall hooks, key holders & entry organizers": 2,
    "Planters & self-watering planters": 2,
    "Custom TPU cases, sleeves & bumpers": 2,
    "Adult desk fidgets & original collectibles": 2,
    "Passive lampshades & light diffusers": 1,
    "Modular pegboard & wall-storage ecosystems": 2,
}

LEGACY_MARKET_PRIOR = {
    "Custom desk & drawer organizers": 5,
    "Cable-management systems": 5,
    "Phone/tablet stands & passive docks": 4,
    "Makeup & vanity organizers": 4,
    "3D wall art, reliefs & gallery panels": 4,
    "Mahjong racks, pushers & tile trays": 5,
    "Personalized signs, house numbers & event decor": 4,
    "Vases & sculptural containers": 3,
    "Headphone, controller & VR stands": 3,
    "Bookends, vinyl & display stands": 4,
    "Journaling & stationery accessories": 5,
    "Bathroom & shower organizers": 3,
    "Board-game inserts, card holders & dice towers": 3,
    "Non-safety-critical replacement parts": 3,
    "Wall hooks, key holders & entry organizers": 4,
    "Planters & self-watering planters": 3,
    "Custom TPU cases, sleeves & bumpers": 3,
    "Adult desk fidgets & original collectibles": 2,
    "Passive lampshades & light diffusers": 3,
    "Modular pegboard & wall-storage ecosystems": 3,
}

CRAFT_TERMS = (
    "sewing",
    "needle",
    "embroidery",
    "crochet",
    "thread",
    "washi",
    "craft",
    "journal",
    "floss",
    "paint",
    "bead",
    "stamp",
)
FIT_TERMS = (
    "exact-fit",
    "exact fit",
    "measured",
    "measurement",
    "fit-gauge",
    "fit gauge",
    "interface",
    "clip-on",
    "snap-on",
    "fold-flat",
    "hinge",
    "latch",
    "flexure",
    " tpu",
)
HIGH_VALIDATION_TERMS = (
    "wall-mounted",
    "wall mounted",
    "hanging",
    "load-bearing",
    "battery",
    "electrical",
    "lamp",
    "light diffuser",
    "heat",
    "water",
    "drain",
    "shower",
    "planter",
    "vase",
    "repair",
    "replacement",
    "appliance",
    "child",
    "toy",
    "food",
)

OUTPUT_FIELDS = [
    "Implementation_Order",
    "New_Build_Rank",
    "Next_Candidate_Rank",
    "SKU_ID",
    "Product",
    "Product_Family",
    "Implementation_Status",
    "Mapped_Working_SKU",
    "Decision_Tier",
    "Priority_Score_0_100",
    "Creation_Effort_1_5",
    "Validation_Effort_1_5",
    "Commercial_Risk_1_5",
    "Estimated_Market_Fit_1_5",
    "Market_Evidence_Confidence_1_5",
    "Strategy_Fit_1_5",
    "AM_Differentiation_1_5",
    "Portfolio_Leverage_1_5",
    "Digital_First_Fit_1_5",
    "Economics_1_5",
    "Source_IDs",
    "Scoring_Rationale",
    "Next_Action",
    "Scored_On",
    "Scoring_Version",
    "Score_Status",
]


def clamp(value: int, minimum: int = 1, maximum: int = 5) -> int:
    return max(minimum, min(maximum, value))


def round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))


def read_dict_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def implementation_map() -> dict[str, dict[str, str]]:
    rows = read_dict_csv(IMPLEMENTATION_CSV)
    return {row["SKU_ID"]: row for row in rows}


def implementation_started(implementation: dict[str, str]) -> bool:
    return implementation.get("Implementation_Status", "NOT_STARTED") != "NOT_STARTED"


def legacy_records() -> list[dict[str, object]]:
    rows = read_xlsx_sheet(LEGACY_WORKBOOK, "Product Matrix")
    records = []
    for values in rows[1:]:
        source = dict(zip(rows[0], values))
        records.append(
            {
                "source_group": "legacy",
                "sku_id": str(source["SKU ID"]),
                "product": str(source["Product"]),
                "family": str(source["Product Family"]),
                "customer_job": str(source["Customer Job"]),
                "trend_signal": str(source["2026 Trend Signal"]),
                "trend_score": float(source["Trend Score"]),
                "opportunity_score": float(source["Opportunity Score"]),
                "difficulty": int(source["Difficulty"]),
                "risk": int(source["Risk Score"]),
                "strategy_fit_text": "",
                "am_advantage": int(source["AM Advantage"]),
                "readiness": str(source["At-home Readiness"]),
                "economics": int(source["Manufacturing Economics"]),
                "offer_mode": "Digital file candidate",
                "material": str(source["Primary Material"]),
                "supports": str(source["Supports"]),
                "concept_type": "Legacy research idea",
                "source_ids": str(source["Source IDs"]),
                "next_gate": str(source["Next Gate"]),
                "dimensions": (float(source["Max L mm"]), float(source["Max W mm"]), float(source["Max H mm"])),
            }
        )
    return records


def additions_records() -> list[dict[str, object]]:
    difficulty_map = {"Easy": 1, "Moderate": 2, "Hard": 4}
    records = []
    for source in read_dict_csv(ADDITIONS_CSV):
        difficulty = difficulty_map.get(source["Difficulty"])
        if difficulty is None:
            raise ValueError(f"Unknown difficulty for {source['SKU_ID']}: {source['Difficulty']}")
        records.append(
            {
                "source_group": "addition",
                "sku_id": source["SKU_ID"],
                "product": source["Product"],
                "family": source["Product_Family"],
                "customer_job": source["Customer_Job"],
                "trend_signal": source["Trend_Signal"],
                "trend_score": None,
                "opportunity_score": float(source["Opportunity_Score"]),
                "difficulty": difficulty,
                "risk": int(source["Risk_Score"]),
                "strategy_fit_text": source["Strategy_Fit"],
                "am_advantage": source["AM_Advantage"],
                "readiness": "Digital first" if source["Offer_Mode"].startswith("Digital first") else "Both after validation",
                "economics": None,
                "offer_mode": source["Offer_Mode"],
                "material": source["Primary_Material"],
                "supports": source["Supports"],
                "concept_type": source["Concept_Type"],
                "source_ids": source["Source_IDs"],
                "next_gate": source["Next_Gate"],
                "dimensions": (float(source["Max_L_mm"]), float(source["Max_W_mm"]), float(source["Max_H_mm"])),
                "digital_price_lower": float(source["Digital_Price_Band_EUR"].split("-", 1)[0]),
            }
        )
    return records


def record_text(record: dict[str, object]) -> str:
    return " ".join(
        str(record[key]).lower()
        for key in ("product", "family", "customer_job", "trend_signal", "am_advantage", "strategy_fit_text", "material")
    )


def validation_text(record: dict[str, object]) -> str:
    return " ".join(
        str(record[key]).lower()
        for key in ("product", "family", "customer_job", "strategy_fit_text", "material")
    )


def score_strategy(record: dict[str, object]) -> int:
    if record["source_group"] == "legacy":
        return LEGACY_STRATEGY_FIT.get(str(record["family"]), 3)
    text = str(record["strategy_fit_text"])
    if text.startswith("Core adjacent"):
        return 4
    if text.startswith("Core"):
        return 5
    if text.startswith("Adjacent specialist"):
        return 1
    return 2


def market_prior(record: dict[str, object]) -> int:
    if record["source_group"] == "legacy":
        return LEGACY_MARKET_PRIOR.get(str(record["family"]), 3)
    text = record_text(record)
    if any(term in text for term in CRAFT_TERMS):
        return 5
    if any(term in text for term in ("drawer", "shelf", "cable", "desk organization", "stationery")):
        return 5
    if any(term in text for term in ("personalized", "keepsake", "memory", "collectible", "jewelry", "media", "vinyl")):
        return 4
    if any(term in text for term in ("phone", "device", "travel", "hospitality")):
        return 4
    if any(term in text for term in ("printer", "workshop", "tool", "repair", "replacement")):
        return 3
    return 3


def score_market_fit(record: dict[str, object]) -> int:
    if record["source_group"] == "legacy":
        trend = float(record["trend_score"])
        base = 5 if trend >= 92 else 4 if trend >= 84 else 3 if trend >= 75 else 2 if trend >= 65 else 1
    else:
        opportunity = float(record["opportunity_score"])
        base = 5 if opportunity >= 93 else 4 if opportunity >= 87 else 3 if opportunity >= 78 else 2 if opportunity >= 65 else 1
    score = clamp(round_half_up((base + market_prior(record)) / 2))
    text = record_text(record)
    sources = str(record["source_ids"])
    if "mahjong" in text and "S01" in sources:
        score = 5
    if any(term in text for term in CRAFT_TERMS) and ("S01" in sources or "S33" in sources):
        score = max(score, 5)
    if any(term in text for term in ("drawer", "cable", "countertop")) and "S31" in sources:
        score = max(score, 4)
    return score


def score_evidence_confidence(record: dict[str, object]) -> int:
    text = record_text(record)
    sources = {item.strip() for item in str(record["source_ids"]).split(";") if item.strip()}
    score = 2
    if sources.intersection({"S01", "S06", "S07", "S08", "S31", "S33", "S34"}):
        score = 3
    if "S01" in sources and ("mahjong" in text or "journal" in text):
        score = 4
    return score


def score_am_differentiation(record: dict[str, object]) -> int:
    if record["source_group"] == "legacy":
        return int(record["am_advantage"])
    text = str(record["am_advantage"]).lower()
    if any(
        term in text
        for term in (
            "exact",
            "measured",
            "one-off",
            "parametric",
            "millimeter",
            "customer-specific",
            "generated",
            "dimensions vary",
            "can match",
            "parameters",
        )
    ):
        return 5
    if any(term in text for term in ("modular", "module", "personal", "variable", "varies", "mixed", "batch", "collection-specific", "clip family", "shared")):
        return 4
    return 3


def score_portfolio_leverage(record: dict[str, object], implementation: dict[str, str]) -> int:
    if implementation_started(implementation):
        return 5
    concept_type = str(record["concept_type"])
    text = record_text(record)
    if concept_type.startswith("Improvement") or concept_type.startswith("Variation"):
        return 5
    if concept_type == "New platform variant":
        return 4
    if any(term in text for term in ("measurement gauge", "clearance coupon", "reusable portfolio", "shelffit", "drawerfit", "label-window")):
        return 5
    if score_strategy(record) >= 4 or str(record["family"]) in {
        "Custom desk & drawer organizers",
        "Cable-management systems",
        "Phone/tablet stands & passive docks",
        "Bookends, vinyl & display stands",
    }:
        return 4
    if score_strategy(record) <= 2:
        return 2
    return 3


def score_digital_fit(record: dict[str, object]) -> int:
    if record["source_group"] == "legacy":
        score = {"Ready": 5, "Guided": 4, "Local only": 2}.get(str(record["readiness"]), 3)
    else:
        score = 5 if str(record["offer_mode"]).startswith("Digital first") else 4
    material = str(record["material"]).lower()
    dimensions = tuple(float(value) for value in record["dimensions"])
    if " with " in material or "optional tpu" in material or "pla with" in material or "petg with" in material:
        score -= 1
    if sum(value >= 180 for value in dimensions) >= 2:
        score -= 1
    if str(record["supports"]).lower() not in {"none", "no"}:
        score -= 1
    return clamp(score)


def score_economics(record: dict[str, object]) -> int:
    if record["source_group"] == "legacy":
        return int(record["economics"])
    price = float(record["digital_price_lower"])
    score = 5 if price >= 10 else 4 if price >= 7 else 3
    dimensions = tuple(float(value) for value in record["dimensions"])
    material = str(record["material"]).lower()
    if sum(value >= 180 for value in dimensions) >= 2:
        score -= 1
    if " with " in material or "optional tpu" in material or "pla with" in material or "petg with" in material:
        score -= 1
    return clamp(score)


def score_validation_effort(record: dict[str, object]) -> int:
    effort = int(record["difficulty"])
    risk = int(record["risk"])
    score = max(risk, round_half_up((effort + risk) / 2))
    text = validation_text(record)
    if any(term in text for term in FIT_TERMS):
        score += 1
    if any(term in text for term in HIGH_VALIDATION_TERMS):
        score += 1
    return clamp(score)


def inverse_component(score: int, weight: float) -> float:
    return ((5 - score) / 4) * weight


def priority_score(scores: dict[str, int]) -> float:
    total = (
        scores["market"] / 5 * 20
        + scores["strategy"] / 5 * 15
        + scores["am"] / 5 * 10
        + scores["leverage"] / 5 * 15
        + scores["digital"] / 5 * 5
        + scores["economics"] / 5 * 5
        + scores["evidence"] / 5 * 5
        + inverse_component(scores["creation"], 8)
        + inverse_component(scores["validation"], 8)
        + inverse_component(scores["risk"], 9)
    )
    return round(total, 1)


def score_records() -> list[dict[str, object]]:
    implementations = implementation_map()
    records = legacy_records() + additions_records()
    ids = [str(record["sku_id"]) for record in records]
    expected = {f"SKU-{number:03d}" for number in range(1, 201)}
    if len(records) != 200 or len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError("Scoring inputs must contain each ID from SKU-001 through SKU-200 exactly once")

    scored = []
    for record in records:
        implementation = implementations.get(str(record["sku_id"]), {})
        scores = {
            "creation": int(record["difficulty"]),
            "validation": score_validation_effort(record),
            "risk": int(record["risk"]),
            "market": score_market_fit(record),
            "evidence": score_evidence_confidence(record),
            "strategy": score_strategy(record),
            "am": score_am_differentiation(record),
            "leverage": score_portfolio_leverage(record, implementation),
            "digital": score_digital_fit(record),
            "economics": score_economics(record),
        }
        scored.append(
            {
                "record": record,
                "implementation": implementation,
                "scores": scores,
                "priority": priority_score(scores),
            }
        )

    unstarted = [item for item in scored if not implementation_started(item["implementation"])]
    unstarted.sort(key=lambda item: (-float(item["priority"]), int(str(item["record"]["sku_id"]).split("-")[1])))
    for rank, item in enumerate(unstarted, start=1):
        item["new_build_rank"] = rank

    eligible = [
        item
        for item in unstarted
        if item["scores"]["risk"] <= 2
        and item["scores"]["creation"] <= 2
        and item["scores"]["validation"] <= 3
        and item["scores"]["strategy"] >= 4
        and item["scores"]["market"] >= 4
        and item["scores"]["evidence"] >= 3
    ][:10]
    eligible_ids = {str(item["record"]["sku_id"]): rank for rank, item in enumerate(eligible, start=1)}

    for item in scored:
        sku_id = str(item["record"]["sku_id"])
        scores = item["scores"]
        if implementation_started(item["implementation"]):
            item["tier"] = "0 FINISH CURRENT VALIDATION"
            item["tier_order"] = 0
        elif sku_id in eligible_ids:
            item["tier"] = "1 NEXT — DEMAND TEST THEN CAD"
            item["tier_order"] = 1
            item["next_candidate_rank"] = eligible_ids[sku_id]
        elif scores["risk"] >= 4 or scores["strategy"] <= 2:
            item["tier"] = "4 HOLD / SPECIALIST"
            item["tier_order"] = 4
        elif float(item["priority"]) >= 70:
            item["tier"] = "2 VALIDATE NEXT"
            item["tier_order"] = 2
        else:
            item["tier"] = "3 LATER"
            item["tier_order"] = 3

    def queue_key(item: dict[str, object]) -> tuple[object, ...]:
        sku_id = str(item["record"]["sku_id"])
        if item["tier_order"] == 0:
            return (0, CURRENT_FINISH_ORDER.get(sku_id, 999), 0, sku_id)
        if item["tier_order"] == 1:
            return (1, int(item["next_candidate_rank"]), 0, sku_id)
        return (int(item["tier_order"]), -float(item["priority"]), int(item.get("new_build_rank", 999)), sku_id)

    scored.sort(key=queue_key)
    for order, item in enumerate(scored, start=1):
        item["implementation_order"] = order
    return scored


def rationale(item: dict[str, object]) -> str:
    scores = item["scores"]
    return (
        f"Estimated market fit {scores['market']}/5 with evidence confidence {scores['evidence']}/5; "
        f"strategy fit {scores['strategy']}/5; additive differentiation {scores['am']}/5; "
        f"portfolio leverage {scores['leverage']}/5; creation effort {scores['creation']}/5, "
        f"validation effort {scores['validation']}/5 and commercial risk {scores['risk']}/5."
    )


def next_action(item: dict[str, object]) -> str:
    next_gate = str(item["record"]["next_gate"])
    tier = str(item["tier"])
    if tier.startswith("0 "):
        workflow = str(item["implementation"].get("Workflow_Stage", ""))
        if workflow == "P2-digital-print-candidate":
            return "Print the declared first-fit coupon or gauge, then the unchanged candidate; record physical fit, use, cycle, safety, rights and commercial-release evidence."
        return f"Do not start another model first; close slicer, physical, rights and commercial evidence. Existing next gate: {next_gate}"
    if tier.startswith("1 "):
        return f"Check German search/competition and collect at least five qualified problem signals; if positive, implement the smallest coupon or prototype. Design gate: {next_gate}"
    if tier.startswith("2 "):
        return f"Run demand and workflow validation before CAD capacity is assigned. Proposed gate: {next_gate}"
    if tier.startswith("4 "):
        return f"Hold CAD until safety, rights, interface and specialist-test scope is cleared. Proposed gate: {next_gate}"
    return f"Keep in the research backlog until higher tiers are resolved. Proposed gate: {next_gate}"


def output_rows() -> list[dict[str, object]]:
    rows = []
    for item in score_records():
        record = item["record"]
        implementation = item["implementation"]
        scores = item["scores"]
        rows.append(
            {
                "Implementation_Order": item["implementation_order"],
                "New_Build_Rank": item.get("new_build_rank", ""),
                "Next_Candidate_Rank": item.get("next_candidate_rank", ""),
                "SKU_ID": record["sku_id"],
                "Product": record["product"],
                "Product_Family": record["family"],
                "Implementation_Status": implementation.get("Implementation_Status", "NOT_STARTED"),
                "Mapped_Working_SKU": implementation.get("Mapped_Working_SKU", ""),
                "Decision_Tier": item["tier"],
                "Priority_Score_0_100": item["priority"],
                "Creation_Effort_1_5": scores["creation"],
                "Validation_Effort_1_5": scores["validation"],
                "Commercial_Risk_1_5": scores["risk"],
                "Estimated_Market_Fit_1_5": scores["market"],
                "Market_Evidence_Confidence_1_5": scores["evidence"],
                "Strategy_Fit_1_5": scores["strategy"],
                "AM_Differentiation_1_5": scores["am"],
                "Portfolio_Leverage_1_5": scores["leverage"],
                "Digital_First_Fit_1_5": scores["digital"],
                "Economics_1_5": scores["economics"],
                "Source_IDs": record["source_ids"],
                "Scoring_Rationale": rationale(item),
                "Next_Action": next_action(item),
                "Scored_On": SCORED_ON,
                "Scoring_Version": SCORING_VERSION,
                "Score_Status": "PLANNING ESTIMATE — NOT RELEASE APPROVAL",
            }
        )
    return rows


def render_csv(rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in priority CSV is stale")
    args = parser.parse_args()
    rendered = render_csv(output_rows())
    if args.check:
        if not OUTPUT_CSV.is_file() or OUTPUT_CSV.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Stale or missing priority output: {OUTPUT_CSV}")
        print(f"Validated {OUTPUT_CSV}")
        return
    OUTPUT_CSV.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV} with 200 scored ideas")


if __name__ == "__main__":
    main()
