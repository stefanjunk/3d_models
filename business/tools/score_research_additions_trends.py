#!/usr/bin/env python3
"""Score SKU-101 through SKU-200 with the documented directional trend model.

The score is a transparent planning screen, not measured product demand.  It
keeps source quality, signal magnitude, strategy fit and portfolio whitespace
separate so that a high general-market signal cannot hide a weak product fit.
"""

from __future__ import annotations

import argparse
import csv
import io
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT = REPO_ROOT / "business/02-portfolio/research-ideas-additions.csv"
ASSESSED_ON = "2026-09-01"
ASSESSMENT_VERSION = "1.0"

TREND_FIELDS = [
    "Trend_Source_Strength_0_30",
    "Trend_Signal_Magnitude_0_30",
    "Trend_MetriMade_Fit_0_25",
    "Trend_Whitespace_0_15",
    "Trend_Score_0_100",
    "Trend_Score_Basis",
    "Trend_Score_Status",
    "Trend_Score_Assessed_On",
    "Trend_Score_Version",
]

# Only directional market/problem sources belong in the trend calculation.
# Compliance, material, printer and process sources remain valuable evidence,
# but they do not increase a trend score.
SOURCE_STRENGTH = {
    "S31": 30,  # representative 31-market IKEA survey, including Germany
    "S34": 27,  # nine-market eBay recommerce survey, including Germany
    "S01": 26,  # Etsy marketplace search-direction report
    "S33": 25,  # Michaels search, sales and survey evidence; North America
    "S35": 24,  # RIAA audited industry direction; US physical media only
    "S10": 22,  # official EU repair-policy direction, not buyer demand
    "S29": 22,  # official EU repair-policy direction, not buyer demand
    "S09": 18,  # active maker marketplace collection; unquantified
}

SOURCE_MAGNITUDE = {
    "S33": 30,  # +40% sales and +86% to +329% search/kit signals
    "S01": 27,  # up to +835%; product relevance varies by concept
    "S31": 24,  # 68% catch-all storage plus concrete clutter/search friction
    "S34": 23,  # 72% hobby reconnection; passion-led recommerce direction
    "S35": 20,  # +9.3% vinyl revenue and 19 consecutive growth years
    "S09": 17,  # visible ecosystem activity without a quantified denominator
    "S10": 15,  # policy change is directional context, not market magnitude
    "S29": 15,
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def source_ids(row: dict[str, str]) -> list[str]:
    return [value.strip() for value in row["Source_IDs"].split(";") if value.strip()]


def relevance_text(row: dict[str, str]) -> str:
    return " ".join(
        row[field].lower()
        for field in ("Product", "Product_Family", "Customer_Job")
    )


def source_relevance(source_id: str, text: str) -> str:
    terms = {
        "S31": ("drawer", "shelf", "organ", "storage", "cubby", "wardrobe", "cable", "charger", "desk", "counter", "keepsake", "memory"),
        "S34": ("collect", "hobby", "coin", "card", "badge", "pin ", "media", "vinyl", "record", "cassette", "cd ", "figure", "mineral"),
        "S01": ("journal", "memory", "keepsake", "personal", "gift", "photo", "card", "washi", "badge", "pin ", "jewelry", "travel"),
        "S33": ("craft", "sewing", "needle", "thread", "floss", "crochet", "paint", "bead", "washi", "journal", "stamp", "die "),
        "S35": ("vinyl", "record", "physical-media", "cassette", "cd "),
        "S10": ("repair", "replacement", "button-cap", "plug", "liner", "glider"),
        "S29": ("repair", "replacement", "button-cap", "plug", "liner", "glider"),
        "S09": ("cable", "printer", "maker", "build-plate", "filament", "maintenance"),
    }
    if any(term in text for term in terms[source_id]):
        return "direct"
    return "adjacent"


def source_strength(row: dict[str, str], ids: list[str]) -> int:
    text = relevance_text(row)
    scored = []
    for value in ids:
        if value not in SOURCE_STRENGTH:
            continue
        score = SOURCE_STRENGTH[value]
        if source_relevance(value, text) == "adjacent":
            score -= 4
        scored.append(score)
    scored.sort(reverse=True)
    if not scored:
        return 12
    # Independent corroboration is useful, but cannot exceed the 30-point cap.
    return min(30, scored[0] + min(2, len(scored) - 1))


def signal_magnitude(row: dict[str, str], ids: list[str]) -> int:
    direct_text = relevance_text(row)
    scored = []
    for value in ids:
        if value not in SOURCE_MAGNITUDE:
            continue
        score = SOURCE_MAGNITUDE[value]
        if source_relevance(value, direct_text) == "adjacent":
            score -= 7 if value in {"S01", "S33"} else 4
        scored.append(score)
    scored.sort(reverse=True)
    if not scored:
        return 10

    value = scored[0]
    text = direct_text

    # Reduce a broad source when the row extrapolates beyond the source's named
    # product/problem family.  Raise only where the cited report names the same
    # behavior or category.
    if "S33" in ids and any(
        term in text
        for term in (
            "craft",
            "sewing",
            "needle",
            "thread",
            "floss",
            "crochet",
            "paint",
            "bead",
            "washi",
            "journal",
        )
    ):
        value = max(value, 30)
    if "S01" in ids and any(
        term in text
        for term in (
            "journal",
            "memory",
            "keepsake",
            "personalized",
            "photo",
            "card",
            "gift",
            "washi",
            "badge",
            "pin",
        )
    ):
        value = max(value, 28)
    if "S31" in ids and any(term in text for term in ("drawer", "cable", "charger", "counter")):
        value = max(value, 24)
    if "S34" in ids and any(term in text for term in ("collect", "coin", "card", "media", "vinyl")):
        value = max(value, 24)
    if "S35" in ids and "vinyl" not in text:
        value = min(value, 19)

    # A second independently relevant directional source adds at most one point;
    # a third adds one more.  This prevents source-count inflation.
    value += min(2, len(scored) - 1)
    return min(30, value)


def strategy_fit(row: dict[str, str]) -> int:
    value = row["Strategy_Fit"]
    if value.startswith("Core adjacent"):
        return 22
    if value.startswith("Core"):
        return 25
    if value.startswith("Adjacent specialist"):
        return 10
    if value.startswith("Adjacent"):
        return 15
    return 8


def portfolio_whitespace(row: dict[str, str], family_counts: Counter[str]) -> int:
    concept = row["Concept_Type"]
    if concept == "New":
        value = 13
    elif concept == "New platform variant":
        value = 10
    elif concept.startswith("Improvement"):
        value = 8
    elif concept.startswith("Variation"):
        value = 7
    else:
        value = 9

    count = family_counts[row["Product_Family"]]
    if count == 1:
        value += 1
    elif count >= 6:
        value -= 2
    elif count >= 3:
        value -= 1
    return max(0, min(15, value))


def expected_values(row: dict[str, str], family_counts: Counter[str]) -> dict[str, str]:
    ids = source_ids(row)
    strength = source_strength(row, ids)
    magnitude = signal_magnitude(row, ids)
    fit = strategy_fit(row)
    whitespace = portfolio_whitespace(row, family_counts)
    total = strength + magnitude + fit + whitespace
    market_ids = [value for value in ids if value in SOURCE_STRENGTH]
    basis = (
        f"Primary-source strength {strength}/30 ({'; '.join(market_ids) or 'no direct market source'}); "
        f"signal magnitude {magnitude}/30; metriMade strategy fit {fit}/25; "
        f"nonduplicate portfolio whitespace {whitespace}/15. "
        "Directional planning judgment; no German product-level demand proof."
    )
    return {
        "Trend_Source_Strength_0_30": str(strength),
        "Trend_Signal_Magnitude_0_30": str(magnitude),
        "Trend_MetriMade_Fit_0_25": str(fit),
        "Trend_Whitespace_0_15": str(whitespace),
        "Trend_Score_0_100": str(total),
        "Trend_Score_Basis": basis,
        "Trend_Score_Status": "DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND",
        "Trend_Score_Assessed_On": ASSESSED_ON,
        "Trend_Score_Version": ASSESSMENT_VERSION,
    }


def render(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if stored trend fields are stale or absent")
    args = parser.parse_args()

    original_fields, rows = read_rows(INPUT)
    required = {"SKU_ID", "Product", "Product_Family", "Concept_Type", "Customer_Job", "Trend_Signal", "Strategy_Fit", "Source_IDs"}
    missing = sorted(required - set(original_fields))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    expected_skus = [f"SKU-{number:03d}" for number in range(101, 201)]
    actual_skus = [row["SKU_ID"] for row in rows]
    if actual_skus != expected_skus:
        raise ValueError("Expected exactly ordered SKU-101 through SKU-200")

    family_counts = Counter(row["Product_Family"] for row in rows)
    mismatches: list[str] = []
    for row in rows:
        expected = expected_values(row, family_counts)
        for field, value in expected.items():
            if args.check and row.get(field, "") != value:
                mismatches.append(f"{row['SKU_ID']}:{field}")
            row[field] = value

    if args.check:
        if mismatches:
            print("Stale or missing trend fields: " + ", ".join(mismatches[:20]))
            if len(mismatches) > 20:
                print(f"... and {len(mismatches) - 20} more")
            return 1
        print(f"PASS: {len(rows)} trend scores are current")
        return 0

    fieldnames = original_fields + [field for field in TREND_FIELDS if field not in original_fields]
    INPUT.write_text(render(fieldnames, rows), encoding="utf-8")
    scores = [int(row["Trend_Score_0_100"]) for row in rows]
    print(f"Wrote {len(rows)} trend scores to {INPUT}")
    print(f"Range {min(scores)}-{max(scores)}; median {sorted(scores)[len(scores) // 2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
