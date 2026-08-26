#!/usr/bin/env python3
"""Copy the bundled Next.js/Firebase foundation into a new, empty target directory."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from create_blueprint import ARCHETYPES, build_blueprint, slugify
from generate_theme import build_theme, render_css


PRODUCT_TO_THEME = {
    "marketing": "editorial",
    "saas": "precision",
    "utility": "calm-data",
    "commerce": "archival",
    "affiliate": "editorial",
    "marketplace": "civic",
    "content": "editorial",
    "community": "playful",
    "portal": "precision",
}


def replace_tokens(root: Path, replacements: dict[str, str]) -> None:
    text_suffixes = {".ts", ".tsx", ".js", ".mjs", ".json", ".css", ".md", ".yaml", ".yml", ".rules", ".example"}
    for path in root.rglob("*"):
        if not path.is_file() or (path.suffix not in text_suffixes and not path.name.startswith(".")):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        changed = text
        for token, value in replacements.items():
            changed = changed.replace(token, value)
        if changed != text:
            path.write_text(changed, encoding="utf-8")


def scaffold(name: str, target: Path, archetype: str, brief: str, install: bool = False) -> Path:
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    assets_dir = skill_dir / "assets"
    template_dir = assets_dir / "firebase-nextjs-foundation"
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Bundled foundation is missing: {template_dir}")

    target = target.resolve()
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"Refusing to write into non-empty target: {target}")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_dir, target, dirs_exist_ok=True)

    slug = slugify(name)
    replace_tokens(
        target,
        {
            "__APP_NAME__": name,
            "__APP_SLUG__": slug,
            "__APP_DESCRIPTION__": brief,
        },
    )

    product_dir = target / "product"
    product_dir.mkdir(exist_ok=True)
    blueprint = build_blueprint(name, brief, archetype)
    blueprint["firebase"]["hosting_profile"] = "app-hosting"
    blueprint["firebase"]["products"] = ["App Hosting"]
    blueprint["assumptions"].append(
        {
            "statement": "Use the bundled Next.js foundation on Firebase App Hosting",
            "basis": "This scaffold is the dynamic Next.js/App Hosting profile",
            "risk": "medium",
            "reversible": True,
            "validation": "Switch to a static export and Firebase Hosting when all routes are static and the simpler profile is preferable",
            "status": "assumed",
        }
    )
    (product_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copy2(assets_dir / "legal-profile.template.yaml", product_dir / "legal-profile.yaml")
    ledger_header = (assets_dir / "asset-ledger.template.csv").read_text(encoding="utf-8").splitlines()[0]
    (product_dir / "asset-ledger.csv").write_text(ledger_header + "\n", encoding="utf-8")
    (product_dir / "compliance.md").write_text(
        "# Compliance readiness\n\n"
        "Profile: global-strict preview mode\n\n"
        "## Launch blockers\n\n"
        "- Verify legal operator, contacts, target markets, audience age, business model, and policy ownership.\n"
        "- Map every data category, purpose, basis, vendor, region, transfer, retention, export, and deletion path.\n"
        "- Configure and test consent/opt-out behavior before enabling optional Analytics, ads, or third-party tags.\n"
        "- Obtain named legal, privacy, security, and accessibility approval before claiming launch-ready.\n\n"
        "Do not publish generated legal text as approved advice.\n",
        encoding="utf-8",
    )

    theme_archetype = PRODUCT_TO_THEME[archetype]
    theme = build_theme(name, theme_archetype)
    (target / "src" / "app" / "theme.generated.css").write_text(render_css(theme, "both"), encoding="utf-8")

    if install:
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError("npm was not found; rerun without --install or install Node/npm.")
        install_command = [npm, "ci"] if (target / "package-lock.json").is_file() else [npm, "install"]
        subprocess.run(install_command, cwd=target, check=True)

    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Human-facing product name")
    parser.add_argument("--target", required=True, help="New or empty destination directory")
    parser.add_argument("--archetype", choices=ARCHETYPES, default="utility")
    parser.add_argument("--brief", help="Original brief; a neutral scaffold brief is used when omitted")
    parser.add_argument("--install", action="store_true", help="Run npm install after copying the foundation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    brief = args.brief or f"Build {args.name} as a complete {args.archetype} web application."
    try:
        target = scaffold(args.name.strip(), Path(args.target), args.archetype, brief.strip(), args.install)
    except (FileExistsError, FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"Created Firebase/Next.js foundation at {target}")
    print("No Firebase project, paid resource, or live deployment was created.")
    if args.install:
        print("Dependencies installed from the lockfile.")
        print("Next: review product/blueprint.json and product/legal-profile.yaml, replace the foundation page, then run npm run build.")
    else:
        print("Next: review product/blueprint.json and product/legal-profile.yaml, replace the foundation page, then run npm ci && npm run build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
