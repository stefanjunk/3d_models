#!/usr/bin/env python3
"""Build the complete research preflight planning overlay."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_CSV = REPO_ROOT / "business/02-portfolio/product-portfolio.csv"
PRIORITY_CSV = REPO_ROOT / "business/02-portfolio/research-idea-priority.csv"
STATUS_CSV = REPO_ROOT / "business/02-portfolio/research-ideas-implementation.csv"
STRUCTURED_RESEARCH_CSV = REPO_ROOT / "business/02-portfolio/research-ideas-additions-2.csv"
R3_VARIANTS_CSV = REPO_ROOT / "business/02-portfolio/research-ideas-r3-variants.csv"
GENERATIVE_RESEARCH_CSV = REPO_ROOT / "business/02-portfolio/research-ideas-additions-3.csv"
OUTPUT = REPO_ROOT / "business/02-portfolio/research-idea-preflight-estimates.csv"
ASSESSMENT_DATE = "2026-09-04"
ESTIMATE_VERSION = "1.3"
# Generic research ideas occupy one contiguous block; named-interface R3 children are
# declared in explicit blocks because SKU-315..414 is reserved for the Step1X block.
GENERIC_RESEARCH_ID_MAX = 300
VARIANT_ID_BLOCKS = ((301, 314), (501, 557))
STEP1X_ID_BLOCK = (315, 414)

FIELDNAMES = [
    "SKU_ID",
    "Preflight_Short",
    "Complexity_Band",
    "Readiness_Band",
    "Criticality_Band",
    "Current_Lane",
    "Target_Lane_After_Evidence",
    "Confidence",
    "Design_Release",
    "Estimate_Status",
    "Creation_Effort_1_5",
    "Validation_Effort_1_5",
    "Research_Risk_1_5",
    "Basis",
    "Source_Or_Linked_Preflight",
    "Assessed_On",
    "Estimate_Version",
]


def read_dict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def preliminary_complexity(creation: int, validation: int) -> str:
    """Return a conservative class band without pretending to calculate full PC."""
    peak = max(creation, validation)
    if peak == 1:
        return "C1"
    if peak == 2:
        return "C1\u2013C2" if creation == 1 else "C2"
    if peak == 3:
        return "C2\u2013C3" if creation <= 2 else "C3"
    if peak == 4:
        return "C3\u2013C4"
    if creation >= 5:
        return "C5"
    if creation >= 4:
        return "C4\u2013C5"
    return "C3\u2013C4"


def preliminary_criticality(research_risk: int) -> str:
    """Map the existing research-risk proxy to a deliberately broad K band."""
    return {
        1: "K1",
        2: "K1\u2013K2",
        3: "K2",
        4: "K2\u2013K3",
        5: "K3",
    }[research_risk]


def upper_level(value: str, prefix: str) -> int:
    levels = [int(match) for match in re.findall(rf"{prefix}([0-5])", value)]
    if not levels:
        raise ValueError(f"Cannot parse {prefix} level from {value!r}")
    return max(levels)


def lower_level(value: str, prefix: str) -> int:
    levels = [int(match) for match in re.findall(rf"{prefix}([0-5])", value)]
    if not levels:
        raise ValueError(f"Cannot parse {prefix} level from {value!r}")
    return min(levels)


def target_lane(complexity: str, criticality: str) -> str:
    """Show the likely design lane only after R/gate evidence is sufficient."""
    c_low = lower_level(complexity, "C")
    c_high = upper_level(complexity, "C")
    k_high = upper_level(criticality, "K")
    if k_high >= 4:
        return "E"
    if c_high >= 4 or k_high >= 3:
        return "D"
    if c_high >= 3 or k_high >= 2:
        return "C"
    if c_low <= 1 and k_high == 0:
        return "A"
    return "B"


def linked_product_row(
    idea: dict[str, str],
    implementation: dict[str, str],
    portfolio_by_sku: dict[str, dict[str, str]],
) -> dict[str, str]:
    mapped_sku = implementation.get("Mapped_Working_SKU", "")
    if not mapped_sku or mapped_sku not in portfolio_by_sku:
        raise ValueError(f"{idea['SKU_ID']} has MODEL_EXISTS without a valid Mapped_Working_SKU")
    portfolio = portfolio_by_sku[mapped_sku]
    preflight_path = REPO_ROOT / portfolio["Source_Path"] / "preflight/preflight-result.json"
    with preflight_path.open(encoding="utf-8") as handle:
        preflight = json.load(handle)
    complexity = str(preflight["complexity"]["class"])
    readiness = str(preflight["readiness"]["level"])
    criticality = str(preflight["criticality"]["level"])
    lane = str(preflight["decision"]["lane"])
    confidence = str(preflight["decision"]["confidence"])
    design_release = str(preflight["decision"]["design_release"])
    relative_preflight = preflight_path.relative_to(REPO_ROOT).as_posix()
    return {
        "Preflight_Short": f"{complexity} \u00b7 {readiness} \u00b7 {criticality} \u00b7 Lane {lane} \u00b7 {confidence}",
        "Complexity_Band": complexity,
        "Readiness_Band": readiness,
        "Criticality_Band": criticality,
        "Current_Lane": lane,
        "Target_Lane_After_Evidence": target_lane(complexity, criticality),
        "Confidence": confidence,
        "Design_Release": design_release,
        "Estimate_Status": "LINKED CURRENT PRODUCT PREFLIGHT \u2014 NOT RELEASE APPROVAL",
        "Basis": f"Mapped to {mapped_sku}; exact current scorecard from the linked product preflight.",
        "Source_Or_Linked_Preflight": relative_preflight,
    }


def preliminary_idea_row(idea: dict[str, str]) -> dict[str, str]:
    creation = int(idea["Creation_Effort_1_5"])
    validation = int(idea["Validation_Effort_1_5"])
    research_risk = int(idea["Commercial_Risk_1_5"])
    if not all(1 <= value <= 5 for value in (creation, validation, research_risk)):
        raise ValueError(f"Research planning inputs are outside 1\u20135 for {idea['SKU_ID']}")
    complexity = preliminary_complexity(creation, validation)
    readiness = "R0\u2013R1"
    criticality = preliminary_criticality(research_risk)
    confidence = "NOT_AUTONOMOUSLY_RELEASABLE" if criticality == "K3" else "LOW_UNKNOWN"
    return {
        "Preflight_Short": f"{complexity} \u00b7 {readiness} \u00b7 {criticality} \u00b7 Lane E \u00b7 {confidence}",
        "Complexity_Band": complexity,
        "Readiness_Band": readiness,
        "Criticality_Band": criticality,
        "Current_Lane": "E",
        "Target_Lane_After_Evidence": target_lane(complexity, criticality),
        "Confidence": confidence,
        "Design_Release": "CONCEPT_ONLY",
        "Estimate_Status": "PRELIMINARY IDEA ESTIMATE \u2014 NOT RELEASE APPROVAL",
        "Basis": (
            f"C band from creation/validation planning effort ({creation}/{validation}); "
            f"K band from the research-risk proxy ({research_risk}/5); R0\u2013R1 and Lane E until "
            "critical interfaces, the manufacturing profile, acceptance criteria, and verification evidence exist."
        ),
        "Source_Or_Linked_Preflight": "business/02-portfolio/research-idea-priority.csv",
    }


def structured_research_row(source: dict[str, str]) -> dict[str, str]:
    """Carry the explicit R2 concept preflight without treating it as a release."""
    required = {
        "Preflight_Short",
        "Complexity",
        "Readiness",
        "Criticality",
        "Current_Lane",
        "Target_Lane_After_Evidence",
        "Confidence",
        "Design_Release",
        "Preflight_Status",
        "PC_0_100",
        "Readiness_Basis",
        "Hard_Gates",
    }
    missing = sorted(required.difference(source))
    if missing:
        raise ValueError(f"Structured research row {source.get('SKU_ID', '?')} lacks: {', '.join(missing)}")
    if source["Readiness"] != "R2" or source["Criticality"] != "K1":
        raise ValueError(f"Structured research row violates the requested R2/K1 gate: {source['SKU_ID']}")
    if source["Complexity"] not in {"C0", "C1", "C2"}:
        raise ValueError(f"Structured research row exceeds C2: {source['SKU_ID']}")
    if float(source["Trend_Score_0_100"]) <= 70:
        raise ValueError(f"Structured research row does not exceed trend score 70: {source['SKU_ID']}")
    if source["Current_Lane"] != "E" or "G3 FAIL" not in source["Hard_Gates"]:
        raise ValueError(f"Structured research row must remain Lane E while the process gate is open: {source['SKU_ID']}")
    return {
        "Preflight_Short": source["Preflight_Short"],
        "Complexity_Band": source["Complexity"],
        "Readiness_Band": source["Readiness"],
        "Criticality_Band": source["Criticality"],
        "Current_Lane": source["Current_Lane"],
        "Target_Lane_After_Evidence": source["Target_Lane_After_Evidence"],
        "Confidence": source["Confidence"],
        "Design_Release": source["Design_Release"],
        "Estimate_Status": source["Preflight_Status"],
        "Basis": (
            f"Explicit concept preflight PC={source['PC_0_100']}/100. {source['Readiness_Basis']} "
            f"Hard gates: {source['Hard_Gates']}"
        ),
        "Source_Or_Linked_Preflight": "business/02-portfolio/research-ideas-additions-2.csv",
    }


def generative_research_row(source: dict[str, str]) -> dict[str, str]:
    """Carry the generative Step1X concept preflight without treating it as a release."""
    required = {
        "Preflight_Short",
        "Complexity",
        "Readiness",
        "Criticality",
        "Current_Lane",
        "Target_Lane_After_Evidence",
        "Confidence",
        "Design_Release",
        "Preflight_Status",
        "PC_0_100",
        "Readiness_Basis",
        "Hard_Gates",
        "Trend_Score_0_100",
        "Generative_Tool_Licence_Gate",
    }
    missing = sorted(required.difference(source))
    if missing:
        raise ValueError(f"Generative research row {source.get('SKU_ID', '?')} lacks: {', '.join(missing)}")
    sku_id = source["SKU_ID"]
    if source["Readiness"] != "R2":
        raise ValueError(f"Generative research row violates the R2 concept gate: {sku_id}")
    if source["Criticality"] not in {"K1", "K2"}:
        raise ValueError(f"Generative research row is outside the K1-K2 band: {sku_id}")
    if source["Complexity"] not in {"C1", "C2", "C3"}:
        raise ValueError(f"Generative research row is outside the C1-C3 band: {sku_id}")
    if float(source["Trend_Score_0_100"]) <= 70:
        raise ValueError(f"Generative research row does not exceed trend score 70: {sku_id}")
    if source["Current_Lane"] != "E" or "G3 FAIL" not in source["Hard_Gates"]:
        raise ValueError(f"Generative research row must remain Lane E while the process gate is open: {sku_id}")
    if "TOOL-LICENCE FAIL" not in source["Hard_Gates"]:
        raise ValueError(f"Generative research row must keep the tooling-licence gate open: {sku_id}")
    if source["Design_Release"] != "CONCEPT_ONLY":
        raise ValueError(f"Generative research row bypasses the concept-only gate: {sku_id}")
    expected_lane = target_lane(source["Complexity"], source["Criticality"])
    if source["Target_Lane_After_Evidence"] != expected_lane:
        raise ValueError(f"Generative research target lane is inconsistent for {sku_id}")
    return {
        "Preflight_Short": source["Preflight_Short"],
        "Complexity_Band": source["Complexity"],
        "Readiness_Band": source["Readiness"],
        "Criticality_Band": source["Criticality"],
        "Current_Lane": source["Current_Lane"],
        "Target_Lane_After_Evidence": source["Target_Lane_After_Evidence"],
        "Confidence": source["Confidence"],
        "Design_Release": source["Design_Release"],
        "Estimate_Status": source["Preflight_Status"],
        "Basis": (
            f"Explicit generative concept preflight PC={source['PC_0_100']}/100. {source['Readiness_Basis']} "
            f"Hard gates: {source['Hard_Gates']}. Generative tooling licence: {source['Generative_Tool_Licence_Gate']}"
        ),
        "Source_Or_Linked_Preflight": "business/02-portfolio/research-ideas-additions-3.csv",
    }


def specific_variant_row(source: dict[str, str]) -> dict[str, str]:
    """Carry an evidence-backed named-interface R3 variant without releasing it."""
    required = {
        "Preflight_Short",
        "Complexity",
        "Readiness",
        "Criticality",
        "Current_Lane",
        "Target_Lane_After_Evidence",
        "Confidence",
        "Design_Release",
        "Preflight_Status",
        "PC_0_100",
        "Readiness_Basis",
        "Hard_Gates",
    }
    missing = sorted(required.difference(source))
    if missing:
        raise ValueError(f"Specific variant row {source.get('SKU_ID', '?')} lacks: {', '.join(missing)}")
    if source["Readiness"] != "R3" or source["Criticality"] != "K1":
        raise ValueError(f"Specific variant violates the R3/K1 gate: {source['SKU_ID']}")
    if source["Complexity"] not in {"C1", "C2", "C3"}:
        raise ValueError(f"Specific variant is outside C1-C3: {source['SKU_ID']}")
    expected_lane = "C" if source["Complexity"] == "C3" else "B"
    if source["Current_Lane"] != expected_lane or source["Target_Lane_After_Evidence"] != expected_lane:
        raise ValueError(f"Specific variant lane is inconsistent: {source['SKU_ID']}")
    if source["Confidence"] != "CONDITIONAL" or source["Design_Release"] != "GO_WITH_CONTROLS":
        raise ValueError(f"Specific variant confidence/release is inconsistent: {source['SKU_ID']}")
    required_gates = {f"G{number} PASS" for number in range(7)}
    gates = {gate.strip() for gate in source["Hard_Gates"].split(";")}
    if not required_gates.issubset(gates):
        raise ValueError(f"Specific variant does not pass G0-G6: {source['SKU_ID']}")
    return {
        "Preflight_Short": source["Preflight_Short"],
        "Complexity_Band": source["Complexity"],
        "Readiness_Band": source["Readiness"],
        "Criticality_Band": source["Criticality"],
        "Current_Lane": source["Current_Lane"],
        "Target_Lane_After_Evidence": source["Target_Lane_After_Evidence"],
        "Confidence": source["Confidence"],
        "Design_Release": source["Design_Release"],
        "Estimate_Status": source["Preflight_Status"],
        "Basis": (
            f"Evidence-backed named-interface variant PC={source['PC_0_100']}/100. "
            f"{source['Readiness_Basis']} Hard gates: {source['Hard_Gates']}"
        ),
        "Source_Or_Linked_Preflight": "business/02-portfolio/research-ideas-r3-variants.csv",
    }


def variant_ids() -> set[str]:
    """Return the declared named-interface R3 child identifiers."""
    return {
        f"SKU-{number:03d}"
        for first, last in VARIANT_ID_BLOCKS
        for number in range(first, last + 1)
    }

def generative_ids() -> set[str]:
    """Return the reserved generative Step1X-3D research identifiers."""
    return {
        f"SKU-{number:03d}" for number in range(STEP1X_ID_BLOCK[0], STEP1X_ID_BLOCK[1] + 1)
    }


def expected_research_ids() -> set[str]:
    """Return every declared research ID: generic ideas, R3 children and generative concepts."""
    generic = {f"SKU-{number:03d}" for number in range(1, GENERIC_RESEARCH_ID_MAX + 1)}
    return generic | variant_ids() | generative_ids()


def build_rows() -> list[dict[str, str]]:
    priority = read_dict_rows(PRIORITY_CSV)
    expected = expected_research_ids()
    if len(priority) != len(expected):
        raise ValueError(f"Expected {len(expected)} research ideas; found {len(priority)}")
    ids = [row["SKU_ID"] for row in priority]
    if set(ids) != expected or len(ids) != len(set(ids)):
        raise ValueError(
            "Research priority must contain each declared research ID exactly once"
        )

    implementation_by_id = {row["SKU_ID"]: row for row in read_dict_rows(STATUS_CSV)}
    portfolio_rows = read_dict_rows(PORTFOLIO_CSV)
    portfolio_by_sku = {row["Working_SKU"]: row for row in portfolio_rows}
    if len(portfolio_by_sku) != len(portfolio_rows):
        raise ValueError("Portfolio Working_SKU values must be unique for linked preflight lookup")
    structured_rows = read_dict_rows(STRUCTURED_RESEARCH_CSV)
    structured_by_id = {row["SKU_ID"]: row for row in structured_rows}
    expected_structured = {f"SKU-{number:03d}" for number in range(201, 301)}
    if len(structured_rows) != 100 or set(structured_by_id) != expected_structured:
        raise ValueError("Structured research source must contain each SKU-201 through SKU-300 exactly once")
    variant_rows = read_dict_rows(R3_VARIANTS_CSV)
    variant_by_id = {row["SKU_ID"]: row for row in variant_rows}
    expected_variants = variant_ids()
    if len(variant_rows) != len(expected_variants) or set(variant_by_id) != expected_variants:
        raise ValueError("Specific R3 variant source must contain each declared variant ID exactly once")
    generative_rows = read_dict_rows(GENERATIVE_RESEARCH_CSV)
    generative_by_id = {row["SKU_ID"]: row for row in generative_rows}
    expected_generative = generative_ids()
    if len(generative_rows) != len(expected_generative) or set(generative_by_id) != expected_generative:
        raise ValueError("Generative research source must contain each declared SKU-315..414 ID exactly once")

    output: list[dict[str, str]] = []
    for idea in sorted(priority, key=lambda row: int(row["SKU_ID"].split("-")[1])):
        implementation = implementation_by_id.get(idea["SKU_ID"], {})
        if implementation.get("Implementation_Status") == "MODEL_EXISTS":
            assessment = linked_product_row(idea, implementation, portfolio_by_sku)
        elif idea["SKU_ID"] in variant_by_id:
            assessment = specific_variant_row(variant_by_id[idea["SKU_ID"]])
        elif idea["SKU_ID"] in structured_by_id:
            assessment = structured_research_row(structured_by_id[idea["SKU_ID"]])
        elif idea["SKU_ID"] in generative_by_id:
            assessment = generative_research_row(generative_by_id[idea["SKU_ID"]])
        else:
            assessment = preliminary_idea_row(idea)
        output.append(
            {
                "SKU_ID": idea["SKU_ID"],
                **assessment,
                "Creation_Effort_1_5": idea["Creation_Effort_1_5"],
                "Validation_Effort_1_5": idea["Validation_Effort_1_5"],
                "Research_Risk_1_5": idea["Commercial_Risk_1_5"],
                "Assessed_On": ASSESSMENT_DATE,
                "Estimate_Version": ESTIMATE_VERSION,
            }
        )
    return output


def render(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the generated CSV is missing or stale.")
    args = parser.parse_args()
    estimate_rows = build_rows()
    content = render(estimate_rows)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale or missing generated research preflight overlay: {OUTPUT}")
        print(f"PASS: {OUTPUT} is current with {len(estimate_rows)} research preflight rows")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(estimate_rows)} research preflight rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
