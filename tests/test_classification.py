#!/usr/bin/env python3
"""Node 4 tests for FlowPrint classification gates and rendering."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "flowprint" / "skills" / "flowprint"
VALIDATOR_PATH = SKILL / "scripts" / "validate_classification.py"
RENDERER_PATH = SKILL / "scripts" / "render_classification.py"
FIXTURES = ROOT / "tests" / "fixtures" / "classification"
RULES_PATH = SKILL / "references" / "decontextualization.md"
POWERSHELL_RUNNER = SKILL / "scripts" / "run_flowprint.ps1"


def load_validator():
    spec = importlib.util.spec_from_file_location("flowprint_validator", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ClassificationValidationTests(unittest.TestCase):
    def test_sticker_fixture_is_valid(self):
        self.assertEqual(VALIDATOR.validate_document(fixture("sticker-valid.json")), [])

    def test_document_fixture_is_valid(self):
        self.assertEqual(VALIDATOR.validate_document(fixture("document-valid.json")), [])

    def test_confirmed_v03_fixture_is_ready_and_valid(self):
        document = fixture("sticker-ready-v0.3.json")
        self.assertEqual(VALIDATOR.validate_document(document), [])
        self.assertEqual(document["gates"]["decision"], "ready")

    def test_v04_multi_workflow_routing_document_is_valid_and_stops(self):
        document = fixture("yueyang-needs-selection-v0.4.json")
        self.assertEqual(VALIDATOR.validate_document(document), [])
        self.assertEqual(document["gates"]["decision"], "needs_workflow_selection")
        self.assertEqual(document["items"], [])

    def test_v04_user_selected_trip_and_poster_are_independently_valid(self):
        for name in ("yueyang-trip-selected-v0.4.json", "yueyang-poster-selected-v0.4.json"):
            with self.subTest(name=name):
                document = fixture(name)
                self.assertEqual(VALIDATOR.validate_document(document), [])
                self.assertEqual(document["gates"]["decision"], "ready")

    def test_v04_single_workflow_does_not_require_selection_confirmation(self):
        document = fixture("report-single-v0.4.json")
        self.assertEqual(VALIDATOR.validate_document(document), [])
        self.assertEqual(document["workflow"]["scope"]["status"], "single_candidate")

    def test_v04_model_cannot_select_one_of_multiple_workflows(self):
        document = fixture("yueyang-trip-selected-v0.4.json")
        document["workflow"]["scope"]["selection_confirmation"]["confirmed_by"] = "model"
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("selection_confirmation.confirmed_by" in error for error in errors))

    def test_v04_unselected_workflow_item_is_rejected(self):
        document = fixture("yueyang-trip-selected-v0.4.json")
        document["items"][0]["workflow_candidate_id"] = "trip-poster"
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("must match selected workflow candidate" in error for error in errors))

    def test_v04_multi_workflow_cannot_hide_as_single_candidate(self):
        document = fixture("yueyang-needs-selection-v0.4.json")
        document["workflow"]["scope"]["status"] = "single_candidate"
        document["workflow"]["scope"]["selected_candidate_id"] = "trip-planning"
        document["workflow"]["candidate_name"] = "适老亲子家庭短途旅行规划"
        document["workflow"]["trigger"] = {
            "summary": "Plan a family trip.",
            "when_to_use": ["家庭旅行规划"],
            "do_not_use": [],
        }
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("single_candidate requires exactly one candidate" in error for error in errors))

    def test_v03_partial_confirmation_cannot_be_ready(self):
        document = fixture("sticker-ready-v0.3.json")
        document["gates"]["confirmations"] = document["gates"]["confirmations"][:1]
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("expected 'needs_review'" in error for error in errors))

    def test_model_cannot_self_confirm_review_items(self):
        document = fixture("sticker-ready-v0.3.json")
        document["gates"]["confirmations"][0]["confirmed_by"] = "model"
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("expected 'user'" in error for error in errors))

    def test_model_confidence_field_is_forbidden(self):
        document = fixture("document-valid.json")
        document["items"][0]["confidence"] = 0.99
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("certainty fields are forbidden" in error for error in errors))

    def test_high_impact_item_cannot_skip_review(self):
        document = fixture("sticker-valid.json")
        item = next(item for item in document["items"] if item["id"] == "item-profile-tail")
        item["review_required"] = False
        document["gates"]["review_item_ids"].remove("item-profile-tail")
        document["gates"]["questions"] = [document["gates"]["questions"][1]]
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("high-impact item must require review" in error for error in errors))

    def test_core_cannot_claim_named_entity_rule(self):
        document = fixture("document-valid.json")
        document["items"][0]["rule_hits"].append("R1")
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("Core cannot use R1" in error for error in errors))

    def test_vision_only_profile_requires_review(self):
        document = fixture("document-valid.json")
        profile = next(item for item in document["items"] if item["layer"] == "profile")
        profile["evidence"] = [
            {
                "source_type": "visual_observation",
                "locator": "single image",
                "quote": "appears blue"
            }
        ]
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("vision/inference-only Profile must require review" in error for error in errors))

    def test_more_than_three_questions_is_rejected(self):
        document = fixture("sticker-valid.json")
        base = document["gates"]["questions"][0]
        document["gates"]["questions"] = []
        for index in range(4):
            question = copy.deepcopy(base)
            question["id"] = f"question-{index + 1}"
            document["gates"]["questions"].append(question)
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("at most three questions" in error for error in errors))

    def test_review_ids_must_match_items(self):
        document = fixture("sticker-valid.json")
        document["gates"]["review_item_ids"] = ["item-profile-tail"]
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("must exactly match" in error for error in errors))

    def test_raw_transcript_storage_is_rejected(self):
        document = fixture("document-valid.json")
        document["source"]["raw_transcript_stored"] = True
        errors = VALIDATOR.validate_document(document)
        self.assertTrue(any("must be false" in error for error in errors))

    def test_renderer_outputs_review_card(self):
        result = subprocess.run(
            [sys.executable, str(RENDERER_PATH), str(FIXTURES / "sticker-valid.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# FlowPrint classification preview", result.stdout)
        self.assertIn("Status: needs_review", result.stdout)
        self.assertIn("Keep the tail rule only", result.stdout)

    def test_renderer_outputs_workflow_selection_card_without_six_layer_items(self):
        result = subprocess.run(
            [sys.executable, str(RENDERER_PATH), str(FIXTURES / "yueyang-needs-selection-v0.4.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Status: needs_workflow_selection", result.stdout)
        self.assertIn("适老亲子家庭短途旅行规划", result.stdout)
        self.assertIn("家庭旅行邀请函与纪念海报制作", result.stdout)
        self.assertNotIn("## Core Workflow", result.stdout)

    def test_rules_exclude_current_session_controls_from_persisted_layers(self):
        rules = RULES_PATH.read_text(encoding="utf-8")
        self.assertIn("Current-session controls", rules)
        self.assertIn("exclude them from all six persisted layers", rules)

    def test_rules_require_visible_result_evidence(self):
        rules = RULES_PATH.read_text(encoding="utf-8")
        self.assertIn("Set evidence inventory `result: yes` only", rules)
        self.assertIn("not sufficient result evidence", rules)

    def test_windows_runner_discovers_real_python_without_installing(self):
        runner = POWERSHELL_RUNNER.read_text(encoding="utf-8")
        self.assertIn("Programs\\Python\\Python*\\python.exe", runner)
        self.assertIn("No software was installed", runner)


if __name__ == "__main__":
    unittest.main(verbosity=2)
