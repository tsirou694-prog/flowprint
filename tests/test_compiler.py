#!/usr/bin/env python3
"""Node 5 integration tests for the real FlowPrint compiler entry point."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "flowprint" / "skills" / "flowprint"
COMPILER = SKILL / "scripts" / "compile_skill.py"
IMPACT = SKILL / "scripts" / "analyze_impact.py"
VALIDATOR = SKILL / "scripts" / "validate_classification.py"
READY_FIXTURE = ROOT / "tests" / "fixtures" / "classification" / "sticker-ready-v0.3.json"
FIXTURES = ROOT / "tests" / "fixtures" / "classification"


def ready_document() -> dict:
    return json.loads(READY_FIXTURE.read_text(encoding="utf-8"))


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class CompilerIntegrationTests(unittest.TestCase):
    def run_compiler(self, document: dict, workspace: Path, label: str = "draft", *extra: str):
        source = workspace / f"{label}.json"
        output = workspace / f"{label}-output"
        source.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(COMPILER), str(source), str(output), "--skill-name", "test-flowprint-skill", *extra],
            check=False,
            capture_output=True,
            text=True,
        )
        return result, output, source

    def assert_rejected_without_output(self, document: dict, label: str, expected_error: str):
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(document, Path(directory), label)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse(output.exists(), f"rejected compilation left output at {output}")
            self.assertEqual(list(Path(directory).glob(f".{output.name}.flowprint-tmp-*")), [])
            self.assertIn('"status": "rejected"', result.stderr)
            self.assertIn(expected_error, result.stderr)

    def test_valid_ready_input_compiles_draft_without_installing(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(ready_document(), Path(directory), "valid")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "SKILL.md").is_file())
            self.assertTrue((output / "flowprint-manifest.json").is_file())
            record = json.loads((output / "compile-record.json").read_text(encoding="utf-8"))
            manifest = json.loads((output / "flowprint-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(record["classification_validator"]["exit_code"], 0)
            self.assertFalse(record["install_performed"])
            self.assertEqual(manifest["skill"]["install_state"], "not_authorized")
            self.assertFalse(manifest["permissions"]["installation_authorized"])

    def test_multi_workflow_routing_document_is_rejected_at_selection_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(
                fixture("yueyang-needs-selection-v0.4.json"),
                Path(directory),
                "needs-selection",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertIn('"gate": "workflow_selection"', result.stderr)

    def test_user_selected_trip_compiles_without_poster_workflow_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(
                fixture("yueyang-trip-selected-v0.4.json"),
                Path(directory),
                "trip-selected",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = (output / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Plan practical 1–3 day family self-drive trips", skill)
            self.assertIn("Do not use for", skill)
            self.assertNotIn("Execute the validated", skill)
            self.assertNotIn("mobile-size readability", skill)
            self.assertNotIn("installation, submission", skill)
            manifest = json.loads((output / "flowprint-manifest.json").read_text(encoding="utf-8"))
            record = json.loads((output / "compile-record.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["workflow_scope"]["selected_candidate_id"], "trip-planning")
            self.assertTrue(manifest["workflow_scope"]["selection_confirmation_bound"])
            self.assertEqual(record["workflow_selection"]["candidate_count"], 2)
            self.assertTrue(record["workflow_selection"]["user_selection_bound"])

    def test_user_selected_poster_compiles_without_trip_planning_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(
                fixture("yueyang-poster-selected-v0.4.json"),
                Path(directory),
                "poster-selected",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = (output / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("family trip invitations", skill)
            self.assertNotIn("travel-time and energy budget", skill)

    def test_v04_single_workflow_compiles_without_user_selection_record(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(
                fixture("report-single-v0.4.json"),
                Path(directory),
                "single-workflow",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads((output / "compile-record.json").read_text(encoding="utf-8"))
            manifest = json.loads((output / "flowprint-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(record["workflow_selection"]["scope_status"], "single_candidate")
            self.assertEqual(record["workflow_selection"]["candidate_count"], 1)
            self.assertFalse(record["workflow_selection"]["user_selection_bound"])
            self.assertFalse(manifest["workflow_scope"]["selection_confirmation_bound"])

    def test_bad_confidence_field_is_rejected_by_real_compiler(self):
        document = ready_document()
        document["items"][0]["confidence"] = 0.99
        self.assert_rejected_without_output(document, "bad-confidence", "certainty fields are forbidden")

    def test_one_time_preference_in_core_is_rejected_by_real_compiler(self):
        document = ready_document()
        document["items"][0]["rule_hits"].append("R1")
        self.assert_rejected_without_output(document, "bad-core-r1", "Core cannot use R1")

    def test_missing_abstracted_rule_is_rejected_by_real_compiler(self):
        document = ready_document()
        lesson = next(item for item in document["items"] if item["id"] == "item-failure-halo")
        del lesson["abstracted_rule"]
        self.assert_rejected_without_output(document, "bad-lesson", "abstracted_rule")

    def test_high_impact_without_review_is_rejected_by_real_compiler(self):
        document = ready_document()
        profile = next(item for item in document["items"] if item["id"] == "item-profile-tail")
        profile["review_required"] = False
        self.assert_rejected_without_output(document, "bad-high-impact", "high-impact item must require review")

    def test_shared_question_missing_item_link_is_rejected_by_real_compiler(self):
        document = ready_document()
        document["gates"]["questions"][0]["item_ids"] = ["item-profile-tail"]
        self.assert_rejected_without_output(document, "bad-question-link", "must be covered by question")

    def test_valid_needs_review_input_is_rejected_by_compiler(self):
        document = ready_document()
        document["gates"]["confirmations"][0]["accepted"] = False
        document["gates"]["decision"] = "needs_review"
        with tempfile.TemporaryDirectory() as directory:
            result, output, _ = self.run_compiler(document, Path(directory), "needs-review")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertIn("review_decision", result.stderr)

    def test_raw_transcript_storage_is_rejected_by_real_compiler(self):
        document = ready_document()
        document["source"]["raw_transcript_stored"] = True
        self.assert_rejected_without_output(document, "bad-transcript", "raw_transcript_stored")

    def test_missing_validator_fails_closed_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing-validator.py"
            result, output, _ = self.run_compiler(
                ready_document(),
                Path(directory),
                "missing-validator",
                "--classification-validator",
                str(missing),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertIn("classification_validation", result.stderr)

    def test_profile_edit_marks_profile_artifact_stale_and_requires_full_revalidation(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result, output, _ = self.run_compiler(ready_document(), workspace, "impact-base")
            self.assertEqual(result.returncode, 0, result.stderr)
            edited = copy.deepcopy(ready_document())
            profile = next(item for item in edited["items"] if item["id"] == "item-profile-tail")
            profile["statement"] = "Laosan has no visible tail."
            edited_path = workspace / "edited.json"
            edited_path.write_text(json.dumps(edited, ensure_ascii=False, indent=2), encoding="utf-8")
            impact = subprocess.run(
                [sys.executable, str(IMPACT), str(output / "flowprint-manifest.json"), str(edited_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(impact.returncode, 0, impact.stderr)
            report = json.loads(impact.stdout)
            self.assertTrue(report["profile_stale"])
            self.assertTrue(report["full_revalidation_required"])
            self.assertIn("profiles/default.json", report["stale_artifacts"])
            self.assertIn("SKILL.md", report["stale_artifacts"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
