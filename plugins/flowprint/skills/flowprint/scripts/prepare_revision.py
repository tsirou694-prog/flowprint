#!/usr/bin/env python3
"""Prepare a fail-closed FlowPrint revision without changing the compiled base draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from analyze_impact import analyze_documents, canonical_json


HERE = Path(__file__).resolve().parent
DEFAULT_VALIDATOR = HERE / "validate_classification.py"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_document(document: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(document).encode("utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(path: Path, validator: Path) -> tuple[int, dict[str, Any]]:
    result = subprocess.run(
        [sys.executable, str(validator), str(path), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {"valid": False, "errors": ["validator returned invalid JSON"]}
    return result.returncode, report


def prepare_revision(
    manifest_path: Path,
    candidate_path: Path,
    output: Path,
    validator: Path,
) -> tuple[int, dict[str, Any]]:
    if output.exists():
        return 2, {"status": "rejected", "gate": "output_exists", "errors": [str(output)]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as error:
        return 1, {"status": "rejected", "gate": "revision_input", "errors": [str(error)]}

    validation_exit, validation = validate(candidate_path, validator)
    if validation_exit != 0 or not validation.get("valid"):
        return 1, {
            "status": "rejected",
            "gate": "classification_validation",
            "validator_exit_code": validation_exit,
            "errors": validation.get("errors", []),
        }

    impact = analyze_documents(manifest, candidate)
    if impact["status"] == "no_change":
        return 3, {
            "status": "rejected",
            "gate": "no_change",
            "errors": ["candidate is identical to the compiled dependency graph"],
        }

    base_manifest_hash = sha256_file(manifest_path)
    candidate_hash = sha256_document(candidate)
    revision_id = "rev-" + sha256_bytes(
        f"{base_manifest_hash}:{candidate_hash}".encode("utf-8")
    )[:16]
    previous_revision = manifest.get("revision", {}).get("sequence", 0)
    revision_sequence = int(previous_revision) + 1

    review_items = set(candidate["gates"]["review_item_ids"])
    affected = set(
        impact["changed_item_ids"] + impact["added_item_ids"] + impact["removed_item_ids"]
    )
    affected_review_items = sorted(review_items & affected)
    questions = candidate["gates"]["questions"]
    if impact["full_revalidation_required"]:
        required_questions = list(questions)
    else:
        required_questions = [
            question for question in questions
            if affected & set(question["item_ids"])
        ]
    required_question_ids = [question["id"] for question in required_questions]
    required_question_map = {
        question["id"]: list(question["item_ids"])
        for question in required_questions
    }

    review_document = json.loads(json.dumps(candidate, ensure_ascii=False))
    source = review_document.setdefault("source", {})
    source["revision_id"] = revision_id
    source["revision_status"] = "needs_confirmation"
    confirmations = review_document["gates"].get("confirmations", [])
    stale_confirmation_ids = [
        confirmation.get("id", "")
        for confirmation in confirmations
        if confirmation.get("question_id") in required_question_ids
    ]
    review_document["gates"]["confirmations"] = [
        confirmation for confirmation in confirmations
        if confirmation.get("question_id") not in required_question_ids
    ]
    confirmed_item_ids = {
        item_id
        for confirmation in review_document["gates"]["confirmations"]
        if confirmation.get("accepted") is True and confirmation.get("confirmed_by") == "user"
        for item_id in confirmation.get("item_ids", [])
    }
    review_document["gates"]["decision"] = (
        "ready" if confirmed_item_ids == review_items else "needs_review"
    )

    base_profiles = manifest.get("dependency_graph", {}).get("profiles", [])
    base_profile_version = int(base_profiles[0].get("version", 1)) if base_profiles else 1
    next_profile_version = base_profile_version + 1 if impact["profile_stale"] else base_profile_version
    base_draft_path = manifest_path.resolve().parent
    plan = {
        "schema_version": "0.1",
        "status": "needs_confirmation",
        "revision_id": revision_id,
        "revision_sequence": revision_sequence,
        "base": {
            "draft_path": str(base_draft_path),
            "manifest_path": str(manifest_path.resolve()),
            "manifest_sha256": base_manifest_hash,
            "profile_version": base_profile_version,
        },
        "candidate": {
            "source_path": str(candidate_path.resolve()),
            "source_sha256": sha256_file(candidate_path),
            "canonical_sha256": candidate_hash,
        },
        "impact": impact,
        "affected_review_item_ids": affected_review_items,
        "stale_confirmation_ids": sorted(value for value in stale_confirmation_ids if value),
        "required_question_ids": required_question_ids,
        "required_question_item_ids": required_question_map,
        "profile_version_after_confirmation": next_profile_version,
        "permissions": {
            "installation_authorized": False,
            "external_actions_authorized": False,
        },
    }

    output_parent = output.resolve().parent
    output_parent.mkdir(parents=True, exist_ok=True)
    stage = output_parent / f".{output.name}.flowprint-revision-{uuid.uuid4().hex}"
    try:
        stage.mkdir(parents=False, exist_ok=False)
        write_json(stage / "classification.review.json", review_document)
        review_exit, review_validation = validate(stage / "classification.review.json", validator)
        if review_exit != 0 or not review_validation.get("valid"):
            raise RuntimeError("prepared review classification is invalid: " + "; ".join(review_validation.get("errors", [])))
        plan["review_classification_sha256"] = sha256_document(review_document)
        write_json(stage / "impact-report.json", impact)
        write_json(stage / "revision-plan.json", plan)
        stage.replace(output)
    except Exception as error:
        if stage.exists():
            shutil.rmtree(stage)
        return 1, {"status": "rejected", "gate": "revision_prepare", "errors": [str(error)]}

    return 0, {
        "status": "needs_confirmation",
        "revision_id": revision_id,
        "revision_directory": str(output),
        "changed_item_ids": impact["changed_item_ids"],
        "stale_artifacts": impact["stale_artifacts"],
        "stale_confirmation_ids": plan["stale_confirmation_ids"],
        "required_question_ids": required_question_ids,
        "full_revalidation_required": impact["full_revalidation_required"],
        "base_draft_unchanged": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--validator", type=Path, default=DEFAULT_VALIDATOR)
    args = parser.parse_args()
    code, report = prepare_revision(args.manifest, args.candidate, args.output, args.validator)
    print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stdout if code == 0 else sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
