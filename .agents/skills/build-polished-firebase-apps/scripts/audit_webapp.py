#!/usr/bin/env python3
"""Run a conservative static readiness audit for a Firebase-oriented web app."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {".git", ".next", ".firebase", "node_modules", "dist", "build", "coverage", "out", ".turbo"}
TEXT_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".css", ".scss", ".html", ".md", ".yaml", ".yml", ".rules", ".txt", ".env"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"}
SEVERITY_RANK = {"info": 0, "warn": 1, "error": 2, "critical": 3}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""
    manual_review: bool = False


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def read_text(path: Path) -> str:
    try:
        if path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith(".env")


def relative(root: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def has_any_path(root: Path, candidates: Iterable[str]) -> bool:
    return any((root / candidate).exists() for candidate in candidates)


def audit(root: Path, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    files = list(iter_files(root))
    text_by_path = {path: read_text(path) for path in files if is_text_file(path)}
    combined = "\n".join(text_by_path.values())
    combined_lower = combined.lower()

    def add(severity: str, code: str, message: str, path: Path | None = None, manual: bool = False) -> None:
        findings.append(Finding(severity, code, message, relative(root, path), manual))

    package_path = root / "package.json"
    package: dict = {}
    if not package_path.exists():
        add("error", "repo.package-missing", "package.json is missing; this audit expects a JavaScript/TypeScript web app.", package_path)
    else:
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            add("critical", "repo.package-invalid", f"package.json is not valid JSON: {exc}", package_path)
        scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
        for script_name in ("build", "lint", "typecheck"):
            if script_name not in scripts:
                severity = "warn" if profile == "prototype" else "error"
                add(severity, f"repo.script-{script_name}", f"Missing npm script: {script_name}.", package_path)
        if not has_any_path(root, ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb")):
            severity = "warn" if profile == "prototype" else "error"
            add(severity, "repo.lockfile-missing", "No dependency lockfile found; reproducible production builds require one.")
        if not has_any_path(root, (".env.example", ".env.local.example", "env.example")):
            add("warn", "repo.env-example-missing", "No environment example file documents required configuration.")

    blueprint_path = root / "product" / "blueprint.json"
    if not blueprint_path.exists():
        add("warn" if profile == "prototype" else "error", "product.blueprint-missing", "product/blueprint.json is missing.", blueprint_path)
    else:
        try:
            blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
            required = {"schema_version", "name", "brief", "archetype", "product", "routes", "flows", "visual", "firebase", "compliance", "acceptance"}
            missing = sorted(required - set(blueprint))
            if missing:
                add("error", "product.blueprint-incomplete", f"Blueprint is missing keys: {', '.join(missing)}.", blueprint_path)
            if blueprint.get("firebase", {}).get("region_status") == "unresolved" and profile != "prototype":
                add("error", "firebase.region-unresolved", "Firebase region selection is unresolved; choose locations before provisioning/deployment.", blueprint_path)
            if blueprint.get("compliance", {}).get("launch_blockers") and profile == "global-strict":
                add("error", "legal.launch-blockers", "Blueprint still contains compliance launch blockers; resolve or keep readiness below launch-ready.", blueprint_path, True)
        except (OSError, json.JSONDecodeError) as exc:
            add("critical", "product.blueprint-invalid", f"Blueprint JSON is invalid: {exc}", blueprint_path)

    deps: dict = {}
    if isinstance(package, dict):
        deps.update(package.get("dependencies", {}) or {})
        deps.update(package.get("devDependencies", {}) or {})
    is_next = "next" in deps or has_any_path(root, ("next.config.js", "next.config.mjs", "next.config.ts"))
    if is_next:
        app_dir = root / "src" / "app" if (root / "src" / "app").exists() else root / "app"
        if not app_dir.exists():
            add("error", "next.app-router-missing", "Next.js app directory was not found.", app_dir)
        else:
            required_state_files = {
                "layout": ("layout.tsx", "layout.jsx", "layout.js", "layout.ts"),
                "loading": ("loading.tsx", "loading.jsx", "loading.js", "loading.ts"),
                "error": ("error.tsx", "error.jsx", "error.js", "error.ts"),
                "not-found": ("not-found.tsx", "not-found.jsx", "not-found.js", "not-found.ts"),
            }
            for label, names in required_state_files.items():
                if not any((app_dir / name).exists() for name in names):
                    severity = "warn" if label in {"loading", "not-found"} else "error"
                    add(severity, f"next.{label}-missing", f"Missing App Router {label} boundary/file.", app_dir)
        if "export const metadata" not in combined and "generatemetadata" not in combined_lower:
            add("warn", "next.metadata-missing", "No Next.js metadata export/generator was detected.")
        if not has_any_path(root, ("apphosting.yaml", "firebase.json")):
            add("error" if profile != "prototype" else "warn", "firebase.deploy-config-missing", "No apphosting.yaml or firebase.json deployment configuration was found.")

    if not re.search(r"<html\b[^>]*\blang\s*=", combined, re.IGNORECASE | re.DOTALL):
        add("error", "a11y.lang-missing", "No explicit document language was detected on the html element.")
    if not re.search(r"<main\b", combined, re.IGNORECASE):
        add("error", "a11y.main-missing", "No main landmark was detected.")
    if "skip" not in combined_lower or not ("#main" in combined_lower or "#content" in combined_lower):
        add("warn", "a11y.skip-link-missing", "No clear skip-to-main/content link was detected.")
    if "focus-visible" not in combined_lower:
        add("error", "a11y.focus-visible-missing", "No explicit focus-visible styling was detected.")
    if "prefers-reduced-motion" not in combined_lower:
        add("warn", "a11y.reduced-motion-missing", "No prefers-reduced-motion behavior was detected.")

    for path, text in text_by_path.items():
        if path.name.endswith(".example") or "references" in path.parts or "node_modules" in path.parts:
            continue
        lower = text.lower()
        placeholder_patterns = (
            (r"\blorem ipsum\b", "placeholder.lorem", "Lorem ipsum placeholder copy remains."),
            (r"__app_(?:name|slug|description)__", "placeholder.template-token", "Unresolved scaffold template token remains."),
            (r"href\s*=\s*[\"']#[\"']", "interaction.dead-link", "A href=\"#\" placeholder link remains."),
            (r"\b(?:todo|fixme)\b", "placeholder.todo", "TODO/FIXME marker remains; classify or resolve it before release."),
        )
        for pattern, code, message in placeholder_patterns:
            if re.search(pattern, lower):
                add("warn" if code == "placeholder.todo" else "error", code, message, path)
        if re.search(r"console\.(?:log|debug)\s*\(", text):
            add("warn", "repo.console-debug", "Console debug output remains in source.", path)
        if re.search(r"<img\b(?![^>]*\balt\s*=)[^>]*>", text, re.IGNORECASE | re.DOTALL):
            add("error", "a11y.img-alt-missing", "An img element without an alt attribute was detected.", path)
        if re.search(r"<Image\b(?![^>]*\balt\s*=)[^>]*>", text, re.DOTALL):
            add("error", "a11y.next-image-alt-missing", "A Next.js Image without an alt prop was detected.", path)

    rules_files = [path for path in files if path.suffix == ".rules"]
    uses_firestore_or_storage = any(term in combined_lower for term in ("getfirestore", "collection(", "getstorage", "firebase/firestore", "firebase/storage"))
    if uses_firestore_or_storage and not rules_files:
        add("critical", "firebase.rules-missing", "Firestore/Storage usage was detected without committed .rules files.")
    for rules_path in rules_files:
        text = read_text(rules_path)
        if re.search(r"allow\s+(?:read\s*,\s*write|read|write)\s*:\s*if\s+true\s*;", text, re.IGNORECASE):
            add("critical", "firebase.rules-open", "Security Rules contain unconditional read/write access.", rules_path)
        if re.search(r"match\s+/\{[^}]+=\*\*\}[\s\S]{0,500}allow\s+(?:read\s*,\s*write|read|write)[\s\S]{0,120}request\.auth\s*!=\s*null", text, re.IGNORECASE):
            add("error", "firebase.rules-broad-auth", "Recursive Rules appear to grant broad access to any signed-in user; verify ownership/tenant/operation constraints.", rules_path, True)

    secret_patterns = (
        (r"-----BEGIN (?:RSA |EC |)PRIVATE KEY-----", "secret.private-key"),
        (r"\bAKIA[0-9A-Z]{16}\b", "secret.aws-key"),
        (r"\bghp_[A-Za-z0-9]{30,}\b", "secret.github-token"),
        (r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b", "secret.slack-token"),
        (r"\bsk-(?:live|prod)-[A-Za-z0-9_-]{16,}\b", "secret.api-key"),
    )
    for path, text in text_by_path.items():
        if path.name.endswith(".example") or path.name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}:
            continue
        for pattern, code in secret_patterns:
            if re.search(pattern, text):
                add("critical", code, "A credential-like value was detected in a committed text file.", path)
        if re.search(r"NEXT_PUBLIC_[A-Z0-9_]*(?:SECRET|PRIVATE|PASSWORD|ADMIN|TOKEN)", text):
            add("critical", "secret.public-env", "A secret-like variable name uses NEXT_PUBLIC_ and would be bundled for the browser.", path)

    tracking_markers = ("getanalytics(", "gtag(", "googletagmanager", "adsbygoogle", "posthog", "mixpanel", "amplitude", "fullstory", "hotjar")
    tracking_detected = any(marker in combined_lower for marker in tracking_markers)
    consent_markers = ("analytics_storage", "ad_storage", "setanalyticscollectionenabled", "privacy choices", "consent")
    if tracking_detected and not any(marker in combined_lower for marker in consent_markers):
        add("critical" if profile == "global-strict" else "error", "privacy.tracking-ungated", "Analytics/advertising/tracking code was detected without a clear consent/choice control.", manual=True)

    legal_profile_path = root / "product" / "legal-profile.yaml"
    if profile == "global-strict":
        if not legal_profile_path.exists():
            add("error", "legal.profile-missing", "product/legal-profile.yaml is missing for the global-strict profile.", legal_profile_path)
        else:
            legal_text = read_text(legal_profile_path)
            if re.search(r"legal_name:\s*[\"']?\s*[\"']?\s*$", legal_text, re.MULTILINE):
                add("error", "legal.operator-missing", "Legal operator name is blank; the app cannot be called launch-ready.", legal_profile_path, True)
            if re.search(r"policy_owner:\s*[\"']?\s*[\"']?\s*$", legal_text, re.MULTILINE):
                add("error", "legal.owner-missing", "Policy owner is blank; the app cannot be called launch-ready.", legal_profile_path, True)

    for route_name in ("privacy", "terms", "accessibility"):
        route_pattern = re.compile(rf"(?:href\s*=\s*[\"'][^\"']*{route_name}|/{route_name}\b)", re.IGNORECASE)
        if not route_pattern.search(combined):
            add("warn" if profile == "prototype" else "error", f"legal.{route_name}-surface", f"No clear /{route_name} route or link was detected.")

    public_images = [path for path in files if path.suffix.lower() in IMAGE_SUFFIXES and "public" in path.parts and not re.search(r"(?:favicon|icon|logo)", path.name, re.IGNORECASE)]
    ledger_path = root / "product" / "asset-ledger.csv"
    if public_images and not ledger_path.exists():
        add("error" if profile == "global-strict" else "warn", "assets.ledger-missing", "Public media exists without product/asset-ledger.csv.", ledger_path)
    elif ledger_path.exists() and "Delete this example row before launch" in read_text(ledger_path):
        add("error", "assets.ledger-placeholder", "The asset ledger still contains the template example row.", ledger_path)

    if not findings:
        add("info", "audit.clean-static-pass", "No static findings were produced; manual and runtime checks are still required.")
    else:
        add("info", "audit.manual-required", "Static analysis cannot prove functional behavior, visual quality, accessibility, legal applicability, or secure runtime configuration; complete manual/runtime gates.", manual=True)

    return sorted(findings, key=lambda item: (-SEVERITY_RANK[item.severity], item.code, item.path))


def render_markdown(root: Path, profile: str, findings: list[Finding]) -> str:
    counts = {severity: sum(1 for item in findings if item.severity == severity) for severity in SEVERITY_RANK}
    lines = [
        "# Web app static readiness audit",
        "",
        f"Root: `{root}`  ",
        f"Profile: `{profile}`  ",
        f"Findings: {counts['critical']} critical, {counts['error']} error, {counts['warn']} warning, {counts['info']} info",
        "",
    ]
    for finding in findings:
        location = f" — `{finding.path}`" if finding.path else ""
        manual = " _(manual review)_" if finding.manual_review else ""
        lines.append(f"- **{finding.severity.upper()} · {finding.code}**{location}: {finding.message}{manual}")
    lines.extend(["", "This audit is a backstop, not a certification. Complete build, browser, Emulator, accessibility, security, content, and legal release checks.", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Web app root")
    parser.add_argument("--profile", choices=("prototype", "deploy", "global-strict"), default="global-strict")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--out", help="Write the report to this path instead of stdout")
    parser.add_argument("--fail-on", choices=("never", "warn", "error", "critical"), default="error")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: Not a directory: {root}")
        return 2
    findings = audit(root, args.profile)
    if args.format == "json":
        output = json.dumps({"root": str(root), "profile": args.profile, "findings": [asdict(item) for item in findings]}, indent=2) + "\n"
    else:
        output = render_markdown(root, args.profile, findings)
    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Wrote {out_path}")
    else:
        print(output, end="")

    if args.fail_on == "never":
        return 0
    threshold = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[item.severity] >= threshold for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
