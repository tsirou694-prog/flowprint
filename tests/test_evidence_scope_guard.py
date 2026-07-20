from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "flowprint" / "skills" / "flowprint" / "scripts" / "check_evidence_scope.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("flowprint_scope_guard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


GUARD = load_guard()


class EvidenceScopeGuardTests(unittest.TestCase):
    def test_blocks_windows_downloads_root(self):
        result = GUARD.classify_workspace(r"C:\Users\demo-user\Downloads", r"C:\Users\demo-user")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["workspace_kind"], "personal_collection")
        self.assertFalse(result["recursive_discovery_allowed"])

    def test_allows_project_below_windows_downloads(self):
        result = GUARD.classify_workspace(
            r"C:\Users\demo-user\Downloads\FlowPrint-Windows-Final-v0.1.0\flowprint",
            r"C:\Users\demo-user",
        )
        self.assertEqual(result["status"], "allowed_project_scope")
        self.assertTrue(result["recursive_discovery_allowed"])

    def test_project_named_downloads_outside_home_collection_is_allowed(self):
        result = GUARD.classify_workspace("/workspace/client/Downloads", "/Users/demo-user")
        self.assertEqual(result["status"], "allowed_project_scope")

    def test_project_below_onedrive_desktop_is_allowed(self):
        result = GUARD.classify_workspace(
            r"C:\Users\demo-user\OneDrive\Desktop\FlowPrint\flowprint",
            r"C:\Users\demo-user",
        )
        self.assertEqual(result["status"], "allowed_project_scope")

    def test_blocks_home_drive_and_macos_personal_roots(self):
        cases = [
            ("C:\\", r"C:\Users\demo-user"),
            (r"C:\Users\demo-user", r"C:\Users\demo-user"),
            (r"C:\Users\demo-user\OneDrive", r"C:\Users\demo-user"),
            (r"C:\Users\demo-user\OneDrive\Desktop", r"C:\Users\demo-user"),
            ("/", "/Users/demo-user"),
            ("/Users/demo-user", "/Users/demo-user"),
            ("/Users/demo-user/Downloads", "/Users/demo-user"),
            ("/Users/demo-user/Library", "/Users/demo-user"),
        ]
        for workspace, home in cases:
            with self.subTest(workspace=workspace):
                self.assertEqual(GUARD.classify_workspace(workspace, home)["status"], "blocked")

    def test_blocks_plugin_cache_as_workspace(self):
        result = GUARD.classify_workspace(
            r"C:\Users\demo-user\.codex\plugins\cache\flowprint-dev\flowprint\0.1.0",
            r"C:\Users\demo-user",
        )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["workspace_kind"], "plugin_cache")

    def test_unsafe_root_allows_only_exact_user_named_sources(self):
        result = GUARD.classify_workspace(
            r"C:\Users\demo-user\Downloads",
            r"C:\Users\demo-user",
            [r"C:\Users\demo-user\Downloads\FlowPrint-Evidence.zip"],
        )
        self.assertEqual(result["status"], "allowed_explicit_only")
        self.assertFalse(result["recursive_discovery_allowed"])
        self.assertEqual(len(result["allowed_exact_sources"]), 1)

    def test_cli_fails_closed_without_enumerating_blocked_root(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            home = root_path / "home"
            downloads = home / "Downloads"
            downloads.mkdir(parents=True)
            (downloads / "unrelated-secret-name.txt").write_text("do not read", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(downloads), "--home", str(home)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertNotIn("unrelated-secret-name.txt", result.stdout)

    def test_cli_unsafe_root_allows_existing_exact_source_only(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            home = root_path / "home"
            downloads = home / "Downloads"
            downloads.mkdir(parents=True)
            exact = downloads / "evidence.txt"
            exact.write_text("allowed", encoding="utf-8")
            (downloads / "unrelated.txt").write_text("not allowed", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(downloads),
                    "--home",
                    str(home),
                    "--exact-source",
                    str(exact),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "allowed_explicit_only")
            self.assertEqual(payload["allowed_exact_sources"], [str(exact.resolve())])
            self.assertNotIn("unrelated.txt", result.stdout)

    def test_cli_missing_exact_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            home = root_path / "home"
            downloads = home / "Downloads"
            downloads.mkdir(parents=True)
            missing = downloads / "missing.txt"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(downloads),
                    "--home",
                    str(home),
                    "--exact-source",
                    str(missing),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "blocked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
