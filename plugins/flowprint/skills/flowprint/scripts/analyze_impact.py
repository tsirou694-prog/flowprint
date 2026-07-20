#!/usr/bin/env python3
"""Compare a compiled FlowPrint manifest with an edited classification and mark stale outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
LAYER_ARTIFACTS = {
    "core": {"SKILL.md", "agents/openai.yaml"},
    "domain": {"references/domain-knowledge.md"},
    "profile": {"profiles/default.json", "SKILL.md"},
    "run_parameter": {"references/run-parameters.md"},
    "failure_lesson": {"references/failure-lessons.md"},
    "permission_boundary": {"references/permission-boundaries.md", "SKILL.md"},
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def analyze_documents(manifest: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic dependency impact report for two parsed documents."""
    old_items = {
        item["item_id"]: item
        for item in manifest["dependency_graph"]["items"]
    }
    new_items = {item["id"]: item for item in classification["items"]}
    new_fingerprints = {item_id: fingerprint(item) for item_id, item in new_items.items()}
    changed = sorted(
        item_id for item_id in old_items.keys() & new_items.keys()
        if old_items[item_id]["fingerprint"] != new_fingerprints[item_id]
    )
    added = sorted(new_items.keys() - old_items.keys())
    removed = sorted(old_items.keys() - new_items.keys())
    affected_item_ids = set(changed + added + removed)
    stale_artifact_set = {
        artifact["path"]
        for artifact in manifest["dependency_graph"]["artifacts"]
        if affected_item_ids & set(artifact["depends_on_item_ids"])
    }
    profile_changed = any(
        item_id in affected_item_ids
        and ((new_items.get(item_id) or old_items.get(item_id, {})).get("layer") == "profile")
        for item_id in affected_item_ids
    )
    if profile_changed:
        stale_artifact_set.update(
            artifact["path"]
            for artifact in manifest["dependency_graph"]["artifacts"]
            if artifact.get("depends_on_profile_ids")
        )
    for item_id in added:
        stale_artifact_set.update(LAYER_ARTIFACTS.get(new_items[item_id]["layer"], set()))
    stale_artifacts = sorted(stale_artifact_set)
    workflow_name_changed = (
        manifest.get("skill", {}).get("candidate_name")
        != classification.get("workflow", {}).get("candidate_name")
    )
    previous_workflow_fingerprint = manifest.get("skill", {}).get("workflow_definition_fingerprint")
    current_workflow_fingerprint = fingerprint({
        "scope": classification.get("workflow", {}).get("scope"),
        "trigger": classification.get("workflow", {}).get("trigger"),
    })
    workflow_definition_changed = (
        previous_workflow_fingerprint is not None
        and previous_workflow_fingerprint != current_workflow_fingerprint
    ) or (
        previous_workflow_fingerprint is None
        and classification.get("schema_version") == "0.4"
    )
    workflow_changed = workflow_name_changed or workflow_definition_changed
    if workflow_changed:
        stale_artifact_set.update({"SKILL.md", "agents/openai.yaml"})
        stale_artifacts = sorted(stale_artifact_set)
    high_or_core_change = any(
        item_id in changed + added
        and (new_items[item_id]["layer"] == "core" or new_items[item_id]["impact"] == "high")
        for item_id in new_items
    ) or any(
        item_id in removed
        and (old_items[item_id]["layer"] == "core" or old_items[item_id]["impact"] == "high")
        for item_id in old_items
    )
    changed_document_fields: list[str] = []
    if workflow_name_changed:
        changed_document_fields.append("workflow.candidate_name")
    if workflow_definition_changed:
        changed_document_fields.append("workflow.scope_or_trigger")
    return {
        "status": "changes_detected" if affected_item_ids or workflow_changed else "no_change",
        "changed_document_fields": changed_document_fields,
        "changed_item_ids": changed,
        "added_item_ids": added,
        "removed_item_ids": removed,
        "stale_artifacts": stale_artifacts,
        "profile_stale": profile_changed,
        "full_revalidation_required": high_or_core_change or workflow_changed,
        "tests_to_rerun": [
            "classification_contract",
            "workflow_scope_check",
            "generated_skill_preflight",
            "profile_dependency_check",
            "permission_boundary_check",
        ] if affected_item_ids or workflow_changed else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("classification", type=Path)
    parser.add_argument("--validator", type=Path, default=HERE / "validate_classification.py")
    args = parser.parse_args()

    validation = subprocess.run(
        [sys.executable, str(args.validator), str(args.classification), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if validation.returncode != 0:
        print(json.dumps({
            "status": "rejected",
            "gate": "classification_validation",
            "validator_exit_code": validation.returncode,
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    classification = json.loads(args.classification.read_text(encoding="utf-8"))
    report = analyze_documents(manifest, classification)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
