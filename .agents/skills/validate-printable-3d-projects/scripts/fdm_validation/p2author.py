from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .common import check, report, sha256_file


def author_anycubic_3mf(
    sources: list[Path],
    output: Path,
    *,
    machine_profile: Path,
    process_profile: Path,
    filament_profile: Path,
    support_mode: str,
    executable: str = "AnycubicSlicerNext",
    timeout_s: int = 600,
    profile: str = "release",
) -> dict:
    inputs = [*sources, machine_profile, process_profile, filament_profile]
    checks = []
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        return report(
            "author-anycubic-3mf",
            [
                check(
                    "author-inputs",
                    "FAIL",
                    "Missing source/profile inputs: " + ", ".join(missing),
                )
            ],
            inputs=inputs,
            profile=profile,
        )
    if output.exists():
        return report(
            "author-anycubic-3mf",
            [
                check(
                    "author-non-destructive-output",
                    "FAIL",
                    f"Refusing to overwrite existing output: {output}",
                )
            ],
            inputs=inputs,
            profile=profile,
        )
    if support_mode not in {"disabled", "enabled"}:
        return report(
            "author-anycubic-3mf",
            [
                check(
                    "author-support-mode",
                    "FAIL",
                    "support_mode must be disabled or enabled",
                )
            ],
            inputs=inputs,
            profile=profile,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="metrimade-p2-3mf-") as temporary:
        state = Path(temporary) / "slicer-state"
        command = [
            executable,
            "--datadir",
            str(state),
            "--load-settings",
            f"{process_profile.resolve()};{machine_profile.resolve()}",
            "--load-filaments",
            str(filament_profile.resolve()),
            "--load-defaultfila",
            "--ensure-on-bed",
            "--arrange",
            "1",
            "--export-3mf",
            str(output.resolve()),
            *[str(path.resolve()) for path in sources],
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_s,
                cwd=temporary,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return report(
                "author-anycubic-3mf",
                [
                    check(
                        "author-slicer-execution",
                        "FAIL",
                        f"{type(exc).__name__}: {exc}",
                    )
                ],
                inputs=inputs,
                profile=profile,
            )

    created = (
        completed.returncode == 0 and output.is_file() and output.stat().st_size > 0
    )
    checks.append(
        check(
            "author-slicer-execution",
            "PASS" if created else "FAIL",
            "Anycubic Slicer Next created the local 3MF project"
            if created
            else f"3MF export failed with return code {completed.returncode}",
            metrics={"return_code": completed.returncode},
        )
    )
    embedded_support = None
    settings_ids = {}
    if created:
        try:
            import zipfile

            with zipfile.ZipFile(output, "r") as archive:
                settings = json.loads(archive.read("Metadata/project_settings.config"))
            embedded_support = str(settings.get("enable_support"))
            settings_ids = {
                key: settings.get(key)
                for key in (
                    "printer_settings_id",
                    "print_settings_id",
                    "filament_settings_id",
                )
            }
            expected = "0" if support_mode == "disabled" else "1"
            checks.append(
                check(
                    "author-support-setting",
                    "PASS" if embedded_support == expected else "FAIL",
                    "Embedded support setting matches the requested mode"
                    if embedded_support == expected
                    else f"Embedded enable_support={embedded_support!r}; expected {expected!r}",
                )
            )
        except Exception as exc:
            checks.append(
                check(
                    "author-project-metadata",
                    "FAIL",
                    f"Could not read embedded slicer settings: {type(exc).__name__}: {exc}",
                )
            )

    version = "unknown"
    executable_hash = None
    try:
        with tempfile.TemporaryDirectory(
            prefix="metrimade-p2-slicer-version-"
        ) as version_directory:
            version_run = subprocess.run(
                [executable, "--help"],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
                cwd=version_directory,
            )
        match = re.search(
            r"AnycubicSlicerNext-([^:\s]+)", version_run.stdout + version_run.stderr
        )
        if match:
            version = match.group(1)
        located = shutil.which(executable)
        executable_path = (
            Path(located).resolve() if located else Path(executable).resolve()
        )
        if executable_path.is_file():
            executable_hash = sha256_file(executable_path)
    except Exception:
        pass

    return report(
        "author-anycubic-3mf",
        checks,
        inputs=inputs,
        profile=profile,
        metrics={
            "output": {
                "path": str(output.resolve()),
                "sha256": sha256_file(output) if output.is_file() else None,
                "size_bytes": output.stat().st_size if output.is_file() else None,
            },
            "sources": [
                {"path": str(path.resolve()), "sha256": sha256_file(path)}
                for path in sources
            ],
            "profiles": {
                "machine": {
                    "path": str(machine_profile.resolve()),
                    "sha256": sha256_file(machine_profile),
                },
                "process": {
                    "path": str(process_profile.resolve()),
                    "sha256": sha256_file(process_profile),
                },
                "filament": {
                    "path": str(filament_profile.resolve()),
                    "sha256": sha256_file(filament_profile),
                },
            },
            "slicer": {
                "executable": executable,
                "version": version,
                "sha256": executable_hash,
            },
            "support_mode": support_mode,
            "embedded_enable_support": embedded_support,
            "settings_ids": settings_ids,
            "invocation": command,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
        limitations=[
            "The export authors a local slicer project only; it does not upload or start a print.",
            "Arrangement preserves source rotations but still requires product-specific confirmation that the selected sources are complete and correctly oriented.",
        ],
    )
