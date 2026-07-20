#!/usr/bin/env python3
"""Render a validated FlowPrint classification JSON document as Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_classification import validate_document


LAYER_TITLES = {
    "core": "Core Workflow",
    "domain": "Domain Knowledge",
    "profile": "Profile",
    "run_parameter": "Run Parameters",
    "failure_lesson": "Failure Lessons",
    "permission_boundary": "Permission Boundaries",
}


def render(document: dict) -> str:
    inventory = document["evidence_inventory"]
    workflow = document["workflow"]
    scope = workflow.get("scope") if document.get("schema_version") == "0.4" else None
    lines = [
        "# FlowPrint classification preview",
        "",
        f"Candidate workflow: {workflow.get('candidate_name') or 'selection required'}",
        "Evidence: "
        + " · ".join(
            f"{field} {'yes' if inventory[field] else 'no'}"
            for field in ("goal", "result", "corrections", "artifacts")
        ),
    ]

    if isinstance(scope, dict) and scope.get("status") == "needs_user_selection":
        lines.extend(["", "## Workflow candidates"])
        for index, candidate in enumerate(scope["candidates"], start=1):
            source = candidate["evidence"][0]
            lines.append(f"{index}. **{candidate['name']}** (`{candidate['id']}`)")
            lines.append(f"   - Evidence: {source['source_type']} — {source['locator']}")
            lines.append(f"   - Why separate: {candidate['rationale']}")
        lines.extend(
            [
                "",
                "Status: needs_workflow_selection",
                "Review: choose exactly one workflow candidate; FlowPrint will not classify or compile a merged draft.",
                "",
                "Next capability: selected-workflow classification",
            ]
        )
        return "\n".join(lines) + "\n"

    if isinstance(scope, dict):
        selected = scope.get("selected_candidate_id")
        excluded = [
            candidate["name"]
            for candidate in scope.get("candidates", [])
            if candidate.get("id") != selected
        ]
        lines.append(
            f"Workflow scope: {scope.get('status')} · selected `{selected}`"
        )
        if excluded:
            lines.append("Excluded workflows: " + "; ".join(excluded))

    for layer, title in LAYER_TITLES.items():
        lines.extend(["", f"## {title}"])
        layer_items = [item for item in document["items"] if item["layer"] == layer]
        if not layer_items:
            lines.append("- None detected")
            continue
        for item in layer_items:
            review = " · review" if item["review_required"] else ""
            lines.append(
                f"- **{item['statement']}** "
                f"`{item['evidence_state']} · {item['impact']}{review}`"
            )
            source = item["evidence"][0]
            lines.append(f"  - Evidence: {source['source_type']} — {source['locator']}")
            lines.append(f"  - Why: {item['rationale']}")

    gates = document["gates"]
    lines.extend(["", f"Status: {gates['decision']}"])
    if gates["questions"] and gates["decision"] == "needs_review":
        lines.extend(["", "## Review"])
        for index, question in enumerate(gates["questions"], start=1):
            lines.append(f"{index}. {question['prompt']}")
            lines.append(f"   Recommended: {question['recommended_answer']}")
        lines.append("")
        lines.append("Reply `接受全部` or override a number, for example `2=Run Parameter`.")
    else:
        confirmations = gates.get("confirmations", [])
        confirmed_count = sum(len(item.get("item_ids", [])) for item in confirmations if item.get("accepted") is True)
        if confirmed_count:
            lines.append(f"Review: {confirmed_count} item(s) confirmed by user")
        else:
            lines.append("Review: none")
    lines.extend(["", "Next capability: Skill compiler (Node 5)"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("classification", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.classification.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2
    errors = validate_document(document)
    if errors:
        print("ERROR classification must pass validation before rendering", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(render(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
