#!/usr/bin/env python3
"""Validate a FlowPrint classification document using deterministic gates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SUPPORTED_SCHEMA_VERSIONS = {"0.2", "0.3", "0.4"}
LAYERS = {
    "core",
    "domain",
    "profile",
    "run_parameter",
    "failure_lesson",
    "permission_boundary",
}
SOURCE_TYPES = {
    "user_instruction",
    "user_correction",
    "final_artifact",
    "workspace_file",
    "test_result",
    "visual_observation",
    "model_inference",
}
EVIDENCE_STATES = {"supported", "ambiguous", "conflicting"}
IMPACTS = {"low", "medium", "high"}
RULE_IDS = {f"R{number}" for number in range(1, 9)}
FORBIDDEN_CERTAINTY_KEYS = re.compile(r"(?:confidence|probability|certainty)", re.IGNORECASE)
ITEM_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
WORKFLOW_SCOPE_STATUSES = {
    "single_candidate",
    "needs_user_selection",
    "user_selected",
}


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _forbidden_keys(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if FORBIDDEN_CERTAINTY_KEYS.search(str(key)):
                errors.append(f"{child_path}: numeric/model certainty fields are forbidden")
            errors.extend(_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_forbidden_keys(child, f"{path}[{index}]"))
    return errors


def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["$: document must be a JSON object"]

    errors.extend(_forbidden_keys(document))

    schema_version = document.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(f"$.schema_version: expected one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}")

    workflow = document.get("workflow")
    workflow_scope_status: str | None = None
    selected_candidate_id: str | None = None
    routing_only = False
    if not isinstance(workflow, dict):
        errors.append("$.workflow: object required")
        workflow = {}

    if schema_version == "0.4":
        scope = workflow.get("scope")
        if not isinstance(scope, dict):
            errors.append("$.workflow.scope: object required for schema 0.4")
            scope = {}
        workflow_scope_status = scope.get("status")
        if workflow_scope_status not in WORKFLOW_SCOPE_STATUSES:
            errors.append(
                "$.workflow.scope.status: expected one of "
                f"{sorted(WORKFLOW_SCOPE_STATUSES)}"
            )

        candidates = scope.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            errors.append("$.workflow.scope.candidates: non-empty array required")
            candidates = []
        candidate_ids: set[str] = set()
        candidate_names: dict[str, str] = {}
        for index, candidate in enumerate(candidates):
            path = f"$.workflow.scope.candidates[{index}]"
            if not isinstance(candidate, dict):
                errors.append(f"{path}: object required")
                continue
            candidate_id = candidate.get("id")
            if not _is_nonempty_string(candidate_id) or not ITEM_ID.fullmatch(candidate_id):
                errors.append(f"{path}.id: use 3–64 lowercase letters, digits, or hyphens")
            elif candidate_id in candidate_ids:
                errors.append(f"{path}.id: duplicate workflow candidate id {candidate_id!r}")
            else:
                candidate_ids.add(candidate_id)
            name = candidate.get("name")
            if not _is_nonempty_string(name):
                errors.append(f"{path}.name: non-empty string required")
            elif _is_nonempty_string(candidate_id):
                candidate_names[candidate_id] = name
            if not _is_nonempty_string(candidate.get("rationale")):
                errors.append(f"{path}.rationale: non-empty string required")
            evidence = candidate.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{path}.evidence: at least one evidence object required")
            else:
                for evidence_index, source_item in enumerate(evidence):
                    source_path = f"{path}.evidence[{evidence_index}]"
                    if not isinstance(source_item, dict):
                        errors.append(f"{source_path}: object required")
                        continue
                    if source_item.get("source_type") not in SOURCE_TYPES:
                        errors.append(
                            f"{source_path}.source_type: expected one of {sorted(SOURCE_TYPES)}"
                        )
                    if not _is_nonempty_string(source_item.get("locator")):
                        errors.append(f"{source_path}.locator: non-empty string required")

        selected_candidate_id = scope.get("selected_candidate_id")
        candidate_name = workflow.get("candidate_name")
        selection_confirmation = scope.get("selection_confirmation")
        if workflow_scope_status == "single_candidate":
            if len(candidates) != 1:
                errors.append("$.workflow.scope.candidates: single_candidate requires exactly one candidate")
            if selected_candidate_id not in candidate_ids:
                errors.append("$.workflow.scope.selected_candidate_id: must select the only candidate")
            if not _is_nonempty_string(candidate_name):
                errors.append("$.workflow.candidate_name: non-empty string required after scope resolution")
            elif candidate_names.get(selected_candidate_id) != candidate_name:
                errors.append("$.workflow.candidate_name: must match the selected workflow candidate name")
            if selection_confirmation not in (None, {}):
                errors.append("$.workflow.scope.selection_confirmation: not allowed for a single candidate")
        elif workflow_scope_status == "needs_user_selection":
            routing_only = True
            if len(candidates) < 2:
                errors.append("$.workflow.scope.candidates: needs_user_selection requires at least two candidates")
            if selected_candidate_id is not None:
                errors.append("$.workflow.scope.selected_candidate_id: must be null until the user selects")
            if candidate_name is not None:
                errors.append("$.workflow.candidate_name: must be null until the user selects")
            if selection_confirmation not in (None, {}):
                errors.append("$.workflow.scope.selection_confirmation: must be null until the user selects")
            if workflow.get("trigger") not in (None, {}):
                errors.append("$.workflow.trigger: must be absent until the user selects a workflow")
        elif workflow_scope_status == "user_selected":
            if len(candidates) < 2:
                errors.append("$.workflow.scope.candidates: user_selected requires at least two candidates")
            if selected_candidate_id not in candidate_ids:
                errors.append("$.workflow.scope.selected_candidate_id: must reference a declared candidate")
            if not _is_nonempty_string(candidate_name):
                errors.append("$.workflow.candidate_name: non-empty string required after scope resolution")
            elif candidate_names.get(selected_candidate_id) != candidate_name:
                errors.append("$.workflow.candidate_name: must match the selected workflow candidate name")
            if not isinstance(selection_confirmation, dict):
                errors.append("$.workflow.scope.selection_confirmation: object required for user_selected")
            else:
                if selection_confirmation.get("selected_candidate_id") != selected_candidate_id:
                    errors.append(
                        "$.workflow.scope.selection_confirmation.selected_candidate_id: "
                        "must match the selected candidate"
                    )
                if selection_confirmation.get("confirmed_by") != "user":
                    errors.append("$.workflow.scope.selection_confirmation.confirmed_by: expected 'user'")
                if selection_confirmation.get("accepted") is not True:
                    errors.append("$.workflow.scope.selection_confirmation.accepted: expected true")
                if not _is_nonempty_string(selection_confirmation.get("answer")):
                    errors.append("$.workflow.scope.selection_confirmation.answer: non-empty string required")

        if workflow_scope_status in {"single_candidate", "user_selected"}:
            trigger = workflow.get("trigger")
            if not isinstance(trigger, dict):
                errors.append("$.workflow.trigger: object required after scope resolution")
            else:
                if not _is_nonempty_string(trigger.get("summary")):
                    errors.append("$.workflow.trigger.summary: non-empty string required")
                when_to_use = trigger.get("when_to_use")
                if (
                    not isinstance(when_to_use, list)
                    or not when_to_use
                    or not all(_is_nonempty_string(value) for value in when_to_use)
                ):
                    errors.append("$.workflow.trigger.when_to_use: non-empty string array required")
                do_not_use = trigger.get("do_not_use")
                if not isinstance(do_not_use, list) or not all(
                    _is_nonempty_string(value) for value in do_not_use
                ):
                    errors.append("$.workflow.trigger.do_not_use: string array required")
    elif not _is_nonempty_string(workflow.get("candidate_name")):
        errors.append("$.workflow.candidate_name: non-empty string required")

    source = document.get("source")
    if not isinstance(source, dict):
        errors.append("$.source: object required")
    else:
        if source.get("type") != "current_task":
            errors.append("$.source.type: expected 'current_task'")
        if source.get("raw_transcript_stored") is not False:
            errors.append("$.source.raw_transcript_stored: must be false")

    inventory = document.get("evidence_inventory")
    if not isinstance(inventory, dict):
        errors.append("$.evidence_inventory: object required")
    else:
        for field in ("goal", "result", "corrections", "artifacts"):
            if not isinstance(inventory.get(field), bool):
                errors.append(f"$.evidence_inventory.{field}: boolean required")

    items = document.get("items")
    if routing_only:
        if items != []:
            errors.append("$.items: must be empty until the user selects a workflow")
        items = []
    elif not isinstance(items, list) or not items:
        errors.append("$.items: non-empty array required")
        items = []

    item_ids: set[str] = set()
    review_ids: set[str] = set()

    for index, item in enumerate(items):
        path = f"$.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: object required")
            continue

        item_id = item.get("id")
        if not _is_nonempty_string(item_id) or not ITEM_ID.fullmatch(item_id):
            errors.append(f"{path}.id: use 3–64 lowercase letters, digits, or hyphens")
            item_id = f"invalid-{index}"
        elif item_id in item_ids:
            errors.append(f"{path}.id: duplicate item id {item_id!r}")
        item_ids.add(item_id)

        if not _is_nonempty_string(item.get("statement")):
            errors.append(f"{path}.statement: non-empty string required")

        if schema_version == "0.4":
            if item.get("workflow_candidate_id") != selected_candidate_id:
                errors.append(
                    f"{path}.workflow_candidate_id: must match selected workflow candidate "
                    f"{selected_candidate_id!r}"
                )

        layer = item.get("layer")
        if layer not in LAYERS:
            errors.append(f"{path}.layer: expected one of {sorted(LAYERS)}")

        evidence = item.get("evidence")
        source_types: set[str] = set()
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{path}.evidence: at least one evidence object required")
        else:
            for evidence_index, source_item in enumerate(evidence):
                source_path = f"{path}.evidence[{evidence_index}]"
                if not isinstance(source_item, dict):
                    errors.append(f"{source_path}: object required")
                    continue
                source_type = source_item.get("source_type")
                if source_type not in SOURCE_TYPES:
                    errors.append(f"{source_path}.source_type: expected one of {sorted(SOURCE_TYPES)}")
                else:
                    source_types.add(source_type)
                if not _is_nonempty_string(source_item.get("locator")):
                    errors.append(f"{source_path}.locator: non-empty string required")

        rule_hits = item.get("rule_hits")
        if not isinstance(rule_hits, list) or not rule_hits:
            errors.append(f"{path}.rule_hits: at least one rule id required")
            rule_hits_set: set[str] = set()
        else:
            rule_hits_set = set(rule_hits)
            invalid_rules = rule_hits_set - RULE_IDS
            if invalid_rules:
                errors.append(f"{path}.rule_hits: invalid rule ids {sorted(invalid_rules)}")

        evidence_state = item.get("evidence_state")
        if evidence_state not in EVIDENCE_STATES:
            errors.append(f"{path}.evidence_state: expected one of {sorted(EVIDENCE_STATES)}")

        impact = item.get("impact")
        if impact not in IMPACTS:
            errors.append(f"{path}.impact: expected one of {sorted(IMPACTS)}")

        review_required = item.get("review_required")
        if not isinstance(review_required, bool):
            errors.append(f"{path}.review_required: boolean required")
            review_required = False
        if review_required:
            review_ids.add(item_id)

        if not _is_nonempty_string(item.get("rationale")):
            errors.append(f"{path}.rationale: non-empty string required")

        if evidence_state in {"ambiguous", "conflicting"} and not review_required:
            errors.append(f"{path}: {evidence_state} evidence must require review")
        if impact == "high" and not review_required:
            errors.append(f"{path}: high-impact item must require review")
        if layer == "core" and "R1" in rule_hits_set:
            errors.append(f"{path}: Core cannot use R1 named-entity stability; split or reclassify")
        if layer == "profile" and source_types and source_types <= {"visual_observation", "model_inference"}:
            if not review_required:
                errors.append(f"{path}: vision/inference-only Profile must require review")
        if layer == "permission_boundary":
            if impact != "high":
                errors.append(f"{path}: permission boundary must be high impact")
            if not review_required:
                errors.append(f"{path}: permission boundary must require review")
        if layer == "failure_lesson" and not _is_nonempty_string(item.get("abstracted_rule")):
            errors.append(f"{path}.abstracted_rule: required for failure lessons")

    gates = document.get("gates")
    if not isinstance(gates, dict):
        errors.append("$.gates: object required")
        return errors

    if routing_only:
        if gates.get("decision") != "needs_workflow_selection":
            errors.append("$.gates.decision: expected 'needs_workflow_selection'")
        if gates.get("review_item_ids") != []:
            errors.append("$.gates.review_item_ids: must be empty before workflow selection")
        if gates.get("questions") != []:
            errors.append("$.gates.questions: must be empty before workflow selection")
        if gates.get("confirmations") not in (None, []):
            errors.append("$.gates.confirmations: must be empty before workflow selection")
        return errors

    declared_review_ids = gates.get("review_item_ids")
    if not isinstance(declared_review_ids, list) or not all(isinstance(value, str) for value in declared_review_ids):
        errors.append("$.gates.review_item_ids: string array required")
        declared_set: set[str] = set()
    else:
        declared_set = set(declared_review_ids)
        if len(declared_set) != len(declared_review_ids):
            errors.append("$.gates.review_item_ids: duplicates are not allowed")
        unknown = declared_set - item_ids
        if unknown:
            errors.append(f"$.gates.review_item_ids: unknown item ids {sorted(unknown)}")
        if declared_set != review_ids:
            errors.append(
                "$.gates.review_item_ids: must exactly match items marked review_required "
                f"(expected {sorted(review_ids)})"
            )

    questions = gates.get("questions")
    if not isinstance(questions, list):
        errors.append("$.gates.questions: array required")
        questions = []
    if len(questions) > 3:
        errors.append("$.gates.questions: at most three questions allowed")
    if review_ids and not questions:
        errors.append("$.gates.questions: review items require at least one question")
    if not review_ids and questions:
        errors.append("$.gates.questions: ready classifications must not ask review questions")

    question_ids: set[str] = set()
    question_item_ids: dict[str, set[str]] = {}
    referenced_review_ids: set[str] = set()
    for index, question in enumerate(questions):
        path = f"$.gates.questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{path}: object required")
            continue
        question_id = question.get("id")
        if not _is_nonempty_string(question_id):
            errors.append(f"{path}.id: non-empty string required")
        elif question_id in question_ids:
            errors.append(f"{path}.id: duplicate question id {question_id!r}")
        else:
            question_ids.add(question_id)
        item_refs = question.get("item_ids")
        if not isinstance(item_refs, list) or not item_refs or not all(isinstance(value, str) for value in item_refs):
            errors.append(f"{path}.item_ids: non-empty string array required")
        else:
            invalid_refs = set(item_refs) - review_ids
            if invalid_refs:
                errors.append(f"{path}.item_ids: must reference review items only; invalid {sorted(invalid_refs)}")
            referenced_review_ids.update(item_refs)
            if _is_nonempty_string(question_id):
                question_item_ids[question_id] = set(item_refs)
        if not _is_nonempty_string(question.get("prompt")):
            errors.append(f"{path}.prompt: non-empty string required")
        if not _is_nonempty_string(question.get("recommended_answer")):
            errors.append(f"{path}.recommended_answer: non-empty string required")

    if review_ids and referenced_review_ids != review_ids:
        missing = review_ids - referenced_review_ids
        errors.append(f"$.gates.questions: every review item must appear in a question; missing {sorted(missing)}")

    confirmed_review_ids: set[str] = set()
    if schema_version in {"0.3", "0.4"}:
        confirmations = gates.get("confirmations")
        if not isinstance(confirmations, list):
            errors.append(f"$.gates.confirmations: array required for schema {schema_version}")
            confirmations = []
        confirmation_ids: set[str] = set()
        for index, confirmation in enumerate(confirmations):
            path = f"$.gates.confirmations[{index}]"
            if not isinstance(confirmation, dict):
                errors.append(f"{path}: object required")
                continue
            confirmation_id = confirmation.get("id")
            if not _is_nonempty_string(confirmation_id):
                errors.append(f"{path}.id: non-empty string required")
            elif confirmation_id in confirmation_ids:
                errors.append(f"{path}.id: duplicate confirmation id {confirmation_id!r}")
            else:
                confirmation_ids.add(confirmation_id)

            question_id = confirmation.get("question_id")
            if question_id not in question_ids:
                errors.append(f"{path}.question_id: must reference a declared review question")

            item_refs = confirmation.get("item_ids")
            if not isinstance(item_refs, list) or not item_refs or not all(isinstance(value, str) for value in item_refs):
                errors.append(f"{path}.item_ids: non-empty string array required")
                item_ref_set: set[str] = set()
            else:
                item_ref_set = set(item_refs)
                if len(item_ref_set) != len(item_refs):
                    errors.append(f"{path}.item_ids: duplicates are not allowed")
                allowed_refs = question_item_ids.get(question_id, set())
                invalid_refs = item_ref_set - allowed_refs
                if invalid_refs:
                    errors.append(
                        f"{path}.item_ids: must be covered by question {question_id!r}; invalid {sorted(invalid_refs)}"
                    )

            if confirmation.get("confirmed_by") != "user":
                errors.append(f"{path}.confirmed_by: expected 'user'")
            if not isinstance(confirmation.get("accepted"), bool):
                errors.append(f"{path}.accepted: boolean required")
            if not _is_nonempty_string(confirmation.get("answer")):
                errors.append(f"{path}.answer: non-empty string required")
            if confirmation.get("accepted") is True and confirmation.get("confirmed_by") == "user":
                overlap = confirmed_review_ids & item_ref_set
                if overlap:
                    errors.append(f"{path}.item_ids: review items confirmed more than once {sorted(overlap)}")
                confirmed_review_ids.update(item_ref_set)
    elif "confirmations" in gates:
        errors.append("$.gates.confirmations: requires schema 0.3 or 0.4")

    expected_decision = "ready" if confirmed_review_ids == review_ids else "needs_review"
    if schema_version == "0.2":
        expected_decision = "needs_review" if review_ids else "ready"
    if gates.get("decision") != expected_decision:
        errors.append(f"$.gates.decision: expected {expected_decision!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("classification", type=Path, help="Path to classification JSON")
    parser.add_argument("--json", action="store_true", help="Emit the validation report as JSON")
    args = parser.parse_args()

    try:
        document = json.loads(args.classification.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR file not found: {args.classification}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"ERROR invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}", file=sys.stderr)
        return 2

    errors = validate_document(document)
    report = {
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "classification": str(args.classification),
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif errors:
        print(f"FAIL {args.classification}: {len(errors)} validation error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        item_count = len(document.get("items", []))
        review_count = len(document.get("gates", {}).get("review_item_ids", []))
        print(f"PASS {args.classification}: {item_count} item(s), {review_count} review item(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
