#!/usr/bin/env python3
"""Compile a validated FlowPrint classification into a non-installed Skill draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_CLASSIFICATION_VALIDATOR = HERE / "validate_classification.py"
DEFAULT_DRAFT_VALIDATOR = HERE / "validate_generated_skill.py"
SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def proposed_name(candidate: str) -> str:
    ascii_words = re.findall(r"[a-z0-9]+", candidate.lower())
    slug = "-".join(ascii_words)[:64].strip("-")
    if slug and SKILL_NAME.fullmatch(slug):
        return slug
    return f"flowprint-{sha256_text(candidate)[:10]}"


def run_validator(validator: Path, classification: Path) -> tuple[int, dict[str, Any], str]:
    if not validator.is_file():
        return 2, {"valid": False, "errors": [f"validator not found: {validator}"]}, ""
    result = subprocess.run(
        [sys.executable, str(validator), str(classification), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        report = json.loads(result.stdout) if result.stdout.strip() else {
            "valid": False,
            "errors": ["validator returned no JSON report"],
        }
    except json.JSONDecodeError:
        report = {"valid": False, "errors": ["validator returned invalid JSON"]}
    return result.returncode, report, result.stderr


def markdown_list(items: list[dict[str, Any]], field: str = "statement") -> str:
    if not items:
        return "- None recorded."
    return "\n".join(f"- {item[field]} (`{item['id']}`)" for item in items)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def generated_description(document: dict[str, Any]) -> str:
    """Build trigger metadata without claiming that the workflow was validated in the field."""
    workflow = document["workflow"]
    trigger = workflow.get("trigger")
    if isinstance(trigger, dict):
        summary = " ".join(str(trigger.get("summary", "")).split())
        when_to_use = [" ".join(str(value).split()) for value in trigger.get("when_to_use", [])]
        do_not_use = [" ".join(str(value).split()) for value in trigger.get("do_not_use", [])]
        description = summary
        if when_to_use:
            description += " Use when the user asks for: " + "; ".join(when_to_use) + "."
        if do_not_use:
            description += " Do not use for: " + "; ".join(do_not_use) + "."
        return description
    candidate = workflow["candidate_name"]
    return (
        f"Run the {candidate} workflow by collecting current inputs, applying its reusable steps, "
        "and enforcing recorded permission boundaries. Use only when the user explicitly requests "
        "this named workflow or invokes the generated Skill."
    )


def artifact_record(
    stage: Path,
    relative_path: str,
    item_ids: list[str],
    kind: str,
    profile_ids: list[str] | None = None,
) -> dict[str, Any]:
    path = stage / relative_path
    return {
        "path": relative_path,
        "kind": kind,
        "depends_on_item_ids": sorted(item_ids),
        "depends_on_profile_ids": sorted(profile_ids or []),
        "sha256": sha256_file(path),
        "state": "current",
    }


def build_draft(
    document: dict[str, Any],
    stage: Path,
    skill_name: str,
    revision_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    items_by_layer = {
        layer: [item for item in document["items"] if item["layer"] == layer]
        for layer in (
            "core",
            "domain",
            "profile",
            "run_parameter",
            "failure_lesson",
            "permission_boundary",
        )
    }
    candidate = document["workflow"]["candidate_name"]
    description = generated_description(document)
    core_lines = [f"{index}. {item['statement']}" for index, item in enumerate(items_by_layer["core"], start=1)]
    if not core_lines:
        core_lines = ["1. Load the references and ask for the current run parameters before proceeding."]

    skill_md = f"""---
name: {skill_name}
description: {json.dumps(description, ensure_ascii=False)}
---

# {candidate}

## Workflow

{chr(10).join(core_lines)}

## Load only what is needed

- Read `references/domain-knowledge.md` when platform or format constraints apply.
- Read `profiles/default.json` before checking named-entity identity or stable preferences.
- Read `references/run-parameters.md` to collect values that may change on this run.
- Read `references/failure-lessons.md` before quality assurance or recovery.
- Always read `references/permission-boundaries.md` before any external, account-specific, or irreversible action.

## Safety boundary

Preparing a result does not authorize an external, account-specific, or irreversible action. Before any action listed in `references/permission-boundaries.md`, obtain fresh and explicit authorization for that action. If authorization is absent or ambiguous, stop after preparing a preview.
"""
    write_text(stage / "SKILL.md", skill_md)

    write_text(
        stage / "references" / "domain-knowledge.md",
        f"# Domain Knowledge\n\n{markdown_list(items_by_layer['domain'])}",
    )
    write_text(
        stage / "references" / "run-parameters.md",
        "# Run Parameters\n\nValues below are examples from the source task and must be reconfirmed for each run.\n\n"
        + markdown_list(items_by_layer["run_parameter"]),
    )
    failure_lines = []
    for item in items_by_layer["failure_lesson"]:
        failure_lines.extend(
            [
                f"## {item['statement']}",
                "",
                f"Prevention or recovery rule: {item['abstracted_rule']}",
                "",
                f"Source item: `{item['id']}`",
                "",
            ]
        )
    write_text(
        stage / "references" / "failure-lessons.md",
        "# Failure Lessons\n\n" + ("\n".join(failure_lines) if failure_lines else "- None recorded."),
    )
    write_text(
        stage / "references" / "permission-boundaries.md",
        "# Permission Boundaries\n\nThese are decision gates, not durable authorization.\n\n"
        + markdown_list(items_by_layer["permission_boundary"]),
    )

    profile_version = int(revision_receipt.get("profile_version", 1)) if revision_receipt else 1
    revision_sequence = int(revision_receipt.get("revision_sequence", 0)) if revision_receipt else 0
    profile = {
        "schema_version": "0.1",
        "profile_id": "default",
        "version": profile_version,
        "fields": [
            {
                "field_id": item["id"],
                "value": item["statement"],
                "source_item_id": item["id"],
                "impact": item["impact"],
            }
            for item in items_by_layer["profile"]
        ],
    }
    write_text(stage / "profiles" / "default.json", json.dumps(profile, ensure_ascii=False, indent=2))

    short_description = " ".join(description.split())[:96].replace(chr(34), chr(39))
    openai_yaml = f'''interface:\n  display_name: "{candidate.replace(chr(34), chr(39))[:64]}"\n  short_description: "{short_description}"\n  default_prompt: "Use ${skill_name} for this task, collect current run parameters, and stay within its workflow boundary."\npolicy:\n  allow_implicit_invocation: true\n'''
    write_text(stage / "agents" / "openai.yaml", openai_yaml)

    active_profile_ids = ["default"] if items_by_layer["profile"] else []
    artifact_specs = [
        ("SKILL.md", [item["id"] for item in items_by_layer["core"] + items_by_layer["permission_boundary"]], "skill", active_profile_ids),
        ("agents/openai.yaml", [item["id"] for item in items_by_layer["core"]], "ui_metadata", []),
        ("references/domain-knowledge.md", [item["id"] for item in items_by_layer["domain"]], "domain", []),
        ("references/run-parameters.md", [item["id"] for item in items_by_layer["run_parameter"]], "run_parameters", []),
        ("references/failure-lessons.md", [item["id"] for item in items_by_layer["failure_lesson"]], "failure_lessons", []),
        ("references/permission-boundaries.md", [item["id"] for item in items_by_layer["permission_boundary"]], "permission_boundaries", []),
        ("profiles/default.json", [item["id"] for item in items_by_layer["profile"]], "profile", []),
    ]
    artifacts = [artifact_record(stage, path, ids, kind, profiles) for path, ids, kind, profiles in artifact_specs]
    item_records = [
        {
            "item_id": item["id"],
            "layer": item["layer"],
            "impact": item["impact"],
            "fingerprint": sha256_text(canonical_json(item)),
        }
        for item in document["items"]
    ]
    edges = [
        {"from_item_id": item_id, "to_artifact": artifact["path"]}
        for artifact in artifacts
        for item_id in artifact["depends_on_item_ids"]
    ]
    profile_edges = [
        {"from_profile_id": profile_id, "from_version": profile_version, "to_artifact": artifact["path"]}
        for artifact in artifacts
        for profile_id in artifact["depends_on_profile_ids"]
    ]
    manifest = {
        "schema_version": "0.1",
        "skill": {
            "name": skill_name,
            "candidate_name": candidate,
            "version": f"0.1.0-draft.r{revision_sequence}" if revision_receipt else "0.1.0-draft",
            "compile_state": "draft",
            "install_state": "not_authorized",
            "workflow_definition_fingerprint": sha256_text(canonical_json({
                "scope": document["workflow"].get("scope"),
                "trigger": document["workflow"].get("trigger"),
            })),
        },
        "source": {
            "classification_schema_version": document["schema_version"],
            "classification_sha256": sha256_text(canonical_json(document)),
            "raw_transcript_stored": False,
        },
        "permissions": {
            "draft_generation_authorized": True,
            "installation_authorized": False,
            "external_actions_authorized": False,
        },
        "dependency_graph": {
            "items": item_records,
            "profiles": [{
                "profile_id": "default",
                "version": profile_version,
                "item_ids": [item["id"] for item in items_by_layer["profile"]],
            }],
            "artifacts": artifacts,
            "edges": edges,
            "profile_edges": profile_edges,
        },
        "required_revalidation": [
            "classification_contract",
            "workflow_scope_check",
            "generated_skill_preflight",
            "profile_dependency_check",
            "permission_boundary_check",
        ],
    }
    workflow_scope = document["workflow"].get("scope")
    if isinstance(workflow_scope, dict):
        manifest["workflow_scope"] = {
            "status": workflow_scope["status"],
            "candidate_ids": [candidate["id"] for candidate in workflow_scope["candidates"]],
            "selected_candidate_id": workflow_scope["selected_candidate_id"],
            "selection_confirmation_bound": workflow_scope["status"] == "user_selected"
            and workflow_scope.get("selection_confirmation", {}).get("confirmed_by") == "user",
        }
    if revision_receipt:
        manifest["source"]["revision_id"] = revision_receipt["revision_id"]
        manifest["revision"] = {
            "revision_id": revision_receipt["revision_id"],
            "sequence": revision_sequence,
            "base_draft_path": revision_receipt["base"]["draft_path"],
            "base_manifest_sha256": revision_receipt["base"]["manifest_sha256"],
            "receipt_sha256": sha256_text(canonical_json(revision_receipt)),
            "changed_item_ids": revision_receipt["impact"]["changed_item_ids"],
            "added_item_ids": revision_receipt["impact"]["added_item_ids"],
            "removed_item_ids": revision_receipt["impact"]["removed_item_ids"],
            "stale_artifacts_rebuilt": revision_receipt["impact"]["stale_artifacts"],
            "full_revalidation_performed": revision_receipt["impact"]["full_revalidation_required"],
        }
    write_text(stage / "flowprint-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def validate_revision_receipt(
    document: dict[str, Any],
    receipt_path: Path | None,
    output: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    revision_id = document.get("source", {}).get("revision_id")
    if not revision_id and receipt_path is None:
        return None, []
    if not revision_id:
        return None, ["revision receipt supplied for a non-revision classification"]
    if receipt_path is None:
        return None, ["revision classification requires a matching revision receipt"]
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        return None, [str(error)]
    errors: list[str] = []
    if receipt.get("schema_version") != "0.1" or receipt.get("status") != "confirmed_revision":
        errors.append("unsupported or unconfirmed revision receipt")
    if receipt.get("revision_id") != revision_id:
        errors.append("revision receipt does not match classification revision_id")
    if receipt.get("classification_sha256") != sha256_text(canonical_json(document)):
        errors.append("classification changed after user confirmation")
    if receipt.get("confirmed_by") != "user":
        errors.append("revision receipt is not bound to user confirmation")
    if receipt.get("installation_authorized") is not False or receipt.get("external_actions_authorized") is not False:
        errors.append("revision receipt may not authorize installation or external actions")
    try:
        plan_path = Path(receipt["revision_plan_path"])
        confirmation_path = Path(receipt["confirmation_path"])
        if not plan_path.is_file() or sha256_file(plan_path) != receipt.get("revision_plan_sha256"):
            errors.append("revision plan is missing or changed after confirmation")
            plan = {}
        else:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if not confirmation_path.is_file() or sha256_file(confirmation_path) != receipt.get("confirmation_sha256"):
            errors.append("user confirmation record is missing or changed")
        for field in ("revision_id", "revision_sequence", "impact"):
            if receipt.get(field) != plan.get(field):
                errors.append(f"revision receipt field {field!r} does not match revision plan")
        if receipt.get("profile_version") != plan.get("profile_version_after_confirmation"):
            errors.append("revision receipt profile version does not match revision plan")
        if receipt.get("base") != plan.get("base"):
            errors.append("revision receipt base binding does not match revision plan")
    except (KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid revision audit binding: {error}")
    base = receipt.get("base", {})
    try:
        base_manifest = Path(base["manifest_path"])
        base_draft = Path(base["draft_path"])
        if not base_manifest.is_file() or sha256_file(base_manifest) != base.get("manifest_sha256"):
            errors.append("base manifest is missing or changed after confirmation")
        if output.resolve() == base_draft.resolve():
            errors.append("revision output must not overwrite the base draft")
    except (KeyError, TypeError, OSError) as error:
        errors.append(f"invalid base draft binding: {error}")
    return receipt, errors


def compile_document(
    classification: Path,
    output: Path,
    skill_name: str | None,
    classification_validator: Path,
    draft_validator: Path,
    revision_receipt_path: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if output.exists():
        return 2, {"status": "rejected", "errors": [f"output already exists: {output}"]}

    validator_exit, validator_report, validator_stderr = run_validator(classification_validator, classification)
    if validator_exit != 0 or not validator_report.get("valid"):
        return 1, {
            "status": "rejected",
            "gate": "classification_validation",
            "validator_exit_code": validator_exit,
            "errors": validator_report.get("errors", []) or [validator_stderr.strip() or "classification validation failed"],
        }

    try:
        document = json.loads(classification.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        return 1, {"status": "rejected", "gate": "classification_read", "errors": [str(error)]}

    if document.get("schema_version") not in {"0.3", "0.4"}:
        return 1, {
            "status": "rejected",
            "gate": "confirmation_schema",
            "errors": [
                "Node 5 compilation requires legacy schema_version '0.3' or "
                "workflow-scoped schema_version '0.4' with explicit confirmation records"
            ],
        }
    workflow_scope = document.get("workflow", {}).get("scope")
    if document.get("schema_version") == "0.4":
        scope_status = workflow_scope.get("status") if isinstance(workflow_scope, dict) else None
        if scope_status == "needs_user_selection":
            return 1, {
                "status": "rejected",
                "gate": "workflow_selection",
                "errors": ["multiple workflow candidates require an explicit user selection before classification or compilation"],
            }
        if scope_status not in {"single_candidate", "user_selected"}:
            return 1, {
                "status": "rejected",
                "gate": "workflow_selection",
                "errors": ["workflow scope is not resolved"],
            }
    if document.get("gates", {}).get("decision") != "ready":
        return 1, {"status": "rejected", "gate": "review_decision", "errors": ["classification is not ready"]}

    revision_receipt, revision_errors = validate_revision_receipt(
        document, revision_receipt_path, output
    )
    if revision_errors:
        return 1, {"status": "rejected", "gate": "revision_receipt", "errors": revision_errors}

    selected_name = skill_name or proposed_name(document["workflow"]["candidate_name"])
    if not SKILL_NAME.fullmatch(selected_name):
        return 2, {"status": "rejected", "errors": ["skill name must use lowercase letters, digits, and hyphens"]}

    output_parent = output.resolve().parent
    output_parent.mkdir(parents=True, exist_ok=True)
    stage = output_parent / f".{output.name}.flowprint-tmp-{uuid.uuid4().hex}"
    try:
        stage.mkdir(parents=False, exist_ok=False)
        manifest = build_draft(document, stage, selected_name, revision_receipt)
        if not draft_validator.is_file():
            raise RuntimeError(f"draft validator not found: {draft_validator}")
        preflight = subprocess.run(
            [sys.executable, str(draft_validator), str(stage), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            preflight_report = json.loads(preflight.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"draft validator returned invalid JSON: {error}") from error
        if preflight.returncode != 0 or not preflight_report.get("valid"):
            raise RuntimeError("generated draft preflight failed: " + "; ".join(preflight_report.get("errors", [])))

        compile_record = {
            "schema_version": "0.1",
            "status": "compiled_draft",
            "classification_validator": {
                "executed": True,
                "exit_code": validator_exit,
                "error_count": validator_report.get("error_count", 0),
            },
            "draft_preflight": {
                "executed": True,
                "exit_code": preflight.returncode,
                "error_count": preflight_report.get("error_count", 0),
                "scope": "FlowPrint structural preflight; not official marketplace certification",
            },
            "workflow_selection": {
                "executed": document.get("schema_version") == "0.4",
                "scope_status": workflow_scope.get("status") if isinstance(workflow_scope, dict) else "legacy_single_candidate",
                "candidate_count": len(workflow_scope.get("candidates", [])) if isinstance(workflow_scope, dict) else 1,
                "selected_candidate_id": workflow_scope.get("selected_candidate_id") if isinstance(workflow_scope, dict) else None,
                "user_selection_bound": (
                    workflow_scope.get("status") == "user_selected"
                    and workflow_scope.get("selection_confirmation", {}).get("confirmed_by") == "user"
                ) if isinstance(workflow_scope, dict) else False,
            },
            "install_performed": False,
            "external_action_performed": False,
        }
        if revision_receipt:
            compile_record["revision_gate"] = {
                "executed": True,
                "revision_id": revision_receipt["revision_id"],
                "receipt_path": str(revision_receipt_path),
                "classification_hash_matched": True,
                "base_manifest_hash_matched": True,
                "base_draft_overwrite_prevented": True,
            }
        write_text(stage / "compile-record.json", json.dumps(compile_record, ensure_ascii=False, indent=2))
        stage.replace(output)
        return 0, {
            "status": "compiled_draft",
            "output": str(output),
            "skill_name": selected_name,
            "manifest": str(output / "flowprint-manifest.json"),
            "install_state": manifest["skill"]["install_state"],
            "install_performed": False,
        }
    except Exception as error:  # fail closed and remove only this invocation's private staging directory
        if stage.exists():
            shutil.rmtree(stage)
        return 1, {"status": "rejected", "gate": "draft_build", "errors": [str(error)]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("classification", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--skill-name")
    parser.add_argument("--classification-validator", type=Path, default=DEFAULT_CLASSIFICATION_VALIDATOR)
    parser.add_argument("--draft-validator", type=Path, default=DEFAULT_DRAFT_VALIDATOR)
    parser.add_argument("--revision-receipt", type=Path)
    args = parser.parse_args()
    code, result = compile_document(
        args.classification,
        args.output,
        args.skill_name,
        args.classification_validator,
        args.draft_validator,
        args.revision_receipt,
    )
    stream = sys.stdout if code == 0 else sys.stderr
    print(json.dumps(result, ensure_ascii=False, indent=2), file=stream)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
