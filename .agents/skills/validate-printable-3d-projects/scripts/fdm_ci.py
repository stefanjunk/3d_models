#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fdm_validation.common import check, exit_code, load_data, report, write_json  # noqa: E402
from fdm_validation.autonomy import (  # noqa: E402
    approve_agent_stage,
    approve_human_stage,
    init_policy,
    request_human_approval,
    validate_approvals,
    validate_policy,
)
from fdm_validation.doctor import MODULE_GROUPS, run as run_doctor  # noqa: E402
from fdm_validation.freeze import freeze_project  # noqa: E402
from fdm_validation.gcode import analyze as analyze_gcode  # noqa: E402
from fdm_validation.geometry import compare as compare_meshes  # noqa: E402
from fdm_validation.interfaces import validate_contract  # noqa: E402
from fdm_validation.mesh import audit as audit_mesh  # noqa: E402
from fdm_validation.profile import validate_profile  # noqa: E402
from fdm_validation.project import validate_project  # noqa: E402
from fdm_validation.skillcheck import validate as validate_skill  # noqa: E402
from fdm_validation.sweep import run as run_sweep  # noqa: E402
from fdm_validation.threemf import validate as validate_3mf  # noqa: E402


def policy(path: Path | None) -> dict:
    if path is None:
        return {}
    value = load_data(path)
    if not isinstance(value, dict):
        raise ValueError("policy root must be an object")
    return value


def output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", choices=("draft", "release"), default="release")
    parser.add_argument("--json-out", type=Path)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Deterministic validation CLI for printable 3D projects.")
    commands = root.add_subparsers(dest="command", required=True)

    item = commands.add_parser("doctor", help="Report optional capabilities and tool versions without installing anything.")
    item.add_argument("--require", action="append", choices=sorted(MODULE_GROUPS), default=[])
    output_args(item)

    item = commands.add_parser("audit-mesh", help="Audit mesh topology, size, bed fit, budgets, and optional sampled thickness.")
    item.add_argument("mesh", type=Path)
    item.add_argument("--policy", type=Path)
    output_args(item)

    item = commands.add_parser("compare-meshes", help="Run seeded bidirectional surface and dimensional regression.")
    item.add_argument("reference", type=Path)
    item.add_argument("candidate", type=Path)
    item.add_argument("--policy", type=Path)
    output_args(item)

    item = commands.add_parser("check-interfaces", help="Check overlap, clearance, and discretized motion contracts.")
    item.add_argument("contract", type=Path)
    output_args(item)

    item = commands.add_parser("analyze-gcode", help="Parse local G-code without uploading or starting a printer.")
    item.add_argument("gcode", type=Path)
    item.add_argument("--policy", type=Path)
    output_args(item)

    item = commands.add_parser("validate-3mf", help="Validate standard 3MF package, references, materials, and optional topology.")
    item.add_argument("file", type=Path)
    item.add_argument("--policy", type=Path)
    output_args(item)

    item = commands.add_parser("run-sweep", help="Execute a declared default/min/max/pairwise parameter sweep.")
    item.add_argument("manifest", type=Path)
    item.add_argument("--output-root", type=Path)
    output_args(item)

    item = commands.add_parser("validate-skill", help="Check skill layout and scripts without bytecode writes.")
    item.add_argument("skill", type=Path)
    item.add_argument("--runtime", choices=("opencode", "portable"), default="portable")
    output_args(item)

    item = commands.add_parser("validate-profile", help="Validate a companion skill's deterministic validation profile.")
    item.add_argument("profile_file", type=Path)
    output_args(item)

    item = commands.add_parser("init-autonomy", help="Create a project-scoped autonomy policy without overwriting an existing file.")
    item.add_argument("project_id")
    item.add_argument("output", type=Path)
    item.add_argument("--mode", choices=("manual", "guided", "autonomous-to-print-candidate", "custom"), default="autonomous-to-print-candidate")
    item.add_argument("--authorized-by", required=True, help="Human identity that selected this workflow delegation.")
    item.add_argument("--force", action="store_true")
    output_args(item)

    item = commands.add_parser("validate-autonomy", help="Validate stage authorities, evidence rules, and the tool-permission boundary.")
    item.add_argument("policy_file", type=Path)
    output_args(item)

    item = commands.add_parser("approve-agent-stage", help="Derive AUTO_APPROVED or BLOCKED from the policy and hash-bound evidence.")
    item.add_argument("policy_file", type=Path)
    item.add_argument("ledger", type=Path)
    item.add_argument("stage")
    item.add_argument("--agent-id", required=True)
    item.add_argument("--model-id", required=True)
    item.add_argument("--evidence", action="append", type=Path, default=[])
    item.add_argument("--attestation")
    item.add_argument("--human-ledger", type=Path)
    output_args(item)

    item = commands.add_parser("request-human-approval", help="Freeze a hash-bound request for a human-controlled stage.")
    item.add_argument("policy_file", type=Path)
    item.add_argument("stage")
    item.add_argument("project_id")
    item.add_argument("output", type=Path)
    item.add_argument("--evidence", action="append", type=Path, default=[])
    item.add_argument("--force", action="store_true")
    output_args(item)

    item = commands.add_parser("approve-human-stage", help="Record HUMAN_APPROVED in the separate human ledger; optionally require HMAC proof.")
    item.add_argument("policy_file", type=Path)
    item.add_argument("request", type=Path)
    item.add_argument("ledger", type=Path)
    item.add_argument("--human-id", required=True)
    item.add_argument("--agent-ledger", type=Path, required=True)
    item.add_argument("--secret-file", type=Path)
    item.add_argument("--key-id")
    output_args(item)

    item = commands.add_parser("validate-approvals", help="Validate ledger chains, evidence hashes, actors, and all stages through a target.")
    item.add_argument("policy_file", type=Path)
    item.add_argument("agent_ledger", type=Path)
    item.add_argument("--target-stage", required=True)
    item.add_argument("--human-ledger", type=Path)
    item.add_argument("--human-secret-file", type=Path)
    output_args(item)

    item = commands.add_parser("freeze-project", help="Write a non-destructive project copy with current artifact SHA-256 hashes.")
    item.add_argument("project", type=Path)
    item.add_argument("output", type=Path)
    item.add_argument("--force", action="store_true")
    output_args(item)

    item = commands.add_parser("validate-project", help="Execute and aggregate the validation project contract.")
    item.add_argument("project", type=Path)
    output_args(item)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "doctor":
            result = run_doctor(args.require)
            result["profile"] = args.profile
        elif args.command == "audit-mesh":
            result = audit_mesh(args.mesh, policy(args.policy), args.profile)
        elif args.command == "compare-meshes":
            result = compare_meshes(args.reference, args.candidate, policy(args.policy), args.profile)
        elif args.command == "check-interfaces":
            result = validate_contract(args.contract, args.profile)
        elif args.command == "analyze-gcode":
            result = analyze_gcode(args.gcode, policy(args.policy), args.profile)
        elif args.command == "validate-3mf":
            result = validate_3mf(args.file, policy(args.policy), args.profile)
        elif args.command == "run-sweep":
            result = run_sweep(args.manifest, args.output_root, args.profile)
        elif args.command == "validate-skill":
            result = validate_skill(args.skill, args.runtime, args.profile)
        elif args.command == "validate-profile":
            result = validate_profile(args.profile_file, args.profile)
        elif args.command == "init-autonomy":
            result = init_policy(args.project_id, args.mode, args.authorized_by, args.output, force=args.force)
            result["profile"] = args.profile
        elif args.command == "validate-autonomy":
            result = validate_policy(args.policy_file, args.profile)
        elif args.command == "approve-agent-stage":
            result = approve_agent_stage(
                args.policy_file,
                args.ledger,
                args.stage,
                agent_id=args.agent_id,
                model_id=args.model_id,
                evidence=args.evidence,
                attestation=args.attestation,
                human_ledger_path=args.human_ledger,
            )
            result["profile"] = args.profile
        elif args.command == "request-human-approval":
            result = request_human_approval(args.policy_file, args.stage, args.project_id, args.evidence, args.output, force=args.force)
            result["profile"] = args.profile
        elif args.command == "approve-human-stage":
            result = approve_human_stage(
                args.policy_file,
                args.request,
                args.ledger,
                human_id=args.human_id,
                agent_ledger_path=args.agent_ledger,
                secret_file=args.secret_file,
                key_id=args.key_id,
            )
            result["profile"] = args.profile
        elif args.command == "validate-approvals":
            result = validate_approvals(
                args.policy_file,
                args.agent_ledger,
                target_stage=args.target_stage,
                human_ledger_path=args.human_ledger,
                human_secret_file=args.human_secret_file,
                profile=args.profile,
            )
        elif args.command == "freeze-project":
            result = freeze_project(args.project, args.output, force=args.force, profile=args.profile)
        elif args.command == "validate-project":
            result = validate_project(args.project, args.profile)
        else:  # pragma: no cover
            raise ValueError(f"unknown command {args.command}")
    except Exception as exc:
        result = report(args.command, [check("unhandled-error", "FAIL", f"{type(exc).__name__}: {exc}")], profile=getattr(args, "profile", "release"))
    rendered = write_json(args.json_out, result)
    sys.stdout.write(rendered)
    return exit_code(result["status"], getattr(args, "profile", "release"))


if __name__ == "__main__":
    raise SystemExit(main())
