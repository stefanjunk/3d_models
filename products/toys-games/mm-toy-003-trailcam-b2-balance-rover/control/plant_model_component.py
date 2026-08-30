"""Component-correlated balance plausibility model for 0.1.0-parametric.3.

This is a sampled nonlinear decision model, not vehicle firmware.  It keeps
the approved five-state cart/pendulum abstraction while deriving total mass
and gravitational first moment from the current component-driven CAD report.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "cad"))
import component_parameters as P
from plant_model import lqr_gain, rk4

OUT = ROOT / "validation" / f"v{P.CANDIDATE}" / "control-model-validation.json"
GEOMETRY_REPORT = ROOT / "validation" / f"v{P.CANDIDATE}" / "geometry-validation.json"


@dataclass(frozen=True)
class Plant:
    cart_mass_kg: float
    body_mass_kg: float
    com_height_m: float
    body_pitch_inertia_kg_m2: float
    cart_damping_n_s_m: float = 0.20
    pitch_damping_n_m_s_rad: float = 0.010
    wheel_radius_m: float = 0.060
    actuator_tau_s: float = 0.020
    continuous_torque_nm_each: float = 0.35
    transient_torque_nm_each: float = 1.00
    controller_hz: float = 250.0
    integrator_dt_s: float = 0.001

    @property
    def transient_force_limit_n(self) -> float:
        return 2.0 * self.transient_torque_nm_each / self.wheel_radius_m

    @property
    def continuous_force_n(self) -> float:
        return 2.0 * self.continuous_torque_nm_each / self.wheel_radius_m


def correlated_plant(geometry: dict[str, object]) -> Plant:
    mass = geometry["mass_properties"]
    total_mass_kg = float(mass["total_mass_g"]) / 1000.0
    whole_com_m = float(mass["center_of_mass_mm"][2]) / 1000.0
    first_moment = total_mass_kg * whole_com_m
    # Wheels, adapters, motors and brackets dominate the axle-following mass.
    # 0.85 kg is a conservative rounded grouping; the remaining body's COM is
    # derived to preserve the complete CAD gravitational first moment exactly.
    cart_mass_kg = 0.85
    body_mass_kg = total_mass_kg - cart_mass_kg
    body_com_m = first_moment / body_mass_kg
    inertia = body_mass_kg * body_com_m * body_com_m
    return Plant(
        cart_mass_kg=cart_mass_kg,
        body_mass_kg=body_mass_kg,
        com_height_m=body_com_m,
        body_pitch_inertia_kg_m2=inertia,
    )


def simulate(p: Plant, initial_pitch_deg: float, duration_s: float = 5.0) -> dict[str, object]:
    gain = lqr_gain(p)
    state = np.array([0.0, 0.0, math.radians(initial_pitch_deg), 0.0, 0.0])
    steps = int(round(duration_s / p.integrator_dt_s))
    control_stride = int(round(1.0 / p.controller_hz / p.integrator_dt_s))
    command = 0.0
    samples = []
    for index in range(steps + 1):
        if index % control_stride == 0:
            command = float(-(gain @ state[:4])[0])
            command = max(-p.transient_force_limit_n, min(p.transient_force_limit_n, command))
        if index % 10 == 0:
            samples.append((index * p.integrator_dt_s, *state.tolist(), command))
        if index < steps:
            state = rk4(p, state, command, p.integrator_dt_s)
    array = np.asarray(samples)
    pitch_deg = np.degrees(array[:, 3])
    abs_pitch = np.abs(pitch_deg)
    settle_time = None
    for index in range(len(abs_pitch)):
        if np.all(abs_pitch[index:] <= 1.0):
            settle_time = float(array[index, 0])
            break
    return {
        "initial_pitch_deg": initial_pitch_deg,
        "duration_s": duration_s,
        "lqr_gain": gain.tolist()[0],
        "max_abs_pitch_deg": float(abs_pitch.max()),
        "final_abs_pitch_deg": float(abs_pitch[-1]),
        "max_abs_position_m": float(np.abs(array[:, 1]).max()),
        "max_abs_velocity_m_s": float(np.abs(array[:, 2]).max()),
        "max_abs_force_n": float(np.abs(array[:, 5]).max()),
        "max_abs_command_n": float(np.abs(array[:, 6]).max()),
        "settle_below_1deg_s": settle_time,
        "sample_count": len(samples),
    }


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def main() -> int:
    geometry = json.loads(GEOMETRY_REPORT.read_text(encoding="utf-8"))
    plant = correlated_plant(geometry)
    proxy_total_mass_kg = float(geometry["mass_properties"]["total_mass_g"]) / 1000.0
    proxy_com_m = float(geometry["mass_properties"]["center_of_mass_mm"][2]) / 1000.0
    proxy_first_moment = proxy_total_mass_kg * proxy_com_m
    plant_total_mass = plant.cart_mass_kg + plant.body_mass_kg
    plant_first_moment = plant.body_mass_kg * plant.com_height_m
    cases = [simulate(plant, -8.0), simulate(plant, 8.0)]
    checks = [
        {
            "id": "sample-rate",
            "required": True,
            "status": "PASS" if plant.controller_hz >= 250.0 else "FAIL",
            "message": "Controller sample rate meets the approved minimum",
            "metrics": {"controller_hz": plant.controller_hz},
        },
        {
            "id": "mass-model-correlation",
            "required": True,
            "status": "PASS"
            if abs(plant_total_mass - proxy_total_mass_kg) <= 1e-9
            and abs(plant_first_moment - proxy_first_moment) <= 1e-9
            else "FAIL",
            "message": "Reduced model preserves component-driven total mass and gravitational first moment",
            "metrics": {
                "proxy_total_mass_kg": proxy_total_mass_kg,
                "plant_total_mass_kg": plant_total_mass,
                "proxy_first_moment_kg_m": proxy_first_moment,
                "plant_first_moment_kg_m": plant_first_moment,
            },
        },
        {
            "id": "symmetric-release",
            "required": True,
            "status": "PASS"
            if all(case["settle_below_1deg_s"] is not None and case["settle_below_1deg_s"] <= 3.0 for case in cases)
            else "FAIL",
            "message": "Both idealized +/-8 degree releases settle below 1 degree within 3 seconds",
            "metrics": {str(case["initial_pitch_deg"]): case["settle_below_1deg_s"] for case in cases},
        },
        {
            "id": "transient-force-limit",
            "required": True,
            "status": "PASS"
            if all(case["max_abs_command_n"] <= plant.transient_force_limit_n + 1e-9 for case in cases)
            else "FAIL",
            "message": "Command stays inside the declared transient torque proxy",
            "metrics": {
                "limit_n": plant.transient_force_limit_n,
                "case_max_n": [case["max_abs_command_n"] for case in cases],
            },
        },
        {
            "id": "capture-corridor",
            "required": True,
            "status": "PASS" if all(case["max_abs_position_m"] <= 1.0 for case in cases) else "FAIL",
            "message": "Idealized release remains inside the one-metre test corridor",
            "metrics": {"case_max_abs_position_m": [case["max_abs_position_m"] for case in cases]},
        },
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "schema_version": "1.0",
        "tool": "MM-TOY-003 component-correlated nonlinear plant study",
        "tool_version": "0.1.0",
        "status": status,
        "candidate": P.CANDIDATE,
        "inputs": [
            file_record(Path(__file__).resolve()),
            file_record(ROOT / "cad" / "component_parameters.py"),
            file_record(GEOMETRY_REPORT),
        ],
        "plant": asdict(plant),
        "derived": {
            "continuous_force_n": plant.continuous_force_n,
            "transient_force_limit_n": plant.transient_force_limit_n,
        },
        "cases": cases,
        "checks": checks,
        "limitations": [
            "The cart/body split and inertia are a correlated reduced-order assumption, not a measured physical decomposition.",
            "The model omits electrical speed/voltage limits, backlash, tire compliance/slip, sensor noise/bias, delay variation, yaw coupling and floor irregularity.",
            "A numerical PASS does not qualify firmware gains, restrained hardware behavior or free balance.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "checks": {item["id"]: item["status"] for item in checks}, "cases": cases}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
