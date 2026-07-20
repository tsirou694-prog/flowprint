#!/usr/bin/env python3
"""Bind explicit user confirmation to one prepared FlowPrint revision."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_VALIDATOR = HERE / "validate_classification.py"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_document(document: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(document).encode("utf-8"))


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def finalize_revision(
    revision_directory: Path,
    confirmation_path: Path,
    validator: Path,
) -> tuple[int, dict[str, Any]]:
    ready_path = revision_directory / "classification.ready.json"
    receipt_path = revision_directory / "revision-receipt.json"
    if ready_path.exists() or receipt_path.exists():
        return 2, {
            "status": "rejected",
            "gate": "already_finalized",
            "errors": ["revision finalization outputs already exist"],
        }
    try:
        plan_path = revision_directory / "revision-plan.json"
        review_path = revision_directory / "classification.review.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        document = json.loads(review_path.read_text(encoding="utf-8"))
        confirmation = json.loads(confirmation_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        return 1, {"status": "rejected", "gate": "revision_confirmation", "errors": [str(error)]}

    errors: list[str] = []
    revision_id = plan.get("revision_id")
    if document.get("source", {}).get("revision_id") != revision_id:
        errors.append("review classification revision_id does not match revision plan")
    if sha256_document(document) != plan.get("review_classification_sha256"):
        errors.append("review classification changed after impact analysis")
    if confirmation.get("revision_id") != revision_id:
        errors.append("confirmation revision_id does not match this revision")
    if confirmation.get("confirmed_by") != "user":
        errors.append("overall confirmation must use confirmed_by 'user'")
    if confirmation.get("accepted") is not True:
        errors.append("overall revision confirmation must be explicitly accepted")
    if not isinstance(confirmation.get("answer"), str) or not confirmation["answer"].strip():
        errors.append("overall confirmation answer must record the user's actual response")

    answers = confirmation.get("questions")
    if not isinstance(answers, list):
        errors.append("confirmation questions must be an array")
        answers = []
    expected_ids = set(plan.get("required_question_ids", []))
    answer_ids = {answer.get("question_id") for answer in answers if isinstance(answer, dict)}
    if answer_ids != expected_ids:
        errors.append(f"confirmation question ids must exactly match {sorted(expected_ids)}")
    expected_map = plan.get("required_question_item_ids", {})
    for answer in answers:
        if not isinstance(answer, dict):
            errors.append("every confirmation question answer must be an object")
            continue
        question_id = answer.get("question_id")
        if answer.get("confirmed_by") != "user" or answer.get("accepted") is not True:
            errors.append(f"question {question_id!r} requires explicit accepted user confirmation")
        if not isinstance(answer.get("answer"), str) or not answer["answer"].strip():
            errors.append(f"question {question_id!r} must record the user's actual answer")
        if answer.get("item_ids") != expected_map.get(question_id):
            errors.append(f"question {question_id!r} item_ids do not match the prepared revision")

    base_manifest = Path(plan.get("base", {}).get("manifest_path", ""))
    if not base_manifest.is_file() or sha256_file(base_manifest) != plan.get("base", {}).get("manifest_sha256"):
        errors.append("base manifest is missing or changed after revision preparation")
    if errors:
        return 1, {"status": "rejected", "gate": "revision_confirmation", "errors": errors}

    required_ids = set(plan["required_question_ids"])
    confirmations = [
        item for item in document["gates"].get("confirmations", [])
        if item.get("question_id") not in required_ids
    ]
    for index, answer in enumerate(answers, start=1):
        confirmations.append({
            "id": f"revision-{plan['revision_sequence']}-confirmation-{index}",
            "question_id": answer["question_id"],
            "item_ids": answer["item_ids"],
            "confirmed_by": "user",
            "accepted": True,
            "answer": answer["answer"],
        })
    document["gates"]["confirmations"] = confirmations
    document["gates"]["decision"] = "ready"
    document["source"]["revision_status"] = "confirmed"

    stage = revision_directory / f".finalize-{uuid.uuid4().hex}"
    stage.mkdir(parents=False, exist_ok=False)
    temporary_classification = stage / "classification.ready.json"
    atomic_write_json(temporary_classification, document)
    result = subprocess.run(
        [sys.executable, str(validator), str(temporary_classification), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        validation = json.loads(result.stdout)
    except json.JSONDecodeError:
        validation = {"valid": False, "errors": ["validator returned invalid JSON"]}
    if result.returncode != 0 or not validation.get("valid"):
        shutil.rmtree(stage)
        return 1, {
            "status": "rejected",
            "gate": "final_classification_validation",
            "errors": validation.get("errors", []),
        }

    classification_hash = sha256_document(document)
    receipt = {
        "schema_version": "0.1",
        "status": "confirmed_revision",
        "revision_id": revision_id,
        "revision_sequence": plan["revision_sequence"],
        "classification_sha256": classification_hash,
        "revision_plan_path": str(plan_path.resolve()),
        "revision_plan_sha256": sha256_file(plan_path),
        "confirmation_path": str(confirmation_path.resolve()),
        "confirmation_sha256": sha256_file(confirmation_path),
        "base": plan["base"],
        "impact": plan["impact"],
        "profile_version": plan["profile_version_after_confirmation"],
        "confirmed_by": "user",
        "installation_authorized": False,
        "external_actions_authorized": False,
    }
    temporary_receipt = stage / "revision-receipt.json"
    atomic_write_json(temporary_receipt, receipt)
    try:
        temporary_receipt.replace(receipt_path)
        temporary_classification.replace(ready_path)
        shutil.rmtree(stage)
    except Exception as error:
        ready_path.unlink(missing_ok=True)
        receipt_path.unlink(missing_ok=True)
        if stage.exists():
            shutil.rmtree(stage)
        return 1, {"status": "rejected", "gate": "revision_commit", "errors": [str(error)]}
    return 0, {
        "status": "confirmed_revision",
        "revision_id": revision_id,
        "classification": str(ready_path),
        "receipt": str(receipt_path),
        "classification_sha256": classification_hash,
        "profile_version": receipt["profile_version"],
        "installation_authorized": False,
        "external_actions_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision_directory", type=Path)
    parser.add_argument("confirmation", type=Path)
    parser.add_argument("--validator", type=Path, default=DEFAULT_VALIDATOR)
    args = parser.parse_args()
    code, report = finalize_revision(args.revision_directory, args.confirmation, args.validator)
    print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stdout if code == 0 else sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
