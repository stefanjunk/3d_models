#!/usr/bin/env python3
"""Create a safe, editable product blueprint from a thin web-app brief."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


ARCHETYPES = (
    "marketing",
    "saas",
    "utility",
    "commerce",
    "affiliate",
    "marketplace",
    "content",
    "community",
    "portal",
)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "web-app"


def infer_archetype(brief: str) -> str:
    text = brief.lower()
    keyword_groups = (
        ("marketplace", ("marketplace", "buyers and sellers", "buyer and seller", "vendors", "anbieter", "marktplatz")),
        ("affiliate", ("affiliate", "referral link", "recommendation site", "best products", "vergleich", "empfehl")),
        ("commerce", ("ecommerce", "e-commerce", "online shop", "storefront", "checkout", "warenkorb", "shop")),
        ("community", ("community", "forum", "social network", "user posts", "ugc", "gemeinschaft")),
        ("saas", ("saas", "dashboard", "analytics", "workspace", "crm", "tickets", "operations")),
        ("portal", ("portal", "internal tool", "admin tool", "back office", "intranet")),
        ("content", ("publication", "knowledge base", "documentation", "blog", "magazine", "catalog")),
        ("marketing", ("landing page", "launch site", "marketing site", "waitlist", "brochure")),
    )
    for archetype, keywords in keyword_groups:
        if any(keyword in text for keyword in keywords):
            return archetype
    return "utility"


def route(path: str, purpose: str, action: str, audience: list[str] | None = None, indexing: str = "private") -> dict[str, Any]:
    return {
        "path": path,
        "purpose": purpose,
        "audience": audience or ["visitor"],
        "primary_action": action,
        "data": [],
        "indexing": indexing,
    }


def routes_for(archetype: str) -> list[dict[str, Any]]:
    public = ["visitor"]
    member = ["member"]
    maps: dict[str, list[dict[str, Any]]] = {
        "marketing": [
            route("/", "Explain the verified product promise and evidence", "Take the primary conversion action", public, "index"),
            route("/contact", "Provide a real contact or next-step route", "Send a request", public, "index"),
        ],
        "saas": [
            route("/", "Orient prospective users and provide product entry", "Open or start the app", public, "index"),
            route("/app", "Prioritize current work and status", "Act on the highest-priority item", member),
            route("/app/items", "Search, filter, and manage the core records", "Open or create a record", member),
            route("/app/items/[id]", "Understand and act on one record", "Complete the primary record action", member),
            route("/app/settings", "Manage account, privacy, and preferences", "Update a setting", member),
        ],
        "utility": [
            route("/", "Let the user perform the useful task immediately", "Submit the primary input", public, "index"),
            route("/result", "Explain, refine, save, copy, or download the result", "Use the result", public, "noindex"),
        ],
        "commerce": [
            route("/", "Enable discovery and communicate trust", "Browse or search products", public, "index"),
            route("/products", "Filter and compare the catalog", "Open a product", public, "index"),
            route("/products/[slug]", "Show complete product, price, seller, delivery, and return information", "Choose a variant and add to cart", public, "index"),
            route("/cart", "Review items and total cost", "Continue to checkout", public, "noindex"),
            route("/checkout", "Collect only necessary purchase information and confirm material terms", "Place the order", public, "noindex"),
            route("/account/orders", "Manage completed orders, returns, and support", "Open an order", member),
        ],
        "affiliate": [
            route("/", "Frame the decision and disclose the commercial model", "Start the decision guide", public, "index"),
            route("/finder", "Collect useful preferences", "Generate recommendations", public, "index"),
            route("/recommendations", "Explain ranked fits, limits, sources, and alternatives", "Compare or visit a retailer", public, "noindex"),
            route("/items/[slug]", "Present sourced facts and current limitations", "Visit a clearly named retailer", public, "index"),
            route("/methodology", "Explain research, scoring, conflicts, and update policy", "Review the method", public, "index"),
        ],
        "marketplace": [
            route("/", "Support trusted discovery across sellers", "Search listings", public, "index"),
            route("/listings", "Filter and compare listings", "Open a listing", public, "index"),
            route("/listings/[slug]", "Show listing, trader, provenance, terms, and reporting", "Start the transaction", public, "index"),
            route("/sell", "Onboard and verify a seller/trader", "Create a listing", ["seller"]),
            route("/account", "Manage transactions, disputes, reports, and identity", "Open a transaction", member),
        ],
        "content": [
            route("/", "Provide topic orientation and high-value entry points", "Search or open a topic", public, "index"),
            route("/search", "Find content with useful zero-result recovery", "Open a result", public, "noindex"),
            route("/topics/[slug]", "Organize a coherent subject collection", "Open an item", public, "index"),
            route("/articles/[slug]", "Deliver sourced, readable, current content", "Continue, save, or follow a cited action", public, "index"),
        ],
        "community": [
            route("/", "Orient visitors and show authentic community activity", "Browse topics or join", public, "index"),
            route("/feed", "Browse and control the content feed", "Open or create a post", member),
            route("/posts/[id]", "Read, respond, report, block, and moderate a thread", "Contribute or take a safety action", public, "index"),
            route("/compose", "Create content with audience and draft clarity", "Publish or save a draft", member),
            route("/settings/privacy", "Control visibility, notifications, export, deletion, and safety", "Update a privacy setting", member),
        ],
        "portal": [
            route("/", "Authenticate and orient authorized users", "Open the work queue", member),
            route("/queue", "Prioritize and process records", "Open the next record", member),
            route("/records/[id]", "Review detail, history, and allowed actions", "Complete the record action", member),
            route("/reports", "Analyze and export authorized operational data", "Run a report", ["lead", "admin"]),
            route("/settings", "Manage profile, security, privacy, and organization settings", "Update a setting", member),
        ],
    }
    result = list(maps[archetype])
    result.extend(
        [
            route("/privacy", "Explain verified data practices and rights", "Open privacy choices or contact", public, "index"),
            route("/terms", "Present verified service terms", "Contact support about a term", public, "index"),
            route("/accessibility", "State verified accessibility status and feedback route", "Report an accessibility issue", public, "index"),
        ]
    )
    return result


def roles_for(archetype: str) -> list[dict[str, str]]:
    roles = [{"id": "visitor", "description": "Unauthenticated or public user"}]
    if archetype not in {"marketing", "affiliate", "content"}:
        roles.append({"id": "member", "description": "Authenticated user acting on their own authorized data"})
    if archetype == "marketplace":
        roles.append({"id": "seller", "description": "Verified seller or trader managing their own listings"})
    if archetype in {"saas", "portal", "community", "marketplace", "commerce"}:
        roles.append({"id": "admin", "description": "Privileged operator with explicit server-side authorization"})
    return roles


def hosting_for(archetype: str) -> str:
    return "hosting" if archetype in {"marketing", "affiliate", "content"} else "app-hosting"


def compliance_flags(archetype: str) -> list[str]:
    flags: dict[str, list[str]] = {
        "marketing": ["public-claims"],
        "saas": ["authentication", "personal-data"],
        "utility": ["input-data-review"],
        "commerce": ["ecommerce", "payments", "consumer-terms"],
        "affiliate": ["affiliate-disclosure", "advertising-claims", "price-freshness"],
        "marketplace": ["marketplace", "trader-traceability", "ugc-moderation", "payments"],
        "content": ["editorial-claims", "copyright"],
        "community": ["ugc-moderation", "minors-assessment", "privacy-controls"],
        "portal": ["authentication", "authorization", "workforce-or-sector-review"],
    }
    return flags[archetype]


def build_blueprint(name: str, brief: str, archetype: str = "auto") -> dict[str, Any]:
    if archetype == "auto":
        archetype = infer_archetype(brief)
    if archetype not in ARCHETYPES:
        raise ValueError(f"Unsupported archetype: {archetype}")

    slug = slugify(name)
    dynamic = hosting_for(archetype) == "app-hosting"
    return {
        "schema_version": "1.0",
        "name": name.strip(),
        "slug": slug,
        "brief": brief.strip(),
        "archetype": archetype,
        "status": "draft",
        "product": {
            "one_liner": brief.strip(),
            "primary_user": "Assumption: define one primary user from the brief and domain research",
            "moment_of_use": "Assumption: mobile-first unless the dominant job is a desktop-dense workspace",
            "job_to_be_done": "Translate the brief into one observable user job",
            "success_action": "Complete the primary journey end to end",
            "success_metric": "Define a product outcome metric after validating the user and business model",
            "non_goals": ["Unrequested live deployment", "Invented claims, credentials, legal facts, or integrations"],
        },
        "assumptions": [
            {
                "statement": "Use a privacy-protective global profile until target markets and data practices are verified",
                "basis": "Safe default for an underspecified globally available app",
                "risk": "medium",
                "reversible": True,
                "validation": "Complete product/legal-profile.yaml with the accountable owner",
                "status": "assumed",
            },
            {
                "statement": "Prioritize responsive mobile behavior while retaining a productive wide layout",
                "basis": "No device context was supplied",
                "risk": "low",
                "reversible": True,
                "validation": "Validate against user research and device analytics",
                "status": "assumed",
            },
        ],
        "routes": routes_for(archetype),
        "flows": [
            {
                "name": "Primary success",
                "type": "primary",
                "steps": ["Enter with clear context", "Perform the primary action", "Receive a persisted or usable result", "Understand the next step"],
                "recovery_states": ["loading", "empty", "no-results", "validation-error", "dependency-error", "unauthorized", "offline", "success"],
            }
        ],
        "roles": roles_for(archetype),
        "entities": [],
        "permissions": [],
        "visual": {
            "thesis": "Create a product-specific visual thesis before building final screens",
            "desired_moods": ["clear", "credible", "distinctive"],
            "forbidden_moods": ["generic template", "decorative without purpose", "derivative"],
            "signature_layout": "Choose one recognizable spatial motif tied to the user's job",
            "typography": "Choose a legible body family and one purposeful display/data relationship with required language coverage",
            "color_logic": "Use semantic neutrals, one primary action color, and accessible status colors",
            "surface_language": "Choose one coherent edge, border, radius, and elevation grammar",
            "asset_treatment": "Use original or cleared assets with a documented consistent treatment",
            "motion_signature": "Use one causal motion behavior with a reduced-motion alternative",
        },
        "content": {
            "source_locale": "en",
            "supported_locales": ["en"],
            "claims_ledger": "product/claims.csv",
            "unverified_claims_allowed": False,
        },
        "assets": {
            "ledger": "product/asset-ledger.csv",
            "required": ["favicon", "app-icon", "open-graph-image"],
            "clearance_status": "unresolved",
        },
        "firebase": {
            "hosting_profile": hosting_for(archetype),
            "environments": ["development", "staging", "production"],
            "region_status": "unresolved",
            "products": ["App Hosting" if dynamic else "Hosting"],
            "auth_model": "Add Authentication only when identity is required; authorize at data/API boundaries",
            "rules_model": "Deny by default; add per-operation ownership/role validation and emulator tests",
            "app_check": "Plan observe-then-enforce rollout when Firebase client resources are enabled",
            "secrets": "Secret Manager/server-only environment; never NEXT_PUBLIC_*",
            "observability": ["error reporting", "route latency/error rate", "cost and usage"],
            "cost_controls": ["budget alerts", "maximum instances/quotas where available"],
        },
        "analytics": {
            "enabled": False,
            "default_consent": "denied",
            "events": [],
        },
        "compliance": {
            "profile": "global-strict",
            "target_markets": [],
            "flags": compliance_flags(archetype),
            "data_categories": [],
            "vendors": ["Google Cloud/Firebase — exact enabled products unresolved"],
            "retention_status": "unresolved",
            "launch_blockers": [
                "Verify legal operator and public contacts",
                "Select enabled markets and minimum audience age",
                "Map data, vendors, retention, deletion/export, regions, and transfers",
                "Obtain legal, security, privacy, and accessibility approval for launch",
            ],
        },
        "acceptance": [
            {"area": "functional", "criterion": "The primary journey works without dead controls or hidden mock behavior", "proof": "Browser end-to-end smoke test"},
            {"area": "responsive", "criterion": "The primary journey works near 320, 375, 768, 1024, and 1440 CSS pixels", "proof": "Rendered visual and interaction checks"},
            {"area": "accessibility", "criterion": "Critical journeys target WCAG 2.2 AA and work by keyboard with reduced motion", "proof": "Automated plus manual keyboard/screen-reader/zoom record"},
            {"area": "security", "criterion": "Data access is deny-first and cross-user/tenant negative cases are tested", "proof": "Emulator Rules and server-authorization tests"},
            {"area": "build", "criterion": "Lint, typecheck, tests, and production build pass from a locked clean install", "proof": "Recorded commands and exit status"},
            {"area": "launch", "criterion": "No unresolved legal/business fact is represented as verified", "proof": "Legal profile, claims ledger, asset ledger, and readiness report"},
        ],
    }


def write_json_atomic(path: Path, payload: dict[str, Any], force: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Human-facing product name")
    parser.add_argument("--brief", required=True, help="Original natural-language app brief")
    parser.add_argument("--archetype", choices=("auto",) + ARCHETYPES, default="auto")
    parser.add_argument("--out", default="product/blueprint.json", help="Output JSON path")
    parser.add_argument("--force", action="store_true", help="Replace an existing blueprint intentionally")
    parser.add_argument("--stdout", action="store_true", help="Print JSON instead of writing a file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_blueprint(args.name, args.brief, args.archetype)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    try:
        write_json_atomic(Path(args.out), payload, args.force)
    except FileExistsError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"Created {Path(args.out).resolve()} ({payload['archetype']}, {payload['firebase']['hosting_profile']})")
    print("Review assumptions, regions, data/permissions, visual DNA, and launch blockers before implementation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
