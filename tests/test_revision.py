#!/usr/bin/env python3
"""Node 7 integration tests for revision invalidation, confirmation, and recompilation."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "flowprint" / "skills" / "flowprint"
SCRIPTS = SKILL / "scripts"
COMPILER = SCRIPTS / "compile_skill.py"
PREPARE = SCRIPTS / "prepare_revision.py"
FINALIZE = SCRIPTS / "finalize_revision.py"
FIXTURE = ROOT / "tests" / "fixtures" / "classification" / "sticker-ready-v0.3.json"
V04_SINGLE_FIXTURE = ROOT / "tests" / "fixtures" / "classification" / "report-single-v0.4.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RevisionIntegrationTests(unittest.TestCase):
    def compile_base(self, workspace: Path) -> tuple[Path, Path]:
        classification = workspace / "base-classification.json"
        classification.write_bytes(FIXTURE.read_bytes())
        draft = workspace / "base-draft"
        result = subprocess.run(
            [sys.executable, str(COMPILER), str(classification), str(draft), "--skill-name", "revision-test-skill"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return classification, draft

    def prepare_profile_revision(self, workspace: Path, draft: Path) -> tuple[Path, dict]:
        candidate = copy.deepcopy(read_json(FIXTURE))
        profile = next(item for item in candidate["items"] if item["id"] == "item-profile-tail")
        profile["statement"] = "Laosan has no visible tail."
        candidate_path = workspace / "classification.next.json"
        write_json(candidate_path, candidate)
        revision = workspace / "revision-1"
        result = subprocess.run(
            [
                sys.executable,
                str(PREPARE),
                str(draft / "flowprint-manifest.json"),
                str(candidate_path),
                str(revision),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return revision, json.loads(result.stdout)

    def confirmation_for(self, revision: Path, workspace: Path) -> Path:
        plan = read_json(revision / "revision-plan.json")
        confirmation = {
            "revision_id": plan["revision_id"],
            "confirmed_by": "user",
            "accepted": True,
            "answer": "接受本次修正及全部受影响项。",
            "questions": [
                {
                    "question_id": question_id,
                    "item_ids": plan["required_question_item_ids"][question_id],
                    "confirmed_by": "user",
                    "accepted": True,
                    "answer": "接受推荐答案。",
                }
                for question_id in plan["required_question_ids"]
            ],
        }
        confirmation_path = workspace / "user-confirmation.json"
        write_json(confirmation_path, confirmation)
        return confirmation_path

    def finalize(self, revision: Path, confirmation: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(FINALIZE), str(revision), str(confirmation)],
            check=False,
            capture_output=True,
            text=True,
        )

    def compile_revision(self, revision: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(COMPILER),
                str(revision / "classification.ready.json"),
                str(output),
                "--skill-name",
                "revision-test-skill",
                "--revision-receipt",
                str(revision / "revision-receipt.json"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_profile_revision_invalidates_confirmations_and_compiles_new_version(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            base_manifest = base / "flowprint-manifest.json"
            base_hash_before = sha256(base_manifest)
            revision, report = self.prepare_profile_revision(workspace, base)

            self.assertTrue(report["full_revalidation_required"])
            self.assertIn("item-profile-tail", report["changed_item_ids"])
            self.assertEqual(set(report["required_question_ids"]), {"question-1", "question-2"})
            self.assertEqual(
                set(report["stale_confirmation_ids"]),
                {"confirmation-1", "confirmation-2"},
            )
            review = read_json(revision / "classification.review.json")
            self.assertEqual(review["gates"]["decision"], "needs_review")
            self.assertEqual(review["gates"]["confirmations"], [])

            confirmation = self.confirmation_for(revision, workspace)
            finalized = self.finalize(revision, confirmation)
            self.assertEqual(finalized.returncode, 0, finalized.stderr)
            new_draft = workspace / "revised-draft"
            compiled = self.compile_revision(revision, new_draft)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)

            self.assertEqual(sha256(base_manifest), base_hash_before)
            base_profile = read_json(base / "profiles" / "default.json")
            revised_profile = read_json(new_draft / "profiles" / "default.json")
            self.assertEqual(base_profile["version"], 1)
            self.assertEqual(revised_profile["version"], 2)
            manifest = read_json(new_draft / "flowprint-manifest.json")
            record = read_json(new_draft / "compile-record.json")
            self.assertEqual(manifest["revision"]["sequence"], 1)
            self.assertEqual(manifest["skill"]["version"], "0.1.0-draft.r1")
            self.assertTrue(record["revision_gate"]["classification_hash_matched"])
            self.assertEqual(manifest["skill"]["install_state"], "not_authorized")
            self.assertFalse(record["install_performed"])
            self.assertFalse(record["external_action_performed"])

    def test_revision_without_confirmation_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            revision, _ = self.prepare_profile_revision(workspace, base)
            confirmation = self.confirmation_for(revision, workspace)
            self.assertEqual(self.finalize(revision, confirmation).returncode, 0)
            output = workspace / "must-not-exist"
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMPILER),
                    str(revision / "classification.ready.json"),
                    str(output),
                    "--skill-name",
                    "revision-test-skill",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("revision_receipt", result.stderr)
            self.assertFalse(output.exists())

    def test_wrong_or_incomplete_user_confirmation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            revision, _ = self.prepare_profile_revision(workspace, base)
            confirmation = self.confirmation_for(revision, workspace)
            payload = read_json(confirmation)
            payload["questions"] = payload["questions"][:1]
            write_json(confirmation, payload)
            result = self.finalize(revision, confirmation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("revision_confirmation", result.stderr)
            self.assertFalse((revision / "classification.ready.json").exists())
            self.assertFalse((revision / "revision-receipt.json").exists())

    def test_low_impact_edit_keeps_review_confirmations_but_requires_revision_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            candidate = copy.deepcopy(read_json(FIXTURE))
            parameter = next(item for item in candidate["items"] if item["id"] == "item-param-count")
            parameter["statement"] = "Produce twelve stickers in this run."
            candidate_path = workspace / "classification.next.json"
            write_json(candidate_path, candidate)
            revision = workspace / "revision-low"
            prepared = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE),
                    str(base / "flowprint-manifest.json"),
                    str(candidate_path),
                    str(revision),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            plan = read_json(revision / "revision-plan.json")
            review = read_json(revision / "classification.review.json")
            self.assertFalse(plan["impact"]["full_revalidation_required"])
            self.assertEqual(plan["required_question_ids"], [])
            self.assertEqual(len(review["gates"]["confirmations"]), 2)
            self.assertEqual(review["gates"]["decision"], "ready")

            confirmation = {
                "revision_id": plan["revision_id"],
                "confirmed_by": "user",
                "accepted": True,
                "answer": "确认本次仅把数量改为十二张。",
                "questions": [],
            }
            confirmation_path = workspace / "confirmation-low.json"
            write_json(confirmation_path, confirmation)
            self.assertEqual(self.finalize(revision, confirmation_path).returncode, 0)
            revised_draft = workspace / "revised-low"
            compiled = self.compile_revision(revision, revised_draft)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            self.assertEqual(read_json(revised_draft / "profiles" / "default.json")["version"], 1)

    def test_changed_base_manifest_invalidates_prepared_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            revision, _ = self.prepare_profile_revision(workspace, base)
            confirmation = self.confirmation_for(revision, workspace)
            manifest_path = base / "flowprint-manifest.json"
            manifest = read_json(manifest_path)
            manifest["test_tamper"] = True
            write_json(manifest_path, manifest)
            result = self.finalize(revision, confirmation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base manifest is missing or changed", result.stderr)
            self.assertFalse((revision / "classification.ready.json").exists())
            self.assertFalse((revision / "revision-receipt.json").exists())

    def test_tampering_after_confirmation_is_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            revision, _ = self.prepare_profile_revision(workspace, base)
            confirmation = self.confirmation_for(revision, workspace)
            self.assertEqual(self.finalize(revision, confirmation).returncode, 0)
            ready_path = revision / "classification.ready.json"
            ready = read_json(ready_path)
            ready["items"][0]["statement"] = "Tampered after confirmation."
            write_json(ready_path, ready)
            output = workspace / "must-not-exist"
            result = self.compile_revision(revision, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("classification changed after user confirmation", result.stderr)
            self.assertFalse(output.exists())

    def test_tampered_receipt_impact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            revision, _ = self.prepare_profile_revision(workspace, base)
            confirmation = self.confirmation_for(revision, workspace)
            self.assertEqual(self.finalize(revision, confirmation).returncode, 0)
            receipt_path = revision / "revision-receipt.json"
            receipt = read_json(receipt_path)
            receipt["profile_version"] = 99
            write_json(receipt_path, receipt)
            output = workspace / "must-not-exist"
            result = self.compile_revision(revision, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("profile version does not match", result.stderr)
            self.assertFalse(output.exists())

    def test_revision_cannot_overwrite_base_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            revision, _ = self.prepare_profile_revision(workspace, base)
            confirmation = self.confirmation_for(revision, workspace)
            self.assertEqual(self.finalize(revision, confirmation).returncode, 0)
            result = self.compile_revision(revision, base)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output already exists", result.stderr)

    def test_no_change_revision_is_rejected_without_revision_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            candidate = workspace / "same.json"
            candidate.write_bytes(FIXTURE.read_bytes())
            revision = workspace / "must-not-exist"
            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE),
                    str(base / "flowprint-manifest.json"),
                    str(candidate),
                    str(revision),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 3)
            self.assertIn("no_change", result.stderr)
            self.assertFalse(revision.exists())

    def test_workflow_name_change_is_a_full_document_level_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            _, base = self.compile_base(workspace)
            candidate = copy.deepcopy(read_json(FIXTURE))
            candidate["workflow"]["candidate_name"] = "Laosan sticker production and delivery QA"
            candidate_path = workspace / "classification.next.json"
            write_json(candidate_path, candidate)
            revision = workspace / "revision-name"
            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE),
                    str(base / "flowprint-manifest.json"),
                    str(candidate_path),
                    str(revision),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = read_json(revision / "revision-plan.json")
            self.assertEqual(plan["impact"]["changed_document_fields"], ["workflow.candidate_name"])
            self.assertTrue(plan["impact"]["full_revalidation_required"])
            self.assertIn("SKILL.md", plan["impact"]["stale_artifacts"])
            self.assertIn("agents/openai.yaml", plan["impact"]["stale_artifacts"])

    def test_v04_trigger_change_is_full_revalidation_and_rebuilds_entry_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            base_classification = workspace / "base-v04.json"
            base_classification.write_bytes(V04_SINGLE_FIXTURE.read_bytes())
            base = workspace / "base-v04-draft"
            compiled = subprocess.run(
                [
                    sys.executable,
                    str(COMPILER),
                    str(base_classification),
                    str(base),
                    "--skill-name",
                    "report-revision-skill",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            base_manifest = base / "flowprint-manifest.json"
            base_hash = sha256(base_manifest)

            candidate = read_json(V04_SINGLE_FIXTURE)
            candidate["workflow"]["trigger"]["summary"] = (
                "Revise evidence-backed structured reports without changing unsupported facts."
            )
            candidate_path = workspace / "candidate-v04.json"
            write_json(candidate_path, candidate)
            revision = workspace / "revision-trigger"
            prepared = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE),
                    str(base_manifest),
                    str(candidate_path),
                    str(revision),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            plan = read_json(revision / "revision-plan.json")
            self.assertTrue(plan["impact"]["full_revalidation_required"])
            self.assertEqual(plan["impact"]["changed_document_fields"], ["workflow.scope_or_trigger"])
            self.assertIn("SKILL.md", plan["impact"]["stale_artifacts"])
            self.assertIn("agents/openai.yaml", plan["impact"]["stale_artifacts"])

            confirmation = {
                "revision_id": plan["revision_id"],
                "confirmed_by": "user",
                "accepted": True,
                "answer": "确认更新触发描述并重新验证。",
                "questions": [],
            }
            confirmation_path = workspace / "trigger-confirmation.json"
            write_json(confirmation_path, confirmation)
            self.assertEqual(self.finalize(revision, confirmation_path).returncode, 0)
            revised = workspace / "revised-v04"
            self.assertEqual(self.compile_revision(revision, revised).returncode, 0)
            self.assertEqual(sha256(base_manifest), base_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
