#!/usr/bin/env python3
"""Engineering sanity checks and diagrams for OpenQuad CF5.

The calculations are deliberately transparent and conservative in wording.
They are not a structural certification and do not replace coupon, proof-load,
vibration, propulsion, or flight tests.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
FIG = OUT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

# Geometry - keep synchronized with CAD/openquad_cf5.scad.
WHEELBASE_MM = 230.0
MOTOR_RADIUS_MM = WHEELBASE_MM / 2.0
PROP_DIAMETER_MM = 129.7
ARM_OUTER_MM = 10.0
ARM_INNER_MM = 8.0
ARM_INNER_RADIUS_MM = 12.0
ARM_LENGTH_MM = MOTOR_RADIUS_MM - ARM_INNER_RADIUS_MM
HUB_SIZE_MM = 86.0
DECK_LENGTH_MM = 80.0
DECK_WIDTH_MM = 52.0
DECK_HEIGHT_MM = 41.0
DECK_THICKNESS_MM = 3.0
BATTERY_LENGTH_MM = 74.0
BATTERY_WIDTH_MM = 33.0
BATTERY_HEIGHT_MM = 31.0
DECK_HOLE_X_MM = 32.0
DECK_HOLE_Y_MM = 20.0
SADDLE_OVERLAP_MM = 28.0
SADDLE_WIDTH_MM = 26.0
HUB_OVERLAP_MM = HUB_SIZE_MM / 2.0 - ARM_INNER_RADIUS_MM
FC_HOLE_SPACING_MM = 30.5
ARM_CLEARANCE_MM = 0.25
MOTOR_PATTERN_MM = 16.0
MOTOR_HOLE_MM = 3.25
CLAMP_HOLE_MM = 3.4
MOTOR_CLAMP_X_MM = (-22.0, -16.0)
MOTOR_CLAMP_Y_MM = (-9.0, 9.0)

# Material/load assumptions - illustrative only.
CF_DENSITY_G_MM3 = 1.55e-3
CF_E_MPA_ASSUMED = 60_000.0
ILLUSTRATIVE_TIP_LOAD_N = 15.0
PRINTED_MASS_NOMINAL_G = 123.0  # pre-slicer range is recorded below


def point_to_rect_distance(px: float, py: float, half_x: float, half_y: float) -> float:
    dx = max(abs(px) - half_x, 0.0)
    dy = max(abs(py) - half_y, 0.0)
    return math.hypot(dx, dy)


def calculate() -> dict:
    adjacent_motor_distance = WHEELBASE_MM / math.sqrt(2.0)
    adjacent_prop_gap = adjacent_motor_distance - PROP_DIAMETER_MM
    prop_radius = PROP_DIAMETER_MM / 2.0
    deck_prop_clearance = (
        point_to_rect_distance(MOTOR_RADIUS_MM, 0.0, DECK_LENGTH_MM / 2.0, DECK_WIDTH_MM / 2.0)
        - prop_radius
    )
    hub_prop_clearance = MOTOR_RADIUS_MM - HUB_SIZE_MM / 2.0 - prop_radius

    motor_points = [
        (x, y)
        for x in (-MOTOR_PATTERN_MM / 2.0, MOTOR_PATTERN_MM / 2.0)
        for y in (-MOTOR_PATTERN_MM / 2.0, MOTOR_PATTERN_MM / 2.0)
    ]
    clamp_points = [(x, y) for x in MOTOR_CLAMP_X_MM for y in MOTOR_CLAMP_Y_MM]
    min_motor_clamp_web = min(
        math.hypot(mx - cx, my - cy) - MOTOR_HOLE_MM / 2.0 - CLAMP_HOLE_MM / 2.0
        for mx, my in motor_points
        for cx, cy in clamp_points
    )
    channel_half_width = (ARM_OUTER_MM + ARM_CLEARANCE_MM) / 2.0
    min_channel_clamp_web = min(
        abs(y) - CLAMP_HOLE_MM / 2.0 - channel_half_width for y in MOTOR_CLAMP_Y_MM
    )
    min_outer_clamp_web = min(
        SADDLE_WIDTH_MM / 2.0 - abs(y) - CLAMP_HOLE_MM / 2.0 for y in MOTOR_CLAMP_Y_MM
    )

    tube_area = ARM_OUTER_MM**2 - ARM_INNER_MM**2
    carbon_mass = 4.0 * tube_area * ARM_LENGTH_MM * CF_DENSITY_G_MM3
    inertia = (ARM_OUTER_MM**4 - ARM_INNER_MM**4) / 12.0
    cantilever_length = MOTOR_RADIUS_MM - HUB_SIZE_MM / 2.0
    root_moment = ILLUSTRATIVE_TIP_LOAD_N * cantilever_length
    bending_stress = root_moment * (ARM_OUTER_MM / 2.0) / inertia
    tip_deflection = (
        ILLUSTRATIVE_TIP_LOAD_N
        * cantilever_length**3
        / (3.0 * CF_E_MPA_ASSUMED * inertia)
    )

    mass_items = {
        "CFK-Rohre (4 x 103 mm)": carbon_mass,
        "FDM-Bauteile, Vorschaetzung": PRINTED_MASS_NOMINAL_G,
        "Schrauben, Abstandshalter, Gurte": 35.0,
        "4 Motoren": 4.0 * 33.5,
        "FC/ESC-Stack (SpeedyBee F405 V5, Herstellerangabe)": 27.2,
        "4S-1300-mAh-Akku": 151.0,
        "Propeller": 4.0 * 3.6,
        "ELRS-Empfaenger": 2.2,
        "Autonomer Buzzer": 5.0,
        "Kabel, XT60, Schutzschlauch": 25.0,
    }
    takeoff_mass = sum(mass_items.values())
    usable_energy_wh = 0.80 * 14.8 * 1.3
    flight_time_min = {
        "at_120_W": usable_energy_wh / 120.0 * 60.0,
        "at_160_W": usable_energy_wh / 160.0 * 60.0,
    }

    # A check passing means only that the chosen numerical design rule is met.
    checks = [
        {
            "name": "Abstand benachbarter Propellerspitzen",
            "value_mm": adjacent_prop_gap,
            "limit_mm": 20.0,
            "pass": adjacent_prop_gap >= 20.0,
        },
        {
            "name": "Propellerabstand zum Akkudeck (XY-Huelle)",
            "value_mm": deck_prop_clearance,
            "limit_mm": 8.0,
            "pass": deck_prop_clearance >= 8.0,
        },
        {
            "name": "Propellerabstand zur Nabenplatte (XY-Huelle)",
            "value_mm": hub_prop_clearance,
            "limit_mm": 5.0,
            "pass": hub_prop_clearance >= 5.0,
        },
        {
            "name": "Einspannlaenge Arm in Zentralknoten",
            "value_mm": HUB_OVERLAP_MM,
            "limit_mm": 25.0,
            "pass": HUB_OVERLAP_MM >= 25.0,
        },
        {
            "name": "Einspannlaenge Arm im Motorhalter",
            "value_mm": SADDLE_OVERLAP_MM,
            "limit_mm": 25.0,
            "pass": SADDLE_OVERLAP_MM >= 25.0,
        },
        {
            "name": "Akkuschrauben ausserhalb 74 x 33 mm Grundflaeche",
            "value_mm": DECK_HOLE_Y_MM - BATTERY_WIDTH_MM / 2.0,
            "limit_mm": 1.7,
            "pass": DECK_HOLE_Y_MM - BATTERY_WIDTH_MM / 2.0 >= 1.7,
        },
        {
            "name": "Mindeststeg Motorloch zu Pod-Klemmloch",
            "value_mm": min_motor_clamp_web,
            "limit_mm": 2.0,
            "pass": min_motor_clamp_web >= 2.0,
        },
        {
            "name": "Mindeststeg Pod-Klemmloch zu Rohrkanal",
            "value_mm": min_channel_clamp_web,
            "limit_mm": 2.0,
            "pass": min_channel_clamp_web >= 2.0,
        },
        {
            "name": "Mindeststeg Pod-Klemmloch zur Aussenkante",
            "value_mm": min_outer_clamp_web,
            "limit_mm": 2.0,
            "pass": min_outer_clamp_web >= 2.0,
        },
    ]

    return {
        "status": "PRELIMINARY_NOT_FLIGHT_PROVEN",
        "geometry": {
            "wheelbase_mm": WHEELBASE_MM,
            "motor_radius_mm": MOTOR_RADIUS_MM,
            "adjacent_motor_distance_mm": adjacent_motor_distance,
            "prop_diameter_mm": PROP_DIAMETER_MM,
            "adjacent_prop_tip_gap_mm": adjacent_prop_gap,
            "deck_prop_xy_clearance_mm": deck_prop_clearance,
            "hub_prop_xy_clearance_mm": hub_prop_clearance,
            "arm_cut_length_each_mm": ARM_LENGTH_MM,
            "hub_arm_overlap_mm": HUB_OVERLAP_MM,
            "motor_saddle_overlap_mm": SADDLE_OVERLAP_MM,
            "motor_hole_to_clamp_hole_min_web_mm": min_motor_clamp_web,
            "clamp_hole_to_channel_min_web_mm": min_channel_clamp_web,
            "clamp_hole_to_outer_edge_min_web_mm": min_outer_clamp_web,
        },
        "mass": {
            "items_g": mass_items,
            "estimated_takeoff_mass_g": takeoff_mass,
            "pre_slicer_printed_mass_range_g": [110.0, 135.0],
            "uncertainty_note": "Re-slice with the exact material profile and weigh every part.",
        },
        "energy": {
            "usable_energy_wh_assuming_80_percent": usable_energy_wh,
            "illustrative_hover_power_w": [120.0, 160.0],
            "illustrative_flight_time_min": flight_time_min,
        },
        "arm_beam_screening": {
            "warning": "Illustrative tube-only screening; clamps, fatigue and resonance are not covered.",
            "assumed_tip_load_n": ILLUSTRATIVE_TIP_LOAD_N,
            "assumed_longitudinal_modulus_mpa": CF_E_MPA_ASSUMED,
            "unsupported_length_mm": cantilever_length,
            "second_moment_mm4": inertia,
            "root_bending_stress_mpa": bending_stress,
            "tip_deflection_mm": tip_deflection,
        },
        "checks": checks,
        "all_numeric_design_rules_pass": all(c["pass"] for c in checks),
    }


def draw_top_view(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 8.2), dpi=190)
    ax.set_facecolor("#f7f7f4")
    orange = "#f07c28"
    dark = "#20252b"
    cyan = "#20a7c9"

    # Props first so structure remains legible.
    for mx, my in [(MOTOR_RADIUS_MM, 0), (0, MOTOR_RADIUS_MM), (-MOTOR_RADIUS_MM, 0), (0, -MOTOR_RADIUS_MM)]:
        ax.add_patch(Circle((mx, my), PROP_DIAMETER_MM / 2, facecolor=cyan, edgecolor=cyan,
                            alpha=0.10, linewidth=1.2, linestyle="--"))

    for angle in [0, 90, 180, 270]:
        a = math.radians(angle)
        transform = plt.matplotlib.transforms.Affine2D().rotate_around(0, 0, a) + ax.transData
        arm = Rectangle((ARM_INNER_RADIUS_MM, -ARM_OUTER_MM / 2), ARM_LENGTH_MM, ARM_OUTER_MM,
                        facecolor=dark, edgecolor="#050607", linewidth=1.0, transform=transform)
        ax.add_patch(arm)

    ax.add_patch(FancyBboxPatch((-HUB_SIZE_MM / 2, -HUB_SIZE_MM / 2), HUB_SIZE_MM, HUB_SIZE_MM,
                                boxstyle="round,pad=0,rounding_size=8", facecolor=orange,
                                edgecolor="#a54711", linewidth=1.4, alpha=0.91))
    ax.add_patch(FancyBboxPatch((-DECK_LENGTH_MM / 2, -DECK_WIDTH_MM / 2), DECK_LENGTH_MM, DECK_WIDTH_MM,
                                boxstyle="round,pad=0,rounding_size=5", facecolor="#ffd5a8",
                                edgecolor="#9f5c1d", linewidth=1.2, alpha=0.87))
    ax.add_patch(Rectangle((-BATTERY_LENGTH_MM / 2, -BATTERY_WIDTH_MM / 2), BATTERY_LENGTH_MM,
                           BATTERY_WIDTH_MM, facecolor="#606b75", edgecolor="#24282d", alpha=0.75))

    for mx, my in [(MOTOR_RADIUS_MM, 0), (0, MOTOR_RADIUS_MM), (-MOTOR_RADIUS_MM, 0), (0, -MOTOR_RADIUS_MM)]:
        ax.add_patch(Circle((mx, my), 18, facecolor="#c8ccd0", edgecolor="#3e454c", linewidth=1.2))
        ax.add_patch(Circle((mx, my), 3, facecolor="#33383d", edgecolor="none"))

    front = MOTOR_RADIUS_MM * 0.83 / math.sqrt(2)
    ax.add_patch(FancyArrowPatch((0, 0), (front, front), arrowstyle="-|>", mutation_scale=18,
                                 linewidth=2.2, color="#7b1fa2"))
    ax.text(front * 0.70, front * 0.70 + 8, "FRONT", color="#7b1fa2", weight="bold", fontsize=9)

    ax.annotate("230 mm Motor-zu-Motor", xy=(-MOTOR_RADIUS_MM, -142), xytext=(MOTOR_RADIUS_MM, -142),
                ha="center", va="center", arrowprops=dict(arrowstyle="<->", color="#4b535a"),
                color="#4b535a", fontsize=9)
    ax.text(0, 154, "OpenQuad CF5 - Draufsicht und Propellerhuellen", ha="center", fontsize=13,
            weight="bold", color="#20252b")
    ax.text(0, -161, "CFK 10 x 10 x 1 mm | vier einzeln wechselbare Arme | Akku 74 x 33 mm",
            ha="center", fontsize=8.5, color="#50565c")

    ax.set_xlim(-170, 170)
    ax.set_ylim(-170, 170)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def draw_side_view(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.7), dpi=190)
    ax.set_facecolor("#f7f7f4")
    # Side schematic, deliberately not a tolerance drawing.
    ax.add_patch(Rectangle((-43, 0), 86, 3, facecolor="#f07c28", edgecolor="#a54711"))
    ax.add_patch(Rectangle((-115, 3), 230, 10, facecolor="#20252b", edgecolor="#050607"))
    ax.add_patch(Rectangle((-43, 13), 86, 3, facecolor="#ff9b43", edgecolor="#a54711"))
    ax.add_patch(Rectangle((-19.5, 19), 39, 4.5, facecolor="#278f54", edgecolor="#1c5737"))
    ax.add_patch(Rectangle((-19.5, 27), 39, 4.5, facecolor="#376fb5", edgecolor="#23466f"))
    for x in [-32, 32]:
        ax.add_patch(Rectangle((x - 2.5, 16), 5, 25, facecolor="#b5b8bb", edgecolor="#73787d"))
    ax.add_patch(Rectangle((-40, 41), 80, 3, facecolor="#ffb56d", edgecolor="#9f5c1d"))
    ax.add_patch(FancyBboxPatch((-37, 44), 74, 31, boxstyle="round,pad=0,rounding_size=2.5",
                                facecolor="#606b75", edgecolor="#24282d"))
    # motor/prop plane at both ends
    for x in [-115, 115]:
        ax.add_patch(Rectangle((x - 18, 12.85), 36, 3.6, facecolor="#ff9b43", edgecolor="#a54711"))
        ax.add_patch(Rectangle((x - 14, 16.45), 28, 17, facecolor="#c8ccd0", edgecolor="#3e454c"))
        ax.plot([x - 64.85, x + 64.85], [45.45, 45.45], color="#20a7c9", lw=2.0, alpha=0.8)

    ax.annotate("75 mm geschaetzte Gesamthoehe", xy=(153, 0), xytext=(153, 75),
                arrowprops=dict(arrowstyle="<->", color="#4b535a"), ha="center", va="center",
                fontsize=8.5, color="#4b535a")
    ax.text(0, 88, "OpenQuad CF5 - schematischer Seitenaufbau", ha="center", fontsize=13,
            weight="bold", color="#20252b")
    ax.text(0, -8, "Nicht als Toleranzzeichnung verwenden; Propellerebene und Akku muessen real vermessen werden.",
            ha="center", fontsize=8.5, color="#50565c")
    ax.set_xlim(-175, 175)
    ax.set_ylim(-14, 94)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def draw_motor_pod_detail(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.4, 5.4), dpi=190)
    ax.set_facecolor("#f7f7f4")
    orange = "#f07c28"
    dark = "#20252b"
    purple = "#7b1fa2"
    blue = "#187a9a"

    # Projected motor plate: 36-mm disk plus 28 x 26-mm tongue.
    ax.add_patch(Rectangle((-28, -13), 28, 26, facecolor="#ffc083", edgecolor="#a54711", lw=1.4))
    ax.add_patch(Circle((0, 0), 18, facecolor=orange, edgecolor="#a54711", lw=1.5))
    # Carbon-channel projection in the saddle underneath.
    ax.add_patch(Rectangle((-28, -(ARM_OUTER_MM + ARM_CLEARANCE_MM) / 2), 28,
                           ARM_OUTER_MM + ARM_CLEARANCE_MM, facecolor=dark,
                           edgecolor="#050607", alpha=0.68, linestyle="--"))

    ax.add_patch(Circle((0, 0), 4, facecolor="#f7f7f4", edgecolor=dark, lw=1.2))
    for x, y in [(x, y) for x in (-8, 8) for y in (-8, 8)]:
        ax.add_patch(Circle((x, y), MOTOR_HOLE_MM / 2, facecolor="#f7f7f4", edgecolor=blue, lw=1.5))
    for x, y in [(x, y) for x in MOTOR_CLAMP_X_MM for y in MOTOR_CLAMP_Y_MM]:
        ax.add_patch(Circle((x, y), CLAMP_HOLE_MM / 2, facecolor="#f7f7f4", edgecolor=purple, lw=1.5))

    ax.annotate("16 x 16 mm Motor", xy=(8, 8), xytext=(13, 18), color=blue, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=blue, lw=1.2))
    ax.annotate("4 x M3 Pod-Klemmung", xy=(-16, 9), xytext=(-30, 19), color=purple, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=purple, lw=1.2))
    ax.annotate("10,25-mm-Rohrkanal", xy=(-24, 0), xytext=(-31, -17), color=dark, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=dark, lw=1.2))
    ax.text(-5, -25.0, "Mindeststege: Loch/Loch 4,74 mm | Loch/Kanal 2,17 mm | Loch/Aussenkante 2,30 mm",
            ha="center", fontsize=8.2, color="#50565c",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#eef0ef", edgecolor="#d7dadd"))
    ax.text(-5, 24, "OpenQuad CF5 - korrigierte Motorpod-Lochlage", ha="center", fontsize=13,
            weight="bold", color=dark)

    ax.set_xlim(-33, 22)
    ax.set_ylim(-29, 27)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0.4)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def write_markdown(data: dict, path: Path) -> None:
    geo = data["geometry"]
    mass = data["mass"]
    beam = data["arm_beam_screening"]
    lines = [
        "# OpenQuad CF5 - automatischer Plausibilitaetsbericht",
        "",
        "**Status:** PRELIMINARY / NOT FLIGHT PROVEN. Ein PASS bestaetigt nur die jeweilige",
        "numerische Entwurfsregel, nicht die Flugsicherheit oder Bauteilfestigkeit.",
        "",
        "## Geometrie",
        "",
        f"- Motorabstand diagonal: {geo['wheelbase_mm']:.1f} mm",
        f"- Schnittlaenge je CFK-Arm: {geo['arm_cut_length_each_mm']:.1f} mm",
        f"- Freiraum benachbarter Propellerspitzen: {geo['adjacent_prop_tip_gap_mm']:.1f} mm",
        f"- XY-Freiraum Propeller/Akkudeck: {geo['deck_prop_xy_clearance_mm']:.1f} mm",
        f"- Einspannung Zentralknoten / Motorhalter: {geo['hub_arm_overlap_mm']:.1f} / {geo['motor_saddle_overlap_mm']:.1f} mm",
        "",
        "## Massen- und Energiebudget",
        "",
        f"- Geschaetzte Startmasse: {mass['estimated_takeoff_mass_g']:.0f} g",
        f"- Druckteile vor Slicer: {mass['pre_slicer_printed_mass_range_g'][0]:.0f}-{mass['pre_slicer_printed_mass_range_g'][1]:.0f} g",
        f"- Nutzbare Akkuenergie bei 80 %: {data['energy']['usable_energy_wh_assuming_80_percent']:.1f} Wh",
        f"- Reine Rechen-Flugzeit bei 120-160 W: {data['energy']['illustrative_flight_time_min']['at_160_W']:.1f}-{data['energy']['illustrative_flight_time_min']['at_120_W']:.1f} min",
        "",
        "## Rohr-Screening (kein Festigkeitsnachweis)",
        "",
        f"- Lastannahme: {beam['assumed_tip_load_n']:.1f} N am {beam['unsupported_length_mm']:.1f} mm Kragarm",
        f"- angenommener E-Modul: {beam['assumed_longitudinal_modulus_mpa']/1000:.1f} GPa",
        f"- Biegespannung Rohr: {beam['root_bending_stress_mpa']:.1f} MPa",
        f"- Enddurchbiegung Rohr: {beam['tip_deflection_mm']:.3f} mm",
        "- Nicht abgedeckt: Klemmschlupf, Kerben, Druckteilfestigkeit, Alterung, Fatigue, Crash und Resonanz.",
        "",
        "## Numerische Regeln",
        "",
        "| Regel | Wert | Grenze | Ergebnis |",
        "|---|---:|---:|:---:|",
    ]
    for check in data["checks"]:
        lines.append(
            f"| {check['name']} | {check['value_mm']:.2f} mm | >= {check['limit_mm']:.2f} mm | {'PASS' if check['pass'] else 'FAIL'} |"
        )
    lines.extend(["", "Erzeugt durch `analysis/validate_design.py`.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    data = calculate()
    (OUT / "design_metrics.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(data, OUT / "validation_report.md")
    draw_top_view(FIG / "openquad_top_view.png")
    draw_side_view(FIG / "openquad_side_stack.png")
    draw_motor_pod_detail(FIG / "openquad_motor_pod_detail.png")
    print(json.dumps({
        "all_numeric_design_rules_pass": data["all_numeric_design_rules_pass"],
        "estimated_takeoff_mass_g": round(data["mass"]["estimated_takeoff_mass_g"], 1),
        "adjacent_prop_tip_gap_mm": round(data["geometry"]["adjacent_prop_tip_gap_mm"], 1),
        "deck_prop_xy_clearance_mm": round(data["geometry"]["deck_prop_xy_clearance_mm"], 1),
    }, indent=2))
    return 0 if data["all_numeric_design_rules_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
