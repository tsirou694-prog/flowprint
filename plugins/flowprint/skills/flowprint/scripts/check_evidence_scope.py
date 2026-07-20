#!/usr/bin/env python3
"""Fail closed before FlowPrint searches an unsafe workspace root."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable


PERSONAL_COLLECTIONS = {
    ".codex",
    ".config",
    ".ssh",
    "appdata",
    "desktop",
    "documents",
    "downloads",
    "library",
    "movies",
    "music",
    "pictures",
    "videos",
}


def _windows_style(value: str) -> bool:
    return len(value) >= 3 and value[1:3] in {":\\", ":/"}


def _pure(value: str):
    return PureWindowsPath(value) if _windows_style(value) else PurePosixPath(value)


def _parts(value: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in _pure(value).parts)


def _same_path(left: str, right: str) -> bool:
    return _parts(left) == _parts(right)


def _is_root(value: str) -> bool:
    path = _pure(value)
    return len(path.parts) == 1 or path.parent == path


def _is_personal_collection(workspace: str, home: str) -> bool:
    workspace_path = _pure(workspace)
    home_path = _pure(home)
    if type(workspace_path) is not type(home_path):
        return False

    try:
        relative = workspace_path.relative_to(home_path)
    except ValueError:
        return False

    relative_parts = tuple(part.casefold() for part in relative.parts)
    if not relative_parts:
        return True

    first = relative_parts[0]
    if first in PERSONAL_COLLECTIONS:
        return len(relative_parts) == 1

    if first.startswith("onedrive"):
        if len(relative_parts) == 1:
            return True
        return len(relative_parts) == 2 and relative_parts[1] in PERSONAL_COLLECTIONS

    return False


def _is_plugin_cache(value: str) -> bool:
    parts = _parts(value)
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == (".codex", "plugins", "cache"):
            return True
    return False


def classify_workspace(workspace: str, home: str, exact_sources: Iterable[str] = ()) -> dict[str, object]:
    exact = [str(source) for source in exact_sources]
    reason_code = "project_scope"
    reason = "Workspace is narrower than the protected personal roots."

    if _is_root(workspace):
        reason_code = "filesystem_root"
        reason = "Filesystem or drive roots are too broad for recursive evidence discovery."
    elif _same_path(workspace, home):
        reason_code = "home_root"
        reason = "The user home directory is too broad for recursive evidence discovery."
    elif _is_personal_collection(workspace, home):
        reason_code = "personal_collection"
        reason = "A broad personal collection such as Downloads or Desktop is not a project workspace."
    elif _is_plugin_cache(workspace):
        reason_code = "plugin_cache"
        reason = "The installed plugin cache is a rule bundle, not completed-task workspace evidence."
    else:
        temp_root = tempfile.gettempdir()
        if _same_path(workspace, temp_root):
            reason_code = "temp_root"
            reason = "The shared temporary directory is too broad for recursive evidence discovery."

    unsafe = reason_code != "project_scope"
    if unsafe and exact:
        return {
            "status": "allowed_explicit_only",
            "workspace_root": workspace,
            "workspace_kind": reason_code,
            "recursive_discovery_allowed": False,
            "allowed_exact_sources": exact,
            "reason": reason,
            "next_action": (
                "Read only the exact user-named sources. Do not enumerate siblings or descendants. "
                "Use visible conversation for everything else."
            ),
        }
    if unsafe:
        return {
            "status": "blocked",
            "workspace_root": workspace,
            "workspace_kind": reason_code,
            "recursive_discovery_allowed": False,
            "allowed_exact_sources": [],
            "reason": reason,
            "next_action": (
                "Do not run find, rg --files, Get-ChildItem -Recurse, or equivalent discovery. "
                "Continue from visible conversation only, or ask the user to open the actual project directory."
            ),
        }
    return {
        "status": "allowed_project_scope",
        "workspace_root": workspace,
        "workspace_kind": reason_code,
        "recursive_discovery_allowed": True,
        "allowed_exact_sources": exact,
        "reason": reason,
        "next_action": "Keep discovery inside this workspace and record every discovered and read path separately.",
    }


def _resolve_native(value: str) -> str:
    return str(Path(value).expanduser().resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=os.getcwd())
    parser.add_argument("--home", default=str(Path.home()))
    parser.add_argument(
        "--exact-source",
        action="append",
        default=[],
        help="Exact path explicitly named and authorized by the user; may be repeated.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = _resolve_native(args.workspace)
    home = _resolve_native(args.home)
    exact_sources: list[str] = []
    for source in args.exact_source:
        resolved = _resolve_native(source)
        if not Path(resolved).is_file():
            print(json.dumps({"status": "blocked", "reason": f"Exact source is not a file: {resolved}"}, indent=2))
            return 2
        exact_sources.append(resolved)

    result = classify_workspace(workspace, home, exact_sources)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 2 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
