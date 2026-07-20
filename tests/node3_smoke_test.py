#!/usr/bin/env python3
"""Deterministic Node 3 checks for the FlowPrint plugin skeleton."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "flowprint"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
SKILL = PLUGIN / "skills" / "flowprint" / "SKILL.md"
OPENAI_YAML = PLUGIN / "skills" / "flowprint" / "agents" / "openai.yaml"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    for path in (MANIFEST, SKILL, OPENAI_YAML, MARKETPLACE):
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["name"] == "flowprint", "plugin name must be flowprint")
    require(
        bool(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", manifest["version"])),
        "version must be semver, optionally with prerelease/build metadata",
    )
    require(manifest.get("skills") == "./skills/", "skills path must be ./skills/")

    interface = manifest["interface"]
    require(interface["displayName"] == "FlowPrint", "display name must preserve FlowPrint casing")
    require(interface["category"] == "Developer Tools", "unexpected plugin category")
    prompts = interface["defaultPrompt"]
    require(isinstance(prompts, list) and 1 <= len(prompts) <= 3, "defaultPrompt must contain 1–3 prompts")
    require(all(len(prompt) <= 128 for prompt in prompts), "default prompts must be at most 128 characters")

    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    require(marketplace["name"] == "flowprint-dev", "development marketplace must use a unique name")
    require(marketplace["interface"]["displayName"] == "FlowPrint Development", "unexpected marketplace label")
    entries = {entry["name"]: entry for entry in marketplace["plugins"]}
    entry = entries["flowprint"]
    require(entry["source"] == {"source": "local", "path": "./plugins/flowprint"}, "invalid local source")
    require(entry["policy"]["installation"] == "AVAILABLE", "plugin must be available")
    require(entry["policy"]["authentication"] == "ON_INSTALL", "unexpected auth policy")

    skill = SKILL.read_text(encoding="utf-8")
    require(skill.startswith("---\nname: flowprint\n"), "invalid Skill frontmatter")
    for phrase in ("$flowprint", "把这个变成可复用 Skill", "turn this into a reusable skill"):
        require(phrase in skill, f"missing positive trigger: {phrase}")
    for boundary in ("ordinary conversation summaries", "Memory updates", "one-off prompt rewriting"):
        require(boundary in skill, f"missing negative trigger boundary: {boundary}")
    require("references/decontextualization.md" in skill, "missing Node 4 classification reference")
    require("Never create or use a model confidence score" in skill, "missing confidence-score prohibition")
    require("Node 5 draft compilation" in skill, "missing Node 5 compilation boundary")
    require("Never call a plugin/Skill install command" in skill, "missing generation/install separation")

    metadata = OPENAI_YAML.read_text(encoding="utf-8")
    require('display_name: "FlowPrint"' in metadata, "missing UI display name")
    require("allow_implicit_invocation: true" in metadata, "implicit invocation must be enabled")

    print("PASS plugin manifest")
    print("PASS marketplace entry")
    print("PASS Skill trigger contract")
    print("PASS Skill UI metadata")


if __name__ == "__main__":
    main()
