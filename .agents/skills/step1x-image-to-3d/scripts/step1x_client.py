#!/usr/bin/env python3
"""Probe or invoke the local Step1X-3D Gradio endpoint with run evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENDPOINT = "/generate_func"
PINNED_CLIENT_VERSION = "1.4.2"
EXPECTED_PARAMETERS = [
    "input_image_path",
    "guidance_scale",
    "inference_steps",
    "max_facenum",
    "symmetry",
    "edge_type",
]
EXPECTED_ENUMS = {
    "symmetry": {"x", "asymmetry"},
    "edge_type": {"sharp", "normal", "smooth"},
}


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def fetch_api_info(base_url: str, timeout: float) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/gradio_api/info"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "step1x-skill/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read Step1X API schema from {url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise TypeError("Step1X API info is not a JSON object")
    return payload


def validate_api_info(info: dict[str, Any]) -> dict[str, Any]:
    endpoints = info.get("named_endpoints")
    if not isinstance(endpoints, dict) or ENDPOINT not in endpoints:
        available = sorted(endpoints) if isinstance(endpoints, dict) else []
        raise RuntimeError(
            f"expected named endpoint {ENDPOINT}; available endpoints: {available}"
        )
    endpoint = endpoints[ENDPOINT]
    if not isinstance(endpoint, dict):
        raise TypeError(f"endpoint schema for {ENDPOINT} is invalid")
    parameters = endpoint.get("parameters")
    returns = endpoint.get("returns")
    if not isinstance(parameters, list):
        raise TypeError("endpoint parameter schema is missing")
    actual_names = [item.get("parameter_name") for item in parameters]
    if actual_names != EXPECTED_PARAMETERS:
        raise RuntimeError(
            "Step1X API parameter drift: "
            f"expected {EXPECTED_PARAMETERS}, received {actual_names}"
        )
    by_name = {item.get("parameter_name"): item for item in parameters}
    for name, expected in EXPECTED_ENUMS.items():
        schema = by_name[name].get("type")
        actual = set(schema.get("enum", [])) if isinstance(schema, dict) else set()
        if actual != expected:
            raise RuntimeError(
                f"Step1X API enum drift for {name}: expected {sorted(expected)}, "
                f"received {sorted(actual)}"
            )
    if not isinstance(returns, list) or len(returns) != 1:
        raise RuntimeError(
            "Step1X endpoint must return exactly one geometry GLB; the owned fork "
            "has no texture stage"
        )
    return endpoint


def probe(base_url: str, timeout: float) -> tuple[dict[str, Any], dict[str, Any]]:
    info = fetch_api_info(base_url, timeout)
    endpoint = validate_api_info(info)
    report = {
        "schema_version": "1.0",
        "captured_at": utc_now(),
        "service_url": base_url.rstrip("/"),
        "endpoint": ENDPOINT,
        "status": "compatible",
        "api_schema_sha256": hashlib.sha256(canonical_bytes(info)).hexdigest(),
        "parameters": [
            {
                "name": item.get("parameter_name"),
                "default": item.get("parameter_default"),
                "has_default": item.get("parameter_has_default"),
                "type": item.get("type"),
            }
            for item in endpoint["parameters"]
        ],
        "return_count": len(endpoint["returns"]),
    }
    return info, report


def default_repo() -> Path:
    configured = os.getenv("STEP1X_REPO")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[5] / "Step1X-3D"


def fork_provenance(repo: Path) -> dict[str, Any]:
    """Identify the checkout that serves the endpoint; its licence posture is commit-specific."""
    record: dict[str, Any] = {"repo": str(repo)}
    if not (repo / ".git").exists():
        record["error"] = "not a git checkout"
        return record
    for key, command in (
        ("commit", ["git", "rev-parse", "HEAD"]),
        ("remote", ["git", "remote", "get-url", "origin"]),
    ):
        try:
            completed = subprocess.run(
                command,
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            record[key] = None
            record.setdefault("errors", []).append(f"{key}: {exc}")
            continue
        record[key] = completed.stdout.strip() if completed.returncode == 0 else None
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        record["worktree_clean"] = None
    else:
        record["worktree_clean"] = (
            not dirty.stdout.strip() if dirty.returncode == 0 else None
        )
    return record


def run_process(
    command: list[str], cwd: Path | None, timeout: float
) -> tuple[subprocess.CompletedProcess[str] | None, str | None]:
    try:
        return (
            subprocess.run(
                command,
                cwd=cwd,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout,
            ),
            None,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)


def docker_service_status(
    repo: Path, compose_file: Path, service: str, timeout: float
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "checked": True,
        "repo": str(repo),
        "compose_file": str(compose_file),
        "service": service,
        "logs_command": [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "logs",
            "--tail",
            "200",
            service,
        ],
    }
    if not compose_file.is_file():
        record.update(
            {
                "observation": "unavailable",
                "error": f"compose file does not exist: {compose_file}",
            }
        )
        return record

    result, error = run_process(
        [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "ps",
            "-a",
            "-q",
            service,
        ],
        repo,
        timeout,
    )
    if result is None:
        record.update({"observation": "unavailable", "error": error})
        return record
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        record.update({"observation": "unavailable", "error": detail})
        return record
    container_ids = [
        line.strip() for line in result.stdout.splitlines() if line.strip()
    ]
    if not container_ids:
        record["observation"] = "container_absent"
        return record

    container_id = container_ids[0]
    record["container_id"] = container_id
    inspected, inspect_error = run_process(
        ["docker", "inspect", container_id], None, timeout
    )
    if inspected is None or inspected.returncode != 0:
        detail = inspect_error or (inspected.stderr or inspected.stdout).strip()
        record.update({"observation": "inspect_failed", "error": detail})
        return record
    try:
        inspect_payload = json.loads(inspected.stdout)
        state = inspect_payload[0]["State"]
        if not isinstance(state, dict):
            raise TypeError("docker inspect State is not an object")
    except (IndexError, KeyError, TypeError, json.JSONDecodeError) as exc:
        record.update({"observation": "inspect_failed", "error": str(exc)})
        return record

    health = state.get("Health") if isinstance(state.get("Health"), dict) else {}
    record.update(
        {
            "observation": "observed",
            "container_status": state.get("Status"),
            "running": bool(state.get("Running")),
            "exit_code": state.get("ExitCode"),
            "health": health.get("Status"),
            "started_at": state.get("StartedAt"),
            "finished_at": state.get("FinishedAt"),
        }
    )

    logs, _ = run_process(
        ["docker", "logs", "--tail", "160", container_id], None, timeout
    )
    if logs is not None and logs.returncode == 0:
        text = f"{logs.stdout}\n{logs.stderr}"
        record["startup_markers"] = {
            "model_loading_seen": any(
                marker in text
                for marker in (
                    "Loading CLIP model",
                    "Loading Dinov2 model",
                    "Loading pipeline components",
                    "Fetching ",
                )
            ),
            "server_listening_seen": "Running on local URL:" in text,
            "traceback_seen": "Traceback (most recent call last)" in text,
        }
    return record


def classify_readiness(
    api: dict[str, Any], docker: dict[str, Any] | None
) -> tuple[str, str, bool | None, bool, str, int]:
    if api.get("contract_status") == "compatible":
        return (
            "ready",
            "loaded_and_ready",
            True,
            True,
            "The current app exposes its API only after the geometry pipeline loads. Submit one job; API readiness does not prove that the queue is idle.",
            0,
        )
    if api.get("reachable"):
        return (
            "incompatible",
            "loaded_but_client_incompatible",
            True,
            False,
            "The server answered after startup, but its API contract drifted. Do not submit until the pinned environment/client contract is restored.",
            2,
        )
    if docker and docker.get("observation") == "container_absent":
        return (
            "not_ready",
            "not_loaded_container_absent",
            False,
            False,
            "Start the Compose service, then rerun status. Do not call generate yet.",
            1,
        )
    if docker and docker.get("observation") == "observed":
        if not docker.get("running"):
            return (
                "not_ready",
                "not_loaded_container_stopped",
                False,
                False,
                "Inspect the recorded logs command and container exit code, then start or repair the service before generation.",
                1,
            )
        markers = docker.get("startup_markers")
        markers = markers if isinstance(markers, dict) else {}
        if markers.get("server_listening_seen"):
            return (
                "not_ready",
                "startup_completed_but_api_unreachable",
                None,
                False,
                "The container previously reached its listen marker, but the API is unavailable now. Inspect logs/networking before retrying; do not assume the models remain usable.",
                1,
            )
        if markers.get("model_loading_seen"):
            return (
                "not_ready",
                "loading_or_initializing",
                False,
                False,
                "Model loading has started. It can take several minutes; wait, inspect logs if needed, and rerun status instead of launching another container or job.",
                1,
            )
        return (
            "not_ready",
            "not_loaded_or_initializing",
            None,
            False,
            "The container runs, but completed model loading is not confirmed. Inspect logs and rerun status before generation.",
            1,
        )
    return (
        "not_ready",
        "model_load_not_confirmed",
        None,
        False,
        "The API is unavailable and local Docker state was not observed. Check the URL or rerun without --skip-docker before generation.",
        1,
    )


def ensure_new_run_dir(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.exists():
        if not resolved.is_dir():
            raise RuntimeError(f"output path is not a directory: {resolved}")
        if any(resolved.iterdir()):
            raise RuntimeError(
                f"refusing to overwrite non-empty run directory: {resolved}"
            )
    else:
        resolved.mkdir(parents=True)
    return resolved


def archive_file(source: Path, destination: Path) -> dict[str, Any]:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise RuntimeError(f"evidence file not found: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise RuntimeError(f"refusing to overwrite evidence file: {destination}")
    shutil.copy2(source, destination)
    return {
        "original_path": str(source),
        "archived_path": str(destination),
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
    }


def diagnose_alpha(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "unknown",
        "meaningful_transparency": "unknown",
        "background_removal_expected": "unknown",
    }
    try:
        from PIL import Image

        with Image.open(path) as image:
            result["mode"] = image.mode
            result["size_px"] = [image.width, image.height]
            has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
            if not has_alpha:
                meaningful = False
                extrema = None
            else:
                alpha = image.convert("RGBA").getchannel("A")
                extrema = list(alpha.getextrema())
                meaningful = extrema[0] < 255
            result.update(
                {
                    "status": "inspected",
                    "alpha_extrema": extrema,
                    "meaningful_transparency": meaningful,
                    "background_removal_expected": (
                        "skipped_use_input_alpha" if meaningful else "rembg_u2net_cpu"
                    ),
                }
            )
    except (ImportError, OSError) as exc:
        result["diagnostic"] = f"alpha inspection unavailable: {exc}"
    return result


def result_path(value: Any) -> Path:
    if isinstance(value, (str, os.PathLike)):
        candidate = Path(value)
    elif isinstance(value, dict) and isinstance(value.get("path"), str):
        candidate = Path(value["path"])
    else:
        raise TypeError(f"unsupported Gradio file result: {type(value).__name__}")
    if not candidate.is_file():
        raise RuntimeError(f"Gradio output file is missing: {candidate}")
    return candidate


def verify_glb(path: Path) -> None:
    with path.open("rb") as handle:
        magic = handle.read(4)
    if magic != b"glTF":
        raise RuntimeError(f"output is not a binary glTF/GLB file: {path}")


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def command_status(args: argparse.Namespace) -> int:
    api: dict[str, Any] = {
        "url": args.url.rstrip("/"),
        "endpoint": ENDPOINT,
        "reachable": False,
        "contract_status": "not_observed",
    }
    try:
        info = fetch_api_info(args.url, args.timeout)
        api.update(
            {
                "reachable": True,
                "api_schema_sha256": hashlib.sha256(canonical_bytes(info)).hexdigest(),
            }
        )
        try:
            validate_api_info(info)
            api["contract_status"] = "compatible"
        except (RuntimeError, TypeError) as exc:
            api.update({"contract_status": "incompatible", "error": str(exc)})
    except (RuntimeError, TypeError) as exc:
        api["error"] = str(exc)

    docker: dict[str, Any] | None
    if args.skip_docker:
        docker = None
    else:
        repo = args.repo.expanduser().resolve()
        compose_file = (
            args.compose_file.expanduser().resolve()
            if args.compose_file
            else repo / "docker-compose.yml"
        )
        docker = docker_service_status(repo, compose_file, args.service, args.timeout)

    status, model_state, model_loaded, safe, action, exit_code = classify_readiness(
        api, docker
    )
    report = {
        "schema_version": "1.0",
        "captured_at": utc_now(),
        "status": status,
        "model_state": model_state,
        "model_loaded": model_loaded,
        "safe_to_submit_generation": safe,
        "readiness_basis": (
            "In the pinned local app, the geometry pipeline is constructed "
            "before Gradio starts listening; a compatible live API therefore confirms "
            "that model loading completed for that process."
        ),
        "api": api,
        "docker": docker if docker is not None else {"checked": False},
        "recommended_action": action,
        "limitations": [
            "API readiness does not prove that the serial queue is idle.",
            "If the app is changed to lazy model loading, this readiness rule must be updated.",
        ],
    }
    if args.report:
        atomic_json(args.report.expanduser().resolve(), report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return exit_code


def command_probe(args: argparse.Namespace) -> int:
    _, report = probe(args.url, args.timeout)
    if args.report:
        atomic_json(args.report.expanduser().resolve(), report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def command_generate(args: argparse.Namespace) -> int:
    source = args.input.expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: input image not found: {source}", file=sys.stderr)
        return 2
    if not 1 <= args.steps <= 100:
        print("ERROR: --steps must be between 1 and 100", file=sys.stderr)
        return 2
    if args.guidance <= 0 or args.max_faces <= 0:
        print("ERROR: guidance and max-faces must be positive", file=sys.stderr)
        return 2
    client_version = package_version("gradio_client")
    if client_version != PINNED_CLIENT_VERSION:
        print(
            "ERROR: incompatible gradio_client version: "
            f"expected {PINNED_CLIENT_VERSION}, received {client_version}; "
            "use scripts/requirements.txt",
            file=sys.stderr,
        )
        return 2

    try:
        run_dir = ensure_new_run_dir(args.output_dir)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    started_wall = time.monotonic()
    started_at = utc_now()
    run_id = str(uuid.uuid4())
    manifest_path = run_dir / "step1x-run.json"
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "status": "running",
        "started_at": started_at,
        "provider": {
            "name": "Step1X-3D",
            "organization": "stepfun-ai",
            "source_repository": "https://github.com/stepfun-ai/Step1X-3D",
            "model_repository": "https://huggingface.co/stepfun-ai/Step1X-3D",
            "code_license": "Apache-2.0",
            "weights_license": "Apache-2.0",
            "served_by_fork": fork_provenance(default_repo()),
        },
        "operation": "single-image-to-geometry-glb",
        "service": {
            "url": args.url.rstrip("/"),
            "endpoint": ENDPOINT,
            "client": "gradio_client",
            "client_version": client_version,
        },
        "parameters": {
            "guidance_scale": args.guidance,
            "inference_steps": args.steps,
            "max_facenum": args.max_faces,
            "symmetry": args.symmetry,
            "edge_type": args.edge_type,
            "geometry_seed": "not_exposed_by_endpoint",
        },
        "limitations": [
            "single image does not determine hidden geometry or physical scale",
            "generated geometry is not a functional or manufacturing authority",
            "GLB must be registered, inspected and routed before slicer/CAD use",
            "commercial clearance requires input rights and dependency review",
        ],
    }

    try:
        suffix = source.suffix.lower() if source.suffix else ".bin"
        input_evidence = archive_file(source, run_dir / "input" / f"source{suffix}")
        input_evidence.update(
            {
                "media_type": mimetypes.guess_type(source.name)[0]
                or "application/octet-stream",
                "alpha": diagnose_alpha(source),
            }
        )
        record["input"] = input_evidence

        optional_evidence: dict[str, Any] = {}
        if args.image_prompt_file:
            prompt_suffix = args.image_prompt_file.suffix or ".txt"
            optional_evidence["image_prompt"] = archive_file(
                args.image_prompt_file,
                run_dir / "input" / f"image-prompt{prompt_suffix}",
            )
        if args.input_record:
            record_suffix = args.input_record.suffix or ".json"
            optional_evidence["input_generation_record"] = archive_file(
                args.input_record,
                run_dir / "input" / f"generation-record{record_suffix}",
            )
        if optional_evidence:
            record["input_evidence"] = optional_evidence

        if args.runtime_profile:
            record["runtime_profile"] = archive_file(
                args.runtime_profile, run_dir / "runtime-profile.json"
            )
        else:
            record["runtime_profile"] = {
                "status": "not_supplied",
                "note": "required before commercial release",
            }

        api_info, probe_report = probe(args.url, args.timeout)
        api_path = run_dir / "api-schema.json"
        atomic_json(api_path, api_info)
        record["service"].update(
            {
                "api_schema_path": str(api_path),
                "api_schema_sha256": probe_report["api_schema_sha256"],
                "api_schema_file_sha256": sha256_file(api_path),
                "contract_status": probe_report["status"],
            }
        )
        atomic_json(manifest_path, record)

        try:
            from gradio_client import Client, handle_file
        except ImportError as exc:
            raise RuntimeError(
                "gradio_client is missing; install scripts/requirements.txt"
            ) from exc

        print(
            "Step1X started. Geometry generation can take several minutes; "
            "a quiet client is not by itself a hang. The server queue allows one job at a time.",
            file=sys.stderr,
            flush=True,
        )
        with tempfile.TemporaryDirectory(prefix="step1x-client-") as temporary:
            client = Client(
                args.url.rstrip("/"),
                verbose=False,
                download_files=temporary,
            )
            result = client.predict(
                handle_file(str(Path(input_evidence["archived_path"]))),
                args.guidance,
                args.steps,
                args.max_faces,
                args.symmetry,
                args.edge_type,
                api_name=ENDPOINT,
            )
            values = list(result) if isinstance(result, (tuple, list)) else [result]
            if len(values) != 1:
                raise RuntimeError(
                    f"Step1X returned {len(values)} value(s); expected one geometry GLB"
                )
            names = ("geometry.raw.glb",)
            roles = ("untextured-geometry-master",)
            outputs = []
            for value, name, role in zip(values, names, roles):
                downloaded = result_path(value)
                destination = run_dir / name
                shutil.copy2(downloaded, destination)
                verify_glb(destination)
                outputs.append(
                    {
                        "path": str(destination),
                        "sha256": sha256_file(destination),
                        "bytes": destination.stat().st_size,
                        "media_type": "model/gltf-binary",
                        "role": role,
                        "physical_scale_verified": False,
                        "semantic_orientation_verified": False,
                    }
                )

        record.update(
            {
                "status": "succeeded",
                "finished_at": utc_now(),
                "duration_seconds": round(time.monotonic() - started_wall, 3),
                "outputs": outputs,
            }
        )
        atomic_json(manifest_path, record)
        print(str(manifest_path))
        return 0
    except Exception as exc:  # noqa: BLE001 - every failure needs a durable run record
        record.update(
            {
                "status": "failed",
                "finished_at": utc_now(),
                "duration_seconds": round(time.monotonic() - started_wall, 3),
                "failure": {"type": type(exc).__name__, "message": str(exc)},
            }
        )
        atomic_json(manifest_path, record)
        print(f"ERROR: Step1X generation failed: {exc}", file=sys.stderr)
        print(f"Failure record: {manifest_path}", file=sys.stderr)
        return 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser(
        "status", help="Confirm that the current model process is loaded and API-ready"
    )
    status_parser.add_argument(
        "--url", default=os.getenv("STEP1X_URL", "http://127.0.0.1:7861")
    )
    status_parser.add_argument("--timeout", type=float, default=10.0)
    status_parser.add_argument("--repo", type=Path, default=default_repo())
    status_parser.add_argument("--compose-file", type=Path)
    status_parser.add_argument("--service", default="step1x3d")
    status_parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Check only the API, for a remote or non-Docker deployment",
    )
    status_parser.add_argument("--report", type=Path)
    status_parser.set_defaults(handler=command_status)

    probe_parser = subparsers.add_parser(
        "probe", help="Validate and hash the API schema"
    )
    probe_parser.add_argument(
        "--url", default=os.getenv("STEP1X_URL", "http://127.0.0.1:7861")
    )
    probe_parser.add_argument("--timeout", type=float, default=10.0)
    probe_parser.add_argument("--report", type=Path)
    probe_parser.set_defaults(handler=command_probe)

    generate_parser = subparsers.add_parser(
        "generate", help="Generate a geometry GLB and an auditable run record"
    )
    generate_parser.add_argument("input", type=Path)
    generate_parser.add_argument("--output-dir", type=Path, required=True)
    generate_parser.add_argument(
        "--url", default=os.getenv("STEP1X_URL", "http://127.0.0.1:7861")
    )
    generate_parser.add_argument("--timeout", type=float, default=10.0)
    generate_parser.add_argument("--guidance", type=float, default=7.5)
    generate_parser.add_argument("--steps", type=int, default=50)
    generate_parser.add_argument("--max-faces", type=int, default=400000)
    generate_parser.add_argument("--symmetry", choices=("x", "asymmetry"), default="x")
    generate_parser.add_argument(
        "--edge-type", choices=("sharp", "normal", "smooth"), default="sharp"
    )
    generate_parser.add_argument("--runtime-profile", type=Path)
    generate_parser.add_argument("--image-prompt-file", type=Path)
    generate_parser.add_argument("--input-record", type=Path)
    generate_parser.set_defaults(handler=command_generate)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return int(args.handler(args))
    except (RuntimeError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
