"""Preliminary inverted-pendulum plant and sampled LQR study for MM-TOY-003.

This is a decision model, not flight/vehicle firmware. It uses a five-state
nonlinear cart-pendulum proxy with first-order force actuation, sample-and-hold
control at 250 Hz, force saturation and deterministic RK4 integration.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.linalg import solve_continuous_are

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "cad"))
import parameters as P

OUT = ROOT / "validation" / f"v{P.CANDIDATE}" / "control-model-validation.json"
GEOMETRY_REPORT = ROOT / "validation" / f"v{P.CANDIDATE}" / "geometry-validation.json"


@dataclass(frozen=True)
class Plant:
    cart_mass_kg: float = 0.62
    body_mass_kg: float = 1.27
    com_height_m: float = 0.105
    body_pitch_inertia_kg_m2: float = 0.0100
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


def linear_state_space(p: Plant) -> tuple[np.ndarray, np.ndarray]:
    m, m_cart, l, inertia = p.body_mass_kg, p.cart_mass_kg, p.com_height_m, p.body_pitch_inertia_kg_m2
    mass_matrix = np.array([[m_cart + m, m * l], [m * l, inertia + m * l * l]], dtype=float)
    inv_mass = np.linalg.inv(mass_matrix)
    a = np.zeros((4, 4), dtype=float)
    a[0, 1] = 1.0
    a[2, 3] = 1.0
    a[[1, 3], 1] = inv_mass @ np.array([-p.cart_damping_n_s_m, 0.0])
    a[[1, 3], 2] = inv_mass @ np.array([0.0, m * 9.81 * l])
    a[[1, 3], 3] = inv_mass @ np.array([0.0, -p.pitch_damping_n_m_s_rad])
    b = np.zeros((4, 1), dtype=float)
    b[[1, 3], 0] = inv_mass @ np.array([1.0, 0.0])
    return a, b


def lqr_gain(p: Plant) -> np.ndarray:
    a, b = linear_state_space(p)
    q = np.diag([2.0, 3.0, 140.0, 12.0])
    r = np.array([[0.45]])
    riccati = solve_continuous_are(a, b, q, r)
    return np.linalg.solve(r, b.T @ riccati)


def derivative(p: Plant, state: np.ndarray, force_command_n: float) -> np.ndarray:
    x, velocity, theta, theta_rate, force = state
    del x
    m, m_cart, l, inertia = p.body_mass_kg, p.cart_mass_kg, p.com_height_m, p.body_pitch_inertia_kg_m2
    c, s = math.cos(theta), math.sin(theta)
    matrix = np.array([[m_cart + m, m * l * c], [m * l * c, inertia + m * l * l]])
    rhs = np.array([
        force - p.cart_damping_n_s_m * velocity + m * l * s * theta_rate * theta_rate,
        m * 9.81 * l * s - p.pitch_damping_n_m_s_rad * theta_rate,
    ])
    acceleration, theta_acceleration = np.linalg.solve(matrix, rhs)
    force_rate = (force_command_n - force) / p.actuator_tau_s
    return np.array([velocity, acceleration, theta_rate, theta_acceleration, force_rate])


def rk4(p: Plant, state: np.ndarray, command: float, dt: float) -> np.ndarray:
    k1 = derivative(p, state, command)
    k2 = derivative(p, state + 0.5 * dt * k1, command)
    k3 = derivative(p, state + 0.5 * dt * k2, command)
    k4 = derivative(p, state + dt * k3, command)
    return state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(initial_pitch_deg: float, duration_s: float = 5.0) -> dict[str, object]:
    p = Plant()
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
    for i in range(len(abs_pitch)):
        if np.all(abs_pitch[i:] <= 1.0):
            settle_time = float(array[i, 0])
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
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size_bytes": path.stat().st_size}


def main() -> int:
    plant = Plant()
    geometry = json.loads(GEOMETRY_REPORT.read_text(encoding="utf-8"))
    proxy_total_mass_kg = float(geometry["mass_properties"]["total_mass_g"]) / 1000.0
    proxy_com_height_m = float(geometry["mass_properties"]["center_of_mass_mm"][2]) / 1000.0
    proxy_first_moment_kg_m = proxy_total_mass_kg * proxy_com_height_m
    plant_total_mass_kg = plant.cart_mass_kg + plant.body_mass_kg
    plant_first_moment_kg_m = plant.body_mass_kg * plant.com_height_m
    mass_error_fraction = abs(plant_total_mass_kg - proxy_total_mass_kg) / proxy_total_mass_kg
    first_moment_error_fraction = abs(plant_first_moment_kg_m - proxy_first_moment_kg_m) / proxy_first_moment_kg_m
    cases = [simulate(-8.0), simulate(8.0)]
    checks = [
        {"id": "sample-rate", "required": True, "status": "PASS" if plant.controller_hz >= 250 else "FAIL", "message": "Controller sample rate meets the approved minimum", "metrics": {"controller_hz": plant.controller_hz}},
        {"id": "mass-model-correlation", "required": True, "status": "PASS" if mass_error_fraction <= 0.05 and first_moment_error_fraction <= 0.05 else "FAIL", "message": "Reduced-order plant preserves revised proxy total mass and gravitational first moment within 5%", "metrics": {"proxy_total_mass_kg": proxy_total_mass_kg, "plant_total_mass_kg": plant_total_mass_kg, "mass_error_fraction": mass_error_fraction, "proxy_first_moment_kg_m": proxy_first_moment_kg_m, "plant_first_moment_kg_m": plant_first_moment_kg_m, "first_moment_error_fraction": first_moment_error_fraction}},
        {"id": "symmetric-release", "required": True, "status": "PASS" if all(case["settle_below_1deg_s"] is not None and case["settle_below_1deg_s"] <= 3.0 for case in cases) else "FAIL", "message": "Both idealized +/-8 degree releases settle below 1 degree within 3 seconds", "metrics": {str(case["initial_pitch_deg"]): case["settle_below_1deg_s"] for case in cases}},
        {"id": "transient-force-limit", "required": True, "status": "PASS" if all(case["max_abs_command_n"] <= plant.transient_force_limit_n + 1e-9 for case in cases) else "FAIL", "message": "Sampled controller command remains inside the declared transient torque proxy", "metrics": {"limit_n": plant.transient_force_limit_n, "case_max_n": [case["max_abs_command_n"] for case in cases]}},
        {"id": "capture-corridor", "required": True, "status": "PASS" if all(case["max_abs_position_m"] <= 1.0 for case in cases) else "FAIL", "message": "Idealized release remains inside the one-metre test corridor", "metrics": {"case_max_abs_position_m": [case["max_abs_position_m"] for case in cases]}},
    ]
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    report = {
        "schema_version": "1.0", "tool": "MM-TOY-003 preliminary nonlinear plant study", "tool_version": "0.1.0", "status": status,
        "inputs": [file_record(Path(__file__).resolve()), file_record(ROOT / "cad" / "parameters.py"), file_record(GEOMETRY_REPORT)], "plant": asdict(plant),
        "derived": {"continuous_force_n": plant.continuous_force_n, "transient_force_limit_n": plant.transient_force_limit_n},
        "cases": cases, "checks": checks,
        "limitations": [
            "Parameters are provisional and not identified from physical hardware.",
            "The reduced-order cart/body split is correlated to proxy total mass and gravitational first moment; it is not a unique physical mass decomposition.",
            "The model omits motor electrical speed/voltage limits, backlash, tire compliance/slip, encoder quantization, IMU bias/noise, delay variation, yaw coupling and floor irregularity.",
            "A model PASS only establishes internal numerical plausibility; it does not qualify firmware tuning, free balance or vehicle-control safety."
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "cases": cases, "checks": {row["id"]: row["status"] for row in checks}}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
