#!/usr/bin/env python3
"""Capture reproducible local Step1X source, Docker, GPU, model and API facts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAFE_ENV_NAMES = {
    "GEOMETRY_DEVICE",
    "TEXTURE_DEVICE",
    "TEXTURE_AUX_DEVICE",
    "TEXTURE_CPU_OFFLOAD",
    "BACKGROUND_REMOVAL_DEVICE",
    "BIREFNET_REVISION",
    "REMBG_PROVIDER",
    "REMBG_CUDA_DEVICE",
    "REMBG_GPU_MEMORY_GB",
    "HF_HOME",
    "PYTORCH_CUDA_ALLOC_CONF",
    "TORCH_CUDA_ARCH_LIST",
}
RUNTIME_FILES = {
    ".python-version",
    "LICENSE",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "requirements.cuda124.txt",
    "requirements.web.txt",
    "app.py",
    "inference.py",
}


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def run(
    command: list[str], cwd: Path | None = None, timeout: float = 30.0
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def require_output(
    command: list[str], cwd: Path | None = None, timeout: float = 30.0
) -> str:
    result = run(command, cwd=cwd, timeout=timeout)
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(command[:3])} failed: {message}")
    return result.stdout.strip()


def parse_status_path(entry: str) -> str | None:
    if len(entry) < 4:
        return None
    path = entry[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path or None


def capture_source(
    repo: Path, patch_output: Path | None, overwrite: bool
) -> dict[str, Any]:
    origin = require_output(["git", "remote", "get-url", "origin"], cwd=repo)
    commit = require_output(["git", "rev-parse", "HEAD"], cwd=repo)
    branch = require_output(["git", "branch", "--show-current"], cwd=repo)
    status_result = run(["git", "status", "--porcelain=v1"], cwd=repo)
    if status_result.returncode != 0:
        message = (status_result.stderr or status_result.stdout).strip()
        raise RuntimeError(f"git status failed: {message}")
    # Porcelain uses both leading status columns.  Do not strip them: doing so
    # turns ` M path` into `M path` and breaks path extraction.
    status_text = status_result.stdout.rstrip("\n")
    status = [line for line in status_text.splitlines() if line]
    diff_result = run(["git", "diff", "--binary", "HEAD", "--", "."], cwd=repo)
    if diff_result.returncode != 0:
        raise RuntimeError(f"git diff failed: {diff_result.stderr.strip()}")
    diff_bytes = diff_result.stdout.encode("utf-8")

    paths = set(RUNTIME_FILES)
    for entry in status:
        parsed = parse_status_path(entry)
        if parsed and parsed != ".env" and not parsed.startswith(".env."):
            paths.add(parsed)
    file_hashes: dict[str, dict[str, Any]] = {}
    for relative in sorted(paths):
        candidate = (repo / relative).resolve()
        try:
            candidate.relative_to(repo)
        except ValueError:
            continue
        if candidate.is_file() and not candidate.is_symlink():
            file_hashes[relative] = {
                "sha256": sha256_file(candidate),
                "bytes": candidate.stat().st_size,
            }

    patch_record: dict[str, Any] | None = None
    if patch_output:
        patch_output = patch_output.expanduser().resolve()
        if patch_output.exists() and not overwrite:
            raise RuntimeError(f"refusing to overwrite patch evidence: {patch_output}")
        patch_output.parent.mkdir(parents=True, exist_ok=True)
        patch_output.write_bytes(diff_bytes)
        patch_record = {
            "path": str(patch_output),
            "sha256": sha256_file(patch_output),
            "bytes": patch_output.stat().st_size,
            "scope": "tracked files only; untracked runtime files are covered by file hashes",
        }

    return {
        "repository": str(repo),
        "origin": origin,
        "branch": branch,
        "base_commit": commit,
        "worktree_clean": not status,
        "status_porcelain": status,
        "tracked_diff_sha256": sha256_bytes(diff_bytes),
        "tracked_diff_bytes": len(diff_bytes),
        "patch_evidence": patch_record,
        "runtime_file_hashes": file_hashes,
    }


def selected_environment(config_env: list[str]) -> dict[str, str]:
    selected: dict[str, str] = {}
    for entry in config_env:
        name, separator, value = entry.partition("=")
        if separator and name in SAFE_ENV_NAMES:
            selected[name] = value
    return selected


def parse_gpu_csv(text: str) -> list[dict[str, str]]:
    fields = ("name", "uuid", "memory_total", "driver_version")
    rows = []
    for line in text.splitlines():
        values = [item.strip() for item in line.split(",")]
        if len(values) == len(fields):
            rows.append(dict(zip(fields, values)))
    return rows


def list_snapshots(hf_root: Path | None) -> list[dict[str, str]]:
    if hf_root is None:
        return []
    hub = hf_root / "hub"
    if not hub.is_dir():
        return []
    snapshots = []
    for snapshot in sorted(hub.glob("models--*/snapshots/*")):
        if not snapshot.is_dir():
            continue
        encoded = snapshot.parents[1].name.removeprefix("models--")
        model_id = "/".join(encoded.split("--", 1))
        snapshots.append(
            {
                "model_id": model_id,
                "revision": snapshot.name,
                "host_path": str(snapshot),
            }
        )
    return snapshots


def fetch_api(base_url: str, timeout: float) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/gradio_api/info"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise TypeError("API schema is not a JSON object")
    return value


def capture_docker(
    repo: Path, compose_file: Path, service: str, warnings: list[str]
) -> tuple[dict[str, Any], Path | None]:
    docker: dict[str, Any] = {
        "compose_file": str(compose_file),
        "compose_file_sha256": (
            sha256_file(compose_file) if compose_file.is_file() else None
        ),
        "service": service,
    }
    if not compose_file.is_file():
        warnings.append(f"compose file missing: {compose_file}")
        return docker, None
    result = run(
        ["docker", "compose", "-f", str(compose_file), "ps", "-q", service],
        cwd=repo,
    )
    if result.returncode != 0 or not result.stdout.strip():
        warnings.append("Step1X container is not running or Docker is unavailable")
        docker["container_status"] = "not_observed"
        return docker, None

    container_id = result.stdout.strip().splitlines()[0]
    inspect_text = require_output(["docker", "inspect", container_id])
    inspected = json.loads(inspect_text)[0]
    docker.update(
        {
            "container_id": inspected.get("Id"),
            "container_name": str(inspected.get("Name", "")).lstrip("/"),
            "container_status": inspected.get("State", {}).get("Status"),
            "health": inspected.get("State", {}).get("Health", {}).get("Status"),
            "started_at": inspected.get("State", {}).get("StartedAt"),
            "image_reference": inspected.get("Config", {}).get("Image"),
            "image_id": inspected.get("Image"),
            "selected_environment": selected_environment(
                inspected.get("Config", {}).get("Env", [])
            ),
            "device_requests": inspected.get("HostConfig", {}).get("DeviceRequests"),
            "mounts": [
                {
                    "type": mount.get("Type"),
                    "source": mount.get("Source"),
                    "destination": mount.get("Destination"),
                    "mode": mount.get("Mode"),
                    "rw": mount.get("RW"),
                }
                for mount in inspected.get("Mounts", [])
            ],
        }
    )

    image_text = require_output(["docker", "image", "inspect", inspected["Image"]])
    image = json.loads(image_text)[0]
    docker["image"] = {
        "id": image.get("Id"),
        "repo_digests": image.get("RepoDigests"),
        "created": image.get("Created"),
        "architecture": image.get("Architecture"),
        "os": image.get("Os"),
    }

    probe_code = (
        "import importlib.metadata as m,json,sys,torch;"
        "names=['torch','torchvision','gradio','gradio_client','pydantic',"
        "'diffusers','transformers','rembg','onnxruntime'];"
        "versions={n:(m.version(n) if n in {d.metadata['Name'] for d in m.distributions()} "
        "else 'not-installed') for n in names};"
        "print(json.dumps({'python':sys.version.split()[0],'torch_build':torch.__version__,"
        "'cuda_abi':torch.version.cuda,'packages':versions}))"
    )
    try:
        version_text = require_output(
            ["docker", "exec", container_id, "python", "-c", probe_code], timeout=60
        )
        docker["runtime_versions"] = json.loads(version_text)
    except (RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        warnings.append(f"container version probe failed: {exc}")

    gpu_result = run(
        [
            "docker",
            "exec",
            container_id,
            "nvidia-smi",
            "--query-gpu=name,uuid,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
    )
    if gpu_result.returncode == 0:
        docker["gpus"] = parse_gpu_csv(gpu_result.stdout)
    else:
        warnings.append("GPU inventory was not available inside the container")

    u2net_result = run(
        [
            "docker",
            "exec",
            container_id,
            "sha256sum",
            "/home/step1x/.u2net/u2net.onnx",
        ]
    )
    if u2net_result.returncode == 0 and u2net_result.stdout.strip():
        checksum = u2net_result.stdout.split()[0]
        size_result = run(
            [
                "docker",
                "exec",
                container_id,
                "stat",
                "-c",
                "%s",
                "/home/step1x/.u2net/u2net.onnx",
            ]
        )
        docker["background_model_asset"] = {
            "container_path": "/home/step1x/.u2net/u2net.onnx",
            "sha256": checksum,
            "bytes": (
                int(size_result.stdout.strip())
                if size_result.returncode == 0 and size_result.stdout.strip().isdigit()
                else None
            ),
            "execution_condition": "opaque input without useful alpha",
        }

    hf_root = None
    for mount in inspected.get("Mounts", []):
        if mount.get("Destination") == "/models/huggingface":
            candidate = Path(str(mount.get("Source", "")))
            if candidate.is_dir():
                hf_root = candidate
            break
    return docker, hf_root


def default_repo() -> Path:
    configured = os.getenv("STEP1X_REPO")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[5] / "Step1X-3D"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=default_repo())
    parser.add_argument("--compose-file", type=Path)
    parser.add_argument("--service", default="step1x3d")
    parser.add_argument(
        "--url", default=os.getenv("STEP1X_URL", "http://127.0.0.1:7861")
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--patch-output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not repo.is_dir() or not (repo / ".git").exists():
        print(f"ERROR: Step1X git repository not found: {repo}", file=sys.stderr)
        return 2
    if output.exists() and not args.overwrite:
        print(
            f"ERROR: refusing to overwrite runtime profile: {output}", file=sys.stderr
        )
        return 2
    compose_file = (
        args.compose_file.expanduser().resolve()
        if args.compose_file
        else repo / "docker-compose.yml"
    )
    warnings: list[str] = []
    try:
        source = capture_source(repo, args.patch_output, args.overwrite)
        docker, hf_root = capture_docker(repo, compose_file, args.service, warnings)
        api_record: dict[str, Any]
        try:
            api = fetch_api(args.url, args.timeout)
            api_record = {
                "url": args.url.rstrip("/"),
                "endpoint": "/generate_func",
                "schema_sha256": sha256_bytes(
                    json.dumps(
                        api, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                    ).encode("utf-8")
                ),
                "status": "observed",
            }
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            warnings.append(f"live API probe failed: {exc}")
            api_record = {"url": args.url.rstrip("/"), "status": "not_observed"}

        snapshots = list_snapshots(hf_root or repo / ".cache" / "huggingface")
        profile = {
            "schema_version": "1.0",
            "profile_type": "Step1X-3D local runtime evidence",
            "captured_at": utc_now(),
            "status": "captured_with_warnings" if warnings else "captured",
            "source": source,
            "docker": docker,
            "api": api_record,
            "model_snapshots": snapshots,
            "license_review_required": True,
            "license_reference": "step1x-image-to-3d/references/commercial-and-research.md",
            "warnings": warnings,
        }
        atomic_json(output, profile)
        print(str(output))
        return 1 if warnings else 0
    except (
        RuntimeError,
        TypeError,
        OSError,
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
    ) as exc:
        print(f"ERROR: runtime capture failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
