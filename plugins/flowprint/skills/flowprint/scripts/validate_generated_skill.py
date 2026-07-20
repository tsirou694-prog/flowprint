#!/usr/bin/env python3
"""Run FlowPrint's deterministic structural preflight on a generated Skill draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_draft(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "profiles/default.json",
        "references/domain-knowledge.md",
        "references/run-parameters.md",
        "references/failure-lessons.md",
        "references/permission-boundaries.md",
        "flowprint-manifest.json",
    ]
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required generated file: {relative}")
    if errors:
        return errors

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\nname: ([^\n]+)\ndescription: ([^\n]+)\n---\n", skill)
    if not match:
        errors.append("SKILL.md: expected name and description frontmatter")
    else:
        if not NAME.fullmatch(match.group(1)):
            errors.append("SKILL.md: invalid skill name")
        if len(match.group(2).strip()) < 40:
            errors.append("SKILL.md: description is too short to explain use and trigger")

    try:
        manifest: dict[str, Any] = json.loads((root / "flowprint-manifest.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return errors + [f"flowprint-manifest.json: invalid JSON: {error}"]
    if manifest.get("schema_version") != "0.1":
        errors.append("flowprint-manifest.json: unsupported schema_version")
    skill_state = manifest.get("skill", {})
    if skill_state.get("compile_state") != "draft":
        errors.append("flowprint-manifest.json: compile_state must be draft")
    if skill_state.get("install_state") != "not_authorized":
        errors.append("flowprint-manifest.json: install_state must be not_authorized")
    if not isinstance(skill_state.get("workflow_definition_fingerprint"), str):
        errors.append("flowprint-manifest.json: workflow_definition_fingerprint required")
    if manifest.get("source", {}).get("classification_schema_version") == "0.4":
        workflow_scope = manifest.get("workflow_scope")
        if not isinstance(workflow_scope, dict):
            errors.append("flowprint-manifest.json: workflow_scope required for classification schema 0.4")
        else:
            if workflow_scope.get("status") not in {"single_candidate", "user_selected"}:
                errors.append("flowprint-manifest.json: workflow scope must be resolved")
            if workflow_scope.get("selected_candidate_id") not in workflow_scope.get("candidate_ids", []):
                errors.append("flowprint-manifest.json: selected workflow candidate is not declared")
            if workflow_scope.get("status") == "user_selected" and workflow_scope.get("selection_confirmation_bound") is not True:
                errors.append("flowprint-manifest.json: user-selected workflow selection confirmation is not bound")
            if workflow_scope.get("status") == "single_candidate" and workflow_scope.get("selection_confirmation_bound") is not False:
                errors.append("flowprint-manifest.json: single-candidate workflow must not claim a selection confirmation")
    permissions = manifest.get("permissions", {})
    if permissions.get("installation_authorized") is not False:
        errors.append("flowprint-manifest.json: installation_authorized must be false")
    if permissions.get("external_actions_authorized") is not False:
        errors.append("flowprint-manifest.json: external_actions_authorized must be false")

    graph = manifest.get("dependency_graph")
    if not isinstance(graph, dict):
        errors.append("flowprint-manifest.json: dependency_graph object required")
        return errors
    items = graph.get("items", [])
    known_items = {item.get("item_id") for item in items if isinstance(item, dict)}
    profiles = graph.get("profiles", [])
    known_profiles = {profile.get("profile_id") for profile in profiles if isinstance(profile, dict)}
    profile_versions = {
        profile.get("profile_id"): profile.get("version")
        for profile in profiles
        if isinstance(profile, dict)
    }
    try:
        generated_profile = json.loads((root / "profiles/default.json").read_text(encoding="utf-8"))
        if generated_profile.get("version") != profile_versions.get("default"):
            errors.append("profiles/default.json: version must match dependency graph")
    except json.JSONDecodeError as error:
        errors.append(f"profiles/default.json: invalid JSON: {error}")
    artifacts = graph.get("artifacts", [])
    known_artifacts: set[str] = set()
    for index, artifact in enumerate(artifacts):
        path = f"dependency_graph.artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{path}: object required")
            continue
        relative = artifact.get("path")
        if not isinstance(relative, str) or not relative:
            errors.append(f"{path}.path: non-empty string required")
            continue
        known_artifacts.add(relative)
        file_path = root / relative
        if not file_path.is_file():
            errors.append(f"{path}: referenced artifact does not exist: {relative}")
        elif artifact.get("sha256") != sha256_file(file_path):
            errors.append(f"{path}: sha256 does not match generated file")
        unknown = set(artifact.get("depends_on_item_ids", [])) - known_items
        if unknown:
            errors.append(f"{path}: unknown item dependencies {sorted(unknown)}")
        unknown_profiles = set(artifact.get("depends_on_profile_ids", [])) - known_profiles
        if unknown_profiles:
            errors.append(f"{path}: unknown profile dependencies {sorted(unknown_profiles)}")
    for index, edge in enumerate(graph.get("edges", [])):
        if edge.get("from_item_id") not in known_items:
            errors.append(f"dependency_graph.edges[{index}]: unknown from_item_id")
        if edge.get("to_artifact") not in known_artifacts:
            errors.append(f"dependency_graph.edges[{index}]: unknown to_artifact")
    for index, edge in enumerate(graph.get("profile_edges", [])):
        if edge.get("from_profile_id") not in known_profiles:
            errors.append(f"dependency_graph.profile_edges[{index}]: unknown from_profile_id")
        if edge.get("to_artifact") not in known_artifacts:
            errors.append(f"dependency_graph.profile_edges[{index}]: unknown to_artifact")
        expected_version = profile_versions.get(edge.get("from_profile_id"))
        if not isinstance(expected_version, int) or expected_version < 1:
            errors.append(f"dependency_graph.profile_edges[{index}]: invalid Profile version")
        elif edge.get("from_version") != expected_version:
            errors.append(
                f"dependency_graph.profile_edges[{index}]: expected Profile version {expected_version}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors = validate_draft(args.draft)
    report = {"valid": not errors, "error_count": len(errors), "errors": errors, "draft": str(args.draft)}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif errors:
        print(f"FAIL {args.draft}: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"PASS {args.draft}: FlowPrint structural preflight")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
