from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "flowprint" / "skills" / "flowprint" / "SKILL.md"
TRIGGERS = ROOT / "tests" / "trigger-cases.md"
AUDIT_CONTRACT = ROOT / "plugins" / "flowprint" / "skills" / "flowprint" / "references" / "evidence-audit-contract.md"
POWERSHELL_RUNNER = ROOT / "plugins" / "flowprint" / "skills" / "flowprint" / "scripts" / "run_flowprint.ps1"


class EvidenceScopeContractTests(unittest.TestCase):
    def test_routing_metadata_carries_scope_and_exclusivity(self):
        text = SKILL.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("exclusively owns", frontmatter)
        self.assertIn("do not pair it with skill-creator", frontmatter)
        self.assertIn("never query Memory", frontmatter)
        self.assertIn("shell history", frontmatter)
        self.assertIn("global Codex config", frontmatter)
        self.assertIn("narrow project root", frontmatter)
        self.assertIn("same-task/date/version evidence cohort", frontmatter)

    def test_skill_packages_explicit_scope_gate(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("## Evidence scope gate", text)
        self.assertIn("currently visible conversation", text)
        self.assertIn("current working directory", text)
        self.assertIn("check_evidence_scope.py", text)
        self.assertIn("Downloads", text)
        self.assertIn("A discovered filename is metadata, not evidence", text)
        self.assertIn("actually read", text)
        self.assertIn("~/.bash_history", text)
        self.assertIn("global Codex config", text)
        self.assertIn("Missing evidence remains", text)

    def test_trigger_contract_covers_scope_and_session_controls(self):
        text = TRIGGERS.read_text(encoding="utf-8")
        self.assertIn("## Evidence-scope regression", text)
        self.assertIn("needs_completed_task", text)
        self.assertIn("must not become reusable Permission Boundary", text)
        self.assertIn("Unsafe workspace root", text)
        self.assertIn("Evidence cohort regression", text)

    def test_audit_contract_separates_discovery_reading_and_rules(self):
        text = AUDIT_CONTRACT.read_text(encoding="utf-8")
        self.assertIn("Discovered metadata", text)
        self.assertIn("Actually read evidence", text)
        self.assertIn("Actually read FlowPrint rules", text)
        self.assertIn("same target version", text)
        self.assertIn("cannot be cited", text)
        self.assertIn("tool trace", text)

    def test_windows_launcher_exposes_scope_preflight(self):
        text = POWERSHELL_RUNNER.read_text(encoding="utf-8")
        self.assertIn("'scope'", text)
        self.assertIn("check_evidence_scope.py", text)


if __name__ == "__main__":
    unittest.main()
