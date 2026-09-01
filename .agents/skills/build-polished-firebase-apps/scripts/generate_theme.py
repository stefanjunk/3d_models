#!/usr/bin/env python3
"""Generate an accessible semantic CSS-token starting point with a stable fingerprint."""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


STYLES: dict[str, dict[str, Any]] = {
    "editorial": {"hues": (6, 32), "canvas_hue": 42, "sat": 70, "radius": "0.35rem", "display": 'Georgia, "Times New Roman", serif', "body": 'Inter, ui-sans-serif, system-ui, sans-serif', "shadow": "0 14px 45px hsl(25 20% 15% / 0.10)"},
    "precision": {"hues": (198, 232), "canvas_hue": 218, "sat": 78, "radius": "0.45rem", "display": 'Inter, ui-sans-serif, system-ui, sans-serif', "body": 'Inter, ui-sans-serif, system-ui, sans-serif', "shadow": "0 10px 34px hsl(220 40% 16% / 0.11)"},
    "warm": {"hues": (18, 48), "canvas_hue": 38, "sat": 72, "radius": "1.1rem", "display": 'Georgia, "Times New Roman", serif', "body": 'Avenir, "Segoe UI", ui-sans-serif, sans-serif', "shadow": "0 18px 42px hsl(28 30% 25% / 0.12)"},
    "civic": {"hues": (198, 218), "canvas_hue": 210, "sat": 70, "radius": "0.25rem", "display": '"Source Serif 4", Georgia, serif', "body": '"Source Sans 3", "Segoe UI", sans-serif', "shadow": "0 8px 24px hsl(210 30% 15% / 0.10)"},
    "playful": {"hues": (255, 345), "canvas_hue": 54, "sat": 72, "radius": "1.4rem", "display": '"Arial Rounded MT Bold", Inter, ui-sans-serif, sans-serif', "body": 'Inter, ui-sans-serif, system-ui, sans-serif', "shadow": "0 16px 0 hsl(220 18% 18% / 0.10)"},
    "technical": {"hues": (152, 194), "canvas_hue": 212, "sat": 68, "radius": "0.2rem", "display": '"IBM Plex Mono", "SFMono-Regular", Consolas, monospace', "body": 'Inter, ui-sans-serif, system-ui, sans-serif', "shadow": "0 0 0 1px hsl(190 35% 28% / 0.18), 0 16px 40px hsl(210 40% 8% / 0.16)"},
    "archival": {"hues": (30, 68), "canvas_hue": 48, "sat": 66, "radius": "0.15rem", "display": '"Bodoni 72", Didot, Georgia, serif', "body": '"Helvetica Neue", Arial, sans-serif', "shadow": "0 10px 28px hsl(35 25% 18% / 0.10)"},
    "cinematic": {"hues": (332, 360), "canvas_hue": 225, "sat": 74, "radius": "0.65rem", "display": '"Helvetica Neue", Arial, sans-serif', "body": 'Inter, ui-sans-serif, system-ui, sans-serif', "shadow": "0 28px 70px hsl(225 50% 5% / 0.30)"},
    "organic": {"hues": (86, 148), "canvas_hue": 62, "sat": 55, "radius": "1.2rem", "display": 'Georgia, "Times New Roman", serif', "body": 'Avenir, "Segoe UI", sans-serif', "shadow": "0 20px 55px hsl(92 30% 15% / 0.13)"},
    "calm-data": {"hues": (174, 226), "canvas_hue": 205, "sat": 62, "radius": "0.7rem", "display": 'Inter, ui-sans-serif, system-ui, sans-serif', "body": 'Inter, ui-sans-serif, system-ui, sans-serif', "shadow": "0 14px 38px hsl(210 35% 14% / 0.10)"},
    "quiet-luxury": {"hues": (22, 50), "canvas_hue": 42, "sat": 48, "radius": "0.1rem", "display": 'Didot, "Bodoni 72", Georgia, serif', "body": '"Helvetica Neue", Arial, sans-serif', "shadow": "0 24px 64px hsl(32 18% 10% / 0.14)"},
    "brutal": {"hues": (0, 359), "canvas_hue": 56, "sat": 86, "radius": "0rem", "display": 'Impact, "Arial Narrow", ui-sans-serif, sans-serif', "body": 'Arial, ui-sans-serif, sans-serif', "shadow": "0.35rem 0.35rem 0 hsl(220 18% 12%)"},
}


def stable_fraction(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def select_hue(name: str, archetype: str, seed: str = "") -> int:
    low, high = STYLES[archetype]["hues"]
    fraction = stable_fraction(f"{name}|{archetype}|{seed}")
    return int(round(low + (high - low) * fraction)) % 360


def hsl_rgb(hue: float, saturation: float, lightness: float) -> tuple[float, float, float]:
    return colorsys.hls_to_rgb((hue % 360) / 360.0, lightness / 100.0, saturation / 100.0)


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (channel(value) for value in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: tuple[float, float, float], second: tuple[float, float, float]) -> float:
    light = max(relative_luminance(first), relative_luminance(second))
    dark = min(relative_luminance(first), relative_luminance(second))
    return (light + 0.05) / (dark + 0.05)


def choose_on_color(hue: int, saturation: int, lightness: int) -> str:
    background = hsl_rgb(hue, saturation, lightness)
    white = (1.0, 1.0, 1.0)
    near_black = hsl_rgb(220, 18, 10)
    return "hsl(0 0% 100%)" if contrast_ratio(background, white) >= contrast_ratio(background, near_black) else "hsl(220 18% 10%)"


def token_set(name: str, archetype: str, seed: str = "", dark: bool = False) -> dict[str, str]:
    style = STYLES[archetype]
    hue = select_hue(name, archetype, seed)
    saturation = int(style["sat"])
    primary_lightness = 64 if dark else 38
    canvas_hue = int(style["canvas_hue"])

    if dark:
        canvas = f"hsl({canvas_hue} 20% 8%)"
        surface = f"hsl({canvas_hue} 18% 11%)"
        raised = f"hsl({canvas_hue} 16% 15%)"
        text = f"hsl({canvas_hue} 18% 94%)"
        muted = f"hsl({canvas_hue} 10% 69%)"
        border = f"hsl({canvas_hue} 12% 26%)"
        shadow = "0 18px 55px hsl(220 50% 2% / 0.38)"
    else:
        canvas = f"hsl({canvas_hue} 32% 97%)"
        surface = f"hsl({canvas_hue} 26% 99%)"
        raised = "hsl(0 0% 100%)"
        text = f"hsl({canvas_hue} 22% 12%)"
        muted = f"hsl({canvas_hue} 10% 42%)"
        border = f"hsl({canvas_hue} 14% 82%)"
        shadow = str(style["shadow"])

    primary = f"hsl({hue} {saturation}% {primary_lightness}%)"
    return {
        "color-canvas": canvas,
        "color-surface": surface,
        "color-surface-raised": raised,
        "color-text": text,
        "color-text-muted": muted,
        "color-border": border,
        "color-primary": primary,
        "color-on-primary": choose_on_color(hue, saturation, primary_lightness),
        "color-focus": f"hsl({hue} {min(92, saturation + 8)}% {70 if dark else 42}%)",
        "color-success": "hsl(146 58% 36%)" if not dark else "hsl(146 54% 61%)",
        "color-warning": "hsl(35 88% 42%)" if not dark else "hsl(42 94% 66%)",
        "color-danger": "hsl(2 72% 46%)" if not dark else "hsl(2 82% 68%)",
        "color-info": "hsl(207 78% 42%)" if not dark else "hsl(207 86% 68%)",
        "font-display": str(style["display"]),
        "font-body": str(style["body"]),
        "radius-control": str(style["radius"]),
        "radius-panel": "calc(var(--radius-control) * 1.35)",
        "shadow-raised": shadow,
        "space-1": "0.25rem",
        "space-2": "0.5rem",
        "space-3": "0.75rem",
        "space-4": "1rem",
        "space-6": "1.5rem",
        "space-8": "2rem",
        "space-12": "3rem",
        "space-16": "4rem",
        "content-prose": "68ch",
        "content-wide": "76rem",
        "motion-fast": "140ms",
        "motion-base": "220ms",
        "motion-slow": "380ms",
        "ease-standard": "cubic-bezier(.2, .8, .2, 1)",
    }


def build_theme(name: str, archetype: str, seed: str = "") -> dict[str, Any]:
    if archetype not in STYLES:
        raise ValueError(f"Unsupported theme archetype: {archetype}")
    hue = select_hue(name, archetype, seed)
    signature = hashlib.sha256(f"{name}|{archetype}|{seed}".encode("utf-8")).hexdigest()[:12]
    return {
        "metadata": {
            "name": name,
            "archetype": archetype,
            "signature": signature,
            "accent_hue": hue,
            "note": "Generated starting point; tune against the product, rendered screens, language coverage, and accessibility tests.",
        },
        "light": token_set(name, archetype, seed, False),
        "dark": token_set(name, archetype, seed, True),
    }


def css_block(selector: str, tokens: dict[str, str], indent: str = "") -> str:
    lines = [f"{indent}{selector} {{"]
    lines.extend(f"{indent}  --{key}: {value};" for key, value in tokens.items())
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def render_css(theme: dict[str, Any], mode: str = "both") -> str:
    metadata = theme["metadata"]
    lines = [
        "/* Generated semantic theme starting point.",
        f"   Product: {metadata['name']}",
        f"   Archetype: {metadata['archetype']}",
        f"   Signature: {metadata['signature']}",
        "   Tune this system against the actual product and rendered UI. */",
        "",
    ]
    if mode == "light":
        lines.append(css_block(":root", theme["light"]))
    elif mode == "dark":
        lines.append(css_block(":root", theme["dark"]))
    else:
        lines.append(css_block(":root", theme["light"]))
        lines.extend(["", css_block(".dark", theme["dark"]), "", "@media (prefers-color-scheme: dark) {", css_block(":root:not(.light)", theme["dark"], "  "), "}"])
    lines.extend(
        [
            "",
            "@media (prefers-reduced-motion: reduce) {",
            "  :root {",
            "    --motion-fast: 1ms;",
            "    --motion-base: 1ms;",
            "    --motion-slow: 1ms;",
            "  }",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def write_atomic(path: Path, text: str, force: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Product name used for the stable fingerprint")
    parser.add_argument("--archetype", choices=tuple(STYLES), default="calm-data")
    parser.add_argument("--seed", default="", help="Optional additional stable variation seed")
    parser.add_argument("--mode", choices=("light", "dark", "both"), default="both")
    parser.add_argument("--format", choices=("css", "json"), default="css")
    parser.add_argument("--out", help="Output path; omit to print to stdout")
    parser.add_argument("--force", action="store_true", help="Replace an existing output intentionally")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    theme = build_theme(args.name, args.archetype, args.seed)
    output = render_css(theme, args.mode) if args.format == "css" else json.dumps(theme, indent=2, ensure_ascii=False) + "\n"
    if not args.out:
        print(output, end="")
        return 0
    try:
        write_atomic(Path(args.out), output, args.force)
    except FileExistsError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"Created {Path(args.out).resolve()} (signature {theme['metadata']['signature']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
