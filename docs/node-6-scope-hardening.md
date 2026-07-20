# FlowPrint Node 6 — Evidence Scope Hardening

Status: complete within the bounded Codex CLI scope  
Candidate version: `0.1.0+codex.20260720012358`  
Date: 2026-07-20

## Why this revision exists

Two Windows implicit-trigger runs exposed different failures:

1. the first run selected older Node 5 evidence when final-version evidence was absent;
2. the second run selected the correct final cohort but treated the whole Downloads directory as a safe workspace and enumerated unrelated filenames.

The second run also cited a contract that was not shown as read and repeated an older WindowsApps fact that was not supported by the selected final evidence cohort. These are evidence-boundary defects, not classification-layer defects.

## Implemented controls

### Deterministic workspace preflight

`scripts/check_evidence_scope.py` runs before workspace discovery.

- Blocks drive/filesystem roots, the user home directory, broad personal collections such as Downloads/Desktop/Documents, shared temporary roots, and installed plugin caches.
- Allows a real project below those collections, such as `Downloads/Project/flowprint`.
- When the user explicitly names an exact source inside an otherwise unsafe root, permits only that file and forbids enumeration of its parent, siblings, or descendants.
- Returns exit code `2` for a blocked root and performs no directory enumeration itself.
- Is exposed on Windows as `run_flowprint.ps1 scope`.

### Evidence cohort contract

Concrete values must come from the current task/date/version cohort. Older or different-version evidence may be used only as an explicitly labeled Failure Lesson or comparison. Missing current values remain unknown.

The version of FlowPrint executing the classification and the version of the completed task being classified are separate fields. A newer runtime may classify an older completed run without relabeling that run as the runtime version.

### Read-ledger and audit contract

The preview must distinguish:

- discovered metadata;
- workspace evidence actually read;
- FlowPrint rule files actually read;
- visible conversation evidence.

A file that was only listed cannot be cited. A contract or rule file that was not opened cannot be named as a source. If the audit conflicts with the tool trace, the output must downgrade to `needs_review` and compilation must stop.

## Validation completed

| Check | Result |
|---|---|
| Classification and compiler regression suite | 26 existing tests passed |
| Evidence scope/frontmatter contract | 5 tests passed |
| New deterministic scope guard | 10 tests passed |
| Total unit/integration tests | 41 passed |
| Node 3 plugin smoke test | passed |
| Skill structural validation | passed |
| Plugin manifest validation | passed |
| Safe project-root direct preflight | `allowed_project_scope`, exit `0` |
| Shared temp-root direct preflight | `blocked`, exit `2` |

Tested guard cases include Windows Downloads, Windows drive root, Windows user home, OneDrive root/Desktop, macOS home/Downloads/Library, plugin cache, shared temp root, a project nested under Downloads, a project nested under OneDrive Desktop, exact-source-only access, and a missing exact source.

## What this does not overclaim

- The workspace root block is deterministic once the Skill calls the preflight; host compliance with the instruction still needs one real implicit-trigger test.
- Evidence cohort selection and final audit consistency remain Agent behaviors governed by the Skill contract, not a host-level filesystem hook.
- This revision does not prove statistical trigger accuracy, universal Windows compatibility, field-tested Skill usefulness, or ChatGPT GUI distribution.

## Release gate

The release gate used two short Windows host tests:

1. start from Downloads and confirm FlowPrint runs preflight and stops before any listing;
2. start from the exact FlowPrint project root and confirm same-version classification plus a trace-consistent audit.

Host test A passed on Windows: implicit routing selected only FlowPrint, preflight blocked `C:\Users\demo-user\Downloads` before any enumeration, no Downloads content was read, and no write or external action occurred.

Host test B also passed: from the exact project root, preflight returned `allowed_project_scope`; only the four intended Windows Node 6 final evidence files were read; older Windows Node 4/5 and Mac Node 6 filenames were discovered but not read or used; the completed-task version remained separate from the newer runtime version; and the final audit matched the tool trace with no write or external action.

The scope-hardening release gate is therefore closed. The bounded conclusion does not include statistical routing accuracy, universal Windows compatibility, current-candidate user-side compilation, field reuse, or ChatGPT GUI distribution.

The valid compile and old-schema rejection tests do not need to be repeated unless either host test unexpectedly invokes or changes the Node 5 compiler path.
